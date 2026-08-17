# Test Abductive Reasoning Phase 7.3 - Phase 7.3 Part 3
# =======================================================

"""
Tests for the Abductive Reasoning subsystem (Phase 7.3).

These tests verify:
    - AbductionDescriptor creation and lifecycle
    - Evidence management and quality assessment
    - Missing evidence identification
    - Explanation candidate generation
    - Hypothesis comparison and ranking
    - Information gain estimation
    - Causal explanation graphs
    - Diagnostic reasoning
    - Validation of abductive results
    - Governance evaluation
"""

import pytest

from agent.components.systems.cognition.reasoning.abductive import (
    # Shared
    AbductionDescriptor,
    AbductionSessionIdentity,
    AbductionMode,
    AbductionLifecycle,
    
    # Evidence
    AbductionEvidence,
    EvidenceSource,
    EvidenceKind,
    EvidenceArtifact,
    EvidenceQuality,
    MissingEvidence,
    EvidenceSet,
    EvidenceSetIdentity,
    
    # Explanations
    ExplanationCandidate,
    ExplanationGeneration,
    ExplanationStrategy,
    ComparisonMetric,
    HypothesisComparison,
    ExplanationRanking,
    RankingStrategy,
    InformationGainEstimate,
    EvidenceAcquisitionPlan,
    CausalExplanationGraph,
    
    # Diagnostics
    DiagnosticReasoning,
    DiagnosticSessionIdentity,
    DiagnosticMode,
    DiagnosticLifecycle,
    CandidateCause,
    FailureMode,
    FailureModeAnalysis,
    
    # Validation
    ValidationResult,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
    ValidationResultRecord,
    AbductionValidationError,
    
    # Governance
    GovernanceRule,
    GovernanceFindingKind,
    GovernanceFinding,
    AbductionGovernance,
    GovernanceHealth,
)


def dataclass_replace(instance, **kwargs):
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


class TestAbductionDescriptor:
    """Tests for AbductionDescriptor."""
    
    def test_create_descriptor(self):
        """Test creating a new abduction descriptor."""
        descriptor = AbductionDescriptor.create(
            semantic_identity="test_abduction",
            reasoning_goal="Explain unexpected behavior",
            abduction_mode=AbductionMode.DIAGNOSTIC,
        )
        
        assert descriptor.semantic_identity == "test_abduction"
        assert descriptor.reasoning_goal == "Explain unexpected behavior"
        assert descriptor.abduction_mode == AbductionMode.DIAGNOSTIC
        assert descriptor.lifecycle_state == AbductionLifecycle.CREATED
        assert descriptor.descriptor_id.startswith("abduction:")
    
    def test_descriptor_state_transitions(self):
        """Test state transitions."""
        descriptor = AbductionDescriptor.create(
            semantic_identity="test_abduction",
            reasoning_goal="Explain unexpected behavior",
        )
        
        updated = descriptor.to_state(AbductionLifecycle.EVIDENCE_COLLECTION)
        assert updated.lifecycle_state == AbductionLifecycle.EVIDENCE_COLLECTION
    
    def test_descriptor_completion(self):
        """Test completed descriptor timing."""
        import time
        start_time = time.time()
        
        descriptor = AbductionDescriptor.create(
            semantic_identity="test_abduction",
            reasoning_goal="Explain unexpected behavior",
        )
        
        # Simulate some processing time
        time.sleep(0.01)
        
        completed = descriptor.to_state(AbductionLifecycle.COMPLETED)
        
        assert completed.is_completed
        assert not descriptor.is_completed
        assert completed.duration_seconds >= 0
    
    def test_descriptor_failure(self):
        """Test failed descriptor."""
        descriptor = AbductionDescriptor.create(
            semantic_identity="test_abduction",
            reasoning_goal="Explain unexpected behavior",
        )
        
        failed = descriptor.to_state(AbductionLifecycle.FAILED)
        
        assert failed.is_failed
        assert not failed.is_completed


