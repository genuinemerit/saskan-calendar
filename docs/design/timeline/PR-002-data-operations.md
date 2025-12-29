# PR-002: Data Operations & CRUD Interface

**Status:** Proposed
**Date:** 2025-12-29
**Related ADRs:** ADR-001 (SQLite), ADR-002 (Time-Series Snapshots)
**Depends On:** PR-001 (Database Foundation)

---

## Overview

Add data entry, query, and management capabilities to the timeline system. This completes the "data layer" and positions the system for simulation engine development (PR-003).

**Goal:** Enable manual data entry and exploration of timeline data through CLI and programmatic interfaces.

---

## Scope

### In Scope
- CRUD operations for all 8 core tables (including Epochs)
- Query/list commands with filtering
- Data validation (soft constraints)
- CSV/JSON import/export
- Relationship verification
- Interactive CLI experience with meta_data key-value prompts
- Epoch management for named time periods
- Basic geography fields (grid coordinates, area, distance)
- Explicit astro_day requirements for queries

### Out of Scope
- Web interface (future)
- Bulk simulation data generation (PR-003)
- Advanced analytics/reporting (future)
- Database migrations (Alembic - future)
- Geographic calculations and constraints (PR-003)
- Automated grid assignment (PR-003)

---

## Implementation Sub-Steps

### Step 1: Service Layer Foundation
**Goal:** Create reusable service classes for database operations + add Epoch model + enhance geography

**Deliverables:**

**A. New Model: Epochs**
- `app_timeline/models/epoch.py` - Epoch model for named time periods
  - Supports overlapping epochs
  - Multiple epochs for same time range
  - Enables epoch-based queries

**B. Geography Enhancements**
- Update Settlement model with grid fields:
  - `grid_x` (INTEGER 1-40) - Grid column
  - `grid_y` (INTEGER 1-30) - Grid row
  - `area_sq_km` (FLOAT, nullable) - Settlement area
- Update Route model:
  - Clarify `distance_km` field (already exists)
- Update schema validation for new table

**C. Service Layer**
- `app_timeline/services/` module
  - `base.py` - Base service class with common CRUD patterns
  - `region_service.py` - Region operations
  - `province_service.py` - Province operations
  - `settlement_service.py` - Settlement operations
  - `snapshot_service.py` - Settlement snapshot operations
  - `route_service.py` - Route operations
  - `entity_service.py` - Entity operations
  - `event_service.py` - Event operations
  - `epoch_service.py` - Epoch operations (NEW)

**Key Features:**
- Type-safe operations (leveraging SQLAlchemy models)
- Transaction management
- Error handling with descriptive messages
- Relationship validation
- Soft validation against YAML config

**Example Pattern:**
```python
class SettlementService:
    def create(self, name: str, settlement_type: str,
               founded_astro_day: int, **kwargs) -> Settlement:
        """Create a new settlement with validation."""

    def get_by_id(self, settlement_id: int) -> Optional[Settlement]:
        """Retrieve settlement by ID."""

    def get_by_name(self, name: str) -> Optional[Settlement]:
        """Retrieve settlement by name."""

    def list_all(self, filters: dict = None) -> List[Settlement]:
        """List settlements with optional filtering."""

    def update(self, settlement_id: int, **kwargs) -> Settlement:
        """Update settlement fields."""

    def delete(self, settlement_id: int) -> bool:
        """Soft delete (set is_active=False)."""

    def get_history(self, settlement_id: int) -> List[SettlementSnapshot]:
        """Get all snapshots for a settlement."""
```

**Testing:**
- `tests/timeline/test_services.py` - Unit tests for all service classes
- Test validation logic
- Test relationship constraints
- Test error conditions

**Estimated Complexity:** Medium
**Time:** ~1 session

---

### Step 2: CLI Add/Create Commands
**Goal:** Interactive data entry via CLI

**Deliverables:**
- `saskan-timeline add` subcommand group
  - `add region` - Create region
  - `add province` - Create province (with region selection)
  - `add settlement` - Create settlement (with province/parent selection)
  - `add snapshot` - Create settlement snapshot
  - `add route` - Create route between settlements
  - `add entity` - Create entity (person/organization)
  - `add event` - Create timeline event

**CLI Features:**
- Interactive prompts for required fields (Typer + Rich)
- Optional fields skippable
- Foreign key selection with autocomplete
- Validation feedback
- Success confirmation with ID

**Example:**
```bash
$ saskan-timeline add settlement
Settlement name: Ingar
Settlement type [ring_town/market_town/...]: ring_town
Founded (astro_day): 0
Province (optional, enter name or ID): Fatunik
Parent settlement (optional):
Location X (optional): 100.5
Location Y (optional): 200.3
Is autonomous? [y/N]: n

Success! Created settlement 'Ingar' (ID: 1)
```

