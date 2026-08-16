# Memory Lifecycle Tests - Phase 5.1.4 Implementation Verification
# ================================================================
"""
Test suite for the Memory Lifecycle system as specified in Phase 5.1.4.

This module verifies:
    - State definitions and transitions
    - Contract implementations
    - History tracking
    - Admission pipeline
    - Retention policies
    - Archival procedures
    - Supersession semantics
    - Failure handling and recovery

Test Coverage:
    - STATE-LAW-XXX: All state laws from the specification
    - TRANSITION-LAW-XXX: All transition laws
    - CONTRACT-PRINCIPLE-XXX: Contract principles verified
"""

from __future__ import annotations

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

import time
import pytest

# Import lifecycle components
from agent.components.systems.memory.lifecycle.states import (
    LifecycleState,
    TransitionType,
    TransitionTrigger,
    LifecycleTransitionRecord,
    LifecycleStateMachine,
    is_transition_valid,
    get_transition_record,
)

from agent.components.systems.memory.lifecycle.contracts import (
    ContractType,
    TransitionValidationResult,
    AdmissionContract,
    ActivationContract,
    RetentionContract,
    RetentionDecision,
    ArchivalContract,
    SupersessionContract,
    FailureContract,
    RecoveryContract,
)

from agent.components.systems.memory.lifecycle.history import (
    LifecycleHistory,
    LifecycleHistoryStore,
    HistoryEntry,
)


# =============================================================================
# TEST: State Definitions and Transitions
# =============================================================================


class TestLifecycleStates:
    """Test lifecycle state definitions."""
    
    def test_states_exist(self):
        """Verify all canonical states are defined."""
        expected_states = [
            "CANDIDATE", "ACTIVE", "RETAINED", 
            "ARCHIVED", "SUPERSEDED", "FAILED", "RECOVERING"
        ]
        for state_name in expected_states:
            assert hasattr(LifecycleState, state_name)
    
    def test_state_values(self):
        """Verify state enum values are correct."""
        assert LifecycleState.CANDIDATE.value == "candidate"
        assert LifecycleState.ACTIVE.value == "active"
        assert LifecycleState.RETAINED.value == "retained"
        assert LifecycleState.ARCHIVED.value == "archived"
        assert LifecycleState.SUPERSEDED.value == "superseded"
        assert LifecycleState.FAILED.value == "failed"
        assert LifecycleState.RECOVERING.value == "recovering"


