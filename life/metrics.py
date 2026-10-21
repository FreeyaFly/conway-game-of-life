"""Measurements on trajectories: cycle detection and damage spreading."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from life.engine import DEFAULT_TOPOLOGY, step
from life.rules import CONWAY, Rule
from life.topology import Topology


@dataclass(frozen=True)
class Cycle:
    """Where a trajectory ends up.

    ``transient`` is the first time step that lies on the cycle, ``period`` the
    cycle length, and ``attractor`` an identifier that is the same for every
    trajectory ending on the same cycle, whatever phase it enters at.
    """

    transient: int
    period: int
    attractor: bytes


def _key(state: np.ndarray) -> bytes:
    return np.packbits(state, axis=None).tobytes()


def detect_cycle(
    state: np.ndarray,
    rule: Rule = CONWAY,
    topology: Topology = DEFAULT_TOPOLOGY,
    max_steps: int = 20_000,
) -> Cycle | None:
    """从初始状态一直推进，直到状态第一次重复，精确给出暂态长度和周期。

    做什么
        规则是确定性的、状态数有限，所以任何轨迹最终都会进入一个循环
        （静止的图样算周期 1）。每一代把状态压缩成字节串，记下它第一次
        出现的时间 ``seen[key] = t``。在时间 ``t`` 遇到已见过的状态时：
        暂态长度 ``transient = seen[key]``，周期 ``period = t - seen[key]``。
        ``attractor`` 取循环上所有状态字节串的最小值，作为这个循环的
        "身份证"：从不同相位进入同一个循环，得到的 ``attractor`` 相同。
        超过 ``max_steps`` 还没有重复就返回 ``None``（统计里记为截断）。

    实验做法
        实验 1a 对大量随机初始状态调用它，得到暂态长度和周期的分布；
        比较两条轨迹的 ``attractor`` 是否相同，就知道它们是否落到同一个
        吸引子（实验 1c）。

    目的和意义
        吸引子（attractor）是动力系统长期行为的归宿；进入吸引子之前的
        暂态（transient）是系统"还在探索"的阶段。v1 只用"最近 50 代
        不同状态少于 10 个"来猜测是否稳定，这里改为精确测量。

    易错点
        - 必须比较完整状态，不能只比较活细胞数：数量相同的状态可以完全不同。
        - 用字节串本身做键（而不是 ``hash()`` 的整数），就不会有哈希碰撞。
        - 内存和步数成正比：每一代存一个 ``n/8`` 字节的键。
        - 截断不等于"没有循环"，只说明在 ``max_steps`` 内没有观察到；
          统计时要单独报告截断的比例，不能直接丢掉。

    Reference
        Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos* (2nd ed.),
        ch. 9–10. Westview Press.
    """
    seen: dict[bytes, int] = {}
    keys: list[bytes] = []
    current = state.astype(bool)
    for t in range(max_steps + 1):
        key = _key(current)
        first = seen.get(key)
        if first is not None:
            return Cycle(transient=first, period=t - first, attractor=min(keys[first:]))
        seen[key] = t
        keys.append(key)
        current = step(current, rule, topology)
    return None


def hamming(a: np.ndarray, b: np.ndarray) -> int:
    """Number of cells in which two states differ."""
    return int(np.count_nonzero(a != b))


def flip(state: np.ndarray, cell: tuple[int, ...]) -> np.ndarray:
    """Return a copy of ``state`` with one cell inverted."""
    flipped = state.astype(bool)
    flipped[cell] = ~flipped[cell]
    return flipped


def damage_spread(
    state: np.ndarray,
    cell: tuple[int, ...],
    steps: int,
    rule: Rule = CONWAY,
    topology: Topology = DEFAULT_TOPOLOGY,
) -> np.ndarray:
    """翻转初始状态里的一个细胞，记录两条轨迹之间的差别随时间的变化。

    做什么
        轨迹 A 从 ``state`` 出发，轨迹 B 从"只在 ``cell`` 处不同"的状态
        出发，两者用同一个规则和拓扑同步推进。返回长度为 ``steps + 1``
        的数组 ``d``，``d[t]`` 是第 ``t`` 代两个状态之间的汉明距离
        （不同格子的个数），``d[0] = 1``。

    实验做法
        实验 1c 对很多随机初始状态和随机位置重复调用，画出 ``d(t)``
        的曲线和平均值，比较不同规则；``d`` 回到 0 表示扰动被"吸收"了。

    目的和意义
        这是混沌里"对初始条件敏感"的离散版本（damage spreading），
        相当于连续系统里的李雅普诺夫指数（Lyapunov exponent）：
        小扰动是被放大、维持还是消失，刻画了系统是有序、临界还是混沌。

    易错点
        - 两条轨迹必须用同一个规则、同一个拓扑、同一个边界。
        - ``d(t)`` 回到 0 之后会一直是 0（两条轨迹已完全重合），但
          ``d(t)`` 很小不代表会回到 0。
        - 在环面上，扰动扩散到绕回自身之后，``d(t)`` 的增长方式会改变；
          网格大小会影响看到的曲线形状。

    Reference
        Bagnoli, F., Rechtman, R., & Ruffo, S. (1992). Damage spreading and
        Lyapunov exponents in cellular automata. *Physics Letters A*, 172(1–2), 34–38.
    """
    if steps < 0:
        raise ValueError("steps must be non-negative")
    a = state.astype(bool)
    b = flip(a, cell)
    distances = np.empty(steps + 1, dtype=np.int64)
    distances[0] = hamming(a, b)
    for t in range(1, steps + 1):
        a = step(a, rule, topology)
        b = step(b, rule, topology)
        distances[t] = hamming(a, b)
    return distances
