# ADR 0003: How avalanches are defined and driven

- **Status:** accepted
- **Date:** 2026-10-22

## Context

Experiment 2 asks whether Life is self-organized critical, by perturbing settled grids one cell at a time and recording the response. Three choices change the answer: what counts as the size of an avalanche, when an avalanche is over, and what the boundary does with material that reaches the edge.

## Decision

- **Size** = number of cells that differ, at some time, from an undisturbed copy of the same grid run in parallel. Counting all cells that change would also count blinkers and other oscillators that were already there.
- **Duration** = number of generations until the disturbed grid is back on a cycle (exact cycle detection, as in experiment 1).
- **Driving**: one live cell at a uniformly random dead interior site; the next avalanche starts from the new settled state. The first 500 avalanches are discarded as warm-up.
- **Open boundary**: the outer two rows and columns are cleared after every step (`life.avalanches.open_border`). A glider that reaches the edge leaves, as sand leaves a sandpile.
- A torus run is kept as a control.
- Avalanches after a grid has become empty are excluded from the statistics: the empty grid is absorbing, and every later "avalanche" is a single cell dying.

## Consequences

- Avalanches always end, except in the rare case of a cycle longer than the step cap, which is reported separately.
- Open boundaries remove material, so small grids can drain to the empty state (seen at $L$ = 32). The live density during driving is therefore recorded and plotted with every run.
- On the torus, released gliders stay; the comparison shows that the boundary choice does not change the rough shape of the size distribution at $L$ = 64.

## Alternatives considered

- **Torus only:** simplest, but a released glider circles forever and changes the background for all later avalanches.
- **Dead (fixed) boundary without clearing:** gliders crash into the wall and turn into debris, so material is never lost and the system is not driven like a sandpile.
- **Size as total number of state changes:** dominated by pre-existing oscillators; it measures the background, not the response.
