# Experiment 1: attractors and chaos

> **Status:** done (v2.0-alpha.1).
> Notebook: [`notebooks/01_attractors.ipynb`](../../notebooks/01_attractors.ipynb) · raw data: [`data/exp01/cycles.csv`](../../data/exp01/cycles.csv), [`data/exp01/damage.npz`](../../data/exp01/damage.npz)

## Question

A finite grid with a deterministic rule must eventually repeat a state, so every run ends on a cycle (an *attractor*). Starting from random soups on a torus:

1. How long does Conway's Game of Life wander before reaching its cycle (the *transient*), and how does that depend on the grid size $L$?
2. What kind of cycle does it end on (the *period*)?
3. How sensitive is the outcome to flipping a single initial cell? *(part 1c)*

## Predictions (written before any run)

| # | Question | Prediction |
|---|---|---|
| 1 | Typical transient on a 64 × 64 torus, density 0.35 | ~10 000 generations |
| 2 | Transient when $L$ doubles from 64 to 128 | grows like $L^2$ |
| 3 | Most common period; very long periods? | around 100; very long periods are rare |
| 4 | Fraction of single-cell flips that end on the same attractor | ~1 in 1000 |
| 5 | Growth of the damage $d(t)$ under Life | grows, then levels off (S-shaped) |
| 6 | Any run not settling within 20 000 generations? | none |

## Method

- Torus, Moore neighbourhood, rule B3/S23. Initial cells alive independently with probability 0.35; seeds 0, 1, 2, … for reproducibility.
- Grid sizes $L$ = 16, 32, 64 (200 soups each) and 128 (50 soups).
- `detect_cycle` stores every state as packed bytes and stops at the first repeat, so transient and period are exact. The cap is 20 000 generations; a run hitting it would be reported as censored.
- Damage spreading (1c): 64 × 64 torus, 100 soups per rule (seeds 10 000, 10 001, …), one randomly chosen cell flipped, both runs advanced for 1500 generations. Rules: Life (B3/S23), HighLife (B36/S23), Seeds (B2/S). For Life and HighLife both runs are also followed to their final cycle and the attractors compared.

Definitions are in [methods](../methods.md); background in [concepts](../concepts.md).

## Results

### 1a. Transients

| $L$ | runs | censored | median | mean | 90th pct. | max |
|---|---|---|---|---|---|---|
| 16 | 200 | 0 | 110 | 136 | 262 | 528 |
| 32 | 200 | 0 | 352 | 479 | 1048 | 2175 |
| 64 | 200 | 0 | 1029 | 1266 | 2272 | 5481 |
| 128 | 50 | 0 | 2404 | 2892 | 4984 | 7824 |

![Transient lengths](../figures/exp01_transients.png)

The median transient grows faster than $L$ but slower than $L^2$, and the growth slows down as $L$ increases (×3.2, ×2.9, ×2.3 per doubling).

### 1b. Periods

| period | 1 | 2 | 64 | 128 | 256 |
|---|---|---|---|---|---|
| runs (all sizes) | 141 | 494 | 5 | 8 | 2 |

By grid size: $L$ = 16 → 112 × period 1, 83 × period 2, 5 × period 64; $L$ = 32 → 28, 164, 8 × period 128; $L$ = 64 → 1, 197, 2 × period 256; $L$ = 128 → 50 × period 2.

![Periods](../figures/exp01_periods.png)

### Predictions vs. results (1a, 1b)

| # | Prediction | Result |
|---|---|---|
| 1 | ~10 000 | Median 1029: off by a factor of ten. Most regions turn into still lifes and blinkers within a few hundred generations. |
| 2 | $\propto L^2$ | Between $L$ and $L^2$, with a falling slope; see puzzle C for why. |
| 3 | period ~100, long periods rare | Period 2 dominates (76 %) because the grid's period is the least common multiple of its objects' periods (puzzle B). Long periods are indeed rare (2.3 %) and come from gliders (puzzle A). |
| 6 | none censored | Correct: all 650 runs settled; the longest transient was 7824. |

