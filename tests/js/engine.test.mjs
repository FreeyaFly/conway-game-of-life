// Run with: node --test tests/js/
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

import {
  CycleDetector,
  latticeAdjacency,
  neighbourCounts,
  parseRule,
  randomGenerator,
  randomState,
  rewire,
  ruleToString,
  step,
} from "../../web/engine.js";

const fixtures = JSON.parse(
  readFileSync(new URL("../fixtures/patterns.json", import.meta.url), "utf-8"),
);

function grid(rows, cols, cells) {
  const state = new Uint8Array(rows * cols);
  for (const [r, c] of cells) state[r * cols + c] = 1;
  return state;
}

for (const fixture of fixtures.cases) {
  test(`shared fixture: ${fixture.name}`, () => {
    const [rows, cols] = fixture.shape;
    const adj = latticeAdjacency(rows, cols, fixture.boundary);
    const rule = parseRule(fixture.rule);
    let state = grid(rows, cols, fixture.initial);
    for (let t = 0; t < fixture.steps; t++) state = step(state, rule, adj);
    assert.deepEqual([...state], [...grid(rows, cols, fixture.expected)]);
  });
}

test("rule strings round-trip", () => {
  for (const text of ["B3/S23", "B36/S23", "B/S", "B2/S"]) {
    assert.equal(ruleToString(parseRule(text)), text);
  }
  assert.equal(ruleToString(parseRule(" b3/s23 ")), "B3/S23");
  assert.throws(() => parseRule("B9/S23"));
  assert.throws(() => parseRule("23/3"));
});

test("lattice degrees", () => {
  const torus = latticeAdjacency(5, 6, "torus");
  const fixed = latticeAdjacency(4, 5, "fixed");
  const degree = (adj, i) => adj.offsets[i + 1] - adj.offsets[i];
  for (let i = 0; i < torus.n; i++) assert.equal(degree(torus, i), 8);
  assert.equal(degree(fixed, 0), 3);
  assert.equal(degree(fixed, 1), 5);
  assert.equal(degree(fixed, 6), 8);
});

test("step does not modify its input", () => {
  const adj = latticeAdjacency(8, 8);
  const state = randomState(adj.n, 0.4, randomGenerator(1));
  const copy = state.slice();
  step(state, parseRule("B3/S23"), adj);
  assert.deepEqual(state, copy);
});

test("rewiring keeps every degree and the number of edges", () => {
  const adj = latticeAdjacency(16, 16);
  const wired = rewire(adj, 1, randomGenerator(2));
  for (let i = 0; i < wired.n; i++) {
    const list = [...wired.neighbours.subarray(wired.offsets[i], wired.offsets[i + 1])];
    assert.equal(list.length, 8);
    assert.ok(!list.includes(i), "no self-loop");
    assert.equal(new Set(list).size, 8, "no duplicate edge");
  }
  let kept = 0;
  for (let i = 0; i < adj.n; i++) {
    const before = new Set(adj.neighbours.subarray(adj.offsets[i], adj.offsets[i + 1]));
    for (const k of wired.neighbours.subarray(wired.offsets[i], wired.offsets[i + 1])) {
      if (before.has(k)) kept += 1;
    }
  }
  assert.ok(kept < 0.2 * adj.neighbours.length, "most edges moved");
});

test("rewiring with beta 0 changes nothing", () => {
  const adj = latticeAdjacency(10, 10);
  const same = rewire(adj, 0, randomGenerator(3));
  const counts = neighbourCounts(randomState(adj.n, 0.5, randomGenerator(4)), adj);
  const counts2 = neighbourCounts(randomState(adj.n, 0.5, randomGenerator(4)), same);
  assert.deepEqual(counts, counts2);
});

test("cycle detector finds a blinker's period", () => {
  const adj = latticeAdjacency(5, 5, "fixed");
  const rule = parseRule("B3/S23");
  let state = grid(5, 5, [[2, 1], [2, 2], [2, 3]]);
  const detector = new CycleDetector();
  let result = null;
  for (let t = 0; t < 10 && !result; t++) {
    result = detector.push(state);
    state = step(state, rule, adj);
  }
  assert.deepEqual(result, { transient: 0, period: 2 });
});

test("a glider on an 8 x 8 torus has period 32", () => {
  const adj = latticeAdjacency(8, 8);
  const rule = parseRule("B3/S23");
  let state = grid(8, 8, [[1, 2], [2, 3], [3, 1], [3, 2], [3, 3]]);
  const detector = new CycleDetector();
  let result = null;
  while (!result) {
    result = detector.push(state);
    state = step(state, rule, adj);
  }
  assert.deepEqual(result, { transient: 0, period: 32 });
});
