from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Literal

from ...engines.types import EngineError


@dataclass(frozen=True)
class ProviderManifest:
    id: str
    display_name: str
    capabilities: frozenset[Literal["asr", "llm", "ocr", "vision", "tts", "translate"]]
    endpoints: Sequence[str]
    data_policy_url: str
    region: str | None
    auth: Literal["api_key", "oauth", "none"]


@dataclass(frozen=True)
class ProviderTerms:
    retention_summary: str
    retention_days: int | None
    user_configured_retention_days: int | None
    training_use: Literal["no", "opt_out_confirmed", "opt_out_unconfirmed", "yes"]
    deletion: Literal["api", "retention_only", "none"]
    source_urls: Sequence[str]
    reviewed_on: str
    contract_status: Literal["dpa_signed", "public_terms_only", "unconfirmed"]


@dataclass(frozen=True)
class RemoteRef:
    provider: str
    request_id: uuid.UUID
    remote_ids: Sequence[str]
    kind: Literal["request_log", "uploaded_file", "transcript", "conversation", "other"]


@dataclass(frozen=True)
class DeletionReceipt:
    ref: RemoteRef
    status: Literal["deleted", "pending", "unsupported", "failed"]
    provider_receipt: str | None
    verified: bool
    checked_at: float


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: bytes


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)


Transport = Callable[[HttpRequest], Awaitable[HttpResponse]]


class NoTransport(EngineError):
    pass


async def no_transport(req: HttpRequest) -> HttpResponse:
    raise NoTransport("BYOK HTTP transport not wired in this build (prototype stub); nothing was sent")


class BaseProvider:
    manifest: ProviderManifest
    supports_deletion: bool = False
    declared_retention_days: int | None = None

    def __init__(self, api_key: str | None = None, *, transport: Transport = no_transport) -> None:
        self._api_key = api_key            # never logged; loaded from /var/lib/pm/secrets (LUKS)
        self.transport = transport

    def __repr__(self) -> str:             # keep keys out of logs/tracebacks
        return f"<{type(self).__name__} key={'set' if self._api_key else 'unset'}>"

    def terms(self) -> ProviderTerms:
        raise NotImplementedError

    def setup_blockers(self) -> list[str]:
        """Checklist items that must be confirmed before the provider can be enabled."""
        return [] if self._api_key else ["api_key"]

    async def validate_credentials(self) -> bool:
        return bool(self._api_key)

    async def estimate(self, capability: str, payload_bytes: int) -> dict:
        return {"latency_s": None, "cost": None, "note": "unknown (stub)"}

    def build_request(self, capability: str, payload: bytes, **opts: object) -> HttpRequest:
        raise NotImplementedError

    async def send(self, capability: str, payload: bytes, **opts: object) -> tuple[HttpResponse, list[str]]:
        """Called by CloudService only after the consent gate passed. Returns (response, remote_ids)."""
        if capability not in self.manifest.capabilities:
            raise EngineError(f"{self.manifest.id} has no {capability}")
        req = self.build_request(capability, payload, **opts)
        resp = await self.transport(req)
        return resp, self.remote_ids(resp)

    def remote_ids(self, resp: HttpResponse) -> list[str]:
        return []

    async def delete(self, refs: Sequence[RemoteRef]) -> list[DeletionReceipt]:
        return [DeletionReceipt(r, "unsupported", None, False, time.time()) for r in refs]

    async def verify_deleted(self, ref: RemoteRef) -> DeletionReceipt:
        return DeletionReceipt(ref, "unsupported", None, False, time.time())