### 1c. Damage spreading

| rule | healed ($d$ back to 0) | median $d(100)$ | median $d(1500)$ | max $d$ |
|---|---|---|---|---|
| Life | 0 % | 670 | 268 | 986 |
| HighLife | 0 % | 836 | 172 | 1259 |
| Seeds | 17 % | 1356 | 1358 | 1506 |

The grid has 4096 cells.

![Damage spreading](../figures/exp01_damage.png)

- **Life:** the damage grows quickly, peaks at about 17 % of the grid around generation 80, then falls slowly to about 7 % and stays there. It never heals.
- **HighLife:** the same shape with a higher, earlier peak (about 23 % around generation 55) and a lower plateau (about 4 %).
- **Seeds:** within about 40 generations the damage jumps to one third of the grid and stays there; 17 % of the pairs heal at once (at generation 1 or 2).
- **Same attractor:** in all 100 Life pairs and all 100 HighLife pairs, the flipped run ends on a **different** attractor than the original.

<p align="center"><img src="../figures/exp01_damage.gif" alt="Damage spreading under Life: grey cells are alive in the original run, red cells differ" width="300"></p>

### Predictions vs. results (1c)

| # | Prediction | Result |
|---|---|---|
| 4 | ~1 in 1000 end on the same attractor | 0 of 100 for both Life and HighLife. Consistent: with 100 pairs, a rate of 1 in 1000 would almost always show 0. One flipped cell is enough to change the final state completely. |
| 5 | Life: grows, then levels off (S-shaped) | Half right. It grows and levels off, but **overshoots**: it peaks around generation 80 and then declines to a plateau (puzzle F). HighLife behaves similarly; Seeds saturates almost immediately and never declines (puzzle G). |

## Puzzles

**A. Long periods are exactly 64, 128 and 256, and each appears on only one grid size ($L$ = 16, 32, 64).**
*Hint: how many generations does a glider need to cross an $L \times L$ torus?*

<details><summary>Answer</summary>

All three equal $4L$. A glider moves one cell diagonally every 4 generations, so on an $L \times L$ torus it is back where it started after $4L$ generations. If a glider survives the transient, it circles forever and the whole grid has period $4L$. Replaying one of the period-64 runs on $L$ = 16 shows exactly that: its final cycle contains a single glider (5 live cells, 8 cells changing every 4 generations). On an infinite plane the glider would simply fly away, so these long periods are an artefact of the torus.
</details>

**B. The bigger the grid, the rarer period 1; on 128 × 128 every soup ends with period 2.**
*Hint: the grid's period depends on the period of every object on it.*

<details><summary>Answer</summary>

The period of the whole grid is the least common multiple of the periods of all objects on it. A single blinker (period 2) makes the whole grid period 2; period 1 requires that not one oscillator is left. A larger grid holds more objects, so "no oscillator at all" becomes very unlikely. A simple Poisson model fitted on $L$ = 16 (where 56 % of runs end with period 1) predicts 10 % for $L$ = 32 (observed 14 %) and essentially 0 for $L$ = 64 and 128 (observed 0.5 % and 0 %): the right trend, slightly underestimating the tail.
</details>

**C. Big grids never settle quickly: on 128 × 128 the shortest transient is 827 generations.**
*Hint: the grid is settled only when every region has settled.*

<details><summary>Answer</summary>

The transient of the whole grid is roughly the **maximum** of the transients of its regions. A 128 × 128 torus has the area of four 64 × 64 ones, so its transient behaves like the slowest of four. Drawing four transients from the $L$ = 64 results and taking the maximum (100 000 times) gives a median of 2042 and a 1st percentile of 764, against an observed median of 2404 and minimum of 827. The model explains most of the effect; the rest plausibly comes from interactions between regions (gliders and debris carrying activity elsewhere). Because a maximum grows slowly with the number of regions, it also explains why the transient grows more slowly than $L^2$.
</details>

**D. Period 3 never appears, although period-3 oscillators (such as the pulsar) exist.**
*Hint: what would the grid's period be with one pulsar and one blinker on it?*

