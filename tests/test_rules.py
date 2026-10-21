import numpy as np
import pytest

from life.rules import CONWAY, parse_rule


@pytest.mark.parametrize("text", ["B3/S23", "b3/s23", " B3/S23 "])
def test_parse_conway(text):
    rule = parse_rule(text)
    assert rule == CONWAY
    assert rule.birth == {3}
    assert rule.survive == {2, 3}


@pytest.mark.parametrize("text", ["B36/S23", "B/S", "B012345678/S012345678", "B3/S"])
def test_str_round_trip(text):
    assert str(parse_rule(text)) == text


@pytest.mark.parametrize("text", ["", "B3S23", "S23/B3", "B9/S23", "B3/S2a", "23/3"])
def test_invalid_rule_strings_raise(text):
    with pytest.raises(ValueError):
        parse_rule(text)


def test_apply_table():
    counts = np.arange(9)
    dead = np.zeros(9, dtype=bool)
    alive = np.ones(9, dtype=bool)
    assert CONWAY.apply(dead, counts).tolist() == [n == 3 for n in range(9)]
    assert CONWAY.apply(alive, counts).tolist() == [n in (2, 3) for n in range(9)]


def test_apply_handles_counts_above_eight():
    # Network nodes can have more than 8 neighbours; such counts match no B/S digit.
    counts = np.array([3, 9, 12])
    alive = np.ones(3, dtype=bool)
    assert CONWAY.apply(~alive, counts).tolist() == [True, False, False]
    assert CONWAY.apply(alive, counts).tolist() == [True, False, False]
