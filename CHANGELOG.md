# Changelog

## v2.0-alpha.4: experiment 4, a systems view

### Added
- `life.rulespace`: rule sampling, Langton's λ, one-digit neighbours, behavioural features and a transparent five-class classification
- Notebook `04_systems`: 500 random rules, class mix along λ, birth vs. survival digits, threshold sensitivity, Life's 17 neighbours, a check on a larger grid
- Write-up `docs/experiments/04-systems.md` with three causal loop diagrams and five puzzles; ADR 0004
- Methods, concepts and references for feedback loops, Wolfram's classes and Langton's λ
- Raw data in `data/exp04/`; figures

## v2.0-alpha.3: experiment 2, phase transition and criticality

### Added
- `life.avalanches`: open boundaries, settling, avalanche size and duration against an undisturbed copy
- `life.stats`: discrete power-law fit (maximum likelihood, KS cut-off, likelihood-ratio test against an exponential)
- Notebook `02_criticality`: initial-density sweep, survival on grids from 32 to 256, avalanches on grids from 32 to 256 and on a torus
- Write-up `docs/experiments/02-criticality.md` with five puzzles; ADR 0003
- Methods, concepts and references for power laws, self-organized criticality, finite-size effects and absorbing states
- Raw data in `data/exp02/`; figures

## v2.0-alpha.2: experiment 3, topology rewiring

### Added
- `life.networks`: degree-preserving rewiring, classic Watts–Strogatz rewiring, clustering, mean path length
- Notebook `03_topology`: structure, dynamics and damage spreading from lattice to small world to random network; a fine sweep that locates the freezing-to-boiling switch at β ≈ 0.2; a mean-field check
- Write-up `docs/experiments/03-topology.md` with six puzzles; ADR 0002
- Methods, concepts and references for networks, mean field, phase transitions and critical slowing down
- Raw data in `data/exp03/`; figures and a side-by-side animation

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
