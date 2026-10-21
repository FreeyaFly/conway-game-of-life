"""Building and measuring networks: rewired lattices, clustering, path length."""

from __future__ import annotations

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph


def edge_list(adjacency: sparse.csr_array) -> np.ndarray:
    """Undirected edges ``(i, j)`` with ``i < j`` of a symmetric 0/1 adjacency matrix."""
    upper = sparse.triu(adjacency, k=1).tocoo()
    return np.column_stack([upper.row, upper.col]).astype(np.int64)


def from_edges(edges: np.ndarray, n_nodes: int) -> sparse.csr_array:
    """Symmetric 0/1 adjacency matrix with the given undirected edges."""
    i, j = edges[:, 0], edges[:, 1]
    rows = np.concatenate([i, j])
    cols = np.concatenate([j, i])
    data = np.ones(rows.size, dtype=np.int64)
    return sparse.csr_array((data, (rows, cols)), shape=(n_nodes, n_nodes))


def _check_simple(adjacency: sparse.csr_array) -> None:
    if (adjacency != adjacency.T).nnz or adjacency.diagonal().any() or adjacency.max() > 1:
        raise ValueError("adjacency must be symmetric, 0/1, and without self-loops")


def rewire(
    adjacency: sparse.csr_array,
    beta: float,
    rng: np.random.Generator,
    swaps_per_edge: int = 10,
) -> sparse.csr_array:
    """保持每个节点度数不变，把比例为 ``beta`` 的边随机打乱。

    做什么
        先随机选出 ``round(beta * E)`` 条边作为"可重连边"，其余的边原样保留。
        然后在可重连边之间反复做双边交换（double-edge swap）：随机取两条边
        ``(a, b)`` 和 ``(c, d)``，换成 ``(a, d)`` 和 ``(c, b)``。如果新边会形成
        自环或重边，这次交换作废、重新抽。交换次数是可重连边数的
        ``swaps_per_edge`` 倍，足以把它们充分打乱。每次交换前后，四个端点的
        度数都不变，所以**每个节点的邻居数始终和原来一样**。

    实验做法
        实验 3 从 64 × 64 环面方格（每个格子 8 个邻居）出发，对一组 ``beta``
        各生成一个网络，交给 :class:`~life.topology.Graph` 运行同一条规则。
        ``beta = 0`` 就是原方格；``beta = 1`` 是随机的 8-正则网络；中间是
        "大部分邻居仍在身边、少数邻居在远处"的小世界网络。

    目的和意义
        Life 的规则只看"有几个活邻居"。经典的 Watts–Strogatz 重连会让节点的
        邻居数变得不一样，结果里就混进了"邻居有几个"的影响。保持度数后，
        唯一改变的是"邻居是谁"，于是行为上的差异只能归因于拓扑结构。

    易错点
        - 交换必须拒绝自环和重边，否则度数虽然不变，图却不再是简单图，
          邻居数里会出现重复计数。
        - 交换的两条边要随机决定方向（``(c, d)`` 或 ``(d, c)``），否则只会
          产生一半可能的新连接。
        - 交换次数太少时，"可重连边"没有被充分打乱，``beta = 1`` 也达不到
          真正的随机网络。
        - 每次运行用新的随机种子生成新网络；同一个网络上跑很多初始状态，
          结论就只适用于那一个网络。

    Reference
        Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of
        "small-world" networks. *Nature*, 393, 440–442.
        Maslov, S., & Sneppen, K. (2002). Specificity and stability in topology
        of protein networks. *Science*, 296, 910–913.
    """
    if not 0 <= beta <= 1:
        raise ValueError("beta must be between 0 and 1")
    _check_simple(adjacency)
    n_nodes = adjacency.shape[0]
    edges = edge_list(adjacency)
    n_marked = round(beta * len(edges))
    if n_marked < 2:
        return from_edges(edges, n_nodes)

    marked = rng.choice(len(edges), size=n_marked, replace=False)
    present = {(int(a), int(b)) for a, b in edges}
    n_swaps = swaps_per_edge * n_marked
    # Draw all random numbers up front; a Python-level draw per swap is the bottleneck.
    picks = marked[rng.integers(n_marked, size=(n_swaps, 2))]
    flips = rng.random(n_swaps) < 0.5
    for (p, q), flip in zip(picks, flips, strict=True):
        if p == q:
            continue
        a, b = (int(x) for x in edges[p])
        c, d = (int(x) for x in edges[q])
        if flip:
            c, d = d, c
        if a == d or c == b:
            continue
        new_1 = (min(a, d), max(a, d))
        new_2 = (min(c, b), max(c, b))
        if new_1 == new_2 or new_1 in present or new_2 in present:
            continue
        present.discard((min(a, b), max(a, b)))
        present.discard((min(c, d), max(c, d)))
        present.add(new_1)
        present.add(new_2)
        edges[p] = new_1
        edges[q] = new_2
    return from_edges(edges, n_nodes)


