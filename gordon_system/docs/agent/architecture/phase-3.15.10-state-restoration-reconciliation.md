# Phase 3.15.10 — State Restoration & Reconciliation Architecture

## Executive Summary

Phase 3.15.10 establishes the canonical architecture governing restoration, reconciliation, repair, and recovery of runtime state throughout the Gordon Core.

This phase extends:
- Phase 3.15.1 — Core State Foundations
- Phase 3.15.2 — State Identity, Scope & Ownership  
- Phase 3.15.3 — Immutable & Mutable State Semantics
- Phase 3.15.4 — Runtime State Hierarchy
- Phase 3.15.5 — State Transitions & Transition Validation
- Phase 3.15.6 — State Snapshots & Views
- Phase 3.15.7 — State Versioning & Generations
- Phase 3.15.8 — State Consistency & Concurrency
- Phase 3.15.9 — State Persistence Boundaries

### Key Achievement

One canonical restoration architecture and one canonical reconciliation architecture now exist throughout the Gordon Core, with restored state always receiving a valid runtime owner before activation.

---

## Architectural Principles

The following principles govern the restoration and reconciliation architecture:

1. **One Canonical Architecture**: Only one restoration architecture exists throughout the Core
2. **Runtime Ownership Preservation**: Runtime State remains owned by live runtime authority; restoration never bypasses ownership validation
3. **Distinct Responsibilities**: Persistent Record, Checkpoint, Restoration, Recovery, Repair remain separate architectural responsibilities
4. **Validation-First**: All restored state is validated before activation
5. **Deterministic Execution**: Restoration and reconciliation operations are deterministic and reproducible
6. **Immutable Results**: All results remain immutable for diagnostics and audit
7. **Policy-Driven**: No implicit behavior; all policies are explicit

---

## Architecture Overview

```
                    RESTORATION PIPELINE
                    ──────────────────────
                    
    Source (Checkpoint/Persistence/Archive)
               │
               ▼
    Restoration Request → Source Validation → Integrity Verification
                                            ↓ Schema Compatibility
                                            ↓ Version Validation
                                            ↓ Generation Validation
                                            ↓ Ownership Assignment
                                            ↓ Runtime Binding
                                            ↓ Hierarchy Reconstruction
                                            ↓ Dependency Validation
                                            ↓ Invariant Validation
                                            ↓ Activation Approval
                                              ↓
                                      Restored State (bound to runtime)

                    RECONCILIATION ENGINE
                    ───────────────────────
                    
    Runtime State → Scope Validation → Consistency Check → Findings
                                                      ↓
                                                Repair Recommendations

                    REPAIR RESOLVER
                    ────────────────
                    
    Strategy Selection → Evidence Production → Repair Application
```

---

## Restoration Architecture

### Source Types

The system supports restoration from multiple source types:

| Source Type | Description |
|-------------|-------------|
| `CHECKPOINT` | State from saved checkpoint file |
| `PERSISTENT_STORE` | Long-term persistence storage records |
| `ARCHIVE` | Versioned backup archive |
| `REPLICATED_STATE` | Copied state from remote instances |
| `MIGRATION_PACKAGE` | Transferred state with schema evolution |
| `RECOVERY_IMAGE` | Complete system recovery snapshot |
| `SERIALIZED_SNAPSHOT` | Encoded state representation |

### Lifecycle Phases

Every restoration follows the canonical sequence:

1. **Restoration Request** - Request received and queued
2. **Source Validation** - Source identification and metadata verified
3. **Integrity Verification** - Hash/digest verification completed
4. **Schema Compatibility Validation** - Schema version compatibility checked
5. **Version Validation** - Version lineage validated
6. **Generation Validation** - Generation epoch validated
7. **Ownership Assignment** - Owner bound to restored state
8. **Runtime Binding** - Runtime context established
9. **Hierarchy Reconstruction** - Parent-child relationships restored
10. **Dependency Validation** - Dependencies verified available
11. **Invariant Validation** - All architectural invariants checked
12. **Activation Approval** - State approved for activation
13. **Restoration Result** - Final result produced
14. **Diagnostics** - Events recorded for observability

### Policies

Restoration policies are explicitly declared:

