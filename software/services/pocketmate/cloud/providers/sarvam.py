"""Sarvam adapter (built-in, ASR first). §6.7.1: no per-request deletion API found (2026-10-21) ->
supports_deletion=False; training opt-out is an Owner-only account toggle -> setup is blocked until
the user confirms it; DPA not signed -> contract_status 'unconfirmed'."""
from __future__ import annotations

import uuid

from .base import BaseProvider, HttpRequest, ProviderManifest, ProviderTerms

SOURCES = ("https://docs.sarvam.ai/api/platform/data-retention.md", "https://docs.sarvam.ai/api/platform/faq.md",
           "https://docs.sarvam.ai/changelog/2026/9/15.md", "https://www.sarvam.ai/privacy-policy",
           "https://www.sarvam.ai/trust-center")


class SarvamProvider(BaseProvider):
    manifest = ProviderManifest("sarvam", "Sarvam AI", frozenset({"asr"}), ("api.sarvam.ai",),
                                "https://www.sarvam.ai/privacy-policy", "IN", "api_key")
    supports_deletion = False

    def __init__(self, api_key: str | None = None, *, training_optout_confirmed: bool = False,
                 retention_days_confirmed: int | None = None, **kw) -> None:
        super().__init__(api_key, **kw)
        self.training_optout_confirmed = training_optout_confirmed
        self.declared_retention_days = retention_days_confirmed

    def terms(self) -> ProviderTerms:
        return ProviderTerms(
            retention_summary=(f"Kept per your workspace setting ({self.declared_retention_days} days)"
                               if self.declared_retention_days is not None
                               else "May be kept indefinitely (workspace retention not confirmed)"),
            retention_days=self.declared_retention_days,
            user_configured_retention_days=self.declared_retention_days,
            training_use="opt_out_confirmed" if self.training_optout_confirmed else "opt_out_unconfirmed",
            deletion="retention_only", source_urls=SOURCES, reviewed_on="2026-10-21",
            contract_status="unconfirmed")

    def setup_blockers(self) -> list[str]:
        b = super().setup_blockers()
        if not self.training_optout_confirmed:
            b.append("training_optout")      # Settings -> Organisation -> General -> Model training: off
        return b

    def build_request(self, capability: str, payload: bytes, **opts: object) -> HttpRequest:
        # VERIFY endpoint/fields against the Sarvam API reference before enabling a real transport.
        boundary = uuid.uuid4().hex
        lang = str(opts.get("language_code", "unknown"))
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"language_code\"\r\n\r\n{lang}\r\n"
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.wav\"\r\n"
                "Content-Type: audio/wav\r\n\r\n").encode() + payload + f"\r\n--{boundary}--\r\n".encode()
        return HttpRequest("POST", "https://api.sarvam.ai/speech-to-text",
                           {"api-subscription-key": self._api_key or "",
                            "Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
