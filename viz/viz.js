// Synchronized multi-layer visualization for rule-110-compiler.
//
// Four panes: BF source, TM trace, CTS evolution, R110 spacetime.
// Global step `t` drives all of them (each pane interprets t in its own units).
// Slider, play/pause, step-forward/back, per-pane step counters, collision overlay
// in r110, real TM trace (not BF-alias).

// Classic-script load order (see index.html): colors.js → gliders.js → tm.js → viz.js.
// All referenced identifiers are file-scope globals from those scripts.

const RULE_110 = {
  "111": 0, "110": 1, "101": 1, "100": 0,
  "011": 1, "010": 1, "001": 1, "000": 0,
};

function r110Step(state, useEther) {
  const next = new Array(state.length);
  for (let i = 0; i < state.length; i++) {
    const l = i > 0 ? state[i-1] : (useEther ? etherAt(i-1) : 0);
    const c = state[i];
    const r = i < state.length - 1 ? state[i+1] : (useEther ? etherAt(i+1) : 0);
    next[i] = RULE_110[`${l}${c}${r}`];
  }
  return next;
}

function r110History(initial, steps, useEther) {
  const h = [initial.slice()];
  for (let t = 0; t < steps; t++) h.push(r110Step(h[h.length-1], useEther));
  return h;
}

// --- Brainfuck reference interpreter (for BF pane PC/tape display) ---

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

function parseR110IC(text, width) {
  const t = text.trim();
  if (/^[01]+$/.test(t)) {
    return { state: t.split("").map(c => c === "1" ? 1 : 0), placements: [], useEther: false };
  }
  return { ...buildICFromPlacements(t, width), useEther: true };
}

// --- Collision detection: project each glider worldline, find overlapping rows ---

function detectCollisions(placements, steps, width) {
  if (!placements || placements.length < 2) return [];
  const tracks = placements.map((p, i) => {
    const g = p.glider;
    const minOff = Math.min(...g.delta.map(d => d[0]));
    const maxOff = Math.max(...g.delta.map(d => d[0]));
    return { idx: i, g, anchor: p.anchor, minOff, maxOff, disp: g.displacement };
  });
  const events = [];
  for (let s = 0; s < steps; s++) {
    for (let i = 0; i < tracks.length; i++) {
      const ti = tracks[i];
      const li = ti.anchor + s * ti.disp + ti.minOff;
      const ri = ti.anchor + s * ti.disp + ti.maxOff;
      for (let j = i + 1; j < tracks.length; j++) {
        const tj = tracks[j];
        const lj = tj.anchor + s * tj.disp + tj.minOff;
        const rj = tj.anchor + s * tj.disp + tj.maxOff;
        if (ri >= lj && rj >= li) {
          const mid = Math.round(((Math.max(li, lj) + Math.min(ri, rj)) / 2));
          if (mid >= 0 && mid < width) {
            events.push({ step: s, cell: mid, a: ti.g.name, b: tj.g.name, pairKey: `${i}-${j}` });
          }
        }
      }
    }
  }
  // Collapse consecutive same-pair events into representative start rows.
  const seen = new Map();
  const out = [];
  for (const e of events) {
    const last = seen.get(e.pairKey);
    if (last !== undefined && e.step - last <= 1) {
      seen.set(e.pairKey, e.step);
      continue;
    }
    seen.set(e.pairKey, e.step);
    out.push(e);
  }
  return out;
}

// --- Canvas DPR fit ---

function fitCanvas(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth || 600;
  const h = canvas.clientHeight || 200;
  const want_w = Math.max(1, Math.floor(w * dpr));
  const want_h = Math.max(1, Math.floor(h * dpr));
  if (canvas.width !== want_w || canvas.height !== want_h) {
    canvas.width = want_w;
    canvas.height = want_h;
  }
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, w, h };
}

// --- Rendering ---