| Policy | Description |
|--------|-------------|
| `FULL_RESTORE` | Complete reconstruction of all state |
| `PARTIAL_RESTORE` | Selective reconstruction by scope |
| `SELECTIVE_RESTORE` | Targeted aggregate restoration |
| `REPLACE_EXISTING` | Overwrite current state unconditionally |
| `MERGE_EXISTING` | Combine restored with current state |
| `RESTORE_IF_MISSING` | Only restore if no current state exists |
| `RESTORE_WITH_MIGRATION` | Apply schema evolution during restore |
| `RESTORE_READ_ONLY` | Create read-only bindings |

---

## Reconciliation Architecture

### Scopes

Reconciliation validates state across multiple scopes:

| Scope | Description |
|-------|-------------|
| `IDENTITY` | Validate aggregate identity uniqueness |
| `HIERARCHY` | Verify parent-child relationships |
| `OWNERSHIP` | Ensure valid ownership chains |
| `SCOPES` | Validate scope boundaries |
| `VERSIONS` | Check version lineage integrity |
| `GENERATIONS` | Validate epoch consistency |
| `DEPENDENCIES` | Confirm dependency availability |
| `RESOURCES` | Verify resource allocation validity |

### Result Status

| Status | Description |
|--------|-------------|
| `VALID` | All validations passed |
| `CONFLICT_DETECTED` | Conflict detected but not necessarily invalid |
| `INCONSISTENCY_DETECTED` | Inconsistency requiring attention |
| `ERROR` | Validation error occurred |

### Key Invariant

**Reconciliation NEVER silently modifies runtime state.** It only validates and reports.

---

## Repair Strategies

Repair is always explicit, policy-driven, and produces observable evidence:

| Strategy | Description |
|----------|-------------|
| `REJECT` | Reject the state as invalid (no repair attempted) |
| `REBUILD` | Recreate from scratch using available evidence |
| `RECONSTRUCT` | Build from partial state with validation |
| `REPLACE` | Swap with known good instance |
| `RETRY` | Attempt operation again |
| `RECONCILE` | Apply reconciliation to resolve inconsistency |
| `ROLLBACK` | Return to prior verified state |
| `COMPENSATE` | Execute compensating actions |
| `ESCALATE` | Delegate to higher authority |

---

## Public API

### StateRestorationFacade

The facade provides one canonical interface for restoration, reconciliation, and repair operations:

```python
class StateRestorationFacade:
    """Canonical facade for state restoration and reconciliation."""
    
    def validate_restoration(
        self, request: RestorationRequest
    ) -> Tuple[ValidationResults, List[str]]:
        """Validate a restoration request before execution."""
        
    def execute_restoration(
        self, request: RestorationRequest
    ) -> Tuple[RestorationResult, Tuple[ValidationFinding, ...]]:
        """Execute the restoration pipeline for a request."""
        
    def reconcile_state(
        self, request: ReconciliationRequest
    ) -> Tuple[ReconciliationResult, List[str]]:
        """Perform state consistency validation."""
        
    def resolve_repair(
        self, request: RepairRequest
    ) -> Tuple[RepairResult, List[str]]:
        """Apply explicit repair strategy."""
```

---

## Implementation Details

### Core Components

1. **RestorationPipeline** - Executes the canonical restoration sequence
2. **ReconciliationEngine** - Validates state consistency across scopes
3. **RepairResolver** - Applies repair strategies based on policy
4. **RestorationDiagnostics** - Immutable diagnostics collection for observability

### Data Structures

All data structures are immutable (frozen dataclasses) to ensure:
- Thread safety
- Deterministic behavior
- Traceable provenance

Key result types:
- `RestorationResult` - Result of restoration operations
- `ReconciliationResult` - Result of reconciliation operations
- `RepairResult` - Result of repair operations
- `ValidationResults` - Collection of validation findings

---

## Validation Model

### Validation Outcomes

| Outcome | Description |
|---------|-------------|
| `VALID` | Check passed successfully |
| `WARNING` | Check passed but with concerns |
| `REJECTED` | Check failed, restoration blocked |

### Validation Phases

Each phase produces structured findings:
1. Source validation - Source identification and metadata
2. Integrity verification - Hash/digest verification
3. Schema compatibility - Version compatibility checking
4. Version validation - Lineage integrity checks
5. Generation validation - Epoch consistency checks
6. Ownership assignment - Owner binding validation
7. Runtime binding - Context establishment
8. Hierarchy reconstruction - Relationship validation
9. Dependency validation - Availability confirmation
10. Invariant validation - Architecture compliance

---

## Diagnostics and Observability

### Diagnostic Events

