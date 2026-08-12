# Thread Lifecycle Tests
# =======================

"""
Tests for Thread lifecycle model and transitions.
"""

import pytest
from agent.execution.threads import (
    ThreadLifecycleState,
    ThreadLifecycleTransitionGraph,
)


class TestThreadLifecycleState:
    """Test ThreadLifecycleState enum."""
    
    def test_all_states_exist(self):
        """All expected states should be defined."""
        states = list(ThreadLifecycleState)
        
        assert len(states) == 7  # CREATED, ACTIVE, SUSPENDED, AWAITING_INPUT, DELEGATED, COMPLETED, INTERRUPTED, TERMINATED
    
    def test_state_values(self):
        """Each state should have a valid string value."""
        for state in ThreadLifecycleState:
            assert isinstance(state.value, str)
            assert len(state.value) > 0


class TestThreadLifecycleTransitionGraph:
    """Test lifecycle transition graph."""
    
    @pytest.fixture
    def graph(self):
        """Create transition graph."""
        return ThreadLifecycleTransitionGraph()
    
    def test_created_to_active_transition(self, graph):
        """CREATED → ACTIVE should be valid."""
        result = graph.is_valid_transition(
            ThreadLifecycleState.CREATED,
            ThreadLifecycleState.ACTIVE
        )
        assert result is True
    
    def test_active_to_suspended_transition(self, graph):
        """ACTIVE → SUSPENDED should be valid."""
        result = graph.is_valid_transition(
            ThreadLifecycleState.ACTIVE,
            ThreadLifecycleState.SUSPENDED
        )
        assert result is True
    
    def test_suspended_to_active_transition(self, graph):
        """SUSPENDED → ACTIVE should be valid."""
        result = graph.is_valid_transition(
            ThreadLifecycleState.SUSPENDED,
            ThreadLifecycleState.ACTIVE
        )
        assert result is True
    
    def test_active_to_completed_transition(self, graph):
        """ACTIVE → COMPLETED should be valid."""
        result = graph.is_valid_transition(
            ThreadLifecycleState.ACTIVE,
            ThreadLifecycleState.COMPLETED
        )
        assert result is True
    
    def test_invalid_transition_rejected(self, graph):
        """Invalid transitions should return False."""
        result = graph.is_valid_transition(
            ThreadLifecycleState.CREATED,
            ThreadLifecycleState.COMPLETED  # Invalid direct transition
        )
        assert result is False
    
    def test_terminal_state_no_transitions(self, graph):
        """Terminal states should have no outgoing transitions."""
        terminal_states = {
            ThreadLifecycleState.COMPLETED,
            ThreadLifecycleState.INTERRUPTED,
            ThreadLifecycleState.TERMINATED,
        }
        
        for state in terminal_states:
            allowed = graph.get_allowed_transitions(state)
            assert len(allowed) == 0
    
    def test_get_transition_returns_object(self, graph):
        """get_transition should return a transition object."""
        transition = graph.get_transition(
            ThreadLifecycleState.CREATED,
            ThreadLifecycleState.ACTIVE
        )
        
        assert transition is not None
        assert transition.from_state == ThreadLifecycleState.CREATED
        assert transition.to_state == ThreadLifecycleState.ACTIVE
    
    def test_get_allowed_transitions(self, graph):
        """get_allowed_transitions should return valid targets."""
        allowed = graph.get_allowed_transitions(ThreadLifecycleState.CREATED)
        
        # Should include ACTIVE
        assert ThreadLifecycleState.ACTIVE in allowed
    
    def test_is_terminal_state(self, graph):
        """is_terminal_state should identify terminal states correctly."""
        assert graph.is_terminal_state(ThreadLifecycleState.COMPLETED) is True
        assert graph.is_terminal_state(ThreadLifecycleState.INTERRUPTED) is True
        assert graph.is_terminal_state(ThreadLifecycleState.ACTIVE) is False


