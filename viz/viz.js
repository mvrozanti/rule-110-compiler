// Synchronized multi-layer visualization for rule-110-compiler.
//
// Four panes. A global step `t` drives all of them (each pane interprets t
// in its own units for now; full cross-layer linking lands once tm->cts is
// online and we can build a unified time map).
//
// Pane sources:
//   bf:   parsed BF source, reference interpreter trace (PC + tape).
//   tm:   compiled TM, step()-by-step.
//   cts:  hand-entered CTS spec, step()-by-step.
//   r110: hand-entered initial bitstring, evolved with zero boundary.

import {
  ACCENT, BG, BF_OP, CELL_OFF, CELL_ON, CTS_N, CTS_Y,
  ETHER_OFF, ETHER_ON, stateColor,
} from "./colors.js";

const RULE_110 = {
  "111": 0, "110": 1, "101": 1, "100": 0,
  "011": 1, "010": 1, "001": 1, "000": 0,
};

function r110Step(state) {
  const next = new Array(state.length);
  for (let i = 0; i < state.length; i++) {
    const l = i > 0 ? state[i-1] : 0;
    const c = state[i];
    const r = i < state.length - 1 ? state[i+1] : 0;
    next[i] = RULE_110[`${l}${c}${r}`];
  }
  return next;
}

function r110History(initial, steps) {
  const h = [initial.slice()];
  for (let t = 0; t < steps; t++) h.push(r110Step(h[h.length-1]));
  return h;
}

// --- Brainfuck reference interpreter ---

function bfParse(src) {
  const ops = [];
  const stack = [];
  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    if ("+-><.,".includes(ch)) ops.push({ op: ch, src_index: i });
    else if (ch === "[") { ops.push({ op: "[", src_index: i, match: -1 }); stack.push(ops.length - 1); }
    else if (ch === "]") {
      const m = stack.pop();
      if (m === undefined) throw new Error("unbalanced ]");
      ops.push({ op: "]", src_index: i, match: m });
      ops[m].match = ops.length - 1;
    }
  }
  if (stack.length) throw new Error("unbalanced [");
  return ops;
}

const CELL_MAX_BF = 7;

function bfTrace(src, maxSteps = 4000) {
  const ops = bfParse(src);
  const tape = new Array(64).fill(0);
  let dp = 0;
  let pc = 0;
  const history = [{ pc, dp, tape: tape.slice() }];
  for (let s = 0; s < maxSteps && pc < ops.length; s++) {
    const { op, match } = ops[pc];
    switch (op) {
      case "+": tape[dp] = (tape[dp] + 1) % (CELL_MAX_BF + 1); pc++; break;
      case "-": tape[dp] = (tape[dp] - 1 + CELL_MAX_BF + 1) % (CELL_MAX_BF + 1); pc++; break;
      case ">": dp = Math.min(tape.length - 1, dp + 1); pc++; break;
      case "<": dp = Math.max(0, dp - 1); pc++; break;
      case "[": if (tape[dp] === 0) pc = match + 1; else pc++; break;
      case "]": if (tape[dp] !== 0) pc = match + 1; else pc++; break;
      case ".": pc++; break;
      case ",": pc++; break;
    }
    history.push({ pc, dp, tape: tape.slice() });
  }
  return { ops, history };
}

// --- Cyclic tag system ---

function ctsParseSpec(text) {
  const lines = text.trim().split("\n").map(l => l.trim()).filter(l => l && !l.startsWith("#"));
  if (lines.length < 2) throw new Error("CTS spec needs 'tape: <tape>' and 'appendants: <list>'");
  let tape = null;
  const appendants = [];
  for (const line of lines) {
    if (line.startsWith("tape:")) tape = line.slice(5).trim();
    else if (line.startsWith("appendants:")) {
      const parts = line.slice(11).split(",").map(s => s.trim());
      for (const p of parts) appendants.push(p === "_" ? "" : p);
    }
  }
  if (tape === null || appendants.length === 0) throw new Error("CTS spec missing tape: or appendants:");
  for (const c of tape) if (!"YN".includes(c)) throw new Error(`CTS tape symbol ${c} not in {Y,N}`);
  for (const a of appendants) for (const c of a) if (!"YN".includes(c)) throw new Error(`CTS appendant symbol ${c} not in {Y,N}`);
  return { tape: tape.split(""), appendants };
}

