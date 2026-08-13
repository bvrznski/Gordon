# Phase 3.10.10 — Agentic Execution Flow, Examples, and Guidelines

**Implementation Date:** August 13, 2026  
**Phase:** Agentic Loop as Orchestration Pattern  
**Version:** 1.0.0  
**Status:** IMPLEMENTED

---

## Executive Summary

This phase makes the agentic execution model explicit in the Gordon codebase.

### Canonical Definition

> The Gordon agentic loop is the repeated runtime advancement of semantic
> ExecutionThreads through their currently active ExecutionLoops, one bounded
> ExecutionCycle at a time.

The agentic loop is therefore an **orchestration process**.

It is NOT:
- A peer of `ConversationLoop`, `TaskLoop`, `PlanningLoop`, etc.
- A concrete `ExecutionLoop` subtype that replaces the others

It IS:
- The runtime coordination mechanism that advances Threads one cycle at a time
- Responsible for selecting which Thread receives execution time next
- Responsible for ensuring exactly one Cycle executes per advancement

---

## Ownership Model

```
┌─────────────────────────────────────────────────────────────────┐
│                      Core Runtime                               │
├─────────────────────────────────────────────────────────────────┤
│  - Global thread selection (which Thread runs now?)            │
│  - Scheduling algorithms                                       │
│  - Resource arbitration                                        │
│  - Lifecycle state transitions (CREATED→ACTIVE, etc.)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                    runtime selection
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               ExecutionCoordinator (this module)                │
├─────────────────────────────────────────────────────────────────┤
│  - Advance one Thread by at most one Cycle                     │
│  - Validate and apply proposed deltas                          │
│  - Produce iteration results for traceability                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Loop decision request
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ExecutionThread                           │
├─────────────────────────────────────────────────────────────────┤
│  - Semantic continuity (identity, objectives, state)           │
│  - At most one active Loop                                     │
│  - At most one active Cycle                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Policy evaluation
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ExecutionLoop                              │
├─────────────────────────────────────────────────────────────────┤
│  - Behavioral policy (how should Thread behave?)               │
│  - Continuation decision (what next for this Thread?)          │
│  - NO: Cycle selection execution                               │
│  - NO: Global scheduling                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Cycle request
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ExecutionCycle                             │
├─────────────────────────────────────────────────────────────────┤
│  - Bounded semantic operation (one pass)                       │
│  - Stage progression                                           │
│  - Produce terminal outcome                                    │
│  - Propose deltas (Thread must accept)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    Stage execution
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ExecutionStage                            │
├─────────────────────────────────────────────────────────────────┤
│  - One bounded semantic transformation                         │
│  - NO: Direct Thread mutation                                  │
│  - NO: Loop selection                                          │
│  - NO: Scheduling                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## One Advancement = At Most One Cycle

A single `advance()` call must:

✅ Execute zero or one Cycle  
✅ Apply at most one ThreadDelta  
✅ Produce exactly one result  

❌ Must NOT execute multiple Cycles in one advancement  
❌ Must NOT run an entire TaskThread to completion  
❌ Must NOT own scheduling (Core does this)  

---

## Loop Decision Model

Thread-local continuation decisions (NOT global scheduling):

```
START_CYCLE          → Execute one Cycle with given definition
SWITCH_LOOP         → Replace active Loop policy
AWAIT_INPUT         → Wait for external input before continuing
AWAIT_CONDITION     → Wait for a condition to become true
DELEGATE            → Defer work to child Thread
YIELD               → Give up execution time, allow other Threads
COMPLETE_THREAD     → Mark Thread as completed successfully
FAIL_THREAD         → Mark Thread as failed (recoverable)
TERMINATE_THREAD    → Permanently terminate Thread
```

Each decision is:
- **Typed** (explicit enum, not `"continue"`/`"stop"`)
- **Explicit** (payload matches decision kind)
- **Thread-local** (does NOT select other Threads to run)

---

## Canonical Advancement Algorithm

```python
async def advance(thread_id: str) -> ExecutionIterationResult:
    # 1. Get Thread state snapshot
    snapshot = get_snapshot(thread_id)
    
    # 2. Resolve active Loop (if any)
    loop = get_active_loop(thread_id)
    
    if not loop:
        return yield_decision()
    
    # 3. Ask Loop for decision
    decision = loop.decide(snapshot)
    
    # 4a. Non-cycle decision (await, complete, fail, etc.)
    if not decision.is_continuation:
        return apply_non_cycle_decision(decision)
    
    # 4b. Cycle execution path
    cycle = create_cycle(
        definition=decision.cycle_definition,
        thread_id=thread_id,
        loop_id=loop.loop_id,
        source_revision=snapshot.thread_revision,
    )
    
    outcome = await execute_cycle(cycle)
    
    # 5. Apply delta from outcome
    commit_result = commit_delta(thread_id, outcome.delta)
    
    # 6. Get continuation decision
    continuation = loop.interpret_outcome(snapshot, outcome, commit_result)
    
    # 7. Apply continuation to Thread state
    apply_continuation(continuation)
    
    return ExecutionIterationResult(...)
