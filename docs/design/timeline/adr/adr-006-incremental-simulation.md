# ADR 006: Incremental, Resumable Simulation Architecture

**Status:** Proposed

**Date:** 2024-12-27

## Context

Simulating 2000+ years of demographic/geographic development involves:
- Thousands of iterative calculations (yearly or decadal steps)
- Complex interdependencies (cities affect each other via migration, trade)
- Stochastic elements (random shocks, climate variability)
- Potential for bugs, implausible results, or creative exploration

Two approaches exist:

1. **Monolithic simulation:** Run entire timeline (0-2450 AA) in one go
   - Pro: Simple script, single execution
   - Con: If error at year 1500, must re-run entire 1500 years
   - Con: Hard to inspect intermediate states
   - Con: Can't easily branch ("what if Kahila won in 1400?")

2. **Incremental simulation:** Run in chunks (e.g., 100-year segments), persist state
   - Pro: Can stop, inspect, adjust, resume
   - Con: More complex state management
   - Con: Requires careful snapshot/restore logic

Given:
- This is exploratory worldbuilding (not production simulation)
- Trial and error expected (tuning parameters, fixing bugs)
- Alternative timelines desirable (scenario testing)
- Human inspection valuable (catch implausible results early)

**Decision needed:** How to structure the simulation loop?

## Decision

**We will implement an incremental, resumable simulation architecture** with the following characteristics:

1. **Chunked execution:** Simulate in configurable segments (default: 100-year chunks)
2. **State persistence:** Save complete world state after each chunk to database
3. **Resume capability:** Can restart from any saved checkpoint
4. **Branch support:** Can fork timeline from any checkpoint
5. **Inspection hooks:** Built-in validation and reporting between chunks

**Architecture:**
```
Simulation Timeline:
[0 AA]--[100 AA]--[200 AA]--[300 AA]--...->[2450 AA]
   |         |         |         |              |
   ✓         ✓         ✓         ✓              ✓
   Checkpoint saved at each marker

Operations:
- simulate(start=0, end=2450, chunk_size=100)
- resume(from_year=1500, to_year=2450)
- branch(from_year=1200, name="kahila_victory")
- inspect(year=800)
```

**Database support:**
```sql
-- Track simulation runs
CREATE TABLE simulation_runs (
    run_id INTEGER PRIMARY KEY,
    config_version TEXT,
    start_year INTEGER,
    end_year INTEGER,
    current_year INTEGER,  -- Progress tracker
    status TEXT,           -- 'running', 'completed', 'paused'
    random_seed INTEGER,   -- For reproducibility
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Link snapshots to runs
ALTER TABLE city_snapshots 
ADD COLUMN run_id INTEGER REFERENCES simulation_runs(run_id);

-- Timeline branches
CREATE TABLE timeline_branches (
    branch_id INTEGER PRIMARY KEY,
    parent_run_id INTEGER REFERENCES simulation_runs(run_id),
    branch_year INTEGER,
    branch_name TEXT,
    description TEXT
);
```

## Consequences

### Positive

- **Fail-fast inspection:** Catch implausible results early (year 100, not year 2000)
  ```
  Run 0-100 AA → Inspect → Looks good
  Run 100-200 AA → Inspect → Ingar population went negative! → Fix bug
  Resume from 100 AA → Continue
  ```

- **Parameter tuning:** Adjust and re-run segments without full simulation
  ```
  Run 0-500 AA with r=0.004 → Too slow
  Reset to year 0, change r=0.006 → Re-run 0-500 AA → Better
  ```

- **Branching timelines:** Explore "what-if" scenarios
  ```
  Main timeline: 0-2450 AA (Fatunik dominates)
  Branch at 1400 AA: "Kahila Victory" → Different outcomes
  Branch at 2000 AA: "No Agency Contact" → Isolationist timeline
  ```

- **Incremental development:** Build complexity gradually
  ```
  Phase 1: Single city, basic growth (0-200 AA)
  Phase 2: Add migration (0-500 AA, re-use Phase 1 work)
  Phase 3: Add multi-species (0-1000 AA, re-use Phases 1-2)
  ```

- **Debugging aid:** Narrow down when/where bugs occur
  ```
  Bug: Beshquahoek population explodes to 1M in 1500 AA
  Bisect: Works in 1400 AA, broken in 1500 AA
  → Problem occurred 1400-1500 AA → Easier to debug
  ```

- **Progress transparency:** User sees simulation advancing, not black box
  ```
  Simulating 0-100 AA... ✓ (5 seconds)
  Simulating 100-200 AA... ✓ (5 seconds)
  Simulating 200-300 AA... ✓ (5 seconds)
  ...
  ```

### Negative

- **Complexity:** More code than monolithic approach
  - Mitigated by: Clean abstraction (`Simulation.run_chunk()`)

- **State management:** Must ensure complete snapshots
  - Mitigated by: Automated validation checks