class TestThreadLifecycleTransition:
    """Test lifecycle transition details."""
    
    def test_transition_metadata(self):
        """Transitions should have proper metadata."""
        from agent.execution.threads import (
            ThreadLifecycleState,
            ThreadLifecycleReason,
            ThreadLifecycleTransition,
        )
        
        transition = ThreadLifecycleTransition(
            from_state=ThreadLifecycleState.CREATED,
            to_state=ThreadLifecycleState.ACTIVE,
            requester="core",
            reason=ThreadLifecycleReason.INITIAL_ACTIVATION,
        )
        
        assert transition.from_state == ThreadLifecycleState.CREATED
        assert transition.to_state == ThreadLifecycleState.ACTIVE
        assert transition.requester == "core"
        assert transition.reason == ThreadLifecycleReason.INITIAL_ACTIVATION


class TestThreadLifecycleSnapshot:
    """Test lifecycle snapshot creation."""
    
    def test_snapshot_creation(self):
        """Create and validate a lifecycle snapshot."""
        from agent.execution.threads import (
            ThreadLifecycleState,
            ThreadLifecycleSnapshot,
        )
        
        snapshot = ThreadLifecycleSnapshot(
            thread_id="test-thread-123",
            current_state=ThreadLifecycleState.ACTIVE,
            semantic_version=5,
            has_active_loop=True,
            child_thread_ids=("child-1", "child-2"),
        )
        
        assert snapshot.thread_id == "test-thread-123"
        assert snapshot.current_state == ThreadLifecycleState.ACTIVE
        assert snapshot.semantic_version == 5
        assert snapshot.has_active_loop is True
        assert len(snapshot.child_thread_ids) == 2


class TestThreadLifecycleTransitionRequest:
    """Test lifecycle transition requests."""
    
    def test_request_creation(self):
        """Create and validate a transition request."""
        from agent.execution.threads import (
            ThreadLifecycleState,
            ThreadLifecycleTransitionRequest,
        )
        
        request = ThreadLifecycleTransitionRequest(
            thread_id="test-thread-123",
            from_state=ThreadLifecycleState.ACTIVE,
            to_state=ThreadLifecycleState.SUSPENDED,
            reason="User requested pause",
            timestamp_utc=0.0,
            requested_by="user-456",
        )
        
        assert request.thread_id == "test-thread-123"
        assert request.from_state == ThreadLifecycleState.ACTIVE
        assert request.to_state == ThreadLifecycleState.SUSPENDED
        assert request.reason == "User requested pause"
        assert request.requested_by == "user-456"
    
    def test_request_to_dict(self):
        """to_dict should return serializable format."""
        from agent.execution.threads import (
            ThreadLifecycleState,
            ThreadLifecycleTransitionRequest,
        )
        
        request = ThreadLifecycleTransitionRequest(
            thread_id="test-thread",
            from_state=ThreadLifecycleState.ACTIVE,
            to_state=ThreadLifecycleState.SUSPENDED,
            reason="Test",
        )
        
        result = request.to_dict()
        
        assert isinstance(result, dict)
        assert "thread_id" in result
        assert "from_state" in result
        assert "to_state" in result


class TestThreadLifecycleTransitionResult:
    """Test lifecycle transition results."""
    
    def test_accepted_result(self):
        """Create an accepted transition result."""
        from agent.execution.threads import (
            ThreadLifecycleState,
            ThreadLifecycleTransitionResult,
        )
        
        result = ThreadLifecycleTransitionResult.accepted(
            previous_state=ThreadLifecycleState.ACTIVE,
            current_state=ThreadLifecycleState.SUSPENDED,
            committed_at_utc=1000.0,
        )
        
        assert result.accepted is True
        assert result.previous_state == ThreadLifecycleState.ACTIVE
        assert result.current_state == ThreadLifecycleState.SUSPENDED
        assert result.committed_at_utc == 1000.0
    
    def test_rejected_result(self):
        """Create a rejected transition result."""
        from agent.execution.threads import (
            ThreadLifecycleState,
            ThreadLifecycleTransitionResult,
        )
        
        result = ThreadLifecycleTransitionResult.rejected(
            previous_state=ThreadLifecycleState.ACTIVE,
            reason="Invalid state for transition",
        )
        
        assert result.accepted is False
        assert result.previous_state == result.current_state  # Unchanged
        assert "Invalid" in str(result.rejection_reason)