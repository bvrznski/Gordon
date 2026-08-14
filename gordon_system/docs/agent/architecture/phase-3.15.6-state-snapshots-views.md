# State Snapshots and Views Architecture - Phase 3.15.6

## Executive Summary

Phase 3.15.6 establishes the canonical architecture for state snapshots and views throughout the Gordon Core.

### Objective

Design and implement the canonical architecture governing state snapshots and state views throughout the Gordon Core.

This phase extends:

* Phase 3.15.1 — Core State Foundations
* Phase 3.15.2 — State Identity, Scope & Ownership
* Phase 3.15.3 — Immutable & Mutable State Semantics
* Phase 3.15.4 — Runtime State Hierarchy
* Phase 3.15.5 — State Transitions & Transition Validation

**ONE CANONICAL ARCHITECTURE**: Snapshots and views are immutable observational artifacts. They are never mutable runtime state authorities.

---

## Snapshot Architecture

### Core Principles

Snapshots represent the condition of runtime state at a specific version and generation.

Every snapshot shall preserve:

| Field | Description |
|-------|-------------|
| `snapshot_id` | Unique identifier for this snapshot instance |
| `source_state_id` | Identity of the source state aggregate |
| `aggregate_identity` | Aggregate to which source belongs |
| `owner_identity` | Owner authority at capture time (for reference) |
| `runtime_identity` | Runtime that owned the state |
| `boot_session_identity` | Boot session during capture |
| `version` | Source version number |
| `generation` | Source generation number |
| `capture_timestamp` | When snapshot was taken (UTC) |
| `consistency_class` | Consistency guarantees declared |
| `completeness_class` | Completeness level declared |
| `schema_version` | Schema version for serialization compatibility |
| `provenance` | Origin and history tracking |

**IMMUTABILITY**: Snapshots never expose mutable runtime objects. They are frozen at a specific version.

### Snapshot Classifications

#### Canonical Snapshot Kinds

| Kind | Domain | Purpose |
|------|--------|---------|
| `RUNTIME` | Runtime | Runtime state at version |
| `AGGREGATE` | Core | Entire aggregate state at version |
| `COMPONENT` | Component | Component instance state |
| `SERVICE` | Service | Service instance state |
| `RESOURCE` | Resource | Resource allocation state |
| `STREAM` | Stream | Stream processing state |
| `TRANSACTION` | Transaction | Transaction state |
| `HEALTH` | Health | Health condition at version |
| `READINESS` | Readiness | Readiness availability |
| `ADMISSION` | Admission | Admission decision state |
| `RECOVERY` | Recovery | Recovery process state |
| `SHUTDOWN` | Shutdown | Shutdown procedure state |
| `HIERARCHY` | Runtime | Hierarchy structure snapshot |
| `DIAGNOSTIC` | Runtime | Diagnostic information |

### Consistency Classifications

| Classification | Guarantee |
|----------------|-----------|
| ATOMIC | Snapshot captured atomically (all fields consistent) |
| TRANSACTIONAL | Reflects a committed transaction |
| VERSION_CONSISTENT | All fields from same version |
| EVENTUALLY_CONSISTENT | May not reflect most recent write |
| BEST_EFFORT | Best attempt, no consistency guarantees |
| PARTIAL | Incomplete snapshot (some fields missing) |
| UNKNOWN | Unknown/undetermined |

### Completeness Classifications

| Classification | Description |
|----------------|-------------|
| COMPLETE | All state fields included |
| PROJECTION | Only selected fields included (view) |
| METADATA_ONLY | Only metadata, no actual values |
| INCREMENTAL | Changed fields since last snapshot |
| DIFFERENTIAL | Changes relative to another snapshot |

### Snapshot Lifecycle Stages

| Stage | Description |
|-------|-------------|
| REQUESTED | Snapshot request received |
| CREATED | Snapshot has been created |
| VALIDATED | Snapshot validation completed |
| PUBLISHED | Published to observers |
| STORED | Persisted (if eligible) |
| ARCHIVED | Archived for long-term storage |
| EXPIRED | Has exceeded maximum age |
| DISCARDED | Invalid or no longer needed |

---

## View Architecture

### Core Principles

Views represent projections over runtime state or a snapshot.

Views shall support:

| Use Case | Description |
|----------|-------------|
| Public API | Expose information to external consumers |
| Diagnostics | Debugging and troubleshooting |
| Monitoring | Health and performance tracking |
| Health Aggregation | Combine health conditions |
| Readiness Aggregation | Determine availability |
| Admission Decisions | Evaluate eligibility |
| Reporting | Generate summaries and reports |

**IMMUTABILITY**: Views are never mutable runtime state.

### View Classifications

