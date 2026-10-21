"""Interaction topologies: who counts as whose neighbour.

Every topology exposes ``neighbor_counts(state)``. A :class:`Lattice` computes it
by convolution; a :class:`Graph` computes it as ``A @ state`` for an adjacency
matrix ``A``. :func:`lattice_adjacency` builds the matrix of a lattice, so both
paths can be checked against each other.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

import numpy as np
from scipy import ndimage, sparse

Boundary = Literal["torus", "fixed"]

# Moore neighbourhood: the 8 surrounding cells, not the cell itself.
MOORE_KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
MOORE_OFFSETS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


class Topology(Protocol):
    def neighbor_counts(self, state: np.ndarray) -> np.ndarray: ...


def _check_boundary(boundary: str) -> None:
    if boundary not in ("torus", "fixed"):
        raise ValueError(f"unknown boundary: {boundary!r}")


@dataclass(frozen=True)
class Lattice:
    """A 2-D square lattice with the Moore neighbourhood.

    ``boundary="torus"`` wraps edges around; ``boundary="fixed"`` treats every
    cell outside the grid as permanently dead.
    """

    boundary: Boundary = "torus"

    def __post_init__(self) -> None:
        _check_boundary(self.boundary)

    def neighbor_counts(self, state: np.ndarray) -> np.ndarray:
        """Number of live Moore neighbours of every cell."""
        mode = "wrap" if self.boundary == "torus" else "constant"
        return ndimage.convolve(state.astype(np.uint8), MOORE_KERNEL, mode=mode, cval=0)


@dataclass(frozen=True, eq=False)
class Graph:
    """An arbitrary network given by an ``n x n`` adjacency matrix.

    ``adjacency[i, j] = 1`` means node ``j`` counts as a neighbour of node ``i``.
    The state may have any shape with ``n`` elements; it is flattened in C order,
    so a 2-D grid state works directly with :func:`lattice_adjacency`.
    """

    adjacency: sparse.csr_array

    def __post_init__(self) -> None:
        rows, cols = self.adjacency.shape
        if rows != cols:
            raise ValueError(f"adjacency must be square, got {self.adjacency.shape}")

    @property
    def n_nodes(self) -> int:
        return self.adjacency.shape[0]

    def neighbor_counts(self, state: np.ndarray) -> np.ndarray:
        """Number of live neighbours of every node, in the shape of ``state``."""
        if state.size != self.n_nodes:
            raise ValueError(f"state has {state.size} cells but the graph has {self.n_nodes} nodes")
        flat = state.reshape(-1).astype(np.int64)
        return (self.adjacency @ flat).reshape(state.shape)


def lattice_adjacency(shape: tuple[int, int], boundary: Boundary = "torus") -> sparse.csr_array:
    """把二维方格写成邻接矩阵 ``A``，使 ``A @ state.ravel()`` 等于卷积得到的邻居数。

    做什么
        给 ``rows x cols`` 的网格里每个格子编号 ``i = r * cols + c``（C 顺序，
        和 ``ravel()`` 一致），对每个格子的 8 个 Moore 邻居 ``j`` 令
        ``A[i, j] = 1``。``torus`` 时越界的坐标取模绕回；``fixed`` 时越界的
        邻居直接丢掉（等价于外面一圈永远是死细胞）。

    实验做法
        把结果包成 :class:`Graph` 交给 ``step``，就是"用网络的方式跑方格"。
        测试里拿它和 :class:`Lattice` 的卷积结果逐格比较；拓扑重连实验
        （Watts–Strogatz）也从这个矩阵出发，一条一条地改边。

    目的和意义
        这是"方格和网络共用一个引擎"的桥梁：方格只是邻接矩阵的一个特例。
        只要两条路径在方格上结果完全一致，之后在网络上看到的差异就只能来自
        拓扑本身，而不是代码实现的不同。

    易错点
        - 编号顺序必须和 ``ravel()`` 的 C 顺序一致，否则邻居会错位。
        - ``fixed`` 边界下角上只有 3 个邻居、边上 5 个，不是 8 个。
        - 网格某一边小于 3 时，环面上同一个邻居会被数两次（甚至数到自己）；
          卷积的 ``wrap`` 模式也是这样，两条路径仍然一致，但这已经不是
          通常意义上的 Moore 邻域。
        - 用稀疏矩阵：``n`` 个格子的稠密矩阵有 ``n²`` 个元素，100 x 100 的
          网格就是一亿个。

    Reference
        Newman, M. E. J. (2018). *Networks* (2nd ed.), ch. 6 "Mathematics of
        networks". Oxford University Press.
    """
    _check_boundary(boundary)
    rows, cols = shape
    r, c = np.divmod(np.arange(rows * cols), cols)
    sources, targets = [], []
    for dr, dc in MOORE_OFFSETS:
        nr, nc = r + dr, c + dc
        if boundary == "torus":
            nr, nc = nr % rows, nc % cols
            keep = np.ones_like(nr, dtype=bool)
        else:
            keep = (nr >= 0) & (nr < rows) & (nc >= 0) & (nc < cols)
        sources.append((r * cols + c)[keep])
        targets.append((nr * cols + nc)[keep])
    i = np.concatenate(sources)
    j = np.concatenate(targets)
    data = np.ones(i.size, dtype=np.int64)
    # Duplicate (i, j) pairs are summed, matching the convolution on tiny tori.
    return sparse.csr_array((data, (i, j)), shape=(rows * cols, rows * cols))
