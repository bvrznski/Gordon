# Tests for Benefit Integrators - Phase 4.10.3
# ==================================================================================================

"""
Test suite for Phase 4.10.3 benefit integrators.
"""

from gordon_system.src.agent.components.networks.reward.integration.benefit import (
    GoalBenefitIntegrator,
    KnowledgeBenefitIntegrator,
    EfficiencyBenefitIntegrator,
    ResourceBenefitIntegrator,
    StabilityBenefitIntegrator,
    SocialBenefitIntegrator,
    CompositeBenefitIntegrator,
)
from gordon_system.src.agent.components.networks.reward.integration.base import IntegrationResult


def test_goal_benefit_integrator_positive():
    """Test goal benefit integrator with positive evidence."""
    integrator = GoalBenefitIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "goal-1",
                "context": ("goal:task_completion",),
                "relationship": "supports_reward",
                "confidence": 0.8,
                "uncertainty": 0.2,
            },
            {
                "evidence_id": "non-goal-1",
                "context": ("resource:acquired",),
                "relationship": "unknown",
                "confidence": 0.5,
                "uncertainty": 0.3,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    assert result.value > 0
    assert result.confidence >= 0.8
    assert result.uncertainty <= 0.2


def test_goal_benefit_integrator_mixed():
    """Test goal benefit integrator with mixed evidence."""
    integrator = GoalBenefitIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "goal-support-1",
                "context": ("goal:progress",),
                "relationship": "supports_reward",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
            {
                "evidence_id": "goal-contradict-1",
                "context": ("goal:blocked",),
                "relationship": "contradicts_reward",
                "confidence": 0.7,
                "uncertainty": 0.2,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    # Mixed evidence: one positive (+1) and one negative (-0.5 * weight=1.0)
    # Support has +1.0 contribution at 0.9 confidence
    # Contradict has -0.5 contribution at 0.7 confidence  
    # Combined: (0.9*1.0 + 0.7*(-0.5)) / (0.9 + 0.7) = (0.9 - 0.35) / 1.6 = 0.34
    assert result.value >= 0, "Supports reward should dominate contradicts_reward"


def test_goal_benefit_integrator_empty():
    """Test goal benefit integrator with no relevant evidence."""
    integrator = GoalBenefitIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "non-goal-1",
                "context": ("resource:acquired",),
                "relationship": "unknown",
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    # No goal evidence should give zero or near-zero value
    assert abs(result.value) < 0.5


def test_composite_benefit_integrator():
    """Test composite benefit integrator aggregates all sources."""
    integrator = CompositeBenefitIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "goal-1",
                "context": ("goal:task",),
                "relationship": "supports_reward",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
            {
                "evidence_id": "knowledge-1",
                "evidence_kind": "learning",
                "relationship": "supports_reward",
                "confidence": 0.85,
                "uncertainty": 0.15,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    # Composite should sum individual benefits
    assert result.value >= 0


def test_benefit_integrator_trace():
    """Test that benefit integrators preserve trace."""
    integrator = GoalBenefitIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "goal-1",
                "context": ("goal:test",),
                "relationship": "supports_reward",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert len(result.trace) >= 2
    assert "GOAL_BENEFIT_INTEGRATION_START" in result.trace


if __name__ == "__main__":
    test_goal_benefit_integrator_positive()
    test_goal_benefit_integrator_mixed()
    test_goal_benefit_integrator_empty()
    test_composite_benefit_integrator()
    test_benefit_integrator_trace()
    
    print("All benefit integrator tests passed!")