```

---

## Concrete Flow Examples

### Example A: Direct Conversation Response

**Iteration 1:**
```
active Thread: ConversationThread (conv-001)
active Loop: ConversationLoop (conv-loop-001)
selected Cycle: InterpretationCycle
result: interpreted user input
continuation: YIELD (awaiting next advancement for ResponseCycle)
```

**Iteration 2:**
```
active Thread: ConversationThread (conv-001) [SAME thread!]
active Loop: ConversationLoop (conv-loop-001) [same loop!]
selected Cycle: ResponseCycle
result: response artifact produced
continuation: AWAIT_INPUT
```

### Example B: Task Planning → Execution

```
TaskThread (task-001)
    active Loop = PlanningLoop
    
PlanningLoop
    ↓
PlanningCycle
    ↓
plan committed
    ↓
SWITCH_LOOP(TaskLoop)  # Loop switching, not nesting!
    
TaskLoop
    ↓
ExecutionCycle
    ↓
one bounded plan increment performed

TaskLoop
    ↓
EvaluationCycle
```

### Example C: Failure → Recovery

```
TaskThread (task-001)
    active Loop = TaskLoop
    
TaskLoop
    ↓
ExecutionCycle fails semantically
    ↓
CycleOutcome records failure
    ↓
TaskLoop selects SWITCH_LOOP(RecoveryLoop)
    
same TaskThread [identity preserved!]
    ↓
RecoveryLoop
    ↓
RecoveryCycle

possible outcomes:
    recovered → SWITCH_LOOP(TaskLoop)
    plan invalid → SWITCH_LOOP(PlanningLoop)
    unrecoverable → FAIL_THREAD
```

### Example D: Parent-Child Delegation

```
ConversationThread (parent)
    active Loop = ConversationLoop
    delegates → TaskThread (child)

TaskThread (child)
    independent lifecycle, own Loop/Cycle progression

When child completes:
    result becomes event for parent
    parent Thread resumes (if suspended waiting)
```

---

## Critical Invariants Enforced

| Invariant | Statement |
|-----------|-----------|
| **A-001** | One advancement executes at most one Cycle |
| **A-002** | Thread state changes only through validated delta application |
| **A-003** | Loop switching replaces, not nests, policies |
| **A-004** | Thread identity persists across Loop switches |
| **A-005** | A Cycle cannot select or execute another Cycle |
| **A-006** | A Stage cannot directly mutate Thread state |
| **A-007** | Loop decisions are typed and explicit (no strings) |

---

## Anti-Patterns Prohibited

### ❌ Monolithic AgenticLoop
```python
class AgenticLoop(ExecutionLoop):
    def run(self):
        while True:
            perceive()   # Runtime scheduling inside!
            think()
            plan()
            act()
            evaluate()
            reflect()
            sleep()      # NEVER sleep in Loop!
```

**Why forbidden:** Combines runtime scheduling with semantic behavior.

### ❌ Cycle Chaining
```python
class PlanningCycle:
    def execute(self):
        return ExecutionCycle(plan).execute()  # NO! Cycles cannot select cycles
```

**Why forbidden:** A Cycle must not select another Cycle.

### ❌ Loop Nesting
```python
class TaskLoop:
    def run(self):
        return PlanningLoop(...).run()  # NO! Use SWITCH_LOOP instead
```

**Why forbidden:** A Thread has one active Loop at a time. Replace, don't nest.

### ❌ Direct Thread Mutation from Cycle
```python
thread.state["plan"] = plan  # NO!
thread.revision += 1         # NO!
```

**Why forbidden:** Cycles propose deltas; Threads validate and commit them.

### ❌ Runtime Waiting in Semantic Loop
```python
while no_change:
    await sleep(interval)   # Core owns timing!
    observe()
```

**Why forbidden:** Core manages suspension and resumption.

---

## Files Created/Modified

| File | Purpose |
|------|---------|
| `src/agent/execution/coordinator.py` | ExecutionCoordinator protocol + implementation |
| `src/agent/execution/examples/__init__.py` | Examples package |
| `src/agent/execution/examples/conversation_flow.py` | ConversationThread advancement example |
| `src/agent/execution/examples/task_flow.py` | TaskThread loop switching example |
| `docs/agent/architecture/phase-3.10.10-agentic-execution.md` | This documentation |

---

## Usage

```python
from agent.execution.coordinator import (
    ExecutionCoordinator,
    SimpleExecutionCoordinator,
    LoopDecisionKind,
)
```

### Basic Advancement
```python
coordinator = SimpleExecutionCoordinator()

# Create thread with initial loop
thread_id = await coordinator.create_thread(
    thread_id="my-thread",
    purpose="Do something interesting",
)

# Advance one step (at most one Cycle executes)
result = await coordinator.advance_thread(thread_id)

print(f"Cycle executed: {result.cycle_executed}")
print(f"Decision: {result.loop_decision.decision_kind.value}")
```

### Check Loop Switching
```python
if result.loop_switched:
    print("Loop policy was replaced (not nested)")
    
if result.completed or result.failed:
    print("Thread reached terminal state")
```

---

## Verification Checklist

| Check | Status |
|-------|--------|
| Agentic loop defined as orchestration, not concrete Loop subtype | ✅ |
| One advancement executes at most one Cycle | ✅ |
| Thread state changes only through delta application | ✅ |
| Loop switching replaces (not nests) policies | ✅ |
| Typed LoopDecision enum with explicit categories | ✅ |
| Canonical advancement algorithm documented | ✅ |
| Examples show Conversation, Task flows | ✅ |
| Anti-patterns explicitly documented and prohibited | ✅ |

---

**Status:** IMPLEMENTED  
**Next Phase:** 3.10.11 (Concrete Execution Types)  
**Validation Status:** PASSED