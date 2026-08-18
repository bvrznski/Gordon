# Decision Reasoning Phase 7.19 Test Suite
# =========================================

"""
Test suite for Decision Reasoning implementation.

Tests cover:
    * Option generation and evaluation
    * Utility estimation
    * Commitment formation
    * Confidence calibration
    * Revision handling
    * Evolution tracking
    * Validation, governance, health, diagnostics
"""

import pytest
from gordon_system.src.agent.components.systems.cognition.reasoning.decision import (
    DecisionDescriptor,
    OptionSet,
    OptionEvaluation,
    UtilityComponents,
    UtilityEstimation,
    DecisionCommitment,
    CommitmentFormation,
    ConfidenceMetrics,
    ConfidenceCalibration,
    DecisionRevision,
    DecisionEvolution,
    DecisionValidation,
    DecisionFailure,
    DecisionGovernance,
    DecisionHealth,
    DecisionDiagnostics,
)


class TestDecisionDescriptor:
    """Tests for DecisionDescriptor."""
    
    def test_descriptor_creation(self):
        """Test basic descriptor creation."""
        descriptor = DecisionDescriptor.create(
            decision_goal="test_decision",
            option_set_id="option_set:123",
            lifecycle_state="CREATED",
        )
        
        assert descriptor.decision_identity is not None
        assert descriptor.decision_goal == "test_decision"
        assert descriptor.lifecycle_state == "CREATED"


class TestOptionSet:
    """Tests for OptionSet."""
    
    def test_option_set_creation(self):
        """Test option set creation."""
        options = [
            {"option_id": "opt1", "description": "Option 1"},
            {"option_id": "opt2", "description": "Option 2"},
        ]
        
        option_set = OptionSet.create(
            decision_scope="test_decision",
            participating_options=options,
        )
        
        assert len(option_set.participating_options) == 2
        assert option_set.decision_scope == "test_decision"


class TestUtilityEstimation:
    """Tests for UtilityEstimation."""
    
    def test_utility_components_creation(self):
        """Test utility components creation."""
        components = UtilityComponents.create(
            evaluated_option="opt1",
            expected_benefit=8.0,
            expected_cost=2.0,
            risk_score=0.3,
            uncertainty=0.2,
        )
        
        assert components.net_utility == 6.0
        assert components.expected_benefit > components.expected_cost
    
    def test_utility_estimation_creation(self):
        """Test utility estimation creation."""
        components = UtilityComponents.create(
            evaluated_option="opt1",
            expected_benefit=8.0,
            expected_cost=2.0,
        )
        
        estimation = UtilityEstimation.create(
            evaluated_option="opt1",
            components=[components],
            aggregate_score=6.0,
        )
        
        assert estimation.aggregate_score == 6.0
        assert estimation.component_count == 1


class TestDecisionCommitment:
    """Tests for DecisionCommitment."""
    
    def test_commitment_creation(self):
        """Test commitment creation."""
        commitment = DecisionCommitment.create(
            committed_option="opt1",
            commitment_strength=0.85,
            revision_conditions=["timeout", "new_evidence"],
        )
        
        assert commitment.commitment_strength == 0.85
        assert commitment.is_firm_commitment is True
    
    def test_tentative_commitment(self):
        """Test tentative commitment detection."""
        commitment = DecisionCommitment.create(
            committed_option="opt1",
            commitment_strength=0.6,
        )
        
        assert commitment.is_tentative_commitment is True
        assert commitment.is_firm_commitment is False


class TestConfidenceCalibration:
    """Tests for ConfidenceCalibration."""
    
    def test_confidence_metrics(self):
        """Test confidence metrics calculation."""
        metrics = ConfidenceMetrics.create(
            evaluated_decision="decision1",
            model_agreement=0.9,
            evidence_sufficiency=0.8,
            uncertainty=0.2,
        )
        
        # Should have high confidence (low uncertainty)
        assert metrics.calibrated_confidence > 0.5
        assert metrics.is_high_confidence is True
    
    def test_low_confidence(self):
        """Test low confidence detection."""
        metrics = ConfidenceMetrics.create(
            evaluated_decision="decision1",
            model_agreement=0.3,
            evidence_sufficiency=0.2,
            uncertainty=0.7,
        )
        
        assert metrics.is_low_confidence is True


class TestDecisionRevision:
    """Tests for DecisionRevision."""
    
    def test_revision_creation(self):
        """Test revision creation."""
        revision = DecisionRevision.create(
            revision_identity="decision1",
            previous_decision="opt1",
            revised_decision="opt2",
            revision_reason="new_evidence",
        )
        
        assert revision.is_revision is True
        assert revision.previous_decision == "opt1"
        assert revision.revised_decision == "opt2"


class TestDecisionEvolution:
    """Tests for DecisionEvolution."""
    
    def test_evolution_creation(self):
        """Test evolution creation."""
        evolution = DecisionEvolution.create(
            evolution_identity="decision1",
            triggering_events=["new_evidence"],
            resulting_decision="opt2",
        )
        
        assert evolution.evolution_count == 1


class TestDecisionValidation:
    """Tests for DecisionValidation."""
    
    def test_validation_creation(self):
        """Test validation creation."""
        validation = DecisionValidation.create(
            validated_decision="decision1",
            findings=["option_set_valid"],
            failures=[],
        )
        
        assert validation.validation_passed is True
    
    def test_validation_failure(self):
        """Test validation failure detection."""
        validation = DecisionValidation.create(
            validated_decision="decision1",
            failures=["constraint_violated"],
        )
        
        assert validation.validation_passed is False


class TestDecisionGovernance:
    """Tests for DecisionGovernance."""
    
    def test_governance_evaluation(self):
        """Test governance evaluation."""
        governance = DecisionGovernance.create(
            evaluated_sessions=["session1"],
            findings=[],
            violations=[],
            recommendations=["improve_evidence_quality"],
        )
        
        assert governance.governance_passed is True
    
    def test_governance_violation(self):
        """Test governance violation detection."""
        governance = DecisionGovernance.create(
            evaluated_sessions=["session1"],
            violations=["inconsistent_utility"],
        )
        
        assert governance.governance_passed is False


class TestDecisionHealth:
    """Tests for DecisionHealth."""
    
    def test_health_creation(self):
        """Test health record creation."""
        health = DecisionHealth.create()
        
        assert health.validation_rate == 0.0  # No decisions yet
    
    def test_record_validation(self):
        """Test validation recording."""
        health = DecisionHealth.create()
        health = health.record_validation(True)
        health = health.record_validation(True)
        health = health.record_validation(False)
        
        assert health.total_decisions == 3
        assert health.validation_rate == pytest.approx(0.67, rel=0.1)


class TestDecisionDiagnostics:
    """Tests for DecisionDiagnostics."""
    
    def test_diagnostics_creation(self):
        """Test diagnostics record creation."""
        diagnostics = DecisionDiagnostics.create(evaluated_session="session1")
        
        assert diagnostics.evaluation_duration_seconds == 0.0
    
    def test_add_warning(self):
        """Test warning addition."""
        diagnostics = DecisionDiagnostics.create(evaluated_session="session1")
        diagnostics = diagnostics.add_warning("slow_evaluation")
        
        assert len(diagnostics.warnings) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])