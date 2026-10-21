# Methods

Definitions of the measurements used in the experiments. Code references point to the `life` package.

## Simulation

- **State:** a boolean array, one entry per cell (lattice) or node (network).
- **Update:** synchronous; every cell is updated from the same previous state: `next = f(state, A · state)` ([ADR 0001](adr/0001-unified-engine.md)).
- **Random soups:** each cell alive independently with probability $\rho$ (0.35 unless stated otherwise), drawn with `numpy.random.default_rng(seed)`; seeds are listed in each experiment, so every run can be repeated exactly.

## Cycles (`life.metrics.detect_cycle`)

A finite system with a deterministic rule must revisit a state, and from then on it repeats forever.

- Every state is packed into bytes and stored with the time it first appeared. At the first repeat, at time $t$ of a state first seen at time $t_0$:
  - **transient** $= t_0$: the number of steps before the trajectory reaches its cycle;
  - **period** $= t - t_0$: the length of the cycle (1 for a still state).
- **Attractor identity:** the smallest byte string among the states of the cycle. Two trajectories end on the same attractor exactly when their identities are equal, whatever phase of the cycle they enter at.
- Comparing full byte strings (not hash values) rules out false matches. Memory grows linearly with the number of steps.
- **Censoring:** a run that reaches the step cap without a repeat is reported separately as censored, never dropped.

## Damage spreading (`life.metrics.damage_spread`)

- Two runs start from states that differ in one cell and are advanced with the same rule and topology.
- **Damage** $d(t)$: the Hamming distance between the two states at time $t$, i.e. the number of cells that differ; $d(0) = 1$.
- **Healed:** $d$ returns to 0. From then on the runs are identical.
- **Reference level for full decorrelation:** two independent grids with live density $\rho$ differ in a fraction $2\rho(1-\rho)$ of cells.

## Networks (`life.networks`)

- **Degree-preserving rewiring** (`rewire`): a fraction $\beta$ of the lattice edges is marked; the marked edges are shuffled by double-edge swaps $(a,b),(c,d) \to (a,d),(c,b)$, rejecting self-loops and duplicate edges. Every node keeps its degree. See [ADR 0002](adr/0002-degree-preserving-rewiring.md).
- **Classic Watts–Strogatz** (`watts_strogatz`): each edge, with probability $\beta$, has one end moved to a random node; degrees vary.
- **Clustering** $C$: for each node, the fraction of pairs of its neighbours that are themselves connected, averaged over nodes; computed as $\mathrm{diag}(A^3)_i / (k_i(k_i-1))$.
- **Mean path length** $\ell$: average number of hops between distinct connected nodes, from breadth-first search; estimated from 200 random sources on large networks.

## Simple models used to explain results

- **Slowest region:** the transient of a grid of area $kA$ is approximated by the maximum of $k$ transients drawn from grids of area $A$.
- **Mean field:** if each neighbour is alive independently with probability $\rho$, one step of a life-like rule maps $\rho$ to $f(\rho) = \rho \sum_{k \in S} P(k) + (1-\rho) \sum_{k \in B} P(k)$, with $P(k)$ binomial over the node's degree. Fixed points $f(\rho) = \rho$ predict steady densities; for B3/S23 with 8 neighbours they are 0, 0.192 (unstable) and 0.370.
- **Poisson oscillators:** if oscillators appear independently with density $\lambda$ per cell, the probability that a grid of $L^2$ cells has none (and so period 1) is $e^{-\lambda L^2}$.
