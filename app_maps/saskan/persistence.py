from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Optional

from .models import Event, SimulationState
from .settings import SimulationConfig


def snapshot_state(
    state: SimulationState,
    events: Iterable[Event],
    config: SimulationConfig,
    snapshot_dir: Path,
    scenario: Optional[str] = None,
) -> Path:
    """Persist a snapshot of the state/events for a given step."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "step": state.step,
            "tick_unit": state.tick_unit,
            "tick_length": state.tick_length,
            "scenario": scenario or config.scenario,
            "seed": config.seed,
        },
        "config": asdict(config),
        "state": asdict(state),
        "events": [asdict(event) for event in events],
    }
    path = snapshot_dir / f"step_{state.step:04d}.json"
    path.write_text(json.dumps(payload, indent=2))
    return path

