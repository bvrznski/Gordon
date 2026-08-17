# Gordon Consciousness Capability

**Phase:** 5.7.1-I  
**Status:** Canonical Implementation  
**Version:** 5.7.1-I  

---

## Overview

The Consciousness capability is a first-class Gordon capability parallel to Cognition,
Agency, and Action. It owns the organization and controlled publication of the bounded,
agent-relative current context.

### Architectural Position

```
Perception ───────────────┐
Memory ───────────────────┤
Working Memory ───────────┤
Workspace ────────────────┤
Attention ────────────────┤
Salience ─────────────────┤
Personality ──────────────┤
Motivation ───────────────┤
Cognition Proposals ──────┤
                          ▼
                    Consciousness
                          │
               ┌──────────┼──────────┐
               ▼          ▼          ▼
            Cognition   Agency      Action
```

This diagram represents architectural contribution and consumption relationships.
Consciousness does not require a strictly linear pipeline.

---

## Core Responsibilities

The Consciousness capability owns:

- **Canonical current context organization** - Agent-relative experiential field
- **Context identity management** - Stable identifiers for contexts and generations  
- **Boundary validation** - Contributions and projections must pass validation
- **Transition authority** - Atomic commits of new context generations
- **Registration systems** - Sources and extensions with lifecycle control

The Consciousness capability does NOT own:

- Global availability (Workspace Network)
- Persistence (Memory System)  
- Reasoning/interpretation (Cognition)
- Decision making (Agency)
- Action execution (Action)

---

## Package Structure

```
src/agent/capabilities/consciousness/
├── __init__.py         # Package initialization and exports
├── config.py           # Configuration types and validation
├── constants.py        # Enums for states, kinds, modes
├── exceptions.py       # Typed exception hierarchy
├── types.py            # Core type definitions (IDs, classifications)
├── identities.py       # Identity classes (context, source, extension)
├── contracts.py        # Public data structures and contracts
├── registry.py         # Source and extension registries
└── facade.py           # Public API facade ( ConsciousnessFacade )
```

Future phase packages (5.7.2-5.7.8) will extend this structure.

---

## Public API

### ConsciousnessFacade

The primary public interface for the Consciousness capability.

```python
from gordon.agent.capabilities.consciousness import (
    ConsciousnessFacade,
    SourceDescriptor,
    ExtensionDescriptor,
)

# Initialize the facade
facade = ConsciousnessFacade()
success, error = facade.initialize()

# Start accepting contributions
success, error = facade.start()

# Register a source
descriptor = SourceDescriptor(
    source_id="my-source",
    source_kind="workspace"
)
success, error = facade.register_source(descriptor)

# Submit a contribution
from gordon.agent.capabilities.consciousness import ContributionEnvelope

contribution = ContributionEnvelope(
    source_id="my-source",
    contribution_kind="workspace_candidate",
    payload_reference="ref://content/123"
)
result = facade.submit_contribution(contribution)

# Query current context
snapshot = facade.get_current_context()
```

---

## Key Concepts

### Context Snapshots

Immutable representations of the current agent-relative experiential state.

```python
from gordon.agent.capabilities.consciousness import CurrentContextSnapshot

snapshot = CurrentContextSnapshot.initial()
print(f"Generation: {snapshot.generation}")
print(f"Context ID: {snapshot.context_id}")
```

### Contributions and Projections

Contributions are proposals for consideration; projections expose bounded views.

```python
# Contribution - proposes something for consideration
contribution = ContributionEnvelope(
    source_id="source-1",
    contribution_kind="perceptual_projection",
)

# Projection - exposes a view from another system  
projection = ProjectionEnvelope(
    source_id="source-2", 
    projection_kind="cognitive_proposal",
)
```

### Transitions

Atomic commits of new context generations.

```python
from gordon.agent.capabilities.consciousness import TransitionResult

result: TransitionResult = facade.request_transition()
if result.succeeded:
    print(f"New generation: {result.new_generation}")
else:
    print(f"Failed: {result.failure_reason}")
```

---

## State Boundaries

### External Systems May NOT:

- Mutate Consciousness state directly
- Access private registries or queues
- Read full extension payloads through Consciousness
- Infer truth/trust/awareness from context membership

### External Systems Should:

- Submit contributions via `submit_contribution()`
- Expose projections via `submit_projection()`
- Query current context via `get_current_context()`
- Request transitions via `request_transition()`

---

## Error Handling

The capability uses typed exceptions for precise error handling.

```python
from gordon.agent.capabilities.consciousness import (
    UnknownSource,
    DuplicateSource,
    InvalidContribution,
)

try:
    facade.submit_contribution(contribution)
except UnknownSource as e:
    # Source not registered - register it first
    pass
except InvalidContribution as e:
    # Contribution was malformed or expired
    pass
```

---

## Integration Points

### Workspace Network
- Outputs workspace candidates as contributions to Consciousness
- Receives current context snapshot for broadcast decisions

### Perception System  
- Outputs integrated percepts as projections to Consciousness

### Memory System
- May expose working memory activation states as contributions

### Cognition
- Consumes current context snapshot for reasoning/interpretation
- May submit interpretations as contributions

---

## Configuration

Configuration is validated at construction time and immutable after creation.

```python
from gordon.agent.capabilities.consciousness import (
    ConsciousnessConfiguration,
)

# Default configuration
config = ConsciousnessConfiguration.default()

# Strict configuration with conservative limits
config = ConsciousnessConfiguration.strict()
```

---

## Testing

Tests are located in `tests/test_consciousness*.py`.

Run tests with:
```bash
pytest gordon_system/tests/test_consciousness*.py -v
```

---

## Documentation

Additional documentation:

- Architecture.md - Complete architecture overview
- Ownership.md - Capability ownership model
- Public-API.md - Detailed API reference
- Contracts.md - Contract specifications
- Identity-Model.md - Identity and generation semantics

---

## Phase Roadmap

| Phase | Status |
|-------|--------|
| 5.7.1-I (Canonical) | **Implemented** - Foundation capability |
| 5.7.2 | Planned - Experiential field construction |
| 5.7.3 | Planned - Intentional context |
| 5.7.4 | Planned - Temporal context |
| 5.7.5 | Planned - Presence & awareness |
| 5.7.6 | Planned - Perspective & self-reference |
| 5.7.7 | Planned - Situated world |
| 5.7.8 | Planned - Conscious integration |

---

*For questions or issues, consult the architecture team.*