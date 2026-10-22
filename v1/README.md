# v1 — Tkinter simulator (March 2023)

This folder keeps the original version of the project, a graduation project from March 2023. It is preserved unchanged so the step from v1 to v2 stays visible. The same state is also tagged as [`v1.0`](https://github.com/ellach123/conway-game-of-life/tree/v1.0).

## What v1 is

`Conway_Life_Game.py` is a single-file (316 lines) desktop simulator built with Python and Tkinter. The UI text is in Chinese.

- Draw an N × N grid, toggle cells by clicking, or fill it randomly (10 % density)
- Start, pause, and clear the simulation; a counter shows the number of generations
- A "stable state" check stops the run and reports whether the pattern died out or settled

Run it with any Python ≥ 3.8 that includes Tkinter:

```
python v1/Conway_Life_Game.py
```

## Limitations

| Area | v1 behaviour | Consequence |
|---|---|---|
| Rule | Only B3/S23 is supported, written directly into the update loop | Other life-like rules cannot be explored |
| Boundary | A fixed ring of dead cells around the grid | Edge effects; gliders are destroyed at the border |
| Topology | Square grid only | Network structure cannot be studied |
| Performance | Nested pure-Python loops, `O(9·N²)` per step | Slow for large grids or long runs |
| Stability check | Stops when the last 50 states contain fewer than 10 distinct states | A heuristic: transient length and cycle period are never measured |
| Structure | Simulation logic, drawing, and global state are mixed together | The engine cannot be reused or tested without the GUI |
| Tests | None | Correctness is checked only by eye |

## What v2 changes

v2 turns the simulator into a small experimentation platform for one question: **how do local rules and the interaction topology together determine global behaviour?**

- A vectorised engine (NumPy convolution) with parsed `B/S` rule strings and periodic or fixed boundaries
- One update rule, `next = f(state, A · state)`, so a lattice and an arbitrary network run on the same engine
- A test suite and continuous integration
- Exact measurement instead of heuristics: transient length, cycle period, and damage spreading
- Four experiments, each documented as question → prediction → method → result → discussion

See the [main README](../README.md) for the current state.
