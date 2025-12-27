from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

from .models import Route, SimulationState
from .map_utils import to_block


def plot_state(
    state: SimulationState,
    block_size_km: int,
    outfile: Path,
    col_min: int,
    col_max: int,
    row_min: int,
    row_max: int,
) -> None:
    """Render a matplotlib plot for a window of the grid."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError("matplotlib is required for plotting") from exc

    outfile.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))

    x_min = (col_min - 1) * block_size_km
    x_max = col_max * block_size_km
    y_min = (row_min - 1) * block_size_km
    y_max = row_max * block_size_km

    locations = {s.name: s.location for s in state.settlements}

    # Plot routes fully inside window
    for route in _routes_in_window(
        state.routes, locations, block_size_km, col_min, col_max, row_min, row_max
    ):
        ax.plot(
            [route[0][0], route[1][0]],
            [route[0][1], route[1][1]],
            color="#888888",
            linewidth=1,
            alpha=0.6,
        )

    for s in state.settlements:
        col, row = to_block(s.location, block_size_km)
        if not (col_min <= col <= col_max and row_min <= row <= row_max):
            continue
        meta = s.metadata or {}
        stype = meta.get("type", "town")
        if s.name == "Ingar":
            color = "#e39d12"
            size = 80
        elif stype == "market-town":
            color = "#d95f02"
            size = 50
        elif stype == "hamlet":
            color = "#7570b3"
            size = 35
        else:
            color = "#1b9e77"
            size = 40
        ax.scatter(
            s.location[0],
            s.location[1],
            s=size,
            color=color,
            alpha=0.9,
            edgecolors="k",
            linewidths=0.3,
        )
        ax.text(
            s.location[0] + 5, s.location[1] + 5, s.name, fontsize=7, color="#222222"
        )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("km east")
    ax.set_ylabel("km south")
    ax.set_title(f"Saskan Lands window C{col_min}-C{col_max}, R{row_min}-R{row_max}")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
    plt.tight_layout()
    fig.savefig(outfile)
    plt.close(fig)


def _routes_in_window(
    routes: Iterable[Route],
    locations: dict,
    block_size_km: int,
    col_min: int,
    col_max: int,
    row_min: int,
    row_max: int,
) -> Iterable[Tuple[Tuple[float, float], Tuple[float, float]]]:
    col_range = range(col_min, col_max + 1)
    row_range = range(row_min, row_max + 1)

    def in_window(coord: Tuple[int, int]) -> bool:
        c, r = to_block(coord, block_size_km)
        return c in col_range and r in row_range

    for route in routes:
        a = locations.get(route.origin)
        b = locations.get(route.destination)
        if not a or not b:
            continue
        # Only plot if both endpoints are inside the window to keep the view focused.
        if in_window(a) and in_window(b):
            yield a, b
