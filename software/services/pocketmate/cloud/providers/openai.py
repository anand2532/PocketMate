"""OpenAI / OpenAI-compatible adapter (optional plug-in). §6.7.1: always store=false; never Files or
Assistants APIs; ids recorded and deleted right after use; abuse logs up to 30 days."""
from __future__ import annotations

import json
import time
from collections.abc import Sequence

from .base import (
    BaseProvider,
    DeletionReceipt,
    HttpRequest,
    HttpResponse,
    ProviderManifest,
    ProviderTerms,
    RemoteRef,
)


class OpenAIProvider(BaseProvider):
    supports_deletion = True
    declared_retention_days = 30

    def __init__(self, api_key: str | None = None, *, base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-4o-mini", **kw) -> None:
        super().__init__(api_key, **kw)
        self.base_url, self.model = base_url.rstrip("/"), model
        host = self.base_url.split("/")[2]
        self.manifest = ProviderManifest("openai", "OpenAI (or compatible)", frozenset({"llm", "vision", "asr"}),
                                         (host,), "https://openai.com/policies/api-data-usage-policies", None,
                                         "api_key")

    def terms(self) -> ProviderTerms:
        return ProviderTerms("Copies may stay in abuse-monitoring logs for up to 30 days", 30, None, "no", "api",
                             ("https://developers.openai.com/api/docs/guides/your-data", "https://trust.openai.com/"), "2026-10-21",
                             "public_terms_only")

    def build_request(self, capability: str, payload: bytes, **opts: object) -> HttpRequest:
        if capability != "llm":
            raise NotImplementedError("prototype stub implements llm only")
        msgs = json.loads(payload)            # payload = the exact JSON the user approved
        body = json.dumps({"model": self.model, "input": msgs, "store": False}).encode()
        return HttpRequest("POST", f"{self.base_url}/responses",
                           {"Authorization": f"Bearer {self._api_key or ''}", "Content-Type": "application/json"},
                           body)

    def remote_ids(self, resp: HttpResponse) -> list[str]:
        try:
            rid = json.loads(resp.body).get("id")
        except (ValueError, AttributeError):
            return []
        return [rid] if rid else []

    async def delete(self, refs: Sequence[RemoteRef]) -> list[DeletionReceipt]:
        out = []
        for ref in refs:
            ok = True
            receipt = None
            for rid in ref.remote_ids:
                r = await self.transport(HttpRequest("DELETE", f"{self.base_url}/responses/{rid}",
                                                     {"Authorization": f"Bearer {self._api_key or ''}"}, b""))
                receipt = str(r.status)
                ok &= r.status in (200, 204, 404)
            out.append(DeletionReceipt(ref, "deleted" if ok else "failed", receipt, False, time.time()))
        return out

    async def verify_deleted(self, ref: RemoteRef) -> DeletionReceipt:
        for rid in ref.remote_ids:
            r = await self.transport(HttpRequest("GET", f"{self.base_url}/responses/{rid}",
                                                 {"Authorization": f"Bearer {self._api_key or ''}"}, b""))
            if r.status != 404:
                return DeletionReceipt(ref, "pending", str(r.status), False, time.time())
        return DeletionReceipt(ref, "deleted", "404", True, time.time())
