# Phase 3.14.13 - Scheduling & Admission Architecture

**Phase Version:** 3.14.13  
**Status:** Implemented  
**Date:** 2026-08-14  

---

## Executive Summary

This phase establishes the canonical architectural model governing **Scheduling** and **Admission** throughout Gordon. 

**Scheduling** determines when work is eligible to execute.

**Admission** determines whether work is permitted to execute.

Neither Scheduling nor Admission performs computation, and neither owns persistent state.

### Key Achievements

- Canonical scheduling architecture with priority-based ordering
- Admission evaluation with explicit decisions (Accepted/Deferred/Waiting/Rejected/Cancelled)
- Ready queue implementation with bounded size and fairness protection
- Priority inheritance support for preventing priority inversion
- Deadline-aware scheduling for time-sensitive operations
- Comprehensive observability and tracing infrastructure
- Replay-compatible observation records

---

## Canonical Model

```
Interaction → Admission → Ready Queue → Scheduler → Execution → Completion
```

**Alternative terminal states:** Cancelled, Rejected, Failed, Timed Out

### Lifecycle Transitions

```
CREATED
    │
    ▼
EVALUATING (Admission)
    │
    ├─→ REJECTED (authority, policy violations)
    ├─→ DEFERRED (retry eligible, timing-dependent)
    ├─→ WAITING (external conditions required)
    └─→ ACCEPTED → READY
                    │
                    ▼
                EXECUTING (Scheduled)
                    │
                    ├─→ COMPLETED (success)
                    ├─→ FAILED (error)
                    └─→ CANCELLED (explicit cancellation)
```

---

## Admission Semantics

Admission evaluates whether a work item may proceed through the execution pipeline.

### Evaluation Criteria

- **Interaction validity** - Is this interaction well-formed?
- **Lifecycle compatibility** - Does current state allow progression?
- **Dependency readiness** - Are dependencies satisfied?
- **Authority verification** (external) - Is requester authorized?
- **Ownership verification** - Is ownership claim valid?
- **Security policy** - Does request comply with security rules?
- **Privacy policy** - Does request respect privacy constraints?
- **Execution context** - Are required context values present?
- **Resource availability** - Are resources available to execute?

### Admission Decisions

| Decision | Description |
|----------|-------------|
| `ACCEPTED` | Work admitted, may proceed to scheduling |
| `DEFERRED` | Eligible but timing-dependent; retry later |
| `WAITING` | Requires external conditions before proceeding |
| `REJECTED` | Not permitted (with explicit reason) |
| `CANCELLED` | Admission request was cancelled |

**Invariant:** Every admission produces exactly one explicit decision. Implicit decisions are prohibited.

---

## Scheduling Semantics

Scheduling determines execution order after successful admission.

### Considerations

- **Priority class** - Critical > High > Normal > Low > Background
- **Deadlines** - Time-sensitive operations may be prioritized
- **Fairness** - Prevents starvation, ensures all work eventually executes
- **Dependencies** - Wait for prerequisite work to complete
- **Execution context** - Group similar context items together

### Deterministic Mode

When `deterministic_mode=True`:
- Same priority items are ordered by creation time (stable sort)
- Queue operations produce predictable results
- Enables replay compatibility

---

## Priority Classes

```
Priority Class       | Value | Use Case
---------------------|-------|----------------------------------
CRITICAL             |   5   | Safety, security, immediate response
HIGH                 |   4   | Time-sensitive operations
NORMAL               |   3   | Standard priority (default)
LOW                  |   2   | Best-effort, can be delayed
BACKGROUND           |   1   | Lowest priority, runs during idle
```

**Invariant:** Priority affects only scheduling order. Priority shall never override:
- Ownership boundaries
- Authority verification
- Security policies
- Admission decisions
- Integrity verification

---

## Ownership Model

| Component | Owns |
|-----------|------|
| **Admission** | Admission decisions (Accepted/Rejected/etc.) |
| **Scheduling** | Execution ordering within ready queue |
| **Execution** | Progression of work items |
| **Capabilities** | Computation logic and results |
| **Systems** | Persistent state |
| **Streams** | Transport mechanism |

**Invariant:** Ownership boundaries are immutable. Scheduling shall never redefine ownership.

---

## Authority Model

- **Admission verifies authority** - Checks authentication, authorization, permissions (external to admission)
- **Scheduling assumes successful admission** - Does not re-verify authority
- **Scheduling shall never grant authority** - Authority remains external

---

## Ready Queue Implementation

### CanonicalReadyQueue

```python
@dataclass
class CanonicalReadyQueue(ReadyQueueProtocol):
    queue_id: QueueId
    max_size: int = 10000
    
    _items: Dict[WorkItemId, WorkItemRecord]
    _priority_buckets: Dict[int, List[WorkItemId]]
```

**Features:**
- Priority-based ordering (higher priority first)
- Within same priority, ordered by creation time
- Bounded size prevents queue overflow
- O(1) peek, O(n) insert with priority search

### PriorityInheritanceQueue

Wraps base queue to implement priority inheritance:
- Prevents priority inversion when items hold resources needed by higher-priority waiters
- Temporarily inherits priority until resource release

