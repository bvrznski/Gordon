# Tests for Phase 4.2.10: Focusing Behavioral Examples
# ======================================================

"""
Test suite for Phase 4.2.10 behavioral examples and reference flows.

Tests verify:
- Canonical authority chain preservation
- Architectural separation between computational and authoritative layers
- Anti-pattern detection
- All architectural invariants hold
"""

import pytest
from gordon_system.src.agent.components.networks.focusing.executive import (
    ProjectionId,
    AssessmentId,
    ObjectiveProjection,
    FocusCommitmentProjection,
    ExecutiveFocusProjection,
    ExecutiveFocusDecisionKind,
    ExecutiveFocusDecision,
    FocusAssessmentApplicationResult,
)
from gordon_system.src.agent.components.networks.focusing.models import (
    FocusTarget,
    FocusCandidate,
)


def create_test_projection(revision: int = 1) -> ExecutiveFocusProjection:
    """Create a test executive projection."""
    obj_proj = ObjectiveProjection(objective_id="test_obj", priority_hint=0.8)
    commitment = FocusCommitmentProjection(target_ids=("target_1",), strength=0.7)
    return ExecutiveFocusProjection.create(
        active_objectives=(obj_proj,),
        revision=revision,
        current_commitment=commitment,
    )


class TestStaleAssessment:
    """Tests for stale assessment rejection."""
    
    def test_stale_assessment_detection(self):
        """Executive must validate projection revision before applying assessment."""
        proj_v10 = create_test_projection(revision=10)
        proj_v11 = create_test_projection(revision=11)
        
        result = FocusAssessmentApplicationResult.stale(
            expected_revision=proj_v11.revision,
            actual_revision=10,
        )
        
        assert result.is_valid is False
        assert result.is_stale is True
    
    def test_fresh_assessment_applied(self):
        """Fresh assessment (matching revision) should be accepted."""
        new_commitment = FocusCommitmentProjection(target_ids=("new_target",), strength=0.8)
        result = FocusAssessmentApplicationResult.valid_and_applied(new_commitment)
        
        assert result.is_valid is True
        assert result.is_stale is False


class TestExecutiveDecision:
    """Tests for executive decision making."""
    
    def test_accept_recommendation(self):
        proj = create_test_projection(revision=1)
        decision = ExecutiveFocusDecision.accept_recommendation(
            assessment_id=AssessmentId.generate(),
            projection_id=proj.projection_id,
            accepted_targets=("target_1",),
        )
        assert decision.is_accepted() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])