# ADR 0005: A small JavaScript engine for the web version

- **Status:** accepted
- **Date:** 2026-10-22

## Context

The experiments run in Python notebooks. A browser version should let anyone turn the same dials (rule, topology, density) without installing anything, and it should stay working for years without maintenance.

## Decision

- **Plain HTML, CSS and JavaScript modules in `web/`**, no framework, no build step, no runtime dependencies. GitHub Pages serves the folder as it is.
- **A separate JavaScript engine** (`web/engine.js`) that mirrors the Python one: every topology is an adjacency list in CSR form and one step is `next = f(state, A · state)`, so lattices and rewired networks share one code path. It also ports degree-preserving rewiring and exact cycle detection.
- **Shared test cases:** the JavaScript tests (`tests/js/`, run with Node's built-in `node --test`) read the same `tests/fixtures/patterns.json` as the Python tests. CI runs both.
- The page reads an optional starting state from its address (rule, size, topology, β, density, steps, twin run, tab, language), so documents can link straight to a given experiment.

## Consequences

- Two implementations must be kept in step; the shared fixtures catch differences in the engine, and the page reproduces findings from the experiments (for example, the Replicator rule empties a 32 × 32 torus at generation 16; Life on a network with 30 % of links rewired never settles).
- Random number generators differ between the two languages, so rewired networks and random soups are statistically, not literally, the same as in the notebooks.
- No dependencies means no dependency updates; it also means features such as charts are drawn by hand on canvas.

## Alternatives considered

- **Pyodide (Python in the browser):** reuses the Python code directly, but downloads about 10 MB before anything runs and starts slowly.
- **A framework (React, Svelte) with a bundler:** more structure for larger interfaces, but a build step and a dependency tree to maintain for a page with one canvas and a dozen controls.
- **Static animations only:** no setup at all, but no way to turn the dials.
