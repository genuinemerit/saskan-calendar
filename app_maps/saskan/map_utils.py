from __future__ import annotations

from typing import Iterable, List, Tuple

from .models import SimulationState


def summarize_settlements(state: SimulationState, block_size_km: int) -> List[str]:
    lines: List[str] = []
    rows = []
    for s in state.settlements:
        meta = s.metadata or {}
        stype = meta.get("type", "town")
        parent = meta.get("parent", "-")
        col, row = to_block(s.location, block_size_km)
        rows.append(
            (
                s.name,
                stype,
                parent,
                s.population,
                col,
                row,
                s.location,
            )
        )
    rows.sort(key=lambda r: r[3], reverse=True)
    lines.append("Settlements (sorted by population):")
    for name, stype, parent, pop, col, row, loc in rows:
        lines.append(
            f"  {name:12s} {stype:12s} pop={pop:5d} block=C{col}/R{row} km={loc} parent={parent}"
        )
    return lines


def render_coarse_map(
    state: SimulationState,
    block_size_km: int,
    col_min: int = 30,
    col_max: int = 38,
    row_min: int = 8,
    row_max: int = 20,
) -> List[str]:
    grid = [["." for _ in range(col_min, col_max + 1)] for _ in range(row_min, row_max + 1)]

    for s in state.settlements:
        col, row = to_block(s.location, block_size_km)
        if col_min <= col <= col_max and row_min <= row <= row_max:
            stype = (s.metadata or {}).get("type")
            if s.name == "Ingar":
                ch = "T"
            elif stype == "market-town":
                ch = "M"
            elif stype == "hamlet":
                ch = "h"
            else:
                ch = "t"
            grid[row - row_min][col - col_min] = ch

    lines: List[str] = []
    lines.append(
        f"Coarse map cols C{col_min}-C{col_max}, rows R{row_min}-R{row_max} "
        "(.: empty, T: Ingar, M: market-town, h: hamlet, t: town)"
    )
    for r_idx, r in enumerate(grid):
        row_num = row_min + r_idx
        lines.append(f"R{row_num:02d} " + "".join(r))
    lines.append("    " + "".join(f"C{c:02d}" for c in range(col_min, col_max + 1)))
    return lines


def to_block(coord: Tuple[int, int], block_size_km: int) -> Tuple[int, int]:
    x, y = coord
    col = int(x // block_size_km) + 1
    row = int(y // block_size_km) + 1
    return col, row

