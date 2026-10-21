import numpy as np
import pytest
from scipy import sparse

from life.engine import run
from life.networks import (
    clustering,
    edge_list,
    from_edges,
    mean_path_length,
    rewire,
    watts_strogatz,
)
from life.topology import Graph, lattice_adjacency

LATTICE = lattice_adjacency((12, 12), "torus")


def _is_simple(a):
    return (a != a.T).nnz == 0 and a.diagonal().sum() == 0 and a.max() == 1


def test_edge_list_round_trip():
    edges = edge_list(LATTICE)
    assert len(edges) == 12 * 12 * 8 // 2
    assert (from_edges(edges, 144) != LATTICE).nnz == 0


def test_rewire_zero_is_identity():
    assert (rewire(LATTICE, 0.0, np.random.default_rng(0)) != LATTICE).nnz == 0


@pytest.mark.parametrize("beta", [0.1, 0.5, 1.0])
def test_rewire_keeps_degrees_and_edge_count(beta):
    a = rewire(LATTICE, beta, np.random.default_rng(1))
    assert _is_simple(a)
    assert (np.asarray(a.sum(axis=1)).ravel() == 8).all()
    assert a.nnz == LATTICE.nnz


def test_rewire_leaves_unmarked_edges_alone():
    beta = 0.3
    a = rewire(LATTICE, beta, np.random.default_rng(2))
    kept = a.multiply(LATTICE).nnz // 2
    assert kept >= round((1 - beta) * LATTICE.nnz // 2)


def test_rewire_actually_changes_edges():
    a = rewire(LATTICE, 1.0, np.random.default_rng(3))
    kept = a.multiply(LATTICE).nnz // 2
    assert kept < 0.2 * (LATTICE.nnz // 2)


def test_rewire_is_reproducible():
    a = rewire(LATTICE, 0.5, np.random.default_rng(4))
    b = rewire(LATTICE, 0.5, np.random.default_rng(4))
    assert (a != b).nnz == 0


@pytest.mark.parametrize("beta", [0.0, 0.2, 1.0])
def test_watts_strogatz_keeps_edge_count(beta):
    a = watts_strogatz(LATTICE, beta, np.random.default_rng(5))
    assert _is_simple(a)
    assert a.nnz == LATTICE.nnz
    if beta == 0.0:
        assert (a != LATTICE).nnz == 0


def test_rewire_rejects_bad_input():
    with pytest.raises(ValueError):
        rewire(LATTICE, 1.5, np.random.default_rng(0))
    with pytest.raises(ValueError):
        rewire(sparse.csr_array(np.eye(3, dtype=np.int64)), 0.5, np.random.default_rng(0))


def _brute_clustering(a):
    dense = a.toarray()
    values = []
    for i in range(len(dense)):
        nb = np.flatnonzero(dense[i])
        k = len(nb)
        if k < 2:
            values.append(0.0)
            continue
        links = sum(dense[x, y] for x in nb for y in nb if x < y)
        values.append(2 * links / (k * (k - 1)))
    return float(np.mean(values))


def test_clustering_small_graphs():
    complete = from_edges(np.array([[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]), 4)
    star = from_edges(np.array([[0, 1], [0, 2], [0, 3]]), 4)
    assert clustering(complete) == pytest.approx(1.0)
    assert clustering(star) == pytest.approx(0.0)


def test_clustering_matches_brute_force():
    a = rewire(LATTICE, 0.2, np.random.default_rng(6))
    assert clustering(a) == pytest.approx(_brute_clustering(a))
    assert clustering(LATTICE) == pytest.approx(_brute_clustering(LATTICE))


def test_mean_path_length_on_a_path():
    path = from_edges(np.array([[0, 1], [1, 2]]), 3)
    assert mean_path_length(path) == pytest.approx(4 / 3)


def test_mean_path_length_sampling_is_close():
    full = mean_path_length(LATTICE)
    sampled = mean_path_length(LATTICE, n_sources=40, rng=np.random.default_rng(7))
    assert sampled == pytest.approx(full, rel=0.05)


def _random_regular_run(density, steps):
    graph = Graph(rewire(lattice_adjacency((32, 32)), 1.0, np.random.default_rng(0)))
    state = np.random.default_rng(1).random((32, 32)) < density
    return run(state, steps, topology=graph)


def test_life_keeps_boiling_on_a_random_regular_network():
    # Experiment 3: dense soups never freeze; the density sits near the mean-field value 0.37.
    history = _random_regular_run(0.35, 600)
    assert 0.33 < history[-100:].mean() < 0.42
    assert (history[-1] != history[-2]).mean() > 0.25


def test_sparse_soups_die_out_on_a_random_regular_network():
    # Below the unstable mean-field fixed point (about 0.19) activity dies out.
    assert not _random_regular_run(0.1, 300)[-1].any()
