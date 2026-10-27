import asyncio
import json
import uuid

import pytest
from conftest import arun

from pocketmate.cloud.consent import MAX_TTL_S, ConsentGate
from pocketmate.cloud.providers.base import HttpResponse, NoTransport
from pocketmate.cloud.providers.gemini import GeminiProvider
from pocketmate.cloud.providers.openai import OpenAIProvider
from pocketmate.cloud.providers.sarvam import SarvamProvider
from pocketmate.cloud.service import DELETE_RETRY_WINDOW_MS, CloudService, CloudTooSlow
from pocketmate.engines.types import ConsentRequired

KEY = b"k" * 32


class Clock:
    t = 100.0

    def __call__(self):
        return self.t


def test_gate_binds_everything():
    clk = Clock()
    g = ConsentGate(KEY, clock=clk)
    rid = uuid.uuid4()
    tok = g.mint(scope="asr", request_id=rid, provider="sarvam", payload=b"audio", ttl_s=600)
    assert tok.expires_at == clk.t + MAX_TTL_S                       # TTL clamped to 60 s
    for kw, why in [({"scope": "llm"}, "scope"), ({"request_id": uuid.uuid4()}, "request_id"),
                    ({"provider": "openai"}, "provider"), ({"payload": b"audio2"}, "payload")]:
        args = {"scope": "asr", "request_id": rid, "provider": "sarvam", "payload": b"audio", **kw}
        with pytest.raises(ConsentRequired, match=why):
            g.verify_and_burn(tok, **args)
    g.verify_and_burn(tok, scope="asr", request_id=rid, provider="sarvam", payload=b"audio")
    with pytest.raises(ConsentRequired, match="already used"):
        g.verify_and_burn(tok, scope="asr", request_id=rid, provider="sarvam", payload=b"audio")


def test_gate_expiry_and_forgery():
    clk = Clock()
    g = ConsentGate(KEY, clock=clk)
    rid = uuid.uuid4()
    tok = g.mint(scope="asr", request_id=rid, provider="sarvam", payload=b"a")
    clk.t += 61
    with pytest.raises(ConsentRequired, match="expired"):
        g.verify_and_burn(tok, scope="asr", request_id=rid, provider="sarvam", payload=b"a")
    other = ConsentGate(b"x" * 32, clock=clk).mint(scope="asr", request_id=rid, provider="sarvam", payload=b"a")
    with pytest.raises(ConsentRequired, match="signature"):
        g.verify_and_burn(other, scope="asr", request_id=rid, provider="sarvam", payload=b"a")
    with pytest.raises(ConsentRequired):
        g.verify_and_burn(None, scope="asr", request_id=rid, provider="sarvam", payload=b"a")


def test_provider_terms_and_blockers():
    s = SarvamProvider("key")
    assert not s.supports_deletion and s.setup_blockers() == ["training_optout"]
    assert s.terms().contract_status == "unconfirmed" and s.terms().training_use == "opt_out_unconfirmed"
    assert "indefinitely" in s.terms().retention_summary
    s2 = SarvamProvider("sk-SECRET", training_optout_confirmed=True, retention_days_confirmed=0)
    assert s2.setup_blockers() == [] and s2.terms().user_configured_retention_days == 0
    assert "sk-SECRET" not in repr(s2)
    g = GeminiProvider("k")
    assert "billing_enabled_project" in g.setup_blockers()
    with pytest.raises(PermissionError):
        g.build_request("llm", b"[]")
    o = OpenAIProvider("k")
    body = json.loads(o.build_request("llm", b'[{"role":"user","content":"hi"}]').body)
    assert body["store"] is False


def _svc(store, providers, **kw):
    return CloudService(store, ConsentGate(KEY), providers, **kw)


def test_dialog_shows_unknowns_and_contract_note(store):
    svc = _svc(store, {"sarvam": SarvamProvider("k")})
    d = svc.consent_dialog("sarvam", "asr", b"x" * 10)
    assert d["contract_note"] == "Terms not yet confirmed by contract"
    assert "Unknown" in d["deletion"] and d["blockers"] == ["training_optout"]
    with pytest.raises(ConsentRequired, match="setup incomplete"):
        svc.grant(provider_id="sarvam", scope="asr", request_id=uuid.uuid4(), payload=b"x")


def test_send_without_token_is_blocked_and_logged(store):
    svc = _svc(store, {"sarvam": SarvamProvider("k", training_optout_confirmed=True)})
    with pytest.raises(ConsentRequired):
        arun(svc.send(provider_id="sarvam", scope="asr", request_id=uuid.uuid4(), payload=b"x", token=None))
    assert store.consent_audit()[0]["event"] == "cloud_error"