Events are captured throughout the lifecycle:

| Event Type | Description |
|------------|-------------|
| `REQUEST_RECEIVED` | Request received from client |
| `SOURCE_VALIDATED` | Source validation completed |
| `INTEGRITY_VERIFIED` | Integrity verification completed |
| `RESTORATION_COMPLETED` | Full restoration completed |
| `RESTORATION_FAILED` | Restoration failed |

### Summary Statistics

Diagnostics provide:
- Total event count
- Completed restoration count
- Failed restoration count

---

## Integration Points

Restoration integrates with:

| Component | Role |
|-----------|------|
| Persistence (Phase 3.15.9) | Source for state restoration |
| Versioning (Phase 3.15.7) | Lineage validation and version tracking |
| Generations (Phase 3.15.7) | Epoch consistency validation |
| Hierarchy (Phase 3.15.4) | Parent-child relationship reconstruction |
| Ownership (Phase 3.15.2) | Owner binding and validation |
| Failure Model (Phase 3.14.x) | Recovery strategy selection |

---

## Invariants

### Restoration Invariants

- RST-001: One canonical restoration architecture exists throughout the Core
- RST-002: Restored state always receives a valid runtime owner before activation
- RST-003: Source validation precedes execution
- RST-004: Runtime binding occurs only after validation
- RST-005: Results are immutable for diagnostics

### Reconciliation Invariants

- REC-001: One canonical reconciliation architecture exists throughout the Core
- REC-002: Reconciliation never silently modifies runtime state
- REC-003: Findings are structured and deterministic
- REC-004: Repair recommendations are policy-driven

---

## Testing Strategy

### Test Coverage

Comprehensive tests cover:
- Full restoration with all policies
- Partial and selective restoration
- Reconciliation across all scopes
- All repair strategies
- Runtime binding validation
- Ownership reassignment
- Version/generation validation
- Hierarchy reconstruction
- Dependency validation
- Schema compatibility checks
- Integrity verification
- Conflict detection

### Test Doubles

Tests use deterministic test doubles for:
- Persistence (no production storage required)
- Runtime infrastructure (no live processes required)

---

## Completion Criteria

This phase is complete when:

- ✅ One canonical restoration architecture exists
- ✅ One canonical reconciliation architecture exists
- ✅ Restored state always receives a valid runtime owner
- ✅ Restored state is validated before activation
- ✅ Runtime bindings are reconstructed explicitly
- ✅ Hierarchy integrity is preserved
- ✅ Reconciliation never silently mutates runtime state
- ✅ Repair strategies are policy-driven
- ✅ Restoration conflicts are detected deterministically
- ✅ Migration preserves provenance
- ✅ Integration with persistence and recovery is clean
- ✅ Public APIs expose no mutable runtime internals
- ✅ No duplicate restoration framework exists

---

## Migration Path

### From Legacy Systems

Legacy Gordon remains conceptual reference only. Do not:
- Import legacy restoration managers
- Reuse legacy recovery logic
- Preserve legacy reconciliation systems
- Introduce compatibility adapters

Extract concepts only; reimplement natively.

### Import Policy

Importing restoration modules shall never:
- Restore runtime state
- Allocate runtime resources
- Connect to persistence
- Mutate runtime state
- Activate restored components

Remain import-pure.

---

## Related Documentation

- Phase 3.15.1 — Core State Foundations
- Phase 3.15.2 — State Identity, Scope & Ownership
- Phase 3.15.3 — Immutable & Mutable State Semantics
- Phase 3.15.4 — Runtime State Hierarchy
- Phase 3.15.5 — State Transitions & Validation
- Phase 3.15.6 — State Snapshots & Views
- Phase 3.15.7 — State Versioning & Generations
- Phase 3.15.8 — State Consistency & Concurrency
- Phase 3.15.9 — State Persistence Boundaries

---

## Implementation Ledger

### Files Created

| File | Purpose |
|------|---------|
| `src/agent/components/core/state/restoration/__init__.py` | Canonical restoration and reconciliation architecture |
| `docs/agent/architecture/phase-3.15.10-state-restoration-reconciliation.md` | Complete documentation |

### Exports Summary

The module exports 42 symbols including:
- Source types (8 enums/classes)
- Policies (2 enums/classes)
- Request structures (3 dataclasses)
- Result structures (7 dataclasses/enums)
- Pipeline/engine classes (4 classes)
- Diagnostics collection