function ctsTrace(spec, maxSteps = 200) {
  let tape = spec.tape.slice();
  let cursor = 0;
  const history = [{ tape: tape.slice(), cursor }];
  for (let s = 0; s < maxSteps && tape.length > 0; s++) {
    const head = tape[0];
    const rest = tape.slice(1);
    if (head === "Y") tape = rest.concat(spec.appendants[cursor].split(""));
    else tape = rest;
    cursor = (cursor + 1) % spec.appendants.length;
    history.push({ tape: tape.slice(), cursor });
  }
  return history;
}

// --- Rule 110 IC parsing ---

function parseR110IC(text) {
  return text.trim().split("").map(c => c === "1" ? 1 : 0);
}

// --- Rendering ---

function drawBF(ctx, src, trace, t, w, h) {
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  const step = trace.history[Math.min(t, trace.history.length - 1)];
  const charW = 14;
  const lineH = 20;
  for (let i = 0; i < src.length; i++) {
    const x = (i % Math.floor(w / charW)) * charW + 6;
    const y = Math.floor(i / Math.floor(w / charW)) * lineH + 20;
    const op = src[i];
    const color = BF_OP[op] || "#555";
    if (trace.ops[step.pc] && trace.ops[step.pc].src_index === i) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(x - 2, y - 14, charW, lineH - 2);
    }
    ctx.fillStyle = color;
    ctx.font = "16px monospace";
    ctx.fillText(op, x, y);
  }
  ctx.fillStyle = "#999";
  ctx.font = "12px monospace";
  ctx.fillText(`step ${Math.min(t, trace.history.length - 1)} / ${trace.history.length - 1}  pc=${step.pc}  dp=${step.dp}  tape=[${step.tape.slice(0, 12).join(",")}]`, 6, h - 8);
}

function drawTM(ctx, src, trace, t, w, h) {
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  const tapeW = 32;
  const cellSize = Math.min(20, Math.floor((w - 20) / tapeW));
  const rows = Math.min(trace.history.length, Math.floor((h - 30) / cellSize));
  const startStep = Math.max(0, Math.min(t, trace.history.length - 1) - rows + 1);
  for (let r = 0; r < rows; r++) {
    const stepIdx = startStep + r;
    if (stepIdx >= trace.history.length) break;
    const step = trace.history[stepIdx];
    const y = r * cellSize + 10;
    for (let c = 0; c < tapeW; c++) {
      const v = step.tape[c] || 0;
      ctx.fillStyle = v === 0 ? CELL_OFF : `rgba(232,232,232,${0.3 + 0.1*v})`;
      ctx.fillRect(c * cellSize + 8, y, cellSize - 1, cellSize - 1);
      if (c === step.dp) {
        ctx.strokeStyle = ACCENT;
        ctx.lineWidth = 2;
        ctx.strokeRect(c * cellSize + 8, y, cellSize - 1, cellSize - 1);
      }
    }
    if (stepIdx === Math.min(t, trace.history.length - 1)) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(2, y, 4, cellSize - 1);
    }
  }
  ctx.fillStyle = "#999";
  ctx.font = "12px monospace";
  ctx.fillText(`tm step ${Math.min(t, trace.history.length - 1)} / ${trace.history.length - 1}`, 6, h - 8);
}

function drawCTS(ctx, spec, trace, t, w, h) {
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  const maxLen = Math.max(...trace.map(s => s.tape.length), 1);
  const cellW = Math.max(4, Math.min(14, Math.floor((w - 100) / maxLen)));
  const rows = Math.min(trace.length, Math.floor((h - 40) / 18));
  const startStep = Math.max(0, Math.min(t, trace.length - 1) - rows + 1);
  for (let r = 0; r < rows; r++) {
    const stepIdx = startStep + r;
    if (stepIdx >= trace.length) break;
    const step = trace[stepIdx];
    const y = r * 18 + 14;
    for (let i = 0; i < step.tape.length; i++) {
      ctx.fillStyle = step.tape[i] === "Y" ? CTS_Y : CTS_N;
      ctx.fillRect(i * cellW + 60, y, cellW - 1, 16);
    }
    ctx.fillStyle = "#aaa";
    ctx.font = "11px monospace";
    ctx.fillText(`a${step.cursor}`, 8, y + 12);
    if (stepIdx === Math.min(t, trace.length - 1)) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(48, y, 4, 16);
    }
  }
  ctx.fillStyle = "#999";
  ctx.font = "12px monospace";
  ctx.fillText(`cts step ${Math.min(t, trace.length - 1)} / ${trace.length - 1}   appendants: ${spec.appendants.map(a => a || "_").join(", ")}`, 6, h - 8);
}

