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
  stepFromCounts,
} from "./engine.js";
import { PRESETS, TEXT } from "./i18n.js";

const MIN_SIZE = 8;
const MAX_SIZE = 512;
const HISTORY = 300; // generations shown in the chart
const SLICE_DEPTH = 140; // generations shown in the space-time slice

const $ = (id) => document.getElementById(id);
const canvas = $("grid");
const context = canvas.getContext("2d");
const offscreen = document.createElement("canvas");
const offContext = offscreen.getContext("2d");
const chart = $("chart");
const chartContext = chart.getContext("2d");
const spacetime = $("spacetime");
const spacetimeContext = spacetime.getContext("2d");
const sliceImage = document.createElement("canvas");
const sliceContext = sliceImage.getContext("2d");

const sim = {
  rows: 96,
  cols: 96,
  rule: parseRule("B3/S23"),
  topology: "torus",
  beta: 0.25,
  adj: null,
  cells: null,
  twin: null, // copy with one flipped cell, or null
  generation: 0,
  running: false,
  random: randomGenerator(Date.now() & 0xffffffff),
  detector: new CycleDetector(),
  history: [], // [density, damage fraction or null, activity]
  activity: 0,
  usage: { birth: new Array(9).fill(0), survive: new Array(9).fill(0) },
  slice: [], // recent copies of one row: { cells, twin }
  sliceRow: 48,
  tab: "curves",
};

// View: `scale` is screen pixels per cell; (x, y) is where cell (0, 0) starts.
// `auto` stays true until the visitor pans or zooms; then resizing no longer refits.
const view = { scale: 6, x: 0, y: 0, width: 0, height: 0, auto: true };
let language = "en";
let panMode = false;
let spaceHeld = false;

const t = (key) => TEXT[language][key];

// ---- colours ---------------------------------------------------------------

let palette = null;
function readPalette() {
  const css = getComputedStyle(document.documentElement);
  const get = (name) => css.getPropertyValue(name).trim();
  const rgb = (name) => [0, 2, 4].map((i) => parseInt(get(name).slice(1).slice(i, i + 2), 16));
  palette = {
    alive: rgb("--alive"),
    dead: rgb("--dead"),
    damage: rgb("--damage"),
    outside: get("--panel"),
    line: get("--grid-line"),
    edge: get("--line"),
    aliveCss: get("--alive"),
    activityCss: get("--activity"),
    accent: rgb("--accent"),
    damageCss: get("--damage"),
    muted: get("--muted"),
  };
}

// ---- topology and size -----------------------------------------------------

function buildTopology() {
  const base = latticeAdjacency(sim.rows, sim.cols, sim.topology === "fixed" ? "fixed" : "torus");
  sim.adj = sim.topology === "rewired" ? rewire(base, sim.beta, sim.random) : base;
}

function resizeGrid(rows, cols) {
  const old = sim.cells;
  const next = new Uint8Array(rows * cols);
  if (old) {
    // Keep the existing pattern centred.
    const dr = Math.floor((rows - sim.rows) / 2);
    const dc = Math.floor((cols - sim.cols) / 2);
    for (let r = 0; r < sim.rows; r++) {
      for (let c = 0; c < sim.cols; c++) {
        const nr = r + dr;
        const nc = c + dc;
        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) next[nr * cols + nc] = old[r * sim.cols + c];
      }
    }
  }
  sim.rows = rows;
  sim.cols = cols;
  sim.cells = next;
  buildTopology();
  offscreen.width = cols;
  offscreen.height = rows;
  $("rows").value = rows;
  $("cols").value = cols;
  sim.sliceRow = Math.floor(rows / 2);
  $("slice-row").max = rows - 1;
  $("slice-row").value = sim.sliceRow;
  $("slice-row-value").textContent = sim.sliceRow;
  restartMeasurements();
  fitCanvasHeight();
  fitView();
}

