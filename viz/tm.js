// BF -> 8-symbol Turing machine, mirrored from compiler/bf_to_tm.py.
// Produces a TM and a stepper that yields successive (state, head, tape) snapshots.

const CELL_MAX = 7;
const ALPHABET = Array.from({ length: CELL_MAX + 1 }, (_, i) => i);

// AST nodes.
function parseBF(src) {
  const root = [];
  const stack = [root];
  for (const ch of src) {
    const top = stack[stack.length - 1];
    if (ch === "+") top.push({ op: "Inc" });
    else if (ch === "-") top.push({ op: "Dec" });
    else if (ch === ">") top.push({ op: "Right" });
    else if (ch === "<") top.push({ op: "Left" });
    else if (ch === ".") top.push({ op: "Put" });
    else if (ch === ",") top.push({ op: "Get" });
    else if (ch === "[") {
      const loop = { op: "Loop", body: [] };
      top.push(loop);
      stack.push(loop.body);
    } else if (ch === "]") {
      if (stack.length === 1) throw new Error("unbalanced ]");
      stack.pop();
    }
  }
  if (stack.length !== 1) throw new Error("unbalanced [");
  return root;
}

function flatten(ast, pc = 0) {
  const out = [];
  let cur = pc;
  for (const node of ast) {
    out.push({ pc: cur, node });
    cur += 1;
    if (node.op === "Loop") {
      const { items, next } = flatten(node.body, cur);
      cur = next;
      out.push(...items);
      out.push({ pc: cur, node: { op: "ENDLOOP" } });
      cur += 1;
    }
  }
  return { items: out, next: cur };
}

function loopPairs(flat) {
  const stack = [];
  const pairs = new Map();
  for (const { pc, node } of flat) {
    if (node.op === "Loop") stack.push(pc);
    else if (node.op === "ENDLOOP") {
      const open = stack.pop();
      pairs.set(open, pc);
      pairs.set(pc, open);
    }
  }
  if (stack.length) throw new Error("unclosed loop");
  return pairs;
}

const stateName = (pc, role = "enter") => `pc${pc}_${role}`;

function compileBF(src) {
  const ast = parseBF(src);
  const { items: flat, next: total } = flatten(ast);
  const pairs = loopPairs(flat);
  const halt = "halt";
  const nextPcState = (pc) => {
    for (const f of flat) if (f.pc > pc) return stateName(f.pc);
    return halt;
  };
  const trans = new Map();
  const key = (s, v) => `${s}|${v}`;
  for (const { pc, node } of flat) {
    const s = stateName(pc);
    const nxt = nextPcState(pc);
    const set = (v, nextState, write, move) => trans.set(key(s, v), { nextState, write, move });
    if (node.op === "Inc") for (const v of ALPHABET) set(v, nxt, (v + 1) % (CELL_MAX + 1), "S");
    else if (node.op === "Dec") for (const v of ALPHABET) set(v, nxt, (v - 1 + CELL_MAX + 1) % (CELL_MAX + 1), "S");
    else if (node.op === "Right") for (const v of ALPHABET) set(v, nxt, v, "R");
    else if (node.op === "Left") for (const v of ALPHABET) set(v, nxt, v, "L");
    else if (node.op === "Put" || node.op === "Get") for (const v of ALPHABET) set(v, nxt, v, "S");
    else if (node.op === "Loop") {
      const afterClose = nextPcState(pairs.get(pc));
      const bodyFirst = nextPcState(pc);
      for (const v of ALPHABET) set(v, v === 0 ? afterClose : bodyFirst, v, "S");
    } else if (node.op === "ENDLOOP") {
      const open = pairs.get(pc);
      for (const v of ALPHABET) set(v, stateName(open), v, "S");
    }
  }
  return {
    transitions: trans,
    initialState: flat.length ? stateName(0) : halt,
    halt,
    flat,
  };
}

function tmTrace(tm, tapeSize = 48, maxSteps = 4000) {
  const tape = new Array(tapeSize).fill(0);
  let head = 0;
  let state = tm.initialState;
  const history = [{ state, head, tape: tape.slice() }];
  for (let s = 0; s < maxSteps && state !== tm.halt; s++) {
    const cell = tape[head] ?? 0;
    const t = tm.transitions.get(`${state}|${cell}`);
    if (!t) break;
    tape[head] = t.write;
    state = t.nextState;
    if (t.move === "R") head = Math.min(tapeSize - 1, head + 1);
    else if (t.move === "L") head = Math.max(0, head - 1);
    history.push({ state, head, tape: tape.slice() });
  }
  return history;
}

// CELL_MAX defined above
