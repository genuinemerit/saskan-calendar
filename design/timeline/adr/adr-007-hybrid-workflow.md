# ADR 007: Hybrid Manual-Algorithmic Worldbuilding Workflow

**Status:** Proposed

**Date:** 2024-12-27

## Context

Worldbuilding for the Saskan Lands involves both:
- **Algorithmic elements:** Population dynamics, migration flows, resource constraints (can be modeled mathematically)
- **Creative elements:** Cultural details, character motivations, narrative arcs (require human authorship)

Two extreme approaches exist:

1. **Fully manual:** Author invents everything (populations, events, timelines) without simulation
   - Pro: Complete creative control
   - Con: Difficult to maintain internal consistency (Did Beshquahoek have enough farmland to support 50k people in 1200 AA?)
   - Con: Time-consuming (2000 years of history is a lot to track)

2. **Fully algorithmic:** Let simulation generate everything (events, culture, narrative)
   - Pro: Internally consistent, deterministic
   - Con: Generic, lacks authorial voice, misses unique Saskan themes (solarpunk, pollinator crisis)
   - Con: Algorithm doesn't "know" what makes good story

The sweet spot is somewhere between: **use algorithms for consistency, humans for creativity**.

**Question:** How do we structure the workflow to leverage both?

## Decision

**We will adopt a hybrid manual-algorithmic workflow** with clear boundaries:

**Algorithms handle:**
- Population growth/decline (logistic formulas)
- Migration flows (network-based calculations)
- Resource constraints (carrying capacity, arable land)
- Rank-size distributions (city hierarchies)
- Stochastic shocks (famine frequency, severity)

**Humans handle:**
- Major historical events (wars, reforms, discoveries)
- Cultural details (Fatunik denominations, Riverwaq songs)
- Character creation (legendary figures, protagonists)
- Thematic arcs (planetary awakening, species cooperation)
- Narrative descriptions (converting data to prose)

**Workflow pattern:**
```
1. Human: Define eras, major events (Eelani-Fatunik War 2190-2200 AA)
2. Algorithm: Simulate population impacts of war (famine shocks, refugee flows)
3. Human: Inspect results, adjust parameters if implausible
4. Algorithm: Re-simulate with adjustments
5. Human: Write narrative descriptions based on final data
6. Algorithm: (Optional) AI generates draft text from templates
7. Human: Review, edit, curate AI-generated content
8. Database: Store curated content as canonical
```

**Integration points:**
- Simulation reads human-authored events from database
- Simulation writes demographic data to database
- Human inspects data, writes narrative
- AI assists with prose generation (optional)

**Feedback loops:**
- Simulation reveals inconsistencies (e.g., "Beshquahoek can't support 100k people without irrigation")
- Human adjusts timeline or adds infrastructure projects
- Simulation validates adjustments

## Consequences

### Positive

- **Best of both worlds:**
  - Mathematical rigor (populations obey carrying capacity)
  - Creative freedom (author decides when wars happen)

- **Consistency checking:**
  ```
  Author: "Beshquahoek has 100k people in 1200 AA"
  Simulation: "Carrying capacity only supports 40k without canals"
  Author: "Okay, add canal project in 1150 AA"
  Simulation: "Now supports 90k. Still 10k short."
  Author: "Make it 90k, or add second canal"
  ```

- **Inspiration from data:**
  ```
  Simulation: "Migration spike from Ingar to Juuj in 1150 AA"
  Author: "Why? Let me invent a reason... Religious persecution?"
  Result: New event added to timeline
  ```

- **Scalability:**
  - Simulation handles tedious calculations (2000 cities × 2000 years)
  - Human focuses on creative high-impact decisions

- **Reproducibility:**
  - Same events + parameters → same demographic outcomes
  - Can version control both code (simulation) and data (events)

- **Division of labor:**
  - Different sessions: sometimes coding (simulation), sometimes writing (narrative)
  - Can alternate based on mood, energy

### Negative

- **Context switching:**
  - Must shift between coding mindset (simulation) and creative mindset (writing)
  - Mitigated by: Clear workflow stages (simulate → inspect → write)

- **Interface complexity:**
  - Need tools to move between algorithm (code) and narrative (text)
  - Mitigated by: Database as shared medium, Jupyter notebooks for exploration

