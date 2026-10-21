# ADR 0002: Degree-preserving rewiring

- **Status:** accepted
- **Date:** 2026-10-21

## Context

Experiment 3 asks how the topology changes the behaviour of a fixed rule. Life-like rules only look at the *number* of live neighbours. Classic Watts–Strogatz rewiring moves one end of an edge to a random node, so some nodes end up with fewer than 8 neighbours and others with more. Any effect seen would then mix two causes: *which* nodes are neighbours, and *how many* neighbours each node has.

## Decision

The main experiments use **degree-preserving rewiring** (`life.networks.rewire`):

1. Mark a fraction $\beta$ of the edges at random; the rest stay exactly as on the lattice.
2. Shuffle the marked edges with double-edge swaps: pick $(a, b)$ and $(c, d)$, replace them with $(a, d)$ and $(c, b)$, and reject the swap if it would create a self-loop or a duplicate edge. Ten swaps per marked edge.

Every node keeps 8 neighbours throughout. $\beta = 1$ yields a random 8-regular graph (about 0.2 % of lattice edges survive by chance, as expected for a random graph).

Classic Watts–Strogatz rewiring (`life.networks.watts_strogatz`) is kept as a comparison.

## Consequences

- Differences between $\beta$ values can be attributed to *who* is connected, not to *how many* connections a node has.
- The comparison in experiment 3d showed nearly identical results for both schemes, so for this rule unequal degrees turned out to matter little; the design still removes the doubt.
- Rewiring at $\beta = 1$ takes about 1 s for 16 384 edges in Python, because swaps are checked one by one; random numbers are drawn in advance to keep this fast enough.

## Alternatives considered

- **Classic Watts–Strogatz only:** simpler and standard, but mixes degree effects into the results.
- **Swaps counted over all edges** (rather than shuffling a marked subset): at "$\beta = 1$" about 37 % of the original edges would remain, so the end point would not be a random graph.
- **networkx generators:** convenient, but they start from a ring, not from a 2-D lattice with the Moore neighbourhood, and would add a dependency.
