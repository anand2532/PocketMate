-- PocketMate memory schema v1 = ARCHITECTURE.md §7 (copied verbatim; changes marked [impl]):
-- [impl] PRAGMAs are applied per connection by store.py, not here.
-- [impl] `meta` is created first.
-- [impl] chunks_fts content options are templated: contentless_delete=1 on SQLite >= 3.43,
--        otherwise a regular (content-storing) FTS5 table so DELETE still works
--        (Debian Bookworm ships SQLite 3.40.x -- see STATUS.md).
-- [impl] tokenizer adds `categories 'L* N* Co Mc Mn'`: with the §7 default, unicode61 splits
--        Devanagari words at every vowel sign (मिलते -> म, लत), breaking Hindi search.
-- [impl] chunk_vec (sqlite-vec) lives in schema_v1_vec.sql and is applied only if vec0 loads.
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);  -- schema_version, etc. (moved first: consent_log trigger reads it)
PRAGMA secure_delete = ON;

-- Common item table: every memorable thing has a row here (source-link target).
CREATE TABLE items (
  id            TEXT PRIMARY KEY,            -- UUIDv7
  kind          TEXT NOT NULL CHECK (kind IN ('note','transcript','ocr_doc','image','interaction','task','summary')),
  title         TEXT,
  created_at    INTEGER NOT NULL,            -- unix ms UTC
  updated_at    INTEGER NOT NULL,
  source        TEXT NOT NULL CHECK (source IN ('voice','typed','camera','import','assistant')),
  locality      TEXT NOT NULL DEFAULT 'local' CHECK (locality IN ('local','cloud')), -- was cloud used to produce it
  retention     TEXT NOT NULL DEFAULT 'keep',    -- [PM 2026-10-21] keep until user sets auto-delete; else ISO duration e.g. 'P30D'
  expires_at    INTEGER,                     -- NULL = keep (default); set only when user configures auto-delete
  language      TEXT,                        -- 'en' | 'hi' | 'hi-en'
  pinned        INTEGER NOT NULL DEFAULT 0,
  deleted_at    INTEGER                      -- soft delete (trash, 7 days) before purge
);
CREATE INDEX items_kind_created ON items(kind, created_at DESC);
CREATE INDEX items_expires ON items(expires_at) WHERE expires_at IS NOT NULL;

CREATE TABLE tags (item_id TEXT REFERENCES items(id) ON DELETE CASCADE, tag TEXT NOT NULL,
                   PRIMARY KEY (item_id, tag));

CREATE TABLE notes (
  item_id   TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  body      TEXT NOT NULL,                   -- markdown
  origin_transcript_id TEXT REFERENCES items(id) ON DELETE SET NULL
);

CREATE TABLE transcripts (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  text        TEXT NOT NULL,
  language    TEXT,
  duration_ms INTEGER,
  audio_path  TEXT,                          -- NULL unless user chose "keep audio" (default: discard audio)
  engine      TEXT NOT NULL                  -- e.g. 'whispercpp:base-q5_1'
);
CREATE TABLE transcript_segments (
  item_id  TEXT REFERENCES items(id) ON DELETE CASCADE,
  seq      INTEGER, start_ms INTEGER, end_ms INTEGER, text TEXT,
  PRIMARY KEY (item_id, seq)
);

CREATE TABLE ocr_docs (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  image_path  TEXT NOT NULL,
  full_text   TEXT NOT NULL,
  language    TEXT,
  blocks_json TEXT,                          -- [{text,bbox,conf}]
  engine      TEXT NOT NULL,
  mean_conf   REAL,
  translation_json TEXT,                     -- [{src,tgt,src_lang,tgt_lang,bbox}] (§9.2)
  target_lang TEXT
);

CREATE TABLE interactions (                  -- Q&A history with citations
  item_id   TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  question  TEXT NOT NULL, answer TEXT NOT NULL, engine TEXT NOT NULL
);
CREATE TABLE citations (
  interaction_id TEXT REFERENCES items(id) ON DELETE CASCADE,
  cited_item_id  TEXT REFERENCES items(id) ON DELETE CASCADE,
  span_start INTEGER, span_end INTEGER,      -- char offsets in cited text (or ms for transcript)
  PRIMARY KEY (interaction_id, cited_item_id, span_start)
);

CREATE TABLE reminders (
  id           TEXT PRIMARY KEY,
  item_id      TEXT REFERENCES items(id) ON DELETE SET NULL,   -- originating note/transcript
  title        TEXT NOT NULL,
  due_at       INTEGER,                      -- unix ms UTC; NULL = undated task
  tz           TEXT NOT NULL DEFAULT 'Asia/Kolkata',  -- [A-15] device tz from settings
  rrule        TEXT,                         -- RFC 5545, e.g. 'FREQ=DAILY;BYHOUR=9'
  status       TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('suggested','pending','done','dismissed','snoozed')),
  snooze_until INTEGER,
  is_task      INTEGER NOT NULL DEFAULT 0,   -- daily task vs timed reminder
  created_at   INTEGER NOT NULL, completed_at INTEGER
);
CREATE INDEX reminders_due ON reminders(status, due_at);

