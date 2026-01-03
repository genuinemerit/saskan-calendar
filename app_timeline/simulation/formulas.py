"""
app_timeline.simulation.formulas

Population dynamics formulas for macro-scale simulation.

PR-003b: Implements logistic growth, carrying capacity calculations,
and multi-species population dynamics.
"""

from __future__ import annotations

from typing import Dict


def calculate_logistic_growth(
    N: int,
    r: float,
    K: int,
    time_step: float = 1.0
) -> int:
    """
    Calculate population growth using discrete logistic equation.

    Formula: N(t+1) = N(t) + r × N(t) × (1 - N(t)/K) × Δt

    The logistic growth model accounts for:
    - Exponential growth at low densities (N << K)
    - Slowdown as population approaches carrying capacity
    - Stability at carrying capacity (N = K)

    :param N: Current population
    :param r: Intrinsic growth rate (per time unit)
    :param K: Carrying capacity
    :param time_step: Time step size in time units (default: 1.0)
    :return: New population (clamped to [0, K])
    """
    if K <= 0:
        return 0

    if N <= 0:
        return 0

    # Calculate change in population
    dN = r * N * (1 - N / K) * time_step

    # Apply change
    new_N = N + dN

    # Clamp to reasonable bounds [0, K]
    return max(0, min(int(new_N), K))


def calculate_multi_species_growth(
    populations: Dict[str, int],
    growth_rates: Dict[str, float],
    K: int,
    time_step: float = 1.0
) -> Dict[str, int]:
    """
    Calculate independent logistic growth for multiple species sharing carrying capacity.

    Each species grows according to its own growth rate but all species
    compete for shared carrying capacity K. This is a simplified model where:
    - Each species applies logistic growth independently
    - If total population exceeds K, all species are scaled down proportionally

    :param populations: Current populations per species (e.g., {"huum": 10000, "sint": 5000})
    :param growth_rates: Growth rates per species (e.g., {"huum": 0.004, "sint": 0.006})
    :param K: Shared carrying capacity across all species
    :param time_step: Time step size in time units (default: 1.0)
    :return: New populations per species
    """
    if K <= 0:
        return {species: 0 for species in populations.keys()}

    total_N = sum(populations.values())

    if total_N == 0:
        return populations.copy()

    # Apply growth to each species independently
    new_populations = {}
    for species, N in populations.items():
        r = growth_rates.get(species, 0.0)  # Default to 0 if rate not specified

        if r == 0.0 or N == 0:
            new_populations[species] = N
            continue

        # Apply logistic growth for this species
        new_N = calculate_logistic_growth(N, r, K, time_step)
        new_populations[species] = new_N

    # Check if total exceeds carrying capacity
    new_total = sum(new_populations.values())

    if new_total > K:
        # Scale down all species proportionally to fit within K
        scale_factor = K / new_total
        new_populations = {
            species: int(N * scale_factor)
            for species, N in new_populations.items()
        }

    return new_populations


def calculate_carrying_capacity(
    K_base: int,
    environmental_factor: float,
    infrastructure_factor: float,
    location_factor: float
) -> int:
    """
    Calculate effective carrying capacity from component factors.

    Formula: K_t = K_base × C_t × I_t × L_t

    Where:
    - K_base: Base carrying capacity (intrinsic to region/province)
    - C_t: Environmental factor (climate, terrain quality)
    - I_t: Infrastructure factor (irrigation, technology, improvements)
    - L_t: Location factor (trade routes, resource access)

    :param K_base: Base carrying capacity
    :param environmental_factor: Environmental quality multiplier (typically 0.8-1.2)
    :param infrastructure_factor: Infrastructure quality multiplier (typically 1.0+)
    :param location_factor: Location advantage multiplier (typically 0.9-1.1)
    :return: Effective carrying capacity
    """
    K_t = K_base * environmental_factor * infrastructure_factor * location_factor
    return int(K_t)
