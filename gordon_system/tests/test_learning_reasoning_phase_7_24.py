# Test Learning Reasoning - Phase 7.24
# ====================================

"""
Tests for the Learning Reasoning subsystem.

These tests verify:
    - Knowledge acquisition with evidence
    - Concept generalization
    - Model refinement
    - Knowledge integration
    - Learning governance and validation
"""

import pytest
from typing import Dict, List

from gordon_system.src.agent.components.systems.cognition.reasoning.learning.shared.descriptor import (
    LearningDescriptor,
    LearningSessionIdentity,
    LearningMode,
    LearningLifecycle,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.learning.acquisition import (
    KnowledgeAcquisition,
    AcquisitionPolicy,
    AcquisitionMetrics,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.learning.failure import (
    LearningFailure,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.learning.governance import (
    LearningGovernance,
    GovernanceViolation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.learning.validation import (
    LearningValidation,
)


class TestLearningDescriptor:
    """Tests for Learning Descriptor."""
    
    def test_create_descriptor(self):
        """Test creating a learning descriptor."""
        descriptor = LearningDescriptor.create(
            semantic_identity="test_learning",
            learning_goal="Learn new concept",
            learning_mode=LearningMode.ACQUISITION,
        )
        
        assert descriptor.descriptor_id.startswith("learning:")
        assert descriptor.semantic_identity == "test_learning"
        assert descriptor.learning_goal == "Learn new concept"
        assert descriptor.learning_mode == LearningMode.ACQUISITION
        assert descriptor.lifecycle_state == LearningLifecycle.CREATED
    
    def test_descriptor_lifecycle_states(self):
        """Test lifecycle state transitions."""
        descriptor = LearningDescriptor.create(
            semantic_identity="test",
            learning_goal="Test goal",
        )
        
        # Start at CREATED
        assert descriptor.lifecycle_state == LearningLifecycle.CREATED
        
        # Transition to another state
        updated = descriptor.to_state(LearningLifecycle.ACQUIRING)
        assert updated.lifecycle_state == LearningLifecycle.ACQUIRING
    
    def test_descriptor_identity(self):
        """Test session identity creation."""
        identity = LearningSessionIdentity.create(
            semantic_identity="test_session",
            session_number=1,
        )
        
        assert identity.semantic_identity == "test_session"
        assert identity.session_number == 1


class TestKnowledgeAcquisition:
    """Tests for Knowledge Acquisition."""
    
    def test_create_acquisition(self):
        """Test creating a knowledge acquisition."""
        evidence = {"source": "observation", "confidence": 0.9}
        knowledge = {"concept": "new_idea", "value": True}
        
        acquisition = KnowledgeAcquisition.create(
            acquired_knowledge=knowledge,
            supporting_evidence=[evidence],
            confidence=0.9,
        )
        
        assert acquisition.acquisition_id.startswith("acquisition:")
        assert acquisition.acquired_knowledge == knowledge
        assert len(acquisition.supporting_evidence) == 1
        assert acquisition.confidence == 0.9
    
    def test_acquisition_is_valid(self):
        """Test validation of acquisitions."""
        # Valid acquisition
        valid = KnowledgeAcquisition.create(
            acquired_knowledge={"concept": "test"},
            supporting_evidence=[],
            confidence=0.7,
        )
        
        assert valid.is_valid is True
        
        # Invalid acquisition (below threshold)
        invalid = KnowledgeAcquisition.create(
            acquired_knowledge={"concept": "test"},
            supporting_evidence=[],
            confidence=0.3,
        )
        
        assert invalid.is_valid is False
    
    def test_add_evidence(self):
        """Test adding evidence to an acquisition."""
        acquisition = KnowledgeAcquisition.create(
            acquired_knowledge={"concept": "test"},
            supporting_evidence=[{"evidence": 1}],
        )
        
        new_evidence = {"evidence": 2}
        updated = acquisition.with_evidence(new_evidence)
        
        assert len(updated.supporting_evidence) == 2
        assert updated.supporting_evidence[-1] == new_evidence


class TestAcquisitionPolicy:
    """Tests for Acquisition Policy."""
    
    def test_strict_policy(self):
        """Test strict policy settings."""
        policy = AcquisitionPolicy.strict()
        
        assert policy.minimum_evidence == 3
        assert policy.confidence_threshold == 0.8
    
    def test_permissive_policy(self):
        """Test permissive policy settings."""
        policy = AcquisitionPolicy.permissive()
        
        assert policy.minimum_evidence == 1
        assert policy.confidence_threshold == 0.5


class TestLearningFailure:
    """Tests for Learning Failure."""
    
    def test_create_failure(self):
        """Test creating a learning failure."""
        failure = LearningFailure.create(
            failure_kind="insufficient_evidence",
            affected_learning="test_session",
        )
        
        assert failure.failure_id.startswith("learning_failure:")
        assert failure.failure_kind == "insufficient_evidence"
        assert failure.is_recoverable is False
    
    def test_failure_with_recovery(self):
        """Test failure with recovery options."""
        failure = LearningFailure.create(
            failure_kind="timeout",
            affected_learning="test_session",
            recovery_options=["retry", "reduce_scope"],
        )
        
        assert failure.is_recoverable is True
        assert len(failure.recovery_options) == 2
    
    def test_add_diagnostic(self):
        """Test adding diagnostics to a failure."""
        failure = LearningFailure.create(
            failure_kind="test_failure",
            affected_learning="test_session",
        )
        
        updated = failure.with_diagnostic("error_code", 500)
        
        assert updated.diagnostics["error_code"] == 500


class TestLearningGovernance:
    """Tests for Learning Governance."""
    
    def test_create_governance(self):
        """Test creating a governance evaluation."""
        governance = LearningGovernance.create(
            evaluated_sessions=["session_1"],
            governance_policy="strict",
        )
        
        assert governance.governance_id.startswith("governance:")
        assert governance.is_compliant is True
        assert len(governance.evaluated_sessions) == 1
    
    def test_add_violation(self):
        """Test adding a violation."""
        governance = LearningGovernance.create()
        
        updated = governance.add_violation("missing_evidence")
        
        assert updated.is_compliant is False
        assert len(updated.violations) == 1
    
    def test_findings_management(self):
        """Test management of findings."""
        governance = LearningGovernance.create()
        
        updated = governance.with_finding("analysis", "complete")
        
        assert updated.findings["analysis"] == "complete"


class TestLearningValidation:
    """Tests for Learning Validation."""
    
    def test_create_validation(self):
        """Test creating a validation result."""
        validation = LearningValidation.create(
            validated_sessions=["session_1"],
            validation_policy="standard",
        )
        
        assert validation.validation_id.startswith("validation:")
        assert validation.is_valid is True
    
    def test_invalidate(self):
        """Test invalidating a learning session."""
        validation = LearningValidation.create()
        
        updated = validation.invalidate("evidence_insufficient")
        
        assert updated.is_valid is False
        assert updated.confidence_score == 0.0
        assert "invalidation_reason" in updated.findings


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


__all__ = [
    "TestLearningDescriptor",
    "TestKnowledgeAcquisition",
    "TestAcquisitionPolicy",
    "TestLearningFailure",
    "TestLearningGovernance",
    "TestLearningValidation",
]
