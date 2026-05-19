// Verified Cook gliders, mirrored from core/gliders.py.
// Each entry: name, period, displacement, left_phase, delta (offset, value).
// To place glider G starting at absolute position p, require p % 14 == G.left_phase
// then set state[p + offset] = value for each (offset, value) in delta.

const ETHER = [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0];

function etherAt(i) {
  return ETHER[((i % 14) + 14) % 14];
}

function etherWindow(start, length) {
  const out = new Array(length);
  for (let i = 0; i < length; i++) out[i] = etherAt(start + i);
  return out;
}

const GLIDERS = {
  A: {
    name: "A", period: 3, displacement: 2, left_phase: 3,
    delta: [[0, 0], [2, 1], [3, 1]],
    color: "#fc0",
  },
  B: {
    name: "B", period: 4, displacement: -2, left_phase: 9,
    delta: [[0, 1], [1, 1], [5, 0], [6, 0], [8, 0], [9, 0],
            [10, 1], [11, 1], [14, 1], [15, 1]],
    color: "#f80",
  },
  C: {
    name: "C", period: 7, displacement: 0, left_phase: 3,
    delta: [[0, 0], [1, 0], [6, 1], [10, 1]],
    color: "#0ff",
  },
  D: {
    name: "D", period: 10, displacement: 2, left_phase: 0,
    delta: [[0, 0], [1, 0], [3, 0], [4, 0], [5, 1], [6, 1], [9, 1], [10, 1]],
    color: "#80ff80",
  },
  Ebar: {
    name: "Ebar", period: 30, displacement: -8, left_phase: 10,
    delta: [[0, 1], [2, 0], [4, 0], [8, 0], [9, 1], [11, 1], [13, 1]],
    color: "#f0f",
  },
};

function placeGlider(state, g, anchor) {
  let adjustedAnchor = anchor;
  const phaseHere = ((adjustedAnchor % 14) + 14) % 14;
  if (phaseHere !== g.left_phase) {
    adjustedAnchor += (g.left_phase - phaseHere + 14) % 14;
  }
  for (const [offset, value] of g.delta) {
    const pos = adjustedAnchor + offset;
    if (pos >= 0 && pos < state.length) {
      state[pos] = value;
    }
  }
  return { anchor: adjustedAnchor };
}

function buildICFromPlacements(spec, width) {
  const state = etherWindow(0, width);
  const placements = [];
  if (!spec || !spec.trim()) {
    return { state, placements };
  }
  for (const item of spec.split(",")) {
    const m = item.trim().match(/^(\w+)\s*@\s*(-?\d+)$/);
    if (!m) continue;
    const [, name, posStr] = m;
    const g = GLIDERS[name];
    if (!g) continue;
    const desired = parseInt(posStr, 10);
    const info = placeGlider(state, g, desired);
    placements.push({ glider: g, ...info });
  }
  return { state, placements };
}
