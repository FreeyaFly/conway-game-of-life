import numpy as np
import pytest

from life.metrics import damage_spread, detect_cycle, flip, hamming
from life.patterns import BLINKER, BLOCK, place
from life.topology import Lattice


def test_still_life_has_period_one():
    cycle = detect_cycle(place(BLOCK, (6, 6), at=(2, 2)))
    assert (cycle.transient, cycle.period) == (0, 1)


def test_blinker_has_period_two():
    cycle = detect_cycle(place(BLINKER, (5, 5), at=(2, 1)), topology=Lattice("fixed"))
    assert (cycle.transient, cycle.period) == (0, 2)


def test_lonely_cell_dies_after_one_step():
    state = np.zeros((5, 5), dtype=bool)
    state[2, 2] = True
    cycle = detect_cycle(state)
    assert (cycle.transient, cycle.period) == (1, 1)
    assert cycle.attractor == detect_cycle(np.zeros((5, 5), dtype=bool)).attractor


def test_attractor_does_not_depend_on_phase():
    horizontal = place(BLINKER, (5, 5), at=(2, 1))
    vertical = place(BLINKER.T, (5, 5), at=(1, 2))
    fixed = Lattice("fixed")
    assert detect_cycle(horizontal, topology=fixed).attractor == (
        detect_cycle(vertical, topology=fixed).attractor
    )


def test_different_attractors_differ():
    block = detect_cycle(place(BLOCK, (6, 6), at=(2, 2)))
    empty = detect_cycle(np.zeros((6, 6), dtype=bool))
    assert block.attractor != empty.attractor


def test_returns_none_when_cut_off():
    state = np.zeros((5, 5), dtype=bool)
    state[2, 2] = True
    assert detect_cycle(state, max_steps=0) is None


def test_hamming_and_flip():
    a = np.zeros((3, 3), dtype=bool)
    b = flip(a, (1, 2))
    assert hamming(a, b) == 1
    assert not a.any()  # flip returns a copy
    assert hamming(b, flip(b, (1, 2))) == 1


def test_damage_starts_at_one_and_has_right_length():
    state = np.random.default_rng(0).random((16, 16)) < 0.3
    d = damage_spread(state, (3, 4), 10)
    assert d.shape == (11,)
    assert d[0] == 1


def test_damage_matches_two_separate_runs():
    from life.engine import run

    state = np.random.default_rng(1).random((12, 12)) < 0.35
    d = damage_spread(state, (5, 5), 15)
    a = run(state, 15)
    b = run(flip(state, (5, 5)), 15)
    assert d.tolist() == [hamming(x, y) for x, y in zip(a, b, strict=True)]


def test_damage_rejects_negative_steps():
    with pytest.raises(ValueError):
        damage_spread(np.zeros((3, 3), dtype=bool), (0, 0), -1)
