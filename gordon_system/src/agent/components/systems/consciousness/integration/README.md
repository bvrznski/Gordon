# Gordon Conscious Integration - Phase 5.7.8-I

## Overview

The **Conscious Integration** layer coordinates committed immutable references from
Gordon's consciousness engines into a coherent, bounded, deterministic,
agent-relative conscious-context snapshot.

### What It Does

- Coordinates committed references from: Experiential Field, Intentional Context,
  Temporal Context, Presence, Awareness, Perspective, Situated World
- Validates cross-engine compatibility and generation alignment
- Publishes atomic composite snapshots with monotonic generations
- Provides bounded health and diagnostics aggregation
- Supports multiple consistency levels and degraded operation modes

### What It Does NOT Do

- **Does not** own engine internals or internal semantics
- **Does not** reason about conflicts between engine outputs
- **Does not** authorize actions
- **Does not** determine truth, trust, or validity of engine content
- **Does not** replace any engine's responsibility for its own state

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Composite Conscious Snapshot              │
│                    (Atomic Publication Point)               │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┬──────────┬──────────┐
        ▼          ▼          ▼          ▼          ▼          ▼
   Field     Intentional  Temporal    Presence   Awareness   Persp.     World
   (Field)    (Intent)    (Time)      (Now)       (Access)  (Self)     (Env)
        │          │          │          │          │          │          │
        └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
                              Integration Coordinator
```

## Key Components

### Types (`types.py`)

- `EngineSnapshotReference`: Immutable reference to committed engine state
- `EngineGenerationMap`: Tracks per-engine generation numbers
- `CompositeSnapshot`: The complete conscious context snapshot
- `IntegrationTransition`: Records of transition metadata
- `UnresolvedReference`: Explicit handling of missing or external references

### Dependencies (`dependencies.py`)

- `EngineDependencyOrder`: Canonical dependency ordering for deterministic processing
- `DependencyGraph`: Validates no cycles exist between engines

### Validation (`validation.py`)

- `CrossEngineValidator`: Checks cross-engine invariants:
  - Perspective/World compatibility
  - Presence/Awareness alignment  
  - Temporal/Field generation alignment
  - Intentional target resolution status

### Composition (`composition.py`)

- `CompositeSnapshotBuilder`: Builds composite snapshots from engine references
- Handles generation alignment and consistency level enforcement

### Coordinator (`coordinator.py`)

- `IntegrationCoordinator`: Orchestrates complete integration transitions
- Coordinates atomic publication with rollback on failure

### Health & Diagnostics (`health.py`, `diagnostics.py`)

- Bounded health aggregation (no full snapshots exposed)
- Operational diagnostics without exposing private content
- Degradation mode tracking and reporting

## Consistency Levels

```python
CONSISTENCY_LEVEL_STRICT = "strict"
    - All required engines must be available
    - No generation lag allowed between engines
    - Full invariant validation required

CONSISTENCY_LEVEL_BOUNDED_STALENESS = "bounded_staleness"  
    - Allows some generation lag (within policy)
    - May publish with partial engine availability
    
CONSISTENCY_LEVEL_DEGRADED_COMPATIBLE = "degraded_compatible"
    - Accepts degraded states explicitly
    - Must indicate degradation mode in snapshot

CONSISTENCY_LEVEL_PARTIAL_OPTIONAL = "partial_optional"
    - Allows optional engines to be unavailable
    - Required engines must be ready
```

## Engine Dependency Order

```python
# Canonical processing order (deterministic):
1. experiential_field      # Base field of current content
2. intentional_context     # Directedness over the field  
3. temporal_context        # Retention/presentation/protention
4. presence                # Admission/maintenance state
5. awareness               # Explicit accessibility state
6. perspective             # Agent-relative observer state
7. situated_world          # Current environment relative to self
8. consciousness_integration  # Composite publication
```

## Integration Flow

1. **Trigger**: Request for context transition (external or engine update)
2. **Collection**: Gather committed engine snapshots/references
3. **Validation**:
   - Check required engines available
   - Validate generation alignment
   - Check cross-engine invariants
4. **Composition**: Build composite snapshot with new generation
5. **Atomic Publication**: Either publish new snapshot or retain previous

## Usage Example

```python
from gordon_system.src.agent.capabilities.consciousness.integration import (
    IntegrationCoordinator,
    CompositeSnapshotBuilder,
    CONSISTENCY_LEVEL_STRICT,
)

# Initialize coordinator
coordinator = IntegrationCoordinator(
    consistency_level=CONSISTENCY_LEVEL_STRICT
)

# Collect engine references (each engine provides committed snapshot reference)
engine_refs = {
    "experiential_field": field_ref,
    "intentional_context": intent_ref,
    # ... other engines ...
}

# Request integration transition
result, new_snapshot = coordinator.integrate(
    request=IntegrationRequest(
        context_id="user-session-001",
        previous_generation=current_gen,
    ),
    engine_refs=engine_refs,
    previous_snapshot=previous_composite,
)

if result.succeeded:
    # Use new_snapshot for next cycle
else:
    # Revert to previous snapshot, handle error
```

## Safety Guarantees

1. **Atomic Publication**: Composite transition is all-or-nothing
2. **Generation Monotonicity**: New generation = previous + 1
3. **No Mutation of Engine State**: Integration only reads committed references
4. **Bounded Health/Diagnostics**: No full snapshots in health/diagnostic outputs
5. **Degradation Explicitness**: Degraded states are clearly marked
6. **Cross-Engine Validation**: Invalid combinations cannot become current context

## Lifecycle States

```
CONSTRUCTED → CONFIGURED → INITIALIZED → STARTING → READY → ACTIVE
                  ↓                        ↘              ↑
               STOPPED                     FAILED      TRANSITIONING
                                                      ↓    ↑
                                                   DEGRADED
```

## Testing

Run tests:
```bash
python -m pytest gordon_system/tests/test_integration_*.py -v
```

## Documentation

- Phase 5.7.1-A/R/I: Consciousness Architecture
- Phase 5.7.2-A/R/I: Experiential Field Construction  
- Phase 5.7.3-A/R/I: Intentional Context
- Phase 5.7.4-A/R/I: Temporal Context
- Phase 5.7.5-A/R/I: Presence & Awareness
- Phase 5.7.6-A/R/I: Perspective & Self-Reference
- Phase 5.7.7-A/R/I: Situated World