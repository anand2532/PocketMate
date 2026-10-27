import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from conftest import arun

from pocketmate.engines.backends.stub import StubLLM
from pocketmate.engines.types import EngineInfo, Locality
from pocketmate.remind.parser import parse, parse_task
from pocketmate.remind.scheduler import ReminderService, local_day_bounds
from pocketmate.remind.summary import CloudNotAllowed, SummaryPolicy, generate_daily_summary

Z = ZoneInfo("Asia/Kolkata")
NOW = datetime(2026, 10, 27, 14, 0, tzinfo=Z)   # Tuesday


@pytest.mark.parametrize("text,title,due,rrule", [
    ("remind me to call mom kal subah 9 baje", "Call mom", datetime(2026, 10, 28, 9, 0, tzinfo=Z), None),
    ("कल सुबह 9 बजे दवा लेना याद दिलाना", "दवा लेना", datetime(2026, 10, 28, 9, 0, tzinfo=Z), None),
    ("remind me in 20 minutes to check oven", "Check oven", datetime(2026, 10, 27, 14, 20, tzinfo=Z), None),
    ("10 minute baad chai", "Chai", datetime(2026, 10, 27, 14, 10, tzinfo=Z), None),
    ("parso shaam 6 baje meeting", "Meeting", datetime(2026, 10, 29, 18, 0, tzinfo=Z), None),
    ("har roz raat 10 baje dawai", "Dawai", datetime(2026, 10, 27, 22, 0, tzinfo=Z), "FREQ=DAILY;BYHOUR=22;BYMINUTE=0"),
    ("every monday at 9am standup", "Standup", datetime(2026, 11, 2, 9, 0, tzinfo=Z),
     "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0"),
    ("remind me at 3:30 pm to pay bill", "Pay bill", datetime(2026, 10, 27, 15, 30, tzinfo=Z), None),
])
def test_parse(text, title, due, rrule):
    p = parse(text, now=NOW)
    assert p is not None and p.title == title and p.due_local == due and p.rrule == rrule
    assert p.status == "suggested"


def test_parse_rejects_non_reminders():
    assert parse("what is the weather", now=NOW) is None
    assert parse("I have 3 cats", now=NOW) is None
    assert parse("at 25:00 call", now=NOW) is None
    assert parse_task("buy milk").is_task


def test_scheduler_flow(store):
    rs = ReminderService(store)
    t0 = int(NOW.timestamp() * 1000)
    rid = rs.add(parse("remind me in 20 minutes to check oven", now=NOW))
    assert rs.next_wake_ms(t0) is None                 # suggested reminders don't wake the device
    rs.confirm(rid)
    assert rs.next_wake_ms(t0) == t0 + 20 * 60_000
    assert rs.due(t0 + 21 * 60_000)[0].id == rid
    rs.snooze(rid, 10, now_ms=t0 + 21 * 60_000)
    assert rs.next_wake_ms(t0 + 21 * 60_000) == t0 + 31 * 60_000
    assert rs.complete(rid) is None and rs.get(rid).status == "done"


def test_recurring_next_occurrence(store):
    rs = ReminderService(store)
    rid = rs.add(parse("har roz raat 10 baje dawai", now=NOW), status="pending")
    nid = rs.complete(rid)
    assert rs.get(nid).due_at == int(datetime(2026, 10, 28, 22, 0, tzinfo=Z).timestamp() * 1000)


def test_agenda(store):
    rs = ReminderService(store)
    a = rs.add(parse("remind me in 20 minutes to check oven", now=NOW), status="pending")
    rs.add(parse("parso shaam 6 baje meeting", now=NOW), status="pending")
    t = rs.add(parse_task("buy milk"), status="pending")
    _, eod, _ = local_day_bounds(NOW)
    assert [r["id"] for r in rs.agenda(eod)] == [a, t]


def _seed(store):
    t = int(NOW.replace(hour=10).timestamp() * 1000)
    n1 = store.add_note("met Ravi about the loan papers", created=t)
    n2 = store.add_note("doctor said walk 30 min daily", created=t + 1000)
    return n1, n2


def test_summary_extractive_when_hot(store):
    _seed(store)
    s = arun(generate_daily_summary(store, NOW, llm=StubLLM(), policy=SummaryPolicy(thermal_stage=2)))
    assert s["mode"] == "extractive" and len(s["highlights"]) == 2
    assert all(h["source_ids"] for h in s["highlights"])


def test_summary_llm_validates_citations(store):
    n1, n2 = _seed(store)
    reply = json.dumps({"highlights": [{"text": "Loan papers with Ravi", "source_ids": [n1, "bogus"]},
                                       {"text": "Invented", "source_ids": ["bogus"]}]})
    s = arun(generate_daily_summary(store, NOW, llm=StubLLM(reply=reply)))
    assert s["mode"] == "llm" and s["highlights"] == [{"text": "Loan papers with Ravi", "source_ids": [n1]}]
    cites = store.conn.execute("SELECT cited_item_id FROM citations WHERE interaction_id=?", (s["item_id"],)).fetchall()
    assert [c[0] for c in cites] == [n1]


def test_summary_refuses_cloud_llm(store):
    _seed(store)

    class CloudLLM(StubLLM):
        def info(self):
            return EngineInfo("x", "0", Locality.CLOUD, ("en",))
    with pytest.raises(CloudNotAllowed):
        arun(generate_daily_summary(store, NOW, llm=CloudLLM()))
