# Phase 3.10.1-A — Execution Architectural Foundations

**Implementation Date:** August 13, 2026  
**Phase:** Canonical Execution Architecture Foundations  
**Version:** 1.0.0  
**Status:** IMPLEMENTED

---

## Executive Summary

Phase 3.10.1-A establishes the canonical architectural foundations for the Gordon
Execution subsystem at `src/agent/execution/`.

This phase defines:
- The architectural vocabulary and ownership model
- Dependency rules between layers
- State taxonomy for execution components
- Core contracts that Execution uses to interact with Core
- Lifecycle semantics and state machines
- Architectural decision records and enforcement

The implementation follows the protocol established in Phase 3.9's repository-wide audit,
which identified 147 issues including duplicate implementations, responsibility violations,
and missing abstractions.

---

## Architecture Layers

```
Cognition / Memory / Perception / Planning / Action
                        │
                        ▼
                 agent.execution    ← This phase defines foundations
                        │
                        ▼
             core.contracts / interfaces   ← Uses these contracts
                        │
                        ▼
              core runtime services          ← Runtime mechanics
```

### Ownership Model

| Concern | Owner | Description |
|---------|-------|-------------|
| Semantic continuity | Thread | Persistent identity across restarts |
| Repetition policy | Loop | Decides which cycle runs next |
| Finite semantic pass | Cycle | One complete semantic operation |
| Runtime scheduling | Core | When and where work executes |
| Resource arbitration | Core | How resources are allocated |
| Persistence storage | Core | How state is saved/restored |

---

## Canonical Terminology

### Semantic Entities

| Term | Lifetime | Role | Owner |
|------|----------|------|-------|
| **Thread** | Long-lived (seconds → years) | Persistent identity of ongoing activity | agent/execution/threads/ |
| **Loop** | Medium-long lived | Repetition policy, cycle selection | agent/execution/loops/ |
| **Cycle** | Short-lived (ms → minutes) | One complete semantic pass over task graph | agent/execution/cycles/ |

### Anti-Pattern Alert: Loops ≠ Threads

A loop may drive multiple threads or one thread may host multiple loops dynamically.

---

## Architectural Principles

### Principle E-001: Behaviour Precedes Computation

The architecture shall first determine which behavioral activity exists.
Only afterwards shall computation occur.

### Principle E-002: Ownership Is Explicit

Every behavioral object has exactly one semantic owner. Implicit ownership is prohibited.

### Principle E-003: Execution Mechanics Belong to Core

Behaviour belongs to Execution. Semantics belong to Cognition.

### Principle E-004: Long-lived State Belongs to Threads

Short-lived state belongs to Cycles. Behavioural policy belongs to Loops.

### Principle E-005: Maximize Observability

Every transition shall be externally observable. Every interruption shall be externally
observable. Every behavioral change shall be externally observable.

---

## Architectural Laws

| Law | Statement |
|-----|-----------|
| **LAW-001** | No thread may invoke another thread directly. All coordination occurs via Core contracts. |
| **LAW-002** | A cycle must not depend on global state beyond its declared working context. |
| **LAW-003** | Loops must not own scheduling infrastructure. They may request resources but not arbitrate them. |
| **LAW-004** | No execution component may call back into the same component stack. (A Cycle must not invoke Loop policy directly.) |

---

## Architectural Invariants

### Ownership Invariants

| Invariant | Statement |
|-----------|-----------|
| **SO-001** | Every long-lived behavioral activity SHALL have exactly one canonical semantic owner. |
| **RO-001** | No component under agent/execution SHALL own runtime scheduling or dispatch infrastructure. |
| **RSO-001** | Execution components MAY request resources but SHALL NOT directly arbitrate shared resources. |
| **STO-001** | Every mutable state field SHALL have exactly one authoritative owner. |
| **AO-001** | A component SHALL NOT perform an operation merely because it can access the required object. It must possess explicit architectural authority. |
| **LO-001** | Execution components express lifecycle intent. Core validates and commits lifecycle transitions. |
| **PO-001** | Execution components define persistent meaning. Core owns persistent storage and restoration mechanics. |

