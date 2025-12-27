# ADR 005: AI for Narrative Generation, Not Simulation Logic

**Status:** Proposed

**Date:** 2024-12-27

## Context

Large Language Models (LLMs) like Claude, GPT-4, etc. offer powerful text generation capabilities. The question is: what role should they play in the worldbuilding workflow?

**Potential uses:**
1. Generate simulation logic/code (e.g., "write a function to calculate migration")
2. Make simulation decisions (e.g., "should this city grow or decline?")
3. Generate narrative descriptions from data (e.g., "Beshquahoek grew 50% → write a paragraph")
4. Create worldbuilding content (character backstories, cultural details)

**Previous experience:**
- Tried using OpenAI Codex to generate simulation code → inconsistent results, logic errors
- AI suggestions often sound plausible but contain subtle mathematical errors
- AI-generated content lacks the specific flavor of Saskan Lands (generic fantasy tropes)

**Project values:**
- Solarpunk themes (not standard D&D)
- Precise demographic modeling (formulas must be correct)
- Narrative coherence (events must make sense in context)
- Author control (creator remains authority, not algorithm)

## Decision

**AI will be used exclusively for narrative content generation FROM existing data**, NOT for simulation logic or decision-making.

**Permitted AI uses:**
- Generate prose descriptions from simulation outputs
- Suggest character names, cultural details (subject to author curation)
- Expand bullet-point notes into full paragraphs
- Create dialogue, flavor text, backstories

**Prohibited AI uses:**
- Write simulation formulas (logistic growth, migration flows)
- Make story decisions (which city should rebel? when does famine strike?)
- Generate historical events without data grounding
- Produce final content without human review/editing

**Workflow pattern:**
```
1. Simulation runs → generates data (Beshquahoek population 5k→15k, 1200-1250 AA)
2. Human writes prompt with context
3. AI generates prose from data
4. Human reviews, edits, curates
5. Approved text stored in database
```

**Integration approach:**
- AI as **assistant**, not **authority**
- AI as **amplifier**, not **replacement**
- AI as **draft generator**, not **final arbiter**

## Consequences

### Positive

- **Correctness guaranteed:** Simulation logic written/reviewed by human with 40 years development experience

- **Narrative consistency:** Author maintains creative control over tone, themes, unique elements

- **AI strengths leveraged:** Text generation, reducing busywork (expanding notes to paragraphs)

- **AI weaknesses avoided:** Mathematical errors, generic fantasy tropes, contextual misunderstanding

- **Transparency:** Clear separation between "computed facts" (simulation) and "authored story" (narrative)

- **Debugging:** When simulation produces weird results, root cause is in code (fixable), not opaque AI decision

- **Reproducibility:** Same inputs → same outputs (deterministic simulation with optional random seed)

### Negative

- **Less "magic":** Can't ask AI to "just handle everything" (this is actually positive—avoid illusion of capability)

- **Manual prompt engineering:** Each narrative generation requires crafting specific, contextualized prompts

- **Curation overhead:** Must review all AI-generated content (but avoids publishing errors)

- **Tool switching:** Simulation in Python, narrative generation via API calls (manageable)

### Neutral

- **AI model choice:** Claude vs. GPT-4 vs. others—depends on API cost, quality, availability
  - **Current preference:** Claude (better at following complex instructions, less generic fantasy)

## Implementation Notes

**Example: Simulation output → AI prompt → curated narrative**

**1. Simulation generates data:**
```python
# Simulation results
event = {
    'type': 'population_growth',
    'city': 'Beshquahoek',
    'year_start': 1200,
    'year_end': 1250,
    'pop_start': 5000,
    'pop_end': 15000,
    'causes': ['canal_completion', 'pilgrimage_increase', 'refugee_influx']
}
```

