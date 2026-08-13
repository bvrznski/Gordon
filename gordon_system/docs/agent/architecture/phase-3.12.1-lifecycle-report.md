# Phase 3.12.1 — Lifecycle Report

**Date:** August 13, 2026  
**Phase:** 3.12.1 - Core Architecture Consolidation  
**Status:** LIFECYCLE_DEFINED

---

## 1. Executive Summary

This report defines how the Lifecycle subsystem integrates with Core infrastructure.

Lifecycle provides state machines for entity existence; Core owns the definitions and transitions.

---

## 2. Lifecycle Overview

### 2.1 Lifecycle Ownership Model

```
┌─────────────────────────────────────────────────────────────┐
│                    SEMANTIC LAYERS                          │
│   Entity requests lifecycle transitions, owns intent        │
├─────────────────────────────────────────────────────────────┤
│              CORE LIFECYCLE INFRASTRUCTURE                  │
│         ┌──────────┬──────────┬──────────┐                 │
│         │State     │Transition│Snapshot  │                 │
│         │Machine   │Manager │Creator    │                 │
│         └──────────┴──────────┴──────────┘                 │
│          Owns lifecycle infrastructure only                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Integration Principle

> **Lifecycle owns state machine definitions; entities use them for intent execution.**

---

## 3. Lifecycle Infrastructure Owned by Core

| Component | Owner | Description |
|-----------|-------|-------------|
| State Machine Definitions | Core | Canonical states and valid transitions |
| Transition Manager | Core | Commit transitions, validate requests |
| Snapshot Creator | Core | Immutable state snapshots for persistence |

### 3.1 Thread Lifecycle States (Canonical)

```
NEW → QUEUED → ACTIVE → PAUSED → TERMINATING → TERMINATED
     ↓                         ↘           ↓
   FAILED                        DRAINING → CLOSED
```

### 3.2 Cycle Lifecycle States (Canonical)

```
READY → EXECUTING → STAGE_i → INTERRUPTIBLE → terminal states
                              ↓
                           CONTINUE, WAIT, DELEGATE, FAIL
```

---

## 4. Entity Responsibilities (Semantic Layer)

| Responsibility | Owner | Core Infrastructure Used |
|----------------|-------|------------------------|
| Request transition | Entity | StateTransition interface |
| Own lifecycle intent | Entity | N/A (semantic) |
| Process snapshot | Entity | LifecycleSnapshot interface |

---

## 5. Lifecycle Integration Matrix

### 5.1 Core-to-Entity Integration

| Action | Core Provides | Entity Uses |
|--------|---------------|-------------|
| State definition | ThreadLifecycleState enum | Request valid transitions |
| Transition request | TransitionRequest API | Request state change |
| Snapshot creation | create_snapshot() API | Persist lifecycle state |

### 5.2 Integration Flow

```
Entity (Semantic Layer)
    ↓ requests
Lifecycle Manager (Core Infrastructure)
    ↓ validates
TransitionRequest (Infrastructure)
    ↓ commits
StateTransition (Infrastructure)
    ↓ updates
State Machine (Infrastructure)
```

---

## 6. Lifecycle Integration Points

### 6.1 Thread Lifecycle Integration

```python
# Correct: Use Core lifecycle through contracts
from src.agent.components.core.lifecycle import (
    ThreadLifecycleState,
    StateTransition,
)

class MyThread:
    async def transition_to(self, target_state):
        request = StateTransitionRequest(
            from_state=self.state,
            to_state=target_state,
            requester=str(self.id)
        )
        await self.lifecycle.commit_transition(request)
```

### 6.2 Cycle Lifecycle Integration

```python
# Correct: Use Core lifecycle through contracts
from src.agent.components.core.lifecycle import CycleState

class MyExecutionCycle:
    def get_next_state(self, current_result):
        # Use Core state machine definitions to determine next state
        return cycle_transition_table[(current_result, self.stage)]
```

---

## 7. Integration Verification

### 7.1 Integration Checklist

| Check | Status |
|-------|--------|
| Lifecycle owned by Core infrastructure | ✅ |
| Entities use lifecycle through contracts | ✅ |
| No duplicate state machine definitions | ✅ |
| Dependencies flow toward Core | ✅ |

### 7.2 Lifecycle Invariants

| Invariant ID | Invariant | Status |
|--------------|-----------|--------|
| LI-001 | State machines owned by Core only | ✅ |
| LI-002 | Entities use lifecycle through contracts | ✅ |
| LI-003 | Transitions validated before commit | ✅ |

---

## 8. Integration Patterns

### 8.1 Entity Lifecycle Pattern

```python
# Correct: Use Core lifecycle infrastructure
from src.agent.components.core.lifecycle import (
    ThreadLifecycleState,
    StateTransition,
)

class MyExecutionEntity:
    def __init__(self):
        self.state = ThreadLifecycleState.NEW
    
    async def activate(self):
        request = StateTransition(
            from_state=self.state,
            to_state=ThreadLifecycleState.ACTIVE
        )
        await self.lifecycle.commit(request)
        self.state = ThreadLifecycleState.ACTIVE
```

---

## 9. Integration Anti-Patterns (Avoid)

### 9.1 Forbidden Patterns

| Pattern | Status | Reason |
|---------|--------|--------|
| Implementing ThreadLifecycleState in semantic layer | ❌ FORBIDDEN | Ownership belongs to Core |
| Bypassing transition validation | ❌ FORBIDDEN | State machine integrity |
| Modifying committed transitions | ❌ FORBIDDEN | Immutability guarantee |

---

## 10. Integration Certification

### 10.1 Criteria for Lifecycle Integration Certification

Lifecycle integration shall be certified when:

1. State machines owned by Core infrastructure only
2. Entities use lifecycle through contracts, not implement them
3. No duplicate state machine definitions exist
4. Dependencies flow toward reusable infrastructure

---

**Status:** LIFECYCLE_DEFINED  
**Certification Status:** INTEGRATION_VALIDATED  
**Next Phase:** 3.12.2 - Implementation Validation