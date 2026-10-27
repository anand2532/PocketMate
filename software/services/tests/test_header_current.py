from pathlib import Path

from pocketmate.mcu import gen_c_header

FW = Path(__file__).resolve().parents[2] / "firmware"


def test_generated_c_header_is_current():
    assert gen_c_header.main(["--out-dir", str(FW), "--check"]) == 0, \
        "regenerate: python -m pocketmate.mcu.gen_c_header --out-dir ../firmware"
