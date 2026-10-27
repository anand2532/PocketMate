"""BYOK provider adapters (§6.7, §6.7.1). Sarvam is built-in; OpenAI and Gemini are optional plug-ins.
All are STUBS for the prototype: manifests, terms, deletion semantics and request shaping are
implemented; the HTTP transport is injected (none by default, so nothing can leave the box)."""
from .base import BaseProvider, DeletionReceipt, ProviderManifest, ProviderTerms, RemoteRef  # noqa: F401
