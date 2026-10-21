# Conway's Game of Life — from simulator to experiments

[![CI](https://github.com/FreeyaFly/conway-game-of-life/actions/workflows/ci.yml/badge.svg)](https://github.com/FreeyaFly/conway-game-of-life/actions/workflows/ci.yml)

> **Status:** v2 in progress. Experiment 1 (attractors and chaos) is done; experiment 2 (topology) comes next.

How do **local rules** and the **interaction topology** together determine **global behaviour**?

This project started as a Tkinter simulator of Conway's Game of Life (v1, 2023). v2 rebuilds it as a small computational-experiment platform. One engine runs both square lattices and arbitrary networks, and four experiments probe attractors, topology, criticality, and rule space.

<p align="center"><img src="docs/figures/glider.gif" alt="A glider crossing a 16 by 16 torus" width="240"></p>

## Growth line

| Version | What it is |
|---|---|
| [v1](v1/) | Single-file Tkinter simulator (March 2023), tagged `v1.0` |
| v2 | Vectorised engine + tests + four documented experiments + a web version *(in progress)* |

## The engine in one line

```
next = f(state, A · state)
```

`A · state` is the number of live neighbours of every cell, and `f` is a life-like rule such as `B3/S23`. On a square lattice, `A · state` is computed by convolution; on any other network, by a sparse matrix product. A lattice is just one particular `A`, and the tests check that both paths agree cell by cell (see [ADR 0001](docs/adr/0001-unified-engine.md)).

```python
from life.engine import run
from life.patterns import GLIDER, place
from life.rules import parse_rule
from life.topology import Graph, Lattice, lattice_adjacency

state = place(GLIDER, (16, 16), at=(1, 1))
history = run(state, 64, parse_rule("B3/S23"), Lattice("torus"))  # shape (65, 16, 16)

# The same lattice, run as a network:
same = run(state, 64, parse_rule("B3/S23"), Graph(lattice_adjacency((16, 16), "torus")))
```

## Getting started

Requires Python 3.11.

```
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"        # Windows: .venv\Scripts\python.exe
.venv/bin/python -m pytest -q
.venv/bin/python scripts/make_glider_gif.py         # writes docs/figures/glider.gif
```

## Layout

```
life/        engine.py, rules.py, topology.py, patterns.py, metrics.py
notebooks/   one notebook per experiment
data/        raw results behind the figures
tests/       pytest suite; fixtures/ holds engine cases shared with the future web version
scripts/     figure generation
docs/        experiment write-ups, methods, concepts, puzzles, decisions (adr/), figures
v1/          the original 2023 simulator, unchanged
```

## Progress

| Stage | What | Status | Details |
|---|---|---|---|
| 0 | **Foundations**: engine, tests, CI | ✅ done | [checklist](docs/stage0-checklist.md) · [#1](https://github.com/FreeyaFly/conway-game-of-life/issues/1) |
| 1 | **Attractors and chaos**: transient length, cycle period, damage spreading from a one-cell flip | ✅ done (`v2.0-alpha.1`) | [checklist](docs/stage1-checklist.md) · [write-up](docs/experiments/01-attractors.md) · [#2](https://github.com/FreeyaFly/conway-game-of-life/issues/2) |
| 2 | **Topology rewiring**: lattice → small world → random graph (Watts–Strogatz β sweep) | next | [#3](https://github.com/FreeyaFly/conway-game-of-life/issues/3) |
| 3 | **Phase transition and criticality**: initial-density sweep and avalanche-size distributions | planned | [#4](https://github.com/FreeyaFly/conway-game-of-life/issues/4) |
| 4 | **Systems view**: causal loop diagrams and an automated scan of life-like rule space | planned | [#5](https://github.com/FreeyaFly/conway-game-of-life/issues/5) |
| 5 | **Report** tying the experiments together | planned | [#6](https://github.com/FreeyaFly/conway-game-of-life/issues/6) |
| 6 | **Web version** on GitHub Pages | planned | [#7](https://github.com/FreeyaFly/conway-game-of-life/issues/7) |

Puzzles the data turned up along the way are collected in [docs/puzzles.md](docs/puzzles.md).

## License

[MIT](LICENSE)