**2. Human writes contextualized prompt:**
```python
prompt = f"""
You are writing a historical chronicle of the Saskan Lands. Maintain a tone 
that is matter-of-fact, emphasizing survival and resilience (solarpunk themes).
Avoid fantasy clichés.

Context:
- Beshquahoek is a hot springs town that became a pilgrimage center
- The Fatunik faith worships Fatune (the Sun)
- This is a harsh world recovering from ecological catastrophe
- No pollinators exist; hand-pollination is required for crops

Write a 3-4 sentence historical summary of this event:

Between {event['year_start']}-{event['year_end']} AA, Beshquahoek's population 
grew from {event['pop_start']:,} to {event['pop_end']:,} people. Contributing 
factors: completion of new canal system, increased pilgrimage traffic, and 
refugees from northern famines.

Style: Concise, emphasizing infrastructure and collective effort.
"""
```

**3. AI generates draft:**
```
The completion of Beshquahoek's canal network in 1205 AA transformed the town 
from a modest rest stop into a hub of survival and faith. As pilgrims seeking 
Fatune's blessing filled the roads, the hot springs could support larger 
populations—but only through painstaking work. Refugees fleeing northern famines 
brought desperate hands for hand-pollination and canal maintenance, tripling the 
town's numbers within two generations. The waters ran clearer, but the labor 
grew heavier.
```

**4. Human reviews and edits:**
```
✅ "survival and faith" - good solarpunk tone
✅ "painstaking work" - emphasizes labor reality
✅ "desperate hands for hand-pollination" - unique detail
⚠️ "The waters ran clearer, but the labor grew heavier" - nice, keep

Final: Approved with minor tweaks
```

**5. Store in database:**
```python
conn.execute(
    "INSERT INTO event_descriptions (event_id, description, source) VALUES (?, ?, ?)",
    (event['id'], curated_text, 'ai_generated_human_curated')
)
```

**Example: Bulk narrative generation script**
```python
# scripts/generate_event_narratives.py
import anthropic
import sqlite3
from pathlib import Path

def generate_event_description(event_data: dict, context: dict) -> str:
    """Generate narrative description using Claude API."""
    client = anthropic.Anthropic()  # API key from env
    
    prompt = build_prompt(event_data, context)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def curate_descriptions(db_path: Path):
    """Interactive curation of AI-generated descriptions."""
    conn = sqlite3.connect(db_path)
    events = conn.execute(
        "SELECT * FROM events WHERE description IS NULL LIMIT 10"
    ).fetchall()
    
    for event in events:
        context = get_historical_context(conn, event)
        draft = generate_event_description(event, context)
        
        print(f"\n{'='*60}")
        print(f"Event: {event['name']} ({event['year']} AA)")
        print(f"{'='*60}")
        print(draft)
        print(f"{'='*60}")
        
        choice = input("Accept? (y/n/e for edit): ").lower()
        
        if choice == 'y':
            save_description(conn, event['id'], draft, 'ai_curated')
        elif choice == 'e':
            edited = input("Enter edited version:\n")
            save_description(conn, event['id'], edited, 'ai_edited')
        else:
            print("Skipped")
    
    conn.close()

# Usage:
# python scripts/generate_event_narratives.py
```

**Prompt template library:**
```python
# saskantinon_sim/ai/prompts.py
from string import Template

EVENT_DESCRIPTION = Template("""
You are chronicling the Saskan Lands, a post-catastrophe world recovering 
through resilience and collective effort (solarpunk themes). 

CRITICAL: Avoid these generic fantasy tropes:
- Epic chosen ones
- Ancient evils awakening  
- Magic solving problems
- Simple good vs evil

EMPHASIZE:
- Infrastructure and labor (canals, roads, hand-pollination)
- Multi-species cooperation/conflict (humans, rabbit-sints, terpins)
- Environmental recovery (pollinators slowly returning after 2000 years)
- Religious/cultural tensions (Fatunik sun-worshippers, river cults)

Event: $event_type in $location, year $year AA
Data: $data_summary

Write a $length description. Tone: $tone
""")

CHARACTER_BACKSTORY = Template("""
Create a backstory for $name, a $species living in $location around year $year AA.

Context:
- World recovering from catastrophe 2000+ years ago
- $location_details
- $species_details

Constraints:
- Grounded in setting (no magic, technology is steampunk-level)
- Shows how environment shapes character
- 2-3 paragraphs maximum

Character role: $role
""")

# Usage:
prompt = EVENT_DESCRIPTION.substitute(
    event_type="population_growth",
    location="Beshquahoek",
    year=1250,
    data_summary="5k→15k people, canal completion, refugee influx",
    length="3-4 sentences",
    tone="matter-of-fact, emphasizing collective effort"
)
```

