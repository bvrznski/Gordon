# Task Flow Example (Phase 3.10.10)
# ===================================

"""
Example: Task Planning → Execution → Evaluation Flow

Demonstrates how a TaskThread advances through multiple Loop policies
(planning → execution → evaluation), one bounded Cycle at a time.

Flow:
    TaskThread (PlanningLoop)
        ↓
    PlanningCycle
        ↓
    Plan committed, SWITCH_LOOP to TaskLoop
        ↓
    TaskThread (TaskLoop)
        ↓
    ExecutionCycle
        ↓
    One bounded plan increment performed
        ↓
    EvaluationCycle
        ↓
    Possible outcomes:
        - Success + more work → continue TaskLoop
        - Success + completion → COMPLETE_THREAD
        - Defect detected → RevisionCycle or ExecutionCycle
        - Plan invalid → SWITCH_LOOP to PlanningLoop
        - Recoverable failure → SWITCH_LOOP to RecoveryLoop
        - Unrecoverable failure → FAIL_THREAD

The key insight: The same Thread identity persists while its active Loop
changes from PlanningLoop → TaskLoop → (possibly) RecoveryLoop.

Usage:
    results = run_task_example()
    
    for result in results:
        print(f"Loop: {result['loop_id']}, "
              f"Decision: {result['decision_kind']}")
"""

from agent.execution.coordinator import (
    SimpleExecutionCoordinator,
    LoopDecisionKind,
)
from typing import List, Dict, Any


class TaskPolicy:
    """
    Policy for TaskThread behavior.
    
    Decides which Cycle to select based on thread state and previous outcome.
    """
    
    def __init__(self):
        self._mode = "active"
        self._iteration_count = 0
    
    @property
    def current_mode(self) -> str:
        return self._mode
    
    def decide(self, snapshot: "ThreadSnapshot") -> "LoopDecision":
        """Decide what should happen next."""
        
        if self._iteration_count == 0:
            # First call - start with PlanningCycle for task planning
            decision = LoopDecision.start_cycle(
                cycle_definition={
                    "definition_id": "planning",
                    "name": "PlanningCycle",
                    "description": "Formulate execution plan",
                },
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                rationale="TaskThread starting - need to form plan first",
            )
        else:
            # Subsequent calls
            decision = LoopDecision.yield_execution(
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                reason="Yielding to allow other threads",
            )
        
        self._iteration_count += 1
        return decision
    
    def interpret_outcome(
        self,
        snapshot: "ThreadSnapshot",
        cycle_outcome: Any,
        commit_result: Any,
    ) -> "LoopDecision":
        """Interpret Cycle outcome and decide continuation."""
        
        if not cycle_outcome:
            return LoopDecision.yield_execution(
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                reason="Waiting for first Cycle execution",
            )
        
        if cycle_outcome.get("status") == "completed":
            # Plan completed, switch to TaskLoop for execution
            return LoopDecision.switch_loop(
                target_loop_definition={
                    "definition_id": "task-execution",
                    "name": "TaskExecutionPolicy",
                },
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                reason="PlanningCycle completed, switching to task loop",
            )
        
        # Default: continue
        return LoopDecision.yield_execution(
            thread_id=snapshot.thread_id,
            thread_revision=snapshot.thread_revision,
            reason="Awaiting further processing",
        )


async def run_task_example() -> List[Dict[str, Any]]:
    """
    Run a task flow example demonstrating loop switching.
    
    Returns:
        List of execution result dictionaries showing each advancement
    """
    coordinator = SimpleExecutionCoordinator()
    
    # Step 1: Create TaskThread with PlanningLoop
    thread_id = coordinator.create_thread(
        thread_id="task-001",
        lifecycle_state="created",
        purpose="Complete a task from planning to completion",
        loop_id="planning-loop-001",
    )
    
    # Attach the policy
    policy = TaskPolicy()
    coordinator._loop_policies["planning-loop-001"] = policy
    
    results: List[Dict[str, Any]] = []
    
    # Advance 1: PlanningCycle
    result1 = await coordinator.advance_thread(thread_id)
    results.append({
        "iteration": 1,
        "thread_id": result1.thread_id,
        "loop_id": result1.loop_id.value if result1.loop_id else None,
        "cycle_executed": result1.cycle_executed,
        "decision_kind": result1.loop_decision.decision_kind.value,
    })
    
    # Advance 2: Switch to TaskLoop
    result2 = await coordinator.advance_thread(thread_id)
    results.append({
        "iteration": 2,
        "thread_id": result2.thread_id,
        "loop_id": result2.loop_id.value if result2.loop_id else None,
        "cycle_executed": result2.cycle_executed,
        "decision_kind": result2.loop_decision.decision_kind.value,
    })
    
    # Advance 3: Continue with task loop
    result3 = await coordinator.advance_thread(thread_id)
    results.append({
        "iteration": 3,
        "thread_id": result3.thread_id,
        "loop_id": result3.loop_id.value if result3.loop_id else None,
        "cycle_executed": result3.cycle_executed,
        "decision_kind": result3.loop_decision.decision_kind.value,
    })
    
    return results


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("=" * 60)
        print("TASK FLOW EXAMPLE - Loop Switching")
        print("=" * 60)
        
        results = await run_task_example()
        
        for result in results:
            print(f"\nIteration {result['iteration']}:")
            print(f"  Thread: {result['thread_id']}")
            print(f"  Loop: {result['loop_id']}")
            print(f"  Cycle executed: {result['cycle_executed']}")
            print(f"  Decision: {result['decision_kind']}")
    
    asyncio.run(main())