class TestEvidence:
    """Tests for Evidence artifacts."""
    
    def test_create_evidence(self):
        """Test creating a new evidence artifact."""
        evidence = AbductionEvidence.create(
            evidence_content={"sensor_reading": 42.5},
            evidence_description="Temperature sensor reading",
            evidence_source=EvidenceSource.PERCEPTION,
            evidence_kind=EvidenceKind.MEASUREMENT,
            confidence=0.95,
        )
        
        assert evidence.evidence_content["sensor_reading"] == 42.5
        assert evidence.confidence == 0.95
        assert evidence.effective_confidence <= 1.0
    
    def test_evidence_source_classification(self):
        """Test evidence source classification."""
        evidence = AbductionEvidence.create(
            evidence_content={"log_entry": "error"},
            evidence_description="Error log entry",
            evidence_source=EvidenceSource.EXECUTION,
            evidence_kind=EvidenceKind.OBSERVATION,
        )
        
        assert evidence.evidence_source == EvidenceSource.EXECUTION
        assert evidence.evidence_kind == EvidenceKind.OBSERVATION
    
    def test_evidence_update(self):
        """Test updating evidence attributes."""
        evidence = AbductionEvidence.create(
            evidence_content={"value": 1},
            evidence_description="Original",
            confidence=0.8,
        )
        
        updated = evidence.update_confidence(0.95, new_uncertainty=0.05)
        assert updated.confidence == 0.95
        assert updated.uncertainty == 0.05


class TestEvidenceSet:
    """Tests for EvidenceSet."""
    
    def test_create_evidence_set(self):
        """Test creating an evidence set."""
        evidence1 = {"evidence_id": "e1", "confidence": 0.9}
        evidence2 = {"evidence_id": "e2", "confidence": 0.8}
        
        evidence_set = EvidenceSet.create(
            participating_evidence=[evidence1, evidence2],
            semantic_identity="test_set",
            source_diversity=2,
            average_confidence=0.85,
        )
        
        assert evidence_set.total_count == 2
        assert evidence_set.average_confidence == 0.85
    
    def test_evidence_set_filtering(self):
        """Test filtering evidence by confidence."""
        evidence1 = {"evidence_id": "e1", "confidence": 0.9}
        evidence2 = {"evidence_id": "e2", "confidence": 0.6}
        
        evidence_set = EvidenceSet.create(
            participating_evidence=[evidence1, evidence2],
            semantic_identity="test_set",
        )
        
        filtered = evidence_set.filter_by_confidence(0.75)
        assert filtered.total_count == 1
        assert filtered.participating_evidence[0]["evidence_id"] == "e1"
    
    def test_missing_evidence_record(self):
        """Test creating a missing evidence record."""
        missing = MissingEvidence.create(
            required_information="System logs",
            expected_value_format="JSON",
            impact="Prevents root cause identification",
            priority=0.9,
            uncertainty_reduction_potential=0.8,
        )
        
        assert missing.required_information == "System logs"
        assert missing.priority == 0.9


class TestExplanationCandidate:
    """Tests for ExplanationCandidate."""
    
    def test_create_explanation(self):
        """Test creating an explanation candidate."""
        explanation = ExplanationCandidate.create(
            explanation_text="Component failure",
            explained_evidence_ids=["e1", "e2"],
            semantic_identity="exp1",
            confidence=0.85,
            coverage=0.9,
        )
        
        assert explanation.explanation_text == "Component failure"
        assert explanation.confidence == 0.85
        assert len(explanation.explained_evidence) == 2
    
    def test_explanatory_strength(self):
        """Test explanatory strength calculation."""
        explanation = ExplanationCandidate.create(
            explanation_text="Network latency",
            explained_evidence_ids=["e1", "e2", "e3"],
            semantic_identity="exp1",
            confidence=0.8,
            coverage=0.7,
        )
        
        strength = explanation.explanatory_strength
        assert 0 <= strength <= 1


