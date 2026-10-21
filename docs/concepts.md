# Concepts

Short introductions for readers who have not met these ideas before. Each entry says where it shows up in the experiments.

## Attractor

The state, or set of states, that a system ends up in and then stays in forever. In a finite cellular automaton every run ends on a cycle of states, so every attractor is a cycle: a still pattern (period 1) or an oscillation. *Experiment 1.*

## Transient

The part of a run before it reaches its attractor: the time the system spends "searching". Long transients mean the system takes a long time to settle, even if what it settles into is simple. *Experiment 1a.*

## Period, and why it is a least common multiple

The length of the cycle a run ends on. When a grid holds several independent objects, the grid repeats only when every object has completed whole cycles at the same time, so the grid's period is the least common multiple of the objects' periods. One blinker (period 2) is enough to make the whole grid period 2. *Experiment 1b.*

## Glider

A five-cell pattern in Conway's Game of Life that moves one cell diagonally every four generations. On a torus of side $L$ it returns to its starting position after $4L$ generations. *Experiment 1, puzzle A.*

## Sensitivity to initial conditions and damage spreading

A system is sensitive to initial conditions when a tiny change at the start leads to a large difference later (the "butterfly effect"). In a cellular automaton the natural test is to flip one cell and count how many cells differ as time goes on (the *damage*). Damage that grows and persists is the discrete counterpart of chaos; damage that dies out signals order. *Experiment 1c.*

## Decorrelation

Two runs are fully decorrelated when knowing one tells you nothing about the other: they differ as much as two unrelated random grids would. For live density $\rho$ that is a fraction $2\rho(1-\rho)$ of cells. *Experiment 1c, puzzle G.*

## Clustering and path length

Two numbers that describe a network. **Clustering** asks how often two of your neighbours are also neighbours of each other (high on a lattice, where neighbours sit together). **Path length** asks how many steps it takes, on average, to get from one node to another (long on a lattice, short on a random network). *Experiment 3a.*

## Small world

A network with short paths *and* high clustering: locally tight-knit, yet everyone is a few steps from everyone else. Watts and Strogatz showed that rewiring a lattice only slightly is enough to get there, because a few shortcuts shrink distances long before they destroy local clusters. *Experiment 3a.*

## Mean field

An approximation that ignores who is next to whom and treats every cell as surrounded by an average environment. It fails on lattices, where neighbours are correlated, but works well on random networks, where they hardly are. *Experiment 3, puzzles B and F.*

## Phase transition

An abrupt change in the collective behaviour of a system when a parameter crosses a critical value, like water freezing at 0 °C. In experiment 3 the parameter is the rewired fraction $\beta$, and the two phases are *freezing* (activity dies into still lifes and blinkers) and *boiling* (activity never stops). *Experiment 3e.*

## Critical slowing down

Close to a transition, a system takes longer and longer to settle, because it hovers between its two possible fates. It is studied as an early-warning signal for sudden shifts in ecosystems, climate and markets. *Experiment 3e, puzzle C.*

## Bistability

A system with two stable states and a tipping point between them: below the threshold it falls into one state, above it into the other. On a random network, Life dies out from starting densities below about 0.19 and boils from densities above it. *Experiment 3e, puzzle F.*

## Power law

A distribution in which the probability of an event of size $s$ falls like $s^{-\alpha}$. Small events are very common, large ones rare but never negligible, and there is no typical size. On log–log axes it is a straight line, but a straight-looking stretch is not proof: other distributions look straight over a limited range. *Experiment 2b.*

## Self-organized criticality

The idea, from the sandpile model of Bak, Tang and Wiesenfeld (1987), that a slowly driven system can tune itself to a critical point without anyone adjusting a parameter: add grains one at a time, and avalanches of all sizes follow a power law. Whether the Game of Life does this has been debated since 1989. *Experiment 2b.*

## Finite-size effects

Behaviour that depends on the size of the system rather than on the rule alone, such as the largest possible avalanche or the chance that a sparse soup survives somewhere. Comparing several sizes separates finite-size effects from genuine properties. *Experiment 2a, 2b.*

## Absorbing state

A state the system can enter but never leave. For Life with one cell added at a time, the empty grid is absorbing: a lone added cell dies at once. *Experiment 2b, puzzle D.*

## Feedback loops

A **reinforcing** loop amplifies change (more activity → more births → more activity); a **balancing** loop counteracts it (more activity → more still lifes → less activity). Drawn as a causal loop diagram, a loop with an even number of negative links is reinforcing, with an odd number balancing. *Experiment 4a.*

## Shift in loop dominance

Several loops act at once, and which one wins can change when a parameter changes. On the lattice the freezing loop wins; when rewiring halves the clustering, it weakens enough for the reinforcing loop to take over. *Experiments 3 and 4a.*

## Wolfram's classes

Wolfram (1984) sorted cellular automata into four classes by their long-run behaviour: (I) uniform, (II) simple stable or periodic structures, (III) chaos, (IV) complex localized structures with long transients. Life is the standard example of class IV. *Experiment 4b.*

## Langton's λ and the edge of chaos

Langton (1990) measured how much of a rule table produces live cells ($\lambda$) and proposed that complex behaviour sits at a transition between order and chaos as $\lambda$ grows. For life-like rules, experiment 4 found that $\lambda$ alone does not locate the complex rules. *Experiment 4b, puzzle D.*
