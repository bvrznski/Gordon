# Gordon Phase 3.15.2: Core State Identity, Scope & Ownership

**Phase Status:** Production Implementation  
**Date:** August 2026  
**Version:** 3.15.2  
**Canonical Location:** `/src/agent/components/core/state/`

---

## Executive Summary

Phase 3.15.2 extends the Phase 3.15.1 Core State Foundation with:

- **Typed Identity Hierarchy**: Strongly-typed immutable identifiers for all state aggregate classifications
- **Scope Inheritance Model**: Explicit scope hierarchy with inheritance rules and visibility boundaries
- **Ownership Transfer Protocol**: Policy-based ownership transfer with evidence preservation
- **Runtime Isolation Enforcement**: Runtime A cannot access/modify Runtime B's state
- **Validation System**: Structured validation findings, not just Boolean results

---

## Identity Hierarchy

### StateTypeId

Type classification for state aggregates:

| Type | Description |
|------|-------------|
| CORE | Core infrastructure state |
| LIFECYCLE | Lifecycle state machine |
| EXECUTION | Execution flow state |
| RUNTIME | Runtime management state |
| COMPONENT | Component instance state |
| SERVICE | Service state |
| STREAM | Stream processing state |
| THREAD | Thread execution state |
| RESOURCE | Resource allocation state |
| TRANSACTION | Transaction context state |
| PERSISTENCE | Persistence operation state |

### AggregateId

Unique identifier for a state aggregate (root of consistency boundaries):

```python
@dataclass(frozen=True, order=True, eq=True)
class AggregateId:
    value: str
    type_id: StateTypeId
    namespace: Optional[str]
```

### RuntimeId & BootSessionId

Runtime binding ensures isolation:

- **RuntimeId**: Identifies a runtime instance
- **BootSessionId**: Identifies a boot session (restart detection)

### OwnerId, AuthorityId

Ownership and authority identifiers are strongly typed with:
- Deterministic generation
- Uniqueness within scope
- Runtime binding verification

### VersionId & GenerationId

Version tracking:

| Concept | Description |
|---------|-------------|
| VersionId | Evolution within a lineage (sequence number) |
| GenerationId | Epoch change indicator (restart, migration) |

### SnapshotId, ViewId, ValidationId, etc.

Specialized identifiers for:
- Snapshots (immutable observations)
- Views (projections/filters)
- Validations (structured findings)
- Transitions (state machine changes)
- Operations (mutation requests)

---

## Scope Hierarchy

```
PROCESS
  ├─ APPLICATION
  │   ├─ SUBSYSTEM
  │   │   └─ COMPONENT
  │   │       └─ SERVICE
  │   └─ REQUEST
  │       └─ TRANSACTION
  └─ RUNTIME
      └─ BOOT_SESSION
```

### Scope Rules

1. **Visibility**: Child scopes inherit visibility from parents
2. **Isolation**: Scopes define boundary for state access
3. **Persistence**: Only persistent-scoped state survives restart
4. **Inheritance**: Properties flow down the hierarchy

---

## Ownership Model

### Authority Types

| Type | Description |
|------|-------------|
| EXCLUSIVE_MUTATION | One exclusive owner who may mutate |
| SHARED_OBSERVATION | Multiple observers, no mutation |
| DERIVED_VIEW | Derived view (observation only) |
| PERSISTENCE_WRITER | May persist but not mutate live state |
| RESTORATION_AUTHORITY | May restore from persistence |
| VALIDATION_AUTHORITY | May validate operations |
| TRANSITION_AUTHORITY | May perform state transitions |

### Ownership Evidence

Immutable evidence of ownership:

```python
@dataclass(frozen=True)
class OwnershipEvidence:
    ownership_id: str
    state_id: str
    owner_identity: str
    owner_kind: Optional[str]
    authority_type: OwnershipAuthorityType
    transfer_eligible: bool
    runtime_binding: Optional[str]
```

### Transfer Policy

