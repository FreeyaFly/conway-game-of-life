"""Scanning the space of life-like rules."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from life.engine import step
from life.metrics import _key, damage_spread
from life.rules import Rule
from life.topology import Lattice

TORUS = Lattice("torus")
CLASSES = ("dead", "frozen", "periodic", "complex", "chaotic")


def sample_rules(n: int, rng: np.random.Generator, exclude_b0: bool = True) -> list[Rule]:
    """``n`` distinct rules drawn uniformly from the life-like rules (without B0 by default)."""
    total = 2**17 if exclude_b0 else 2**18
    if n > total:
        raise ValueError("more rules requested than exist")
    chosen: set[tuple[frozenset[int], frozenset[int]]] = set()
    rules = []
    while len(rules) < n:
        digits = rng.random(18) < 0.5
        if exclude_b0:
            digits[0] = False
        birth = frozenset(int(k) for k in np.flatnonzero(digits[:9]))
        survive = frozenset(int(k) for k in np.flatnonzero(digits[9:]))
        if (birth, survive) not in chosen:
            chosen.add((birth, survive))
            rules.append(Rule(birth, survive))
    return rules


def langton_lambda(rule: Rule) -> float:
    """Fraction of the 18 neighbour-count entries that produce a live cell."""
    return (len(rule.birth) + len(rule.survive)) / 18


def neighbours(rule: Rule, exclude_b0: bool = True) -> list[Rule]:
    """All rules that differ from ``rule`` by adding or removing one digit."""
    out = []
    for k in range(1 if exclude_b0 else 0, 9):
        out.append(Rule(rule.birth ^ {k}, rule.survive))
    for k in range(9):
        out.append(Rule(rule.birth, rule.survive ^ {k}))
    return out


@dataclass(frozen=True)
class RuleFeatures:
    """Median behaviour of one rule over several random soups.

    ``settled``: fraction of soups that reached a cycle within the step cap.
    ``transient`` and ``period``: medians over the settled soups (NaN if none).
    ``density``: median live density at the end. ``activity``: median fraction of
    cells changing per step at the end. ``damage``: mean damage after
    ``damage_steps`` from one flipped cell, relative to the level of two
    unrelated grids, ``2ρ(1−ρ)`` with ``ρ`` the live density at that time
    (0 = no spread, about 1 = fully decorrelated). It is averaged over the flips
    that did not heal, because even under chaotic rules some flips die out at once;
    0 if every flip healed.
    """

    settled: float
    transient: float
    period: float
    density: float
    activity: float
    damage: float


def _run(state, rule, max_steps):
    seen: dict[bytes, int] = {}
    changes: deque[float] = deque(maxlen=100)
    current = state
    for t in range(max_steps + 1):
        key = _key(current)
        if key in seen:
            first = seen[key]
            period = t - first
            cycle_changes = []
            s = current
            for _ in range(period):
                nxt = step(s, rule, TORUS)
                cycle_changes.append(np.mean(nxt != s))
                s = nxt
            return True, first, period, current.mean(), float(np.mean(cycle_changes))
        seen[key] = t
        nxt = step(current, rule, TORUS)
        changes.append(float(np.mean(nxt != current)))
        current = nxt
    return False, np.nan, np.nan, current.mean(), float(np.mean(changes))


def rule_features(
    rule: Rule,
    size: int = 32,
    runs: int = 10,
    density: float = 0.35,
    max_steps: int = 2000,
    damage_steps: int = 200,
    seed: int = 0,
) -> RuleFeatures:
    """Run ``runs`` random soups under ``rule`` on a torus and summarise their behaviour."""
    settled, transients, periods, densities, activities, damages = [], [], [], [], [], []
    for r in range(runs):
        rng = np.random.default_rng([seed, r])
        soup = rng.random((size, size)) < density
        ok, transient, period, rho, activity = _run(soup, rule, max_steps)
        settled.append(ok)
        if ok:
            transients.append(transient)
            periods.append(period)
        densities.append(rho)
        activities.append(activity)
        cell = tuple(int(v) for v in rng.integers(0, size, 2))
        d = damage_spread(soup, cell, damage_steps, rule, TORUS)[-1] / soup.size
        # Compare with two unrelated grids at the density the run has at that time.
        state = soup
        for _ in range(damage_steps):
            state = step(state, rule, TORUS)
        rho_then = state.mean()
        reference = 2 * rho_then * (1 - rho_then)
        damages.append(d / reference if reference > 0 else 0.0)
    spread = [d for d in damages if d > 0]
    return RuleFeatures(
        settled=float(np.mean(settled)),
        transient=float(np.median(transients)) if transients else float("nan"),
        period=float(np.median(periods)) if periods else float("nan"),
        density=float(np.median(densities)),
        activity=float(np.median(activities)),
        damage=float(np.mean(spread)) if spread else 0.0,
    )


def classify_rule(
    f: RuleFeatures,
    long_transient: float = 100.0,
    chaotic_damage: float = 0.5,
) -> str:
    """用几条透明的阈值，把一条规则的长期行为归入五类之一。

    做什么
        依次判断（先命中先返回）：
        1. **dead（死寂）**：多数初始状态最后一个活细胞都不剩（中位密度为 0）。
        2. 多数初始状态在步数上限内进入循环时：
           暂态中位数 ≥ ``long_transient`` → **complex（复杂）**；
           否则周期中位数为 1 → **frozen（冻结）**，大于 1 → **periodic（周期）**。
        3. 多数初始状态始终不进入循环时：
           翻转一个细胞后的损伤达到"两张无关网格"水平的 ``chaotic_damage`` 倍以上
           → **chaotic（混沌）**；否则 → **complex（复杂）**。

    实验做法
        实验 4b 对几百条随机规则先用 :func:`rule_features` 提取特征，再用本函数
        分类，统计各类比例、各类随 Langton λ 的分布；4c 对 Life 的 17 条
        "邻居规则"逐条分类。两个阈值都放大、缩小一半重新分类，检查结论是否
        依赖于阈值。

    目的和意义
        这是 Wolfram（1984）四类行为的一个可计算版本：冻结、简单周期、混沌，
        以及介于秩序和混沌之间、暂态很长、有局部结构的"复杂"类。
        用透明的阈值而不是黑箱聚类，是为了让每条规则的归类都能被追问
        "为什么"，也方便检查阈值对结论的影响。

    易错点
        - 阈值是人为设定的，而且和网格大小、步数上限有关：同一条规则在
          32 × 32 上暂态 300，在 64 × 64 上可能是 1000。比较必须在同一设置下。
        - "复杂"是一个兜底的中间类：长暂态，或者不收敛但损伤不扩散。
          它包含了 Life 这样的规则，也可能混进一些只是"慢"的规则，
          需要用代表性规则逐一复核。
        - 损伤是相对于 2ρ(1−ρ) 计算的；密度接近 0 或 1 时参照值很小，
          比值会不稳定，所以先判死寂。

    Reference
        Wolfram, S. (1984). Universality and complexity in cellular automata.
        *Physica D*, 10(1–2), 1–35.
        Langton, C. G. (1990). Computation at the edge of chaos: Phase
        transitions and emergent computation. *Physica D*, 42(1–3), 12–37.
    """
    if f.density == 0:
        return "dead"
    if f.settled >= 0.5:
        if f.transient >= long_transient:
            return "complex"
        return "frozen" if f.period == 1 else "periodic"
    if f.damage >= chaotic_damage:
        return "chaotic"
    return "complex"
