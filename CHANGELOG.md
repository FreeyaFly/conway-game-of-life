# Changelog

## Unreleased: v2 stage 0 (foundations)

### Added
- `life` package: B/S rule parser, convolution engine with torus and fixed boundaries, graph topology with sparse adjacency, reference patterns
- Test suite with shared engine fixtures and a convolution vs. adjacency agreement check
- CI with ruff and pytest on Python 3.11
- Glider animation, ADR 0001, stage 0 checklist

### Changed
- The v1 simulator moved to `v1/`, unchanged

## v1.0: 2023

- Tkinter simulator of Conway's Game of Life (B3/S23 on a square grid with a dead border)