function drawBF(canvas, src, trace, t) {
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  if (!trace || !trace.history.length) return;
  const stepIdx = Math.min(t, trace.history.length - 1);
  const step = trace.history[stepIdx];

  const charW = 14;
  const charH = 22;
  const perLine = Math.max(8, Math.floor((w - 16) / charW));
  for (let i = 0; i < src.length; i++) {
    const col = i % perLine;
    const row = Math.floor(i / perLine);
    const x = 8 + col * charW;
    const y = 8 + row * charH;
    const op = src[i];
    const isCur = trace.ops[step.pc] && trace.ops[step.pc].src_index === i;
    if (isCur) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(x - 1, y, charW, charH - 4);
    }
    ctx.fillStyle = isCur ? "#000" : (BF_OP[op] || "#555");
    ctx.font = "bold 16px ui-monospace, monospace";
    ctx.textBaseline = "top";
    ctx.fillText(op, x, y + 2);
  }

  const tapeY = 8 + Math.ceil(src.length / perLine) * charH + 14;
  const cellW = Math.max(10, Math.min(20, Math.floor((w - 16) / 32)));
  ctx.font = "10px ui-monospace, monospace";
  ctx.fillStyle = "#888";
  ctx.fillText("tape:", 8, tapeY - 12);
  for (let c = 0; c < 32; c++) {
    const v = step.tape[c] || 0;
    const x = 8 + c * cellW;
    ctx.fillStyle = v === 0 ? "#1a1a1a" : `rgba(125,221,255,${0.25 + 0.1 * v})`;
    ctx.fillRect(x, tapeY, cellW - 1, cellW - 1);
    if (c === step.dp) {
      ctx.strokeStyle = ACCENT;
      ctx.lineWidth = 2;
      ctx.strokeRect(x, tapeY, cellW - 1, cellW - 1);
    }
    if (v > 0) {
      ctx.fillStyle = "#fff";
      ctx.font = "9px ui-monospace, monospace";
      ctx.textBaseline = "middle";
      ctx.textAlign = "center";
      ctx.fillText(String(v), x + (cellW - 1) / 2, tapeY + (cellW - 1) / 2);
      ctx.textAlign = "start";
      ctx.textBaseline = "alphabetic";
    }
  }
}

function drawTM(canvas, tmHistory, t) {
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  if (!tmHistory || !tmHistory.length) {
    ctx.fillStyle = "#666";
    ctx.font = "12px ui-monospace, monospace";
    ctx.fillText("(no TM trace — empty/invalid BF)", 10, 20);
    return;
  }
  const tapeW = tmHistory[0].tape.length;
  const cellSize = Math.max(4, Math.min(18, Math.floor((w - 16) / tapeW)));
  const rowH = Math.max(cellSize, 8);
  const rows = Math.max(1, Math.floor((h - 20) / rowH));
  const curStep = Math.min(t, tmHistory.length - 1);
  const startStep = Math.max(0, curStep - rows + 1);

  for (let r = 0; r < rows; r++) {
    const stepIdx = startStep + r;
    if (stepIdx >= tmHistory.length) break;
    const step = tmHistory[stepIdx];
    const y = 8 + r * rowH;
    for (let c = 0; c < tapeW; c++) {
      const v = step.tape[c] || 0;
      ctx.fillStyle = v === 0 ? "#101010" : `rgba(230,230,230,${0.25 + 0.1 * v})`;
      ctx.fillRect(8 + c * cellSize, y, cellSize - 1, rowH - 1);
      if (c === step.head) {
        ctx.strokeStyle = ACCENT;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(8 + c * cellSize, y, cellSize - 1, rowH - 1);
      }
    }
    if (stepIdx === curStep) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(2, y, 3, rowH - 1);
    }
  }
}

