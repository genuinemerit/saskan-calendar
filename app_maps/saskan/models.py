from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

Coord = Tuple[int, int]


@dataclass
class Region:
    name: str
    width: int
    height: int
    description: str = ""


@dataclass
class Settlement:
    name: str
    population: int
    location: Coord
    growth_rate: float
    carrying_capacity: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Route:
    origin: str
    destination: str
    distance: float
    difficulty: float

    def key(self) -> Tuple[str, str]:
        """Normalized key for de-duplication."""
        ordered = tuple(sorted((self.origin, self.destination)))
        return (ordered[0], ordered[1])


@dataclass
class Event:
    step: int
    message: str


@dataclass
class SimulationState:
    step: int
    tick_unit: str
    tick_length: float
    region: Region
    settlements: List[Settlement]
    routes: List[Route]
