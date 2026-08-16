# Internal Thought System (Phase 4.3.4)

## Overview

The InternalThought system is the canonical architecture for generating internally originated semantic content in Gordon's Default Network.

### Architecture Role

```
Internal Context
        │
        ▼
Internal Episode
        │
        ▼
Thought Generator
        │
        ▼
InternalThought
        │
        ├────────► Reflection
        │
        ├────────► Simulation
        │
        ├────────► Narrative
        │
        ├────────► Identity
        │
        ├────────► Memory
        │
        ├────────► Prediction
        │
        ├────────► Learning
        │
        └────────► Executive (optional)
```

Thought Generation never executes behaviour. It produces semantic candidates.

### Core Principles

- **Bounded**: All thoughts are bounded by explicit limits
- **Immutable**: Thoughts are deeply frozen for safety and determinism  
- **Revisioned**: Immutable revision history is preserved
- **Explainable**: Provenance, confidence, and relationships are documented
- **Typed**: Specific kinds determine interpretation
- **Provenance-aware**: Every thought has complete origin tracking

## Components

### InternalThought

The core semantic object representing one internally generated cognitive product.

```python
from gordon_system.src.agent.networks.default.internal_thought import InternalThought, RelationshipKind

thought = InternalThought.new(
    concept="test_concept",
    purpose="test_purpose", 
    thought_kind="reflection",
    originating_episode_id="episode:123",
    originating_context_version="v1.0"
)

# Add relationships
thought_with_rel = thought.with_relationship(RelationshipKind.SUPPORTS, "other:thought")
```

### ThoughtFactory

Constructs validated thoughts:

```python
from gordon_system.src.agent.networks.default.internal_thought import create_factory

factory = create_factory()

success, thought = factory.new_thought(
    concept="test",
    purpose="purpose",
    thought_kind="reflection",
)
```

### ThoughtGenerator

Generates thoughts from context:

```python
from gordon_system.src.agent.networks.default.internal_thought import create_generator

generator = create_generator()

thoughts, errors = generator.generate_from_context({
    "context_id": "ctx:123",
    "version": "v1.0",
    "active_focus_strength": 0.7,
})
```

### ThoughtAssessment

Quality evaluation with metrics:

```python
from gordon_system.src.agent.networks.default.internal_thought import InternalThoughtMetrics

metrics = InternalThoughtMetrics(
    confidence=0.7,
    novelty=0.3,
    expected_utility=0.5,
)
```

## Thought Kinds

- `reflection`: Self-referential processing
- `hypothesis`: Proposed explanation awaiting validation
- `prediction`: Expected outcome based on models  
- `simulation`: Scenario exploration
- `counterfactual`: Alternative scenario analysis
- `evaluation`: Assessment of validity or utility
- `association`: Concept connections
- `question`: Unknowns requiring answers
- `goal`: Desired state representation
- `integration`: Disparate information combination

## Lifecycle States

- `generated` → `validated` → `ready` → `active`
- Terminal: `superseded`, `archived`, `discarded`, `invalid`

## Relationships

Types: `supports`, `extends`, `refines`, `contradicts`, `invalidates`, etc.

## Serialization

```python
# To dictionary
data = thought.to_dict()

# From dictionary  
restored = InternalThought.from_dict(data)

# To JSON
json_str = InternalThoughtSerializer.to_json(thought)
```

## Architectural Invariants

- **THOUGHT-INV-001**: Thoughts are semantic objects (not language)
- **THOUGHT-INV-002**: Thoughts are immutable (deeply frozen)
- **THOUGHT-INV-003**: Thoughts never execute behaviour
- **THOUGHT-INV-004**: Thought generation never invokes Executive
- **THOUGHT-INV-005**: Thought generation never schedules Threads
- **THOUGHT-INV-006**: Thoughts belong exclusively to the Default Network
- **THOUGHT-INV-007**: Every thought has provenance
- **THOUGHT-INV-008**: Every thought belongs to an InternalEpisode
- **THOUGHT-INV-009**: Thoughts remain bounded
- **THOUGHT-INV-010**: Relationships remain typed

## Anti-Patterns

Do NOT implement:

- Free-form string thoughts
- Language-only thoughts  
- Runtime commands
- Execution requests
- Scheduler integration
- Thread ownership
- Loop ownership
- Unlimited graphs
- Mutable thoughts
- Anonymous thoughts

## Testing

Run tests with pytest:

```bash
pytest gordon_system/tests/test_internal_thought_4_3_4.py -v
```

## Glossary

| Term | Definition |
|------|------------|
| **Thought** | Bounded semantic object representing one internally generated cognitive product |
| **Generation** | Process of producing thoughts from context (never executes) |
| **Assessment** | Quality evaluation with confidence, novelty, utility metrics |
| **Relationship** | Typed semantic connection between thoughts (supports, contradicts, etc.) |
| **Lifecycle** | Semantic state transitions (generated → validated → active → ...) |
| **Revision** | Immutable update preserving original provenance |

## Package Structure

```
internal_thought/
├── __init__.py           # Package exports
├── thought.py            # Core InternalThought model
├── enums.py              # Kinds, states, relationships
├── factory.py            # ThoughtFactory (construction)
├── generator.py          # ThoughtGenerator (generation)
├── assessment/           # Assessment metrics
│   ├── __init__.py
│   └── metrics.py
├── state/                # State snapshots and transitions
│   ├── __init__.py
│   ├── snapshot.py
│   ├── transition.py
│   └── history.py
├── relationships/        # Relationship graph
│   ├── __init__.py
│   └── kind.py
├── revision/             # Revision tracking
│   ├── __init__.py
│   └── revision.py
├── serialization/        # Serialization utilities
│   ├── __init__.py
│   ├── serializer.py
│   └── validator.py
├── registry/             # Bounded registry
│   ├── __init__.py
│   ├── registry.py
│   └── history.py
└── validation/           # Validation functions
    ├── __init__.py
    └── validation.py
```

## Version

Current: 1.0.0 (Phase 4.3.4)