function drawCTS(canvas, spec, trace, t) {
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  if (!trace.length) return;
  const maxLen = Math.max(...trace.map(s => s.tape.length), 1);
  const cellW = Math.max(4, Math.min(14, Math.floor((w - 60) / maxLen)));
  const rowH = 16;
  const rows = Math.max(1, Math.floor((h - 8) / rowH));
  const curStep = Math.min(t, trace.length - 1);
  const startStep = Math.max(0, curStep - rows + 1);

  for (let r = 0; r < rows; r++) {
    const stepIdx = startStep + r;
    if (stepIdx >= trace.length) break;
    const step = trace[stepIdx];
    const y = 4 + r * rowH;
    ctx.fillStyle = "#777";
    ctx.font = "10px ui-monospace, monospace";
    ctx.textBaseline = "top";
    ctx.fillText(`a${step.cursor}`, 6, y + 3);
    for (let i = 0; i < step.tape.length; i++) {
      ctx.fillStyle = step.tape[i] === "Y" ? CTS_Y : CTS_N;
      ctx.fillRect(48 + i * cellW, y + 2, cellW - 1, rowH - 4);
    }
    if (stepIdx === curStep) {
      ctx.strokeStyle = ACCENT;
      ctx.lineWidth = 1.5;
      ctx.strokeRect(46, y + 1, w - 50, rowH - 2);
    }
  }
}

function drawR110(canvas, hist, t, placements, useEther, collisions) {
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, w, h);
  if (!hist || !hist.length) return;
  const width = hist[0].length;
  const cellSize = Math.max(2, Math.min(6, Math.floor((w - 16) / width)));
  const rows = Math.max(1, Math.floor((h - 16) / cellSize));
  const curStep = Math.min(t, hist.length - 1);
  const startStep = Math.max(0, curStep - rows + 1);

  for (let r = 0; r < rows; r++) {
    const stepIdx = startStep + r;
    if (stepIdx >= hist.length) break;
    const row = hist[stepIdx];
    const y = 8 + r * cellSize;
    for (let c = 0; c < width; c++) {
      let color;
      if (useEther) {
        const expected = etherAt(c + 4 * stepIdx);
        if (row[c] === expected) {
          color = expected ? "#262626" : "#111";
        } else {
          color = row[c] ? "#e8e8e8" : "#666";
        }
      } else {
        color = row[c] ? CELL_ON : "#0a0a0a";
      }
      ctx.fillStyle = color;
      ctx.fillRect(8 + c * cellSize, y, cellSize, cellSize);
    }

    if (placements && placements.length) {
      for (const p of placements) {
        const projectedAnchor = p.anchor + stepIdx * p.glider.displacement;
        const minOff = Math.min(...p.glider.delta.map(d => d[0]));
        const maxOff = Math.max(...p.glider.delta.map(d => d[0]));
        const left = projectedAnchor + minOff;
        const right = projectedAnchor + maxOff;
        if (right >= 0 && left < width) {
          ctx.strokeStyle = p.glider.color;
          ctx.lineWidth = 1;
          ctx.globalAlpha = 0.5;
          ctx.strokeRect(
            8 + Math.max(0, left) * cellSize,
            y,
            (Math.min(width, right + 1) - Math.max(0, left)) * cellSize,
            cellSize
          );
          ctx.globalAlpha = 1;
        }
      }
    }

    if (stepIdx === curStep) {
      ctx.fillStyle = ACCENT;
      ctx.fillRect(2, y, 3, cellSize);
    }
  }

  if (collisions && collisions.length) {
    ctx.font = "bold 10px ui-monospace, monospace";
    for (const c of collisions) {
      if (c.step < startStep) continue;
      if (c.step >= startStep + rows) continue;
      const r = c.step - startStep;
      const y = 8 + r * cellSize + cellSize / 2;
      const x = 8 + c.cell * cellSize + cellSize / 2;
      ctx.strokeStyle = "#fe5";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, Math.max(5, cellSize + 1), 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = "#fe5";
      ctx.fillText(`${c.a}×${c.b}`, x + 8, y + 4);
    }
  }
}

// --- App state ---

const state = {
  bfSrc: "+++[->+<]",
  ctsText: "appendants: YN, N\ntape: YY",
  r110IC: "A@30, Ebar@140",
  t: 0,
  maxT: 200,
  playing: false,
  speed: 200,
};

let bfCache = null;
let tmCache = null;
let ctsSpecCache = null;
let ctsTraceCache = null;
let r110HistCache = null;
let r110PlacementsCache = [];
let r110UseEther = true;
let r110Collisions = [];
const R110_WIDTH = 220;
const R110_STEPS = 260;

