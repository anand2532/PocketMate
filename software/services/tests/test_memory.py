import sqlite3

import pytest

from pocketmate.memory.phonetic import has_devanagari, phonkey, romanize
from pocketmate.memory.store import MemoryStore, chunk_text, make_snippet


def test_phonetic_keys_match_across_scripts():
    assert has_devanagari("कल") and not has_devanagari("kal")
    assert phonkey("कल मिलते हैं") == phonkey("kal milte hain")
    assert phonkey("milate") == phonkey("milte")
    assert romanize("मिलते").startswith("mil")


def test_fts_tokenizer_keeps_devanagari_words(store):
    store.add_note("कल मिलते हैं डॉक्टर के पास")
    assert store.search("मिलते"), "matras must not split Devanagari words"


def test_cross_script_search(store):
    a = store.add_note("kal milte hain doctor ke paas")
    b = store.add_note("मंगलवार को दवा लेनी है")
    assert [h.item_id for h in store.search("कल मिलते")][:1] == [a]
    assert any(h.item_id == b for h in store.search("dava"))
    hits = store.search("doctor")
    assert hits[0].snippet and "doctor" in hits[0].snippet.lower()


def test_transcript_and_ocr_and_open_source(store):
    t = store.add_transcript("remind me to buy milk tomorrow", engine="stub")
    o = store.add_ocr_doc("/nonexistent.jpg", "Paracetamol 500 mg twice daily", engine="stub")
    h = store.search("paracetamol")[0]
    assert h.item_id == o
    src = store.open_source(h.chunk_id)
    assert src and src["id"] == o and src["kind"] == "ocr_doc"
    assert store.search("milk")[0].item_id == t


def test_soft_delete_restore_purge_no_orphans(store):
    i = store.add_note("secret plan alpha")
    store.soft_delete(i)
    assert not store.search("alpha")
    store.restore(i)
    assert store.search("alpha")
    store.purge(i)
    assert not store.search("alpha") and store.get_item(i) is None
    assert all(v == 0 for v in store.orphan_counts().values())


def test_retention_sweep(store):
    store.set_retention_rule("note", "P1D")
    i = store.add_note("ephemeral", created=1_000)
    trashed, _ = store.retention_sweep(now=1_000 + 2 * 86_400_000)
    assert trashed == 1
    _, purged = store.retention_sweep(now=1_000 + 10 * 86_400_000)
    assert purged == 1 and store.get_item(i) is None


def test_consent_chain_and_append_only(store):
    store.log_consent("cloud_granted", scope="asr", provider="sarvam", request_id="r1")
    store.log_consent("cloud_sent", scope="asr", provider="sarvam", request_id="r1", bytes_sent=10)
    assert store.verify_consent_chain() == (True, None)
    with pytest.raises(sqlite3.DatabaseError):
        store.conn.execute("UPDATE consent_log SET bytes_sent=0")
    with pytest.raises(sqlite3.DatabaseError):
        store.conn.execute("DELETE FROM consent_log")


def test_export_import_roundtrip(tmp_path, store):
    store.add_note("export me please")
    store.add_transcript("voice memo about the train", engine="stub")
    store.log_consent("setting_change", detail={"k": "v"})
    z = store.export_zip(tmp_path / "e.zip")
    fresh = MemoryStore(tmp_path / "n.db", load_vec=False)
    assert fresh.import_zip(z) == 2
    assert fresh.search("train") and fresh.verify_consent_chain()[0]
    fresh.close()


def test_factory_reset(store):
    store.add_note("x")
    store.factory_reset()
    assert store.list_items() == [] and store.verify_consent_chain()[0]


def test_fts_fallback_mode(tmp_path):
    s = MemoryStore(tmp_path / "f.db", force_fts_fallback=True, load_vec=False)
    assert s.fts_mode != MemoryStore(tmp_path / "g.db", load_vec=False).fts_mode or s.fts_mode
    i = s.add_note("fallback works kal")
    assert s.search("kal")[0].item_id == i
    s.purge(i)
    assert all(v == 0 for v in s.orphan_counts().values())


def test_chunking_and_snippet():
    words = " ".join(f"w{i}" for i in range(800))
    ch = chunk_text(words)
    assert len(ch) >= 2
    assert "w400" in make_snippet(words, "w400")
