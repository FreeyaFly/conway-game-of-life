"""The update loop: ``next = f(state, neighbour_counts(state))``."""

from __future__ import annotations

import numpy as np

from life.rules import CONWAY, Rule
from life.topology import Lattice, Topology

DEFAULT_TOPOLOGY = Lattice("torus")


def step(
    state: np.ndarray,
    rule: Rule = CONWAY,
    topology: Topology = DEFAULT_TOPOLOGY,
) -> np.ndarray:
    """把整个系统同步推进一代。

    做什么
        先由 topology 算出每个细胞的活邻居数 ``counts``，再由 rule 按
        "当前状态 + 邻居数" 决定下一代：死细胞在 ``counts ∈ birth`` 时出生，
        活细胞在 ``counts ∈ survive`` 时存活，其余一律死亡。
        所有细胞**同时**更新，输入数组不会被修改。

    实验做法
        这是所有实验的唯一入口。换规则（如 B36/S23 HighLife）只改 ``rule``；
        换交互结构（环面、固定边界、任意网络 :class:`~life.topology.Graph`）只改 ``topology``。
        状态和规则不变、只换 topology，就能单独看"拓扑"对全局行为的影响。

    目的和意义
        把"局部规则"和"谁是谁的邻居"拆成两个独立参数，对应项目的核心问题：
        局部规则和交互拓扑怎样共同决定全局行为。抽象形式是
        ``next = f(state, A · state)``，其中 ``A · state`` 就是邻居数。

    易错点
        - 不能边算边写回同一个数组：那样会变成"异步更新"，结果完全不同。
        - 环面（torus）和固定边界在网格边缘给出不同结果；glider 在环面上
          能一直飞，在固定边界上会撞墙变形。比较实验时边界必须一致。
        - 状态用 ``bool``；邻居数用整数，不要把两者混用做算术。

    Reference
        Gardner, M. (1970). The fantastic combinations of John Conway's new
        solitaire game "life". Scientific American, 223(4), 120–123.
    """
    counts = topology.neighbor_counts(state)
    return rule.apply(state.astype(bool), counts)


def run(
    state: np.ndarray,
    steps: int,
    rule: Rule = CONWAY,
    topology: Topology = DEFAULT_TOPOLOGY,
) -> np.ndarray:
    """Return the history as an array of shape ``(steps + 1, *state.shape)``.

    ``history[0]`` is the initial state and ``history[t]`` the state after ``t`` steps.
    """
    if steps < 0:
        raise ValueError("steps must be non-negative")
    history = np.empty((steps + 1, *state.shape), dtype=bool)
    history[0] = state
    for t in range(steps):
        history[t + 1] = step(history[t], rule, topology)
    return history