- **Disk I/O:** More database writes (after each chunk)
  - Mitigated by: Chunks are infrequent (100 years), SQLite is fast

- **Determinism:** Random seeds must be managed across chunks
  - Mitigated by: Store seed in database, advance RNG state consistently

### Neutral

- **Chunk size:** 100 years is default, but configurable
  - Smaller chunks (10 years): More inspection points, slower
  - Larger chunks (500 years): Faster, less inspection
  - **Recommendation:** Start with 100 years, adjust as needed

## Implementation Notes

**Example: Simulation engine with chunking**
```python
# saskantinon_sim/simulation/engine.py
import sqlite3
import random
from dataclasses import dataclass
from typing import Optional

@dataclass
class SimulationConfig:
    chunk_size: int = 100
    random_seed: int = 42
    config_version: str = "v1_baseline"

class Simulation:
    def __init__(self, db_path: str, config: SimulationConfig):
        self.db = sqlite3.connect(db_path)
        self.config = config
        self.current_run_id: Optional[int] = None
        self.current_year = 0
        self.rng = random.Random(config.random_seed)
    
    def run(self, start_year: int, end_year: int):
        """Run simulation from start to end in chunks."""
        self.current_run_id = self._create_run(start_year, end_year)
        
        for chunk_start in range(start_year, end_year, self.config.chunk_size):
            chunk_end = min(chunk_start + self.config.chunk_size, end_year)
            
            print(f"\n{'='*60}")
            print(f"Simulating {chunk_start}-{chunk_end} AA...")
            print(f"{'='*60}")
            
            self._run_chunk(chunk_start, chunk_end)
            self._validate_chunk(chunk_end)
            self._report_chunk(chunk_end)
            
            self.current_year = chunk_end
            self._update_run_progress(chunk_end)
        
        self._mark_run_completed()
        print(f"\n✓ Simulation complete: {start_year}-{end_year} AA")
    
    def resume(self, from_year: int, to_year: int):
        """Resume simulation from a previous checkpoint."""
        self._load_state(from_year)
        self.run(from_year, to_year)
    
    def branch(self, from_year: int, branch_name: str) -> 'Simulation':
        """Create alternative timeline from checkpoint."""
        branch_db = f"saskantinon_{branch_name}.db"
        self._copy_state_to(from_year, branch_db)
        
        branch_sim = Simulation(branch_db, self.config)
        branch_sim._register_branch(self.current_run_id, from_year, branch_name)
        return branch_sim
    
    def _run_chunk(self, start: int, end: int):
        """Execute one chunk of simulation."""
        for year in range(start, end):
            self._apply_events(year)
            self._step_all_cities(year)
            self._calculate_migrations(year)
            self._save_snapshots(year)
    
    def _validate_chunk(self, year: int):
        """Check for implausible results."""
        issues = []
        
        # Check for negative populations
        negative_pops = self.db.execute("""
            SELECT city_id, population_total 
            FROM city_snapshots 
            WHERE year = ? AND population_total < 0
        """, (year,)).fetchall()
        
        if negative_pops:
            issues.append(f"Negative populations detected: {negative_pops}")
        
        # Check for populations exceeding capacity by >50%
        over_capacity = self.db.execute("""
            SELECT s.city_id, s.population_total, c.K_base 
            FROM city_snapshots s
            JOIN cities c ON s.city_id = c.id
            WHERE s.year = ? AND s.population_total > c.K_base * 1.5
        """, (year,)).fetchall()
        
        if over_capacity:
            issues.append(f"Cities over capacity: {over_capacity}")
        
        if issues:
            print("\n⚠️ VALIDATION WARNINGS:")
            for issue in issues:
                print(f"  {issue}")
            
            # Optional: Pause for user intervention
            if input("Continue anyway? (y/n): ").lower() != 'y':
                raise RuntimeError("Simulation paused due to validation issues")
    
    def _report_chunk(self, year: int):
        """Display chunk summary."""
        total_pop = self.db.execute("""
            SELECT SUM(population_total) FROM city_snapshots WHERE year = ?
        """, (year,)).fetchone()[0]
        
        num_cities = self.db.execute("""
            SELECT COUNT(DISTINCT city_id) FROM city_snapshots WHERE year = ?
        """, (year,)).fetchone()[0]
        
        print(f"Year {year} AA:")
        print(f"  Total population: {total_pop:,}")
        print(f"  Active cities: {num_cities}")
    
    def _create_run(self, start: int, end: int) -> int:
        """Register new simulation run."""
        cursor = self.db.execute("""
            INSERT INTO simulation_runs 
            (config_version, start_year, end_year, current_year, status, random_seed, created_at)
            VALUES (?, ?, ?, ?, 'running', ?, CURRENT_TIMESTAMP)
        """, (self.config.config_version, start, end, start, self.config.random_seed))
        self.db.commit()
        return cursor.lastrowid
    
    def _update_run_progress(self, year: int):
        """Update simulation run progress."""
        self.db.execute("""
            UPDATE simulation_runs 
            SET current_year = ?, updated_at = CURRENT_TIMESTAMP
            WHERE run_id = ?
        """, (year, self.current_run_id))
        self.db.commit()
    
    def _mark_run_completed(self):
        """Mark simulation run as complete."""
        self.db.execute("""
            UPDATE simulation_runs 
            SET status = 'completed', updated_at = CURRENT_TIMESTAMP
            WHERE run_id = ?
        """, (self.current_run_id,))
        self.db.commit()
    
    def _load_state(self, year: int):
        """Load world state from checkpoint."""
        # Restore cities, populations, etc. from snapshots at `year`
        # Set RNG state appropriately
        pass
    
    def _copy_state_to(self, year: int, target_db: str):
        """Copy state up to year into new database (for branching)."""
        # SQL: Copy cities, snapshots, events up to `year`
        pass
```

