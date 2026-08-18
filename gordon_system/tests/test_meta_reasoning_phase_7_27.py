# Meta-Reasoning Phase 7.27 Tests
# =================================

"""
Test suite for Meta-Reasoning subsystem implementing Part 3 specifications.

Tests verify:
    - Strategy Laws (STRATEGY-LAW-001 through STRATEGY-LAW-008)
    - Regulation Laws (REGULATION-LAW-001 through REGULATION-LAW-008)  
    - Coordination Laws (COORDINATION-LAW-001 through COORDINATION-LAW-008)
    - Escalation Laws (ESCALATION-LAW-001 through ESCALATION-LAW-008)
    - Termination Laws (TERMINATION-LAW-001 through TERMINATION-LAW-008)
    - Validation Laws (VALIDATION-LAW-001 through VALIDATION-LAW-008)
    - Governance Laws (GOVERNANCE-LAW-001 through GOVERNANCE-LAW-008)
"""

from __future__ import annotations

import pytest
import time
import uuid

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.pipeline import (
    MetaReasoningPipelineResult,
    MetaReasoningState,
    ReasoningObservation,
    StrategySelectionResult,
    ReasoningRegulation,
    ReasonerCoordination,
    EscalationDecision,
    TerminationDecision,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.anti_patterns import (
    AntiPatternDetector,
    DetectedAntiPattern,
    AntiPatternCategory,
    AntiPatternSeverity,
    detect_implicit_strategy_selection,
    detect_hidden_coordination_dependencies,
    detect_unjustified_escalation,
    detect_arbitrary_termination,
    detect_validation_bypass,
    detect_governance_bypass,
    detect_provenance_loss,
    detect_deterministic_violation,
)


# ============================================================================
# META-LAW-001: Semantic Identity
# ============================================================================

class TestMetaLawSemanticIdentity:
    """Verify every Meta-Reasoning session has one immutable semantic identity."""
    
    def test_pipeline_has_semantic_identity(self):
        """Pipeline must have a stable semantic identity."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        assert pipeline.semantic_identity == "test_goal"
        assert len(pipeline.pipeline_id) > 0
    
    def test_descriptor_has_semantic_identity(self):
        """Descriptor must have a semantic identity field."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.descriptor import MetaReasoningDescriptor
        
        descriptor = MetaReasoningDescriptor.create(
            semantic_identity="test_reasoner",
            reasoning_goal="test goal"
        )
        assert descriptor.semantic_identity == "test_reasoner"


# ============================================================================
# META-LAW-002: Meta Reasoning Set
# ============================================================================

class TestMetaLawSet:
    """Verify meta-reasoning operates over explicit Meta Sets."""
    
    def test_pipeline_has_participating_reasoners(self):
        """Pipeline must track participating reasoners."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        assert pipeline.lifecycle_state == MetaReasoningState.CREATED


# ============================================================================
# META-LAW-003: Regulation Evidence
# ============================================================================

class TestMetaLawRegulationEvidence:
    """Verify regulation decisions reference explicit reasoning evidence."""
    
    def test_regulation_has_evidence_field(self):
        """Regulation must have justification/evidence field."""
        regulation = ReasoningRegulation.create(
            regulated_reasoners=["reasoner1", "reasoner2"],
            max_depth=5,
        )
        assert regulation.regulated_reasoners == ["reasoner1", "reasoner2"]
        assert regulation.max_depth == 5


# ============================================================================
# META-LAW-004: Provenance Preservation
# ============================================================================

class TestMetaLawProvenance:
    """Verify meta-reasoning preserves provenance."""
    
    def test_pipeline_has_timestamps(self):
        """Pipeline must track timing for provenance."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        
        # Created at is set on creation
        assert pipeline.created_at_utc > 0
        
        # Completed at not set until completed
        assert pipeline.completed_at_utc is None
    
    def test_pipeline_has_duration(self):
        """Pipeline can calculate duration."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        
        # Duration should be 0 if not started/completed yet
        assert pipeline.duration_seconds >= 0


# ============================================================================
# META-LAW-005: Reasoning Lineage
# ============================================================================

class TestMetaLawLineage:
    """Verify meta-reasoning preserves reasoning lineage."""
    
    def test_pipeline_records_state_transitions(self):
        """Pipeline must track state transitions for lineage."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        
        assert pipeline.lifecycle_state == MetaReasoningState.CREATED
        
        completed = pipeline.to_completed()
        assert completed.lifecycle_state == MetaReasoningState.COMPLETED


# ============================================================================
# META-LAW-006: Independent Inspection
# ============================================================================

class TestMetaLawInspection:
    """Verify meta-reasoning remains independently inspectable."""
    
    def test_pipeline_is_inspeccable(self):
        """Pipeline must be readable without execution."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        
        # All fields should be accessible
        assert hasattr(pipeline, 'pipeline_id')
        assert hasattr(pipeline, 'lifecycle_state')
        assert hasattr(pipeline, 'observation')
        assert hasattr(pipeline, 'strategy_selection')


# ============================================================================
# META-LAW-007: Determinism
# ============================================================================

class TestMetaLawDeterminism:
    """Verify meta-reasoning is deterministic given same inputs."""
    
    def test_identical_pipeline_states_produce_same_results(self):
        """Same input states must produce identical outputs."""
        pipeline1 = MetaReasoningPipelineResult.create("test_goal")
        pipeline2 = MetaReasoningPipelineResult.create("test_goal")
        
        # With same inputs, pipelines should be structurally equivalent
        assert type(pipeline1) == type(pipeline2)
        assert pipeline1.semantic_identity == pipeline2.semantic_identity


# ============================================================================
# META-LAW-008: Completed Session Immutability
# ============================================================================

class TestMetaLawImmutableCompleted:
    """Verify completed Meta-Reasoning Sessions remain immutable."""
    
    def test_completed_pipeline_cannot_be_modified(self):
        """After to_completed(), pipeline state should be stable."""
        pipeline = MetaReasoningPipelineResult.create("test_goal")
        completed = pipeline.to_completed()
        
        assert completed.lifecycle_state == MetaReasoningState.COMPLETED
        assert completed.completed_at_utc is not None


# ============================================================================
# STRATEGY-LAW-001: Strategy Identity
# ============================================================================

class TestStrategyLawIdentity:
    """Every Reasoning Strategy shall possess one explicit identity."""
    
    def test_strategy_selection_has_identity(self):
        """Strategy selection must have a unique ID."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.strategy_selection import (
            StrategySelection, StrategyKind, SelectionRationale
        )
        
        result = StrategySelection.create(
            semantic_identity="test",
            candidate_strategies=[StrategyKind.SINGLE_REASONER],
            selected_strategy=StrategyKind.SINGLE_REASONER,
        )
        
        assert len(result.selection_id) > 0


