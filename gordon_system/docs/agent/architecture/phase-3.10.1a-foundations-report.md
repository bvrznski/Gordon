# Phase 3.10.1-A — Foundations Report

**Implementation Date:** August 12, 2026  
**Phase:** Execution Architecture Foundations  
**Version:** 1.0.0

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
- Registry mechanisms for discovery

The implementation follows the protocol established in Phase 3.9's repository-wide audit,
which identified 147 issues including duplicate implementations, responsibility violations,
and missing abstractions.

---

## Architecture Layers

```
Cognition / Memory / Perception / Planning / Action
                        │
                        ▼
                 agent.execution    ← This phase implements
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

## Directory Structure

```
src/agent/execution/
├── __init__.py              # Package exports
├── base.py                  # Base classes (Thread, Loop, Cycle)
├── types/
│   ├── __init__.py          # Neutral value types
│   └── failures.py          # Contract-level failure taxonomy
├── contracts/
│   └── __init__.py          # Core boundary protocols
├── lifecycle/
│   └── __init__.py          # State machines and transitions
└── registry/
    └── __init__.py          # Unit type registries
```

---

## Neutral Types (`types/`)

These are immutable, serialization-stable types that cross Core-Execution boundaries.

### Identifiers

| Type | Description |
|------|-------------|
| `ExecutionId` | Unique ID for any execution unit |
| `ThreadId` | Thread identity |
| `LoopId` | Loop policy identity |
| `CycleId` | Cycle execution identity |

### Lifecycle States

| State | Meaning |
|-------|---------|
| `NEW`, `QUEUED`, `ACTIVE`, `PAUSED` | Thread lifecycle phases |
| `READY`, `EXECUTING`, `COMPLETED` | Cycle execution phases |

### Results and Policies

| Type | Description |
|------|-------------|
| `CycleResult` | COMPLETED, CONTINUE, WAIT, DELEGATE, FAIL |
| `Priority` | CRITICAL=0, HIGH=1, NORMAL=2, LOW=3 |
| `ResourceBudget` | Timeout and resource limits |

---

## Core Boundary Contracts (`contracts/`)

These protocols define how Execution interacts with Core.

### ExecutableUnit Protocol

```python
class ExecutableUnit(Protocol):
    @property
    def execution_id(self) -> str: ...
    async def execute(self, context: RuntimeExecutionContext) -> ExecutionOutcome: ...
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
```

Execution expresses intent, Core validates and commits transitions.

### ExecutionRuntimePort

```python
class ExecutionRuntimePort(Protocol):
    async def submit(self, request: ExecutionRequest) -> ExecutionHandle: ...
    async def await_result(self, handle: ExecutionHandle) -> ExecutionOutcome: ...
```

Submit semantic work; get a handle for tracking results.

---

## Lifecycle State Machines (`lifecycle/`)

### Thread Lifecycle

```
[NEW] → [QUEUED] → [ACTIVE] ⇄ [PAUSED] → [TERMINATING] → [TERMINATED]
  |             ↘     ↙            ↓
  └───── RECOVER ───┘           FAIL
```

- `Thread` owns semantic intent (when to terminate)
- `Core` owns runtime state transitions

### Cycle Lifecycle

```
[READY] → [EXECUTING] → [STAGE_i] ⇄ [INTERRUPTIBLE]
                        ↓
                  [POSTCONDITION_CHECK]
                        ↓
        {COMPLETED, CONTINUE, WAIT, DELEGATE, FAIL}
```

---

## Registry (`registry/`)

```python
class ExecutionRegistry:
    def register_thread(name, ...) -> UnitDescriptor: ...
    def register_loop(name, ...) -> UnitDescriptor: ...
    def register_cycle(name, ...) -> UnitDescriptor: ...
    
    def get_by_implementation_path(path) -> Optional[UnitDescriptor]: ...
```

- Single canonical registry per unit type
- Stores descriptors (not concrete classes)
- Core uses this to instantiate units without imports

---

## Base Classes (`base.py`)

### ExecutionThread

```python
class ExecutionThread(ABC):
    id: str
    name: str
    purpose: Optional[str]
    
    @abstractmethod
    async def run(self) -> None: ...
    
    @abstractmethod
    def completion_condition(self) -> bool: ...
```

Owns semantic continuity and lifecycle intent.

### ExecutionLoop

```python
class ExecutionLoop(ABC):
    @abstractmethod
    def select_next(thread, state) -> tuple[CycleClass, Policy]: ...
    
    @abstractmethod
    def accept_result(result, state) -> str: ...
```

Policy function mapping state → next cycle choice.

### ExecutionCycle

```python
class ExecutionCycle(ABC):
    id: str
    
    @property
    @abstractmethod
    def stages(self) -> List[ExecutionStage]: ...
    
    @abstractmethod
    async def execute(context) -> str: ...  # Returns CycleResult
```

Finite sequence of semantic stages.

---

## Architectural Laws

| Law | Statement |
|-----|-----------|
| **LAW-001** | No thread may invoke another thread directly. All coordination occurs via Core contracts. |
| **LAW-002** | A cycle must not depend on global state beyond its declared working context. |
| **LAW-003** | Loops must not own scheduling infrastructure. They may request resources but not arbitrate them. |

---

## Dependency Rules

### Legal Imports
- `execution/types` ← can import nothing (neutral types)
- `execution/contracts` ← can import Core contract interfaces only
- `execution/lifecycle` ← can import types, contracts
- `execution/registry` ← can import types, contracts
- `execution/base` ← can import types, contracts

### Forbidden Imports
- ❌ Concrete scheduler implementation
- ❌ Checkpoint backend
- ❌ Recovery manager
- ❌ Worker pool implementation
- ❌ Infrastructure-specific exceptions

---

## Files Created

| File | Purpose |
|------|---------|
| `types/__init__.py` | Neutral identifiers, states, priorities, budgets, timestamps |
| `types/failures.py` | Contract-level failure taxonomy (15 categories) |
| `contracts/__init__.py` | Core boundary protocols (8 protocol types) |
| `lifecycle/__init__.py` | State machines, transition graphs, snapshots |
| `registry/__init__.py` | Unit type registries with descriptor system |
| `base.py` | Abstract base classes for Thread, Loop, Cycle |
| `__init__.py` | Package exports (83 symbols) |

---

## Validation Checklist

- [x] No duplicate implementations created
- [x] All types are immutable where applicable  
- [x] Contracts expose capabilities, not implementations
- [x] Lifecycle state machines define legal transitions
- [x] Registry stores descriptors only (no concrete classes)
- [x] Base classes use abstract methods for required behavior
- [x] Ownership boundaries clearly defined
- [x] Dependency rules enforce layer direction

---

## Next Steps

Phase 3.10.1-B and beyond will implement:

1. Concrete thread implementations (ConversationThread, ReasoningThread, etc.)
2. Concrete loop implementations (InteractiveLoop, DeliberativeLoop, etc.)
3. Concrete cycle implementations (AgenticCycle, ConversationCycle, ReflectionCycle)
4. Core runtime adapters (connecting contracts to actual scheduler/checkpoint)
5. Composition root integration

---

## Migration Notes

This phase creates a new `agent/execution/` directory from scratch.
No existing components were modified during this foundational phase.

Future phases will migrate existing execution-related code to use these
foundations rather than duplicate the architecture.

---

**Status:** IMPLEMENTED  
**Next Phase:** 3.10.1-B (Concrete Implementations)