import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def store(tmp_path):
    from pocketmate.memory.store import MemoryStore
    s = MemoryStore(tmp_path / "m.db", load_vec=False)
    yield s
    s.close()


def arun(coro, timeout=10):
    return asyncio.run(asyncio.wait_for(coro, timeout))
