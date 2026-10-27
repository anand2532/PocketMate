"""Reminder CRUD + scheduling on the memory DB (§7 reminders, §9).

* due_at stored UTC ms; tz column per row (default Asia/Kolkata).
* Recurring reminders: after done/dismiss, the next occurrence (dateutil rrule) is inserted.
* next_wake_ms() = Query 5; pm-remind sends it to the MCU as SET_WAKE (RTC alarm) before S4."""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil.rrule import rrulestr

from ..memory.store import MemoryStore
from ..util.ids import new_id
from .parser import ParsedReminder


def _ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Reminder:
    id: str
    title: str
    due_at: int | None
    tz: str
    rrule: str | None
    status: str
    snooze_until: int | None
    is_task: bool


class ReminderService:
    def __init__(self, store: MemoryStore) -> None:
        self.s = store

    def add(self, p: ParsedReminder, *, item_id: str | None = None, status: str | None = None,
            tz: str = "Asia/Kolkata") -> str:
        rid = new_id()
        with self.s.tx() as c:
            c.execute("INSERT INTO reminders(id, item_id, title, due_at, tz, rrule, status, is_task, created_at) "
                      "VALUES (?,?,?,?,?,?,?,?,?)",
                      (rid, item_id, p.title, p.due_at_ms, tz, p.rrule, status or p.status, int(p.is_task), _ms()))
        return rid

    def get(self, rid: str) -> Reminder | None:
        r = self.s.conn.execute("SELECT * FROM reminders WHERE id=?", (rid,)).fetchone()
        if not r:
            return None
        return Reminder(r["id"], r["title"], r["due_at"], r["tz"], r["rrule"], r["status"], r["snooze_until"],
                        bool(r["is_task"]))

    def confirm(self, rid: str) -> None:
        with self.s.tx() as c:
            c.execute("UPDATE reminders SET status='pending' WHERE id=? AND status='suggested'", (rid,))

    def snooze(self, rid: str, minutes: int = 10, now_ms: int | None = None) -> None:
        with self.s.tx() as c:
            c.execute("UPDATE reminders SET status='snoozed', snooze_until=? WHERE id=?",
                      ((now_ms or _ms()) + minutes * 60_000, rid))

    def complete(self, rid: str, *, dismissed: bool = False, now_ms: int | None = None) -> str | None:
        """Mark done (or dismissed). For recurring reminders returns the id of the next occurrence."""
        t = now_ms or _ms()
        r = self.get(rid)
        if r is None:
            return None
        with self.s.tx() as c:
            c.execute("UPDATE reminders SET status=?, completed_at=? WHERE id=?",
                      ("dismissed" if dismissed else "done", t, rid))
        if r.rrule and r.due_at:
            nxt = self.next_occurrence(r.rrule, r.due_at, r.tz)
            if nxt:
                nid = new_id()
                with self.s.tx() as c:
                    c.execute("INSERT INTO reminders(id, title, due_at, tz, rrule, status, is_task, created_at) "
                              "VALUES (?,?,?,?,?, 'pending', ?, ?)",
                              (nid, r.title, nxt, r.tz, r.rrule, int(r.is_task), t))
                return nid
        return None

    @staticmethod
    def next_occurrence(rrule: str, after_ms: int, tz: str) -> int | None:
        z = ZoneInfo(tz)
        start = datetime.fromtimestamp(after_ms / 1000, z)
        rule = rrulestr(rrule, dtstart=start.replace(tzinfo=None))
        nxt = rule.after(start.replace(tzinfo=None), inc=False)
        if nxt is None:
            return None
        return int(nxt.replace(tzinfo=z).timestamp() * 1000)

    def agenda(self, end_of_day_ms: int) -> list[dict]:
        """Query 4."""
        return [dict(r) for r in self.s.conn.execute(
            "SELECT id, title, due_at, is_task FROM reminders WHERE status IN ('pending','snoozed') "
            "AND (due_at < ? OR (is_task = 1 AND due_at IS NULL)) ORDER BY due_at NULLS LAST", (end_of_day_ms,))]

    def next_wake_ms(self, now_ms: int | None = None) -> int | None:
        """Query 5."""
        r = self.s.conn.execute(
            "SELECT MIN(COALESCE(snooze_until, due_at)) FROM reminders WHERE status IN ('pending','snoozed') "
            "AND COALESCE(snooze_until, due_at) > ?", (now_ms or _ms(),)).fetchone()
        return r[0] if r and r[0] is not None else None

    def due(self, now_ms: int | None = None) -> list[Reminder]:
        t = now_ms or _ms()
        rows = self.s.conn.execute(
            "SELECT id FROM reminders WHERE status IN ('pending','snoozed') AND COALESCE(snooze_until, due_at) <= ?",
            (t,)).fetchall()
        return [r for r in (self.get(x[0]) for x in rows) if r]

    def list(self, statuses: tuple[str, ...] = ("suggested", "pending", "snoozed")) -> list[dict]:
        q = ",".join("?" * len(statuses))
        return [dict(r) for r in self.s.conn.execute(
            f"SELECT * FROM reminders WHERE status IN ({q}) ORDER BY due_at NULLS LAST", statuses)]


def local_day_bounds(day: datetime, tz: str = "Asia/Kolkata") -> tuple[int, int, int]:
    z = ZoneInfo(tz)
    d0 = day.astimezone(z).replace(hour=0, minute=0, second=0, microsecond=0)
    d1 = d0 + timedelta(days=1)
    d2 = d1 + timedelta(days=1)
    return int(d0.timestamp() * 1000), int(d1.timestamp() * 1000), int(d2.timestamp() * 1000)
