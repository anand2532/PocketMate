"""Schema migrations for memory.db. meta.schema_version tracks the applied version.
Each migration runs in one transaction. Add new versions by appending to MIGRATIONS."""
from __future__ import annotations

import logging
import sqlite3
from collections.abc import Callable
from importlib import resources

log = logging.getLogger("pm.memory")

CONTENTLESS_DELETE_MIN = (3, 43, 0)


def sqlite_version() -> tuple[int, int, int]:
    return tuple(int(x) for x in sqlite3.sqlite_version.split(".")[:3])  # type: ignore[return-value]


def fts_options(force_fallback: bool = False) -> tuple[str, str]:
    if not force_fallback and sqlite_version() >= CONTENTLESS_DELETE_MIN:
        return "content='', contentless_delete=1,", "contentless_delete"
    return "", "content_storing"


def _sql(name: str) -> str:
    return resources.files("pocketmate.memory").joinpath(name).read_text(encoding="utf-8")


def _v1(conn: sqlite3.Connection, *, force_fts_fallback: bool = False, load_vec: bool = True) -> None:
    opts, mode = fts_options(force_fts_fallback)
    # executescript() commits implicitly, so the transaction is part of the script itself.
    conn.executescript("BEGIN;\n" + _sql("schema_v1.sql").replace("{FTS_CONTENT_OPTIONS}", opts)
                       + f"\nINSERT OR REPLACE INTO meta(key, value) VALUES ('fts_mode', '{mode}');"
                       + "\nINSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', '1');\nCOMMIT;")
    vec = "absent"
    if load_vec:
        try:
            import sqlite_vec  # type: ignore[import-not-found]
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            conn.executescript(_sql("schema_v1_vec.sql"))
            vec = "vec0"
        except (ImportError, AttributeError, sqlite3.OperationalError) as e:
            log.info("sqlite-vec unavailable (%s); semantic search disabled", e)
    conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('vec_mode', ?)", (vec,))


MIGRATIONS: list[Callable[..., None]] = [_v1]
LATEST = len(MIGRATIONS)


def current_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    except sqlite3.OperationalError:
        return 0
    return int(row[0]) if row else 0


def migrate(conn: sqlite3.Connection, **kw: object) -> int:
    v = current_version(conn)
    for i in range(v, LATEST):
        try:
            MIGRATIONS[i](conn, **kw)    # each migration commits atomically and bumps schema_version
        except BaseException:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            raise
        log.info("memory.db migrated to v%d", i + 1)
    return LATEST
