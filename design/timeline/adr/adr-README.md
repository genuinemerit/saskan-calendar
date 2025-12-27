# Architecture Decision Records (ADRs)
## Saskantinon Worldbuilding Simulation System

**Date:** 2024-12-27  
**Status:** Proposed architecture for development

---

## Overview

This collection of Architecture Decision Records (ADRs) documents the technical architecture for a hybrid worldbuilding system that combines:
- Demographic simulation (population dynamics, migration, resource constraints)
- Geographic modeling (cities, roads, regions, infrastructure)
- Narrative generation (historical timeline, events, character stories)

The system is designed to support the Saskan Lands worldbuilding project: a solarpunk post-catastrophe world recovering over 2000+ years.

---

## Core Principles

1. **Separation of Concerns:** Data (SQLite), configuration (JSON), logic (Python), narrative (human-authored with AI assistance)
2. **Human Authority:** Author remains creative decision-maker; algorithms provide consistency and inspiration
3. **Incremental Development:** Build complexity gradually; validate frequently
4. **Reproducibility:** Deterministic simulation with version-controlled configs
5. **Pragmatism:** Use appropriate tools for each task (SQL for queries, Python for math, AI for prose)

---

## ADR Index

### Foundation (Data & Configuration)

**[ADR-001: SQLite as Source of Truth](adr-001-sqlite-source-of-truth.md)**  
Use SQLite as the canonical database for all worldbuilding data (cities, populations, events, historical snapshots). JSON is relegated to configuration only.

**Key decision:** Relational database for state/data, JSON for parameters.

---

**[ADR-002: Time-Series Snapshot Architecture](adr-002-time-series-snapshots.md)**  
Store entity state at yearly intervals in dedicated snapshot tables, enabling temporal queries, branching timelines, and perfect reproducibility.

**Key decision:** One row per entity per year (not current-state-only).

---

**[ADR-004: JSON for Configuration Only](adr-004-json-config-only.md)**  
JSON files store only configuration/parameters (regional settings, species traits, event templates). All state data lives in SQLite.

**Key decision:** Clear separation between immutable config and mutable state.

---

### Simulation Engine

**[ADR-003: Python Simulation Engine](adr-003-python-simulation-engine.md)**  
Implement simulation engine in Python with modular, testable architecture. No Rust unless profiling reveals bottlenecks.

**Key decision:** Leverage existing Python expertise, functional-friendly design.

---

**[ADR-006: Incremental, Resumable Simulation](adr-006-incremental-simulation.md)**  
Run simulation in chunks (default: 100-year segments) with state persistence, enabling inspection, parameter adjustment, and timeline branching.

**Key decision:** Fail-fast validation over monolithic execution.

---

### Content Generation

**[ADR-005: AI for Narrative Generation Only](adr-005-ai-narrative-generation.md)**  
Use AI (Claude, GPT-4) exclusively for generating prose from simulation data. Humans write all simulation logic and make all creative decisions.

**Key decision:** AI as assistant, not authority; AI as amplifier, not replacement.

---

### Integration

**[ADR-007: Hybrid Manual-Algorithmic Workflow](adr-007-hybrid-workflow.md)**  
Combine algorithmic rigor (demographic consistency) with human creativity (narrative, culture, themes). Clear boundaries between what algorithms handle vs. what humans author.

**Key decision:** Use algorithms for consistency checking, humans for storytelling.

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Database | SQLite | Portable, powerful queries, ACID guarantees |
| Language | Python 3.10+ | Familiar, rich ecosystem, rapid prototyping |
| Data Analysis | pandas, numpy | Standard tools for data wrangling |
| Network | networkx | Graph algorithms for Ring Road, migration |
| Visualization | matplotlib, plotly | Static and interactive plots |
| Testing | pytest | Industry standard, good for scientific code |
| AI | Claude API | Best for complex instructions, less generic |
| Config | JSON | Stdlib support, version control friendly |

---