class TestLifecycleStateMachine:
    """Test the state machine validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sm = LifecycleStateMachine()
    
    def test_legal_transition_candidate_to_active(self):
        """CANDIDATE -> ACTIVE is legal."""
        assert self.sm.is_legal_transition(
            LifecycleState.CANDIDATE, 
            LifecycleState.ACTIVE
        ) is True
    
    def test_illegal_transition_candidate_to_retained(self):
        """CANDIDATE -> RETAINED is illegal (must go through ACTIVE)."""
        assert self.sm.is_legal_transition(
            LifecycleState.CANDIDATE, 
            LifecycleState.RETAINED
        ) is False
    
    def test_active_can_transition_to_multiple_states(self):
        """ACTIVE can transition to RETAINED, SUPERSEDED, or FAILED."""
        active = LifecycleState.ACTIVE
        
        assert self.sm.is_legal_transition(active, LifecycleState.RETAINED) is True
        assert self.sm.is_legal_transition(active, LifecycleState.SUPERSEDED) is True
        assert self.sm.is_legal_transition(active, LifecycleState.FAILED) is True
    
    def test_failed_can_only_go_to_recovering(self):
        """FAILED can only transition to RECOVERING."""
        failed = LifecycleState.FAILED
        
        assert self.sm.is_legal_transition(failed, LifecycleState.RECOVERING) is True
        assert self.sm.is_legal_transition(failed, LifecycleState.ACTIVE) is False
    
    def test_recovery_path(self):
        """Test full recovery path: FAILED -> RECOVERING -> ACTIVE."""
        failed = LifecycleState.FAILED
        recovering = LifecycleState.RECOVERING
        active = LifecycleState.ACTIVE
        
        assert self.sm.is_legal_transition(failed, recovering) is True
        assert self.sm.is_legal_transition(recovering, active) is True
    
    def test_validate_transition_returns_error(self):
        """Invalid transitions produce error messages."""
        is_valid, error = self.sm.validate_transition(
            LifecycleState.CANDIDATE,
            LifecycleState.RETAINED
        )
        
        assert is_valid is False
        assert error is not None
        assert len(error) > 0
    
    def test_get_legal_next_states(self):
        """Get all legal next states from a given state."""
        active = LifecycleState.ACTIVE
        
        next_states = self.sm.get_legal_next_states(active)
        
        assert LifecycleState.RETAINED in next_states
        assert LifecycleState.SUPERSEDED in next_states
        assert LifecycleState.FAILED in next_states
    
    def test_record_transition(self):
        """Test transition record creation."""
        artifact_id = "test-artifact-123"
        
        record = self.sm.record_transition(
            artifact_id=artifact_id,
            previous_state=LifecycleState.CANDIDATE,
            next_state=LifecycleState.ACTIVE,
            trigger=TransitionTrigger.MEMORY_OPERATION,
            type_=TransitionType.ADMISSION,
        )
        
        assert record.transition_id is not None
        assert record.previous_state == LifecycleState.CANDIDATE
        assert record.next_state == LifecycleState.ACTIVE
        assert record.trigger == TransitionTrigger.MEMORY_OPERATION
        assert record.type_ == TransitionType.ADMISSION
        assert record.validation_passed is True


# =============================================================================
# TEST: Contract Implementations
# =============================================================================


class TestAdmissionContract:
    """Test the admission contract."""
    
    def test_validation_requires_id(self):
        """Admission validation fails without artifact ID."""
        contract = AdmissionContract()
        
        result = contract.validate_admission(
            artifact_id="",
            provenance={"origin": "test"},
        )
        
        assert result.is_valid is False
        assert result.error_code == "MISSING_ID"
    
    def test_validation_requires_provenance(self):
        """Admission validation fails without provenance."""
        contract = AdmissionContract()
        
        result = contract.validate_admission(
            artifact_id="art-123",
            provenance=None,
        )
        
        assert result.is_valid is False
        assert result.error_code == "MISSING_PROVENANCE"
    
    def test_successful_admission(self):
        """Test successful admission."""
        contract = AdmissionContract()
        
        result = contract.execute_admission(
            artifact_id="art-123",
            provenance={"origin": "test", "timestamp_utc": time.time()},
        )
        
        assert result.is_admitted is True
        assert result.artifact_id == "art-123"
        assert result.validation_passed is True
        assert "admission_time_utc" in result.provenance
    
    def test_admission_count(self):
        """Verify admission counter increments."""
        # Note: validate_admission is called first, incrementing the counter,
        # then execute_admission also increments it
        contract = AdmissionContract()
        
        initial_count = contract.admission_count
        
        contract.execute_admission(
            artifact_id="art-123",
            provenance={"origin": "test"},
        )
        
        # The counter should increase (validate + execute both count)
        assert contract.admission_count >= initial_count + 1


class TestActivationContract:
    """Test the activation contract."""
    
    def test_candidate_to_active(self):
        """CANDIDATE can be activated to ACTIVE."""
        contract = ActivationContract()
        
        is_valid, error = contract.validate_activation(
            artifact_id="art-123",
            current_state=LifecycleState.CANDIDATE.value,
        )
        
        assert is_valid is True
        assert error is None
    
    def test_active_remains_active(self):
        """ACTIVE stays ACTIVE (refresh)."""
        contract = ActivationContract()
        
        is_valid, error = contract.validate_activation(
            artifact_id="art-123",
            current_state=LifecycleState.ACTIVE.value,
        )
        
        assert is_valid is True
    
    def test_failed_cannot_be_activated(self):
        """FAILED artifacts cannot be activated (must recover first)."""
        contract = ActivationContract()
        
        is_valid, error = contract.validate_activation(
            artifact_id="art-123",
            current_state=LifecycleState.FAILED.value,
        )
        
        assert is_valid is False
        assert "recovered" in error.lower()


class TestRetentionContract:
    """Test the retention contract."""
    
    def test_default_thresholds(self):
        """Default thresholds produce expected results."""
        contract = RetentionContract(
            default_retention_period=86400,
            importance_threshold=0.5,
            utility_threshold=0.5,
            stability_threshold=0.5,
        )
        
        decision = contract.evaluate_retention(
            artifact_id="art-123",
            current_state="active",
            semantic_content={"key": "value"},
        )
        
        assert isinstance(decision, RetentionDecision)
    
    def test_high_importance_is_retained(self):
        """High importance artifacts are retained."""
        contract = RetentionContract(importance_threshold=0.3)
        
        # High content count = high importance
        decision = contract.evaluate_retention(
            artifact_id="art-123",
            current_state="active",
            semantic_content={f"key_{i}": f"value_{i}" for i in range(50)},
        )
        
        assert decision.is_retained is True
        assert decision.importance_score >= 0.3


class TestArchivalContract:
    """Test the archival contract."""
    
    def test_active_can_be_archived(self):
        """ACTIVE artifacts can be archived."""
        contract = ArchivalContract()
        
        is_valid, error = contract.validate_archival(
            artifact_id="art-123",
            current_state=LifecycleState.ACTIVE.value,
        )
        
        assert is_valid is True
    
    def test_retained_can_be_archived(self):
        """RETAINED artifacts can be archived."""
        contract = ArchivalContract()
        
        is_valid, error = contract.validate_archival(
            artifact_id="art-123",
            current_state=LifecycleState.RETAINED.value,
        )
        
        assert is_valid is True
    
    def test_failed_cannot_be_archived(self):
        """FAILED artifacts cannot be archived directly."""
        contract = ArchivalContract()
        
        is_valid, error = contract.validate_archival(
            artifact_id="art-123",
            current_state=LifecycleState.FAILED.value,
        )
        
        assert is_valid is False


class TestSupersessionContract:
    """Test the supersession contract."""
    
    def test_active_can_be_superseded(self):
        """ACTIVE artifacts can be superseded (new revision)."""
        contract = SupersessionContract()
        
        is_valid, error, new_revision = contract.validate_supersession(
            artifact_id="art-123",
            current_state=LifecycleState.ACTIVE.value,
            current_revision=1,
        )
        
        assert is_valid is True
        assert new_revision == 2
    
    def test_non_active_cannot_be_superseded(self):
        """Non-active artifacts cannot be superseded."""
        contract = SupersessionContract()
        
        for state in [LifecycleState.FAILED, LifecycleState.ARCHIVED]:
            is_valid, error, _ = contract.validate_supersession(
                artifact_id="art-123",
                current_state=state.value,
                current_revision=1,
            )
            
            assert is_valid is False


class TestFailureContract:
    """Test the failure contract."""
    
    def test_failure_record_creation(self):
        """Failures are recorded with proper details."""
        contract = FailureContract()
        
        result = contract.execute_failure(
            artifact_id="art-123",
            current_state=LifecycleState.ACTIVE.value,
            failure_type="validation_failed",
            severity=0.75,
            description="Artifact failed validation",
            recoverable=True,
        )
        
        assert result.is_failure is True
        assert result.failure_record.failure_type == "validation_failed"
        assert result.failure_record.severity == 0.75
        assert result.failure_record.recoverable is True
    
    def test_failure_count(self):
        """Failure counter increments."""
        contract = FailureContract()
        
        initial_count = contract.failure_count
        
        contract.execute_failure(
            artifact_id="art-123",
            current_state=LifecycleState.ACTIVE.value,
            failure_type="test_failure",
        )
        
        assert contract.failure_count == initial_count + 1


class TestRecoveryContract:
    """Test the recovery contract."""
    
    def test_only_failed_can_be_recovered(self):
        """Only FAILED artifacts can be recovered."""
        contract = RecoveryContract()
        
        is_valid, error = contract.validate_recovery_initiation(
            artifact_id="art-123",
            current_state=LifecycleState.ACTIVE.value,
        )
        
        assert is_valid is False
        assert "FAILED" in error
    
    def test_failed_can_be_recovered_with_actions(self):
        """Failed artifacts can be recovered when recovery actions are provided."""
        contract = RecoveryContract()
        
        result = contract.execute_recovery(
            artifact_id="art-123",
            current_state=LifecycleState.FAILED.value,
            recovery_method="revalidation",
            recovery_actions=("revalidate_content", "repair_metadata"),
        )
        
        assert result.is_recovered is True


# =============================================================================
# TEST: History Tracking
# =============================================================================


class TestLifecycleHistory:
    """Test lifecycle history tracking."""
    
    def test_initial_state_is_candidate(self):
        """New histories start with candidate state."""
        history = LifecycleHistory(artifact_id="art-123")
        
        assert history.current_state == "candidate"
        assert history.entry_count >= 1
    
    def test_append_entry_creates_new_instance(self):
        """Appending creates new instance (immutable)."""
        history = LifecycleHistory(artifact_id="art-123")
        initial_entries = len(history.get_entries())
        
        updated = history.append_entry(
            next_state="active",
            trigger="admission",
            type_="admission",
        )
        
        # Original should be unchanged
        assert history.entry_count == initial_entries
        
        # Updated should have one more entry
        assert updated.entry_count == initial_entries + 1
    
    def test_history_records_all_transitions(self):
        """History records all state transitions."""
        history = LifecycleHistory(artifact_id="art-123")
        
        # Apply multiple transitions
        history = history.append_entry("active", "admission", "admission")
        history = history.append_entry("retained", "retention", "retention")
        history = history.append_entry("archived", "archival", "archival")
        
        entries = history.get_entries()
        
        assert len(entries) == 4  # Initial + 3 transitions
        assert all(isinstance(e, HistoryEntry) for e in entries)
    
    def test_find_state_changes(self):
        """Find all transitions involving a state."""
        history = LifecycleHistory(artifact_id="art-123")
        
        history = history.append_entry("active", "admission", "admission")
        history = history.append_entry("retained", "retention", "retention")
        
        # Find entries where active was previous state
        active_as_source = history.find_state_changes(
            "active",
            include_from=True,
            include_to=False,
        )
        
        assert len(active_as_source) >= 1
    
    def test_take_snapshot(self):
        """Create a point-in-time snapshot."""
        history = LifecycleHistory(artifact_id="art-123")
        history = history.append_entry("active", "admission", "admission")
        
        snapshot = history.take_snapshot()
        
        assert snapshot.snapshot_id is not None
        assert snapshot.artifact_id == "art-123"
        assert len(snapshot.entries_before) >= 1


class TestLifecycleHistoryStore:
    """Test the history store for multiple artifacts."""
    
    def test_store_manages_multiple_histories(self):
        """Store manages histories for multiple artifacts."""
        store = LifecycleHistoryStore()
        
        # Add entries for different artifacts
        store.append_entry("art-001", "active")
        store.append_entry("art-002", "candidate")
        store.append_entry("art-003", "retained")
        
        assert store.artifact_count == 3
        assert store.total_entry_count >= 6  # At least initial + 1 per artifact
    
    def test_get_current_states(self):
        """Get current states for all tracked artifacts."""
        store = LifecycleHistoryStore()
        
        store.append_entry("art-001", "active")
        store.append_entry("art-002", "archived")
        
        states = store.get_current_states()
        
        assert "art-001" in states
        assert "art-002" in states
    
    def test_find_artifacts_by_state(self):
        """Find all artifacts in a particular state."""
        store = LifecycleHistoryStore()
        
        store.append_entry("art-001", "active")
        store.append_entry("art-002", "active")
        store.append_entry("art-003", "archived")
        
        active_artifacts = store.find_artifacts_by_state("active")
        
        assert len(active_artifacts) == 2
        assert "art-001" in active_artifacts
        assert "art-002" in active_artifacts


# =============================================================================
# TEST: INTEGRATION
# =============================================================================


class TestLifecycleIntegration:
    """Integration tests for complete lifecycle scenarios."""
    
    def test_complete_admission_to_active(self):
        """Test artifact admission through to ACTIVE state."""
        history = LifecycleHistory(artifact_id="test-art-1")
        
        # Initial state is CANDIDATE
        assert history.current_state == "candidate"
        
        # Admit the artifact (CANDIDATE -> ACTIVE)
        history = history.append_entry(
            next_state="active",
            trigger="admission",
            type_="admission",
            validation_passed=True,
        )
        
        assert history.current_state == "active"
    
    def test_admission_to_retained(self):
        """Test artifact progression from ACTIVE to RETAINED."""
        history = LifecycleHistory(artifact_id="test-art-2")
        
        # Admit to ACTIVE
        history = history.append_entry("active", "admission", "admission")
        
        # Apply retention policy (ACTIVE -> RETAINED)
        history = history.append_entry(
            next_state="retained",
            trigger="retention_policy",
            type_="retention",
        )
        
        assert history.current_state == "retained"
    
    def test_supersession_scenario(self):
        """Test supersession scenario: ACTIVE -> SUPERSEDED."""
        contract = SupersessionContract()
        
        # Create initial artifact in ACTIVE state
        history = LifecycleHistory(artifact_id="test-art-3")
        history = history.append_entry("active", "admission", "admission")
        
        # Create new revision (supersede)
        history = history.append_entry(
            next_state="superseded",
            trigger="new_revision",
            type_="supersession",
        )
        
        assert history.current_state == "superseded"
    
    def test_failure_and_recovery_scenario(self):
        """Test failure detection and recovery."""
        # Create artifact in ACTIVE state
        history = LifecycleHistory(artifact_id="test-art-4")
        history = history.append_entry("active", "admission", "admission")
        
        # Simulate failure (ACTIVE -> FAILED)
        failure_contract = FailureContract()
        result = failure_contract.execute_failure(
            artifact_id="test-art-4",
            current_state="active",
            failure_type="validation_error",
        )
        
        assert result.is_failure is True
        history = history.append_entry("failed", "failure_detection", "failure")
        
        # Recover using RecoveryContract (FAILED -> RECOVERING -> ACTIVE)
        recovery_contract = RecoveryContract()
        recovery_result = recovery_contract.execute_recovery(
            artifact_id="test-art-4",
            current_state="failed",
            recovery_method="manual_repair",
            recovery_actions=("fix_validation", "revalidate_content"),
        )
        
        assert recovery_result.is_recovered is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])