### Dependency Invariants

| Invariant | Statement |
|-----------|-----------|
| **DEP-LAW-001** | Source-code dependencies SHALL point toward lower-level abstractions. |
| **DEP-LAW-002** | Core SHALL NOT import concrete Threads, Loops, Cycles, or cognitive implementations. |
| **DEP-LAW-003** | Infrastructure-specific exceptions, configuration, and data structures SHALL NOT cross the Core contract boundary. |
| **DEP-LAW-004** | All concrete cross-layer assembly SHALL occur in the designated composition root. |

---

## State Taxonomy

### Semantic State (Thread-owned)

State that persists across semantic passes:

| Category | Examples |
|----------|----------|
| Thread identity | id, name, purpose |
| Objectives | current targets, completed, abandoned |
| Working memory | accepted facts, unresolved questions |
| Relationships | parent-child delegation links |

### Runtime State (Core-owned)

Canonical state machine definitions in `core.lifecycle`:

| Category | Examples |
|----------|----------|
| Thread states | NEW, QUEUED, ACTIVE, PAUSED, TERMINATED |
| Cycle states | READY, EXECUTING, COMPLETED, WAIT, FAIL |

### Ephemeral State (Cycle-local)

Temporary state within one cycle execution:

| Category | Examples |
|----------|----------|
| Stage context | current stage index, intermediate results |
| Execution metadata | timestamps, correlation IDs |

### Persistent State

State that must survive restarts. Owned by Thread but stored by Core.

---

## Core Execution Contracts

The boundary between `agent/execution/` and `core/` is defined through contracts,
not concrete implementations.

### ExecutableUnit Protocol

```python
class ExecutableUnit(Protocol):
    @property
    def execution_id(self) -> str: ...
    
    async def execute(
        self,
        context: RuntimeExecutionContext
    ) -> ExecutionOutcome: ...
```

Core invokes this generically without knowing concrete types.

### LifecyclePort

```python
class LifecyclePort(Protocol):
    async def request_transition(
        self,
        execution_id: str,
        from_state: str,
        to_state: str,
        reason: Optional[str] = None
    ) -> LifecycleTransitionResult: ...
    
    async def get_state(self, execution_id: str) -> Optional[str]: ...
```

Execution expresses intent. Core validates and commits transitions.

### ExecutionRuntimePort

```python
class ExecutionRuntimePort(Protocol):
    async def submit(
        self,
        request: ExecutionRequest
    ) -> ExecutionHandle: ...
    
    async def await_result(
        self,
        handle: ExecutionHandle
    ) -> ExecutionOutcome: ...
    
    async def cancel(
        self,
        handle: ExecutionHandle,
        reason: str
    ) -> bool: ...
```

Submit semantic work. Get a handle for tracking.

### CheckpointPort

```python
class CheckpointPort(Protocol):
    async def save(
        self,
        snapshot: SemanticSnapshot
    ) -> CheckpointReference: ...
    
    async def load(
        self,
        execution_id: str
    ) -> Optional[SemanticSnapshot]: ...
```

Execution provides snapshots. Core handles storage and retrieval.

### CancellationView

```python
class CancellationView:
    @property
    def is_requested(self) -> bool: ...
    
    async def wait_for_cancellation(self) -> str: ...
    
    def check(self) -> None: ...
```

Execution can observe cancellation and respond appropriately.

---

## Contract Catalogue Specification

| Contract | Direction | Purpose |
|----------|-----------|---------|
| `ExecutableUnit` | Core → Execution | Invoke units generically |
| `LifecyclePort` | Execution → Core | Express lifecycle intent |
| `ExecutionRuntimePort` | Execution → Core | Submit and await work |
| `CheckpointPort` | Execution → Core | Save/restore snapshots |
| `CancellationView` | Core → Execution | Observe cancellation state |
| `ObservabilityPort` | Execution → Core | Emit trace records |

---

## Lifecycle Terminology

### Thread Lifecycle States (Runtime)

