# Conway's Game of Life — from simulator to experiments

> **Status:** v2 in progress (stage 0: foundations).

How do **local rules** and the **interaction topology** together determine **global behaviour**?

This project started as a Tkinter simulator of Conway's Game of Life (v1, 2023). v2 rebuilds it as a small computational-experiment platform. One engine runs both square lattices and arbitrary networks, and four experiments probe attractors, topology, criticality, and rule space.

## Growth line

| Version | What it is |
|---|---|
| [v1](v1/) | Single-file Tkinter simulator (March 2023), tagged `v1.0` |
| v2 | Vectorised engine + tests + four documented experiments + a web version *(in progress)* |

## Planned experiments

1. **Attractors and chaos**: transient length, cycle period, and damage spreading from a one-cell perturbation
2. **Topology rewiring**: lattice → small world → random graph (Watts–Strogatz β sweep)
3. **Phase transition and criticality**: initial-density sweep and avalanche-size distributions
4. **Systems view**: causal loop diagrams and an automated scan of life-like rule space

## License

[MIT](LICENSE)
