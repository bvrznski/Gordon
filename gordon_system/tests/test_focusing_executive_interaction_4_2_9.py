# Tests for Phase 4.2.9: Focusing–Executive Interaction Guidelines
# ================================================================

"""
Test suite for the executive interaction contracts of the FocusingNetwork.

Tests verify:
    - Executive input projections are immutable
    - Assessment application results correctly validate projections
    - Decision types are properly distinguished
    - Interaction records track events without ownership
    - Stale assessment detection works correctly
    
NO EXECUTIVE IMPLEMENTATION:
    Tests do NOT implement executive decision-making logic.
    They test the contract interfaces and data structures only.
"""

import pytest
from datetime import datetime, timedelta

# Import Phase 4.2.9 executive interaction contracts
from gordon_system.src.agent.components.networks.focusing.executive import (
    ProjectionId,
    AssessmentId,
    CorrelationId,
    CausationId,
    FocusMode,
    ObjectiveProjection,
    FocusCommitmentProjection,
    FocusPolicyConstraints,
    FocusResourceConstraints,
    ExecutiveFocusProjection,
    FocusAssessmentApplicationResult,
    FocusDecisionModification,
    ExecutiveFocusDecisionKind,
    ExecutiveFocusDecision,
    FocusInteractionRecord,
)


# =============================================================================
# IDENTITY TYPE TESTS
# =============================================================================


class TestIdentityTypes:
    """Test identity type generation and properties."""
    
    def test_projection_id_generates_unique_values(self):
        """ProjectionId should generate unique values."""
        id1 = ProjectionId.generate()
        id2 = ProjectionId.generate()
        
        assert id1.value != id2.value
        assert id1.value.startswith("proj_")
    
    def test_assessment_id_generates_unique_values(self):
        """AssessmentId should generate unique values."""
        id1 = AssessmentId.generate()
        id2 = AssessmentId.generate()
        
        assert id1.value != id2.value
        assert id1.value.startswith("assess_")
    
    def test_correlation_id_generates_unique_values(self):
        """CorrelationId should generate unique values."""
        id1 = CorrelationId.generate()
        id2 = CorrelationId.generate()
        
        assert id1.value != id2.value
        assert id1.value.startswith("corr_")
    
    def test_causation_id_generates_unique_values(self):
        """CausationId should generate unique values."""
        id1 = CausationId.generate()
        id2 = CausationId.generate()
        
        assert id1.value != id2.value
        assert id1.value.startswith("cause_")


# =============================================================================
# FOCUS MODE TESTS
# =============================================================================


class TestFocusMode:
    """Test focus mode constants."""
    
    def test_focus_mode_has_single_target(self):
        """Single target mode should be defined."""
        assert FocusMode.SINGLE_TARGET == "single_target"
    
    def test_focus_mode_has_divided_target(self):
        """Divided target mode should be defined."""
        assert FocusMode.DIVIDED_TARGET == "divided_target"
    
    def test_focus_mode_has_monitoring(self):
        """Monitoring mode should be defined."""
        assert FocusMode.MONITORING == "monitoring"
    
    def test_all_modes_included(self):
        """All modes should be in the ALL tuple."""
        assert FocusMode.SINGLE_TARGET in FocusMode.ALL
        assert FocusMode.DIVIDED_TARGET in FocusMode.ALL
        assert FocusMode.MONITORING in FocusMode.ALL


# =============================================================================
# OBJECTIVE PROJECTION TESTS
# =============================================================================


class TestObjectiveProjection:
    """Test objective projection data structure."""
    
    def test_objective_projection_creates_valid_instance(self):
        """ObjectiveProjection should create a valid instance."""
        obj = ObjectiveProjection(
            objective_id="goal_1",
            priority_hint=0.85,
            completion_status="in_progress",
        )
        
        assert obj.objective_id == "goal_1"
        assert obj.priority_hint == 0.85
        assert obj.completion_status == "in_progress"
    
    def test_objective_projection_defaults(self):
        """ObjectiveProjection should have correct defaults."""
        obj = ObjectiveProjection(objective_id="goal_1")
        
        assert obj.priority_hint is None
        assert obj.deadline_utc is None
        assert obj.completion_status is None
        assert obj.context == {}
    
    def test_objective_projection_is_frozen(self):
        """ObjectiveProjection should be immutable (frozen dataclass)."""
        obj = ObjectiveProjection(objective_id="goal_1")
        
        with pytest.raises(Exception):
            obj.priority_hint = 0.5