- **Judgment calls:**
  - Not always clear where algorithm ends and human begins
  - Example: Should famines be randomly generated or manually placed?
  - Mitigated by: Start with defaults (random), manually override as needed

### Neutral

- **Who decides events?**
  - Option A: Human places all major events → simulation fills in demographic details
  - Option B: Simulation generates event candidates → human curates
  - **Recommendation:** Start with A (human-driven), add B later if desired

## Implementation Notes

**Example: War event (human-authored, algorithm-executed)**

**1. Human creates event template:**
```json
// configs/events.json
{
  "eelani_fatunik_war": {
    "start_year": 2190,
    "end_year": 2200,
    "type": "war",
    "description": "Religious and political conflict over seed bank control",
    "affected_regions": ["ingar", "juuj", "qurol", "morilly"],
    "effects": {
      "shock_multiplier": 0.75,  // 25% population loss in war zones
      "migration_boost": 2.0,     // Double migration to neutral zones
      "infrastructure_damage": 0.9  // 10% reduction in I_t
    }
  }
}
```

**2. Simulation reads and applies event:**
```python
def apply_event(self, event_data: dict, year: int):
    """Execute event effects on simulation state."""
    if event_data['type'] == 'war':
        for region_id in event_data['affected_regions']:
            cities_in_region = self.get_cities_by_region(region_id)
            
            for city in cities_in_region:
                # Apply shock
                shock = event_data['effects']['shock_multiplier']
                city.apply_shock(year, shock)
                
                # Reduce infrastructure
                damage = event_data['effects']['infrastructure_damage']
                city.infrastructure[year] *= damage
        
        # Boost outbound migration
        migration_boost = event_data['effects']['migration_boost']
        self.migration_coefficient *= migration_boost
```

**3. Simulation generates results:**
```
Year 2190 AA:
  Ingar population: 120,000 → 90,000 (war shock)
  Juuj population: 80,000 → 60,000 (war shock)
  Beshquahoek population: 40,000 → 45,000 (refugee influx)
  
Year 2200 AA (war ends):
  Ingar population: 92,000 (recovery begins)
  ...
```

**4. Human reviews results:**
```
✓ Population losses plausible for 10-year war
✓ Migration patterns make sense (people flee to neutral Beshquahoek)
⚠️ Juuj recovered too quickly (population back to 75k by 2210)
```

**5. Human adjusts parameters:**
```json
// Reduce recovery rate for Juuj specifically
"eelani_fatunik_war": {
  ...
  "aftermath": {
    "juuj": {
      "recovery_penalty": 0.5  // Slower recovery (damaged infrastructure)
    }
  }
}
```

**6. Re-simulate and validate:**
```
Year 2210 AA:
  Juuj population: 68,000 (slower recovery, more realistic)
  ✓ Approved
```

**7. Human writes narrative (with optional AI assist):**
```python
# Generate narrative description
event_summary = {
    'name': 'Eelani-Fatunik War',
    'years': '2190-2200 AA',
    'combatants': 'Eelani Confederation vs. Fatunik Dominion',
    'cause': 'Dispute over seed bank monopoly and religious authority',
    'outcome': 'Stalemate; Beshquahoek Accords signed',
    'casualties': '~50,000 total (25% in war zones)',
    'refugees': '~15,000 fled to neutral territories'
}

# AI generates draft
draft = ai.generate_event_description(event_summary, context=saskan_lore)

# Human curates
final = curate(draft)  # Review, edit, approve

# Store
db.save_event_description(event_id='eelani_war', text=final)
```

**Example: Discovery event (algorithm-suggested, human-curated)**

**1. Simulation runs, generates migration spike:**
```
Year 1750 AA:
  Anomaly detected: Migration from Ingar → Beshquahoek increased 300%
  Probable cause: Carrying capacity exceeded in Ingar (famine)
```

**2. Human investigates:**
```python
inspect_year(db, 1750)
# Output shows Ingar hit carrying capacity, no infrastructure improvements scheduled
```

**3. Human invents explanation and adds event:**
```json
{
  "great_famine_1750": {
    "year": 1750,
    "type": "famine",
    "regions": ["ingar"],
    "cause": "Canal failure + bad harvest",
    "effects": {
      "shock_multiplier": 0.70
    }
  }
}
```