**Usage examples:**
```python
# Initial run
sim = Simulation('saskantinon.db', SimulationConfig(chunk_size=100))
sim.run(start_year=0, end_year=500)
# Output:
# Simulating 0-100 AA... ✓
# Simulating 100-200 AA... ✓
# Simulating 200-300 AA... ✓
# Simulating 300-400 AA... ✓
# Simulating 400-500 AA... ✓

# Resume after fixing bug
sim2 = Simulation('saskantinon.db', SimulationConfig())
sim2.resume(from_year=500, to_year=1000)

# Create alternative timeline
main_sim = Simulation('saskantinon.db', SimulationConfig())
alt_sim = main_sim.branch(from_year=1200, branch_name="kahila_victory")
alt_sim.run(start_year=1200, end_year=2450)
```

**Inspection tools:**
```python
def inspect_year(db_path: str, year: int):
    """Generate detailed report for a specific year."""
    conn = sqlite3.connect(db_path)
    
    print(f"\n{'='*60}")
    print(f"World State: Year {year} AA")
    print(f"{'='*60}\n")
    
    # Population summary
    city_pops = conn.execute("""
        SELECT c.name, s.population_total
        FROM city_snapshots s
        JOIN cities c ON s.city_id = c.id
        WHERE s.year = ?
        ORDER BY s.population_total DESC
        LIMIT 10
    """, (year,)).fetchall()
    
    print("Top 10 Cities by Population:")
    for name, pop in city_pops:
        print(f"  {name:20s} {pop:>10,}")
    
    # Events
    events = conn.execute("""
        SELECT name, type FROM events WHERE year = ?
    """, (year,)).fetchall()
    
    if events:
        print(f"\nEvents in {year} AA:")
        for name, event_type in events:
            print(f"  [{event_type}] {name}")
    
    conn.close()

# Usage:
inspect_year('saskantinon.db', 1200)
```

## Alternatives Considered

**Monolithic simulation (run everything at once):**
- Pro: Simpler code
- Con: No inspection, hard to debug, can't branch
- **Rejected:** Loses too much flexibility

**Save-on-demand (manual checkpoints):**
- Pro: Minimal overhead
- Con: Easy to forget, inconsistent checkpoints
- **Rejected:** Automated checkpoints more reliable

**Event sourcing (store only state changes):**
- Pro: Minimal storage, perfect audit trail
- Con: Slow state reconstruction, complex query logic
- **Rejected:** Premature optimization (see ADR-002)

**Micro-checkpoints (every year):**
- Pro: Maximum granularity
- Con: Excessive I/O, database bloat
- **Rejected:** 100-year chunks sufficient

## Testing Strategy

```python
def test_resumability():
    """Verify simulation can resume correctly."""
    # Run 0-200
    sim1 = Simulation('test.db', SimulationConfig(random_seed=42))
    sim1.run(0, 200)
    state_200 = get_state(sim1.db, 200)
    
    # Run 0-200 again in chunks with resume
    sim2 = Simulation('test2.db', SimulationConfig(random_seed=42))
    sim2.run(0, 100)
    sim2.resume(100, 200)
    state_200_resumed = get_state(sim2.db, 200)
    
    # Should be identical
    assert state_200 == state_200_resumed

def test_branching():
    """Verify branching creates independent timelines."""
    main_sim = Simulation('main.db', SimulationConfig())
    main_sim.run(0, 500)
    
    # Branch at 300
    branch_sim = main_sim.branch(300, "test_branch")
    
    # Modify branch (different shock)
    branch_sim.run(300, 400)
    
    # Main and branch should differ after 300
    main_state = get_state(main_sim.db, 400)
    branch_state = get_state(branch_sim.db, 400)
    
    assert main_state != branch_state
```

## References

- Checkpoint/restore patterns: https://martinfowler.com/bliki/MemoryImage.html
- Branching version control analogy: Git's branching model