// ---- measurements ----------------------------------------------------------

function detectorFor(n) {
  // Bound memory: each stored state takes about n / 8 bytes.
  return new CycleDetector(Math.max(200, Math.min(5000, Math.floor(40e6 / (n / 8)))));
}

function restartMeasurements() {
  sim.detector = detectorFor(sim.cells.length);
  sim.detector.push(sim.cells);
  sim.history = [];
  sim.activity = 0;
  sim.usage = { birth: new Array(9).fill(0), survive: new Array(9).fill(0) };
  sim.slice = [];
  record();
}

function liveDensity(cells) {
  let alive = 0;
  for (let i = 0; i < cells.length; i++) alive += cells[i];
  return alive / cells.length;
}

function difference() {
  if (!sim.twin) return 0;
  let d = 0;
  for (let i = 0; i < sim.cells.length; i++) d += sim.cells[i] !== sim.twin[i];
  return d;
}

function record() {
  const damage = sim.twin ? difference() / sim.cells.length : null;
  sim.history.push([liveDensity(sim.cells), damage, sim.history.length ? sim.activity : null]);
  if (sim.history.length > HISTORY) sim.history.shift();
  const start = sim.sliceRow * sim.cols;
  sim.slice.push({
    cells: sim.cells.slice(start, start + sim.cols),
    twin: sim.twin ? sim.twin.slice(start, start + sim.cols) : null,
  });
  if (sim.slice.length > SLICE_DEPTH) sim.slice.shift();
}

function touched() {
  // Any manual change starts a new trajectory.
  sim.generation = 0;
  stopTwin();
  restartMeasurements();
}

// ---- drawing ---------------------------------------------------------------

