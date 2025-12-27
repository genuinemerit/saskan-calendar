# ADR 003: Python Simulation Engine with Modular Architecture

**Status:** Proposed

**Date:** 2024-12-27

## Context

The demographic and geographic simulation requires:
- Complex mathematical operations (logistic growth, network flows, stochastic shocks)
- Iterative year-by-year calculations over 2000+ years
- Integration with SQLite database (read configs, write snapshots)
- Testability and debuggability (verify formulas, inspect intermediate states)
- Extensibility (add new features: technology, species, events)

Language candidates: Python (familiar, ecosystem), Rust (performance), JavaScript (web integration).

Developer profile: 40 years SQL/functional programming, Python enthusiast, VS Code workflow.

## Decision

**We will implement the simulation engine in Python 3.10+** with a modular, functional-friendly architecture.

**Core principles:**
1. **Pure functions where possible:** Calculations separate from I/O
2. **Class-based entities:** Cities, Regions, Events as objects (mutable state acceptable for simulation)
3. **Module separation:** Clear boundaries between concerns
4. **Type hints:** Use `typing` for self-documenting code
5. **Testability:** Each module independently testable with pytest

**Module structure:**
```
saskantinon_sim/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── city.py          # City entity, snapshot methods
│   ├── region.py        # Region config, carrying capacity
│   ├── network.py       # Road network (networkx wrapper)
│   └── species.py       # Species-specific growth parameters
├── simulation/
│   ├── __init__.py
│   ├── population.py    # Logistic growth formulas
│   ├── migration.py     # Network flow calculations
│   ├── economy.py       # Urban/rural allocation, rank-size
│   ├── events.py        # Event triggering, effects
│   └── engine.py        # Main simulation loop
├── persistence/
│   ├── __init__.py
│   ├── database.py      # SQLite operations (read/write)
│   └── config.py        # JSON config loading
├── analysis/
│   ├── __init__.py
│   ├── queries.py       # Common SQL queries
│   └── visualization.py # Plotting helpers
└── cli/
    ├── __init__.py
    └── main.py          # Command-line interface
```

**Technology stack:**
- **Core:** Python 3.10+ (match expressions, better type hints)
- **Database:** `sqlite3` (stdlib) or `sqlalchemy` (if ORM benefits emerge)
- **Data:** `pandas` (DataFrames for analysis), `numpy` (array ops)
- **Network:** `networkx` (Ring Road graph, shortest paths)
- **Viz:** `matplotlib` (static plots), `plotly` (interactive, optional)
- **Testing:** `pytest`, `hypothesis` (property-based testing for formulas)
- **Types:** `mypy` for static type checking (optional but recommended)

**No Rust** unless profiling reveals bottlenecks (unlikely for 2000-iteration sim).

## Consequences

### Positive

- **Familiarity:** Leverage 40 years of development discipline in comfortable language

- **Rapid prototyping:** Test formulas in Jupyter, migrate to modules when stable

- **Rich ecosystem:** 
  - `scipy` for advanced math (if logistic growth needs refinement)
  - `networkx` for graph algorithms (betweenness centrality, shortest paths)
  - `pandas` for data wrangling (groupby, pivot, merge)

- **Readability:** Python's clarity makes formulas transparent
  ```python
  def logistic_growth(N_t: float, r: float, K_t: float) -> float:
      """One year of population growth."""
      return N_t + r * N_t * (1 - N_t / K_t)
  ```

- **Testability:** Pure functions easy to test
  ```python
  def test_logistic_growth_equilibrium():
      # At K, growth should be zero
      assert logistic_growth(N_t=1000, r=0.01, K_t=1000) == 1000
  ```

- **VS Code integration:** First-class Python support, debugging, IntelliSense

- **Cross-platform:** Works on Windows, macOS, Linux without changes

### Negative

- **Performance:** Python slower than Rust/C++ (mitigated by: Numba JIT if needed, simulations are offline batch jobs)

- **Dependency management:** Virtual environments required (mitigated by: `poetry` or `pipenv`)

- **Type safety:** Optional types, runtime errors possible (mitigated by: `mypy`, comprehensive tests)

- **Packaging:** Distribution more complex than compiled binary (not a concern for personal project)

### Neutral

- **Functional style:** Python supports functional patterns (map, filter, reduce) but not enforced
  - Decision: Use where natural (pure calculations), classes where stateful (simulation entities)

- **Concurrency:** GIL limits parallelism (not needed for single-timeline simulation; can use multiprocessing for scenario testing)

## Implementation Notes

