# Conversation Flow Example (Phase 3.10.10)
# ===========================================

"""
Example: Direct Conversation Response Flow

Demonstrates how a ConversationThread advances through its active Loop,
one bounded Cycle at a time.

Flow:
    ConversationThread
        ↓
    ConversationLoop
        ↓
    InterpretationCycle
        ↓
    ThreadDelta commits interpreted intent
        ↓
    ConversationLoop selects ResponseCycle (via continuation decision)
        ↓
    ResponseCycle produces response artifact
        ↓
    ThreadDelta records commitments
        ↓
    ConversationLoop returns AWAIT_INPUT
        ↓
    ConversationThread becomes waiting

Expected multi-iteration sequence:

Iteration 1:
    active Thread: ConversationThread
    active Loop: ConversationLoop
    selected Cycle: InterpretationCycle
    result: interpreted user input
    continuation: YIELD or START_NEXT_ON_FUTURE_ADVANCE

Iteration 2:
    active Thread: ConversationThread
    active Loop: ConversationLoop
    selected Cycle: ResponseCycle
    result: response artifact
    continuation: AWAIT_INPUT

Do not execute both Cycles inside one Cycle.
Do not let InterpretationCycle call ResponseCycle.

Usage:
    results = run_conversation_example()
    
    # Each result shows what happened in one advancement
    for i, result in enumerate(results):
        print(f"Iteration {i+1}:")
        print(f"  Thread: {result.thread_id}")
        print(f"  Loop: {result.loop_id}")
        print(f"  Cycle executed: {result.cycle_executed}")
        if result.cycle_outcome:
            print(f"  Outcome status: {result.cycle_outcome.status}")
        print(f"  Decision: {result.loop_decision.decision_kind.value}")
"""

from agent.execution.coordinator import (
    SimpleExecutionCoordinator,
    LoopDecisionKind,
)
from agent.execution.loops import BehavioralMode
from typing import List, Dict, Any


class ConversationPolicy:
    """
    Policy for ConversationThread behavior.
    
    Decides which Cycle to select based on thread state and previous outcome.
    """
    
    def __init__(self):
        self._mode = BehavioralMode.ACTIVE
        self._iteration_count = 0
    
    @property
    def current_mode(self) -> BehavioralMode:
        return self._mode
    
    def decide(self, snapshot: "ThreadSnapshot") -> "LoopDecision":
        """Decide what should happen next based on thread state."""
        
        # First iteration - start with InterpretationCycle
        if self._iteration_count == 0:
            decision = LoopDecision.start_cycle(
                cycle_definition={
                    "definition_id": "interpretation",
                    "name": "InterpretationCycle",
                    "stage_definitions": [
                        {"stage_id": "1", "name": "receive_input"},
                        {"stage_id": "2", "name": "parse_intent"},
                        {"stage_id": "3", "name": "extract_entities"},
                    ],
                },
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                rationale="Starting conversation: first interaction",
            )
        else:
            # Check previous outcome to decide continuation
            decision = LoopDecision.yield_execution(
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                reason="Yielding to allow external input or other threads",
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
            # No outcome yet (first call)
            return LoopDecision.yield_execution(
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                reason="Waiting for first Cycle execution",
            )
        
        if cycle_outcome.get("status") == "completed":
            # InterpretationCycle completed, now select ResponseCycle
            self._mode = BehavioralMode.ACTIVE
            
            return LoopDecision.start_cycle(
                cycle_definition={
                    "definition_id": "response",
                    "name": "ResponseCycle",
                    "stage_definitions": [
                        {"stage_id": "1", "name": "generate_response"},
                        {"stage_id": "2", "name": "format_output"},
                    ],
                },
                thread_id=snapshot.thread_id,
                thread_revision=snapshot.thread_revision,
                rationale="Interpretation complete, generating response",
            )
        
        # Default: continue or yield
        return LoopDecision.yield_execution(
            thread_id=snapshot.thread_id,
            thread_revision=snapshot.thread_revision,
            reason="Awaiting external input",
        )


def run_conversation_example() -> List[Dict[str, Any]]:
    """
    Run a conversation flow example and return the advancement results.
    
    This simulates:
        1. Thread creation with ConversationLoop
        2. First advancement: InterpretationCycle
        3. Second advancement: ResponseCycle (continuation)
        4. Third advancement: AWAIT_INPUT
    
    Returns:
        List of execution result dictionaries showing each advancement
    """
    coordinator = SimpleExecutionCoordinator()
    
    # Step 1: Create a ConversationThread with ConversationLoop
    thread_id = coordinator.create_thread(
        thread_id="conv-001",
        lifecycle_state="created",
        purpose="Interact with user in conversation",
        loop_id="conv-loop-001",
    )
    
    # Attach the policy to the loop
    policy = ConversationPolicy()
    coordinator._loop_policies["conv-loop-001"] = policy
    
    # Activate the thread (start with loop)
    results: List[Dict[str, Any]] = []
    
    # Advance 1: First cycle (InterpretationCycle)
    result1 = await coordinator.advance_thread(thread_id)
    results.append({
        "iteration": 1,
        "thread_id": result1.thread_id,
        "loop_id": result1.loop_id.value if result1.loop_id else None,
        "cycle_executed": result1.cycle_executed,
        "cycle_outcome_status": result1.cycle_outcome.status if result1.cycle_outcome else None,
        "decision_kind": result1.loop_decision.decision_kind.value,
    })
    
    # Advance 2: Second cycle (ResponseCycle - continuation)
    result2 = await coordinator.advance_thread(thread_id)
    results.append({
        "iteration": 2,
        "thread_id": result2.thread_id,
        "loop_id": result2.loop_id.value if result2.loop_id else None,
        "cycle_executed": result2.cycle_executed,
        "cycle_outcome_status": result2.cycle_outcome.status if result2.cycle_outcome else None,
        "decision_kind": result2.loop_decision.decision_kind.value,
    })
    
    # Advance 3: Thread now awaits input
    result3 = await coordinator.advance_thread(thread_id)
    results.append({
        "iteration": 3,
        "thread_id": result3.thread_id,
        "loop_id": result3.loop_id.value if result3.loop_id else None,
        "cycle_executed": result3.cycle_executed,
        "cycle_outcome_status": result3.cycle_outcome.status if result3.cycle_outcome else None,
        "decision_kind": result3.loop_decision.decision_kind.value,
    })
    
    return results


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("=" * 60)
        print("CONVERSATION FLOW EXAMPLE")
        print("=" * 60)
        
        results = await run_conversation_example()
        
        for result in results:
            print(f"\nIteration {result['iteration']}:")
            print(f"  Thread: {result['thread_id']}")
            print(f"  Loop: {result['loop_id']}")
            print(f"  Cycle executed: {result['cycle_executed']}")
            if result.get('cycle_outcome_status'):
                print(f"  Outcome status: {result['cycle_outcome_status']}")
            print(f"  Decision: {result['decision_kind']}")
    
    asyncio.run(main())