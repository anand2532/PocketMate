"""CloudService: hard gate -> send -> record -> deletion queue (§6.7)."""
from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from ..engines.types import ConsentRequired, ConsentToken, EngineError
from ..memory.store import MemoryStore, now_ms
from .consent import ConsentGate, payload_hash
from .providers.base import BaseProvider, RemoteRef

CLOUD_LATENCY_CAP_S = 4.0              # [PM 2026-10-21]
DELETE_RETRY_WINDOW_MS = 7 * 86_400_000  # locked UX parameter
BACKOFF_S = (60, 300, 900, 3600, 4 * 3600, 12 * 3600)


class CloudTooSlow(EngineError):
    """pm-core shows 'Cloud too slow, using on-device' and uses the local result."""


@dataclass
class CloudResult:
    request_id: uuid.UUID
    status: int
    body: bytes
    remote_ids: list[str]


class CloudService:
    def __init__(self, store: MemoryStore, gate: ConsentGate, providers: dict[str, BaseProvider], *,
                 online: Callable[[], bool] = lambda: True, egress_lease: Callable[[str], object] | None = None,
                 latency_cap_s: float = CLOUD_LATENCY_CAP_S) -> None:
        self.store, self.gate, self.providers = store, gate, providers
        self.online, self.egress_lease, self.cap = online, egress_lease, latency_cap_s
        self._last_try: dict[str, int] = {}

    def consent_dialog(self, provider_id: str, scope: str, payload: bytes) -> dict:
        """Data for UI screen 12b. Unknown fields are shown as 'Unknown' (amber), never hidden."""
        p = self.providers[provider_id]
        t = p.terms()
        return {
            "provider": p.manifest.display_name, "scope": scope, "bytes": len(payload),
            "kept": t.retention_summary or "Unknown",
            "training": t.training_use,
            "deletion": ("Can delete on request" if p.supports_deletion else
                         f"{p.manifest.display_name} keeps data for "
                         f"{t.retention_days if t.retention_days is not None else 'Unknown'} days and can't "
                         "delete on request"),
            "contract_note": None if t.contract_status == "dpa_signed" else "Terms not yet confirmed by contract",
            "sources": list(t.source_urls), "reviewed_on": t.reviewed_on, "blockers": p.setup_blockers(),
        }

    def grant(self, *, provider_id: str, scope: str, request_id: uuid.UUID, payload: bytes) -> ConsentToken:
        p = self.providers[provider_id]
        if p.setup_blockers():
            raise ConsentRequired(f"provider setup incomplete: {p.setup_blockers()}")
        tok = self.gate.mint(scope=scope, request_id=request_id, provider=provider_id, payload=payload)
        t = p.terms()
        self.store.log_consent("cloud_granted", scope=scope, provider=provider_id, request_id=str(request_id),
                               payload_sha256=tok.payload_sha256,
                               detail={"token_id": str(tok.token_id), "terms_reviewed_on": t.reviewed_on,
                                       "contract_status": t.contract_status, "training_use": t.training_use})
        return tok

    def deny(self, *, provider_id: str, scope: str, request_id: uuid.UUID) -> None:
        self.store.log_consent("cloud_denied", scope=scope, provider=provider_id, request_id=str(request_id))

    async def send(self, *, provider_id: str, scope: str, request_id: uuid.UUID, payload: bytes,
                   token: ConsentToken | None, item_id: str | None = None, **opts: object) -> CloudResult:
        p = self.providers.get(provider_id)
        if p is None:
            raise EngineError(f"unknown provider {provider_id}")
        try:
            self.gate.verify_and_burn(token, scope=scope, request_id=request_id, provider=provider_id,
                                      payload=payload)
        except ConsentRequired as e:
            self.store.log_consent("cloud_error", scope=scope, provider=provider_id, request_id=str(request_id),
                                   detail={"reason": f"gate: {e}"})
            raise
        lease = self.egress_lease("cloud") if self.egress_lease else None
        try:
            resp, rids = await asyncio.wait_for(p.send(scope, payload, **opts), timeout=self.cap)
        except TimeoutError as e:
            self.store.log_consent("cloud_error", scope=scope, provider=provider_id, request_id=str(request_id),
                                   bytes_sent=len(payload), detail={"reason": "latency_cap", "cap_s": self.cap})
            self._record(request_id, provider_id, scope, item_id, [])   # bytes may have left: track for deletion
            raise CloudTooSlow("Cloud too slow, using on-device") from e
        except EngineError as e:
            self.store.log_consent("cloud_error", scope=scope, provider=provider_id, request_id=str(request_id),
                                   detail={"reason": type(e).__name__})
            raise
        finally:
            if lease is not None and hasattr(lease, "release"):
                lease.release()
        self._record(request_id, provider_id, scope, item_id, rids)
        self.store.log_consent("cloud_sent", scope=scope, provider=provider_id, request_id=str(request_id),
                               payload_sha256=payload_hash(payload), bytes_sent=len(payload),
                               detail={"http_status": resp.status, "remote_ids": len(rids)})
        return CloudResult(request_id, resp.status, resp.body, rids)

    def _record(self, request_id: uuid.UUID, provider: str, cap: str, item_id: str | None, rids: list[str]) -> None:
        with self.store.tx() as c:
            c.execute("INSERT OR REPLACE INTO cloud_requests(request_id, provider, capability, item_id, remote_ids, "
                      "sent_at) VALUES (?,?,?,?,?,?)", (str(request_id), provider, cap, item_id, json.dumps(rids),
                                                        now_ms()))

    # ---- deletion -------------------------------------------------------------
    def request_delete(self, *, request_id: str | None = None, provider_id: str | None = None,
                       item_id: str | None = None) -> int:
        q, a = "SELECT request_id FROM cloud_requests WHERE delete_state IN ('none','failed')", []
        if request_id:
            q, a = q + " AND request_id=?", [*a, request_id]
        if provider_id:
            q, a = q + " AND provider=?", [*a, provider_id]
        if item_id:
            q, a = q + " AND item_id=?", [*a, item_id]
        rows = [r[0] for r in self.store.conn.execute(q, a)]
        dl = now_ms() + DELETE_RETRY_WINDOW_MS
        with self.store.tx() as c:
            for rid in rows:
                c.execute("UPDATE cloud_requests SET delete_state='requested', delete_deadline=? WHERE request_id=?",
                          (dl, rid))
        for rid in rows:
            r = self.store.conn.execute("SELECT provider FROM cloud_requests WHERE request_id=?", (rid,)).fetchone()
            self.store.log_consent("cloud_delete_requested", provider=r[0], request_id=rid)
        return len(rows)

    async def process_deletions(self, now: int | None = None) -> dict[str, str]:
        """One pass of the retry loop. Call while online (same egress rules). Returns {request_id: state}."""
        now = now or now_ms()
        out: dict[str, str] = {}
        if not self.online():
            return out
        rows = list(self.store.conn.execute(
            "SELECT * FROM cloud_requests WHERE delete_state IN ('requested','pending')"))
        for r in rows:
            rid, prov = r["request_id"], r["provider"]
            p = self.providers.get(prov)
            ref = RemoteRef(prov, uuid.UUID(rid), json.loads(r["remote_ids"]), "request_log")
            if p is None or not p.supports_deletion:
                self._set_state(rid, "unsupported", r["delete_attempts"])
                self.store.log_consent("cloud_delete_unsupported", provider=prov, request_id=rid)
                out[rid] = "unsupported"
                continue
            if r["delete_attempts"] and now < self._next_try(rid, r["delete_attempts"]):
                continue
            try:
                rec = (await p.delete([ref]))[0]
                if rec.status == "deleted":
                    rec = await p.verify_deleted(ref)
            except (EngineError, OSError):
                rec = None
            self._last_try[rid] = now
            if rec is not None and rec.status == "deleted" and rec.verified:
                self._set_state(rid, "deleted", r["delete_attempts"] + 1, verified=True)
                self.store.log_consent("cloud_delete_confirmed", provider=prov, request_id=rid,
                                       detail={"receipt": rec.provider_receipt})
                out[rid] = "deleted"
            elif now >= (r["delete_deadline"] or 0):
                self._set_state(rid, "failed", r["delete_attempts"] + 1)
                self.store.log_consent("cloud_delete_failed", provider=prov, request_id=rid,
                                       detail={"reason": "7-day retry window elapsed"})
                out[rid] = "failed"
            else:
                self._set_state(rid, "pending", r["delete_attempts"] + 1)
                out[rid] = "pending"
        return out

    def _next_try(self, rid: str, attempts: int) -> int:
        n = min(attempts, len(BACKOFF_S)) - 1
        return self._last_try.get(rid, 0) + BACKOFF_S[max(n, 0)] * 1000

    def _set_state(self, rid: str, state: str, attempts: int, verified: bool = False) -> None:
        with self.store.tx() as c:
            c.execute("UPDATE cloud_requests SET delete_state=?, delete_attempts=?, "
                      "verified_at=COALESCE(?, verified_at) WHERE request_id=?",
                      (state, attempts, now_ms() if verified else None, rid))

    def cloud_log(self, limit: int = 100) -> list[dict]:
        """Screen 12d."""
        return [dict(r) for r in self.store.conn.execute(
            "SELECT request_id, provider, capability, sent_at, delete_state, delete_attempts FROM cloud_requests "
            "ORDER BY sent_at DESC LIMIT ?", (limit,))]