**Testing:**
- Manual smoke tests for each command
- Integration tests using Typer's testing utilities

**Estimated Complexity:** Medium-High (interactive UX)
**Time:** ~1-2 sessions

---

### Step 3: CLI List/Query Commands
**Goal:** View and search existing data

**Deliverables:**
- `saskan-timeline list` subcommand group
  - `list regions` - Show all regions
  - `list provinces` - Show provinces (filterable by region)
  - `list settlements` - Show settlements (filterable by province/type)
  - `list routes` - Show routes (filterable by settlement)
  - `list entities` - Show entities (filterable by type)
  - `list events` - Show events (filterable by time range/type)

- `saskan-timeline show` subcommand group
  - `show settlement <name|id>` - Detailed settlement view with snapshots
  - `show province <name|id>` - Province with settlements
  - `show region <name|id>` - Region with provinces
  - `show entity <name|id>` - Entity details
  - `show event <id>` - Event details

**CLI Features:**
- Rich table formatting
- Pagination for long lists
- Filtering options (--province, --type, --active-only, etc.)
- Sorting options
- Summary statistics

**Example:**
```bash
$ saskan-timeline list settlements --province Fatunik --type ring_town

Settlements in Fatunik Province (type: ring_town)
+----+---------+------------+---------+----------+--------+
| ID | Name    | Type       | Founded | Pop (ID) | Active |
+----+---------+------------+---------+----------+--------+
| 1  | Ingar   | ring_town  | 0       | -        | Yes    |
| 2  | Rutonik | ring_town  | 50      | -        | Yes    |
+----+---------+------------+---------+----------+--------+

Total: 2 settlements
```

```bash
$ saskan-timeline show settlement Ingar

Settlement: Ingar (ID: 1)
Type: ring_town
Province: Fatunik (ID: 1)
Founded: Day 0
Status: Active

Snapshots (3):
  Day 0:    Population 1,000 (huum: 900, sint: 100)
  Day 100:  Population 5,000 (huum: 4,500, sint: 500)
  Day 200:  Population 8,000 (huum: 7,200, sint: 800)
```

**Testing:**
- Unit tests for query logic
- Manual verification of formatting

**Estimated Complexity:** Medium
**Time:** ~1 session

---

### Step 4: CLI Update/Delete Commands
**Goal:** Modify and remove data

**Deliverables:**
- `saskan-timeline update` subcommand group
  - `update settlement <id>` - Modify settlement
  - `update province <id>` - Modify province
  - `update region <id>` - Modify region
  - (Similar for other entities)

- `saskan-timeline delete` subcommand group
  - `delete settlement <id>` - Soft delete settlement
  - `delete province <id>` - Soft delete province
  - (Similar for other entities)
  - Confirmation prompts
  - Cascade warnings (if relationships exist)

**CLI Features:**
- Interactive field selection (which fields to update?)
- Show current values
- Confirmation before delete
- Relationship warnings

**Example:**
```bash
$ saskan-timeline update settlement 1
Current values for 'Ingar':
  Type: ring_town
  Province: Fatunik
  Founded: 0
  Location: (100.5, 200.3)

Fields to update (comma-separated, or 'all'): location
New Location X: 101.0
New Location Y: 201.0

Updated settlement 'Ingar' (ID: 1)
```

```bash
$ saskan-timeline delete settlement 1
WARNING: Settlement 'Ingar' has 3 snapshots and 2 routes.
These relationships will remain but may become orphaned.
Are you sure you want to delete? [y/N]: n
Cancelled.
```

**Testing:**
- Unit tests for update logic
- Manual smoke tests for delete confirmation

**Estimated Complexity:** Medium
**Time:** ~1 session

---

### Step 5: Import/Export Commands
**Goal:** Bulk data operations

**Deliverables:**
- `app_timeline/io/` module
  - `csv_handler.py` - CSV import/export
  - `json_handler.py` - JSON import/export
  - `validators.py` - Import validation

- `saskan-timeline import` subcommand group
  - `import settlements <file>` - Import from CSV/JSON
  - `import provinces <file>`
  - `import snapshots <file>`
  - (Similar for other entities)
  - Validation and error reporting
  - Dry-run mode (--validate-only)

- `saskan-timeline export` subcommand group
  - `export settlements <file>` - Export to CSV/JSON
  - `export all <directory>` - Export entire database
  - Format selection (--format csv|json)

**CSV Format Example (settlements):**
```csv
name,settlement_type,founded_astro_day,province_name,location_x,location_y,is_autonomous
Ingar,ring_town,0,Fatunik,100.5,200.3,false
Rutonik,ring_town,50,Fatunik,150.0,250.0,false
```

