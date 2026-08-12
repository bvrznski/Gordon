# Phase 3.10.3 — Thread Architecture

**Implementation Date:** August 12, 2026  
**Phase:** Thread Architecture Implementation  
**Version:** 1.0.0

---

## Executive Summary

This phase establishes the canonical Thread architecture for Gordon's semantic execution layer.

A Thread is **not**:
- An operating-system thread, coroutine, task, worker, process, or scheduler entry
- A runtime execution unit (Core owns this)
- A scheduling entity (Core owns this)

A Thread IS:
- The semantic owner of one continuous agent activity
- Persistent identity across multiple finite executions
- Purpose-driven: maintains purpose while objectives may evolve
- Lifecycle-managed through controlled transitions

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Thread (Semantic)                       │
├─────────────────────────────────────────────────────────────┤
│ • Identity (ThreadId, immutable)                            │
│ • Purpose (why this thread exists)                          │
│ • Objectives (current targets, evolve over time)            │
│ • Semantic State (working memory, facts, context)           │
│ • Lifecycle Intent (when to complete/suspend)               │
│ • Relationships (parent-child delegation)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                    semantic state transitions
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Core Runtime                            │
├─────────────────────────────────────────────────────────────┤
│ • Runtime scheduling (when work executes)                   │
│ • State machine transitions (CREATED→ACTIVE, etc.)          │
│ • Resource allocation                                       │
│ • Persistence storage                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Thread Identity

Every Thread must have a stable semantic identity.

**Requirements:**
- Immutable (cannot change once created)
- Unique within its execution domain
- Stable across suspension and resumption
- Distinct from Core runtime handles, scheduler task IDs, persistence record IDs

```python
# Canonical Thread ID
thread_id = ThreadId.generate()  # UUID-based

# Human-readable name (for display only)
name = ThreadName("my-conversation")
```

---

## Purpose vs Objectives

### Purpose
The enduring reason the Thread exists. This is stable and defines the thread's fundamental role.

### Objectives
Current semantic targets pursued within the Thread. These may be:
- Added
- Refined
- Completed
- Abandoned
- Superseded

**Example:**
```
Thread: "Code Review Assistant"
  Purpose: "Help developers improve code quality through automated review"
  Objectives:
    - [active] Review pull request #1234
    - [completed] Analyze Python syntax in last commit
    - [pending] Check for security vulnerabilities
```

---

## Semantic State

Thread state is long-lived semantic state. It includes:
- Accepted context
- Active objectives
- Semantic summaries
- Accepted facts
- Unresolved questions
- Commitments
- Constraints
- References to relevant memory
- Relationships to other Threads
- Current behavioral mode

**State changes must occur through controlled delta application**, not direct mutation.

---

## Lifecycle States

| State | Description |
|-------|-------------|
| CREATED | Thread artifact exists, not yet queued |
| ACTIVE | Currently engaged in semantic activity (has active Loop) |
| SUSPENDED | Behavioral progression paused, identity preserved |
| AWAITING_INPUT | Waiting for external input before resuming |
| DELEGATED | Work delegated to child thread |
| COMPLETED | Thread fulfilled its purpose |
| INTERRUPTED | Semantic or runtime condition prevented continuation |
| TERMINATED | Thread stopped without normal completion |

---

## Delta Application Flow

```
Cycle produces outcome
        ↓
Outcome contains proposed semantic delta
        ↓
Loop interprets outcome
        ↓
Thread validates and accepts or rejects delta
        ↓
Thread advances semantic version
```

A delta specifies:
- Source Cycle (which cycle produced this delta)
- Expected Thread version (for validation - prevents stale deltas)
- Proposed changes (what state changes)
- Provenance (how the change was derived)
- Validation result
- Acceptance status

---

## Invariants

Enforced invariants:

| Number | Invariant |
|--------|-----------|
| T-001 | Thread identity never changes |
| T-002 | Semantic revision never decreases |
| T-003 | Terminal threads cannot return to active without explicit reopening |
| T-004 | A Thread has at most one active Loop when behavior progresses |
| T-005 | A Thread has at most one active authoritative Cycle |
| T-006 | Stale semantic delta cannot be silently applied |
| T-007 | Parent-child relationships cannot be self-referential |
| T-008 | Completion and termination require explicit reasons |
| T-009 | Thread state cannot contain runtime resource ownership |

---

## Package Structure

```
src/agent/execution/threads/
├── __init__.py          # Package exports
├── identity.py          # Semantic Thread identity (immutable)
├── state.py             # Thread semantic state (controlled mutation)
├── lifecycle.py         # Lifecycle transitions and states
├── delta.py             # Semantic delta application model
├── relationships.py     # Parent-child Thread relationships
├── snapshot.py          # Immutable snapshots for persistence
└── validation.py        # Invariant validators
```

---

## Ownership Model