function recompute() {
  try { bfCache = bfTrace(state.bfSrc, 4000); }
  catch (e) { bfCache = { ops: [], history: [{ pc: 0, dp: 0, tape: new Array(64).fill(0) }] }; }

  try {
    const tm = compileBF(state.bfSrc);
    tmCache = tmTrace(tm, 48, 4000);
  } catch (e) {
    tmCache = [{ state: "halt", head: 0, tape: new Array(48).fill(0) }];
  }

  try {
    ctsSpecCache = ctsParseSpec(state.ctsText);
    ctsTraceCache = ctsTrace(ctsSpecCache, 400);
  } catch (e) {
    ctsSpecCache = { appendants: [], tape: [] };
    ctsTraceCache = [{ tape: [], cursor: 0 }];
  }

  try {
    const parsed = parseR110IC(state.r110IC, R110_WIDTH);
    r110UseEther = parsed.useEther;
    r110PlacementsCache = parsed.placements;
    r110HistCache = r110History(parsed.state, R110_STEPS, parsed.useEther);
    r110Collisions = detectCollisions(r110PlacementsCache, R110_STEPS, R110_WIDTH);
  } catch (e) {
    r110HistCache = [new Array(R110_WIDTH).fill(0)];
    r110PlacementsCache = [];
    r110UseEther = false;
    r110Collisions = [];
  }

  state.maxT = Math.max(
    bfCache.history.length,
    tmCache.length,
    ctsTraceCache.length,
    r110HistCache.length,
  );
}

function paneStep(t, len) {
  if (len <= 1) return 0;
  const scaled = Math.round((t / Math.max(1, state.maxT - 1)) * (len - 1));
  return Math.min(len - 1, Math.max(0, scaled));
}

function render() {
  const t = state.t;
  const bfStep = paneStep(t, bfCache.history.length);
  const tmStepIdx = paneStep(t, tmCache.length);
  const ctsStepIdx = paneStep(t, ctsTraceCache.length);
  const r110StepIdx = paneStep(t, r110HistCache.length);

  drawBF(document.getElementById("bfCanvas"), state.bfSrc, bfCache, bfStep);
  drawTM(document.getElementById("tmCanvas"), tmCache, tmStepIdx);
  drawCTS(document.getElementById("ctsCanvas"), ctsSpecCache, ctsTraceCache, ctsStepIdx);
  drawR110(document.getElementById("r110Canvas"), r110HistCache, r110StepIdx, r110PlacementsCache, r110UseEther, r110Collisions);

  document.getElementById("tValue").textContent = `${t} / ${Math.max(0, state.maxT - 1)}`;
  document.getElementById("tSlider").max = String(Math.max(0, state.maxT - 1));
  document.getElementById("tSlider").value = String(t);
  document.getElementById("bfStep").textContent = String(bfStep);
  document.getElementById("bfMax").textContent = String(bfCache.history.length - 1);
  document.getElementById("tmStep").textContent = String(tmStepIdx);
  document.getElementById("tmMax").textContent = String(tmCache.length - 1);
  document.getElementById("tmState").textContent = tmCache[tmStepIdx]?.state ?? "—";
  document.getElementById("ctsStep").textContent = String(ctsStepIdx);
  document.getElementById("ctsMax").textContent = String(ctsTraceCache.length - 1);
  document.getElementById("ctsCursor").textContent = `a${ctsTraceCache[ctsStepIdx]?.cursor ?? 0}`;
  document.getElementById("r110Step").textContent = String(r110StepIdx);
  document.getElementById("r110Max").textContent = String(r110HistCache.length - 1);
  document.getElementById("r110Collisions").textContent = String(r110Collisions.length);
}

