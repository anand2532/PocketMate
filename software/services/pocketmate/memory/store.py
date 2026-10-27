"""pm-memory store: the single writer of /var/lib/pm/memory.db (§7).

All mutating methods run inside one transaction; chunk/FTS/vec rows are written and deleted with
their item (contentless FTS and vec0 ignore FK cascades)."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import sqlite3
import time
import zipfile
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from ..util.ids import new_id
from . import migrations
from .phonetic import WORD_RE, LatinToDeva, has_devanagari, phonkey

# Question words dropped before any-term RAG retrieval (EN + romanized Hindi). [impl]
STOPWORDS = frozenset("""a an the is are was were be been am do does did what who whom whose which when where why how
i me my we our you your he she it its they them their this that these those of to in on at for from with and or
not no yes can could should would will shall may might tell about please kya kaun kab kahan kaise kyun hai hain
tha thi the ka ki ke ko se mein me par aur ya mera meri mere""".split())

GENESIS_HASH = "0" * 64
TRASH_MS = 7 * 86_400_000
CHUNK_WORDS = 350
CHUNK_OVERLAP = 50


def now_ms() -> int:
    return int(time.time() * 1000)


_DUR = re.compile(r"^P(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)W)?(?:(\d+)D)?$")


def iso_duration_ms(d: str) -> int:
    m = _DUR.match(d)
    if not m or not any(m.groups()):
        raise ValueError(f"unsupported ISO-8601 duration {d!r} (use PnY/PnM/PnW/PnD)")
    y, mo, w, dd = (int(x or 0) for x in m.groups())
    return ((y * 365) + (mo * 30) + (w * 7) + dd) * 86_400_000


@dataclass(frozen=True)
class Chunk:
    seq: int
    text: str
    span_start: int
    span_end: int
    t_start_ms: int | None = None
    t_end_ms: int | None = None
    bbox_json: str | None = None


@dataclass(frozen=True)
class SearchHit:
    item_id: str
    kind: str
    title: str | None
    created_at: int
    chunk_id: int
    snippet: str
    span_start: int | None
    span_end: int | None
    score: float


def chunk_text(text: str, words: int = CHUNK_WORDS, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    """~300-500-token windows with 50-word overlap; spans are char offsets into `text`."""
    toks = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    if not toks:
        return []
    out, seq, i = [], 0, 0
    while True:
        j = min(i + words, len(toks))
        s, e = toks[i][0], toks[j - 1][1]
        out.append(Chunk(seq, text[s:e], s, e))
        if j >= len(toks):
            return out
        seq += 1
        i = j - overlap


class MemoryStore:
    def __init__(self, path: str | Path = "/var/lib/pm/memory.db", *, media_root: str | Path | None = None,
                 xlit: Callable[[str], str] | None = None, force_fts_fallback: bool = False,
                 load_vec: bool = True) -> None:
        self.path = str(path)
        self.media_root = Path(media_root) if media_root else Path(self.path).parent / "media"
        self.conn = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        if self.path != ":memory:":
            self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 5000")
        self.conn.execute("PRAGMA secure_delete = ON")
        migrations.migrate(self.conn, force_fts_fallback=force_fts_fallback, load_vec=load_vec)
        self.xlit = xlit or LatinToDeva()
        self.fts_mode = self.meta("fts_mode")
        self.vec_mode = self.meta("vec_mode") or "absent"

    def close(self) -> None:
        self.conn.close()

    # ---- infra --------------------------------------------------------------
    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        self.conn.execute("COMMIT")

    def meta(self, key: str) -> str | None:
        r = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def _expires_for(self, kind: str, created: int) -> tuple[str, int | None]:
        r = self.conn.execute("SELECT duration FROM retention_rules WHERE kind=?", (kind,)).fetchone()
        if not r:
            return "keep", None
        return r[0], created + iso_duration_ms(r[0])

    def _insert_item(self, kind: str, *, title: str | None, source: str, language: str | None = None,
                     locality: str = "local", created: int | None = None, item_id: str | None = None) -> str:
        iid = item_id or new_id()
        t = created or now_ms()
        retention, expires = self._expires_for(kind, t)
        self.conn.execute(
            "INSERT INTO items(id, kind, title, created_at, updated_at, source, locality, retention, expires_at, "
            "language) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (iid, kind, title, t, t, source, locality, retention, expires, language))
        return iid

    def _index(self, item_id: str, kind: str, title: str | None, chunks: Iterable[Chunk]) -> None:
        for c in chunks:
            cur = self.conn.execute(
                "INSERT INTO chunks(item_id, seq, text, span_start, span_end, t_start_ms, t_end_ms, bbox_json) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (item_id, c.seq, c.text, c.span_start, c.span_end, c.t_start_ms, c.t_end_ms, c.bbox_json))
            deva = "" if has_devanagari(c.text) and not re.search(r"[A-Za-z]", c.text) else self.xlit(c.text)
            self.conn.execute(
                "INSERT INTO chunks_fts(rowid, text, text_rom, text_deva, title, kind) VALUES (?,?,?,?,?,?)",
                (cur.lastrowid, c.text, phonkey(c.text), deva, title or "", kind))

    def _unindex(self, item_id: str) -> None:
        ids = [r[0] for r in self.conn.execute("SELECT id FROM chunks WHERE item_id=?", (item_id,))]
        for cid in ids:
            self.conn.execute("DELETE FROM chunks_fts WHERE rowid=?", (cid,))
            if self.vec_mode == "vec0":
                self.conn.execute("DELETE FROM chunk_vec WHERE chunk_id=?", (cid,))
        self.conn.execute("DELETE FROM chunks WHERE item_id=?", (item_id,))

    # ---- writers ------------------------------------------------------------
    def add_note(self, body: str, *, title: str | None = None, source: str = "typed", language: str | None = None,
                 origin_transcript_id: str | None = None, created: int | None = None) -> str:
        with self.tx():
            iid = self._insert_item("note", title=title or body.strip().split("\n")[0][:60], source=source,
                                    language=language, created=created)
            self.conn.execute("INSERT INTO notes(item_id, body, origin_transcript_id) VALUES (?,?,?)",
                              (iid, body, origin_transcript_id))
            self._index(iid, "note", title, chunk_text(body))
        return iid

    def update_note(self, item_id: str, body: str) -> None:
        with self.tx():
            self.conn.execute("UPDATE notes SET body=? WHERE item_id=?", (body, item_id))
            self.conn.execute("UPDATE items SET updated_at=? WHERE id=?", (now_ms(), item_id))
            title = self.conn.execute("SELECT title FROM items WHERE id=?", (item_id,)).fetchone()[0]
            self._unindex(item_id)
            self._index(item_id, "note", title, chunk_text(body))
            self.conn.execute("UPDATE daily_summaries SET stale=1 WHERE item_id IN "
                              "(SELECT interaction_id FROM citations WHERE cited_item_id=?)", (item_id,))

    def add_transcript(self, text: str, *, engine: str, segments: Iterable[tuple[int, int, str]] = (),
                       language: str | None = None, duration_ms: int | None = None, title: str | None = None,
                       locality: str = "local", created: int | None = None) -> str:
        segs = list(segments)
        with self.tx():
            iid = self._insert_item("transcript", title=title or text[:60], source="voice", language=language,
                                    locality=locality, created=created)
            self.conn.execute("INSERT INTO transcripts(item_id, text, language, duration_ms, audio_path, engine) "
                              "VALUES (?,?,?,?,NULL,?)", (iid, text, language, duration_ms, engine))
            for n, (s, e, t) in enumerate(segs):
                self.conn.execute("INSERT INTO transcript_segments VALUES (?,?,?,?,?)", (iid, n, s, e, t))
            chunks = chunk_text(text)
            if segs and chunks:   # map chunk spans to audio time via segment text positions (approximate)
                total = max(1, len(text))
                dur = duration_ms or segs[-1][1]
                chunks = [Chunk(c.seq, c.text, c.span_start, c.span_end, c.span_start * dur // total,
                                c.span_end * dur // total) for c in chunks]
            self._index(iid, "transcript", title, chunks)
        return iid

    def add_ocr_doc(self, image_path: str, full_text: str, *, engine: str, blocks: list[dict] | None = None,
                    language: str | None = None, mean_conf: float | None = None,
                    translation: list[dict] | None = None, target_lang: str | None = None,
                    title: str | None = None, created: int | None = None) -> str:
        with self.tx():
            iid = self._insert_item("ocr_doc", title=title or full_text.strip().split("\n")[0][:60],
                                    source="camera", language=language, created=created)
            self.conn.execute(
                "INSERT INTO ocr_docs(item_id, image_path, full_text, language, blocks_json, engine, mean_conf, "
                "translation_json, target_lang) VALUES (?,?,?,?,?,?,?,?,?)",
                (iid, image_path, full_text, language, json.dumps(blocks or [], ensure_ascii=False), engine,
                 mean_conf, json.dumps(translation, ensure_ascii=False) if translation else None, target_lang))
            chunks = chunk_text(full_text)
            if blocks:
                bb = json.dumps([b.get("bbox") for b in blocks])
                chunks = [Chunk(c.seq, c.text, c.span_start, c.span_end, bbox_json=bb) for c in chunks]
            self._index(iid, "ocr_doc", title, chunks)
        return iid

    def add_interaction(self, question: str, answer: str, *, engine: str,
                        citations: Iterable[tuple[str, int | None, int | None]] = (),
                        locality: str = "local") -> str:
        with self.tx():
            iid = self._insert_item("interaction", title=question[:60], source="assistant", locality=locality)
            self.conn.execute("INSERT INTO interactions VALUES (?,?,?,?)", (iid, question, answer, engine))
            for cited, s, e in citations:
                self.conn.execute("INSERT OR IGNORE INTO citations VALUES (?,?,?,?)", (iid, cited, s, e))
        return iid

    # ---- delete / retention -------------------------------------------------
    def soft_delete(self, item_id: str, *, now: int | None = None) -> None:
        with self.tx():
            self.conn.execute("UPDATE items SET deleted_at=? WHERE id=? AND deleted_at IS NULL",
                              (now or now_ms(), item_id))

    def restore(self, item_id: str) -> None:
        with self.tx():
            self.conn.execute("UPDATE items SET deleted_at=NULL WHERE id=?", (item_id,))

    def purge(self, item_id: str) -> None:
        """Hard delete: item + chunks + FTS + vec rows + media, one transaction (files after commit)."""
        media: list[str] = []
        with self.tx():
            for r in self.conn.execute("SELECT image_path FROM ocr_docs WHERE item_id=? "
                                       "UNION ALL SELECT audio_path FROM transcripts WHERE item_id=?",
                                       (item_id, item_id)):
                if r[0]:
                    media.append(r[0])
            self._unindex(item_id)
            self.conn.execute("DELETE FROM items WHERE id=?", (item_id,))
        for m in media:
            p = Path(m)
            if p.is_file() and self.media_root in p.resolve().parents:
                p.unlink()

    def set_retention_rule(self, kind: str, duration: str | None) -> None:
        with self.tx():
            if duration is None:
                self.conn.execute("DELETE FROM retention_rules WHERE kind=?", (kind,))
                self.conn.execute("UPDATE items SET retention='keep', expires_at=NULL WHERE kind=?", (kind,))
            else:
                ms = iso_duration_ms(duration)
                self.conn.execute("INSERT OR REPLACE INTO retention_rules VALUES (?,?,?)", (kind, duration, now_ms()))
                self.conn.execute("UPDATE items SET retention=?, expires_at=created_at+? WHERE kind=?",
                                  (duration, ms, kind))
        self.log_consent("retention_change", detail={"kind": kind, "duration": duration})

    def retention_sweep(self, *, now: int | None = None) -> tuple[int, int]:
        """Query 6: trash expired items, then purge trash older than 7 days. Returns (trashed, purged)."""
        t = now or now_ms()
        with self.tx():
            trashed = self.conn.execute("UPDATE items SET deleted_at=? WHERE expires_at < ? AND pinned=0 "
                                        "AND deleted_at IS NULL", (t, t)).rowcount
        old = [r[0] for r in self.conn.execute("SELECT id FROM items WHERE deleted_at IS NOT NULL AND deleted_at < ?",
                                               (t - TRASH_MS,))]
        for iid in old:
            self.purge(iid)
        return trashed, len(old)

    def orphan_counts(self) -> dict[str, int]:
        q = {
            "chunks": "SELECT count(*) FROM chunks WHERE item_id NOT IN (SELECT id FROM items)",
            "chunks_fts": "SELECT count(*) FROM chunks_fts WHERE rowid NOT IN (SELECT id FROM chunks)",
            "notes": "SELECT count(*) FROM notes WHERE item_id NOT IN (SELECT id FROM items)",
            "citations": "SELECT count(*) FROM citations WHERE cited_item_id NOT IN (SELECT id FROM items)",
        }
        if self.vec_mode == "vec0":
            q["chunk_vec"] = "SELECT count(*) FROM chunk_vec WHERE chunk_id NOT IN (SELECT id FROM chunks)"
        return {k: self.conn.execute(v).fetchone()[0] for k, v in q.items()}

    # ---- search -------------------------------------------------------------
    @staticmethod
    def _q(tokens: Iterable[str], any_term: bool = False) -> str:
        return (" OR " if any_term else " ").join('"' + t.replace('"', '""') + '"' for t in tokens if t)

    def build_match(self, query: str, *, any_term: bool = False) -> str:
        """All-terms match for explicit search; any-term (stopwords dropped) for RAG questions. [impl]"""
        if any_term:
            query = " ".join(w for w in WORD_RE.findall(query) if w.lower() not in STOPWORDS)
        words = WORD_RE.findall(query)
        if not words:
            return ""
        groups = [f"{{text}}: ({self._q(words, any_term)})"]
        rom = phonkey(query).split()
        if rom:
            groups.append(f"{{text_rom}}: ({self._q(rom, any_term)})")
        deva = [] if has_devanagari(query) else self.xlit(query).split()
        if deva:
            groups.append(f"{{text_deva}}: ({self._q(deva, any_term)})")
        return " OR ".join(groups)

    def search(self, query: str, *, limit: int = 20, kinds: Iterable[str] | None = None,
               now: int | None = None, any_term: bool = False) -> list[SearchHit]:
        match = self.build_match(query, any_term=any_term)
        if not match:
            return []
        t = now or now_ms()
        kind_sql, params = "", [match]
        if kinds:
            ks = list(kinds)
            kind_sql = f" AND i.kind IN ({','.join('?' * len(ks))})"
            params += ks
        rows = self.conn.execute(
            "SELECT i.id, i.kind, i.title, i.created_at, c.id AS cid, c.text, c.span_start, c.span_end, "
            "bm25(chunks_fts, 1.0, 0.6, 0.8) AS score "
            "FROM chunks_fts JOIN chunks c ON c.id = chunks_fts.rowid JOIN items i ON i.id = c.item_id "
            f"WHERE chunks_fts MATCH ? AND i.deleted_at IS NULL{kind_sql} "
            "ORDER BY score + (? - i.created_at) / 8.64e10 * 0.05 LIMIT ?",
            (*params, t, limit * 3)).fetchall()
        seen: set[str] = set()
        hits = []
        for r in rows:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            hits.append(SearchHit(r["id"], r["kind"], r["title"], r["created_at"], r["cid"],
                                  make_snippet(r["text"], query), r["span_start"], r["span_end"], r["score"]))
            if len(hits) >= limit:
                break
        return hits

    def open_source(self, chunk_id: int) -> dict | None:
        """Query 10."""
        r = self.conn.execute(
            "SELECT i.id, i.kind, c.span_start, c.span_end, c.t_start_ms, c.t_end_ms, c.bbox_json, "
            "t.audio_path, o.image_path FROM chunks c JOIN items i ON i.id = c.item_id "
            "LEFT JOIN transcripts t ON t.item_id = i.id LEFT JOIN ocr_docs o ON o.item_id = i.id "
            "WHERE c.id = ?", (chunk_id,)).fetchone()
        return dict(r) if r else None

    def get_item(self, item_id: str) -> dict | None:
        r = self.conn.execute(
            "SELECT i.*, n.body, t.text AS transcript, o.full_text, o.image_path, o.translation_json "
            "FROM items i LEFT JOIN notes n ON n.item_id=i.id LEFT JOIN transcripts t ON t.item_id=i.id "
            "LEFT JOIN ocr_docs o ON o.item_id=i.id WHERE i.id=?", (item_id,)).fetchone()
        return dict(r) if r else None

    def list_items(self, kind: str | None = None, limit: int = 50) -> list[dict]:
        sql = "SELECT id, kind, title, created_at, pinned FROM items WHERE deleted_at IS NULL"
        args: list = []
        if kind:
            sql += " AND kind=?"
            args.append(kind)
        sql += " ORDER BY created_at DESC LIMIT ?"
        return [dict(r) for r in self.conn.execute(sql, (*args, limit))]

    def daily_summary_input(self, day_start_ms: int, day_end_ms: int, tomorrow_end_ms: int) -> tuple[list, list]:
        """Query 8."""
        items = [dict(r) for r in self.conn.execute(
            "SELECT i.id, i.kind, i.title, substr(coalesce(n.body, t.text, o.full_text), 1, 160) AS first_line "
            "FROM items i LEFT JOIN notes n ON n.item_id = i.id LEFT JOIN transcripts t ON t.item_id = i.id "
            "LEFT JOIN ocr_docs o ON o.item_id = i.id WHERE i.created_at >= ? AND i.created_at < ? "
            "AND i.deleted_at IS NULL AND i.kind IN ('note','transcript','ocr_doc','image') "
            "ORDER BY i.pinned DESC, i.created_at LIMIT 40", (day_start_ms, day_end_ms))]
        rems = [dict(r) for r in self.conn.execute(
            "SELECT id, title, status, due_at, completed_at FROM reminders "
            "WHERE (completed_at BETWEEN ? AND ?) "
            "OR (status IN ('pending','snoozed','suggested') AND (due_at IS NULL OR due_at < ?))",
            (day_start_ms, day_end_ms, tomorrow_end_ms))]
        return items, rems

    # ---- consent log (P11 hash chain) --------------------------------------
    @staticmethod
    def _row_hash(prev: str, fields: tuple) -> str:
        return hashlib.sha256((prev + "|" + json.dumps(fields, ensure_ascii=False, separators=(",", ":")))
                              .encode()).hexdigest()

    def log_consent(self, event: str, *, scope: str | None = None, provider: str | None = None,
                    request_id: str | None = None, payload_sha256: str | None = None,
                    bytes_sent: int | None = None, detail: dict | None = None, ts: int | None = None) -> str:
        d = json.dumps(detail, sort_keys=True, ensure_ascii=False) if detail is not None else None
        t = ts or now_ms()
        with self.tx():
            r = self.conn.execute("SELECT row_hash FROM consent_log ORDER BY id DESC LIMIT 1").fetchone()
            prev = r[0] if r else GENESIS_HASH
            fields = (t, event, scope, provider, request_id, payload_sha256, bytes_sent, d)
            h = self._row_hash(prev, fields)
            self.conn.execute("INSERT INTO consent_log(ts, event, scope, provider, request_id, payload_sha256, "
                              "bytes_sent, detail, prev_hash, row_hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
                              (*fields, prev, h))
        return h

    def verify_consent_chain(self) -> tuple[bool, int | None]:
        prev = GENESIS_HASH
        for r in self.conn.execute("SELECT * FROM consent_log ORDER BY id"):
            fields = (r["ts"], r["event"], r["scope"], r["provider"], r["request_id"], r["payload_sha256"],
                      r["bytes_sent"], r["detail"])
            if r["prev_hash"] != prev or self._row_hash(prev, fields) != r["row_hash"]:
                return False, r["id"]
            prev = r["row_hash"]
        return True, None

    def consent_audit(self, limit: int = 100) -> list[dict]:
        return [dict(r) for r in self.conn.execute(
            "SELECT ts, event, scope, provider, bytes_sent FROM consent_log ORDER BY id DESC LIMIT ?", (limit,))]

    def factory_reset(self) -> None:
        with self.tx():
            self.conn.execute("INSERT OR REPLACE INTO meta VALUES ('factory_reset_in_progress', '1')")
            for t in ("chunks_fts", "chunks", "citations", "reminders", "cloud_requests", "daily_summaries",
                      "items", "retention_rules", "consent_log"):
                self.conn.execute(f"DELETE FROM {t}")  # noqa: S608 (fixed table list)
            self.conn.execute("DELETE FROM meta WHERE key='factory_reset_in_progress'")
        self.log_consent("factory_reset")
        if self.media_root.exists():
            shutil.rmtree(self.media_root)

    # ---- export / import ----------------------------------------------------
    def export_zip(self, dest: str | Path) -> Path:
        dest = Path(dest)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            lines = []
            for r in self.conn.execute("SELECT id FROM items WHERE deleted_at IS NULL ORDER BY created_at"):
                it = self.get_item(r[0]) or {}
                lines.append(json.dumps(it, ensure_ascii=False))
                if it.get("kind") == "note":
                    z.writestr(f"notes/{it['id']}.md", it.get("body") or "")
                img = it.get("image_path")
                if img and Path(img).is_file():
                    z.write(img, f"media/{Path(img).name}")
            z.writestr("items.jsonl", "\n".join(lines) + ("\n" if lines else ""))
            rems = [dict(r) for r in self.conn.execute("SELECT * FROM reminders")]
            z.writestr("reminders.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rems))
            buf = io.StringIO()
            cols = ["id", "ts", "event", "scope", "provider", "request_id", "payload_sha256", "bytes_sent", "detail",
                    "prev_hash", "row_hash"]
            w = csv.writer(buf)
            w.writerow(cols)
            for r in self.conn.execute(f"SELECT {','.join(cols)} FROM consent_log ORDER BY id"):
                w.writerow(list(r))
            z.writestr("consent_log.csv", buf.getvalue())
            z.writestr("manifest.json", json.dumps({"format": "pocketmate-export", "version": 1,
                                                    "schema_version": self.meta("schema_version")}))
        self.log_consent("export", detail={"items": len(lines)})
        return dest

    def import_zip(self, src: str | Path) -> int:
        """Restore items/reminders/consent_log from an export into an EMPTY store. Returns item count."""
        n = 0
        with zipfile.ZipFile(src) as z:
            items = [json.loads(x) for x in z.read("items.jsonl").decode().splitlines() if x.strip()]
            for it in items:
                k = it["kind"]
                if k == "note":
                    self.add_note(it.get("body") or "", title=it.get("title"), source="import",
                                  created=it["created_at"])
                elif k == "transcript":
                    self.add_transcript(it.get("transcript") or "", engine="import", title=it.get("title"),
                                        created=it["created_at"])
                elif k == "ocr_doc":
                    self.add_ocr_doc(it.get("image_path") or "", it.get("full_text") or "", engine="import",
                                     title=it.get("title"), created=it["created_at"])
                else:
                    continue
                n += 1
            if "reminders.jsonl" in z.namelist():
                with self.tx():
                    for line in z.read("reminders.jsonl").decode().splitlines():
                        if line.strip():
                            r = json.loads(line)
                            r["item_id"] = None
                            cols = ",".join(r)
                            self.conn.execute(f"INSERT OR IGNORE INTO reminders({cols}) VALUES "
                                              f"({','.join('?' * len(r))})", tuple(r.values()))
            rows = list(csv.DictReader(io.StringIO(z.read("consent_log.csv").decode())))
            with self.tx():
                if self.conn.execute("SELECT count(*) FROM consent_log").fetchone()[0] == 0:
                    for r in rows:
                        vals = [None if r[c] == "" else r[c] for c in
                                ("ts", "event", "scope", "provider", "request_id", "payload_sha256", "bytes_sent",
                                 "detail", "prev_hash", "row_hash")]
                        vals[0] = int(vals[0])
                        vals[6] = int(vals[6]) if vals[6] is not None else None
                        self.conn.execute("INSERT INTO consent_log(ts, event, scope, provider, request_id, "
                                          "payload_sha256, bytes_sent, detail, prev_hash, row_hash) "
                                          "VALUES (?,?,?,?,?,?,?,?,?,?)", vals)
        return n


def make_snippet(text: str, query: str, width: int = 60) -> str:
    """snippet() is NULL on contentless FTS tables, so snippets are cut from chunks.text here."""
    low = text.lower()
    pos = -1
    for w in WORD_RE.findall(query.lower()):
        pos = low.find(w)
        if pos >= 0:
            end = pos + len(w)
            break
    if pos < 0:
        return text[: width * 2] + ("…" if len(text) > width * 2 else "")
    s = max(0, pos - width)
    e = min(len(text), end + width)
    return ("…" if s else "") + text[s:pos] + "[" + text[pos:end] + "]" + text[end:e] + ("…" if e < len(text) else "")