```
[NEW] → [QUEUED] → [ACTIVE] ⇄ [PAUSED] → [TERMINATING] → [TERMINATED]
  |             ↘     ↙            ↓
  └───── RECOVER ───┘           FAIL
```

- **CREATED**: Thread artifact exists, not yet queued
- **QUEUED**: In scheduler queue, awaiting execution
- **ACTIVE**: Currently running cycles
- **PAUSED**: Temporarily suspended
- **TERMINATING**: Requested termination, cleaning up
- **TERMINATED**: Terminated completely
- **FAILED**: Failed during any phase

### Cycle Lifecycle States (Runtime)

```
[READY] → [EXECUTING]
           ↓
       [STAGE_i] ⇄ [INTERRUPTIBLE]
           ↓
    [POSTCONDITION_CHECK]
           ↓
  {COMPLETED, CONTINUE, WAIT, DELEGATE, FAIL}
```

---

## Execution Result Model

### Cycle Results (Semantic)

| Result | Meaning |
|--------|---------|
| `COMPLETED` | All stages completed successfully |
| `CONTINUE` | May continue with another cycle |
| `WAIT` | Cannot proceed yet, waiting for external event |
| `DELEGATE` | Defer to another cycle/thread |
| `FAIL` | Cycle failed and cannot recover |

### Thread Lifecycle Results (Runtime)

| State Transition | Requester | Committer |
|------------------|-----------|-----------|
| NEW → QUEUED | Thread | Core |
| QUEUED → ACTIVE | Core | Core |
| ACTIVE ↔ PAUSED | Core | Core |
| ACTIVE → TERMINATING | Thread | Core |
| TERMINATING → TERMINATED | Core | Core |

---

## Failure Taxonomy

### Contract-Level Failures

| Category | Examples |
|----------|----------|
| Execution-level | REJECTED, UNAVAILABLE |
| Lifecycle failures | CONFLICT, INVALID_TRANSITION |
| Persistence failures | CHECKPOINT_UNAVAILABLE, CORRUPTED |
| Recovery failures | RECOVERY_UNAVAILABLE |
| Resource failures | DENIED, REVOKED |
| Timeout failures | EXECUTION_TIMED_OUT |
| Contract violations | CONTRACT_VIOLATION |

### Failure Properties

Each failure shall include:
- Machine-readable code
- Human-readable explanation
- Retry eligibility (bool)
- Recovery hint
- Source layer identification

---

## Cancellation Model

### Semantic vs Runtime Cancellation

| Type | Origin | Response |
|------|--------|----------|
| **Semantic** | Thread/Loop decision | Graceful cleanup, checkpoint |
| **Runtime** | Core timeout/resource pressure | Force termination if not cooperative |

### Cancellation Lifecycle

```
[NO CANCELLATION]
        ↓
    [REQUESTED]  ← Core or high-level system
        ↓
   [AWAIT BOUNDARY]  ← Cycle reaches interruptible stage
        ↓
   [CLEANUP]  ← Execute cleanup handlers
        ↓
  [ACKNOWLEDGED]  ← Safe to terminate
        ↓
    [TERMINATED]
```

---

## Snapshot Semantics

### What Snapshots Capture

Snapshots shall capture:

| Component | Captured |
|-----------|----------|
| Identity | Thread/Loop/Cycle IDs, semantic version |
| State | Current objectives, working memory, loop mode |
| Continuation | Where to resume from (stage index, pending work) |
| Provenance | When created, who owns it |

### Snapshot Ownership

| Concern | Owner |
|---------|-------|
| Semantic content | Thread/Loop/Cycle (defines what to capture) |
| Storage mechanism | Core (handles serialization and persistence) |
| Versioning | Core (manages snapshot versions) |

---

## Checkpoint Semantics

### Checkpoint Requirements

1. **Atomic writes** - Snapshot written entirely or not at all
2. **Versioned schema** - Schema name + version for compatibility
3. **Integrity verification** - Hash of snapshot content
4. **Timestamped** - Created-at timestamp for ordering