## Implementation Phases

### Phase 1: Foundation (MVP)
**Goal:** Single city, basic population growth simulation  
**Duration:** 2-3 weeks

**Deliverables:**
- SQLite schema (minimal)
- Python classes (City, Simulation)
- Config loader (JSON → objects)
- Basic visualization (population curves)

**Success criteria:** Can reproduce Beshquahoek's historical population arc

---

### Phase 2: Complexity
**Goal:** Multiple cities, migration, road network  
**Duration:** 1 month

**Deliverables:**
- Network graph (Ring Road)
- Migration flows
- Event system (famines, wars)
- Rank-size city distribution

**Success criteria:** Simulate Ingar + Rutónik + Beshquahoek for 500 years with plausible patterns

---

### Phase 3: Multi-Species & Politics
**Goal:** Species-specific dynamics, political entities  
**Duration:** 1 month

**Deliverables:**
- Species growth models (rabbit-sints, terpins, humans)
- Political control tracking (Fatunik Dominion, etc.)
- War mechanics (territory occupation, K_t depression)
- Infrastructure projects (canals, irrigation)

**Success criteria:** Simulate Eelani-Fatunik War (2190-2200 AA) with realistic impacts

---

### Phase 4: Full Timeline & Narrative
**Goal:** Complete 2000-year simulation with AI-assisted narrative  
**Duration:** Ongoing

**Deliverables:**
- Full 0-2450 AA simulation
- AI narrative generation pipeline
- Timeline export (Markdown, WorldAnvil)
- Branching scenarios (alternative histories)

**Success criteria:** Publishable timeline document with coherent narrative

---

## File Structure

```
saskantinon_sim/
├── docs/
│   └── adr/                    # This directory
│       ├── README.md           # This file
│       ├── adr-001-*.md
│       ├── adr-002-*.md
│       └── ...
├── configs/
│   ├── v1_baseline/
│   │   ├── regions.json
│   │   ├── species.json
│   │   ├── events.json
│   │   └── simulation.json
│   └── current -> v1_baseline/
├── saskantinon_sim/
│   ├── models/
│   ├── simulation/
│   ├── persistence/
│   ├── analysis/
│   └── cli/
├── tests/
├── scripts/
│   ├── migrate_data.py
│   ├── generate_narratives.py
│   └── workflow.py
├── data/
│   └── saskantinon.db          # SQLite database
└── notebooks/
    ├── exploration.ipynb
    └── visualization.ipynb
```

---

## Getting Started (Developer)

1. **Read the ADRs** (start with ADR-001, -003, -007)
2. **Set up environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Initialize database:**
   ```bash
   python scripts/init_db.py
   ```
4. **Run Phase 1 demo:**
   ```bash
   python -m saskantinon_sim.cli.main simulate --start 0 --end 100 --city beshquahoek
   ```
5. **Inspect results:**
   ```bash
   python scripts/inspect_year.py 100
   ```

---

## Design Philosophy

**"The simulation suggests; the author decides."**

The goal is not to replace human creativity with algorithms, but to:
- **Amplify** worldbuilding capacity (track 100 cities × 2000 years reliably)
- **Validate** creative choices (does this population make sense given resources?)
- **Inspire** narrative discoveries (migration spike → why? → invent event)
- **Maintain** internal consistency (carrying capacity, demographic realism)

The author remains the storyteller. The simulation is a tool, not a replacement.

---

## Questions & Discussions

For questions about these ADRs, create issues in the project repository or discuss in:
- Design decisions → ADR comments
- Implementation details → Code reviews
- Narrative/lore questions → Separate worldbuilding docs

---

## Revision History

| Date | Changes |
|------|---------|
| 2024-12-27 | Initial ADR collection created |

---

## References

- ADR pattern: https://adr.github.io/
- Worldbuilding resources: [Saskan Lands timeline](../timeline/saskantinon_timeline_master.md)
- Project background: [Scrivener "Code" materials]
