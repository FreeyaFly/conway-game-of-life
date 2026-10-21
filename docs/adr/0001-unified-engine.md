# ADR 0001: One engine for lattices and networks

- **Status:** accepted
- **Date:** 2026-10-21

## Context

The experiments compare the same local rule on different interaction structures: a square lattice, a lattice with some edges rewired (small world), and a random graph. If each structure had its own simulation code, any difference in behaviour could come from the structure or from the code. v1 had one hard-coded update loop for a square grid with a dead border, so it could not answer this kind of question.

## Decision

Every update is `next = f(state, A · state)`:

- `A · state` gives the number of live neighbours of every cell. It is provided by a **topology** object with one method, `neighbor_counts(state)`.
- `f` is a life-like **rule** in B/S notation, applied through a lookup table indexed by neighbour count.

There are two topology implementations:

| Topology | How `A · state` is computed | Used for |
|---|---|---|
| `Lattice("torus" \| "fixed")` | 2-D convolution with the 3 × 3 Moore kernel (`scipy.ndimage.convolve`) | Fast lattice runs |
| `Graph(A)` | Sparse matrix–vector product with a CSR adjacency matrix | Any network |

`lattice_adjacency(shape, boundary)` builds the matrix `A` of a lattice. The test suite runs both paths on random states and on shared fixtures and requires identical results, cell by cell and generation by generation.

## Consequences

- A difference seen on a network can be attributed to the topology, because on the lattice the two paths are proven equal.
- Rewiring experiments start from `lattice_adjacency` and edit edges, without new simulation code.
- The rule lookup table grows with the largest neighbour count, so nodes with more than 8 neighbours work; counts above 8 never match a B/S digit.
- The convolution path stays as the fast default for plain lattices; the matrix path costs more memory (8 non-zeros per cell) but is still linear in the number of cells.
- On tori with a side shorter than 3, both paths count some neighbours twice. They still agree, but the neighbourhood is no longer the usual Moore neighbourhood, so experiments use sides of at least 3.

## Alternatives considered

- **Separate simulators per topology**: simpler at first, but differences between results could not be separated from implementation differences.
- **Only the matrix path**: one code path, but slower and heavier for the many plain-lattice runs.
- **networkx graphs inside the update loop**: convenient to build, far too slow to iterate; networkx may still be used to *generate* graphs, which are then converted to a sparse matrix.
