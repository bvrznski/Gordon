# Gordon Phase 5.7.5-I: Presence Engine - Implementation Report
# ===============================================================================
"""
Canonical Presence Engine for conscious accessibility.

This document describes the implementation of Gordon's canonical Presence Engine,
the subsystem that answers "What is consciously present right now?"

The Presence Engine determines which portions of current conscious organization
remain actively accessible. It represents accessibility, not truth, importance,
attention, or salience.
"""

# ==============================================================================
# 1. ARCHITECTURAL OVERVIEW
# ==============================================================================

## 1.1 Purpose
The Presence Engine is responsible for determining conscious accessibility:
- What content becomes consciously available from the Experiential Field
- How long content remains accessible (bounded persistence)
- When content withdraws from presence (gradual fading)

## 1.2 Key Distinctions

| NOT Part of Presence | Part of Other Systems |
|---------------------|----------------------|
| Truth assessment | Reasoning, Verification |
| Importance rating | Intentional Context |
| Attention allocation | Focus/Attention systems |
| Salience computation | Perception salience |
| Memory storage | Long-term memory |

## 1.3 Core Responsibilities

**YES (Presence owns):**
- conscious presence
- admission policies
- persistence duration
- fading transitions
- accessibility determination
- presence snapshots

**NO (Not Presence's responsibility):**
- reasoning about content
- planning with content
- executing actions

# ==============================================================================
# 2. LIFECYCLE STATES
# ==============================================================================

## 2.1 State Transitions

```
candidate → admitted → active → weakening → fading → withdrawn
                              ↑          ↓
                            suspended ←──┘
```

## 2.2 State Definitions

| State | Description |
|-------|-------------|
| candidate | Content proposed but not yet admitted |
| admitted | Admitted, awaiting activation |
| active | Consciously accessible |
| weakening | Fading transition started |
| fading | Withdrawing from presence |
| suspended | Temporarily inactive (can resume) |
| withdrawn | No longer consciously accessible |

# ==============================================================================
# 3. PACKAGE STRUCTURE
# ==============================================================================

```
src/agent/capabilities/consciousness/presence/
├── __init__.py      # Package exports
├── constants.py     # State and policy constants
├── state.py         # PresenceItem, PresenceStateSnapshot
├── exceptions.py    # Error types
├── admission.py     # AdmissionAuthority, AdmissionPolicy
├── persistence.py   # PersistenceManager, PersistencePolicy
├── fading.py        # FadingManager, FadePolicy
├── transition.py    # PresenceTransition, TransitionBatch
├── snapshot.py      # PresenceSnapshot (immutable)
├── diagnostics.py   # Diagnostics, Metrics, HealthStatus
├── integrity.py     # IntegrityEnforcer
└── engine.py        # Canonical PresenceEngine
```

# ==============================================================================
# 4. API REFERENCE
# ==============================================================================

## 4.1 Core Engine

```python
engine = PresenceEngine()

# Propose a candidate from Experiential Field, Intentional Context, etc.
success, reason = engine.propose_candidate(
    item_id="item-1",
    source_id="source-1",
)

# Activate an admitted item into conscious presence
success, reason = engine.activate_item(item_id="item-1")

# Get current presence snapshot (immutable)
snapshot = engine.get_snapshot()

# Check fading progress
advanced, withdrawn = engine.check_fading_progress()
```

## 4.2 Snapshot API

```python
snapshot = engine.get_snapshot()

# Access item counts
active_count = snapshot.active_count
fading_count = snapshot.fading_count

# Access source IDs
sources = snapshot.source_ids

# Check totals
total_present = snapshot.total_present
total_active = snapshot.total_active
```

## 4.3 Metrics and Health

```python
metrics = engine.metrics  # admitted_total, active_count, etc.
health = engine.health    # can_admit, can_withdraw, etc.
```

# ==============================================================================
# 5. POLICY CONFIGURATION
# ==============================================================================

## 5.1 Admission Policy

```python
AdmissionPolicy(
    source_validation=True,     # Validate source identity
    freshness_check=True,       # Check content freshness
    capacity_limit=100,         # Max concurrent active items
    max_admitted=200,           # Max admitted but not active
)
```

## 5.2 Persistence Policy

```python
PersistencePolicy(
    default_lifetime_seconds=3600.0,   # Content lifetime (1 hour)
    grace_period_seconds=300.0,        # Grace before fading (5 min)
    reuse_expired=True,                # Can re-admit expired content
)
```

## 5.3 Fade Policy

```python
FadePolicy(
    weakening_duration_seconds=60.0,   # Time in weakening state
    fade_duration_seconds=30.0,        # Time in fading state
    grace_period_seconds=300.0,        # Grace before first fade
)
```

# ==============================================================================
# 6. INTEGRATION POINTS
# ==============================================================================

## 6.1 Experiential Field
- Proposes candidate content for conscious presence
- Provides freshness timestamps for admission checks
- Supplies source identity for provenance tracking

## 6.2 Intentional Context
- Specifies which items should be activated into presence
- May request withdrawal of specific items
- Provides target information for item classification

## 6.3 Temporal Context
- Provides timing information for fading decisions
- Supplies generation numbers for replayability
- Maintains continuity window for state transitions

# ==============================================================================
# 7. CONCURRENCY MODEL
# ==============================================================================

- **Readers**: Multiple readers can access snapshots concurrently
- **Publications**: Immutable snapshot publication (thread-safe)
- **Transitions**: Deterministic, atomic updates to presence state
- **Updates**: Single writer controls all state changes

# ==============================================================================
# 8. TESTING
# ==============================================================================

## 8.1 Unit Tests

```bash
pytest tests/test_presence_engine_foundation.py -v
```

## 8.2 Test Coverage

- State transitions (all valid paths)
- Admission policy enforcement
- Persistence expiration
- Fading progression
- Snapshot immutability
- Deterministic publication

# ==============================================================================
# 9. INTEGRITY VERIFICATION
# ==============================================================================

The IntegrityEnforcer validates:

1. **State Consistency**: States must be from the valid set
2. **Transition Validity**: Only allowed transitions permitted
3. **Capacity Bounds**: Active count never exceeds max capacity
4. **Fading Progress**: Fading follows correct sequence

```python
integrity = IntegrityEnforcer()

# Validate transition
result = integrity.validate_transition(from_state, to_state)

# Validate snapshot
result = integrity.validate_snapshot_integrity(
    active_count=10,
    fading_count=5,
    total_items=20,
)
```

# ==============================================================================
# 10. DIAGNOSTICS & OBSERVABILITY
# ==============================================================================

## 10.1 Metrics

```python
{
    "admitted_total": int,      # Total items admitted
    "withdrawn_total": int,     # Total items withdrawn
    "active_count": int,        # Currently active items
    "fading_count": int,        # Currently fading items
    "failure_count": int,       # Admission failures
}
```

## 10.2 Health Status

```python
{
    "can_admit": bool,
    "can_withdraw": bool,
    "can_transition": bool,
}
```

# ==============================================================================
# 11. ARCHITECTURAL PRINCIPLES
# ==============================================================================

1. **Engineering Model**: Implements an accessibility model, not phenomenal awareness
2. **Deterministic Transitions**: All state changes are predictable and reproducible
3. **Bounded Persistence**: Content never persists indefinitely
4. **Immutable Snapshots**: Published state is never modified after creation
5. **Provenance Preservation**: Source and contribution information maintained
6. **Separation of Concerns**: Strictly separated from attention, salience, reasoning

# ==============================================================================
# 12. CERTIFICATION STATUS
# ==============================================================================

**Status**: IMPLEMENTATION_COMPLETE

The Presence Engine implements all canonical responsibilities:

- [x] One Presence Engine (canonical)
- [x] One admission authority
- [x] Immutable snapshots
- [x] Explicit lifecycle states
- [x] Deterministic publication
- [x] Bounded persistence
- [x] Deterministic fading
- [x] Provenance preservation
- [x] Separation from attention/salience/reasoning/planning

# ==============================================================================
# 13. FUTURE ENHANCEMENTS (Not for Phase 5.7.5)
# ==============================================================================

The following are explicitly OUT OF SCOPE:

- **Phase 5.7.6 - Perspective Engine**: Not to be implemented
- **Phase 5.7.7 - Situated World Engine**: Not to be implemented
- **Phase 5.7.8 - Conscious Integration Engine**: Not to be implemented

# ==============================================================================
# END OF PRESENCE ENGINE IMPLEMENTATION REPORT
# ==============================================================================