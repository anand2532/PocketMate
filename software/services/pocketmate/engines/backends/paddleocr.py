"""PaddleOCR (PP-OCR) backend (§6.4) via RapidOCR's ONNX runtime port (`rapidocr_onnxruntime`),
or the `paddleocr` package if present. Devanagari recognition model selection is a TODO pending
the model pack (§13). Not exercised on x86 CI."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence

from ..types import EngineError, EngineInfo, ImageRef, Locality, OCRBlock, OCRResult, RequestContext


class PaddleOCR:
    def __init__(self, model_dir: str = "/opt/pm/models/ocr", **_: object) -> None:
        self.model_dir = model_dir
        self._impl = None
        self._kind = ""

    def info(self) -> EngineInfo:
        return EngineInfo("pp-ocr", self._kind or "unloaded", Locality.LOCAL, ("en", "hi"))

    async def load(self) -> None:
        try:
            from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-not-found]
            self._impl, self._kind = await asyncio.to_thread(RapidOCR), "rapidocr"
            return
        except ImportError:
            pass
        try:
            from paddleocr import PaddleOCR as _P  # type: ignore[import-not-found]
            self._impl, self._kind = await asyncio.to_thread(_P, lang="hi"), "paddleocr"
        except ImportError as e:
            raise EngineError("neither rapidocr_onnxruntime nor paddleocr installed") from e

    async def unload(self) -> None:
        self._impl = None

    async def health(self) -> bool:
        return self._impl is not None

    async def recognize(self, ctx: RequestContext, image: ImageRef, langs: Sequence[str] = ("en", "hi"),
                        mode: str = "document") -> OCRResult:
        if self._impl is None:
            raise EngineError("not loaded")
        t0 = time.monotonic()
        if self._kind == "rapidocr":
            res, _ = await asyncio.to_thread(self._impl, image.path)
            items = [(r[0], r[1], float(r[2])) for r in (res or [])]
        else:
            res = await asyncio.to_thread(self._impl.ocr, image.path)
            items = [(r[0], r[1][0], float(r[1][1])) for page in (res or []) for r in (page or [])]
        blocks = []
        for box, text, conf in items:
            xs = [int(p[0]) for p in box]
            ys = [int(p[1]) for p in box]
            blocks.append(OCRBlock(text, (min(xs), min(ys), max(xs), max(ys)), conf))
        blocks.sort(key=lambda b: (b.bbox[1] // 20, b.bbox[0]))
        return OCRResult(tuple(blocks), "\n".join(b.text for b in blocks), None,
                         int((time.monotonic() - t0) * 1000))