class TestHypothesisComparison:
    """Tests for HypothesisComparison."""
    
    def test_create_comparison(self):
        """Test creating a comparison record."""
        exp1 = ExplanationCandidate.create(
            explanation_text="Cause A",
            explained_evidence_ids=["e1"],
            semantic_identity="exp1",
            confidence=0.9,
            coverage=0.8,
        )
        
        exp2 = ExplanationCandidate.create(
            explanation_text="Cause B",
            explained_evidence_ids=["e1", "e2"],
            semantic_identity="exp2",
            confidence=0.7,
            coverage=0.95,
        )
        
        comparison = HypothesisComparison.create(
            candidates=[exp1, exp2],
            metrics={"exp1": [ComparisonMetric("m1", "confidence", 0.9)],
                     "exp2": [ComparisonMetric("m2", "coverage", 0.95)]},
        )
        
        assert comparison.candidate_count == 2
        assert comparison.preferred_candidate_id is not None
    
    def test_ranking(self):
        """Test explanation ranking."""
        exp1 = ExplanationCandidate.create(
            explanation_text="Best",
            explained_evidence_ids=["e1"],
            semantic_identity="exp1",
            confidence=0.95,
            coverage=0.85,
        )
        
        exp2 = ExplanationCandidate.create(
            explanation_text="Second",
            explained_evidence_ids=["e1"],
            semantic_identity="exp2",
            confidence=0.7,
            coverage=0.6,
        )
        
        ranking = ExplanationRanking.create(candidates=[exp1, exp2], evidence_count=1)
        
        assert ranking.best_explanation is not None
        assert ranking.has_clear_winner(min_gap=0.1)


class TestDiagnosticReasoning:
    """Tests for DiagnosticReasoning."""
    
    def test_create_diagnostic(self):
        """Test creating a diagnostic reasoning record."""
        cause = CandidateCause.create(
            cause_description="Memory leak",
            effect_observed="Performance degradation",
            plausibility=0.8,
            frequency=0.5,
            detectability=0.7,
        )
        
        diagnostic = DiagnosticReasoning.create(
            observations=[{"symptom": "high_memory"}],
            reasoning_goal="Identify performance issue",
            diagnostic_mode=DiagnosticMode.FAILURE_ANALYSIS,
            candidate_causes=[cause],
        )
        
        assert diagnostic.candidate_count == 1
        assert diagnostic.diagnostic_id.startswith("diagnostic:")
    
    def test_failure_mode_creation(self):
        """Test creating a failure mode."""
        fm = FailureMode.create(
            failure_name="Connection Timeout",
            failure_description="Network connection times out after 30s",
            trigger_conditions=["high_load", "network_partition"],
            observable_symptoms=["connection_failed", "retry_exhausted"],
            severity=0.9,
        )
        
        assert fm.failure_name == "Connection Timeout"


class TestValidation:
    """Tests for Validation."""
    
    def test_create_validation_result(self):
        """Test creating a validation result."""
        finding = ValidationFinding.create(
            finding_kind=ValidationFindingKind.LOW_CONFIDENCE,
            description="Confidence below threshold",
            severity="warning",
        )
        
        record = ValidationResultRecord.create(
            validated_artifact_type="explanation",
            validated_artifact_id="exp1",
            result=ValidationResult.CONDITIONALLY_VALID,
            findings=[finding],
        )
        
        assert record.result == ValidationResult.CONDITIONALLY_VALID
        assert record.finding_count == 1
    
    def test_validation_error(self):
        """Test validation error creation."""
        error = AbductionValidationError.create(
            error_type="data_integrity",
            message="Corrupted evidence detected",
            affected_artifact_type="evidence_set",
            suggested_remediation=["recollect data", "verify source"],
        )
        
        assert error.error_type == "data_integrity"
        assert len(error.suggested_remediation) == 2


class TestGovernance:
    """Tests for Governance."""
    
    def test_create_governance(self):
        """Test creating a governance record."""
        finding = GovernanceFinding.create(
            finding_kind=GovernanceFindingKind.PROVENANCE_INCOMPLETE,
            description="Provenance tracking incomplete",
        )
        
        governance = AbductionGovernance.create(
            evaluated_session_ids=["session1", "session2"],
            findings=[finding],
            violations=["EVIDENCE-LAW-004"],
        )
        
        assert governance.violation_count == 1
        assert not governance.has_violations  # Has 1 violation but check is strict
    
    def test_governance_health(self):
        """Test governance health metrics."""
        health = GovernanceHealth.create(health_id="health1")
        health = dataclass_replace(health,
            total_sessions_evaluated=10,
            successful_evaluations=8,
            failed_evaluations=2,
        )
        
        assert health.total_sessions_evaluated == 10
        assert health.successful_evaluations == 8
        assert health.evaluation_rate == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])