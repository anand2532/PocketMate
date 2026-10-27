"""Consent tokens (§6.1/§6.7 hard gate).

pm-core mints a token after the user approves dialog 12b for ONE request: bound to request_id,
scope, provider, and sha256 of the exact payload bytes; <= 60 s TTL (monotonic); HMAC-SHA256
signed with the consent-gate key (generated at first boot on the LUKS data partition, never
exported). pm-cloud verifies and burns it (single use) before any byte leaves the device."""
from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from ..engines.types import ConsentRequired, ConsentToken
from ..util.ids import uuid7

MAX_TTL_S = 60.0
SCOPES = ("asr", "llm", "ocr", "vision", "tts")


def payload_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_or_create_key(path: str | Path = "/var/lib/pm/secrets/consent.key") -> bytes:
    p = Path(path)
    if p.exists():
        return p.read_bytes()
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    key = os.urandom(32)
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(key)
    return key


def _msg(t: ConsentToken) -> bytes:
    return "|".join([str(t.token_id), t.scope, str(t.request_id), t.provider, t.payload_sha256,
                     f"{t.expires_at:.6f}"]).encode()


class ConsentGate:
    def __init__(self, key: bytes, *, clock: Callable[[], float] = time.monotonic,
                 on_burn: Callable[[ConsentToken], None] | None = None) -> None:
        if len(key) < 32:
            raise ValueError("consent key must be >= 32 bytes")
        self._key = key
        self._clock = clock
        self._used: dict[uuid.UUID, float] = {}
        self._on_burn = on_burn

    def mint(self, *, scope: str, request_id: uuid.UUID, provider: str, payload: bytes,
             ttl_s: float = MAX_TTL_S) -> ConsentToken:
        if scope not in SCOPES:
            raise ValueError(f"bad scope {scope}")
        ttl = min(ttl_s, MAX_TTL_S)
        unsigned = ConsentToken(uuid7(), scope, request_id, provider, payload_hash(payload),  # type: ignore[arg-type]
                                self._clock() + ttl, b"")
        sig = hmac.new(self._key, _msg(unsigned), hashlib.sha256).digest()
        return ConsentToken(unsigned.token_id, unsigned.scope, unsigned.request_id, unsigned.provider,
                            unsigned.payload_sha256, unsigned.expires_at, sig)

    def verify_and_burn(self, token: ConsentToken | None, *, scope: str, request_id: uuid.UUID, provider: str,
                        payload: bytes) -> ConsentToken:
        """Raise ConsentRequired unless every binding matches; then mark the token used."""
        if token is None:
            raise ConsentRequired("no consent token")
        good = hmac.new(self._key, _msg(token), hashlib.sha256).digest()
        if not hmac.compare_digest(good, token.signature):
            raise ConsentRequired("bad signature")
        now = self._clock()
        self._gc(now)
        if token.token_id in self._used:
            raise ConsentRequired("token already used")
        if now > token.expires_at:
            raise ConsentRequired("token expired")
        if token.request_id != request_id:
            raise ConsentRequired("request_id mismatch")
        if token.scope != scope:
            raise ConsentRequired("scope mismatch")
        if token.provider != provider:
            raise ConsentRequired("provider mismatch")
        if not hmac.compare_digest(token.payload_sha256, payload_hash(payload)):
            raise ConsentRequired("payload differs from what the user approved")
        self._used[token.token_id] = token.expires_at
        if self._on_burn:
            self._on_burn(token)
        return token

    def _gc(self, now: float) -> None:
        for k, exp in list(self._used.items()):
            if exp + MAX_TTL_S < now:      # expired tokens can't verify anyway; keep a margin
                del self._used[k]
