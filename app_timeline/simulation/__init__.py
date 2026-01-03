"""
app_timeline.simulation

Macro-scale demographic simulation engine.

PR-003b: Provides population dynamics simulation for regions and provinces,
with logistic growth, carrying capacity, multi-species tracking, and event integration.

Public API:
- SimulationConfig: Configuration dataclass
- SimulationEngine: Main simulation engine
- Population dynamics formulas (for advanced use)
- Event effects application
"""

from __future__ import annotations

from .config import SimulationConfig, load_simulation_config_from_settings
from .effects import apply_event_effects
from .engine import SimulationEngine
from .formulas import (
    calculate_carrying_capacity,
    calculate_logistic_growth,
    calculate_multi_species_growth,
)
from .state import PopulationState, SimulationState

__all__ = [
    # Configuration
    "SimulationConfig",
    "load_simulation_config_from_settings",
    # Engine
    "SimulationEngine",
    # State
    "PopulationState",
    "SimulationState",
    # Effects
    "apply_event_effects",
    # Formulas
    "calculate_logistic_growth",
    "calculate_multi_species_growth",
    "calculate_carrying_capacity",
]
