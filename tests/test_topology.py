import numpy as np
import pytest
from scipy import sparse

from life.topology import Graph, Lattice, lattice_adjacency

SHAPES = [(3, 3), (3, 5), (7, 4), (10, 10), (16, 9)]


@pytest.mark.parametrize("boundary", ["torus", "fixed"])
@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_convolution_matches_adjacency(boundary, shape, seed):
    """The lattice (convolution) and graph (A @ state) paths must agree exactly."""
    state = np.random.default_rng(seed).random(shape) < 0.4
    by_convolution = Lattice(boundary).neighbor_counts(state)
    by_adjacency = Graph(lattice_adjacency(shape, boundary)).neighbor_counts(state)
    np.testing.assert_array_equal(by_convolution, by_adjacency)


def test_torus_degrees_are_all_eight():
    degrees = lattice_adjacency((5, 6), "torus").sum(axis=1)
    assert (degrees == 8).all()


def test_fixed_degrees():
    degrees = np.asarray(lattice_adjacency((4, 5), "fixed").sum(axis=1)).reshape(4, 5)
    expected = np.full((4, 5), 8)
    expected[[0, -1], :] = 5
    expected[:, [0, -1]] = 5
    expected[[0, 0, -1, -1], [0, -1, 0, -1]] = 3
    np.testing.assert_array_equal(degrees, expected)


@pytest.mark.parametrize("boundary", ["torus", "fixed"])
def test_lattice_adjacency_is_symmetric_without_self_loops(boundary):
    a = lattice_adjacency((6, 7), boundary)
    assert (a != a.T).nnz == 0
    assert a.diagonal().sum() == 0


def test_lattice_counts_by_hand():
    state = np.zeros((4, 4), dtype=bool)
    state[0, 0] = True
    torus = Lattice("torus").neighbor_counts(state)
    fixed = Lattice("fixed").neighbor_counts(state)
    # On the torus the corner cell also neighbours the opposite corners.
    assert torus[3, 3] == 1 and torus[1, 1] == 1 and torus[0, 0] == 0
    assert fixed[3, 3] == 0 and fixed[1, 1] == 1


def test_graph_on_a_path():
    # 0 - 1 - 2 - 3
    a = sparse.csr_array(
        np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=np.int64)
    )
    state = np.array([True, False, True, True])
    assert Graph(a).neighbor_counts(state).tolist() == [0, 2, 1, 1]


def test_graph_rejects_wrong_sizes():
    with pytest.raises(ValueError):
        Graph(sparse.csr_array(np.zeros((2, 3), dtype=np.int64)))
    with pytest.raises(ValueError):
        Graph(lattice_adjacency((3, 3))).neighbor_counts(np.zeros(10, dtype=bool))


def test_unknown_boundary_raises():
    with pytest.raises(ValueError):
        Lattice("mirror")
    with pytest.raises(ValueError):
        lattice_adjacency((3, 3), "mirror")