**4. Re-simulate to validate:**
```
Year 1750 AA (with famine event):
  Migration spike now explained by famine
  ✓ Consistent with data
```

**Example workflow script:**
```python
# scripts/workflow.py
"""
Interactive workflow for hybrid worldbuilding.
"""

def worldbuilding_session(db_path: str):
    """Run interactive worldbuilding session."""
    sim = Simulation(db_path, load_config())
    
    while True:
        print("\n" + "="*60)
        print("Saskan Lands Worldbuilding")
        print("="*60)
        print("1. Simulate era")
        print("2. Inspect year")
        print("3. Add event")
        print("4. Generate narrative")
        print("5. Export timeline")
        print("6. Quit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            start = int(input("Start year: "))
            end = int(input("End year: "))
            sim.run(start, end)
        
        elif choice == '2':
            year = int(input("Year to inspect: "))
            inspect_year(db_path, year)
        
        elif choice == '3':
            add_event_interactive(db_path)
        
        elif choice == '4':
            generate_narratives_interactive(db_path)
        
        elif choice == '5':
            export_timeline(db_path, output_format='markdown')
        
        elif choice == '6':
            break

# Usage:
# python scripts/workflow.py
```

**Decision tree for when to use algorithm vs. manual:**

```
Question: Should this be algorithmic or manual?

Is it a mathematical/demographic pattern?
├─ YES → Algorithm
│   Examples: population growth, migration flows, city sizes
└─ NO → Is it a unique creative element?
    ├─ YES → Manual
    │   Examples: character names, cultural practices, theology
    └─ NO → Is it a recurring pattern that's tedious to do manually?
        ├─ YES → Algorithm with human oversight
        │   Examples: minor town founding, trade route formation
        └─ NO → Manual
            Examples: major historical events, thematic arcs
```

## Alternatives Considered

**Fully manual worldbuilding:**
- Pro: Total creative control
- Con: Can't track 2000 years × 100 cities without help
- **Rejected:** Too much busywork

**Fully algorithmic worldbuilding:**
- Pro: Consistent, deterministic
- Con: Generic, no authorial voice
- **Rejected:** Loses unique Saskan identity

**Algorithmic generation with no human review:**
- Pro: Fast, automated
- Con: Will produce nonsense, lore conflicts
- **Rejected:** Quality suffers

**Manual events only, no demographic simulation:**
- Pro: Simple
- Con: Can't validate consistency (did Beshquahoek have enough food?)
- **Rejected:** Loses rigor

## Best Practices

**1. Start with human-authored skeleton:**
- Define eras, major events first
- Let simulation fill in demographic details
- Avoids aimless procedural generation

**2. Use simulation for validation:**
- "Can this city support this population?"
- "Do these events explain migration patterns?"

**3. Iterate on feedback:**
- Simulate → inspect → adjust → re-simulate
- Don't expect perfection on first run

**4. Document assumptions:**
- Why did you choose r=0.004 for humans?
- Why is Kahila arable fraction only 15%?
- Comments in JSON configs, ADRs, wiki

**5. Preserve creative decisions:**
- Mark manually-placed events clearly
- Don't let algorithm overwrite human choices

**6. Use AI sparingly:**
- For grunt work (expanding notes to paragraphs)
- Always review before accepting

## Testing Strategy

```python
def test_hybrid_workflow():
    """Verify algorithm respects human-authored events."""
    # Create event: famine in year 100
    add_event(db, {
        'year': 100,
        'type': 'famine',
        'regions': ['ingar'],
        'shock': 0.7
    })
    
    # Run simulation
    sim = Simulation(db, config)
    sim.run(0, 200)
    
    # Verify event was applied
    ingar_pop_100 = get_population(db, 'ingar', 100)
    ingar_pop_99 = get_population(db, 'ingar', 99)
    
    # Should show ~30% decline
    assert ingar_pop_100 < ingar_pop_99 * 0.75
    assert ingar_pop_100 > ingar_pop_99 * 0.65
```

## References

- Procedural Content Generation in Games: http://pcgbook.com/
- Worldbuilding and simulation: https://www.gamedeveloper.com/design/procedural-world-generation-of-stellaris
- Human-in-the-loop AI: https://en.wikipedia.org/wiki/Human-in-the-loop