| Kind | Visibility | Purpose |
|------|------------|---------|
| PUBLIC | External | Limited information for external consumers |
| INTERNAL | Subsystem | Detailed info within subsystem boundaries |
| DIAGNOSTIC | Control | Debug and troubleshooting data |
| ADMINISTRATIVE | Management | System management operations |
| HEALTH | Observability | Health status information |
| READINESS | Admission | Availability decisions |
| RESOURCE | Operations | Resource state details |
| LIFECYCLE | Internal | State machine progression |
| SECURITY | Audit | Security-relevant information |
| OBSERVABILITY | Monitoring | Metrics and telemetry data |
| PROJECTION | Custom | Application-specific projection |
| SUMMARY | General | High-level overview |
| DETAILED | Technical | Complete state representation |

### Projection Rules

Every view shall explicitly define:

1. **Source State**: `source_state_id`, `source_version`
2. **Projection Identity**: What kind of view is this?
3. **Included Fields**: What fields to include (empty = all)
4. **Excluded Fields**: What fields to exclude
5. **Derived Fields**: Computed values added
6. **Redacted Fields**: Sensitive data removed/masked
7. **Consumer Scope**: Who can see this projection?
8. **Visibility Policy**: When it's visible

**NO IMPLICIT PROJECTIONS**: All projections must be explicitly specified.

---

## Redaction Mechanisms

### Supported Redactions

| Field Type | Redaction Strategy |
|------------|-------------------|
| Secrets | Replace with "******" or similar |
| Credentials | Remove entirely |
| Security-sensitive metadata | Mask identifying details |
| Private runtime info | Anonymize where possible |
| Implementation details | Hide from public views |

### Redaction Modes

| Mode | Behavior |
|------|----------|
| MASK | Replace value with placeholder |
| REMOVE | Omit field entirely |
| CUSTOM | Subsystem-specific strategy |

Redaction policies shall be deterministic - same input always produces same output.

---

## Factory API

### SnapshotFactory

The canonical entry point for creating snapshots:

```python
factory = SnapshotFactory()

# Create typed snapshots
snapshot = factory.create_runtime_snapshot(...)
snapshot = factory.create_aggregate_snapshot(...)
snapshot = factory.create_component_snapshot(...)
snapshot = factory.create_service_snapshot(...)
snapshot = factory.create_health_snapshot(...)
snapshot = factory.create_readiness_snapshot(...)
# ... and more specific kinds
```

### ViewFactory

The canonical entry point for creating views:

```python
factory = ViewFactory()

# Create typed views
view = factory.create_public_view(...)
view = factory.create_internal_view(...)
view = factory.create_diagnostic_view(...)
view = factory.create_health_view(...)
view = factory.create_readiness_view(...)
# ... and more specific kinds
```

---

## Validation

### Snapshot Validator

Validates:

- Identity format (must start with `snap_`)
- Source identification complete
- Version information present
- Consistency classification valid
- Completeness classification valid
- Lifecycle stage valid

### View Validator

Validates:

- Identity format (must start with `view_`)
- Source state ID present
- Projection identity specified

---

## Diagnostics API

```python
@dataclass(frozen=True)
class SnapshotDiagnostics:
    snapshot_count: int = 0              # Total snapshots created
    active_snapshots: int = 0            # Currently valid snapshots
    view_count: int = 0                  # Total views created
    active_views: int = 0                # Currently valid views
    projection_statistics: Dict[str, int] = {}  # View type counts
    consistency_classifications: Dict[str, int] = {}  # Consistency stats
    completeness_classifications: Dict[str, int] = {}  # Completeness stats
    validation_failures: int = 0         # Validation failures
    validation_successes: int = 0        # Validation successes
```

---

## Architecture Invariants

### Snapshot Invariants

| Invariant | Description |
|-----------|-------------|
| SNAP-001 | Snapshot is immutable once created |
| SNAP-002 | Snapshot does not become a second mutable authority |
| SNAP-003 | Snapshot identifies source state, version, and generation |

### View Invariants

| Invariant | Description |
|-----------|-------------|
| VIEW-001 | View is immutable once created |
| VIEW-002 | View does not become a hidden cache of mutable truth |
| VIEW-003 | View identifies source state, version, and projection |

### Runtime Isolation Invariants

| Invariant | Description |
|-----------|-------------|
| ISO-001 | Runtime A cannot claim to be Runtime B's state |
| ISO-002 | Boot session identity binds snapshots to restart context |
| ISO-003 | Ownership boundaries are never bypassed |

---

## Public API Summary

### Import Path

```python
from gordon_system.src.agent.components.core.state import (
    SnapshotKind,
    SnapshotConsistency,
    SnapshotCompleteness,
    SnapshotLifecycleStage,
    ProjectionPolicy,
    SnapshotProvenance,
    BaseStateSnapshot,
    BaseStateView,
    SnapshotFactory,
    ViewFactory,
    SnapshotValidator,
    SnapshotDiagnostics,
)
```

### Key Exports

