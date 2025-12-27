from __future__ import annotations

from typing import Iterable, List

from ..models import Event, SimulationState


def render_step(state: SimulationState, events: Iterable[Event]) -> List[str]:
    """Format a simulation step as human-readable text."""
    settlements = sorted(state.settlements, key=lambda s: s.population, reverse=True)
    total_population = sum(s.population for s in settlements)
    settlement_map = {s.name: s for s in settlements}
    lines: List[str] = []
    lines.append(
        f"Step {state.step} ({state.tick_unit}): population {total_population} across {len(settlements)} settlements."
    )
    top_settlements = settlements[:3]
    summary = ", ".join(f"{s.name} ({s.population})" for s in top_settlements)
    lines.append(f"  Top settlements: {summary}")
    lines.append(f"  Routes: {len(state.routes)}")

    hamlets = [s for s in settlements if (s.metadata or {}).get("type") == "hamlet"]
    market_candidates = [s for s in settlements if (s.metadata or {}).get("type") == "market-town"]
    if hamlets:
        lines.append("  Hamlets:")
        hamlets_sorted = sorted(hamlets, key=lambda s: s.population, reverse=True)
        for hamlet in hamlets_sorted:
            parent = (hamlet.metadata or {}).get("parent", "unknown")
            affinity = (hamlet.metadata or {}).get("affinity")
            affinity_str = f", affinity={affinity}" if affinity is not None else ""
            lines.append(f"    - {hamlet.name} ({hamlet.population}) parent={parent}{affinity_str}")

        cluster_pop = {}
        for hamlet in hamlets:
            parent = (hamlet.metadata or {}).get("parent", "unknown")
            cluster_pop.setdefault(parent, 0)
            cluster_pop[parent] += hamlet.population
        if cluster_pop:
            cluster_summary = ", ".join(f"{p}: {pop}" for p, pop in cluster_pop.items())
            lines.append(f"  Hamlet clusters (pop by parent): {cluster_summary}")

        # Parent rollups: core + hamlets
        rollups = []
        for parent, pop in cluster_pop.items():
            core = settlement_map.get(parent)
            rollups.append((parent, core.population if core else 0, pop))
        if rollups:
            rollup_summary = ", ".join(f"{p} core {core}+hamlets {h}={core+h}" for p, core, h in rollups)
            lines.append(f"  Parent rollups: {rollup_summary}")

    if market_candidates:
        lines.append("  Market-town candidates:")
        for mt in sorted(market_candidates, key=lambda s: s.population, reverse=True):
            parent = (mt.metadata or {}).get("parent", "unknown")
            lines.append(f"    - {mt.name} ({mt.population}) parent={parent}")

    event_list = list(events)
    if event_list:
        lines.append("  Events:")
        for event in event_list:
            lines.append(f"    - {event.message}")
    else:
        lines.append("  Events: none")
    return lines