**JSON Format Example (settlements):**
```json
[
  {
    "name": "Ingar",
    "settlement_type": "ring_town",
    "founded_astro_day": 0,
    "province_name": "Fatunik",
    "location_x": 100.5,
    "location_y": 200.3,
    "is_autonomous": false,
    "meta_data": {
      "water": "fresh",
      "fertile": true
    }
  }
]
```

**CLI Features:**
- Progress bars for large imports
- Validation error reporting (line numbers)
- Transaction rollback on error
- Summary statistics (imported/skipped/errors)

**Example:**
```bash
$ saskan-timeline import settlements data/settlements.csv --validate-only
Validating data/settlements.csv...
  Line 1: OK
  Line 2: WARNING - Province 'Unknown' not found
  Line 3: ERROR - Invalid settlement_type 'castle'

Validation complete: 1 OK, 1 WARNING, 1 ERROR
Run without --validate-only to import valid rows.
```

```bash
$ saskan-timeline export settlements output/settlements.json --format json
Exported 42 settlements to output/settlements.json
```

**Testing:**
- Unit tests for CSV/JSON parsing
- Test validation logic
- Test error handling
- Sample CSV/JSON files in tests/fixtures/

**Estimated Complexity:** Medium-High
**Time:** ~1-2 sessions

---

### Step 6: Validation & Helper Utilities
**Goal:** Data quality and convenience features

**Deliverables:**
- `saskan-timeline validate` subcommand group
  - `validate data` - Check data integrity
    - Orphaned relationships
    - Invalid foreign keys
    - Type mismatches with config
  - `validate snapshots` - Check time-series consistency
    - Gaps in snapshot timeline
    - Snapshots before settlement founding
  - `validate routes` - Check network consistency
    - Bidirectional routes
    - Disconnected settlements

- `saskan-timeline stats` command
  - Database statistics
  - Data distribution (settlements by type, events by type)
  - Time range coverage
  - Relationship counts

- Helper functions in services
  - Duplicate detection
  - Name normalization
  - Relationship suggestions (e.g., "Did you mean Fatunik Province?")

**Example:**
```bash
$ saskan-timeline validate data
Running data validation...

Regions: OK (3 regions, all active)
Provinces: OK (7 provinces)
Settlements: WARNING
  - Settlement 'Hamlet X' (ID: 42) has no province
  - Settlement 'Camp Y' (ID: 55) founded before parent settlement

Routes: ERROR
  - Route ID 12: Origin settlement not found (ID: 999)

Events: OK (127 events)

Validation complete: 2 warnings, 1 error
```

```bash
$ saskan-timeline stats
Timeline Database Statistics

Entities:
  Regions:              3
  Provinces:            7
  Settlements:         42 (ring_town: 5, hamlet: 30, village: 7)
  Snapshots:          184
  Routes:              38
  Entities:            12 (person: 8, organization: 4)
  Events:             127

Time Range:
  Earliest: Day 0
  Latest:   Day 2450
  Span:     2450 days

Most Recent Snapshot: Day 2400
```

**Testing:**
- Unit tests for validation logic
- Manual verification with test data

**Estimated Complexity:** Medium
**Time:** ~1 session

---

## File Structure After PR-002

```
app_timeline/
  __init__.py
  cli.py                    # EXPANDED - new command groups
  config.py                 # (unchanged)
  models/                   # (unchanged)
  db/                       # (unchanged)
  services/                 # NEW
    __init__.py
    base.py
    region_service.py
    province_service.py
    settlement_service.py
    snapshot_service.py
    route_service.py
    entity_service.py
    event_service.py
  io/                       # NEW
    __init__.py
    csv_handler.py
    json_handler.py
    validators.py

tests/timeline/
  conftest.py               # (unchanged)
  test_config.py            # (unchanged)
  test_db.py                # (unchanged)
  test_models.py            # (unchanged)
  test_services.py          # NEW
  test_io.py                # NEW
  fixtures/                 # NEW
    sample_settlements.csv
    sample_settlements.json
    sample_provinces.csv
```

---

## Testing Strategy

### Unit Tests
- Service layer: all CRUD operations
- Validation logic: soft constraints, relationships
- Import/export: CSV/JSON parsing, error handling

### Integration Tests
- CLI commands end-to-end
- Import -> List -> Export roundtrip
- Multi-step workflows (create province -> create settlements)

### Manual Testing
- Interactive CLI experience
- Data entry workflow
- Error message clarity

### Test Coverage Goals
- Services: 90%+ coverage
- IO handlers: 85%+ coverage
- Overall: 85%+ coverage