function sizeCanvas(target, ctx) {
  const box = target.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  target.width = Math.max(1, Math.round(box.width * dpr));
  target.height = Math.max(1, Math.round(box.height * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return box;
}

function fitCanvasHeight() {
  const width = canvas.getBoundingClientRect().width;
  if (!width) return;
  const cap = Math.min(window.innerHeight * 0.72, 680);
  const height = Math.max(160, Math.min(cap, (width * sim.rows) / sim.cols));
  if (Math.abs(canvas.getBoundingClientRect().height - height) > 1) canvas.style.height = `${height}px`;
}

function fitView() {
  const box = sizeCanvas(canvas, context); // the height may just have changed
  view.width = box.width;
  view.height = box.height;
  if (!view.width) return;
  view.scale = Math.min(view.width / sim.cols, view.height / sim.rows);
  view.x = (view.width - sim.cols * view.scale) / 2;
  view.y = (view.height - sim.rows * view.scale) / 2;
  view.auto = true;
  draw();
}

function draw() {
  if (!palette) readPalette();
  const image = offContext.createImageData(sim.cols, sim.rows);
  const { alive, dead, damage } = palette;
  for (let i = 0; i < sim.cells.length; i++) {
    let colourOf = sim.cells[i] ? alive : dead;
    if (sim.twin && sim.twin[i] !== sim.cells[i]) colourOf = damage;
    const p = i * 4;
    image.data[p] = colourOf[0];
    image.data[p + 1] = colourOf[1];
    image.data[p + 2] = colourOf[2];
    image.data[p + 3] = 255;
  }
  offContext.putImageData(image, 0, 0);

  context.fillStyle = palette.outside;
  context.fillRect(0, 0, view.width, view.height);
  context.imageSmoothingEnabled = false;
  const w = sim.cols * view.scale;
  const h = sim.rows * view.scale;
  context.drawImage(offscreen, view.x, view.y, w, h);
  drawGridLines(w, h);
  context.strokeStyle = palette.edge;
  context.lineWidth = 1;
  context.strokeRect(view.x - 0.5, view.y - 0.5, w + 1, h + 1);
  if (sim.tab === "spacetime") {
    // Mark the row shown in the space-time slice.
    const y = view.y + sim.sliceRow * view.scale;
    context.strokeStyle = palette.activityCss;
    context.lineWidth = 2;
    context.strokeRect(view.x - 1, y - 1, w + 2, Math.max(view.scale, 1) + 2);
  }
  showMeasurements();
  if (sim.tab === "curves") drawChart();
  if (sim.tab === "spacetime") drawSpacetime();
  if (sim.tab === "usage") drawUsage();
}

function drawGridLines(w, h) {
  // Faint lines once cells are big enough to tell apart; stronger as you zoom in.
  if (view.scale < 6) return;
  const alpha = Math.min(1, (view.scale - 6) / 14) * 0.6 + 0.25;
  const c0 = Math.max(0, Math.floor(-view.x / view.scale));
  const c1 = Math.min(sim.cols, Math.ceil((view.width - view.x) / view.scale));
  const r0 = Math.max(0, Math.floor(-view.y / view.scale));
  const r1 = Math.min(sim.rows, Math.ceil((view.height - view.y) / view.scale));
  const top = Math.max(view.y, 0);
  const bottom = Math.min(view.y + h, view.height);
  const left = Math.max(view.x, 0);
  const right = Math.min(view.x + w, view.width);
  context.save();
  context.globalAlpha = alpha;
  context.strokeStyle = palette.line;
  context.lineWidth = 1;
  context.beginPath();
  for (let c = c0; c <= c1; c++) {
    const x = Math.round(view.x + c * view.scale) + 0.5;
    context.moveTo(x, top);
    context.lineTo(x, bottom);
  }
  for (let r = r0; r <= r1; r++) {
    const y = Math.round(view.y + r * view.scale) + 0.5;
    context.moveTo(left, y);
    context.lineTo(right, y);
  }
  context.stroke();
  context.restore();
}

function showMeasurements() {
  const [density] = sim.history[sim.history.length - 1] ?? [0];
  $("generation").textContent = sim.generation;
  $("live").textContent = density.toFixed(3);
  $("activity").textContent = sim.activity.toFixed(3);
  const d = sim.detector;
  let cycle = t("searching");
  if (d.result) cycle = t("cycleFound").replace("{t}", d.result.transient).replace("{p}", d.result.period);
  else if (d.gaveUp) cycle = t("gaveUp").replace("{n}", d.limit);
  $("cycle").textContent = cycle;
  if (sim.twin) {
    const diff = difference();
    $("damage").textContent = `${diff} (${((100 * diff) / sim.cells.length).toFixed(1)} %)`;
  }
}

function drawChart() {
  const box = chart.getBoundingClientRect();
  if (!box.width) return;
  const width = box.width;
  const height = box.height;
  chartContext.clearRect(0, 0, width, height);
  if (sim.history.length < 2) return;
  let top = 0.1;
  for (const [a, b] of sim.history) top = Math.max(top, a, b ?? 0);
  top = Math.min(1, top * 1.15);
  const x = (i) => (i / (HISTORY - 1)) * width;
  const y = (v) => height - 2 - (v / top) * (height - 4);
  const series = (index, colourCss) => {
    chartContext.beginPath();
    let started = false;
    sim.history.forEach((point, i) => {
      if (point[index] === null) {
        started = false;
        return;
      }
      if (!started) chartContext.moveTo(x(i), y(point[index]));
      else chartContext.lineTo(x(i), y(point[index]));
      started = true;
    });
    chartContext.strokeStyle = colourCss;
    chartContext.lineWidth = 1.5;
    chartContext.stroke();
  };
  series(0, palette.aliveCss);
  series(2, palette.activityCss);
  series(1, palette.damageCss);
  chartContext.fillStyle = palette.muted;
  chartContext.font = "10px system-ui, sans-serif";
  chartContext.fillText(top.toFixed(2), 2, 10);
}

function drawSpacetime() {
  const box = spacetime.getBoundingClientRect();
  if (!box.width) return;
  sliceImage.width = sim.cols;
  sliceImage.height = SLICE_DEPTH;
  const image = sliceContext.createImageData(sim.cols, SLICE_DEPTH);
  const { alive, dead, damage } = palette;
  const offset = SLICE_DEPTH - sim.slice.length; // newest row at the bottom
  for (let r = 0; r < SLICE_DEPTH; r++) {
    const row = sim.slice[r - offset];
    for (let c = 0; c < sim.cols; c++) {
      let colourOf = dead;
      if (row) {
        colourOf = row.cells[c] ? alive : dead;
        if (row.twin && row.twin[c] !== row.cells[c]) colourOf = damage;
      }
      const p = (r * sim.cols + c) * 4;
      image.data[p] = colourOf[0];
      image.data[p + 1] = colourOf[1];
      image.data[p + 2] = colourOf[2];
      image.data[p + 3] = 255;
    }
  }
  sliceContext.putImageData(image, 0, 0);
  spacetimeContext.imageSmoothingEnabled = false;
  spacetimeContext.drawImage(sliceImage, 0, 0, box.width, box.height);
}

function drawUsage() {
  const fill = (rowId, counts, digits, kindKey) => {
    const row = $(rowId);
    while (row.cells.length > 1) row.deleteCell(1);
    const total = counts.reduce((a, b) => a + b, 0) || 1;
    const max = Math.max(...counts, 1);
    counts.forEach((n, k) => {
      const cell = row.insertCell();
      const share = (100 * n) / total;
      const strength = n ? Math.log10(1 + n) / Math.log10(1 + max) : 0;
      const [r, g, b] = palette.accent;
      cell.style.background = `rgba(${r}, ${g}, ${b}, ${(0.08 + 0.72 * strength).toFixed(3)})`;
      cell.textContent = n ? (share >= 1 ? share.toFixed(0) : share >= 0.01 ? share.toFixed(2) : "<.01") : "";
      cell.classList.toggle("in-rule", digits.has(k));
      cell.classList.toggle("unused", digits.has(k) && n === 0);
      let tip = t("usageTip")
        .replace("{kind}", t(kindKey))
        .replace("{k}", k)
        .replace("{n}", n)
        .replace("{p}", share.toFixed(3));
      if (digits.has(k)) tip += ` · ${t("inRule")}`;
      cell.title = tip;
    });
  };
  fill("usage-b", sim.usage.birth, sim.rule.birth, "deadCells");
  fill("usage-s", sim.usage.survive, sim.rule.survive, "liveCells");
}

function selectTab(name) {
  sim.tab = name;
  for (const tab of document.querySelectorAll(".tab")) {
    tab.setAttribute("aria-selected", String(tab.dataset.tab === name));
  }
  for (const panel of document.querySelectorAll(".tab-panel")) panel.hidden = panel.dataset.panel !== name;
  sizeCanvas(chart, chartContext);
  sizeCanvas(spacetime, spacetimeContext);
  draw();
}

// ---- simulation ------------------------------------------------------------

function advance() {
  const counts = neighbourCounts(sim.cells, sim.adj);
  for (let i = 0; i < counts.length; i++) {
    const k = Math.min(8, counts[i]);
    if (sim.cells[i]) sim.usage.survive[k] += 1;
    else sim.usage.birth[k] += 1;
  }
  const next = stepFromCounts(sim.cells, counts, sim.rule);
  let changed = 0;
  for (let i = 0; i < next.length; i++) changed += next[i] !== sim.cells[i];
  sim.activity = changed / next.length;
  sim.cells = next;
  if (sim.twin) sim.twin = step(sim.twin, sim.rule, sim.adj);
  sim.generation += 1;
  sim.detector.push(sim.cells);
  record();
}

let last = 0;
function loop(time) {
  if (sim.running) {
    const interval = 1000 / Number($("speed").value);
    if (time - last >= interval) {
      last = time;
      advance();
      draw();
    }
  }
  requestAnimationFrame(loop);
}

function setRunning(running) {
  sim.running = running;
  $("play").textContent = t(running ? "pause" : "play");
}

function randomise() {
  sim.cells = randomState(sim.cells.length, Number($("density").value), sim.random);
  touched();
  draw();
}

// ---- twin run ----------------------------------------------------------------

function startTwin() {
  sim.twin = sim.cells.slice();
  const i = Math.floor(sim.random() * sim.twin.length);
  sim.twin[i] = sim.twin[i] ? 0 : 1;
  sim.history = sim.history.map(([a]) => [a, null]);
  record();
  updateTwinUi();
  draw();
}

function stopTwin() {
  sim.twin = null;
  updateTwinUi();
}

function updateTwinUi() {
  $("twin-legend").hidden = !sim.twin;
  $("twin").textContent = t(sim.twin ? "twinStop" : "twinStart");
  $("twin").setAttribute("aria-pressed", String(Boolean(sim.twin)));
  for (const el of document.querySelectorAll(".twin-only")) el.hidden = !sim.twin;
}

// ---- rule and topology controls ----------------------------------------------

function fillPresets() {
  const select = $("preset");
  const current = ruleToString(sim.rule);
  select.innerHTML = "";
  for (const preset of PRESETS) {
    const option = new Option(`${preset[language][0]} (${preset.rule})`, preset.rule);
    select.add(option);
  }
  select.add(new Option(t("customRule"), "custom"));
  select.value = PRESETS.some((p) => p.rule === current) ? current : "custom";
  showRuleNote();
}

function showRuleNote() {
  const preset = PRESETS.find((p) => p.rule === ruleToString(sim.rule));
  const note = $("rule-note");
  note.textContent = "";
  if (!preset) return;
  note.append(`${preset[language][1]} `);
  const link = document.createElement("a");
  link.href = preset.link;
  link.textContent = t("readMore");
  note.append(link);
}

function setRule(text) {
  try {
    sim.rule = parseRule(text);
  } catch {
    $("rule-error").hidden = false;
    return;
  }
  $("rule-error").hidden = true;
  $("rule").value = ruleToString(sim.rule);
  $("preset").value = PRESETS.some((p) => p.rule === ruleToString(sim.rule))
    ? ruleToString(sim.rule)
    : "custom";
  showRuleNote();
  restartMeasurements();
  sim.generation = 0;
  draw();
}

function showTopologyNote() {
  $("topology-note").textContent = t(`${sim.topology}Note`);
  $("beta-row").hidden = sim.topology !== "rewired";
}

function setTopology() {
  $("topology-note").textContent = t("building");
  // Let the message paint before a large rewiring blocks the page.
  setTimeout(() => {
    buildTopology();
    restartMeasurements();
    sim.generation = 0;
    if (sim.twin) startTwin();
    showTopologyNote();
    draw();
  }, 20);
}

// ---- language --------------------------------------------------------------

function applyLanguage() {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  for (const el of document.querySelectorAll("[data-text]")) el.textContent = t(el.dataset.text);
  document.title = t("title");
  const docs = "https://github.com/ellach123/conway-game-of-life/blob/main/docs/";
  const suffix = language === "zh" ? ".zh.md" : ".md";
  $("link-report").href = `${docs}report${suffix}`;
  $("link-brief").href = `${docs}policy-brief${suffix}`;
  $("language").textContent = t("language");
  setRunning(sim.running);
  setPanMode(panMode);
  updateTwinUi();
  fillPresets();
  showTopologyNote();
  draw();
}

// ---- pointer: draw, pan, zoom ----------------------------------------------

function cellAt(event) {
  const box = canvas.getBoundingClientRect();
  const c = Math.floor((event.clientX - box.left - view.x) / view.scale);
  const r = Math.floor((event.clientY - box.top - view.y) / view.scale);
  return r >= 0 && r < sim.rows && c >= 0 && c < sim.cols ? r * sim.cols + c : null;
}

function setPanMode(on) {
  panMode = on;
  $("mode-draw").setAttribute("aria-pressed", String(!on));
  $("mode-pan").setAttribute("aria-pressed", String(on));
  canvas.classList.toggle("panning", on);
}

let drag = null; // { kind: "paint", value } or { kind: "pan", x, y }
canvas.addEventListener("pointerdown", (event) => {
  const wantsPan = panMode || spaceHeld || event.button === 1 || event.button === 2;
  canvas.setPointerCapture(event.pointerId);
  if (wantsPan) {
    drag = { kind: "pan", x: event.clientX, y: event.clientY };
    canvas.classList.add("grabbing");
    return;
  }
  const i = cellAt(event);
  if (i === null) return;
  drag = { kind: "paint", value: sim.cells[i] ? 0 : 1 };
  sim.cells[i] = drag.value;
  touched();
  draw();
});
canvas.addEventListener("pointermove", (event) => {
  if (!drag) return;
  if (drag.kind === "pan") {
    view.auto = false;
    view.x += event.clientX - drag.x;
    view.y += event.clientY - drag.y;
    drag.x = event.clientX;
    drag.y = event.clientY;
    draw();
    return;
  }
  const i = cellAt(event);
  if (i !== null && sim.cells[i] !== drag.value) {
    sim.cells[i] = drag.value;
    touched();
    draw();
  }
});
const endDrag = () => {
  drag = null;
  canvas.classList.remove("grabbing");
};
canvas.addEventListener("pointerup", endDrag);
canvas.addEventListener("pointercancel", endDrag);
canvas.addEventListener("contextmenu", (event) => event.preventDefault());

canvas.addEventListener(
  "wheel",
  (event) => {
    if (!event.ctrlKey && !event.metaKey) return; // plain scrolling scrolls the page
    event.preventDefault();
    const box = canvas.getBoundingClientRect();
    const mx = event.clientX - box.left;
    const my = event.clientY - box.top;
    const factor = Math.exp(-event.deltaY * 0.0015);
    const scale = Math.min(60, Math.max(0.5, view.scale * factor));
    view.x = mx - ((mx - view.x) * scale) / view.scale;
    view.y = my - ((my - view.y) * scale) / view.scale;
    view.scale = scale;
    view.auto = false;
    draw();
  },
  { passive: false },
);

window.addEventListener("keydown", (event) => {
  if (event.code === "Space" && event.target === document.body) {
    spaceHeld = true;
    canvas.classList.add("panning");
    event.preventDefault();
  }
});
window.addEventListener("keyup", (event) => {
  if (event.code === "Space") {
    spaceHeld = false;
    canvas.classList.toggle("panning", panMode);
  }
});

// ---- controls --------------------------------------------------------------

$("play").addEventListener("click", () => setRunning(!sim.running));
$("step").addEventListener("click", () => {
  setRunning(false);
  advance();
  draw();
});
$("random").addEventListener("click", randomise);
$("clear").addEventListener("click", () => {
  setRunning(false);
  sim.cells = new Uint8Array(sim.rows * sim.cols);
  touched();
  draw();
});
$("density").addEventListener("input", (e) => {
  $("density-value").textContent = Number(e.target.value).toFixed(2);
});
$("speed").addEventListener("input", (e) => {
  $("speed-value").textContent = e.target.value;
});
$("mode-draw").addEventListener("click", () => setPanMode(false));
$("mode-pan").addEventListener("click", () => setPanMode(true));
$("fit").addEventListener("click", fitView);
$("size-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const clamp = (v) => Math.min(MAX_SIZE, Math.max(MIN_SIZE, Math.round(Number(v) || 0)));
  stopTwin();
  resizeGrid(clamp($("rows").value), clamp($("cols").value));
});
$("preset").addEventListener("change", (e) => {
  if (e.target.value !== "custom") setRule(e.target.value);
});
$("rule").addEventListener("change", (e) => setRule(e.target.value));
for (const radio of document.querySelectorAll('input[name="topology"]')) {
  radio.addEventListener("change", (e) => {
    sim.topology = e.target.value;
    setTopology();
  });
}
$("beta").addEventListener("input", (e) => {
  $("beta-value").textContent = Number(e.target.value).toFixed(2);
});
$("beta").addEventListener("change", (e) => {
  sim.beta = Number(e.target.value);
  setTopology();
});
$("twin").addEventListener("click", () => {
  if (sim.twin) stopTwin();
  else startTwin();
  draw();
});
for (const tab of document.querySelectorAll(".tab")) {
  tab.addEventListener("click", () => selectTab(tab.dataset.tab));
}
$("slice-row").addEventListener("input", (e) => {
  sim.sliceRow = Number(e.target.value);
  $("slice-row-value").textContent = sim.sliceRow;
  sim.slice = [];
  draw();
});
$("language").addEventListener("click", () => {
  language = language === "en" ? "zh" : "en";
  applyLanguage();
});
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  readPalette();
  draw();
});
new ResizeObserver(() => {
  sizeCanvas(chart, chartContext);
  sizeCanvas(spacetime, spacetimeContext);
  if (view.auto) {
    fitCanvasHeight();
    fitView();
    return;
  }
  const box = sizeCanvas(canvas, context);
  view.width = box.width;
  view.height = box.height;
  draw();
}).observe(document.querySelector(".board"));

