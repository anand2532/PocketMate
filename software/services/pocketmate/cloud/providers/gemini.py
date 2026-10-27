"""Gemini adapter (optional plug-in). §6.7.1: paid (billing-enabled) projects only - refuses
otherwise; no Files API / Grounding / caching / session resumption; 55-day abuse-log retention."""
from __future__ import annotations

import json

from .base import BaseProvider, HttpRequest, ProviderManifest, ProviderTerms


class GeminiProvider(BaseProvider):
    manifest = ProviderManifest("gemini", "Google Gemini API", frozenset({"llm", "vision"}),
                                ("generativelanguage.googleapis.com",), "https://ai.google.dev/gemini-api/terms",
                                None, "api_key")
    supports_deletion = False
    declared_retention_days = 55

    def __init__(self, api_key: str | None = None, *, billing_enabled: bool | None = None,
                 model: str = "gemini-2.0-flash", **kw) -> None:
        super().__init__(api_key, **kw)
        self.billing_enabled = billing_enabled
        self.model = model

    def terms(self) -> ProviderTerms:
        return ProviderTerms("Kept up to 55 days for abuse monitoring", 55, None, "no", "none",
                             ("https://ai.google.dev/gemini-api/terms",), "2026-10-21", "public_terms_only")

    def setup_blockers(self) -> list[str]:
        b = super().setup_blockers()
        if self.billing_enabled is not True:
            b.append("billing_enabled_project")   # unpaid tier may use data for training [A-52]
        return b

    async def validate_credentials(self) -> bool:
        return bool(self._api_key) and self.billing_enabled is True

    def build_request(self, capability: str, payload: bytes, **opts: object) -> HttpRequest:
        if self.billing_enabled is not True:
            raise PermissionError("Gemini adapter refuses non-billing projects")
        body = json.dumps({"contents": json.loads(payload)}).encode()
        return HttpRequest("POST", f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                           {"x-goog-api-key": self._api_key or "", "Content-Type": "application/json"}, body)
