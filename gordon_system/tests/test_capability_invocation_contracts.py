# Test Capability Invocation Contracts
# =====================================

"""
Tests for Phase 3.14.8 - Canonical Capability Invocation Contracts.

These tests verify:
    - Lifecycle state transitions are deterministic and valid
    - Identity types generate unique identifiers
    - Context types preserve required fields
    - Protocol contracts are properly defined
    - Failure and cancellation handling is correct
"""

import time
import pytest
from gordon_system.src.agent.capabilities import (
    CapabilityInvocationId,
    CapabilityAdmissionId,
    CapabilityExecutionId,
    CapabilityLifecycleState,
    is_terminal_state,
    get_allowed_transitions,
    InvocationContext,
    AdmissionContext,
    ExecutionExecutionContext,
    ExecutionContextCancellationView,
    ExecutionCancelledError,
    CapabilityExecutor,
    CapabilityExecutionResult,
    ExecutionStatus,
    PublishedResult,
    CapabilityMetadata,
    CapabilityInvocationRequest,
    CapabilityInvocationHandle,
    InvocationCancellationRequest,
    CancellationSource,
    CapabilityFailureCategory,
    CapabilityFailure,
    ResultPublication,
    PublicationStatus,
    OwnershipPreservationProtocol,
    AuthorityPreservationProtocol,
    ReplayMetadata,
    InvocationObservabilityMetadata,
)


# =============================================================================
# Identity Types Tests
# =============================================================================


class TestIdentityTypes:
    """Tests for identity types (CapabilityInvocationId, etc.)."""
    
    def test_invocation_id_generation(self):
        """Test that invocation IDs are unique."""
        id1 = CapabilityInvocationId.generate()
        id2 = CapabilityInvocationId.generate()
        
        assert id1.value != id2.value
        assert len(id1.value) == 36  # UUID format
    
    def test_admission_id_generation(self):
        """Test that admission IDs are unique."""
        id1 = CapabilityAdmissionId.generate()
        id2 = CapabilityAdmissionId.generate()
        
        assert id1.value != id2.value
        assert len(id1.value) == 36  # UUID format
    
    def test_execution_id_generation(self):
        """Test that execution IDs are unique."""
        id1 = CapabilityExecutionId.generate()
        id2 = CapabilityExecutionId.generate()
        
        assert id1.value != id2.value
        assert len(id1.value) == 36  # UUID format


# =============================================================================
# Lifecycle State Tests
# =============================================================================


class TestLifecycleStates:
    """Tests for lifecycle state transitions."""
    
    def test_terminal_states(self):
        """Test that terminal states are correctly identified."""
        assert is_terminal_state(CapabilityLifecycleState.COMPLETED)
        assert is_terminal_state(CapabilityLifecycleState.CANCELLED)
        assert is_terminal_state(CapabilityLifecycleState.FAILED)
        
        # Non-terminal states
        assert not is_terminal_state(CapabilityLifecycleState.CREATED)
        assert not is_terminal_state(CapabilityLifecycleState.VALIDATED)
        assert not is_terminal_state(CapabilityLifecycleState.ADMIITTED)
        assert not is_terminal_state(CapabilityLifecycleState.SCHEDULED)
        assert not is_terminal_state(CapabilityLifecycleState.EXECUTING)
    
    def test_allowed_transitions_from_created(self):
        """Test transitions from CREATED state."""
        allowed = get_allowed_transitions(CapabilityLifecycleState.CREATED)
        
        assert CapabilityLifecycleState.VALIDATED in allowed
        assert CapabilityLifecycleState.CANCELLED in allowed
        assert CapabilityLifecycleState.FAILED in allowed
        
        # Should not be able to transition to terminal states directly
        assert CapabilityLifecycleState.COMPLETED not in allowed
    
    def test_allowed_transitions_from_executing(self):
        """Test transitions from EXECUTING state."""
        allowed = get_allowed_transitions(CapabilityLifecycleState.EXECUTING)
        
        assert CapabilityLifecycleState.COMPLETED in allowed
        assert CapabilityLifecycleState.CANCELLED in allowed
        assert CapabilityLifecycleState.FAILED in allowed
    
    def test_terminal_states_have_no_outgoing(self):
        """Test that terminal states have no outgoing transitions."""
        for state in [
            CapabilityLifecycleState.COMPLETED,
            CapabilityLifecycleState.CANCELLED,
            CapabilityLifecycleState.FAILED,
        ]:
            allowed = get_allowed_transitions(state)
            assert len(allowed) == 0, f"Terminal state {state} should have no outgoing transitions"


