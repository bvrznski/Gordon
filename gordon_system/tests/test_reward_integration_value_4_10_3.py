# Tests for Value Integration - Phase 4.10.3
# ==================================================================================================

"""
Test suite for Phase 4.10.3 value integration.
"""

from gordon_system.src.agent.components.networks.reward.integration.value import (
    ValueIntegrationResult,
    ValueIntegrationPolicy,
    ValueIntegrator,
    MixedValue,
)


def test_value_integration_positive():
    """Test value integration with positive net benefit."""
    policy = ValueIntegrationPolicy()
    integrator = ValueIntegrator(policy=policy)
    
    result = integrator.integrate(
        benefit_value=1.0,
        cost_value=0.2,
        confidence=0.9,
        uncertainty=0.1,
    )
    
    assert isinstance(result, ValueIntegrationResult)
    # Positive net value
    assert result.total_value > 0
    # Benefit component preserved
    assert result.benefit_component == 1.0
    # Cost component preserved
    assert result.cost_component == 0.2


def test_value_integration_negative():
    """Test value integration with negative net value."""
    policy = ValueIntegrationPolicy()
    integrator = ValueIntegrator(policy=policy)
    
    result = integrator.integrate(
        benefit_value=0.3,
        cost_value=1.0,
        confidence=0.8,
        uncertainty=0.2,
    )
    
    assert isinstance(result, ValueIntegrationResult)
    # Negative net value
    assert result.total_value < 0


def test_value_integration_neutral():
    """Test value integration with neutral net value."""
    policy = ValueIntegrationPolicy()
    integrator = ValueIntegrator(policy=policy)
    
    result = integrator.integrate(
        benefit_value=1.0,
        cost_value=1.0,
        confidence=1.0,
        uncertainty=0.0,
    )
    
    assert isinstance(result, ValueIntegrationResult)
    # Near-zero net value
    assert abs(result.total_value) < 0.01


def test_mixed_value_representation():
    """Test mixed value preserves both positive and negative components."""
    mixed = MixedValue(positive_component=1.5, negative_component=0.8)
    
    assert mixed.positive_component == 1.5
    assert mixed.negative_component == 0.8
    # Net is positive
    assert mixed.net_value > 0
    assert mixed.is_positive


def test_mixed_value_is_negative():
    """Test mixed value with negative net."""
    mixed = MixedValue(positive_component=0.3, negative_component=1.2)
    
    assert mixed.positive_component == 0.3
    assert mixed.negative_component == 1.2
    # Net is negative
    assert mixed.net_value < 0
    assert mixed.is_negative


def test_mixed_value_is_neutral():
    """Test mixed value with approximately neutral net."""
    mixed = MixedValue(positive_component=1.0, negative_component=1.0)
    
    assert abs(mixed.net_value) < 0.01
    assert mixed.is_neutral


def test_policy_validation():
    """Test policy rejects invalid weights."""
    # Negative weight should raise error
    try:
        ValueIntegrationPolicy(benefit_weight=-1.0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    try:
        ValueIntegrationPolicy(cost_weight=-0.5)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_value_integration_trace():
    """Test that value integration preserves trace."""
    policy = ValueIntegrationPolicy()
    integrator = ValueIntegrator(policy=policy)
    
    result = integrator.integrate(
        benefit_value=0.5,
        cost_value=0.2,
    )
    
    assert len(result.trace) >= 2
    assert "VALUE_INTEGRATION_START" in result.trace


if __name__ == "__main__":
    test_value_integration_positive()
    test_value_integration_negative()
    test_value_integration_neutral()
    test_mixed_value_representation()
    test_mixed_value_is_negative()
    test_mixed_value_is_neutral()
    test_policy_validation()
    test_value_integration_trace()
    
    print("All value integration tests passed!")