---

## Success Criteria

1. **Data Entry:** Can manually create a complete timeline scenario
   - 3+ epochs (named time periods)
   - 2+ regions
   - 5+ provinces
   - 20+ settlements with snapshots (including grid coordinates)
   - 10+ routes
   - 10+ events
   - 5+ entities

2. **Query:** Can efficiently find and view data
   - List settlements by province/type
   - Show settlement history over time
   - Find events in time range

3. **Import:** Can bulk-load data from CSV/JSON
   - Import 50+ settlements without errors
   - Validation catches common mistakes

4. **Export:** Can export entire database for backup/analysis
   - Round-trip import/export preserves data
   - Readable format for external tools

5. **Quality:** Data validation catches issues
   - Orphaned relationships
   - Type mismatches
   - Timeline inconsistencies

---

## Documentation Updates

### README.md
- Update "Data Management" section with new commands
- Add examples of CLI usage
- Add import/export formats

### TECHNICAL.md
- Document service layer architecture
- Add import/export specifications
- Update CLI command reference

### New Files
- `docs/timeline/IMPORT_FORMATS.md` - CSV/JSON format specifications
- `docs/timeline/EXAMPLES.md` - Sample workflows and use cases

---

## Dependencies

### New Python Packages
None required - using existing stack:
- typer (CLI)
- rich (formatting)
- sqlalchemy (ORM)
- pyyaml (config)

### Optional Enhancements
- `python-tabulate` - Better table formatting (if Rich tables insufficient)
- `click-repl` - Interactive REPL mode (future)

---

## Implementation Order Recommendation

**Recommended sequence for turtle-paced development:**

1. **Step 1: Service Layer** (Foundation)
   - Complete and test before moving to CLI
   - Provides reusable building blocks

2. **Step 3: List/Query Commands** (Quick win)
   - Useful immediately for inspecting test data
   - Simpler than add/update

3. **Step 2: Add Commands** (Core functionality)
   - Build on services from Step 1
   - Use list commands from Step 3 for verification

4. **Step 4: Update/Delete** (Complete CRUD)
   - Natural extension of add commands
   - Can test with data from Step 2

5. **Step 5: Import/Export** (Efficiency)
   - Useful for loading test scenarios
   - Enables backup/sharing

6. **Step 6: Validation & Stats** (Polish)
   - Ensure data quality
   - Nice-to-have utilities

**Each step is independently testable and deliverable.**

---

## Design Decisions (Approved 2025-12-29)

1. **Meta_data JSON editing:** ✓ **Option B - Interactive key-value prompts**
   - More user-friendly
   - Self-documenting
   - Reduces errors from malformed JSON

2. **Soft delete vs hard delete:** ✓ **Soft delete with future --purge flag**
   - Provides safety and undo capability
   - Better data management practice
   - Can add hard delete later if needed

3. **Duplicate handling on import:** ✓ **Error by default, --update-existing flag**
   - Maintains data quality
   - Encourages good practices
   - Explicit opt-in for updates

4. **astro_day on queries:** ✓ **Require explicit astro_day**
   - Queries focused on specific epochs
   - More intentional data exploration
   - No implicit defaults that might confuse

5. **Epoch support:** ✓ **Add in PR-002 Step 1**
   - Low complexity, high value
   - Enables epoch-based queries immediately
   - Supports overlapping time periods

6. **Geography fields:** ✓ **Add basic fields in PR-002, defer calculations to PR-003**
   - grid_x, grid_y (1-40 x 1-30 grid)
   - area_sq_km for settlements
   - distance_km already exists for routes
   - Calculations and constraints deferred to simulation engine

---

## Version Increment

After PR-002 completion:
- Version: 0.2.0 (minor feature addition)
- Update all version strings in:
  - `app_timeline/__init__.py`
  - `config/timeline/settings.yaml`
  - `pyproject.toml`
  - Documentation headers

---

## Next Steps After PR-002

**PR-003: Basic Simulation Engine**
- Implement population growth formulas (ADR-003)
- Single settlement simulation
- Snapshot generation
- Foundations for multi-settlement simulation

This will leverage the data operations from PR-002 for setting up initial conditions and storing simulation results.

---

## Notes

- All CLI commands should use Rich for formatted output
- All database operations should use service layer (not direct model access from CLI)
- All imports should validate before committing to database
- All exports should be human-readable and version-control friendly
- All commands should provide helpful error messages

---

## Approval Checklist

Before starting implementation:
- [ ] User approves overall scope
- [ ] User approves 6-step breakdown
- [ ] User approves recommended implementation order
- [ ] User provides answers to open questions
- [ ] Any worldbuilding-specific requirements clarified
