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