| Concern | Owner |
|---------|-------|
| Semantic continuity | Thread |
| Identity, purpose, objectives | Thread |
| Semantic state changes | Thread (via delta) |
| Runtime scheduling | Core |
| Lifecycle state transitions | Core (uses thread's intent) |
| Resource allocation | Core |

---

## Key Types and Interfaces

### Identity
```python
ThreadId              # Immutable semantic identifier
ThreadName            # Human-readable name
ThreadMetadata        # Semantic metadata
ThreadDescriptor      # Read-only reference to a Thread
```

### State
```python
BehavioralMode        # CONVERSATION, PLANNING, MONITORING, etc.
ThreadObjective       # A single objective within the thread
ThreadFacts           # Accepted semantic facts
ThreadContext         # Current working memory and constraints
ThreadSemanticState   # Immutable state snapshot
ThreadStateBuilder    # Builder for controlled state changes
```

### Lifecycle
```python
ThreadLifecycleState        # State enum (CREATED, ACTIVE, etc.)
ThreadLifecycleReason       # Reason codes for transitions
ThreadLifecycleTransition   # A single transition definition
ThreadLifecycleTransitionGraph  # Valid transitions graph
ThreadLifecycleSnapshot     # Snapshot of lifecycle state
ThreadLifecycleTransitionRequest  # Request to transition
ThreadLifecycleTransitionResult   # Result of transition request
```

### Delta
```python
DeltaValidationResult       # VALID, STALE_VERSION, INVALID_CONTENT, etc.
ThreadSemanticDelta         # A single semantic delta
ThreadDeltaBatch            # Batch of deltas for atomic application
DeltaApplicationResult      # Result of applying a delta
ThreadDeltaValidator        # Validator for deltas and invariants
```

### Relationships
```python
RelationshipKind            # DELEGATION, COLLABORATION, MONITORING, etc.
ThreadRelationship          # General relationship between threads
ParentChildRelationship     # Parent-child delegation relationship
ThreadRelationshipGraph     # Graph of all thread relationships
```

### Snapshots
```python
ThreadSnapshot              # Immutable state snapshot at point in time
ThreadRecoveryDescriptor    # Minimal info for recovery from persistence
ThreadSnapshotBuilder       # Builder for creating snapshots
ThreadSnapshotChain         # Chain of historical snapshots
```

### Validation
```python
ValidationResult            # Result of validation (is_valid, errors, warnings)
ThreadValidator             # Validator for all thread invariants
```

---

## Usage Examples

### Creating a Thread
```python
from agent.execution.threads import (
    ThreadId,
    ThreadStateBuilder,
    BehavioralMode,
)

# Create new thread with initial state
thread_id = str(ThreadId.generate())
builder = ThreadStateBuilder(thread_id)
builder.with_name("My Conversation")
builder.with_purpose("Help user with coding questions")

state = builder.build()
```

### Adding an Objective
```python
from agent.execution.threads import ThreadObjective

objective = ThreadObjective(
    objective_id="obj-1",
    description="Review PR #1234"
)

builder.add_objective(objective)
state_with_objective = builder.build()
```

### Applying a Delta
```python
from agent.execution.threads import (
    ThreadSemanticDelta,
    ThreadDeltaValidator,
)

delta = ThreadSemanticDelta(
    source_cycle_id="cycle-123",
    expected_thread_version=5,
    change_type="objective_completed",
    changes={"objective_id": "obj-1"},
    provenance="cycle_outcome"
)

validator = ThreadDeltaValidator(current_version=5)
result = validator.validate_delta(delta)

if result == DeltaValidationResult.VALID:
    # Apply the delta
    success, new_version, error = validator.apply_delta(delta, 5)
```

### Checking Lifecycle Transitions
```python
from agent.execution.threads import (
    ThreadLifecycleState,
    ThreadLifecycleTransitionGraph,
)

graph = ThreadLifecycleTransitionGraph()

# Check if transition is valid
is_valid = graph.is_valid_transition(
    ThreadLifecycleState.ACTIVE,
    ThreadLifecycleState.SUSPENDED
)
```

---

## Migration Notes

### From Existing ExecutionThread

The existing `ExecutionThread` in `src/agent/execution/base.py` is a base class that will be replaced by the canonical Thread model.

**Key differences:**
- Canonical Thread has immutable identity (ThreadId)
- Canonical Thread uses controlled delta application for state changes
- Canonical Thread has explicit lifecycle transitions via ThreadLifecycleTransitionGraph
- Semantic state is separated from runtime execution

### Migration Strategy

1. Create new threads using `ThreadStateBuilder`
2. Use `ThreadSemanticDelta` and `ThreadDeltaValidator` for state updates
3. Replace direct mutation with delta application
4. Use `ThreadLifecycleTransitionGraph` for lifecycle transitions
5. Migrate Loop/Cycle associations to use new Thread model

---

## Verification Checklist (Phase 3.10.3)

| Check | Status |
|-------|--------|
| Thread identity is immutable (semantic) | ✅ |
| Semantic state changes occur through controlled delta application | ✅ |
| Lifecycle transitions are validated by core.lifecycle | ✅ |
| Loop cardinality: at most one active Loop per Thread | ✅ |
| Cycle cardinality: at most one active Cycle per Thread | ✅ |
| Stale deltas are rejected with STALE_VERSION result | ✅ |
| Parent-child relationships prevent cycles | ✅ |
| Terminal states have explicit reasons | ✅ |
| No runtime resource ownership in Thread state | ✅ |
| All tests pass | ✅ |

---

## Future Work

### Phase 3.10.4 - Concrete Implementations
- Implement concrete Loop types (InteractiveLoop, DeliberativeLoop, etc.)
- Implement concrete Cycle types (ConversationCycle, ReflectionCycle, PlanningCycle)
- Implement Loop selection policy based on Thread state and context

### Phase 3.10.5 - Runtime Integration
- Implement core adapters connecting Thread contracts to actual runtime
- Implement CheckpointPort for persistence integration
- Implement ObservabilityPort for tracing

### Phase 3.10.6 - Concrete Threads
- Implement ConversationThread (for user dialogue)
- Implement PlanningThread (for strategy formulation)
- Implement MonitoringThread (for condition watching)
- Implement ReflectionThread (for internal review)

---

**Status:** IMPLEMENTED  
**Next Phase:** 3.10.4 (Concrete Loop and Cycle Implementations)