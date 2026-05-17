"""Cook-faithful glider catalogue.

Distinct from `core/gliders.py`, which contains our originally-extracted
glider patterns (all measuring width 0 mod 14 by the procedure in
`tests/test_alpha_beta.py`). The ones here match Cook's Figure 5 widths:

  A   period (3, +2)   width 6   (Cook's A glider, fast right-mover)
  C2  period (7, 0)    width 3   (Cook's tape-data glider)
  Ebar period (30, -8) width 7   (Cook's moving-data glider)

A Cook-style glider has DIFFERENT ether phases on its left and right
sides. Placing it requires:

  1. The cells before the glider follow ether at the 'left phase'.
  2. The cells of the glider's delta are written explicitly.
  3. The cells AFTER the glider follow ether at left_phase + width
     (mod 14) instead of the standard continuation.

`place_cook_glider` handles steps 2 and 3; the caller is responsible
for step 1 (typically by initializing the state with `ether_window` at
phase 0 and then overlaying gliders left-to-right, propagating each
glider's width into the running phase).
"""

from dataclasses import dataclass

from core.ether import ETHER, SPATIAL_PERIOD, ether_cell


@dataclass(frozen=True)
class CookGlider:
    name: str
    period_t: int
    displacement: int
    left_phase: int
    width: int
    delta: tuple[int, ...]
    citation: str

    @property
    def extent(self) -> int:
        return len(self.delta)


A = CookGlider(
    name="A",
    period_t=3,
    displacement=2,
    left_phase=4,
    width=6,
    delta=(1, 0, 1, 1, 1, 0),
    citation="period (3, +2), Cook width 6; discovered by "
             "scripts/find_cook_variants.py with two-phase ether halo "
             "verification (left ether at phase 4, right ether at phase 10).",
)


C2 = CookGlider(
    name="C2",
    period_t=7,
    displacement=0,
    left_phase=2,
    width=3,
    delta=(1, 0, 0, 0, 0, 0),
    citation="period (7, 0) tape-data glider, Cook width 3 = C2 variant; "
             "discovered by scripts/find_cook_variants.py with two-phase "
             "ether halo verification (left phase 2, right phase 5).",
)


Ebar = CookGlider(
    name="Ebar",
    period_t=30,
    displacement=-8,
    left_phase=4,
    width=7,
    delta=(1, 1, 0, 0, 1, 1, 1),
    citation="period (30, -8) moving-data glider, Cook width 7 = Ebar; "
             "discovered by scripts/find_cook_variants.py with two-phase "
             "ether halo verification (left phase 4, right phase 11).",
)


COOK_CATALOG: dict[str, CookGlider] = {"A": A, "C2": C2, "Ebar": Ebar}


def place_cook_glider(state: list[int], anchor: int, gl: CookGlider,
                      cumulative_width: int = 0) -> tuple[int, int]:
    """Write a Cook-faithful glider into `state` at or near `anchor`.

    The left side of the glider must be at ether phase `gl.left_phase`,
    interpreted relative to the global "phase-shifted ether" specified by
    `cumulative_width` (the total Cook-width contribution of all previously
    placed gliders to the LEFT of this anchor). `state` is assumed to be
    pre-filled such that the cell at position p has value
    `ether_cell(p + cumulative_width)`.

    The function snaps `anchor` forward so that `(delta_anchor +
    cumulative_width) % 14 == gl.left_phase`, writes the glider's delta,
    then rewrites all cells from `delta_anchor + extent` to the end of
    `state` to be ether at phase `(cumulative_width + gl.width)`.

    Returns (delta_anchor, new_cumulative_width).
    """
    current_phase = (anchor + cumulative_width) % SPATIAL_PERIOD
    shift = (gl.left_phase - current_phase) % SPATIAL_PERIOD
    delta_anchor = anchor + shift

    for j, b in enumerate(gl.delta):
        pos = delta_anchor + j
        if 0 <= pos < len(state):
            state[pos] = b

    new_width = cumulative_width + gl.width
    start = delta_anchor + gl.extent
    for pos in range(start, len(state)):
        state[pos] = ether_cell(pos + new_width)

    return delta_anchor, new_width


def fresh_ether_state(width: int, phase: int = 0) -> list[int]:
    """A clean ether row of `width` cells with the cell at position 0 at
    `phase` of the ether period."""
    return [ETHER[(phase + i) % SPATIAL_PERIOD] for i in range(width)]
