# Saskan-Calendar Project Structure Analysis

## Top-Level Directories & Purposes

### Application Packages (Poetry-managed packages)

- app_calendar/ - Main/complete calendar application (~21 Python files)
  - Core astronomical/calendrical calculations for Saskantinon world
  - Music generation subsystem (music/ subdirectory with ~15 files)
  - JSON data files for moons, events, lore

- app_maps/ - Experimental AI-generated mapping application (~14 Python files)
  - Settlement simulation and geographic modeling
  - Typer-based CLI with multiple commands
  - Structured into: geo/, graphs/, saskan/, common/ subdirectories

- app_timeline/ - Nascent timeline application (minimal - just __init__.py)
  - Placeholder for worldbuilding simulation system
  - Guided by ADRs in design/timeline/adr/

### Configuration & Management

- config/ - Application configuration
  - config/calendar/config.py - Flask config classes (Dev/Test/Prod)
  - Uses environment variables for secrets
  - SQLAlchemy, session, Babel settings

- manage/ - Management scripts
  - manage/calendar/manage.py - Flask CLI entrypoint

### Supporting Directories

- data/ - Runtime data & artifacts
  - data/calendar/ - Music compositions, JSON logs, spreadsheets
  - data/maps/ - Map simulation data

- design/ - Design documentation
  - design/timeline/adr/ - 7 Architecture Decision Records for timeline app

- docs/ - Documentation
  - docs/calendar/README.md - calendar app usage guide

- tests/ - Test suites
  - tests/calendar/ - pytest tests for calendars, moons, UDT, wanderers
  - tests/maps/ - pytest tests for maps app

- snips/ - Code snippets/experiments
  - Older versions of musebox.py and music_core.py

- env/ - Environment files (likely .env files)

## Shared vs. App-Specific Code

### Shared/Reusable Code (Currently scattered - refactoring opportunity!)

- File utilities: method_files.py (in app_calendar/music/)
- Shell utilities: method_shell.py (in app_calendar/music/)
- Common patterns:
  - JSON config loading
  - Data persistence patterns
  - CLI patterns (Flask CLI in calendar, Typer in maps)

### App-Specific Code

#### app_calendar/ - Highly specialized

- core.py (54,941 bytes) - Astronomical calculations, calendar systems

  - Astro Solar calendar, Terpin/Fatunik solar calendars
  - Moon phases, wanderers, star context
  - Date translation between systems
  - Heavy use of numpy for calculations

- Music generation subsystem - Unique to this app

  - music_core.py, io_music.py, musebox.py
  - Integration with music21 library
  - Thematic music generation for world objects/events

- Language/translation: lang_converter.py, lang_converter_debug.py

#### app_maps/ - Structured for extensibility

- Core simulation: saskan/engine.py (18,423 bytes)
- Configuration: saskan/settings.py (SimulationConfig dataclasses)
- Persistence: saskan/persistence.py (JSON snapshots)
- Visualization: saskan/plotting.py, saskan/map_utils.py
- CLI: Typer-based with multiple commands (geo, graph, saskan-sim, saskan-map, saskan-plot)

#### app_timeline/ - Currently just a placeholder

## Poetry Configuration & Key Dependencies

### Project Metadata

```yaml
name = "saskan-calendar"
version = "0.1.0"
description = "Experimental sub-apps for the Saskan Lands"
python = ">=3.12,<3.13"
```

### Key Dependency Groups

#### Web Framework (for calendar app)

- flask + ecosystem (flask-login, flask-bcrypt, flask-wtf, flask-cors, flask-sqlalchemy, flask-babel)
- gunicorn (implied from README - production server)

#### Database & Data

- sqlalchemy + sqlalchemy-utils
- pandas, numpy
- numbers-parser, odfpy, openpyxl (spreadsheet I/O)

#### Date/Time

- pendulum (modern date/time library)

#### Specialized Domain Libraries

- music21 (music theory/generation)
- networkx (graph algorithms for roads/migration)
- matplotlib (visualization)

#### CLI & Utilities

- typer (maps app CLI)
- tabulate, colorama (pretty console output)
- python-slugify, prettyprinter, markdown
- langdetect (language detection)

#### AI Integration

- openai (narrative generation per ADR-005)

#### Dev Dependencies

- pytest + plugins (pytest-flask, pytest-html, pytest-sqlalchemy, -pytest-playwright, pytest-mock)
- playwright (browser automation)
- locust (load testing)
- black, isort (code formatting)

#### CLI Entry Points

```yaml
[
tool.poetry.scripts
]
saskan-calendar = "scripts.manage:cli"  # Note: This path seems incorrect
saskan-experiments = "experiments.cli:app"  # Note: This path also seems incorrect
```

## App Purpose Summaries

- app_calendar/ - calendar Application