def watts_strogatz(
    adjacency: sparse.csr_array, beta: float, rng: np.random.Generator
) -> sparse.csr_array:
    """Classic Watts–Strogatz rewiring: degrees are *not* preserved.

    Each edge ``(i, j)`` is, with probability ``beta``, replaced by ``(i, k)`` for a
    uniformly random ``k`` that is neither ``i`` nor already a neighbour of ``i``.
    The number of edges stays the same; individual degrees spread out.
    """
    if not 0 <= beta <= 1:
        raise ValueError("beta must be between 0 and 1")
    _check_simple(adjacency)
    n_nodes = adjacency.shape[0]
    edges = edge_list(adjacency)
    present = {(int(a), int(b)) for a, b in edges}
    neighbours = [set() for _ in range(n_nodes)]
    for a, b in edges:
        neighbours[a].add(int(b))
        neighbours[b].add(int(a))
    for e in np.flatnonzero(rng.random(len(edges)) < beta):
        i, j = (int(x) for x in edges[e])
        if len(neighbours[i]) >= n_nodes - 1:
            continue
        k = int(rng.integers(n_nodes))
        while k == i or k in neighbours[i]:
            k = int(rng.integers(n_nodes))
        present.discard((min(i, j), max(i, j)))
        neighbours[i].discard(j)
        neighbours[j].discard(i)
        neighbours[i].add(k)
        neighbours[k].add(i)
        present.add((min(i, k), max(i, k)))
        edges[e] = (min(i, k), max(i, k))
    return from_edges(edges, n_nodes)


def clustering(adjacency: sparse.csr_array) -> float:
    """Average local clustering coefficient (nodes with fewer than 2 neighbours count as 0)."""
    a = adjacency.astype(np.int64)
    degree = np.asarray(a.sum(axis=1)).ravel()
    closed = np.asarray((a @ a).multiply(a).sum(axis=1)).ravel()  # twice the triangles
    possible = degree * (degree - 1)
    local = np.divide(closed, possible, out=np.zeros(len(degree)), where=possible > 0)
    return float(local.mean())


def mean_path_length(
    adjacency: sparse.csr_array,
    n_sources: int | None = None,
    rng: np.random.Generator | None = None,
) -> float:
    """Mean shortest-path length between distinct connected node pairs.

    With ``n_sources`` set, distances are measured from that many random sources
    only, which is much cheaper on large graphs and accurate to about a percent.
    """
    n_nodes = adjacency.shape[0]
    if n_sources is None or n_sources >= n_nodes:
        sources = np.arange(n_nodes)
    else:
        rng = rng or np.random.default_rng()
        sources = rng.choice(n_nodes, size=n_sources, replace=False)
    dist = csgraph.shortest_path(adjacency, unweighted=True, indices=sources)
    finite = np.isfinite(dist) & (dist > 0)
    return float(dist[finite].mean())
