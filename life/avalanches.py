"""Avalanches: add one live cell to a settled state and measure the response."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from life.engine import step
from life.metrics import _key
from life.rules import CONWAY, Rule
from life.topology import Lattice, Topology

OPEN = Lattice("fixed")


def open_border(shape: tuple[int, int], width: int = 2) -> np.ndarray:
    """Mask that keeps the interior and clears a frame of ``width`` cells.

    Clearing the frame after every step lets gliders leave the system, like sand
    falling off the edge of a sandpile.
    """
    mask = np.zeros(shape, dtype=bool)
    mask[width:-width, width:-width] = True
    return mask


def _advance(state, rule, topology, mask):
    nxt = step(state, rule, topology)
    return nxt if mask is None else nxt & mask


def settle(
    state: np.ndarray,
    rule: Rule = CONWAY,
    topology: Topology = OPEN,
    mask: np.ndarray | None = None,
    max_steps: int = 20_000,
) -> np.ndarray | None:
    """Run until the trajectory reaches its cycle; return the first state on the cycle."""
    seen: dict[bytes, int] = {}
    history = []
    current = state.astype(bool) if mask is None else state.astype(bool) & mask
    for t in range(max_steps + 1):
        key = _key(current)
        if key in seen:
            return history[seen[key]]
        seen[key] = t
        history.append(current)
        current = _advance(current, rule, topology, mask)
    return None


@dataclass(frozen=True)
class Avalanche:
    """Outcome of one added cell.

    ``size`` counts the cells that differed at least once from the undisturbed run;
    ``duration`` is the number of steps until the disturbed run is back on a cycle;
    ``state`` is that new settled state (``None`` if the run hit the step cap).
    """

    size: int
    duration: int
    state: np.ndarray | None


def avalanche(
    state: np.ndarray,
    cell: tuple[int, int],
    rule: Rule = CONWAY,
    topology: Topology = OPEN,
    mask: np.ndarray | None = None,
    max_steps: int = 20_000,
) -> Avalanche:
    """在已经稳定的状态里加一个活细胞，测量它引发的"雪崩"有多大、持续多久。

    做什么
        输入的 ``state`` 必须已经在循环上（静止或振荡）。复制一份，把 ``cell``
        设为活细胞，然后让"原状态 A"和"加了细胞的状态 B"用同一规则并排推进。
        每一代记下 A 和 B 不同的格子，取所有代的并集作为雪崩的"足迹"。
        B 一旦回到它见过的状态（重新进入循环），雪崩结束：
        ``size`` = 足迹里的格子数，``duration`` = B 重新进入循环所用的代数，
        ``state`` = B 所在的新循环上的一个状态，作为下一次加细胞的起点。

    实验做法
        实验 2b 从一个已稳定的随机汤出发，反复"随机挑一个死细胞变活 →
        测雪崩 → 用新的稳定状态继续"，几千次后得到雪崩大小和持续时间的分布，
        再用 :func:`life.stats.fit_power_law` 判断是否服从幂律。
        ``mask`` 用来实现开放边界：每一代清空网格最外一圈，glider 飞出即消失。

    目的和意义
        这就是自组织临界（self-organized criticality）的标准做法：
        像往沙堆上一粒一粒加沙一样慢慢驱动系统，每次都等它完全平静再加下一粒。
        如果雪崩大小没有"典型尺度"、服从幂律，说明系统自己停在了临界状态。
        Bak、Chen 和 Creutz（1989）曾用这种方法论证 Life 是自组织临界的。

    易错点
        - 起点必须已经稳定，否则测到的是原来的暂态，而不是新加细胞的影响。
        - 振荡子（blinker）一直在变，不能用"有多少格子变了"来量雪崩；
          必须和不受干扰的 A 逐格比较，只算"因为加了细胞才不同"的格子。
        - 在环面上，雪崩可能放出一个永远绕圈的 glider，B 的循环周期会变成
          4L，此后每次雪崩都受它影响；开放边界可以避免这一点。
        - 达到 ``max_steps`` 还没结束的雪崩要单独记录（``state`` 为 ``None``），
          不能当作普通数据混进分布里。

    Reference
        Bak, P., Chen, K., & Creutz, M. (1989). Self-organized criticality in
        the 'Game of Life'. *Nature*, 342, 780–782.
        Bak, P., Tang, C., & Wiesenfeld, K. (1987). Self-organized criticality:
        An explanation of the 1/f noise. *Physical Review Letters*, 59, 381–384.
    """
    a = state.astype(bool)
    b = a.copy()
    b[cell] = True
    if mask is not None:
        a &= mask
        b &= mask
    footprint = a != b
    seen: dict[bytes, int] = {}
    history = []
    for t in range(max_steps + 1):
        key = _key(b)
        if key in seen:
            return Avalanche(int(footprint.sum()), seen[key], history[seen[key]])
        seen[key] = t
        history.append(b)
        a = _advance(a, rule, topology, mask)
        b = _advance(b, rule, topology, mask)
        footprint |= a != b
    return Avalanche(int(footprint.sum()), max_steps, None)
