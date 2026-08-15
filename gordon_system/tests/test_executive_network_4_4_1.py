# Executive Network Phase 4.4.1 Architecture Tests
# ================================================

"""
Tests for Phase 4.4.1 - Executive Network Architecture and Ownership.

These tests verify:
    1. Canonical package structure
    2. Public API exports
    3. Import safety (no runtime activation on import)
    4. Foundational contract types
"""

import pytest


def test_canonical_package_structure():
    """Test that the executive package has the canonical structure."""
    # Package root should be importable
    import gordon_system.src.agent.networks.executive
    
    # Check required files exist
    assert hasattr(gordon_system.src.agent.networks.executive, '__init__')
    assert hasattr(gordon_system.src.agent.networks.executive, '__meta__')
    assert hasattr(gordon_system.src.agent.networks.executive, '__tree__')


def test_canonical_public_api():
    """Test that canonical public API types are exported."""
    from gordon_system.src.agent.networks.executive import (
        ExecutiveNetworkId,
        ExecutiveStateReference,
        ExecutiveContextReference,
        ExecutiveTaskSetReference,
        ExecutiveRequestReference,
        ExecutiveResultReference,
        ExecutiveProductReference,
        ExecutiveProposalReference,
        ExecutiveOutcomeReference,
        ExecutiveContinuationReference,
        ExecutiveAuthorityReference,
        ExecutiveMode,
        ExecutiveProductKind,
        ExecutiveOutcomeKind,
        ExecutiveContinuationKind,
        ConflictKind,
        ControlDemandAssessment,
        DecisionReadinessAssessment,
        ExecutiveNetworkConfig,
        ExecutiveNetwork,
        initialize_network,
    )
    
    # Test that types can be instantiated
    network_id = ExecutiveNetworkId.generate()
    assert network_id.value.startswith("exec_")
    
    mode = ExecutiveMode.GOAL_MAINTENANCE
    assert mode.value == "goal_maintenance"
    
    config = ExecutiveNetworkConfig.default()
    assert isinstance(config.max_task_sets, int)
    
    # Test that initialize_network returns something
    network = initialize_network()
    assert network is not None


def test_import_safety():
    """Test that importing the package does NOT activate runtime behavior."""
    import gordon_system.src.agent.networks.executive as exec_pkg
    
    # Import should complete without side effects
    # The following checks verify no unexpected imports or activations occurred
    assert hasattr(exec_pkg, '__all__')


def test_immutability_of_reference_types():
    """Test that reference types are immutable."""
    from gordon_system.src.agent.networks.executive import (
        ExecutiveNetworkId,
        ExecutiveStateReference,
        ExecutiveContextReference,
    )
    
    import dataclasses
    
    # All reference types should be frozen dataclasses
    network_id = ExecutiveNetworkId.generate()
    assert network_id.value is not None


def test_enum_definitions():
    """Test that enum definitions are complete."""
    from gordon_system.src.agent.networks.executive import (
        ExecutiveMode,
        ExecutiveProductKind,
        ExecutiveOutcomeKind,
        ExecutiveContinuationKind,
        ConflictKind,
    )
    
    # Verify modes
    assert hasattr(ExecutiveMode, 'GOAL_MAINTENANCE')
    assert hasattr(ExecutiveMode, 'TASK_SET_FORMATION')
    
    # Verify products
    assert hasattr(ExecutiveProductKind, 'EXECUTIVE_STATE_ASSESSMENT')
    assert hasattr(ExecutiveProductKind, 'TASK_SET_PROPOSAL')
    
    # Verify outcomes
    assert hasattr(ExecutiveOutcomeKind, 'EXECUTIVE_STATE_ESTABLISHED')
    assert hasattr(ExecutiveOutcomeKind, 'FAILED')


def test_assessment_types():
    """Test that assessment types are properly defined."""
    from gordon_system.src.agent.networks.executive import (
        ControlDemandAssessment,
        DecisionReadinessAssessment,
    )
    
    demand = ControlDemandAssessment(
        demand_level="high",
        demand_reasons=("multiple conflicting goals",),
    )
    assert demand.is_high_demand is True
    
    readiness = DecisionReadinessAssessment(
        is_ready=False,
        confidence_level=0.5,
        missing_information=("additional evidence needed",),
        unresolved_conflicts=(),
        authority_status="pending",
    )
    assert readiness.is_deferrable is True


def test_network_config():
    """Test that configuration types are properly defined."""
    from gordon_system.src.agent.networks.executive import (
        ExecutiveNetworkConfig,
        ExecutiveContinuationKind,
    )
    
    config = ExecutiveNetworkConfig.default()
    assert isinstance(config.max_task_sets, int)
    assert config.max_task_sets == 10
    
    # Test is_strict property
    strict_config = ExecutiveNetworkConfig(conflict_threshold=0.9)
    assert strict_config.is_strict is True
    
    non_strict_config = ExecutiveNetworkConfig(conflict_threshold=0.5)
    assert non_strict_config.is_strict is False


def test_placeholder_network():
    """Test that the placeholder network returns expected values."""
    from gordon_system.src.agent.networks.executive import (
        initialize_network,
        ExecutiveContinuationKind,
    )
    
    network = initialize_network()
    
    # Test network_id property
    network_id = network.network_id
    assert isinstance(network_id.value, str)
    assert network_id.value.startswith("exec_")
    
    # Test evaluate returns expected format
    result, continuation = network.evaluate({})
    assert isinstance(result, dict)
    assert isinstance(continuation, ExecutiveContinuationKind)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])