function drawR110(ctx, hist, t, w, h) {
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  const width = hist[0].length;
  const cellSize = Math.min(8, Math.floor((w - 20) / width));
  const rows = Math.min(hist.length, Math.floor((h - 30) / cellSize));
  const startStep = Math.max(0, Math.min(t, hist.length - 1) - rows + 1);
  for (let r = 0; r < rows; r++) {
    const stepIdx = startStep + r;
    if (stepIdx >= hist.length) break;
    const row = hist[stepIdx];
    const y = r * cellSize + 10;
    for (let c = 0; c < width; c++) {
      ctx.fillStyle = row[c] ? CELL_ON : ETHER_OFF;
      ctx.fillRect(c * cellSize + 8, y, cellSize - 1, cellSize - 1);
    }
    if (stepIdx === Math.min(t, hist.length - 1)) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(2, y, 4, cellSize - 1);
    }
  }
  ctx.fillStyle = "#999";
  ctx.font = "12px monospace";
  ctx.fillText(`r110 step ${Math.min(t, hist.length - 1)} / ${hist.length - 1}`, 6, h - 8);
}

// --- App state ---

const state = {
  bfSrc: "+++[->+<]",
  ctsText: "appendants: YN, N\ntape: YY",
  r110IC: "00000000000000000000000000000000111000000000000000000000000000000",
  t: 0,
  maxT: 200,
};

let bfTraceCache = null;
let bfTMTraceCache = null;
let ctsSpecCache = null;
let ctsTraceCache = null;
let r110HistCache = null;

function recompute() {
  try {
    bfTraceCache = bfTrace(state.bfSrc, 4000);
  } catch (e) { bfTraceCache = { ops: [], history: [{pc:0, dp:0, tape:[]}] }; }
  try {
    bfTMTraceCache = bfTraceCache;
  } catch (e) { bfTMTraceCache = null; }
  try {
    ctsSpecCache = ctsParseSpec(state.ctsText);
    ctsTraceCache = ctsTrace(ctsSpecCache, 400);
  } catch (e) { ctsSpecCache = { appendants: [], tape: [] }; ctsTraceCache = [{tape:[], cursor:0}]; }
  try {
    r110HistCache = r110History(parseR110IC(state.r110IC), 200);
  } catch (e) { r110HistCache = [parseR110IC("0")]; }
  state.maxT = Math.max(
    bfTraceCache.history.length,
    ctsTraceCache.length,
    r110HistCache.length,
  );
}

function render() {
  const t = state.t;
  drawBF(document.getElementById("bfCanvas").getContext("2d"), state.bfSrc, bfTraceCache, t, document.getElementById("bfCanvas").width, document.getElementById("bfCanvas").height);
  drawTM(document.getElementById("tmCanvas").getContext("2d"), state.bfSrc, bfTMTraceCache, t, document.getElementById("tmCanvas").width, document.getElementById("tmCanvas").height);
  drawCTS(document.getElementById("ctsCanvas").getContext("2d"), ctsSpecCache, ctsTraceCache, t, document.getElementById("ctsCanvas").width, document.getElementById("ctsCanvas").height);
  drawR110(document.getElementById("r110Canvas").getContext("2d"), r110HistCache, t, document.getElementById("r110Canvas").width, document.getElementById("r110Canvas").height);
  document.getElementById("tValue").textContent = String(t);
  document.getElementById("tSlider").max = String(state.maxT - 1);
}

function init() {
  document.getElementById("bfInput").value = state.bfSrc;
  document.getElementById("ctsInput").value = state.ctsText;
  document.getElementById("r110Input").value = state.r110IC;

  document.getElementById("bfInput").addEventListener("input", e => { state.bfSrc = e.target.value; recompute(); render(); });
  document.getElementById("ctsInput").addEventListener("input", e => { state.ctsText = e.target.value; recompute(); render(); });
  document.getElementById("r110Input").addEventListener("input", e => { state.r110IC = e.target.value; recompute(); render(); });
  document.getElementById("tSlider").addEventListener("input", e => { state.t = parseInt(e.target.value, 10); render(); });

  recompute();
  render();
}

document.addEventListener("DOMContentLoaded", init);
