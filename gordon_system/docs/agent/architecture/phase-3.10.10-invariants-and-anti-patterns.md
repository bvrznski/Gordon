# Phase 3.10.10 — Invariants and Anti-Patterns

**Implementation Date:** August 13, 2026  
**Phase:** Agentic Loop as Orchestration Pattern  
**Version:** 1.0.0  
**Status:** IMPLEMENTED

---

## Ownership Layer Hierarchy

```
Core Runtime
    └─ Selects which Thread runs next (global scheduling)
        │
        ▼
ExecutionCoordinator
    └─ Advances one Thread by at most one Cycle
        │
        ▼
ExecutionThread
    └─ Semantic continuity, identity, objectives
        │
        ▼
ExecutionLoop (active policy)
    └─ Continuation decision: what should this Thread do next?
        │
        ▼
ExecutionCycle (if selected)
    └─ Bounded semantic pass: one complete operation
        │
        ▼
ExecutionStage (if executed)
    └─ One bounded transformation
```

**Critical Rule:** Each layer has distinct ownership. Never blur the boundaries.

---

## Cardinality Rules

| Entity | Cardinality | Constraint |
|--------|-------------|------------|
| Thread | 1 | Each Thread is unique by ID |
| Active Loop per Thread | ≤ 1 | At most one active policy |
| Active Cycle per Thread | ≤ 1 | At most one executing cycle |
| Active Stage per Cycle | N | Ordered sequence, but only current stage executes |

---

## Revision Safety Rules

### Rule R-001: Stale Delta Rejection
```python
# Thread revision is 5
delta = ThreadSemanticDelta(
    expected_thread_revision=5,
    ...
)

# If another operation advances thread to revision 6 first...
# This delta will be rejected as STALE_VERSION
```

### Rule R-002: Delta Proposal Only
```python
# ❌ WRONG: Direct mutation
thread.state["plan"] = plan  # Thread owns state!

# ✅ CORRECT: Propose delta for validation and commitment
delta = ThreadSemanticDelta(
    expected_thread_revision=current_revision,
    change_type="plan_proposed",
    changes={"plan": plan},
)
commit_result = coordinator.commit_delta(thread_id, delta, current_revision)
```

---

## Loop Decision Rules

### Rule L-001: Typed Decisions Only
```python
# ❌ WRONG: String-based decisions (ambiguous!)
return "continue"
return "stop"

# ✅ CORRECT: Explicit enum with typed payload
return LoopDecision.start_cycle(cycle_definition=...)
return LoopDecision.complete_thread(...)
```

### Rule L-002: Thread-Local, Not Global
```python
# ❌ WRONG: Loop selecting which Thread runs
def decide(...) -> str:
    return "run other_thread"

# ✅ CORRECT: Loop deciding what THIS Thread does next
def decide(...) -> LoopDecision:
    return LoopDecision.start_cycle(...)
```

---

## Cycle Boundary Rules

### Rule C-001: Bounded Execution
```python
class MyCycle:
    def execute(self):
        # ❌ WRONG: Unbounded loop inside cycle
        while not done:
            do_work()
        
        # ✅ CORRECT: One bounded semantic pass
        return self._execute_one_pass()

def _execute_one_pass(self) -> CycleOutcome:
    # Execute all Stages in order, produce terminal outcome
```

### Rule C-002: No Cycle Selection Inside Cycle
```python
class PlanningCycle:
    def execute(self):
        # ❌ WRONG: Selecting another cycle
        return ExecutionCycle(plan).execute()
        
        # ✅ CORRECT: Produce outcome and let Loop decide next cycle
        return CycleOutcome(
            status="completed",
            semantic_delta=ThreadSemanticDelta(...),
        )
```

---

## Stage Boundary Rules

### Rule S-001: Bounded Transformation
```python
class MyStage:
    def execute(self) -> StageResult:
        # Perform ONE bounded transformation
        # Return result, don't call other stages directly
        
        return StageResult(
            status="completed",
            semantic_output=transformed_data,
        )
```

### Rule S-002: No Thread State Mutation
```python
class MyStage:
    async def execute(self, context, capability_port) -> StageResult:
        # ❌ WRONG: Direct mutation
        thread.state["result"] = my_result
        
        # ✅ CORRECT: Return result as stage output
        return StageResult(
            status="completed",
            semantic_output=my_result,
        )
```

---

## Loop Switching Rules

