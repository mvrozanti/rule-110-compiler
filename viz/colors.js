// Color palette for the rule-110-compiler visualization.
//
// Discipline (per AGENTS.md visualization caution):
//   - One unambiguous color per concept.
//   - Ether is dim gray so it recedes; computation pops.
//   - Same-family colors for same-role entities (tape data, control, movers).
//
// Until the cross-layer linking is wired (after TM->CTS lands), each pane
// renders with its own consistent palette and the same `t` slider drives
// all four.

const BG = "#0b0b0b";
const ETHER_OFF = "#1a1a1a";
const ETHER_ON = "#333";
const CELL_OFF = "#0b0b0b";
const CELL_ON = "#e8e8e8";

const ACCENT = "#7df";

const CTS_Y = "#fc0";
const CTS_N = "#f0f";

const BF_OP = {
  "+": "#4ade80",
  "-": "#f87171",
  ">": "#fbbf24",
  "<": "#fb923c",
  "[": "#22d3ee",
  "]": "#06b6d4",
  ".": "#e879f9",
  ",": "#c026d3",
};

const GLIDER = {
  A: "#fc0",
  B: "#f80",
  C1: "#0ff",
  C2: "#0ee",
  D1: "#80ff80",
  D2: "#80ff40",
  E: "#f0f",
  Ebar: "#c0f",
};

const NAMED_COLORS = [
  "#60a5fa", "#a78bfa", "#f472b6", "#fb7185",
  "#fbbf24", "#34d399", "#22d3ee", "#facc15",
  "#94a3b8", "#fdba74", "#a3e635", "#22c55e",
];

const stateColorCache = new Map();
function stateColor(name) {
  if (stateColorCache.has(name)) return stateColorCache.get(name);
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0;
  const c = NAMED_COLORS[h % NAMED_COLORS.length];
  stateColorCache.set(name, c);
  return c;
}