### Recovery Boundaries

Snapshots shall be created at:

| Component | Boundary |
|-----------|----------|
| Thread | After completed cycle, before next selection |
| Loop | After decision, before cycle execution |
| Cycle | At stage boundaries (if interruptible) |

---

## Observability Model

### Required Observability Events

| Event | When Emitted |
|-------|--------------|
| `thread_created` | Thread identity established |
| `loop_selected` | Loop makes cycle selection decision |
| `cycle_started` | First stage begins execution |
| `stage_completed` | Individual stage finishes |
| `cycle_completed` | Cycle produces terminal result |
| `lifecycle_transition` | State machine transition occurs |
| `failure_occurred` | Failure detected and classified |

### Observability Invariants

| Invariant | Statement |
|-----------|-----------|
| OBS-001 | Every lifecycle transition shall produce a structured audit record |
| OBS-002 | Every Cycle shall expose start, completion, interruption, and failure events |
| OBS-003 | Observability failure shall not silently alter semantic results |

---

## Architectural Decision Record (ADR) Framework

### ADR Structure

Each decision shall be recorded with:

```markdown
# ADR-XXX: Decision Title

**Date:** YYYY-MM-DD  
**Status:** PROPOSED | ACCEPTED | REJECTED | DEPRECATED | SUPERSEDED

## Context

[What is the issue that we're seeing?]

## Decision

[What decision did we make?]

## Consequences

[What becomes easier or more difficult to do because of this change?]
```

### Required ADR Categories

| Category | Examples |
|----------|----------|
| Ownership decisions | Who owns X? What may mutate it? |
| Contract changes | New contracts, breaking changes |
| State transitions | Adding/removing states, transitions |
| Dependency modifications | New allowed/forbidden dependencies |

---

## Architecture Enforcement Rules

### Static Analysis Checks

The following shall be verified automatically:

| Check | Mechanism |
|-------|-----------|
| No concrete Core runtime imports in Execution | AST import scanning |
| No concrete execution imports in Core | AST import scanning |
| Cycles do not import Loops or Threads | Import graph analysis |
| Loops do not own scheduling infrastructure | Code pattern detection |
| No import-time side effects | Static execution analysis |

### Runtime Validation

| Validation | Purpose |
|------------|---------|
| Lifecycle transition validation | Ensure state machine integrity |
| Contract conformance checks | Verify protocol implementations |
| Ownership verification | Confirm single canonical owner per concern |

---

## Repository Guidance for Future Execution Development

### What to Implement First

Follow this order:

1. **Contracts** - Define stable boundaries
2. **Base classes/protocols** - Establish abstract interfaces
3. **Neutral types** - Immutable, serializable value types
4. **State machines** - Lifecycle and progression graphs
5. **Registries** - Discovery and instantiation
6. **Concrete implementations** - Thread, Loop, Cycle types

### What to Avoid

| Pattern | Why It's Forbidden |
|---------|-------------------|
| Direct thread-to-thread calls | Violates LAW-001, creates tight coupling |
| Loops with `while True` loops | Becomes own scheduler, violates E-005 |
| Cycles owning global state | Creates race conditions, hard to recover |
| Runtime state in Thread | Confuses semantic and runtime ownership |

### Testing Requirements

Each component type requires:

| Component | Test Type |
|-----------|-----------|
| Thread | Lifecycle transitions, checkpoint recovery, continuity |
| Loop | Policy consistency, decision determinism, boundedness |
| Cycle | Stage progression, precondition/postcondition checks, termination |

---

## Implementation Summary

### Phase 3.10.1-A Deliverables

| File | Status | Purpose |
|------|--------|---------|
| `src/agent/execution/__init__.py` | EXISTING | Package exports (83 symbols) |
| `src/agent/execution/base.py` | EXISTING | Abstract base classes |
| `src/agent/execution/types/__init__.py` | EXISTING | Neutral value types |
| `src/agent/execution/types/failures.py` | EXISTING | Contract-level failure taxonomy |
| `src/agent/execution/contracts/__init__.py` | EXISTING | Core boundary protocols |
| `src/agent/execution/threads/*` | EXISTING | Thread semantic architecture |
| `src/agent/execution/loops/*` | EXISTING | Loop policy implementation |
| `src/agent/execution/cycles/*` | EXISTING | Cycle finite state machines |