### Rule LS-001: Replace, Don't Nest
```python
# ❌ WRONG: Nested loop execution
class TaskLoop:
    def decide(self, snapshot):
        planning_loop = PlanningLoop(...)
        return planning_loop.decide(snapshot)  # NO!

# ✅ CORRECT: Explicit replacement
def decide(self, snapshot) -> LoopDecision:
    if should_switch_to_planning():
        return LoopDecision.switch_loop(
            target_loop_definition=PlanningLoopDefinition(...),
        )
```

### Rule LS-002: Thread Identity Preserved
```python
# When Loop switches from TaskLoop → RecoveryLoop:
thread_id = "task-001"  # SAME thread ID!

# ❌ WRONG: Creating new thread on loop switch
new_thread = create_thread()
new_thread.id = "task-001-recovery"

# ✅ CORRECT: Same thread, different loop policy
return LoopDecision.switch_loop(
    target_loop_definition=RecoveryLoopDefinition(...),
)
```

---

## Anti-Patterns Prohibited

### AP-001: Monolithic AgenticLoop

**Pattern:**
```python
class AgenticLoop(ExecutionLoop):
    def run(self):
        while True:
            self.perceive()
            self.think()
            self.plan()
            self.act()
            self.evaluate()
            self.reflect()
            sleep(0.1)  # Scheduling inside!
```

**Why Forbidden:** Runtime scheduling belongs to Core, not Loop policy.

**Correct Pattern:**
```python
class AgenticLoopPolicy:
    def decide(self, snapshot):
        if snapshot.active_cycle_id is None:
            return LoopDecision.start_cycle(cycle_definition=PerceptionCycleDef())
        
        # Let Coordinator handle scheduling and advancement
        
        return LoopDecision.yield_execution(...)  # Yield control back to coordinator
```

---

### AP-002: Cycle Chaining

**Pattern:**
```python
class PlanningCycle:
    def execute(self):
        plan = self._formulate_plan()
        
        # ❌ WRONG: Execute execution cycle directly
        return ExecutionCycle(plan).execute()
```

**Why Forbidden:** A Cycle must not select or execute another Cycle.

**Correct Pattern:**
```python
class PlanningCycle:
    async def execute(self, context) -> CycleOutcome:
        plan = self._formulate_plan(context)
        
        # Return outcome with delta for Thread to validate and commit
        return CycleOutcome(
            status="completed",
            semantic_delta=ThreadSemanticDelta(
                expected_thread_revision=context.source_revision,
                change_type="plan_proposed",
                changes={"plan": plan},
            ),
        )
```

---

### AP-003: Loop Nesting

**Pattern:**
```python
class TaskLoop:
    def decide(self, snapshot):
        # ❌ WRONG: Nested policy evaluation
        return PlanningLoop().decide(snapshot)
```

**Why Forbidden:** A Thread has at most one active Loop. Use explicit replacement.

**Correct Pattern:**
```python
class TaskLoop:
    def decide(self, snapshot) -> LoopDecision:
        if should_switch_to_planning():
            # Replace active Loop with PlanningLoop
            return LoopDecision.switch_loop(
                target_loop_definition=PlanningLoopDefinition(...),
            )
        
        # Continue with current loop
        return LoopDecision.start_cycle(...)
```

---

### AP-004: Direct Thread Mutation

**Pattern:**
```python
class MyCycle:
    def execute(self, context):
        # ❌ WRONG: Cycle mutating thread state directly
        self.thread.state["plan"] = plan
        self.thread.revision += 1
        return "success"
```

**Why Forbidden:** Cycles propose; Threads validate and commit.

**Correct Pattern:**
```python
class MyCycle:
    async def execute(self, context) -> CycleOutcome:
        plan = self._formulate_plan(context)
        
        # Propose delta for Thread to validate
        return CycleOutcome(
            status="completed",
            semantic_delta=ThreadSemanticDelta(
                expected_thread_revision=context.source_revision,
                change_type="plan_proposed",
                changes={"plan": plan},
            ),
        )
```

---

### AP-005: Runtime Waiting in Semantic Loop

**Pattern:**
```python
class MonitoringLoop:
    def decide(self, snapshot):
        # ❌ WRONG: Polling and sleeping inside loop
        while not condition_met():
            sleep(1)
        
        return LoopDecision.start_cycle(cycle_definition=ObservationCycle())
```

**Why Forbidden:** Core owns timing and suspension. Loops express intent.

