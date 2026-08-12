# Tests for Loop Architecture (Phase 3.10.4)
# ============================================

"""
Tests for the canonical Loop architecture.

A Loop is not a while loop, event loop, scheduler loop, or runtime dispatcher.
A Loop IS the behavioral policy controller of a Thread.

Loop Responsibilities:
- Behavioral policy: decide what to do next based on thread state + cycle outcome
- Cycle selection policy: choose which cycle to execute
- Continuation policy: decide whether to continue, suspend, complete, etc.
- Interpretation of Cycle outcomes
- Policy-local adaptation state

Loop Must NOT Own:
- Execute reasoning or planning algorithms (Capabilities do this)
- Invoke model runtimes directly (Core does this through Cycles)
- Own Thread continuity (Thread owns this)
- Mutate Thread state arbitrarily (Thread accepts deltas)
- Execute Stage logic (Cycles execute stages)
- Allocate runtime resources (Core does this)
"""

import pytest
from agent.execution.loops import (
    ExecutionLoop,
    StandardPolicy,
    LoopMode,
    DecisionType,
    LoopContext,
    CycleOutcome,
    ContinueDecision,
    SuspendDecision,
    CompleteDecision,
    TerminateDecision,
    RequestRecoveryDecision,
)


class TestBasicLoop:
    """Test basic Loop functionality."""
    
    def test_loop_creates_with_thread_id(self):
        """A Loop is associated with exactly one Thread."""
        loop = ExecutionLoop("thread-123")
        assert loop.thread_id == "thread-123"
    
    def test_loop_uses_standard_policy_by_default(self):
        """Default policy is StandardPolicy when none provided."""
        loop = ExecutionLoop("thread-456")
        assert isinstance(loop.current_policy, StandardPolicy)
    
    def test_loop_current_mode_from_policy(self):
        """Loop's current mode matches its policy's mode."""
        loop = ExecutionLoop("thread-789")
        assert loop.current_mode == LoopMode.ACTIVE
    
    def test_evaluate_returns_decision(self):
        """Evaluate produces a valid decision for context."""
        loop = ExecutionLoop("test-thread")
        context = LoopContext(
            thread_id="test-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        decision = loop.evaluate(context)
        
        assert decision is not None
        assert hasattr(decision, 'decision_type')
        assert hasattr(decision, 'thread_revision')


class TestDecisionTypes:
    """Test decision type semantics."""
    
    def test_continue_decision_is_continuation(self):
        """ContinueDecision.is_continuation returns True."""
        decision = ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=1,
            cycle_definition="test_cycle",
            rationale="Testing continuation"
        )
        assert decision.is_continuation is True
        assert decision.is_terminal is False
    
    def test_complete_decision_is_terminal(self):
        """CompleteDecision.is_terminal returns True."""
        decision = CompleteDecision(
            decision_type=DecisionType.COMPLETE,
            thread_revision=1,
            completion_reason="Test complete"
        )
        assert decision.is_continuation is False
        assert decision.is_terminal is True
    
    def test_terminate_decision_is_terminal(self):
        """TerminateDecision.is_terminal returns True."""
        decision = TerminateDecision(
            decision_type=DecisionType.TERMINATE,
            thread_revision=1,
            termination_reason="Test terminate"
        )
        assert decision.is_continuation is False
        assert decision.is_terminal is True


class TestStandardPolicy:
    """Test StandardPolicy implementation."""
    
    def test_policy_returns_decision_for_empty_context(self):
        """Policy produces decision even with minimal context."""
        policy = StandardPolicy()
        context = LoopContext(
            thread_id="test",
            thread_revision=0
        )
        decision = policy.decide(context)
        
        assert decision is not None
        assert isinstance(decision, (ContinueDecision, CompleteDecision, RequestRecoveryDecision))
    
    def test_policy_handles_pending_interruptions(self):
        """Policy produces suspend decision when interruptions present."""
        policy = StandardPolicy()
        context = LoopContext(
            thread_id="test",
            thread_revision=1,
            pending_interruptions=["int-1", "int-2"]
        )
        decision = policy.decide(context)
        
        assert isinstance(decision, SuspendDecision)


class TestLoopState:
    """Test Loop state management."""
    
    def test_state_tracks_iteration_count(self):
        """Iteration count increments with evaluations."""
        loop = ExecutionLoop("thread-x")
        initial_count = loop.get_state().iteration_count
        
        context = LoopContext(thread_id="thread-x", thread_revision=1)
        loop.evaluate(context)
        
        assert loop.get_state().iteration_count == initial_count + 1
    
    def test_state_tracks_mode(self):
        """Mode can be updated in state."""
        loop = ExecutionLoop("thread-y")
        initial_mode = loop.current_mode
        
        # Create a decision that changes mode
        context = LoopContext(
            thread_id="thread-y",
            thread_revision=1,
            current_mode=initial_mode
        )
        
        # Evaluate (mode may or may not change based on context)
        loop.evaluate(context)


class TestLoopIntegration:
    """Test Loop integration with Thread and Cycle."""
    
    def test_loop_context_contains_thread_info(self):
        """Context provides thread information to policy."""
        context = LoopContext(
            thread_id="integration-thread",
            thread_revision=5,
            current_mode=LoopMode.ACTIVE,
            active_objectives=["obj-1", "obj-2"],
            previous_cycle_outcome=CycleOutcome(
                cycle_id="cycle-99",
                status="completed"
            )
        )
        
        assert context.thread_id == "integration-thread"
        assert context.thread_revision == 5
        assert len(context.active_objectives) == 2
    
    def test_loop_evaluate_validates_thread_id(self):
        """Evaluate rejects context with wrong thread ID."""
        loop = ExecutionLoop("thread-a")
        bad_context = LoopContext(
            thread_id="wrong-thread",  # Different thread
            thread_revision=1
        )
        
        with pytest.raises(ValueError, match="does not match"):
            loop.evaluate(bad_context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])