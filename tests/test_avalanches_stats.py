import numpy as np
import pytest

from life.avalanches import OPEN, avalanche, open_border, settle
from life.metrics import detect_cycle
from life.patterns import BLINKER, BLOCK, place
from life.stats import fit_power_law

SHAPE = (12, 12)
MASK = open_border(SHAPE)


def test_open_border_clears_a_frame():
    assert MASK.sum() == 8 * 8
    assert not MASK[:2].any() and not MASK[:, -2:].any()


def test_settle_returns_a_state_on_the_cycle():
    state = place(BLINKER, SHAPE, at=(5, 4))
    settled = settle(state, topology=OPEN, mask=MASK)
    cycle = detect_cycle(settled, topology=OPEN)
    assert cycle.transient == 0 and cycle.period == 2


def test_lonely_added_cell_is_a_size_one_avalanche():
    empty = np.zeros(SHAPE, dtype=bool)
    result = avalanche(empty, (6, 6), topology=OPEN, mask=MASK)
    assert (result.size, result.duration) == (1, 1)
    assert not result.state.any()


def test_cell_next_to_a_block_has_a_bounded_footprint():
    block = place(BLOCK, SHAPE, at=(5, 5))
    result = avalanche(block, (4, 5), topology=OPEN, mask=MASK)
    assert result.state is not None
    assert 1 <= result.size <= MASK.sum()
    # The new state is settled: running it on gives a cycle that starts at once.
    assert detect_cycle(result.state, topology=OPEN).transient == 0


def test_footprint_ignores_oscillators_that_were_already_there():
    # A blinker far from the added cell keeps changing, but it is not damage.
    blinker = place(BLINKER, SHAPE, at=(3, 3))
    result = avalanche(blinker, (8, 8), topology=OPEN, mask=MASK)
    assert result.size == 1


def test_avalanche_reports_cutoff():
    soup = np.random.default_rng(0).random(SHAPE) < 0.5
    result = avalanche(soup & MASK, (6, 6), topology=OPEN, mask=MASK, max_steps=1)
    assert result.state is None


def _power_law_sample(alpha, xmin, n, seed):
    u = np.random.default_rng(seed).random(n)
    return np.floor((xmin - 0.5) * (1 - u) ** (-1 / (alpha - 1)) + 0.5)


@pytest.mark.parametrize("alpha", [1.8, 2.5])
def test_fit_recovers_power_law_exponent(alpha):
    fit = fit_power_law(_power_law_sample(alpha, 1, 5000, seed=1))
    assert fit.alpha == pytest.approx(alpha, abs=0.1)
    assert fit.loglik_ratio > 0


def test_fit_prefers_exponential_for_exponential_data():
    data = np.random.default_rng(2).geometric(0.2, size=5000)
    fit = fit_power_law(data)
    assert fit.loglik_ratio < 0
    assert fit.p_value < 0.1


def test_fit_needs_enough_data():
    with pytest.raises(ValueError):
        fit_power_law(np.array([1, 2, 3]))
