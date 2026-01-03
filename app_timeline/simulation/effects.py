"""
app_timeline.simulation.effects

Event effect application for simulation.

PR-003b: Implements ADR-007 hybrid manual-algorithmic workflow.
Humans author events with effect parameters in meta_data["effects"],
and this module applies those effects to simulation state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.event import Event
    from .state import SimulationState


def apply_event_effects(state: SimulationState, event: Event) -> SimulationState:
    """
    Apply event effects to simulation state.

    Reads effect parameters from event.meta_data["effects"] and modifies
    the simulation state accordingly. This implements ADR-007: humans
    define events and their effects, the algorithm applies them.

    Supported effect parameters:
    - shock_multiplier (float): Population shock, 0.0-1.0
      Example: 0.75 = 25% population loss from famine/war/disaster
    - infrastructure_damage (float): Reduce infrastructure factor, 0.0-1.0
      Example: 0.90 = 10% infrastructure damage from war
    - environmental_change (float): Modify environmental factor, ±0.5
      Example: -0.1 = environmental degradation, +0.1 = improvement
    - infrastructure_boost (float): Increase infrastructure factor
      Example: +0.2 = 20% improvement from irrigation project

    :param state: Current simulation state
    :param event: Event with effects in meta_data["effects"]
    :return: Modified simulation state
    """
    # Extract effects from event metadata
    effects = event.meta_data.get("effects", {}) if event.meta_data else {}

    if not effects:
        # No effects to apply
        return state

    # Apply population shock (famine, war, disaster)
    if "shock_multiplier" in effects:
        multiplier = float(effects["shock_multiplier"])
        # Clamp to reasonable range [0.0, 1.0]
        multiplier = max(0.0, min(1.0, multiplier))
        state.population = state.population.apply_shock(multiplier)

    # Apply infrastructure damage (war, natural disaster)
    if "infrastructure_damage" in effects:
        damage = float(effects["infrastructure_damage"])
        # Clamp to reasonable range [0.0, 1.0]
        damage = max(0.0, min(1.0, damage))
        state.infrastructure_factor *= damage
        # Keep above minimum threshold
        state.infrastructure_factor = max(0.1, state.infrastructure_factor)

    # Apply infrastructure boost (irrigation, technology)
    if "infrastructure_boost" in effects:
        boost = float(effects["infrastructure_boost"])
        # Clamp boost to reasonable range [-0.5, +1.0]
        boost = max(-0.5, min(1.0, boost))
        state.infrastructure_factor += boost
        # Keep within reasonable bounds [0.1, 3.0]
        state.infrastructure_factor = max(0.1, min(3.0, state.infrastructure_factor))

    # Apply environmental change (climate shift, ecological recovery/damage)
    if "environmental_change" in effects:
        change = float(effects["environmental_change"])
        # Clamp to reasonable range [-0.5, +0.5]
        change = max(-0.5, min(0.5, change))
        state.environmental_factor += change
        # Keep within reasonable bounds [0.1, 2.0]
        state.environmental_factor = max(0.1, min(2.0, state.environmental_factor))

    return state