# =============================================================================
# FOCUS COMMITMENT PROJECTION TESTS
# =============================================================================


class TestFocusCommitmentProjection:
    """Test focus commitment projection data structure."""
    
    def test_focus_commitment_projection_creates_valid_instance(self):
        """FocusCommitmentProjection should create a valid instance."""
        commit = FocusCommitmentProjection(
            target_ids=("target_1", "target_2"),
            strength=0.75,
        )
        
        assert commit.target_ids == ("target_1", "target_2")
        assert commit.strength == 0.75
    
    def test_focus_commitment_projection_defaults(self):
        """FocusCommitmentProjection should have correct defaults."""
        commit = FocusCommitmentProjection(target_ids=("target_1",))
        
        assert commit.strength == 0.5
        assert commit.estimated_completion_seconds is None


# =============================================================================
# POLICY CONSTRAINTS TESTS
# =============================================================================


class TestPolicyConstraints:
    """Test policy constraints data structure."""
    
    def test_policy_constraints_defaults(self):
        """FocusPolicyConstraints should have correct defaults."""
        constraints = FocusPolicyConstraints()
        
        assert constraints.max_concurrent_targets == 3
        assert constraints.min_precision_threshold == 0.1
        assert constraints.allow_focus_division is False
        assert constraints.prohibit_suppression_of_types == tuple()
        assert constraints.resource_budget_limit == 1.0
    
    def test_policy_constraints_custom(self):
        """FocusPolicyConstraints should accept custom values."""
        constraints = FocusPolicyConstraints(
            max_concurrent_targets=5,
            prohibit_suppression_of_types=("safety_monitor",),
        )
        
        assert constraints.max_concurrent_targets == 5
        assert constraints.prohibit_suppression_of_types == ("safety_monitor",)


# =============================================================================
# RESOURCE CONSTRAINTS TESTS
# =============================================================================


class TestResourceConstraints:
    """Test resource constraints data structure."""
    
    def test_resource_constraints_defaults(self):
        """FocusResourceConstraints should have correct defaults."""
        constraints = FocusResourceConstraints()
        
        assert constraints.available_threads == 4
        assert constraints.max_cpu_percent == 80.0
        assert constraints.memory_limit_mb == 4096
        assert constraints.timeout_seconds is None


# =============================================================================
# EXECUTIVE FOCUS PROJECTION TESTS
# =============================================================================


class TestExecutiveFocusProjection:
    """Test executive focus projection data structure."""
    
    def test_projection_creates_valid_instance(self):
        """ExecutiveFocusProjection should create a valid instance."""
        obj_proj = ObjectiveProjection(objective_id="goal_1")
        proj = ExecutiveFocusProjection.create(
            active_objectives=(obj_proj,),
            revision=1,
        )
        
        assert proj.revision == 1
        assert len(proj.active_objectives) == 1
        assert isinstance(proj.projection_id, ProjectionId)
    
    def test_projection_with_commitment(self):
        """ExecutiveFocusProjection should accept commitment."""
        obj_proj = ObjectiveProjection(objective_id="goal_1")
        commit = FocusCommitmentProjection(target_ids=("target_1",), strength=0.8)
        proj = ExecutiveFocusProjection.create(
            active_objectives=(obj_proj,),
            current_commitment=commit,
        )
        
        assert proj.current_commitment is not None
        assert proj.current_commitment.strength == 0.8
    
    def test_projection_with_revision_update(self):
        """ExecutiveFocusProjection should support revision updates."""
        obj_proj = ObjectiveProjection(objective_id="goal_1")
        proj1 = ExecutiveFocusProjection.create(
            active_objectives=(obj_proj,),
            revision=1,
        )
        
        proj2 = proj1.with_revision(2)
        
        assert proj1.revision == 1
        assert proj2.revision == 2
    
    def test_projection_is_frozen(self):
        """ExecutiveFocusProjection should be immutable."""
        obj_proj = ObjectiveProjection(objective_id="goal_1")
        proj = ExecutiveFocusProjection.create(active_objectives=(obj_proj,))
        
        with pytest.raises(Exception):
            proj.revision = 5


