# ADR 0004: Classifying life-like rules

- **Status:** accepted
- **Date:** 2026-10-22

## Context

Experiment 4 sorts hundreds of rules into behavioural classes in the spirit of Wolfram's four classes. The classification has to be automatic, cheap enough for hundreds of rules, and open to the question "why was this rule put here?".

## Decision

For each rule, `life.rulespace.rule_features` runs 10 random soups (density 0.35) on a 32 × 32 torus for up to 2000 generations and records: the fraction that reach a cycle, the median transient and period, the final live density and activity, and the damage from one flipped cell after 200 generations, relative to the level of two unrelated grids at the density of that moment, averaged over flips that did not heal.

`classify_rule` then applies, in order:

1. median final density 0 → **dead**;
2. most soups settle: median transient ≥ 100 → **complex**; else period 1 → **frozen**, period > 1 → **periodic**;
3. most soups never settle: damage ≥ 0.5 of full decorrelation → **chaotic**; else → **complex**.

B0 rules are excluded from sampling.

## Consequences

- Each class is explained by one or two numbers.
- The 100-generation threshold is tied to the grid size: on 64 × 64 it is scaled by the growth of Life's own transient (factor 2.2).
- Sensitivity was checked: the damage threshold (0.25–0.75) changes nothing, because damage is either near 0 or near 1; the transient threshold (50–150) moves the complex share between 6.6 % and 2.4 %.
- "Complex" is the residual middle class and can contain rules that are merely slow; representative rules are re-run on a larger grid.

## Alternatives considered

- **Clustering on features (k-means etc.):** no labelling decisions to defend, but the clusters would need interpretation afterwards and would shift with the sample.
- **Compression-based complexity** of the space–time diagram: a single number, but it mixes density and disorder and is hard to explain rule by rule.
- **Median damage over all flips:** misclassifies chaotic rules such as Seeds when, by chance, several flips heal at once.