__Status__: Most mature/complete
__Purpose__: Interactive CLI and web app for managing calendrical and astronomical calculations for the Saskantinon RPG world

### Calendar Core Features

- Multiple calendar systems (Astro Solar, Terpin Solar, Fatunik Solar, Lunar A/B/C)
- Astronomical events (moon phases, wanderers/planets, stars, seasons)
- "Turn" (year) system based on planet Gavor's 365.2422-day orbit around star Fatune
- 8-moon system with individual lunar cycles
- Language/translation system for fictional languages
- Music generation tied to world events/objects
- Flask-based web interface with SQLAlchemy backend
- Database of lore events and meaningful dates

__Tech Stack__: Flask, SQLAlchemy, music21, numpy, pendulum

app_maps/ - Geographic Simulation (Experimental, AI-Generated)

__Status__: Experimental, CLI-focused
__Purpose__: Settlement growth simulation and geographic modeling for the Saskan Lands

### Maps Core Features

- Settlement population dynamics (growth, migration, carrying capacity)
- Geographic modeling (block-based grid system)
- Road network simulation (Ring Road, migration paths)
- Event system (famines, wars)
- Multiple visualization modes:
  - Coarse block maps (ASCII-style)
  - matplotlib plots (PNG export)
  - Settlement summaries (tabular)
- Scenario system ("great-migration" preset)
- Deterministic simulation (seed-based)
- JSON snapshot persistence for time-series analysis

__Tech Stack__: Typer (CLI), networkx (graphs), matplotlib (plotting), pandas/numpy

__AI Generation Note__: Code shows clean separation of concerns, suggesting careful AI-assisted development with human refinement

app_timeline/ - Worldbuilding Simulation (Nascent)

__Status__: Early planning phase
__Purpose__: Comprehensive demographic/historical simulation system per ADRs

__Planned Architecture__ (from ADRs):

1. SQLite source of truth (ADR-001) - All state in relational DB
2. Time-series snapshots (ADR-002) - Yearly snapshots for temporal queries
3. Python simulation engine (ADR-003) - Modular, testable, functional-friendly
4. JSON config only (ADR-004) - Parameters separate from state
5. AI narrative generation (ADR-005) - Claude/GPT-4 for prose, humans for logic
6. Incremental simulation (ADR-006) - 100-year chunks, resumable
7. Hybrid workflow (ADR-007) - Algorithms for consistency, humans for creativity

### Timeline Planned Features

- 2000+ year timeline simulation (0-2450 AA)
- Multi-species population dynamics (rabbit-sints, terpins, humans)
- Political entities (Fatunik Dominion, etc.)
- War mechanics, infrastructure projects
- Migration flows, carrying capacity
- Narrative export to Markdown/WorldAnvil
- Branching scenarios (alternative histories)

__Overlap with__ app_maps: Significant! Maps app appears to be a proof-of-concept for timeline features (settlement simulation, migration, events)

## Refactoring Opportunities

### Immediate Shared Code Extraction

1. File I/O utilities - method_files.py should move to shared location
2. Shell utilities - method_shell.py likewise
3. CLI patterns - Both Flask CLI and Typer CLI patterns could be standardized
4. Config management - Pattern from config/calendar/config.py could be generalized
5. Data persistence - JSON snapshot logic in maps could be shared library
6. Testing utilities - Shared pytest fixtures

### Proposed Shared Structure

```text
/shared/
  /utils/
    file_io.py      # from method_files.py
    shell.py        # from method_shell.py
    cli.py          # CLI helpers
  /persistence/
    json_store.py   # snapshot logic
    sqlite.py       # SQLAlchemy patterns
  /config/
    base_config.py  # Flask config base class
  /testing/
    fixtures.py     # shared pytest fixtures
```

### Timeline App Strategy

Given ADRs and maps app overlap:

1. Harvest from maps app: Simulation engine patterns, persistence, CLI structure
2. Extend for timeline needs: Multi-species, politics, longer timescales
3. Integrate calendar app: Astronomical calculations for date anchoring
4. Share common infrastructure: Use refactored shared utilities

---

## Key Insights

1. Project is a worldbuilding toolkit for the Saskantinon RPG world, not a single app
2. Calendar app is mature but isolated; has valuable astronomical/temporal calculations
3. Maps app is a well-structured prototype that anticipates timeline app needs
4. Timeline app has excellent architectural planning (ADRs) but minimal implementation
5. Shared code exists but is duplicated/isolated - prime refactoring target
6. Poetry setup is correct but CLI entry points may need fixing
7. Testing infrastructure exists but could be expanded with shared fixtures

## Recommended Next Steps

1. Create /shared package for common utilities
2. Refactor method_files.py and method_shell.py into shared utilities
3. Decide on maps→timeline relationship (merge? keep separate? shared library?)
4. Fix Poetry CLI entry points
5. Begin timeline MVP following ADR Phase 1 (single city simulation)