const box = sizeCanvas(canvas, context);
view.width = box.width;
view.height = box.height;
sizeCanvas(chart, chartContext);
// Optional starting state from the address, e.g.
// ?rule=B36/S23&w=128&h=96&topology=rewired&beta=0.3&density=0.35&steps=200&twin=1&tab=usage&lang=zh&paused=1
const params = new URLSearchParams(location.search);
const clampSize = (v, fallback) =>
  Math.min(MAX_SIZE, Math.max(MIN_SIZE, Math.round(Number(v) || fallback)));
if (params.has("lang") && params.get("lang") in TEXT) language = params.get("lang");
if (params.has("rule")) {
  try {
    sim.rule = parseRule(params.get("rule"));
    $("rule").value = ruleToString(sim.rule);
  } catch {
    // ignore an invalid rule and keep Life
  }
}
if (["torus", "fixed", "rewired"].includes(params.get("topology"))) {
  sim.topology = params.get("topology");
  document.querySelector(`input[name="topology"][value="${sim.topology}"]`).checked = true;
}
if (params.has("beta")) {
  sim.beta = Math.min(1, Math.max(0, Number(params.get("beta")) || 0));
  $("beta").value = sim.beta;
  $("beta-value").textContent = sim.beta.toFixed(2);
}
if (params.has("density")) {
  const d = Math.min(0.9, Math.max(0.05, Number(params.get("density")) || 0.35));
  $("density").value = d;
  $("density-value").textContent = d.toFixed(2);
}
sim.cells = new Uint8Array(sim.rows * sim.cols);
resizeGrid(clampSize(params.get("h"), 96), clampSize(params.get("w"), 96));
randomise();
if (params.get("twin") === "1") startTwin();
const warmup = Math.min(5000, Math.max(0, Math.round(Number(params.get("steps")) || 0)));
for (let i = 0; i < warmup; i++) advance();
applyLanguage();
if (["curves", "spacetime", "usage"].includes(params.get("tab"))) selectTab(params.get("tab"));
const paused = params.get("paused") === "1" || matchMedia("(prefers-reduced-motion: reduce)").matches;
setRunning(!paused);
draw();
requestAnimationFrame(loop);