<details><summary>Answer</summary>

A pulsar would make the grid's period 3, or 6 together with any blinker. Neither value appears, so none of the 650 final states (about 13 000 separate clusters of live cells in total) contains a period-3 oscillator. The pulsar has 48 cells and a high symmetry, and random soups rarely build it.
</details>

**F. Under Life the damage falls after its peak, yet the two runs never come back together.**
*Hint: compare the damage with the number of live cells in each run.*

<details><summary>Answer</summary>

At the end, the damage is almost exactly the number of live cells in the original run plus the number in the flipped run (for example 144 + 128 live cells against a damage of 264). So the two final states share almost nothing: they are completely different. The damage falls only because the soups themselves thin out from 35 % live cells to a few percent; with fewer live cells there are fewer cells that can differ. Measured relative to the number of live cells, the two runs stay fully decorrelated.
</details>

**G. Under Seeds the damage settles at almost exactly one third of the grid.**
*Hint: how different are two unrelated random grids with the same density of live cells?*

<details><summary>Answer</summary>

If two grids are independent and each cell is alive with probability $
ho$, they differ in a fraction $2
ho(1-
ho)$ of cells. Seeds settles at a live density of about $
ho = 0.211$, and $2 \cdot 0.211 \cdot 0.789 = 0.333$. So after about 40 generations the flipped run is as different from the original as an unrelated random grid: one cell has erased all memory of the starting state.
</details>

**H. Under Seeds 17 % of the pairs heal at once, but no pair heals later.**
*Hint: in Seeds every live cell dies at the next step. When can a flip change anything?*

<details><summary>Answer</summary>

The flipped cell itself never matters for long, since every live cell dies at the next step. What matters is whether the flip changes the fate of one of its 8 neighbours: a dead neighbour is born only with **exactly** 2 live neighbours, so the flip matters only if it moves a neighbour's count onto or off 2. When none of the neighbours is affected, the difference vanishes at generation 1; in one pair a single extra cell was born and died, so it vanished at generation 2. When the flip does change a birth that can feed further births, the difference spreads explosively and, in these runs, never disappeared again.
</details>

**E (open). No period 512 on the 128 × 128 torus.**

<details><summary>Current thinking</summary>

Not known. A glider survived in 2.5 %, 4 % and 1 % of the runs on $L$ = 16, 32 and 64. With a rate of 1–4 %, 50 runs would be expected to show 0.5–2 gliders; at 2 %, seeing none has a probability of about 36 %. So the absence may be chance. More runs on $L$ = 128, or a direct measurement of how often gliders are destroyed by debris on large grids, would settle it.
</details>

## Conclusions

- Random Life soups settle fast compared with the number of possible states: a typical 64 × 64 soup reaches its cycle after about 1000 generations, and the time grows more slowly than the area of the grid.
- The final state is almost always a mixture of still lifes and blinkers, so the grid's period is 2; long periods come from a glider circling the torus.
- The outcome is extremely sensitive to the initial state: flipping one cell in Life or HighLife changed the final attractor in every one of 200 pairs. Life is not "chaotic" in the sense of damage growing forever (the damage stays bounded by the shrinking number of live cells), but it never forgets a perturbation either. Seeds, by contrast, decorrelates completely within 40 generations.

## Limitations

- Only one initial density (0.35) and one rule for parts 1a and 1b.
- Damage spreading was measured on one grid size (64 × 64) with 100 pairs per rule; the healing rate of 0 for Life is an upper bound of a few percent, not proof that it never happens.
- 50 runs at $L$ = 128 make the large-grid numbers less precise.
- The torus lets gliders circle forever; on an open or infinite grid the long periods would not exist.

## Open questions

- How exactly does the transient scale with $L$ for larger grids, and how much of it is "slowest region" versus long-range interaction?
- Puzzle E: are gliders rarer survivors on large grids, or was it chance?
- Does a single flip ever leave a Life soup's final attractor unchanged, and how rare is it (needs thousands of pairs)?
- How does the damage behave on networks instead of lattices? (experiment 3)
