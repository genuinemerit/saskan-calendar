# ADR 002: Time-Series Snapshot Architecture for Entity State

**Status:** Proposed

**Date:** 2024-12-27

## Context

The simulation must track how entities (cities, populations, infrastructure) change over 2000+ years. Two primary approaches exist:

1. **Current-state only:** Store only the present state; calculate history on-the-fly
2. **Time-series snapshots:** Store state at regular intervals (yearly, decadal)

Requirements:
- Must support temporal queries ("What was Beshquahoek's population in 1200 AA?")
- Must enable rollback/branching ("Replay from year 1000 with different parameters")
- Must persist simulation results for inspection, visualization, narrative generation
- Must handle entities that exist in some years but not others (cities founded/destroyed)

## Decision

**We will use a time-series snapshot architecture**, storing entity state at yearly intervals in dedicated snapshot tables.

**Schema pattern:**
```sql
-- Entity definition (timeless attributes)
CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    founded_year INTEGER NOT NULL,
    region_id INTEGER,
    destroyed_year INTEGER  -- NULL if still exists
);

-- Time-variant state (one row per entity per year)
CREATE TABLE city_snapshots (
    city_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    population_total INTEGER,
    population_human INTEGER,
    population_rabbit INTEGER,
    population_terpin INTEGER,
    area_km2 REAL,
    infrastructure_level REAL,
    political_control TEXT,
    PRIMARY KEY (city_id, year),
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

CREATE INDEX idx_snapshot_year ON city_snapshots(year);
CREATE INDEX idx_snapshot_city_year ON city_snapshots(city_id, year);
```

**Snapshot frequency:** 
- Yearly resolution for primary simulation (0-2450 AA)
- Can aggregate to decadal for long-term visualization
- Can store sub-yearly for dramatic events if needed (war years, etc.)

## Consequences

### Positive

- **Direct temporal queries:** No recalculation needed
  ```sql
  SELECT * FROM city_snapshots 
  WHERE year = 1200 AND city_id IN (SELECT id FROM cities WHERE region_id = 'kahila');
  ```

- **Perfect reproducibility:** Simulation runs are permanently stored; can compare runs

- **Easy visualization:** Export to CSV, plot with matplotlib/pandas
  ```python
  df = pd.read_sql(
      "SELECT year, population_total FROM city_snapshots WHERE city_id = ?",
      conn, params=[beshquahoek_id]
  )
  df.plot(x='year', y='population_total')
  ```

- **Branching timelines:** Copy snapshots up to branch point, continue in new database
  ```sql
  -- Create alternative history database
  INSERT INTO alt_timeline.city_snapshots 
  SELECT * FROM main.city_snapshots WHERE year <= 1500;
  ```

- **Data validation:** Can easily spot anomalies (population spikes, negative values)

- **Narrative generation:** AI can generate descriptions from actual historical data
  ```python
  growth = snapshot_1250.population - snapshot_1200.population
  prompt = f"Beshquahoek grew by {growth} people (1200-1250 AA). Describe why."
  ```

### Negative

- **Storage overhead:** ~2000 rows per city (2000 years × 1 row/year)
  - For 100 cities = 200k rows (negligible for SQLite)
  - For 1000 cities = 2M rows (still manageable)

- **Write amplification:** Each simulation year writes N city snapshots
  - Mitigated by: batch inserts, transactions

- **Schema rigidity:** Adding new tracked attributes requires ALTER TABLE
  - Mitigated by: JSON column for flexible metadata if needed

- **Temporal gaps:** If simulation skips years, must handle missing data
  - Mitigated by: forward-fill logic or explicit NULL handling

### Neutral

- **Denormalization:** Species populations could be separate table (`species_snapshots`)
  - Current approach: store in columns for simplicity
  - Future: normalize if species list becomes dynamic

## Implementation Notes

**Efficient bulk inserts during simulation:**
```python
def save_snapshots(self, year):
    snapshots = [
        (city.id, year, city.population_total, city.population_human, ...)
        for city in self.cities.values()
    ]
    self.db.executemany(
        "INSERT INTO city_snapshots VALUES (?, ?, ?, ?, ...)",
        snapshots
    )
    self.db.commit()
```

**Query patterns:**
```sql
-- Latest state for all cities
SELECT c.name, s.* 
FROM cities c
JOIN city_snapshots s ON c.id = s.city_id
WHERE s.year = (SELECT MAX(year) FROM city_snapshots WHERE city_id = c.id);

-- Population change over period
SELECT 
    city_id,
    MAX(population_total) - MIN(population_total) as growth
FROM city_snapshots
WHERE year BETWEEN 1000 AND 1500
GROUP BY city_id;

-- Cities that existed in year X
SELECT c.* FROM cities c
WHERE c.founded_year <= 1200 
  AND (c.destroyed_year IS NULL OR c.destroyed_year > 1200);
```

**Sparse snapshots (optimization if needed):**
- Only store snapshots when state changes significantly
- Interpolate for queries (more complex, defer until proven necessary)

## Alternatives Considered

**Event sourcing (store deltas, reconstruct state):**
- Pro: Minimal storage, perfect audit trail
- Con: Queries require reconstruction (slow), complex implementation
- **Rejected:** Premature optimization; snapshot storage is cheap

**Current-state only + calculation cache:**
- Pro: Less storage
- Con: Invalidation complexity, reproducibility issues, loses historical fidelity
- **Rejected:** Defeats purpose of "living timeline"

**Temporal database (e.g., PostgreSQL with temporal tables):**
- Pro: Built-in temporal query support
- Con: Requires PostgreSQL (see ADR-001), overkill for needs
- **Rejected:** Complexity exceeds benefits

## References

- Temporal Data in SQL: https://www.oreilly.com/library/view/sql-the-ultimate/9781449390099/ch18.html
- Time-series optimization: https://docs.timescale.com/timescaledb/latest/how-to-guides/schema-management/
