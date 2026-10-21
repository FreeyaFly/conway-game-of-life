import numpy as np
import pytest

from life.rules import CONWAY, parse_rule
from life.rulespace import (
    RuleFeatures,
    classify_rule,
    langton_lambda,
    neighbours,
    rule_features,
    sample_rules,
)


def test_sample_rules_are_distinct_and_without_b0():
    rules = sample_rules(200, np.random.default_rng(0))
    assert len({str(r) for r in rules}) == 200
    assert all(0 not in r.birth for r in rules)


def test_sample_rules_is_reproducible():
    a = sample_rules(20, np.random.default_rng(1))
    b = sample_rules(20, np.random.default_rng(1))
    assert [str(r) for r in a] == [str(r) for r in b]


def test_langton_lambda():
    assert langton_lambda(CONWAY) == pytest.approx(3 / 18)
    assert langton_lambda(parse_rule("B/S")) == 0


def test_life_has_seventeen_neighbours():
    near = neighbours(CONWAY)
    assert len(near) == 17
    assert len({str(r) for r in near}) == 17
    assert "B/S23" in {str(r) for r in near}
    assert "B3/S2" in {str(r) for r in near}
    assert all(0 not in r.birth for r in near)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("B/S", "dead"),
        ("B3/S012345678", "frozen"),
        ("B2/S", "chaotic"),
        ("B3/S23", "complex"),
    ],
)
def test_reference_rules_are_classified_as_expected(text, expected):
    features = rule_features(parse_rule(text), runs=4)
    assert classify_rule(features) == expected


def test_classify_thresholds():
    base = dict(settled=1.0, transient=10.0, period=1.0, density=0.1, activity=0.0, damage=0.0)
    assert classify_rule(RuleFeatures(**base)) == "frozen"
    assert classify_rule(RuleFeatures(**{**base, "period": 2.0})) == "periodic"
    assert classify_rule(RuleFeatures(**{**base, "transient": 500.0})) == "complex"
    assert classify_rule(RuleFeatures(**{**base, "density": 0.0})) == "dead"
    unsettled = {**base, "settled": 0.0, "transient": np.nan, "period": np.nan}
    assert classify_rule(RuleFeatures(**{**unsettled, "damage": 0.9})) == "chaotic"
    assert classify_rule(RuleFeatures(**{**unsettled, "damage": 0.1})) == "complex"


def test_replicator_empties_a_32_torus_at_generation_16():
    # Experiment 4, puzzle E: B1357/S1357 is a parity rule; 16 steps cancel every shift.
    from life.engine import run
    from life.topology import Lattice

    rule = parse_rule("B1357/S1357")
    for seed in range(3):
        soup = np.random.default_rng(seed).random((32, 32)) < 0.35
        history = run(soup, 16, rule, Lattice("torus"))
        assert history[15].any()
        assert not history[16].any()


def test_low_birth_digits_make_life_chaotic():
    # Experiment 4c: adding B1 to Life tips it into chaos; adding B8 does not.
    assert classify_rule(rule_features(parse_rule("B13/S23"), runs=4)) == "chaotic"
    assert classify_rule(rule_features(parse_rule("B38/S23"), runs=4)) == "complex"