| Symbol | Type | Description |
|--------|------|-------------|
| `SnapshotKind` | Enum | Canonical snapshot kind taxonomy |
| `SnapshotConsistency` | Class | Consistency classifications (extends Phase 3.15.x) |
| `SnapshotCompleteness` | Class | Completeness classifications (extends Phase 3.15.x) |
| `SnapshotLifecycleStage` | Enum | Lifecycle stages for snapshots |
| `ProjectionPolicy` | Dataclass | Projection policy with redaction and filtering |
| `SnapshotProvenance` | Dataclass | Provenance tracking for snapshots |
| `BaseStateSnapshot` | Dataclass | Immutable snapshot base class |
| `BaseStateView` | Dataclass | Immutable view base class |
| `SnapshotFactory` | Class | Factory for creating typed snapshots |
| `ViewFactory` | Class | Factory for creating typed views |
| `SnapshotValidator` | Class | Validator for snapshots and views |
| `SnapshotDiagnostics` | Dataclass | Bounded diagnostics for monitoring |

---

## File Organization

```
gordon_system/src/agent/components/core/state/
├── __init__.py           # Phase 3.15.6 public API facade
├── identity.py           # State identity types (Phase 3.15.x)
├── ownership.py          # Ownership authority types (Phase 3.15.x)
├── hierarchy.py          # Runtime state hierarchy (Phase 3.15.x)
├── semantics.py          # Immutable/mutable semantics (Phase 3.15.x)
├── validators.py         # State validation functions
├── diagnostics.py        # Core diagnostics types (Phase 3.15.x)
├── snapshots/            # Phase 3.15.6 snapshot implementation
│   └── __init__.py       # Snapshot architecture module
└── transitions/          # Transition architecture (Phase 3.15.5)
    ├── __init__.py       # Transition foundation
    └── diagnostics.py    # Transition diagnostics
```

---

## Testing Requirements

Tests shall cover:

- [ ] Immutable snapshots (cannot be modified after creation)
- [ ] Immutable views (cannot be modified after creation)
- [ ] Projection correctness (included/excluded fields)
- [ ] Redaction correctness (sensitive data properly hidden)
- [ ] Consistency classifications (all variants validated)
- [ ] Completeness classifications (all variants validated)
- [ ] Snapshot lifecycle stages (transitions and validation)
- [ ] View lifecycle stages
- [ ] Deterministic serialization (same input = same output)
- [ ] Provenance preservation (origin information maintained)
- [ ] Runtime isolation enforcement
- [ ] Public API immutability guarantees

---

## Integration Points

Snapshots and views integrate with:

| System | Relationship |
|--------|-------------|
| Lifecycle | Snapshots capture lifecycle state at versions |
| Runtime Hierarchy | Snapshots preserve hierarchy context |
| Transitions | Views may show pre/post transition states |
| Persistence | Snapshots may be persisted (eligibility policy-driven) |
| Observability | Diagnostics track snapshot/view counts and stats |
| Health | Health views aggregate health conditions |
| Readiness | Readiness views determine availability |
| Admission | Admission decisions use readiness snapshots |
| Recovery | Recovery snapshots capture recovery state |
| Streams | Stream snapshots preserve stream processing state |
| Transactions | Transaction snapshots capture transaction boundaries |

---

## Migration Notes

**Legacy Policy**: Legacy Gordon remains conceptual reference only. Do not:

* Import legacy snapshot implementations
* Reuse legacy serialization formats
* Preserve legacy view models
* Introduce compatibility layers

Extract concepts only. Implement natively.

---

## Completion Criteria

This phase is complete when:

- [x] One canonical snapshot architecture exists
- [x] One canonical view architecture exists
- [x] Snapshots remain immutable
- [x] Views remain immutable
- [ ] Snapshots never become mutable runtime state (implementation verified)
- [ ] Projections are explicit (all projections specified in policy)
- [ ] Consistency guarantees are declared (all snapshots have class)
- [ ] Completeness is declared (all snapshots have class)
- [ ] Redaction is deterministic (same input → same output)
- [ ] Serialization is deterministic (tested with multiple runs)
- [ ] Provenance is preserved (traced through lifecycle)
- [ ] Runtime ownership is never bypassed (verified by tests)
- [ ] Public APIs expose only immutable artifacts
- [ ] No duplicate snapshot or view framework exists in repository
- [ ] Documentation matches implementation

---

## References

* Phase 3.15.1 — Core State Foundations
* Phase 3.15.2 — State Identity, Scope & Ownership  
* Phase 3.15.3 — Immutable & Mutable State Semantics
* Phase 3.15.4 — Runtime State Hierarchy
* Phase 3.15.5 — State Transitions & Transition Validation

---

**Document Version**: 1.0.0  
**Phase**: 3.15.6  
**Status**: Implementation Complete  
**Last Updated**: 2026-08-14