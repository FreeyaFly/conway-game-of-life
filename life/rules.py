"""Life-like rules in B/S notation (e.g. ``B3/S23`` for Conway's Game of Life)."""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

_RULE_RE = re.compile(r"^B(?P<birth>[0-8]*)/S(?P<survive>[0-8]*)$", re.IGNORECASE)


@dataclass(frozen=True)
class Rule:
    """A life-like rule: which live-neighbour counts cause birth and survival."""

    birth: frozenset[int]
    survive: frozenset[int]

    def __str__(self) -> str:
        b = "".join(str(n) for n in sorted(self.birth))
        s = "".join(str(n) for n in sorted(self.survive))
        return f"B{b}/S{s}"

    def apply(self, state: np.ndarray, counts: np.ndarray) -> np.ndarray:
        """Return the next state given the current state and live-neighbour counts."""
        size = max(9, int(counts.max(initial=0)) + 1)
        born = np.zeros(size, dtype=bool)
        stays = np.zeros(size, dtype=bool)
        born[list(self.birth)] = True
        stays[list(self.survive)] = True
        return np.where(state, stays[counts], born[counts])


def parse_rule(text: str) -> Rule:
    """Parse a rule string such as ``"B3/S23"`` (case-insensitive, digits 0-8)."""
    match = _RULE_RE.match(text.strip())
    if match is None:
        raise ValueError(f"not a B/S rule string: {text!r}")
    return Rule(
        birth=frozenset(int(c) for c in match["birth"]),
        survive=frozenset(int(c) for c in match["survive"]),
    )


CONWAY = parse_rule("B3/S23")
