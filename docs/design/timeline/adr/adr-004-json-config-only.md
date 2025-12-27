# ADR 004: JSON for Configuration Only, Not Data Storage

**Status:** Proposed

**Date:** 2024-12-27

## Context

The project requires storing two distinct types of information:

1. **Configuration/Parameters:** Regional settings (arable land %), growth rates, event templates, simulation tuning
2. **State/Data:** City populations, historical snapshots, event occurrences, simulation results

Previous approach used JSON for both, which led to:
- Complex queries becoming unwieldy (filtering, joining across nested structures)
- Relationship management requiring custom logic
- Schema evolution causing breaking changes across files
- Version control diffs becoming noisy and hard to review

The question: What role should JSON play in the new architecture?

## Decision

**JSON will be used exclusively for configuration and parameters**, NOT as a data store.

**Configuration scope:**
- Regional definitions (geography, climate, arable land)
- Species growth parameters (r, shock sensitivity)
- Event templates (famine profiles, war effects)
- Simulation settings (shock frequency, migration coefficients)
- Technology progression (irrigation multipliers by era)

**NOT for JSON:**
- City current state (population, infrastructure)
- Historical snapshots (time-series data)
- Event occurrences (actual historical events)
- Simulation results (output data)

These belong in SQLite (see ADR-001, ADR-002).

**File organization:**
```
configs/
├── regions.json          # Geographic/environmental definitions
├── species.json          # Species-specific growth parameters
├── events.json           # Event templates and probabilities
├── technology.json       # Tech progression timelines
└── simulation.json       # Simulation engine settings
```

**Versioning strategy:**
```
configs/
├── v1_baseline/
│   ├── regions.json
│   ├── species.json
│   └── ...
├── v2_high_fertility/   # Alternative scenario
│   ├── regions.json     # Same as v1
│   ├── species.json     # Modified r values
│   └── ...
└── current -> v1_baseline/  # Symlink to active config
```

## Consequences

### Positive

- **Clean separation:** Config (immutable, versioned) vs. State (mutable, simulated)

- **Human-readable tuning:** Adjust parameters in text editor without touching code or database
  ```json
  {
    "species": {
      "rabbit_sint": {
        "r_normal": 0.015,
        "shock_sensitivity": {
          "bad_harvest": 0.90,
          "famine": 0.75
        }
      }
    }
  }
  ```

- **Version control friendly:** Text files diff cleanly in Git
  ```diff
  - "r_normal": 0.010,
  + "r_normal": 0.015,
  ```

- **Scenario testing:** Swap configs to test "what-if" without changing code
  ```bash
  python simulate.py --config configs/v2_high_fertility/
  ```

- **Documentation as code:** Comments in JSON explain modeling choices
  ```json
  {
    "regions": {
      "ingar": {
        "arable_fraction": 0.25,  // Based on medieval England analogy
        "base_productivity": 120  // people/km² (rain-fed cereals)
      }
    }
  }
  ```

- **Type safety (with validation):** Use `pydantic` or `jsonschema` to validate on load
  ```python
  from pydantic import BaseModel
  
  class RegionConfig(BaseModel):
      arable_fraction: float  # 0.0-1.0
      base_productivity: int  # people per km²
      
  config = RegionConfig(**json.load(f))  # Validates types
  ```

### Negative

- **Duplication risk:** Must resist temptation to store state in JSON
  - Mitigated by: Clear file naming (`config/`, not `data/`), code review

- **Schema evolution:** Changing config structure requires updating loader code
  - Mitigated by: Versioned configs, explicit migration scripts if needed

- **No relational integrity:** Can't enforce foreign keys between JSON files
  - Mitigated by: Validation logic in loader, comprehensive tests

- **No query power:** Can't easily ask "which regions have arable_fraction > 0.2?"
  - Mitigated by: Configs are small enough to load entirely into memory

### Neutral

- **Formats:** Could use YAML or TOML instead of JSON
  - YAML: More human-friendly (comments, multi-line), but whitespace-sensitive
  - TOML: Good for flat configs, less good for nested structures
  - **Decision:** Stick with JSON (stdlib support, tooling, familiarity)

## Implementation Notes

**Example: Region configuration**
```json
// configs/regions.json
{
  "regions": {
    "ingar": {
      "name": "Ingar Heartland",
      "area_km2": 40000,
      "arable_fraction": 0.25,
      "base_productivity": 120,
      "climate": {
        "baseline": 1.0,
        "oscillation_period": 11,    // years
        "oscillation_amplitude": 0.15,
        "drought_threshold": 0.85
      },
      "irrigation": [
        {"year": 0, "multiplier": 1.0},
        {"year": 1000, "multiplier": 1.2},
        {"year": 2200, "multiplier": 1.35}
      ]
    },
    "kahila": {
      "name": "Kahila Forests",
      "area_km2": 35000,
      "arable_fraction": 0.15,      // Forested, less arable
      "base_productivity": 80,      // Lower than Ingar
      "climate": {
        "baseline": 1.05,            // Slightly better rainfall
        "oscillation_period": 13,
        "oscillation_amplitude": 0.10,
        "drought_threshold": 0.90
      },
      "irrigation": [
        {"year": 0, "multiplier": 1.0},
        {"year": 1500, "multiplier": 1.1}  // Late adopters
      ]
    }
  }
}
```

