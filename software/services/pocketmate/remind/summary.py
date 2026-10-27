"""Daily summary (§9.1). Local only, always (P13).

Task/reminder lists come deterministically from SQL (Q8). The LLM writes only the highlights,
each of which must cite >= 1 source id from the input; invalid citations are dropped. Extractive
mode (no LLM) on the 2 GB SKU, at thermal stage >= Soft ('T2'), below 10 % battery, or on LLM failure."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from ..engines.types import ChatMessage, EngineError, GenParams, LLMEngine, Locality, new_ctx
from ..memory.store import MemoryStore
from ..util.ids import new_id
from .scheduler import local_day_bounds

HIGHLIGHT_SCHEMA = {
    "type": "object",
    "properties": {"highlights": {"type": "array", "maxItems": 5, "items": {
        "type": "object", "required": ["text", "source_ids"],
        "properties": {"text": {"type": "string"},
                       "source_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}}}}}},
    "required": ["highlights"],
}


class CloudNotAllowed(RuntimeError):
    pass


@dataclass
class SummaryPolicy:
    sku_ram_gb: int = 4
    thermal_stage: int = 0          # ThermalStage: >= 2 (Soft) -> extractive
    battery_pct: int = 100


async def generate_daily_summary(store: MemoryStore, day: datetime, *, llm: LLMEngine | None = None,
                                 policy: SummaryPolicy = SummaryPolicy(), tz: str = "Asia/Kolkata") -> dict:
    d0, d1, d2 = local_day_bounds(day, tz)
    items, rems = store.daily_summary_input(d0, d1, d2)
    done = [{"id": r["id"], "title": r["title"]} for r in rems if r["completed_at"] and d0 <= r["completed_at"] <= d1]
    open_ = [{"id": r["id"], "title": r["title"], "status": r["status"]} for r in rems
             if r["status"] in ("pending", "snoozed", "suggested") and (r["due_at"] is None or r["due_at"] < d1)]
    tomorrow = [{"id": r["id"], "title": r["title"], "due_at": r["due_at"]} for r in rems
                if r["status"] in ("pending", "snoozed") and r["due_at"] is not None and d1 <= r["due_at"] < d2]
    extractive = (llm is None or policy.sku_ram_gb <= 2 or policy.thermal_stage >= 2 or policy.battery_pct < 10
                  or not items)
    mode = "extractive"
    highlights: list[dict] = []
    if not extractive:
        assert llm is not None
        if llm.info().locality != Locality.LOCAL:
            raise CloudNotAllowed("daily summary must use a local engine (P13)")
        try:
            highlights = await _llm_highlights(llm, items)
            mode = "llm" if highlights else "extractive"
        except EngineError:
            highlights = []
    if not highlights:
        highlights = [{"text": (it["title"] or it["first_line"] or "")[:80], "source_ids": [it["id"]]}
                      for it in items[:5]]
        mode = "extractive"
    body = {"highlights": highlights, "done": done, "open": open_, "tomorrow": tomorrow,
            "counts": {"captures": len(items), "done": len(done), "open": len(open_)}}
    day_s = day.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d")
    now = int(time.time() * 1000)
    with store.tx() as c:
        old = c.execute("SELECT item_id FROM daily_summaries WHERE day=?", (day_s,)).fetchone()
        if old:
            c.execute("DELETE FROM items WHERE id=?", (old[0],))
        sid = new_id()
        c.execute("INSERT INTO items(id, kind, title, created_at, updated_at, source) "
                  "VALUES (?, 'summary', ?, ?, ?, 'assistant')", (sid, f"Daily summary {day_s}", now, now))
        c.execute("INSERT INTO daily_summaries(item_id, day, body_json, mode, generated_at) VALUES (?,?,?,?,?)",
                  (sid, day_s, json.dumps(body, ensure_ascii=False), mode, now))
        for h in highlights:
            for src in h["source_ids"]:
                c.execute("INSERT OR IGNORE INTO citations VALUES (?,?,NULL,NULL)", (sid, src))
    body["item_id"], body["mode"], body["day"] = sid, mode, day_s
    return body


async def _llm_highlights(llm: LLMEngine, items: list[dict]) -> list[dict]:
    valid = {it["id"] for it in items}
    lines = [f"[{it['id']}] ({it['kind']}) {it['title'] or ''}: {(it['first_line'] or '')[:120]}" for it in items]
    prompt = ("Write at most 5 short highlights of the user's day from these captures. Every highlight must cite "
              "the ids it came from. Reply as JSON {\"highlights\":[{\"text\":..., \"source_ids\":[...]}]}.\n"
              + "\n".join(lines)[:2400])
    ctx = new_ctx("schedule")
    out = []
    async for d in llm.generate(ctx, [ChatMessage("user", prompt)],
                                GenParams(max_tokens=300, temperature=0.2, json_schema=HIGHLIGHT_SCHEMA)):
        out.append(d.text)
    try:
        data = json.loads("".join(out))
    except ValueError:
        return []
    res = []
    for h in data.get("highlights", [])[:5]:
        ids = [i for i in h.get("source_ids", []) if i in valid]
        if ids and isinstance(h.get("text"), str) and h["text"].strip():
            res.append({"text": h["text"].strip()[:160], "source_ids": ids})
    return res