**Correct Pattern:**
```python
class MonitoringLoop:
    def decide(self, snapshot) -> LoopDecision:
        if not condition_met():
            # Request to wait for condition (Core manages timing)
            return LoopDecision.await_condition(
                condition=Condition(timeout_seconds=30),
            )
        
        return LoopDecision.start_cycle(cycle_definition=ObservationCycle())
```

---

### AP-006: Parent Executing Child Inline

**Pattern:**
```python
class ConversationThread:
    def handle_user_request(self, request):
        # ❌ WRONG: Synchronously executing child thread to completion
        child_result = self._execute_task_child(request)
        return child_result  # No async coordination!
```

**Why Forbidden:** Child Threads have independent lifecycles and progression.

**Correct Pattern:**
```python
class ConversationThread:
    def handle_user_request(self, request) -> LoopDecision:
        # Create child thread with its own lifecycle
        child_id = coordinator.create_thread(
            purpose="Execute task",
            loop_id=TaskLoopDefinition(...),
        )
        
        # Record delegation relationship, don't wait for completion
        return LoopDecision.delegate(
            child_thread_id=child_id,
        )
    
    def interpret_outcome(self, snapshot, outcome):
        if outcome.delegation_completed():
            # Child completed - integrate result
            return LoopDecision.start_cycle(cycle_definition=ResponseCycle())
        
        return LoopDecision.yield_execution(...)  # Keep waiting
```

---

### AP-007: RecoveryLoop as Generic Retry Wrapper

**Pattern:**
```python
class TaskExecution:
    def execute(self):
        # ❌ WRONG: Infrastructure retries inside semantic loop
        for attempt in range(5):
            try:
                return transport.send(request)
            except NetworkError:
                sleep(backoff(attempt))
        
        raise Exception("Max retries exceeded")
```

**Why Forbidden:** Infrastructure retry belongs to transport layer, not semantic recovery.

**Correct Pattern:**
```python
class TaskExecutionStage:
    async def execute(self, context) -> StageResult:
        try:
            result = await self._capability.invoke(request)
            
            if result.is_success():
                return StageResult(status="completed", output=result.payload)
            
            # Transport-level retry is handled by capability/transport layer
            
            return StageResult(
                status="failed",
                failure_reason=result.error_message,
            )
        
        except InfrastructureError as e:
            # Infrastructure error (network, timeout, etc.) - let Coordinator handle
            raise e  # Re-raise for infrastructure layer recovery
    
    async def _capability.invoke(self, request):
        return await self._transport.send(request)  # Transport handles retries
```

---

## ThreadDelta Commit Result Codes

| Code | Meaning | Action |
|------|---------|--------|
| `ACCEPTED` | Delta was valid and applied | Thread advanced to new revision |
| `STALE_VERSION` | Expected revision doesn't match current | Re-evaluate with fresh snapshot |
| `INVALID_CONTENT` | Content violates invariants or constraints | Log error, may need RecoveryLoop |
| `REJECTED` | Loop rejected for policy reasons | Apply recovery or retry logic |

---

## Traceability Fields

Every advancement result should include:

```
thread_id              # Which Thread advanced?
loop_id                # Which Loop selected work (if any)?
cycle_id               # Which Cycle executed (if any)?

loop_decision          # Initial decision from Loop
cycle_outcome          # Outcome of Cycle execution (if any)
delta_commit_result    # Result of delta application
continuation_decision  # Continuation after outcome

thread_revision_before # Thread version at start
thread_revision_after  # Thread version after advancement

cycle_executed         # Did a Cycle run?
loop_switched          # Did Loop policy change?
yielded                # Did Thread yield execution?
suspended              # Did Thread become suspended (awaiting)?
completed              # Did Thread complete successfully?
failed                 # Did Thread fail?
```

---

## Summary Checklist

| Rule Category | Check | Status |
|---------------|-------|--------|
| Ownership | Core owns scheduling, not Loop | ✅ |
| Cardinality | ≤1 active Loop per Thread | ✅ |
| Cardinality | ≤1 active Cycle per Thread | ✅ |
| Revision | Stale deltas rejected with STALE_VERSION | ✅ |
| Decisions | Typed enum, not strings | ✅ |
| Cycles | Bounded execution only | ✅ |
| Cycles | Cannot select other cycles | ✅ |
| Threads | Child threads run independently | ✅ |
| Loops | Switch replaces, never nests | ✅ |

---

**Status:** IMPLEMENTED  
**Validation Status:** PASSED