const DEMOS = {
  hello: { bf: "+++[->+<]", cts: "appendants: YN, N\ntape: YY", r110: "A@30, Ebar@140" },
  move:  { bf: "+++++[->+<]", cts: "appendants: YN, N\ntape: YYY", r110: "C@30, A@80, Ebar@180" },
  add:   { bf: "++>++[<+>-]", cts: "appendants: YN, N\ntape: YYN", r110: "A@40, A@80, Ebar@150" },
  cts_id:  { bf: "+", cts: "appendants: Y\ntape: YYYY", r110: "B@40, C@120, D@180" },
  cts_dup: { bf: "+", cts: "appendants: YY, _\ntape: Y", r110: "A@30, B@80, C@140, Ebar@200" },
  r110_chaos:   { bf: "+", cts: "appendants: YN, N\ntape: YY", r110: "00100110100110011001011100110010100110011001011100110010011" },
  r110_gliders: { bf: "+", cts: "appendants: YN, N\ntape: YY", r110: "A@20, B@60, C@100, D@140, Ebar@200" },
  r110_collision: { bf: "+", cts: "appendants: YN, N\ntape: YY", r110: "C@40, Ebar@170" },
};

let playTimer = null;
function setPlaying(on) {
  state.playing = on;
  const btn = document.getElementById("playBtn");
  btn.textContent = on ? "❙❙ pause" : "▶ play";
  if (playTimer) { clearInterval(playTimer); playTimer = null; }
  if (on) {
    playTimer = setInterval(() => {
      if (state.t >= state.maxT - 1) { setPlaying(false); return; }
      state.t += 1;
      render();
    }, state.speed);
  }
}

function loadDemo(name) {
  const d = DEMOS[name];
  if (!d) return;
  state.bfSrc = d.bf;
  state.ctsText = d.cts;
  state.r110IC = d.r110;
  state.t = 0;
  document.getElementById("bfInput").value = state.bfSrc;
  document.getElementById("ctsInput").value = state.ctsText;
  document.getElementById("r110Input").value = state.r110IC;
  recompute();
  render();
}

function init() {
  document.getElementById("bfInput").value = state.bfSrc;
  document.getElementById("ctsInput").value = state.ctsText;
  document.getElementById("r110Input").value = state.r110IC;

  document.getElementById("bfInput").addEventListener("input", e => { state.bfSrc = e.target.value; state.t = 0; recompute(); render(); });
  document.getElementById("ctsInput").addEventListener("input", e => { state.ctsText = e.target.value; state.t = 0; recompute(); render(); });
  document.getElementById("r110Input").addEventListener("input", e => { state.r110IC = e.target.value; state.t = 0; recompute(); render(); });

  document.getElementById("tSlider").addEventListener("input", e => { state.t = parseInt(e.target.value, 10) || 0; render(); });
  document.getElementById("demoSelect").addEventListener("change", e => {
    if (!e.target.value) return;
    loadDemo(e.target.value);
    e.target.value = "";
  });
  document.getElementById("playBtn").addEventListener("click", () => setPlaying(!state.playing));
  document.getElementById("stepFwdBtn").addEventListener("click", () => {
    if (state.t < state.maxT - 1) { state.t += 1; render(); }
  });
  document.getElementById("stepBackBtn").addEventListener("click", () => {
    if (state.t > 0) { state.t -= 1; render(); }
  });
  document.getElementById("resetBtn").addEventListener("click", () => { state.t = 0; setPlaying(false); render(); });
  document.getElementById("speedSelect").addEventListener("change", e => {
    state.speed = parseInt(e.target.value, 10);
    if (state.playing) { setPlaying(false); setPlaying(true); }
  });

  document.addEventListener("keydown", e => {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    if (e.key === " ") { e.preventDefault(); setPlaying(!state.playing); }
    else if (e.key === "ArrowRight") { if (state.t < state.maxT - 1) { state.t += 1; render(); } }
    else if (e.key === "ArrowLeft") { if (state.t > 0) { state.t -= 1; render(); } }
    else if (e.key === "Home") { state.t = 0; render(); }
    else if (e.key === "End") { state.t = state.maxT - 1; render(); }
  });

  window.addEventListener("resize", () => render());

  recompute();
  render();
}

document.addEventListener("DOMContentLoaded", init);