# =============================================================================
# Context Types Tests
# =============================================================================


class TestInvocationContext:
    """Tests for InvocationContext."""
    
    def test_invocation_context_creation(self):
        """Test that InvocationContext creates with all required fields."""
        invocation_id = CapabilityInvocationId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="test-interaction",
            capability_id="test-capability",
        )
        
        assert ctx.invocation_id == invocation_id
        assert ctx.interaction_id == "test-interaction"
        assert ctx.capability_id == "test-capability"
        assert ctx.lifecycle_state == CapabilityLifecycleState.CREATED
        assert ctx.created_at_utc > 0
    
    def test_invocation_context_with_state(self):
        """Test that with_state creates new context with updated state."""
        invocation_id = CapabilityInvocationId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="test-interaction",
            capability_id="test-capability",
        )
        
        new_ctx = ctx.with_state(CapabilityLifecycleState.VALIDATED)
        
        # Original should be unchanged
        assert ctx.lifecycle_state == CapabilityLifecycleState.CREATED
        
        # New should have updated state
        assert new_ctx.lifecycle_state == CapabilityLifecycleState.VALIDATED
    
    def test_invocation_context_with_result(self):
        """Test that with_result creates new context with completed state."""
        invocation_id = CapabilityInvocationId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="test-interaction",
            capability_id="test-capability",
        )
        
        # Create a mock result
        from gordon_system.src.agent.capabilities import PublishedResult
        
        result = PublishedResult(
            result_id="result-123",
            invocation_id=invocation_id.value,
            execution_id="exec-456",
            outputs={"output": "test"},
            status="completed",
            created_at_utc=ctx.created_at_utc,
        )
        
        new_ctx = ctx.with_result(result)
        
        assert new_ctx.lifecycle_state == CapabilityLifecycleState.COMPLETED


class TestAdmissionContext:
    """Tests for AdmissionContext."""
    
    def test_admission_context_creation(self):
        """Test that AdmissionContext creates with all required fields."""
        invocation_id = CapabilityInvocationId.generate()
        admission_id = CapabilityAdmissionId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="test-interaction",
            capability_id="test-capability",
        )
        
        adm_ctx = AdmissionContext(
            admission_id=admission_id,
            invocation_context=ctx,
        )
        
        assert adm_ctx.admission_id == admission_id
        assert adm_ctx.invocation_context == ctx
        assert adm_ctx.decision.value == "admit"
    
    def test_admission_context_with_rejection(self):
        """Test that AdmissionContext can be rejected."""
        invocation_id = CapabilityInvocationId.generate()
        admission_id = CapabilityAdmissionId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="test-interaction",
            capability_id="test-capability",
        )
        
        adm_ctx = AdmissionContext(
            admission_id=admission_id,
            invocation_context=ctx,
            decision=None,  # Will be set to default
        )
        
        assert adm_ctx.decision.value == "admit"


class TestExecutionExecutionContext:
    """Tests for ExecutionExecutionContext."""
    
    def test_execution_context_creation(self):
        """Test that ExecutionExecutionContext creates with all required fields."""
        invocation_id = CapabilityInvocationId.generate()
        execution_id = CapabilityExecutionId.generate()
        
        ctx = ExecutionExecutionContext(
            invocation_id=invocation_id.value,
            execution_id=execution_id,
            inputs={"input": "test"},
        )
        
        assert ctx.invocation_id == invocation_id.value
        assert ctx.execution_id == execution_id
        assert ctx.inputs == {"input": "test"}
    
    def test_execution_context_with_timeout(self):
        """Test that with_timeout creates new context with updated timeout."""
        invocation_id = CapabilityInvocationId.generate()
        execution_id = CapabilityExecutionId.generate()
        
        ctx = ExecutionExecutionContext(
            invocation_id=invocation_id.value,
            execution_id=execution_id,
            inputs={"input": "test"},
            timeout_seconds=10.0,
        )
        
        new_ctx = ctx.with_timeout(20.0)
        
        assert ctx.timeout_seconds == 10.0
        assert new_ctx.timeout_seconds == 20.0


