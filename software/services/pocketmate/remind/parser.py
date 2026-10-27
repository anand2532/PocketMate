"""Fast-path reminder parser for English / Hinglish (and common Devanagari time words).

Output is always status='suggested' until the user confirms (P8). Anything the fast path can't
parse returns None and pm-core falls back to the LLM JSON-schema extractor (§9)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DEFAULT_TZ = "Asia/Kolkata"

_DAYS = {
    "monday": 0, "mon": 0, "somvar": 0, "somwar": 0, "tuesday": 1, "tue": 1, "mangalvar": 1, "mangalwar": 1,
    "wednesday": 2, "wed": 2, "budhvar": 2, "budhwar": 2, "thursday": 3, "thu": 3, "guruvar": 3, "guruwar": 3,
    "friday": 4, "fri": 4, "shukravar": 4, "shukrawar": 4, "saturday": 5, "sat": 5, "shanivar": 5, "shaniwar": 5,
    "sunday": 6, "sun": 6, "ravivar": 6, "raviwar": 6, "itvaar": 6, "itwar": 6,
}
_RR_DAY = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
_DEVA = {"कल": "kal", "आज": "aaj", "परसों": "parso", "सुबह": "subah", "शाम": "shaam", "रात": "raat",
         "दोपहर": "dopahar", "बजे": "baje", "को": "ko", "हर": "har", "रोज़": "roz", "रोज": "roz",
         "मिनट": "minute", "घंटे": "ghante", "बाद": "baad", "याद": "yaad", "दिलाना": "dilana"}
_PERIOD = {"subah": "am", "morning": "am", "savere": "am", "dopahar": "noon", "afternoon": "noon",
           "shaam": "pm", "sham": "pm", "evening": "pm", "raat": "night", "night": "night", "tonight": "night"}
_FILLER = re.compile(
    r"\b(remind me to|remind me|reminder to|reminder|please|yaad dilana|yaad dila(?:o|na)?|mujhe|ko|ki|ke|"
    r"at|on|by|baje|o'?clock|bajkar|tak)\b", re.I)


@dataclass(frozen=True)
class ParsedReminder:
    title: str
    due_local: datetime | None        # tz-aware (Asia/Kolkata by default)
    rrule: str | None
    is_task: bool
    status: str = "suggested"
    confidence: float = 0.8

    @property
    def due_at_ms(self) -> int | None:
        return int(self.due_local.timestamp() * 1000) if self.due_local else None


def _norm(text: str) -> str:
    for deva, lat in _DEVA.items():
        text = text.replace(deva, f" {lat} ")
    return re.sub(r"\s+", " ", text).strip()


def parse(text: str, now: datetime | None = None, tz: str = DEFAULT_TZ) -> ParsedReminder | None:
    z = ZoneInfo(tz)
    now = (now or datetime.now(z)).astimezone(z)
    s = _norm(text)
    low = s.lower()
    used: list[tuple[int, int]] = []

    def take(m: re.Match[str]) -> None:
        used.append(m.span())

    day_off: int | None = None
    weekday: int | None = None
    rrule: str | None = None
    hour: int | None = None
    minute = 0
    period: str | None = None
    rel: timedelta | None = None

    if m := re.search(r"\bin (\d+) (minutes?|mins?|hours?|hrs?)\b|\b(\d+) (minute|min|ghante|ghanta) (baad|mein)\b",
                      low):
        n = int(m.group(1) or m.group(3))
        unit = (m.group(2) or m.group(4))
        rel = timedelta(hours=n) if unit.startswith(("h", "g")) else timedelta(minutes=n)
        take(m)
    if m := re.search(r"\b(?:har|every) (?:din|day)\b|\b(?:har )?(?:roz|rozana)\b|\b(?:daily|every ?day)\b", low):
        rrule = "FREQ=DAILY"
        take(m)
    elif m := re.search(r"\b(?:har|every) (" + "|".join(_DAYS) + r")\b", low):
        weekday = _DAYS[m.group(1)]
        rrule = f"FREQ=WEEKLY;BYDAY={_RR_DAY[weekday]}"
        take(m)
    if m := re.search(r"\b(day after tomorrow|parso|parson)\b", low):
        day_off = 2
        take(m)
    elif m := re.search(r"\b(tomorrow|kal)\b", low):
        day_off = 1
        take(m)
    elif m := re.search(r"\b(today|aaj|tonight)\b", low):
        day_off = 0
        if m.group(1) == "tonight":
            period = "night"
        take(m)
    if weekday is None and (m := re.search(r"\b(?:on |next )?(" + "|".join(_DAYS) + r")\b", low)):
        weekday = _DAYS[m.group(1)]
        take(m)
    if m := re.search(r"\b(subah|morning|savere|dopahar|afternoon|shaam|sham|evening|raat|night)\b", low):
        period = _PERIOD[m.group(1)]
        take(m)
    if m := re.search(r"\b(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?(?:\s*(?:baje|o'?clock))?\b", low):
        # only accept a bare number as a time when an am/pm, ':', 'baje', 'at', or a period word is present
        ctx = low[max(0, m.start() - 3): m.end() + 6]
        if m.group(2) or m.group(3) or "baje" in ctx or "at " in ctx or "o'clock" in ctx or period:
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)
            ap = (m.group(3) or "").replace(".", "")
            if hour > 23 or minute > 59:
                return None
            if ap == "pm" and hour < 12:
                hour += 12
            elif ap == "am" and hour == 12:
                hour = 0
            elif not ap:
                if period in ("pm", "night") and hour < 12:
                    hour += 12 if not (period == "night" and hour <= 3) else 0
                elif period == "noon" and hour < 6:
                    hour += 12
            take(m)

    if rel is None and hour is None and day_off is None and weekday is None and rrule is None:
        return None

    if rel is not None:
        due: datetime | None = now + rel
    else:
        if hour is None:
            hour = {"am": 9, "noon": 13, "pm": 18, "night": 21}.get(period or "", 9)
        base = now
        if day_off is not None:
            base = now + timedelta(days=day_off)
        elif weekday is not None:
            delta = (weekday - now.weekday()) % 7
            base = now + timedelta(days=delta)
        due = base.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if due <= now and day_off is None:
            due += timedelta(days=7 if weekday is not None else 1)
        if rrule and "BYHOUR" not in rrule:
            rrule += f";BYHOUR={hour};BYMINUTE={minute}"

    title = s
    for a, b in sorted(used, reverse=True):
        title = title[:a] + " " + title[b:]
    title = _FILLER.sub(" ", title)
    title = re.sub(r"\s+", " ", title).strip(" ,.-")
    title = re.sub(r"^(?:to|ki|ke|that)\s+", "", title, flags=re.I)
    if not title:
        title = text.strip()
    is_task = False
    return ParsedReminder(title[:1].upper() + title[1:], due, rrule, is_task)


def parse_task(text: str) -> ParsedReminder:
    """'add task …' / 'kaam: …' -> undated task (is_task=1)."""
    t = re.sub(r"^\s*(add (a )?task|task|kaam|todo)\s*[:\-]?\s*", "", text, flags=re.I).strip()
    return ParsedReminder(t[:1].upper() + t[1:], None, None, True)