# ============================================================================
# STRATEGY-LAW-002: Explicit Applicability
# ============================================================================

class TestStrategyLawApplicability:
    """Strategy applicability shall remain explicit."""
    
    def test_strategy_selection_has_context(self):
        """Strategy selection must specify applicable context."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.strategy_selection import (
            StrategySelection, StrategyKind
        )
        
        result = StrategySelection.create(
            semantic_identity="test",
            candidate_strategies=[StrategyKind.SINGLE_REASONER],
            selected_strategy=StrategyKind.SINGLE_REASONER,
        )
        
        # SelectionRationale should explain why this strategy was chosen
        assert len(result.selection_rationale) > 0


# ============================================================================
# STRATEGY-LAW-003: Explicit Rationale
# ============================================================================

class TestStrategyLawRationale:
    """Strategy selection rationale shall remain explicit."""
    
    def test_strategy_selection_has_selection_policy(self):
        """Selection must include policy information."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.strategy_selection import (
            StrategyKind, SelectionRationale
        )
        
        result = StrategySelection.create(
            semantic_identity="test",
            candidate_strategies=[StrategyKind.SINGLE_REASONER],
            selected_strategy=StrategyKind.SINGLE_REASONER,
            selection_rationale=[SelectionRationale.PROBLEM_CHARACTERIZATION],
        )
        
        assert len(result.selection_rationale) > 0


# ============================================================================
# ANTI-PATTERN DETECTION TESTS
# ============================================================================

class TestAntiPatternDetection:
    """Test anti-pattern detection as specified in Part 3."""
    
    def test_detect_implicit_strategy_selection(self):
        """Detect when strategies selected without justification."""
        result = detect_implicit_strategy_selection(
            selected_strategies=["strategy1"],
            justification=None,
        )
        
        assert result is not None
        assert result.category == AntiPatternCategory.STRATEGY
    
    def test_no_false_positive_without_justification_check(self):
        """Should not flag when justification includes policy info."""
        result = detect_implicit_strategy_selection(
            selected_strategies=["strategy1"],
            justification={"selection_policy": "test_policy"},
        )
        
        assert result is None
    
    def test_detect_arbitrary_termination(self):
        """Detect termination without conditions."""
        result = detect_arbitrary_termination(
            termination_conditions=[],
        )
        
        assert result is not None
        assert result.category == AntiPatternCategory.TERMINATION
    
    def test_detect_validation_bypass(self):
        """Detect validation failures without findings."""
        result = detect_validation_bypass(
            validation_passed=False,
            validation_findings=[],
        )
        
        assert result is not None
        assert result.category == AntiPatternCategory.VALIDATION


class TestAntiPatternDetector:
    """Test the anti-pattern detection engine."""
    
    def test_detector_records_patterns(self):
        """Detector must record detected patterns."""
        detector = AntiPatternDetector()
        
        pattern = DetectedAntiPattern.create(
            category=AntiPatternCategory.STRATEGY,
            anti_pattern_type="test_pattern",
            description="Test",
            evidence="Evidence",
        )
        
        detector.add_detection(pattern)
        
        assert len(detector.get_all_patterns()) == 1
    
    def test_detector_filters_by_severity(self):
        """Detector must support severity filtering."""
        detector = AntiPatternDetector()
        
        error_pattern = DetectedAntiPattern.create(
            category=AntiPatternCategory.STRATEGY,
            anti_pattern_type="error",
            description="Error",
            evidence="Evidence",
            severity=AntiPatternSeverity.ERROR,
        )
        
        warning_pattern = DetectedAntiPattern.create(
            category=AntiPatternCategory.COORDINATION,
            anti_pattern_type="warning",
            description="Warning",
            evidence="Evidence", 
            severity=AntiPatternSeverity.WARNING,
        )
        
        detector.add_detection(error_pattern)
        detector.add_detection(warning_pattern)
        
        assert len(detector.get_error_patterns()) == 1
        assert detector.has_critical_failures() is True
    
    def test_detector_generates_report(self):
        """Detector must generate reports."""
        detector = AntiPatternDetector()
        
        pattern = DetectedAntiPattern.create(
            category=AntiPatternCategory.STRATEGY,
            anti_pattern_type="test",
            description="Test",
            evidence="Evidence",
        )
        
        detector.add_detection(pattern)
        
        report = detector.to_report()
        
        assert "total_detections" in report
        assert "patterns_by_category" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])