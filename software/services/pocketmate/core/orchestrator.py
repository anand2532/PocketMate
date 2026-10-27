"""Fast-path intents (≤50 ms grammar, §14 L2) + RAG answers with mandatory source links (P12)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..engines.types import ChatMessage, EngineError, GenParams, LLMEngine, new_ctx
from ..memory.store import MemoryStore, SearchHit
from ..remind.parser import parse as parse_reminder
from ..remind.scheduler import ReminderService

NO_SOURCES = "No sources: general knowledge"
RAG_K = 5
SYSTEM = ("You are PocketMate, an offline assistant. Answer briefly in the user's language (English, Hindi or "
          "Hinglish). Use ONLY the numbered notes when they are relevant and cite them like [1]. If the notes "
          "don't contain the answer, say so and answer from general knowledge.")

_NOTE = re.compile(r"^\s*(?:note(?: that)?|take a note|likh lo|likho|yaad rakh(?:na|o)?|नोट(?: करो)?)\s*[:,-]?\s*(.+)$",
                   re.I | re.S)
_NOTE_SUFFIX = re.compile(r"^(.+?)\s*(?:note kar lo|note karo|likh lo|नोट करो|लिख लो)\s*$", re.I | re.S)
_SEARCH = re.compile(r"^\s*(?:search|find|dhundo|khojo|खोजो)\s+(?:for\s+)?(.+)$", re.I | re.S)


@dataclass
class Answer:
    kind: str                         # note_saved | reminder_suggested | search | answer | error
    text: str
    item_id: str | None = None
    reminder_id: str | None = None
    sources: list[dict] = field(default_factory=list)
    source_label: str | None = None   # NO_SOURCES when nothing was retrieved (P12)
    needs_confirmation: bool = False


class Orchestrator:
    def __init__(self, store: MemoryStore, *, llm: LLMEngine | None = None, tz: str = "Asia/Kolkata") -> None:
        self.store, self.llm, self.tz = store, llm, tz
        self.reminders = ReminderService(store)

    def route(self, text: str) -> str:
        t = text.strip()
        if _NOTE.match(t) or _NOTE_SUFFIX.match(t):
            return "note"
        if _SEARCH.match(t):
            return "search"
        if parse_reminder(t, tz=self.tz) is not None:
            return "remind"
        return "ask"

    async def handle(self, text: str, *, origin: str = "voice") -> Answer:
        intent = self.route(text)
        if intent == "note":
            m = _NOTE.match(text.strip()) or _NOTE_SUFFIX.match(text.strip())
            assert m
            body = m.group(1).strip()
            iid = self.store.add_note(body, source="voice" if origin == "voice" else "typed")
            return Answer("note_saved", body, item_id=iid)
        if intent == "remind":
            p = parse_reminder(text, tz=self.tz)
            assert p is not None
            rid = self.reminders.add(p, tz=self.tz)       # status 'suggested': user confirms on the card
            when = p.due_local.strftime("%a %d %b, %H:%M") if p.due_local else "no time"
            return Answer("reminder_suggested", f"{p.title} — {when}", reminder_id=rid, needs_confirmation=True)
        if intent == "search":
            m = _SEARCH.match(text.strip())
            assert m
            hits = self.store.search(m.group(1), limit=10)
            return Answer("search", f"{len(hits)} results", sources=[_src(h) for h in hits],
                          source_label=None if hits else "No matches")
        return await self.ask(text)

    async def ask(self, question: str) -> Answer:
        hits = self.store.search(question, limit=RAG_K, any_term=True)
        if self.llm is None:
            if hits:
                txt = "Here is what I found in your notes:\n" + "\n".join(f"[{i + 1}] {h.snippet}"
                                                                          for i, h in enumerate(hits))
            else:
                txt = "I can't answer that offline right now (model not loaded)."
            return self._record(question, txt, hits, "extractive")
        ctx_block = "\n".join(f"[{i + 1}] ({h.kind}) {h.snippet}" for i, h in enumerate(hits))
        msgs = [ChatMessage("system", SYSTEM)]
        if hits:
            msgs.append(ChatMessage("system", "Notes:\n" + ctx_block, tuple(h.item_id for h in hits)))
        msgs.append(ChatMessage("user", question))
        out = []
        try:
            async for d in self.llm.generate(new_ctx("voice"), msgs, GenParams(max_tokens=256)):
                out.append(d.text)
        except EngineError as e:
            return Answer("error", f"Assistant unavailable: {e}")
        return self._record(question, "".join(out).strip(), hits, self.llm.info().name)

    def _record(self, q: str, a: str, hits: list[SearchHit], engine: str) -> Answer:
        cited = [h for i, h in enumerate(hits) if f"[{i + 1}]" in a] or hits   # keep retrieved set if no marks
        iid = self.store.add_interaction(q, a, engine=engine,
                                         citations=[(h.item_id, h.span_start, h.span_end) for h in cited])
        return Answer("answer", a, item_id=iid, sources=[_src(h) for h in cited],
                      source_label=None if cited else NO_SOURCES)


def _src(h: SearchHit) -> dict:
    return {"item_id": h.item_id, "kind": h.kind, "title": h.title, "chunk_id": h.chunk_id, "snippet": h.snippet,
            "created_at": h.created_at}