# =============================================================================
# ASSESSMENT APPLICATION RESULT TESTS
# =============================================================================


class TestAssessmentApplicationResult:
    """Test assessment application result data structure."""
    
    def test_valid_and_applied_result(self):
        """Should create a valid and applied result."""
        commit = FocusCommitmentProjection(target_ids=("target_1",))
        result = FocusAssessmentApplicationResult.valid_and_applied(commit)
        
        assert result.is_valid is True
        assert result.is_stale is False
        assert result.action_taken == "applied"
        assert result.resulting_commitment is not None
    
    def test_stale_result(self):
        """Should create a stale assessment result."""
        result = FocusAssessmentApplicationResult.stale(
            expected_revision=5,
            actual_revision=3,
        )
        
        assert result.is_valid is False
        assert result.is_stale is True
        assert "Revision mismatch" in str(result.validation_errors)
    
    def test_incompatible_result(self):
        """Should create an incompatible assessment result."""
        errors = ("Policy violation", "Constraint conflict")
        result = FocusAssessmentApplicationResult.incompatible(errors)
        
        assert result.is_valid is False
        assert result.is_compatible is False
        assert result.action_taken == "rejected"
        assert len(result.validation_errors) == 2
    
    def test_application_allowed(self):
        """Should correctly determine if application is allowed."""
        valid_result = FocusAssessmentApplicationResult.valid_and_applied(
            FocusCommitmentProjection(target_ids=("target_1",))
        )
        stale_result = FocusAssessmentApplicationResult.stale(5, 3)
        
        assert valid_result.is_application_allowed() is True
        assert stale_result.is_application_allowed() is False


# =============================================================================
# EXECUTIVE DECISION KIND TESTS
# =============================================================================


class TestExecutiveFocusDecisionKind:
    """Test executive decision kind constants."""
    
    def test_decision_kinds_defined(self):
        """All expected decision kinds should be defined."""
        kinds = [
            ExecutiveFocusDecisionKind.ACCEPT_FOCUS_RECOMMENDATION,
            ExecutiveFocusDecisionKind.ACCEPT_WITH_MODIFICATION,
            ExecutiveFocusDecisionKind.PRESERVE_CURRENT_FOCUS,
            ExecutiveFocusDecisionKind.DEFER_FOCUS_CHANGE,
            ExecutiveFocusDecisionKind.REQUEST_REASSESSMENT,
            ExecutiveFocusDecisionKind.DIVIDE_FOCUS,
            ExecutiveFocusDecisionKind.RELEASE_FOCUS,
            ExecutiveFocusDecisionKind.REJECT_RECOMMENDATION,
        ]
        
        for kind in kinds:
            assert isinstance(kind, str)
            assert len(kind) > 0


# =============================================================================
# EXECUTIVE DECISION TESTS
# =============================================================================


class TestExecutiveFocusDecision:
    """Test executive decision data structure."""
    
    def test_accept_recommendation_decision(self):
        """Should create an acceptance decision."""
        proj = ExecutiveFocusProjection.create(
            active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
        )
        
        decision = ExecutiveFocusDecision.accept_recommendation(
            assessment_id=AssessmentId.generate(),
            projection_id=proj.projection_id,
            accepted_targets=("target_1",),
            rationale=("High goal relevance", "Low competition"),
        )
        
        assert decision.is_accepted() is True
        assert len(decision.accepted_target_ids) == 1
    
    def test_rejected_decision(self):
        """Should correctly identify rejected decisions."""
        proj = ExecutiveFocusProjection.create(
            active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
        )
        
        decision = ExecutiveFocusDecision(
            decision_kind=ExecutiveFocusDecisionKind.REJECT_RECOMMENDATION,
            assessment_id=AssessmentId.generate(),
            projection_id=proj.projection_id,
        )
        
        assert decision.is_rejected() is True
    
    def test_deferred_decision(self):
        """Should correctly identify deferred decisions."""
        proj = ExecutiveFocusProjection.create(
            active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
        )
        
        decision = ExecutiveFocusDecision(
            decision_kind=ExecutiveFocusDecisionKind.DEFER_FOCUS_CHANGE,
            assessment_id=AssessmentId.generate(),
            projection_id=proj.projection_id,
        )
        
        assert decision.is_deferred() is True


