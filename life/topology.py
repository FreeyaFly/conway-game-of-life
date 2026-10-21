"""Interaction topologies: who counts as whose neighbour."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import ndimage

Boundary = Literal["torus", "fixed"]

# Moore neighbourhood: the 8 surrounding cells, not the cell itself.
MOORE_KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)


@dataclass(frozen=True)
class Lattice:
    """A 2-D square lattice with the Moore neighbourhood.

    ``boundary="torus"`` wraps edges around; ``boundary="fixed"`` treats every
    cell outside the grid as permanently dead.
    """

    boundary: Boundary = "torus"

    def __post_init__(self) -> None:
        if self.boundary not in ("torus", "fixed"):
            raise ValueError(f"unknown boundary: {self.boundary!r}")

    def neighbor_counts(self, state: np.ndarray) -> np.ndarray:
        """Number of live Moore neighbours of every cell."""
        mode = "wrap" if self.boundary == "torus" else "constant"
        return ndimage.convolve(state.astype(np.uint8), MOORE_KERNEL, mode=mode, cval=0)