CREATE TABLE consent_log (                   -- append-only audit log
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           INTEGER NOT NULL,
  event        TEXT NOT NULL CHECK (event IN ('cloud_granted','cloud_denied','cloud_sent','cloud_error',
                                              'mic_open','mic_close','camera_capture','export','delete',
                                              'retention_change','setting_change','factory_reset',
                                              'cloud_delete_requested','cloud_delete_confirmed',
                                              'cloud_delete_failed','cloud_delete_unsupported','charge_inhibit','thermal_stage')),
  scope        TEXT,                         -- asr/llm/ocr/vision
  provider     TEXT,
  request_id   TEXT,
  payload_sha256 TEXT,
  bytes_sent   INTEGER,
  detail       TEXT,                         -- JSON, no user content
  prev_hash    TEXT NOT NULL,                -- hash chain for tamper evidence
  row_hash     TEXT NOT NULL
);
CREATE TRIGGER consent_log_no_update BEFORE UPDATE ON consent_log
BEGIN SELECT RAISE(ABORT, 'consent_log is append-only'); END;
CREATE TRIGGER consent_log_no_delete BEFORE DELETE ON consent_log
WHEN (SELECT value FROM meta WHERE key='factory_reset_in_progress') IS NOT '1'
BEGIN SELECT RAISE(ABORT, 'consent_log is append-only'); END;


-- Auto-delete rules (user-set; none by default) [PM 2026-10-21]
CREATE TABLE retention_rules (
  kind TEXT PRIMARY KEY, duration TEXT NOT NULL,   -- e.g. 'transcript' -> 'P90D'
  created_at INTEGER NOT NULL
);

-- Cloud requests and remote ids for the deletion API (§6.7)
CREATE TABLE cloud_requests (
  request_id   TEXT PRIMARY KEY,
  provider     TEXT NOT NULL, capability TEXT NOT NULL,
  item_id      TEXT REFERENCES items(id) ON DELETE SET NULL,
  remote_ids   TEXT NOT NULL DEFAULT '[]',         -- JSON array
  sent_at      INTEGER NOT NULL,
  delete_state TEXT NOT NULL DEFAULT 'none' CHECK (delete_state IN ('none','requested','pending','deleted','failed','unsupported')),
  delete_attempts INTEGER NOT NULL DEFAULT 0, delete_deadline INTEGER, verified_at INTEGER
);

-- Daily summary (§9.1)
CREATE TABLE daily_summaries (
  item_id     TEXT PRIMARY KEY REFERENCES items(id) ON DELETE CASCADE,
  day         TEXT NOT NULL UNIQUE,               -- local date 'YYYY-MM-DD'
  body_json   TEXT NOT NULL,                      -- {highlights[{text,source_ids}], done[], open[], tomorrow[]}
  mode        TEXT NOT NULL CHECK (mode IN ('llm','extractive')),
  stale       INTEGER NOT NULL DEFAULT 0,         -- set when a cited item is deleted/edited
  generated_at INTEGER NOT NULL, notified_at INTEGER
);
-- Highlights reuse `citations` (interaction_id = summary item_id).
CREATE TRIGGER summary_stale_on_delete AFTER UPDATE OF deleted_at ON items
WHEN NEW.deleted_at IS NOT NULL
BEGIN
  UPDATE daily_summaries SET stale = 1
  WHERE item_id IN (SELECT interaction_id FROM citations WHERE cited_item_id = NEW.id);
END;

-- Full-text index over all searchable text (external-content style, one row per chunk).
CREATE TABLE chunks (
  id       INTEGER PRIMARY KEY,
  item_id  TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  seq      INTEGER NOT NULL,
  text     TEXT NOT NULL,                    -- ~300-500 tokens, overlap 50
  span_start INTEGER, span_end INTEGER,      -- offsets back into source text (source links)
  t_start_ms INTEGER, t_end_ms INTEGER,      -- transcript chunks: audio timestamps (source link)
  bbox_json  TEXT,                           -- OCR chunks: region(s) in the photo (source link)
  UNIQUE(item_id, seq)
);
CREATE VIRTUAL TABLE chunks_fts USING fts5(
  text,                                      -- original (any script)
  text_rom,                                  -- phonetic key of romanized text (§6.12)
  text_deva,                                 -- Devanagari shadow of Latin-script Hindi tokens
  title UNINDEXED, kind UNINDEXED,
  {FTS_CONTENT_OPTIONS}                       -- contentless_delete needs SQLite >= 3.43; see migrations.py
  tokenize = "unicode61 remove_diacritics 2 categories 'L* N* Co Mc Mn'"  -- [impl] Mc/Mn: keep Devanagari matras inside tokens
);
-- pm-memory writes chunks_fts(rowid=chunks.id, ...) in the same transaction as chunks.
-- Optional: second index with tokenize='trigram' for substring/OCR-noise tolerant search.

CREATE TABLE embedding_meta (chunk_id INTEGER PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
                             model TEXT NOT NULL, created_at INTEGER NOT NULL);