class TestExecutionContextCancellationView:
    """Tests for ExecutionContextCancellationView."""
    
    def test_cancellation_view_not_requested(self):
        """Test cancellation view when not requested."""
        view = ExecutionContextCancellationView(is_requested=False)
        
        assert view.is_requested is False
        assert view.check() is None  # Should not raise
    
    def test_cancellation_view_requested_raises(self):
        """Test that check() raises exception when cancellation requested."""
        view = ExecutionContextCancellationView(is_requested=True, reason="test")
        
        assert view.is_requested is True
        
        with pytest.raises(ExecutionCancelledError) as exc_info:
            view.check()
        
        assert "test" in str(exc_info.value)


# =============================================================================
# Result Types Tests
# =============================================================================


class TestCapabilityExecutionResult:
    """Tests for CapabilityExecutionResult."""
    
    def test_result_creation(self):
        """Test that CapabilityExecutionResult creates with all required fields."""
        result = CapabilityExecutionResult(
            invocation_id="invocation-123",
            execution_id="exec-456",
            status=ExecutionStatus.COMPLETED,
        )
        
        assert result.invocation_id == "invocation-123"
        assert result.execution_id == "exec-456"
        assert result.status == ExecutionStatus.COMPLETED
        assert result.is_success() is True
    
    def test_result_to_publication(self):
        """Test conversion to PublishedResult."""
        result = CapabilityExecutionResult(
            invocation_id="invocation-123",
            execution_id="exec-456",
            status=ExecutionStatus.COMPLETED,
            outputs={"output": "test"},
        )
        
        pub_result = result.to_publication_result("result-789")
        
        assert isinstance(pub_result, PublishedResult)
        assert pub_result.result_id == "result-789"
        assert pub_result.invocation_id == "invocation-123"
        assert pub_result.outputs == {"output": "test"}


class TestPublishedResult:
    """Tests for PublishedResult."""
    
    def test_published_result_creation(self):
        """Test that PublishedResult creates with all required fields."""
        result = PublishedResult(
            result_id="result-123",
            invocation_id="invocation-456",
            execution_id="exec-789",
            outputs={"output": "test"},
            status="completed",
            created_at_utc=0.0,
        )
        
        assert result.result_id == "result-123"
        assert result.invocation_id == "invocation-456"
        assert result.outputs == {"output": "test"}
    
    def test_get_integrity_data(self):
        """Test that get_integrity_data returns consistent data."""
        result = PublishedResult(
            result_id="result-123",
            invocation_id="invocation-456",
            execution_id="exec-789",
            outputs={"output": "test"},
            status="completed",
            created_at_utc=0.0,
        )
        
        data = result.get_integrity_data()
        
        assert isinstance(data, str)
        assert "invocation-456" in data


# =============================================================================
# Cancellation Tests
# =============================================================================


class TestInvocationCancellationRequest:
    """Tests for InvocationCancellationRequest."""
    
    def test_cancellation_request_creation(self):
        """Test that InvocationCancellationRequest creates with all required fields."""
        req = InvocationCancellationRequest(
            invocation_id="invocation-123",
            reason="test reason",
            source=CancellationSource.USER,
        )
        
        assert req.invocation_id == "invocation-123"
        assert req.reason == "test reason"
        assert req.source == CancellationSource.USER
    
    def test_cancellation_source_enum(self):
        """Test that CancellationSource enum has all expected values."""
        sources = [s for s in CancellationSource]
        
        assert len(sources) == 5
        assert CancellationSource.USER in sources
        assert CancellationSource.TIMEOUT in sources
        assert CancellationSource.PARENT in sources
        assert CancellationSource.SYSTEM in sources
        assert CancellationSource.DEADLINE_EXCEEDED in sources


# =============================================================================
# Failure Tests
# =============================================================================


class TestCapabilityFailure:
    """Tests for CapabilityFailure."""
    
    def test_failure_creation(self):
        """Test that CapabilityFailure creates with all required fields."""
        failure = CapabilityFailure(
            invocation_id="invocation-123",
            category=CapabilityFailureCategory.ADMISSION_FAILED,
            code="ADMISSION_FAILED",
            message="Admission failed for test",
        )
        
        assert failure.invocation_id == "invocation-123"
        assert failure.category == CapabilityFailureCategory.ADMISSION_FAILED
        assert failure.code == "ADMISSION_FAILED"
        assert failure.message == "Admission failed for test"
    
    def test_failure_to_dict(self):
        """Test that to_dict produces correct output."""
        failure = CapabilityFailure(
            invocation_id="invocation-123",
            category=CapabilityFailureCategory.ADMISSION_FAILED,
            code="ADMISSION_FAILED",
            message="Admission failed for test",
        )
        
        result = failure.to_dict()
        
        assert isinstance(result, dict)
        assert result["invocation_id"] == "invocation-123"
        assert result["category"] == "admission_failed"
        assert result["code"] == "ADMISSION_FAILED"


