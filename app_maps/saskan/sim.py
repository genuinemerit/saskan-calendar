from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .engine import SaskanEngine
from .persistence import snapshot_state
from .renderers.text import render_step
from .settings import SimulationConfig


def run_simulation(
    steps: int = 8,
    seed: Optional[int] = None,
    scenario: Optional[str] = None,
    tick_unit: str = "year",
    tick_length: float = 1.0,
    snapshot_every: int = 0,
    snapshot_dir: Optional[str] = None,
) -> List[str]:
    """Run a Saskan Lands simulation and return text lines."""
    config = SimulationConfig(
        steps=steps,
        seed=seed,
        scenario=scenario,
        tick_unit=tick_unit,
        tick_length=tick_length,
    )
    engine = SaskanEngine(config)
    output: List[str] = []
    snapshot_path: Optional[Path] = Path(snapshot_dir) if snapshot_dir else None
    output.extend(_preamble(engine))
    for _ in range(steps):
        events = engine.step()
        output.extend(render_step(engine.state, events))
        if snapshot_every and snapshot_path and engine.state.step % snapshot_every == 0:
            snapshot_state(
                engine.state, events, engine.config, snapshot_path, scenario=scenario
            )
    return output


def _preamble(engine: SaskanEngine) -> List[str]:
    lines: List[str] = []
    if not engine.state.settlements:
        return lines
    first = engine.state.settlements[0]
    if not first.metadata:
        return lines
    if "travel_losses" in first.metadata:
        losses = first.metadata["travel_losses"]
        roles = first.metadata.get("roles", {})
        lines.append(
            f"Arrival at {first.name}: {first.population} survivors after {losses} lost en route over "
            f"{engine.config.travel_years} {engine.config.tick_unit}s."
        )
        if roles:
            role_summary = ", ".join(f"{k}: {v}" for k, v in roles.items())
            lines.append(f"  Composition: {role_summary}")
    notes = first.metadata.get("notes") if first.metadata else None
    if notes:
        lines.append(f"  Notes: {notes}")
    return lines