**API cost management:**
```python
class AIBudget:
    """Track and limit AI API costs."""
    def __init__(self, max_tokens_per_session: int = 100_000):
        self.max_tokens = max_tokens_per_session
        self.used_tokens = 0
    
    def can_generate(self, estimated_tokens: int) -> bool:
        return (self.used_tokens + estimated_tokens) <= self.max_tokens
    
    def record_usage(self, actual_tokens: int):
        self.used_tokens += actual_tokens
        remaining = self.max_tokens - self.used_tokens
        print(f"Tokens used: {self.used_tokens}/{self.max_tokens} ({remaining} remaining)")
    
    def get_cost_estimate(self, model: str) -> float:
        """Estimate USD cost based on model pricing."""
        rates = {
            'claude-sonnet-4': 0.003 / 1000,  # per input token
            'gpt-4': 0.03 / 1000,
        }
        return self.used_tokens * rates.get(model, 0.01 / 1000)
```

## Alternatives Considered

**Let AI write simulation code:**
- Pro: Faster initial development
- Con: Introduces bugs, logic errors, lacks understanding of domain
- **Rejected:** Human expertise in software architecture, demographics more valuable

**Let AI generate events:**
- Pro: Creative, surprising
- Con: Breaks narrative coherence, introduces lore conflicts, generic outputs
- **Rejected:** Events must be grounded in simulation + author vision

**No AI at all:**
- Pro: Total human control
- Con: Writing 2000 years of event descriptions is tedious busywork
- **Rejected:** AI good at reducing grunt work; use it for that

**Local AI models (LLaMA, Mistral):**
- Pro: No API costs, privacy, unlimited usage
- Con: Lower quality, requires GPU, more setup
- **Deferred:** Start with API (Claude/GPT-4); migrate to local if costs become issue

**Fine-tuned models:**
- Pro: Better at Saskan-specific style and lore
- Con: Requires large dataset, training expertise, ongoing maintenance
- **Deferred:** Premature; prompt engineering sufficient for now

## Testing Strategy

**Validate AI outputs:**
```python
def validate_ai_description(description: str, event_data: dict) -> list[str]:
    """Check AI output for common issues."""
    issues = []
    
    # Check for generic fantasy tropes
    tropes = ['chosen one', 'ancient evil', 'dark lord', 'magical', 'prophecy']
    for trope in tropes:
        if trope in description.lower():
            issues.append(f"Contains fantasy trope: '{trope}'")
    
    # Check for factual consistency
    if event_data['year'] not in description:
        issues.append("Missing year/date reference")
    
    # Check for length
    if len(description) > 1000:
        issues.append("Too long (>1000 chars)")
    
    return issues

# Usage in curation workflow
issues = validate_ai_description(draft, event)
if issues:
    print("⚠️ Issues detected:")
    for issue in issues:
        print(f"  - {issue}")
```

## Migration Path

If currently using AI for simulation logic:

1. **Audit existing AI usage:** Identify where AI makes decisions vs. generates text
2. **Extract logic:** Convert AI-generated code into human-written, tested functions
3. **Create prompt library:** Formalize narrative generation prompts
4. **Establish curation workflow:** Human review before content enters canon
5. **Document boundary:** Clear policy on what AI can/can't do

## References

- Anthropic Claude API: https://docs.anthropic.com/
- Prompt engineering guide: https://www.promptingguide.ai/
- AI-assisted writing best practices: https://every.to/chain-of-thought/how-to-use-ai-to-do-stuff-an-opinionated-guide
