"""
app_timeline.simulation.state

State dataclasses for tracking simulation state.

PR-003b: Defines PopulationState and SimulationState for managing
demographic data during simulation runs.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Optional

from .formulas import calculate_carrying_capacity, calculate_multi_species_growth


@dataclass
class PopulationState:
    """
    Multi-species population state at a point in time.

    Tracks total population and breakdowns by species and habitat.
    Provides methods for applying growth and shocks.
    """

    total: int
    """Total population across all species"""

    by_species: Dict[str, int]
    """Population breakdown by species (e.g., {"huum": 10000, "sint": 2000})"""

    by_habitat: Dict[str, int]
    """Population breakdown by habitat (e.g., {"on_ground": 11000, "under_ground": 1000})"""

    def apply_growth(self, growth_rates: Dict[str, float], K: int) -> PopulationState:
        """
        Apply logistic growth to all species and return new state.

        :param growth_rates: Growth rates per species
        :param K: Carrying capacity
        :return: New PopulationState after growth
        """
        new_by_species = calculate_multi_species_growth(
            populations=self.by_species,
            growth_rates=growth_rates,
            K=K,
            time_step=1.0
        )

        new_total = sum(new_by_species.values())

        # Scale habitat breakdown proportionally
        if self.total > 0:
            scale_factor = new_total / self.total
            new_by_habitat = {
                habitat: int(pop * scale_factor)
                for habitat, pop in self.by_habitat.items()
            }
        else:
            new_by_habitat = self.by_habitat.copy()

        return PopulationState(
            total=new_total,
            by_species=new_by_species,
            by_habitat=new_by_habitat
        )

    def apply_shock(self, shock_multiplier: float) -> PopulationState:
        """
        Apply population shock (famine, war, disaster) and return new state.

        Shock is applied proportionally to all species and habitats.

        :param shock_multiplier: Multiplier (0.0-1.0, e.g., 0.75 = 25% loss)
        :return: New PopulationState after shock
        """
        new_total = int(self.total * shock_multiplier)

        new_by_species = {
            species: int(pop * shock_multiplier)
            for species, pop in self.by_species.items()
        }

        new_by_habitat = {
            habitat: int(pop * shock_multiplier)
            for habitat, pop in self.by_habitat.items()
        }

        return PopulationState(
            total=new_total,
            by_species=new_by_species,
            by_habitat=new_by_habitat
        )

    def copy(self) -> PopulationState:
        """Create a deep copy of this population state."""
        return PopulationState(
            total=self.total,
            by_species=self.by_species.copy(),
            by_habitat=self.by_habitat.copy()
        )


@dataclass
class SimulationState:
    """
    Complete simulation state for a region or province.

    Tracks entity information, population state, carrying capacity factors,
    and provides the random number generator for deterministic simulation.
    """

    # === Entity Information ===

    entity_type: str
    """Entity type: "region" or "province" """

    entity_id: int
    """Database ID of the entity being simulated"""

    entity_name: str
    """Name of the entity (for logging/reporting)"""

    # === Temporal State ===

    current_day: int
    """Current astro_day in the simulation"""

    # === Population State ===

    population: PopulationState
    """Current population state (total and breakdowns)"""

    # === Carrying Capacity Components ===

    K_base: int
    """Base carrying capacity"""

    environmental_factor: float
    """Environmental factor (climate, terrain) - modifiable by events"""

    infrastructure_factor: float
    """Infrastructure factor (irrigation, tech) - modifiable by events"""

    location_factor: float
    """Location factor (trade, resources) - relatively stable"""

    # === Random Number Generator ===

    rng: random.Random
    """Dedicated RNG for deterministic simulation"""

    @property
    def carrying_capacity(self) -> int:
        """Calculate current effective carrying capacity from components."""
        return calculate_carrying_capacity(
            K_base=self.K_base,
            environmental_factor=self.environmental_factor,
            infrastructure_factor=self.infrastructure_factor,
            location_factor=self.location_factor
        )

    def to_dict(self) -> Dict:
        """
        Convert state to dictionary (for reporting/logging).

        Note: Does not include RNG (not serializable).
        """
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "current_day": self.current_day,
            "population": {
                "total": self.population.total,
                "by_species": self.population.by_species,
                "by_habitat": self.population.by_habitat,
            },
            "carrying_capacity": {
                "total": self.carrying_capacity,
                "K_base": self.K_base,
                "environmental_factor": self.environmental_factor,
                "infrastructure_factor": self.infrastructure_factor,
                "location_factor": self.location_factor,
            }
        }
