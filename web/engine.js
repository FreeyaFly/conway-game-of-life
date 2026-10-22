// Life-like cellular automata on any topology: next = f(state, A · state).
// A JavaScript port of the `life` Python package, checked against the same
// fixtures (tests/fixtures/patterns.json).

const RULE_RE = /^B([0-8]*)\/S([0-8]*)$/i;

/** Parse a rule string such as "B3/S23" (case-insensitive, digits 0-8). */
export function parseRule(text) {
  const match = RULE_RE.exec(String(text).trim());
  if (!match) throw new Error(`not a B/S rule string: ${text}`);
  const digits = (s) => new Set([...s].map(Number));
  return { birth: digits(match[1]), survive: digits(match[2]) };
}

/** Format a rule back into B/S notation. */
export function ruleToString(rule) {
  const join = (set) => [...set].sort((a, b) => a - b).join("");
  return `B${join(rule.birth)}/S${join(rule.survive)}`;
}

/**
 * Adjacency of a rows x cols lattice with the Moore neighbourhood, in CSR form:
 * the neighbours of cell i are neighbours[offsets[i] .. offsets[i + 1]).
 * Cell (r, c) has index r * cols + c. "torus" wraps; "fixed" drops outside cells.
 */
export function latticeAdjacency(rows, cols, boundary = "torus") {
  if (boundary !== "torus" && boundary !== "fixed") {
    throw new Error(`unknown boundary: ${boundary}`);
  }
  const n = rows * cols;
  const lists = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const list = [];
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (dr === 0 && dc === 0) continue;
          let nr = r + dr;
          let nc = c + dc;
          if (boundary === "torus") {
            nr = (nr + rows) % rows;
            nc = (nc + cols) % cols;
          } else if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
            continue;
          }
          list.push(nr * cols + nc);
        }
      }
      lists.push(list);
    }
  }
  return fromLists(lists, n);
}

function fromLists(lists, n) {
  const offsets = new Int32Array(n + 1);
  for (let i = 0; i < n; i++) offsets[i + 1] = offsets[i] + lists[i].length;
  const neighbours = new Int32Array(offsets[n]);
  for (let i = 0; i < n; i++) neighbours.set(lists[i], offsets[i]);
  return { n, offsets, neighbours };
}

/** Number of live neighbours of every node. */
export function neighbourCounts(state, adj) {
  const counts = new Uint8Array(adj.n);
  const { offsets, neighbours } = adj;
  for (let i = 0; i < adj.n; i++) {
    let k = 0;
    for (let j = offsets[i]; j < offsets[i + 1]; j++) k += state[neighbours[j]];
    counts[i] = k;
  }
  return counts;
}

/** Apply the rule to precomputed neighbour counts; the input array is not modified. */
export function stepFromCounts(state, counts, rule) {
  const next = new Uint8Array(state.length);
  for (let i = 0; i < state.length; i++) {
    const k = counts[i];
    next[i] = state[i] ? (rule.survive.has(k) ? 1 : 0) : rule.birth.has(k) ? 1 : 0;
  }
  return next;
}

/** Advance every cell at once; the input array is not modified. */
export function step(state, rule, adj) {
  return stepFromCounts(state, neighbourCounts(state, adj), rule);
}

/** Small seeded random generator (mulberry32), returning floats in [0, 1). */
export function randomGenerator(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Random state with each cell alive with probability `density`. */
export function randomState(n, density, random) {
  const state = new Uint8Array(n);
  for (let i = 0; i < n; i++) state[i] = random() < density ? 1 : 0;
  return state;
}

/**
 * Degree-preserving rewiring: mark a fraction `beta` of the (undirected) edges
 * and shuffle them by double-edge swaps (a,b),(c,d) -> (a,d),(c,b), rejecting
 * self-loops and duplicate edges. Every node keeps its number of neighbours.
 * Mirrors life.networks.rewire; the random streams differ, so networks do too.
 */
export function rewire(adj, beta, random, swapsPerEdge = 10) {
  const edges = [];
  for (let i = 0; i < adj.n; i++) {
    for (let j = adj.offsets[i]; j < adj.offsets[i + 1]; j++) {
      const k = adj.neighbours[j];
      if (i < k) edges.push([i, k]);
    }
  }
  const key = (a, b) => (a < b ? `${a},${b}` : `${b},${a}`);
  const present = new Set(edges.map(([a, b]) => key(a, b)));
  if (present.size !== edges.length) throw new Error("rewire needs a simple graph");
  const marked = [];
  for (let e = 0; e < edges.length; e++) if (random() < beta) marked.push(e);
  if (marked.length >= 2) {
    for (let s = 0; s < swapsPerEdge * marked.length; s++) {
      const p = marked[Math.floor(random() * marked.length)];
      const q = marked[Math.floor(random() * marked.length)];
      if (p === q) continue;
      const [a, b] = edges[p];
      let [c, d] = edges[q];
      if (random() < 0.5) [c, d] = [d, c];
      if (a === d || c === b) continue;
      const k1 = key(a, d);
      const k2 = key(c, b);
      if (k1 === k2 || present.has(k1) || present.has(k2)) continue;
      present.delete(key(a, b));
      present.delete(key(c, d));
      present.add(k1);
      present.add(k2);
      edges[p] = [a, d];
      edges[q] = [c, b];
    }
  }
  const lists = Array.from({ length: adj.n }, () => []);
  for (const [a, b] of edges) {
    lists[a].push(b);
    lists[b].push(a);
  }
  return fromLists(lists, adj.n);
}

/** Compact string key of a state, for cycle detection. */
export function stateKey(state) {
  let out = "";
  for (let i = 0; i < state.length; i += 16) {
    let word = 0;
    for (let b = 0; b < 16 && i + b < state.length; b++) word |= state[i + b] << b;
    out += String.fromCharCode(word);
  }
  return out;
}

/**
 * Watches a trajectory and reports where it first repeats a state:
 * { transient, period }. Gives up after `limit` states to bound memory.
 */
export class CycleDetector {
  constructor(limit = 5000) {
    this.limit = limit;
    this.reset();
  }

  reset() {
    this.seen = new Map();
    this.t = 0;
    this.result = null;
    this.gaveUp = false;
  }

  push(state) {
    if (this.result || this.gaveUp) return this.result;
    const key = stateKey(state);
    const first = this.seen.get(key);
    if (first !== undefined) {
      this.result = { transient: first, period: this.t - first };
    } else if (this.seen.size >= this.limit) {
      this.gaveUp = true;
      this.seen = new Map();
    } else {
      this.seen.set(key, this.t);
    }
    this.t += 1;
    return this.result;
  }
}