# =============================================================================
# INTERACTION RECORD TESTS
# =============================================================================


class TestFocusInteractionRecord:
    """Test interaction record data structure."""
    
    def test_record_creates_valid_instance(self):
        """FocusInteractionRecord should create a valid instance."""
        proj = ExecutiveFocusProjection.create(
            active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
        )
        
        record = FocusInteractionRecord.from_projection_and_assessment(
            projection=proj,
            assessment_id=AssessmentId.generate(),
            recommended_targets=("target_1", "target_2"),
        )
        
        assert record.projection_revision == proj.revision
        assert len(record.recommended_targets) == 2
    
    def test_record_with_decision(self):
        """FocusInteractionRecord should support decision attachment."""
        proj = ExecutiveFocusProjection.create(
            active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
        )
        
        record = FocusInteractionRecord.from_projection_and_assessment(
            projection=proj,
            assessment_id=AssessmentId.generate(),
            recommended_targets=("target_1",),
        )
        
        decision = ExecutiveFocusDecision.accept_recommendation(
            assessment_id=record.assessment_id,
            projection_id=proj.projection_id,
            accepted_targets=("target_1",),
        )
        
        updated_record = record.with_decision(decision)
        
        assert updated_record.decision_kind == decision.decision_kind
        assert len(updated_record.accepted_targets) == 1


# =============================================================================
# ARCHITECTURAL BOUNDARY TESTS
# =============================================================================


class TestArchitecturalBoundaries:
    """Test that Focusing contracts preserve architectural boundaries."""
    
    def test_no_computation_in_contract_classes(self):
        """
        Contract classes should not contain computational logic.
        
        This ensures Phase 4.2.9 is purely interface definition without
        any implementation logic.
        """
        import inspect
        
        contract_classes = [
            ExecutiveFocusProjection,
            FocusAssessmentApplicationResult,
            ExecutiveFocusDecision,
            FocusInteractionRecord,
        ]
        
        for cls in contract_classes:
            # Check no execute, compute, or process methods exist that would
            # indicate computational behavior rather than data structure
            methods = [m for m in dir(cls) if "exec" in m.lower() or 
                      "comput" in m.lower() or "process" in m.lower()]
            
            user_methods = [m for m in methods if not m.startswith("_")]
            assert len(user_methods) == 0, (
                f"{cls.__name__} should not contain computational methods: "
                f"{user_methods}"
            )
    
    def test_frozen_dataclasses(self):
        """All dataclasses should be frozen (immutable)."""
        objects_to_test = [
            ExecutiveFocusProjection.create(
                active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
            ),
            FocusAssessmentApplicationResult.valid_and_applied(
                FocusCommitmentProjection(target_ids=("target_1",))
            ),
            ExecutiveFocusDecision.accept_recommendation(
                assessment_id=AssessmentId.generate(),
                projection_id=ProjectionId.generate(),
                accepted_targets=("target_1",),
            ),
            FocusInteractionRecord.from_projection_and_assessment(
                projection=ExecutiveFocusProjection.create(
                    active_objectives=(ObjectiveProjection(objective_id="goal_1"),)
                ),
                assessment_id=AssessmentId.generate(),
                recommended_targets=("target_1",),
            ),
        ]
        
        for obj in objects_to_test:
            # Attempt to modify - should raise an exception
            with pytest.raises((TypeError, AttributeError)):
                # Use object.__setattr__ to attempt modification (should fail on frozen dataclasses)
                object.__setattr__(obj, 'test_attr', 'value')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])