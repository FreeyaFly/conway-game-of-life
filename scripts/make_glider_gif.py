"""Render a glider crossing a 16 x 16 torus and save it as docs/figures/glider.gif.

A glider moves one cell diagonally every 4 generations, so after 4 * 16 = 64
generations it has wrapped around the torus and is back where it started.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

from life.engine import run  # noqa: E402
from life.patterns import GLIDER, place  # noqa: E402
from life.topology import Lattice  # noqa: E402

SIZE = 16
STEPS = 4 * SIZE
OUT = Path(__file__).resolve().parents[1] / "docs" / "figures" / "glider.gif"


def main() -> None:
    history = run(place(GLIDER, (SIZE, SIZE), at=(1, 1)), STEPS, topology=Lattice("torus"))

    fig, ax = plt.subplots(figsize=(3, 3), dpi=100)
    image = ax.imshow(history[0], cmap=ListedColormap(["#eef0f2", "#2f7d4f"]), vmin=0, vmax=1)
    ax.set_xticks([])
    ax.set_yticks([])
    title = ax.set_title("")
    fig.tight_layout()

    def update(t: int):
        image.set_data(history[t])
        title.set_text(f"B3/S23 on a torus · t = {t}")
        return image, title

    animation = FuncAnimation(fig, update, frames=len(history), blit=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    animation.save(OUT, writer=PillowWriter(fps=8))
    print(f"saved {OUT.relative_to(OUT.parents[2])} ({len(history)} frames)")


if __name__ == "__main__":
    main()
