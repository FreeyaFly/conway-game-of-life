import json
from pathlib import Path

import numpy as np
import pytest

from life.engine import run, step
from life.patterns import GLIDER, place
from life.rules import CONWAY, parse_rule
from life.topology import Graph, Lattice, lattice_adjacency

FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "patterns.json").read_text("utf-8"))


def _grid(shape, cells):
    grid = np.zeros(shape, dtype=bool)
    for r, c in cells:
        grid[r, c] = True
    return grid


@pytest.mark.parametrize("case", FIXTURES["cases"], ids=lambda case: case["name"])
@pytest.mark.parametrize("path", ["lattice", "graph"])
def test_fixture(case, path):
    shape = tuple(case["shape"])
    if path == "lattice":
        topology = Lattice(case["boundary"])
    else:
        topology = Graph(lattice_adjacency(shape, case["boundary"]))
    initial = _grid(shape, case["initial"])
    final = run(initial, case["steps"], parse_rule(case["rule"]), topology)[-1]
    np.testing.assert_array_equal(final, _grid(shape, case["expected"]))


@pytest.mark.parametrize("boundary", ["torus", "fixed"])
def test_lattice_and_graph_histories_match(boundary):
    shape = (20, 24)
    state = np.random.default_rng(42).random(shape) < 0.35
    by_lattice = run(state, 30, CONWAY, Lattice(boundary))
    by_graph = run(state, 30, CONWAY, Graph(lattice_adjacency(shape, boundary)))
    np.testing.assert_array_equal(by_lattice, by_graph)


def test_glider_on_fixed_boundary_ends_as_corner_block():
    history = run(place(GLIDER, (16, 16), at=(1, 1)), 64, topology=Lattice("fixed"))
    expected = _grid((16, 16), [(14, 14), (14, 15), (15, 14), (15, 15)])
    np.testing.assert_array_equal(history[-1], expected)


def test_step_does_not_modify_input():
    state = place(GLIDER, (8, 8), at=(1, 1))
    before = state.copy()
    step(state)
    np.testing.assert_array_equal(state, before)


def test_run_shape_and_initial_frame():
    state = place(GLIDER, (8, 8))
    history = run(state, 5)
    assert history.shape == (6, 8, 8)
    assert history.dtype == bool
    np.testing.assert_array_equal(history[0], state)


def test_run_rejects_negative_steps():
    with pytest.raises(ValueError):
        run(np.zeros((3, 3), dtype=bool), -1)
