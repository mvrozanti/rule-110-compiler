"""Check that viz/gliders.js mirrors core/gliders.py byte-for-byte.

If somebody updates the python glider catalog and forgets to update the JS
mirror, this test catches it. We parse the JS file with light regex; if the
format drifts substantially the test fails loudly.
"""

import re
from pathlib import Path

from core.gliders import ALL_VERIFIED
from core.ether import ETHER


VIZ_GLIDERS_PATH = Path(__file__).resolve().parent.parent / "viz" / "gliders.js"


def _parse_js_object(src: str, name: str) -> dict:
    pat = re.compile(rf"{name}:\s*\{{(.*?)\}},\s*\n", re.DOTALL)
    m = pat.search(src)
    if not m:
        raise AssertionError(f"{name} not found in viz/gliders.js")
    body = m.group(1)
    out = {}
    for field in ("period", "displacement", "left_phase"):
        fm = re.search(rf"{field}:\s*(-?\d+)", body)
        if not fm:
            raise AssertionError(f"{name}.{field} not found")
        out[field] = int(fm.group(1))
    dm = re.search(r"delta:\s*\[(.*?)\]\s*,\s*color", body, re.DOTALL)
    if not dm:
        raise AssertionError(f"{name}.delta not found")
    pairs = re.findall(r"\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]", dm.group(1))
    out["delta"] = tuple((int(a), int(b)) for a, b in pairs)
    return out


def _js_ether(src: str) -> tuple[int, ...]:
    m = re.search(r"export const ETHER\s*=\s*\[(.*?)\];", src)
    if not m:
        raise AssertionError("ETHER not found in viz/gliders.js")
    return tuple(int(x.strip()) for x in m.group(1).split(",") if x.strip())


def test_viz_ether_matches_core():
    src = VIZ_GLIDERS_PATH.read_text()
    assert _js_ether(src) == ETHER


def test_viz_gliders_match_core_definitions():
    src = VIZ_GLIDERS_PATH.read_text()
    for g in ALL_VERIFIED:
        js = _parse_js_object(src, g.name)
        assert js["period"] == g.period_t, f"{g.name} period mismatch"
        assert js["displacement"] == g.displacement, f"{g.name} displacement mismatch"
        assert js["left_phase"] == g.left_phase, f"{g.name} left_phase mismatch"
        assert js["delta"] == g.delta, f"{g.name} delta mismatch"