def test_default_transport_sends_nothing(store):
    svc = _svc(store, {"sarvam": SarvamProvider("k", training_optout_confirmed=True)})
    rid = uuid.uuid4()
    tok = svc.grant(provider_id="sarvam", scope="asr", request_id=rid, payload=b"pcm")
    with pytest.raises(NoTransport):
        arun(svc.send(provider_id="sarvam", scope="asr", request_id=rid, payload=b"pcm", token=tok))


def _fake_openai(responses):
    calls = []

    async def transport(req):
        calls.append((req.method, req.url))
        return responses.get((req.method, req.url.rsplit("/", 1)[-1]), HttpResponse(200, b'{"id":"resp_1"}'))
    return transport, calls


def test_send_record_and_delete_verified(store):
    tr, calls = _fake_openai({("GET", "resp_1"): HttpResponse(404, b"")})
    svc = _svc(store, {"openai": OpenAIProvider("k", transport=tr)})
    rid = uuid.uuid4()
    payload = b'[{"role":"user","content":"hi"}]'
    tok = svc.grant(provider_id="openai", scope="llm", request_id=rid, payload=payload)
    r = arun(svc.send(provider_id="openai", scope="llm", request_id=rid, payload=payload, token=tok))
    assert r.remote_ids == ["resp_1"]
    assert svc.request_delete(request_id=str(rid)) == 1
    out = arun(svc.process_deletions())
    assert out == {str(rid): "deleted"} and ("DELETE", "https://api.openai.com/v1/responses/resp_1") in calls
    ev = [e["event"] for e in store.consent_audit()]
    assert ev[:4] == ["cloud_delete_confirmed", "cloud_delete_requested", "cloud_sent", "cloud_granted"]
    assert store.verify_consent_chain()[0]
    detail = json.loads(store.conn.execute(
        "SELECT detail FROM consent_log WHERE event='cloud_granted'").fetchone()[0])
    assert detail["terms_reviewed_on"] == "2026-10-21" and detail["contract_status"] == "public_terms_only"


def test_delete_retries_then_fails_after_7_days(store):
    tr, _ = _fake_openai({("DELETE", "resp_1"): HttpResponse(500, b"")})
    svc = _svc(store, {"openai": OpenAIProvider("k", transport=tr)})
    rid = uuid.uuid4()
    tok = svc.grant(provider_id="openai", scope="llm", request_id=rid, payload=b"[]")
    arun(svc.send(provider_id="openai", scope="llm", request_id=rid, payload=b"[]", token=tok))
    svc.request_delete(provider_id="openai")
    t0 = store.conn.execute("SELECT delete_deadline FROM cloud_requests").fetchone()[0] - DELETE_RETRY_WINDOW_MS
    assert arun(svc.process_deletions(now=t0 + 1)) == {str(rid): "pending"}
    assert arun(svc.process_deletions(now=t0 + 2)) == {}                    # backoff
    assert arun(svc.process_deletions(now=t0 + DELETE_RETRY_WINDOW_MS + 1)) == {str(rid): "failed"}


def test_unsupported_deletion_logged(store):
    async def tr(req):
        return HttpResponse(200, b"{}")
    svc = _svc(store, {"sarvam": SarvamProvider("k", training_optout_confirmed=True, transport=tr)})
    rid = uuid.uuid4()
    tok = svc.grant(provider_id="sarvam", scope="asr", request_id=rid, payload=b"pcm")
    arun(svc.send(provider_id="sarvam", scope="asr", request_id=rid, payload=b"pcm", token=tok))
    svc.request_delete(provider_id="sarvam")
    assert arun(svc.process_deletions()) == {str(rid): "unsupported"}
    assert store.consent_audit()[0]["event"] == "cloud_delete_unsupported"


def test_latency_cap(store):
    async def slow(req):
        await asyncio.sleep(1)
        return HttpResponse(200, b"{}")
    svc = _svc(store, {"openai": OpenAIProvider("k", transport=slow)}, latency_cap_s=0.05)
    rid = uuid.uuid4()
    tok = svc.grant(provider_id="openai", scope="llm", request_id=rid, payload=b"[]")
    with pytest.raises(CloudTooSlow):
        arun(svc.send(provider_id="openai", scope="llm", request_id=rid, payload=b"[]", token=tok))
    assert svc.cloud_log()[0]["request_id"] == str(rid)      # tracked for deletion even though it timed out
