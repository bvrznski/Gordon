# Tests for Loop Architecture Invariants (Phase 3.10.4)
# ======================================================

"""
Tests verifying architectural invariants of the canonical Loop.

Invariants Enforced:
    L-001: Every active Loop belongs to exactly one Thread
    L-002: A Thread has at most one authoritative active Loop
    L-003: Loop evaluation is bounded (not infinite)
    L-004: One evaluation produces exactly one decision
    L-005: Loop does not mutate Thread state directly
    L-006: Loop does not execute Cycle stages
"""

import pytest
from agent.execution.loops import (
    ExecutionLoop,
    StandardPolicy,
    LoopMode,
    DecisionType,
    LoopContext,
    ContinueDecision,
    SuspendDecision,
    CompleteDecision,
    TerminateDecision,
    RequestRecoveryDecision,
)


class TestThreadOwnership:
    """Tests for invariant L-001: Every active Loop belongs to exactly one Thread."""
    
    def test_loop_is_created_for_specific_thread(self):
        """Loop is bound to a single thread at creation time."""
        loop = ExecutionLoop("thread-abc")
        assert loop.thread_id == "thread-abc"
    
    def test_loop_cannot_be_reassigned_to_different_thread(self):
        """Thread ID cannot be changed after creation (immutable property)."""
        loop = ExecutionLoop("thread-x")
        
        # Thread ID should remain consistent
        original_id = loop.thread_id
        
        # Create new context with different thread - evaluation should reject it
        bad_context = LoopContext(
            thread_id="different-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        # Should raise ValueError when context doesn't match loop's thread
        with pytest.raises(ValueError, match="does not match"):
            loop.evaluate(bad_context)


class TestLoopCardinality:
    """Tests for invariant L-002: A Thread has at most one authoritative active Loop."""
    
    def test_single_loop_per_thread(self):
        """Creating multiple loops for same thread creates separate instances."""
        # This is allowed - different loops can be used at different times
        loop1 = ExecutionLoop("thread-a")
        loop2 = ExecutionLoop("thread-a")  # Different instance, same thread
        
        # They are different objects but serve the same thread
        assert loop1.thread_id == loop2.thread_id == "thread-a"
        assert loop1 is not loop2
    
    def test_loop_switch_policy(self):
        """Policy can be switched while serving same thread."""
        loop = ExecutionLoop("thread-b")
        original_policy = loop.current_policy
        
        new_policy = StandardPolicy()
        loop.switch_policy(new_policy)
        
        # Still serves same thread, but different policy
        assert loop.thread_id == "thread-b"
        assert loop.current_policy is new_policy


class TestEvaluationBounded:
    """Tests for invariant L-003: Loop evaluation is bounded."""
    
    def test_evaluate_returns_immediately(self):
        """Evaluate does not block or require async."""
        loop = ExecutionLoop("test-thread")
        context = LoopContext(
            thread_id="test-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        # Evaluate should return immediately without await
        decision = loop.evaluate(context)
        assert decision is not None
    
    def test_evaluate_does_not_loop_indefinitely(self):
        """Evaluate does not contain unbounded loops."""
        import time
        
        loop = ExecutionLoop("fast-thread")
        context = LoopContext(
            thread_id="fast-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        start = time.time()
        decision = loop.evaluate(context)
        elapsed = time.time() - start
        
        # Should complete in less than 100ms (practical boundedness check)
        assert elapsed < 0.1, f"Evaluation took too long: {elapsed}s"


class TestSingleDecisionPerEvaluation:
    """Tests for invariant L-004: One evaluation produces exactly one decision."""
    
    def test_evaluate_returns_single_decision(self):
        """Each evaluate call returns exactly one decision."""
        loop = ExecutionLoop("single-thread")
        context = LoopContext(
            thread_id="single-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        result = loop.evaluate(context)
        
        # Result should be a single decision object, not a list
        assert isinstance(result, (ContinueDecision, SuspendDecision, CompleteDecision, TerminateDecision))
    
    def test_decision_has_single_type(self):
        """Each decision has exactly one decision type."""
        loop = ExecutionLoop("type-thread")
        context = LoopContext(
            thread_id="type-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        decision = loop.evaluate(context)
        
        # Decision type should be a single enum value, not a list
        assert isinstance(decision.decision_type, DecisionType)


class TestNoThreadStateMutation:
    """Tests for invariant L-005: Loop does not mutate Thread state directly."""
    
    def test_evaluate_does_not_accept_thread_object(self):
        """Loop context doesn't allow passing mutable thread objects."""
        loop = ExecutionLoop("immutable-thread")
        
        # Context should only contain immutable/semantic data
        context = LoopContext(
            thread_id="immutable-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        decision = loop.evaluate(context)
        
        # Decision should not require any mutation operations


class TestNoStageExecution:
    """Tests for invariant L-006: Loop does not execute Cycle stages."""
    
    def test_evaluate_returns_decision_not_execution(self):
        """Evaluate returns decision, not execution result."""
        loop = ExecutionLoop("stage-thread")
        context = LoopContext(
            thread_id="stage-thread",
            thread_revision=1,
            current_mode=LoopMode.ACTIVE
        )
        
        decision = loop.evaluate(context)
        
        # Decision should indicate what to do, not execute it
        assert hasattr(decision, 'decision_type')
        assert hasattr(decision, 'thread_revision')


class TestDecisionTypes:
    """Test that all decision types conform to invariants."""
    
    def test_continue_decision_requires_cycle(self):
        """CONTINUE decisions must include a cycle definition."""
        decision = ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=1,
            cycle_definition="test_cycle",
            is_valid=True
        )
        assert decision.cycle_definition is not None
    
    def test_terminal_decisions_cannot_have_cycle(self):
        """TERMINATE/COMPLETE decisions should not select a Cycle."""
        complete = CompleteDecision(
            decision_type=DecisionType.COMPLETE,
            thread_revision=1,
            completion_reason="done"
        )
        
        # For terminal decisions, cycle_definition should be None or not set
        assert complete.cycle_definition is None
    
    def test_decision_has_validity_flag(self):
        """Decisions include validity flag for validation."""
        decision = CompleteDecision(
            decision_type=DecisionType.COMPLETE,
            thread_revision=1,
            completion_reason="test",
            is_valid=True
        )
        assert hasattr(decision, 'is_valid')


class TestPolicyInterface:
    """Test policy contract conformance."""
    
    def test_policy_has_decide_method(self):
        """Policy must have decide() method that returns valid decisions."""
        policy = StandardPolicy()
        
        # Empty context may complete immediately (no cycles available)
        context_empty = LoopContext(
            thread_id="policy-thread",
            thread_revision=1
        )
        
        decision = policy.decide(context_empty)
        assert isinstance(decision, ContinueDecision) or isinstance(decision, CompleteDecision) or isinstance(decision, RequestRecoveryDecision)
    
    def test_policy_has_current_mode_property(self):
        """Policy exposes current_mode as property."""
        policy = StandardPolicy()
        mode = policy.current_mode
        
        assert isinstance(mode, LoopMode)
    
    def test_policy_transition_returns_new_instance(self):
        """transition_mode returns a new policy instance."""
        policy = StandardPolicy()
        
        new_policy = policy.transition_mode(LoopMode.EXPLORATORY)
        
        # Should return different instance with different mode
        assert new_policy is not policy
        assert new_policy.current_mode == LoopMode.EXPLORATORY


class TestStateManagement:
    """Test state management conformance."""
    
    def test_iteration_count_increments(self):
        """Iteration count increments on each evaluate."""
        loop = ExecutionLoop("count-thread")
        
        initial = loop.get_state().iteration_count
        context = LoopContext(thread_id="count-thread", thread_revision=1)
        loop.evaluate(context)
        
        assert loop.get_state().iteration_count == initial + 1
    
    def test_mode_updates_from_decision(self):
        """Mode can be updated based on decision."""
        loop = ExecutionLoop("mode-thread")
        original_mode = loop.current_mode
        
        context = LoopContext(
            thread_id="mode-thread",
            thread_revision=1,
            current_mode=original_mode
        )
        
        # Evaluate (decision may or may not change mode)
        loop.evaluate(context)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])