**Example: Species configuration**
```json
// configs/species.json
{
  "species": {
    "human_rider": {
      "r_baseline": 0.004,  // 0.4% per year
      "shock_multipliers": {
        "no_shock": 1.0,
        "bad_harvest": 0.95,
        "famine": 0.80,
        "war": 0.75,
        "plague": 0.60
      },
      "recovery_boost": 0.003,  // Added to r for 2 years post-shock
      "migration_propensity": 0.05
    },
    "rabbit_sint": {
      "r_baseline": 0.012,  // Higher fertility
      "shock_multipliers": {
        "no_shock": 1.0,
        "bad_harvest": 0.90,
        "famine": 0.75,
        "war": 0.70,
        "plague": 0.50
      },
      "recovery_boost": 0.005,  // Faster recovery
      "migration_propensity": 0.08,
      "notes": "High fertility offsets higher shock sensitivity"
    },
    "terpin": {
      "r_baseline": 0.0005,  // Very slow
      "shock_multipliers": {
        "no_shock": 1.0,
        "bad_harvest": 0.98,
        "famine": 0.95,
        "war": 0.92,         // Resilient, but can be killed
        "plague": 0.99       // Long-lived, disease-resistant
      },
      "recovery_boost": 0.0001,
      "migration_propensity": 0.01,  // Low mobility
      "lifespan_years": 300
    }
  }
}
```

**Loading with validation:**
```python
# saskantinon_sim/persistence/config.py
import json
from pathlib import Path
from typing import Dict
from pydantic import BaseModel, Field, validator

class ClimateConfig(BaseModel):
    baseline: float = Field(ge=0.5, le=1.5)
    oscillation_period: int = Field(ge=5, le=50)
    oscillation_amplitude: float = Field(ge=0.0, le=0.5)
    drought_threshold: float = Field(ge=0.5, le=1.0)

class RegionConfig(BaseModel):
    name: str
    area_km2: int = Field(gt=0)
    arable_fraction: float = Field(ge=0.0, le=1.0)
    base_productivity: int = Field(ge=50, le=300)
    climate: ClimateConfig
    irrigation: list[Dict]  # Could further validate
    
    @validator('irrigation')
    def validate_irrigation_timeline(cls, v):
        years = [item['year'] for item in v]
        if years != sorted(years):
            raise ValueError("Irrigation timeline must be sorted by year")
        return v

class ConfigLoader:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
    
    def load_regions(self) -> Dict[str, RegionConfig]:
        path = self.config_dir / 'regions.json'
        with open(path) as f:
            data = json.load(f)
        return {
            region_id: RegionConfig(**region_data)
            for region_id, region_data in data['regions'].items()
        }
    
    def load_species(self) -> Dict:
        path = self.config_dir / 'species.json'
        with open(path) as f:
            return json.load(f)['species']

# Usage
loader = ConfigLoader(Path('configs/v1_baseline/'))
regions = loader.load_regions()  # Validated on load
species = loader.load_species()
```

**Scenario comparison:**
```python
def compare_scenarios(scenario_a: Path, scenario_b: Path):
    """Show diff between two config scenarios."""
    loader_a = ConfigLoader(scenario_a)
    loader_b = ConfigLoader(scenario_b)
    
    species_a = loader_a.load_species()
    species_b = loader_b.load_species()
    
    for species_id in species_a:
        r_a = species_a[species_id]['r_baseline']
        r_b = species_b[species_id]['r_baseline']
        if r_a != r_b:
            print(f"{species_id}: r changed from {r_a} to {r_b}")
```

## Alternatives Considered

**YAML:**
- Pro: Comments, multi-line strings, more human-friendly
- Con: Whitespace-sensitive (indentation errors), requires `PyYAML` dependency
- **Deferred:** JSON sufficient for now; can migrate if configs become unwieldy

**TOML:**
- Pro: Clean syntax, good for flat configs
- Con: Less good for deeply nested structures (our configs are hierarchical)
- **Rejected:** JSON handles nesting better

**Python files (e.g., `config.py`):**
- Pro: Full language power, can compute values
- Con: Harder to validate, security risk (arbitrary code execution), less portable
- **Rejected:** Configs should be declarative data, not code

**Environment variables:**
- Pro: 12-factor app pattern, easy overrides
- Con: Awkward for complex nested configs, not self-documenting
- **Rejected:** Use for deployment settings (DB path, etc.), not worldbuilding params

**Database tables for config:**
- Pro: Queryable, can version in same DB
- Con: Harder to edit (need DB client), less obvious what's config vs. state
- **Rejected:** Keep clear separation; configs in files, state in DB

## Migration Path

If currently using JSON as database:

1. **Audit existing JSON files:** Separate config from state
2. **Create new JSON structure:** Move parameters to `configs/`
3. **Design SQL schema:** Move state data to SQLite
4. **Write migration script:**
   ```python
   # migrate_json_to_sql.py
   import json
   import sqlite3
   
   # Load old JSON "database"
   with open('old_data.json') as f:
       old_data = json.load(f)
   
   # Extract config
   config = {
       'regions': {id: r['config'] for id, r in old_data['regions'].items()}
   }
   with open('configs/regions.json', 'w') as f:
       json.dump(config, f, indent=2)
   
   # Extract state -> SQL
   conn = sqlite3.connect('saskantinon.db')
   for city_id, city_data in old_data['cities'].items():
       conn.execute(
           "INSERT INTO cities VALUES (?, ?, ?)",
           (city_id, city_data['name'], city_data['founded_year'])
       )
       for year, snapshot in city_data['history'].items():
           conn.execute(
               "INSERT INTO city_snapshots VALUES (?, ?, ?)",
               (city_id, int(year), snapshot['population'])
           )
   conn.commit()
   ```

5. **Update loaders:** Point to new locations
6. **Validate:** Ensure simulation runs with new architecture
7. **Archive old JSON:** Keep for reference, but don't use

## References

- JSON Schema: https://json-schema.org/
- Pydantic documentation: https://docs.pydantic.dev/
- Configuration management best practices: https://12factor.net/config