### DeadlineQueue

Extends ready queue with deadline awareness:
- Items past their deadline are prioritized
- Supports time-sensitive scheduling requirements

---

## Scheduling Lifecycle States

| State | Description |
|-------|-------------|
| `CREATED` | Request received, not yet evaluated |
| `EVALUATING` | Admission evaluation in progress |
| `ACCEPTED/DEFERRED/WAITING` | Waiting for scheduling conditions |
| `READY` | Admitted and ready for scheduling |
| `EXECUTING` | Currently executing |
| `COMPLETED` | Successfully completed |
| `REJECTED` | Admission denied |
| `CANCELLED` | Request cancelled |
| `FAILED` | Execution failed |

---

## Observability Infrastructure

### Observation Context

```python
@dataclass(frozen=True)
class ObservationContext:
    observer_id: str
    correlation_id: str  # Cross-system trace context
    timestamp_utc: float
```

### Admission Observations

- `REQUEST_RECEIVED` - Work item submitted for admission
- `EVALUATING` - Admission evaluation started
- `DECISION_MADE` - Final decision reached
- `REJECTED` / `DEFERRED` / `WAITING` / `ACCEPTED` - Specific decisions

### Scheduler Observations

- `ITEM_SUBMITTED` - Work item submitted for scheduling
- `QUEUED` - Item added to ready queue
- `SELECTED` - Item selected from queue
- `EXECUTING` - Execution started
- `COMPLETED` / `FAILED` / `CANCELLED` - Terminal states

### Replay Compatibility

All observation data is replay-compatible:
- No non-deterministic values (except trace IDs which are acceptable)
- All timestamps are monotonic UTC
- Full context preserved for debugging

---

## Architectural Invariants

**Admission shall never:**
- Perform computation (only evaluate pre-existing data and rules)
- Mutate persistent state
- Bypass authority verification

**Scheduling shall never:**
- Bypass admission (must go through admission first)
- Redefine ownership boundaries
- Bypass execution layer
- Grant authority

**Both are architectural orchestration mechanisms only.**

---

## Files Created

| File | Purpose |
|------|---------|
| `scheduling_admission/__init__.py` | Canonical scheduler, admission controller, and record types |
| `scheduling_admission/ready_queue.py` | Priority queue implementations |
| `scheduling_admission/observability.py` | Observation logging and tracing |

---

## Usage Example

```python
from agent.architecture.scheduling_admission import (
    CanonicalScheduler,
    CanonicalAdmissionController,
    WorkItemRecord,
    PriorityClass,
)

# Create admission controller and scheduler
controller = CanonicalAdmissionController("my-controller")
scheduler = CanonicalScheduler(
    SchedulerId.generate(),
    admission_controller=controller
)

# Submit work item
work_item = WorkItemRecord(
    work_item_id=WorkItemId.generate(),
    correlation_id="trace_12345",
    source_system="api-server"
)

result = await scheduler.submit_work(work_item, PriorityClass.HIGH)

if result.is_accepted():
    # Get ready items and schedule execution
    ready_items = await scheduler.get_ready_items(limit=10)
    for item in ready_items:
        # Mark as executing
        await scheduler.mark_executing(item.work_item_id)
        
        # ... execute work ...
        
        # Mark as completed
        await scheduler.complete_work(item.work_item_id)
```

---

## Acceptance Criteria

- [x] Canonical admission architecture defined
- [x] Canonical scheduling architecture defined
- [x] Admission lifecycle model established
- [x] Scheduling lifecycle model established
- [x] Priority classes defined with semantics
- [x] Resource allocation semantics documented
- [x] Fairness guarantees implemented (bounded queue, no starvation)
- [x] Ready queue semantics defined and implemented
- [x] Ownership boundaries preserved
- [x] Authority preservation maintained
- [x] Execution integration established
- [x] Stream integration ready
- [x] Replay compatibility ensured
- [x] Observability hooks in place

---

## Future Compatibility

This phase establishes the architectural foundation for all scheduling and admission mechanisms in Gordon. Future implementations:

- May add specialized schedulers (deadline-based, ML-optimized, etc.)
- May implement advanced fairness algorithms
- May integrate with external systems
- Shall conform to these contracts
- Shall never redefine these principles

---

## Related Phases

| Phase | Relation |
|-------|----------|
| 3.14.1 - Interaction Foundations | Provides interaction types for work items |
| 3.14.2 - Interaction Taxonomy | Categorizes interactions |
| 3.14.5 - Event/Signal/Notification Semantics | Defines communication patterns |
| 3.14.8 - Capability Invocation | Capabilities consume scheduled work |
| 3.14.9 - System Integration | Systems own state that scheduling may access |

---

## Conclusion

This phase establishes the immutable architectural contracts governing Scheduling and Admission in Gordon. These contracts ensure:

- **Deterministic execution ordering** through priority-based scheduling
- **Explicit decision-making** through admission evaluation
- **Fair resource allocation** through bounded queues and fairness protection
- **Comprehensive observability** for debugging and replay
- **Architectural integrity** through ownership and authority preservation

The canonical model enables future specialization while preserving core architectural principles.