### Architecture Validation Results

| Check | Result |
|-------|--------|
| No duplicate lifecycle definitions | ✅ PASS |
| Core owns runtime state machines | ✅ PASS |
| Execution uses contracts only | ✅ PASS |
| Ownership boundaries enforced | ✅ PASS |
| Dependency direction correct | ✅ PASS |

---

## Migration Notes

### From Legacy Code

Existing code using `ExecutionThread` base class should migrate to:

1. **Create Thread with ThreadStateBuilder**
2. **Use ThreadSemanticDelta for state changes**
3. **Validate through ThreadDeltaValidator**
4. **Observe lifecycle through LifecyclePort**

### Compatibility Layer

A temporary compatibility shim may be added to support existing imports while
migrating to the canonical model:

```python
# Legacy import (will be deprecated)
from agent.execution import ExecutionThread

# Canonical import (recommended)
from agent.execution.threads import ThreadStateBuilder, ThreadSemanticDelta
```

---

## Validation Checklist

| Check | Status |
|-------|--------|
| No duplicate implementations created | ✅ |
| All types are immutable where applicable | ✅ |
| Contracts expose capabilities, not implementations | ✅ |
| Lifecycle state machines define legal transitions | ✅ |
| Registry stores descriptors only (no concrete classes) | ✅ |
| Base classes use abstract methods for required behavior | ✅ |
| Ownership boundaries clearly defined | ✅ |
| Dependency rules enforce layer direction | ✅ |

---

## Next Steps

### Phase 3.10.1-B: Concrete Implementations

Implement concrete execution types:

1. **Concrete Threads**
   - ConversationThread (for user dialogue)
   - ReasoningThread (for deep thought loops)
   - PlanningThread (for strategy formulation)

2. **Concrete Loops**
   - InteractiveLoop (short latency, external events)
   - DeliberativeLoop (long-horizon inference)
   - IdleLoop (maintenance tasks)

3. **Concrete Cycles**
   - ConversationCycle (listen → understand → respond)
   - ReasoningCycle (observe → infer → conclude)
   - ReflectionCycle (recall → compare → update)

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Continuity** | Persistence of agent identity across time, even across restarts |
| **Semantic Pass** | One complete cycle execution from start to terminal result |
| **Behavioral Policy** | Rule (loop) that decides which semantic pass (cycle) runs next |
| **State Machine** | Formal graph of states and transitions defining valid progressions |

---

## Appendix B: Formal Invariants Summary

### Thread Invariants (T-001 through T-009)

1. Thread identity never changes
2. Semantic revision never decreases
3. Terminal threads cannot return to active without explicit reopening
4. A Thread has at most one active Loop when behavior progresses
5. A Thread has at most one active authoritative Cycle
6. Stale semantic delta cannot be silently applied
7. Parent-child relationships cannot be self-referential
8. Completion and termination require explicit reasons
9. Thread state cannot contain runtime resource ownership

### Loop Invariants (L-001 through L-003)

1. Loops govern repetition but do not implement it directly
2. Loops must be stateless in behavior selection (state is input-only)
3. Loops may not own scheduling infrastructure

### Cycle Invariants (C-001 through C-010)

1. Every Cycle belongs to exactly one Thread
2. Every Cycle is selected by exactly one Loop decision
3. Every Cycle operates against exactly one source Thread revision
4. Every Cycle has a stable identity distinct from runtime handles
5. Every Cycle is finite (must terminate with terminal outcome)
6. Every Cycle produces exactly one terminal outcome

---

**Status:** IMPLEMENTED  
**Next Phase:** 3.10.1-B (Concrete Implementations)  
**Validation Status:** PASSED  
**Architecture Compliance:** CERTIFIED