**Example: Population module (functional core)**
```python
# saskantinon_sim/simulation/population.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class GrowthParams:
    r: float          # intrinsic growth rate
    K_base: float     # base carrying capacity
    C_t: float = 1.0  # climate multiplier
    I_t: float = 1.0  # irrigation multiplier
    L_t: float = 1.0  # labor/organization multiplier

def carrying_capacity(params: GrowthParams) -> float:
    """Calculate effective carrying capacity for this year."""
    return params.K_base * params.C_t * params.I_t * params.L_t

def apply_growth(N_t: float, params: GrowthParams) -> float:
    """Apply logistic growth for one year."""
    K_t = carrying_capacity(params)
    return N_t + params.r * N_t * (1 - N_t / K_t)

def apply_shock(N_t: float, shock: float) -> float:
    """Apply population shock (famine, war, etc.)."""
    return max(0, N_t * shock)

# Composition
def step_population(
    N_t: float, 
    params: GrowthParams, 
    shock: float = 1.0
) -> float:
    """Full population step: growth then shock."""
    N_after_growth = apply_growth(N_t, params)
    return apply_shock(N_after_growth, shock)
```

**Example: City class (stateful shell)**
```python
# saskantinon_sim/models/city.py
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class City:
    id: int
    name: str
    founded_year: int
    region_id: int
    K_base: float
    
    # Mutable state
    population: Dict[int, float] = field(default_factory=dict)
    infrastructure: Dict[int, float] = field(default_factory=dict)
    
    def step_year(self, year: int, params: GrowthParams, shock: float):
        """Run one year of simulation for this city."""
        N_prev = self.population.get(year - 1, 0)
        N_new = step_population(N_prev, params, shock)
        self.population[year] = N_new
    
    def get_snapshot(self, year: int) -> Dict:
        """Export state for database persistence."""
        return {
            'city_id': self.id,
            'year': year,
            'population_total': self.population.get(year, 0),
            'infrastructure_level': self.infrastructure.get(year, 0),
        }
```

**Example: Simulation engine (orchestration)**
```python
# saskantinon_sim/simulation/engine.py
from typing import List, Dict
from saskantinon_sim.models.city import City
from saskantinon_sim.persistence.database import Database

class Simulation:
    def __init__(self, db: Database, config: Dict):
        self.db = db
        self.config = config
        self.cities: Dict[int, City] = {}
        self.current_year = 0
    
    def run(self, start_year: int, end_year: int):
        """Run simulation from start to end year."""
        for year in range(start_year, end_year + 1):
            self.current_year = year
            self.apply_events(year)
            self.step_all_cities(year)
            self.calculate_migrations(year)
            self.save_snapshots(year)
            
            if year % 100 == 0:  # Progress indicator
                print(f"Completed year {year}")
    
    def step_all_cities(self, year: int):
        """Update all cities for this year."""
        for city in self.cities.values():
            params = self._get_growth_params(city, year)
            shock = self._get_shock(city, year)
            city.step_year(year, params, shock)
```

**Testing strategy:**
```python
# tests/test_population.py
import pytest
from saskantinon_sim.simulation.population import *

def test_carrying_capacity():
    params = GrowthParams(r=0.01, K_base=1000, C_t=1.2, I_t=1.1, L_t=1.0)
    assert carrying_capacity(params) == 1000 * 1.2 * 1.1 * 1.0

def test_growth_below_capacity():
    N = apply_growth(500, GrowthParams(r=0.01, K_base=1000))
    assert N > 500  # Should grow

def test_growth_above_capacity():
    N = apply_growth(1100, GrowthParams(r=0.01, K_base=1000))
    assert N < 1100  # Should decline

@pytest.mark.parametrize("shock,expected_survival", [
    (1.0, 1.0),    # No shock
    (0.8, 0.8),    # 20% loss
    (0.0, 0.0),    # Total collapse
])
def test_shock_application(shock, expected_survival):
    N_after = apply_shock(1000, shock)
    assert N_after == 1000 * expected_survival
```

## Alternatives Considered

**Rust:**
- Pro: Performance (10-100x faster), memory safety, concurrency
- Con: Steep learning curve, slower prototyping, overkill for offline simulation
- **Deferred:** Use Python first; profile; optimize hotspots with Rust/Numba only if needed

**Julia:**
- Pro: Scientific computing focus, REPL, multiple dispatch
- Con: Less mature ecosystem, smaller community, another language to learn
- **Rejected:** Benefits don't outweigh Python familiarity

**JavaScript/TypeScript:**
- Pro: Web integration (browser-based visualization)
- Con: Weaker numerical libraries, less natural for scientific computing
- **Rejected:** Keep simulation backend in Python; can export data to web frontend if desired

**Haskell/OCaml:**
- Pro: Functional purity, strong types, pattern matching
- Con: Significant learning investment, less accessible for future maintainers
- **Rejected:** Python functional features sufficient; prioritize pragmatism

## References

- Python Data Science Handbook: https://jakevdp.github.io/PythonDataScienceHandbook/
- NetworkX documentation: https://networkx.org/documentation/stable/
- Effective Python (Brett Slatkin): Best practices
- pytest documentation: https://docs.pytest.org/
