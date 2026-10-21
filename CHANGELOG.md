# Changelog

## v2.0-alpha.1: experiment 1, attractors and chaos

### Added
- `life.metrics`: exact cycle detection with attractor identity, Hamming distance, damage spreading
- Notebook `01_attractors`: transients and periods of 650 random soups on 16–128 tori; damage spreading under Life, HighLife and Seeds
- Write-up `docs/experiments/01-attractors.md` with predictions, results and eight puzzles (one open)
- `docs/methods.md`, `docs/concepts.md`, `docs/references.md`, `docs/puzzles.md`
- Raw data in `data/exp01/`; figures and a damage-spreading animation
- Tests that confirm the findings (a lone glider on an L × L torus has period 4L; grid period is the LCM of object periods)

### Changed
- README: progress table per stage
- CI actions moved to versions running on Node 24

## v2 stage 0 (foundations)

### Added
- `life` package: B/S rule parser, convolution engine with torus and fixed boundaries, graph topology with sparse adjacency, reference patterns
- Test suite with shared engine fixtures and a convolution vs. adjacency agreement check
- CI with ruff and pytest on Python 3.11
- Glider animation, ADR 0001, stage 0 checklist

### Changed
- The v1 simulator moved to `v1/`, unchanged

## v1.0: 2023

- Tkinter simulator of Conway's Game of Life (B3/S23 on a square grid with a dead border)