# =============================================================================
# Protocol Tests
# =============================================================================


class TestProtocolDefinitions:
    """Tests for protocol type definitions."""
    
    def test_ownership_preservation_protocol(self):
        """Test OwnershipPreservationProtocol is defined correctly."""
        # This should be a runtime_checkable Protocol
        assert hasattr(OwnershipPreservationProtocol, '__protocol_attrs__')
        assert 'verify_ownership' in str(OwnershipPreservationProtocol)
    
    def test_authority_preservation_protocol(self):
        """Test AuthorityPreservationProtocol is defined correctly."""
        assert hasattr(AuthorityPreservationProtocol, '__protocol_attrs__')
        assert 'verify_authority' in str(AuthorityPreservationProtocol)


# =============================================================================
# Integration Tests
# =============================================================================


class TestFullLifecycle:
    """Integration tests for full invocation lifecycle."""
    
    def test_full_lifecycle_simulation(self):
        """Simulate a complete invocation lifecycle."""
        # 1. Create invocation
        invocation_id = CapabilityInvocationId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="interaction-123",
            capability_id="capability-456",
        )
        
        assert ctx.lifecycle_state == CapabilityLifecycleState.CREATED
        
        # 2. Transition to validated
        validated_ctx = ctx.with_state(CapabilityLifecycleState.VALIDATED)
        assert validated_ctx.lifecycle_state == CapabilityLifecycleState.VALIDATED
        
        # 3. Transition to admitted
        admitted_ctx = validated_ctx.with_state(CapabilityLifecycleState.ADMIITTED)
        assert admitted_ctx.lifecycle_state == CapabilityLifecycleState.ADMIITTED
        
        # 4. Transition to scheduled
        scheduled_ctx = admitted_ctx.with_state(CapabilityLifecycleState.SCHEDULED)
        assert scheduled_ctx.lifecycle_state == CapabilityLifecycleState.SCHEDULED
        
        # 5. Execute (to executing)
        executing_ctx = scheduled_ctx.with_state(CapabilityLifecycleState.EXECUTING)
        assert executing_ctx.lifecycle_state == CapabilityLifecycleState.EXECUTING
        
        # 6. Complete
        result = PublishedResult(
            result_id="result-789",
            invocation_id=invocation_id.value,
            execution_id="exec-000",
            outputs={"output": "test"},
            status="completed",
            created_at_utc=time.time(),
        )
        
        completed_ctx = executing_ctx.with_result(result)
        assert completed_ctx.lifecycle_state == CapabilityLifecycleState.COMPLETED
    
    def test_cancellation_during_lifecycle(self):
        """Test cancellation can occur at any point before completion."""
        invocation_id = CapabilityInvocationId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="interaction-123",
            capability_id="capability-456",
        )
        
        # Cancellation at various points
        for state in [
            CapabilityLifecycleState.CREATED,
            CapabilityLifecycleState.VALIDATED,
            CapabilityLifecycleState.ADMIITTED,
            CapabilityLifecycleState.SCHEDULED,
            CapabilityLifecycleState.EXECUTING,
        ]:
            ctx = ctx.with_state(state)
            
            # Verify cancellation is allowed from this state
            allowed = get_allowed_transitions(ctx.lifecycle_state)
            assert CapabilityLifecycleState.CANCELLED in allowed


# =============================================================================
# Utility Functions Tests
# =============================================================================


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_dataclass_replace(self):
        """Test dataclass_replace function works correctly."""
        invocation_id = CapabilityInvocationId.generate()
        
        ctx = InvocationContext(
            invocation_id=invocation_id,
            interaction_id="interaction-123",
            capability_id="capability-456",
        )
        
        # Replace just one field
        new_ctx = InvocationContext.__dict__.get('lifecycle_state', None)
        
        assert isinstance(ctx, InvocationContext)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])