| Policy | Description |
|--------|-------------|
| NEVER | Transfer is prohibited |
| WITH_CONSENT | Requires current owner's consent |
| WITH_POLICY | Allowed if policy conditions met |
| AUTOMATIC | Automatic on specific events (e.g., restart) |
| CONDITIONAL | Conditional on external factors |

---

## Runtime Isolation

### Enforcement Rules

1. **State belongs to exactly one runtime**
2. **Owner must match state's runtime binding**
3. **Cross-runtime operations require explicit policy**

### Validation

```python
RuntimeIsolationEnforcement.validate_runtime_binding(
    state_runtime_id,
    owner_runtime_id,
    boot_session_id,
    owner_boot_session_id,
) -> Tuple[bool, Optional[str]]
```

---

## Validation System

### Validator Classes

- **IdentityValidator**: Format compliance, uniqueness
- **ScopeValidator**: Inheritance rules, visibility
- **OwnershipValidator**: Uniqueness, conflicts
- **RuntimeIsolationValidator**: Runtime/session bindings
- **OwnershipTransferValidator**: Transfer policies

### Validation Result Structure

```python
@dataclass(frozen=True)
class ValidationResult:
    validation_id: str
    overall_validity: bool  # True only if no ERROR findings
    findings: Tuple[ValidationFinding, ...]  # All checks performed
```

---

## Diagnostics

### StateDiagnostics

Bounded diagnostics for debugging:

```python
@dataclass(frozen=True)
class StateDiagnostics:
    state_id: str
    domain: Optional[str]
    owner_identity: Optional[str]
    authority_type: Optional[str]
    version_sequence: int
    generation: int
    recent_findings: Tuple[str, ...]  # Bounded to last 10
```

### OwnershipDiagnostics

Ownership metadata without exposing mutable state:

```python
@dataclass(frozen=True)
class OwnershipDiagnostics:
    current_owner_identity: Optional[str]
    ownership_history: Tuple[str, ...]  # Ordered oldest first
    transfer_count: int
```

---

## Files Created/Modified

### Core State Extensions (Phase 3.15.2)

| File | Purpose |
|------|---------|
| `/src/agent/components/core/state/identity.py` | Typed identity hierarchy |
| `/src/agent/components/core/state/ownership.py` | Ownership model & transfer |
| `/src/agent/components/core/state/validators.py` | Validation utilities |
| `/src/agent/components/core/state/diagnostics.py` | Diagnostic utilities |

### Test Suite

| File | Purpose |
|------|---------|
| `/tests/test_phase_3_15_2_identity_scope_ownership.py` | Unit tests for extensions |

---

## Testing

Tests verify:

1. **Typed identity generation** - UUID-based, unique per type
2. **Deterministic serialization** - Can round-trip to/from string
3. **Scope inheritance** - Parent-child relationships work correctly
4. **Ownership uniqueness** - Only one EXCLUSIVE_MUTATION owner per state
5. **Runtime isolation** - Cross-runtime access rejected
6. **Transfer evidence** - All transfers create immutable records

---

## Design Principles

1. **One mutation owner per mutable aggregate**
2. **All public artifacts remain immutable**
3. **Observation authority does not imply mutation authority**
4. **Persistence authority does not imply live mutation authority**
5. **Runtime isolation enforced**
6. **No global mutable state authority**

---

## Import Policy

Importing identity/ownership modules shall never:
- Allocate runtime owners
- Create runtime identities
- Register mutable state
- Create active runtimes
- Perform ownership transfers

Remain import-pure.

---

## Legacy Policy

Do not:
- Import legacy identity classes
- Reuse legacy ownership managers
- Preserve legacy mutable globals
- Implement compatibility adapters

Extract concepts only. Reimplement natively.

---

## Conclusion

Phase 3.15.2 completes the canonical Core State Identity, Scope & Ownership architecture:

✅ Typed identities (StateTypeId through OperationId)  
✅ Scope hierarchy with inheritance rules  
✅ Ownership model with transfer protocols  
✅ Runtime isolation enforcement  
✅ Validation with structured findings  
✅ Diagnostics without exposing mutable state  

The foundation is ready for domain authorities to implement their own state mutations under these contracts.