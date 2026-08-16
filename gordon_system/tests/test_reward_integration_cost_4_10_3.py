# Tests for Cost Integrators - Phase 4.10.3
# ==================================================================================================

"""
Test suite for Phase 4.10.3 cost integrators.
"""

from gordon_system.src.agent.components.networks.reward.integration.cost import (
    TimeCostIntegrator,
    EnergyCostIntegrator,
    ComputeCostIntegrator,
    MemoryCostIntegrator,
    AttentionCostIntegrator,
    OpportunityCostIntegrator,
    RiskCostIntegrator,
    CompositeCostIntegrator,
)
from gordon_system.src.agent.components.networks.reward.integration.base import IntegrationResult


def test_time_cost_integrator():
    """Test time cost integrator."""
    integrator = TimeCostIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "time-1",
                "evidence_kind": "time_duration",
                "relationship": "supports_punishment",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    # Time cost should be positive (cost contributes to negative value)
    assert result.value > 0


def test_composite_cost_integrator():
    """Test composite cost integrator aggregates all sources."""
    integrator = CompositeCostIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "time-1",
                "evidence_kind": "time_duration",
                "relationship": "supports_punishment",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
            {
                "evidence_id": "energy-1",
                "evidence_kind": "energy_usage",
                "relationship": "supports_punishment",
                "confidence": 0.85,
                "uncertainty": 0.15,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    # Composite should sum individual costs
    assert result.value > 0


def test_cost_integrator_empty():
    """Test cost integrator with no relevant evidence."""
    integrator = TimeCostIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "non-time-1",
                "context": ("goal:progress",),
                "relationship": "unknown",
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert isinstance(result, IntegrationResult)
    # No time cost evidence should give zero or near-zero value
    assert abs(result.value) < 0.5


def test_cost_integrator_trace():
    """Test that cost integrators preserve trace."""
    integrator = TimeCostIntegrator()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "time-1",
                "evidence_kind": "duration",
                "relationship": "supports_punishment",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
        )
    }
    
    result = integrator.integrate(evidence_state)
    
    assert len(result.trace) >= 2
    assert "TIME_COST_INTEGRATION_START" in result.trace


if __name__ == "__main__":
    test_time_cost_integrator()
    test_composite_cost_integrator()
    test_cost_integrator_empty()
    test_cost_integrator_trace()
    
    print("All cost integrator tests passed!")