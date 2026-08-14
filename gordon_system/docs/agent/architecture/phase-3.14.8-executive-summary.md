# Phase 3.14.8 - Capability Invocation Contracts

**Phase Version:** 3.14.8  
**Status:** COMPLETE  
**Date:** August 14, 2026  
**Author:** Gordon Architecture Team  

---

## Executive Summary

This phase establishes the canonical architectural contracts governing Capability invocation within Gordon. The contracts define how Capabilities are invoked, admitted, executed, and produce results while preserving ownership, authority, determinism, and architectural integrity.

### Key Accomplishments

1. **Canonical Invocation Contracts**: Established immutable contracts for Capability admission, invocation, execution, completion, cancellation, and result publication
2. **Lifecycle Model**: Defined the complete invocation lifecycle with deterministic state transitions
3. **Ownership Preservation**: Formalized architectural ownership model where Capabilities own computation but never redefine System or Stream ownership
4. **Authority Model**: Established that authority remains external to computation - Capabilities never self-authorize

---

## Architectural Principles

The following principles govern all Capability invocations:

```
Execution schedules work.
Interactions request work.
Capabilities perform work.
Streams transport interaction records.
Systems own persistent state.

Ownership Model:
- Capabilities own computation
- Execution owns scheduling
- Interactions own communication semantics
- Streams own transport
- Systems own persistent state

Authority Model:
- Capabilities never self-authorize
- Invocation subject to external authority verification
- Authority remains external to computation
```

---

## Canonical Invocation Flow

```
Execution
    │
    ▼
Interaction
    │
    ▼
Capability Admission
    │
    ▼
Capability Invocation
    │
    ▼
Capability Execution
    │
    ▼
Capability Result
    │
    ▼
Interaction Publication
```

---

## Invocation Lifecycle

### State Machine

```
Created → Validated → Admitted → Scheduled → Executing
    │                              ├─► Cancelled
    │                              ├─► Failed
    ▼
Completed → Published
```

### Terminal States

- **COMPLETED**: Execution completed successfully
- **CANCELLED**: Invocation was cancelled (explicitly or via external request)
- **FAILED**: Execution failed due to error

---

## Contract Categories

### 1. Identity Types

| Type | Purpose |
|------|---------|
| `CapabilityInvocationId` | Unique identifier for one invocation |
| `CapabilityAdmissionId` | Unique identifier for admission decision |
| `CapabilityExecutionId` | Unique identifier for execution instance |

All IDs are UUID-based and immutable.

### 2. Context Types

| Type | Purpose |
|------|---------|
| `InvocationContext` | Immutable context provided to Capabilities |
| `AdmissionContext` | Context for capability admission evaluation |
| `ExecutionExecutionContext` | Runtime context during capability execution |
| `ExecutionContextCancellationView` | Read-only cancellation state view |

### 3. Lifecycle States

```python
class CapabilityLifecycleState(Enum):
    CREATED = "created"           # Initial state
    VALIDATED = "validated"       # Inputs validated
    ADMIITTED = "admitted"        # Passed admission checks
    SCHEDULED = "scheduled"       # Scheduled for execution
    EXECUTING = "executing"       # Currently executing
    COMPLETED = "completed"       # Success terminal state
    CANCELLED = "cancelled"       # Cancelled terminal state
    FAILED = "failed"             # Failed terminal state
```

### 4. Protocol Types

| Protocol | Purpose |
|----------|---------|
| `CapabilityExecutor` | Execute capabilities with given context and inputs |
| `ExecutionObservabilityPort` | Emit observability data during execution |
| `OwnershipPreservationProtocol` | Verify ownership preservation |
| `AuthorityPreservationProtocol` | Verify authority preservation |

### 5. Result Types

| Type | Purpose |
|------|---------|
| `CapabilityExecutionResult` | Result of capability execution |
| `PublishedResult` | Result published to streams after successful invocation |
| `ResultPublication` | Request to publish a Capability result |

### 6. Failure Categories

```python
class CapabilityFailureCategory(Enum):
    ADMISSION_FAILED = "admission_failed"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    DEPENDENCY_TIMEOUT = "dependency_timeout"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_TIMED_OUT = "execution_timed_out"
    INTERUPTED = "interrupted"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    INTERNAL_ERROR = "internal_error"
```

---

## Key Invariants

### Lifecycle Invariants

- **LC-001**: Lifecycle progression shall remain deterministic
- **LC-002**: Invalid transitions shall be rejected
- **LC-003**: Each transition shall produce observable event
- **LC-004**: Terminal states never transition to non-terminal states

### Ownership Invariants

- **OWN-001**: Capabilities own computation
- **OWN-002**: Execution owns scheduling
- **OWN-003**: Interactions own communication semantics
- **OWN-004**: Streams own transport
- **OWN-005**: Systems own persistent state
- **OWN-006**: Ownership shall remain immutable throughout invocation

### Authority Invariants

- **AUTH-001**: Capabilities shall never self-authorize
- **AUTH-002**: Capability invocation shall always remain subject to external authority verification
- **AUTH-003**: Capability execution shall never elevate architectural privileges
- **AUTH-004**: Authority remains external to computation

### Execution Invariants

- **EXEC-001**: Execute shall consume declared inputs
- **EXEC-002**: Execute shall produce explicit outputs
- **EXEC-003**: Execute shall preserve execution context
- **EXEC-004**: Execute shall never mutate System state directly
- **EXEC-005**: Execution shall never bypass authority verification

---

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `gordon_system/src/agent/capabilities/invocation.py` | Canonical Capability invocation contracts |
| `gordon_system/tests/test_capability_invocation_contracts.py` | Acceptance tests for contracts |

### Modified Files

| File | Changes |
|------|---------|
| `gordon_system/src/agent/capabilities/__init__.py` | Export all new contract types |

---

## Testing

The test suite includes:

1. **Identity Tests**: Verify unique ID generation
2. **Lifecycle Tests**: Verify deterministic state transitions
3. **Context Tests**: Verify context immutability and proper field handling
4. **Protocol Tests**: Verify protocol definitions are correct
5. **Integration Tests**: Full lifecycle simulation

Run tests with:
```bash
pytest gordon_system/tests/test_capability_invocation_contracts.py -v
```

---

## Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Canonical Capability invocation contracts defined | ✅ |
| Admission semantics specified | ✅ |
| Execution lifecycle documented | ✅ |
| Completion semantics defined | ✅ |
| Cancellation semantics defined | ✅ |
| Result publication rules established | ✅ |
| Ownership preservation contracts | ✅ |
| Authority preservation contracts | ✅ |
| Replay compatibility rules | ✅ |
| Observability requirements | ✅ |
| Determinism declaration rules | ✅ |
| Acceptance tests created | ✅ |

---

## Next Steps

After this phase is integrated:

1. Update existing Capability implementations to conform to new contract
2. Implement InvocationContext handlers in Execution layer
3. Add admission validation middleware
4. Implement result publication to streams
5. Update documentation with concrete examples

---

## References

- Phase 3.10.x - Execution Foundations
- Phase 3.11.x - Streams Integration
- Phase 3.12.x - Core Architecture
- Phase 3.13.x - Functionality Markers
- Phase 3.14.x - Interaction Architecture