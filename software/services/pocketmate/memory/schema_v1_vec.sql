-- Optional semantic retrieval (sqlite-vec extension)
CREATE VIRTUAL TABLE chunk_vec USING vec0(
  chunk_id INTEGER PRIMARY KEY,
  embedding float[384]                       -- multilingual-e5-small (EN+HI)
);
