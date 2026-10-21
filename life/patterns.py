"""Small reference patterns and a helper to place them on a grid."""

from __future__ import annotations

import numpy as np


def _pattern(rows: list[str]) -> np.ndarray:
    return np.array([[ch == "#" for ch in row] for row in rows], dtype=bool)


BLOCK = _pattern(["##", "##"])
BLINKER = _pattern(["###"])
# Moves one cell down and one cell right every 4 generations.
GLIDER = _pattern([".#.", "..#", "###"])


def place(pattern: np.ndarray, shape: tuple[int, int], at: tuple[int, int] = (0, 0)) -> np.ndarray:
    """Return an empty grid of ``shape`` with ``pattern`` placed at top-left ``at``."""
    grid = np.zeros(shape, dtype=bool)
    r, c = at
    h, w = pattern.shape
    if r < 0 or c < 0 or r + h > shape[0] or c + w > shape[1]:
        raise ValueError("pattern does not fit inside the grid at this position")
    grid[r : r + h, c : c + w] = pattern
    return grid
