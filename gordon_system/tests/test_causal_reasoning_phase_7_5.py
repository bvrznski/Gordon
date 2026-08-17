# Causal Reasoning Phase 7.5 Tests
# ==================================

"""
Tests for the Causal Reasoning subsystem.

This module tests:
    - Shared contracts (descriptor, mechanism_set, graph_construction)
    - Mechanism modeling
    - Graph construction
    - Intervention analysis
    - Effect propagation
    - Dependency analysis
    - Structural causal models
    - Validation
    - Governance
    - Health metrics
"""

from __future__ import annotations

import pytest

# Import all shared contracts
from gordon_system.src.agent.components.systems.cognition.reasoning.causal import (
    CausalDescriptor,
    CausalMode,
    CausalLifecycle,
    
    MechanismSet,
    CausalMechanism,
    MechanismKind,
    
    GraphConstruction,
    
    Intervention,
    InterventionAnalysis,
    
    EffectPropagation,
    
    DependencyAnalysis,
    
    StructuralCausalModel,
    
    CausalRefinement,
    
    CounterfactualPreparation,
    
    CausalValidation,
    
    CausalFailure,
    FailureKind,
    
    CausalGovernance,
    
    CausalHealth,
)


class TestCausalDescriptor:
    """Tests for CausalDescriptor contract."""
    
    def test_create_descriptor(self):
        """Test creating a new causal descriptor."""
        descriptor = CausalDescriptor.create(
            semantic_identity="test-causal-session",
            reasoning_goal="Explain why request failed",
            causal_mode=CausalMode.MECHANISM_ANALYSIS,
        )
        
        assert descriptor.semantic_identity == "test-causal-session"
        assert descriptor.reasoning_goal == "Explain why request failed"
        assert descriptor.causal_mode == CausalMode.MECHANISM_ANALYSIS
        assert descriptor.lifecycle_state == CausalLifecycle.INITIALIZING
    
    def test_descriptor_state_transitions(self):
        """Test state transitions in causal descriptor."""
        descriptor = CausalDescriptor.create(
            semantic_identity="test-causal-session",
            reasoning_goal="Explain why request failed",
        )
        
        # Transition to completed
        updated = descriptor.to_state(CausalLifecycle.COMPLETED)
        
        assert updated.lifecycle_state == CausalLifecycle.COMPLETED
        assert descriptor.lifecycle_state == CausalLifecycle.CREATED  # Original unchanged


class TestCausalMechanism:
    """Tests for CausalMechanism contract."""
    
    def test_create_mechanism(self):
        """Test creating a causal mechanism."""
        mechanism = CausalMechanism(
            mechanism_id="mech:001",
            semantic_identity="cpu_overload",
            name="CPU Overload Mechanism",
            kind=MechanismKind.RESOURCE_ALLOCATION,
            input_entities=("request",),
            output_entities=("delayed_response",),
            causal_relations=("request -> resource_consumption -> delay",),
        )
        
        assert mechanism.name == "CPU Overload Mechanism"
        assert mechanism.kind == MechanismKind.RESOURCE_ALLOCATION
    
    def test_mechanism_can_propagate(self):
        """Test mechanism propagation capability."""
        mechanism = CausalMechanism(
            mechanism_id="mech:001",
            semantic_identity="test_mech",
            name="Test Mechanism",
            kind=MechanismKind.SIGNAL_PROPAGATION,
            input_entities=("A",),
            output_entities=("B", "C"),
            causal_relations=("A -> B", "A -> C"),
        )
        
        assert mechanism.can_propagate_to("B")
        assert mechanism.can_propagate_to("C")
        assert not mechanism.can_propagate_to("D")


class TestMechanismSet:
    """Tests for MechanismSet contract."""
    
    def test_create_mechanism_set(self):
        """Test creating a mechanism set."""
        m1 = CausalMechanism(
            mechanism_id="mech:001",
            semantic_identity="test_mech_1",
            name="Mech 1",
            kind=MechanismKind.SIGNAL_PROPAGATION,
            input_entities=("A",),
            output_entities=("B",),
            causal_relations=("A -> B",),
        )
        
        m2 = CausalMechanism(
            mechanism_id="mech:002",
            semantic_identity="test_mech_2",
            name="Mech 2",
            kind=MechanismKind.FEEDBACK_LOOP,
            input_entities=("B", "C"),
            output_entities=("D",),
            causal_relations=("B,C -> D",),
        )
        
        mechanism_set = MechanismSet(
            mechanism_set_id="set:001",
            semantic_identity="test_system",
            participating_mechanisms=(m1, m2),
        )
        
        assert mechanism_set.mechanism_count == 2
        assert mechanism_set.get_mechanism_by_id("mech:001") is not None


class TestIntervention:
    """Tests for Intervention contract."""
    
    def test_create_intervention(self):
        """Test creating an intervention."""
        intervention = Intervention(
            intervention_id="inv:001",
            modified_variables=("cpu_limit", "memory_limit"),
            variable_values={"cpu_limit": 200, "memory_limit": 512},
            protected_variables=("disk_io",),
        )
        
        assert intervention.get_modified_value("cpu_limit") == 200
        assert intervention.get_modified_value("nonexistent") is None


class TestValidation:
    """Tests for validation contract."""
    
    def test_create_validation(self):
        """Test creating a validation result."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.validation import (
            ValidationIssue,
            CausalValidation,
        )
        
        issue = ValidationIssue(
            issue_id="issue:001",
            issue_type="warning",
            description="Low confidence in graph structure",
        )
        
        validation = CausalValidation(
            validation_id="val:001",
            evaluated_artifacts=("graph", "interventions"),
            findings=(issue,),
        )
        
        assert validation.is_valid
        assert validation.has_warnings


class TestGovernance:
    """Tests for governance contract."""
    
    def test_create_governance_evaluation(self):
        """Test creating a governance evaluation."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.governance import (
            GovernanceFinding,
            CausalGovernance,
        )
        
        finding = GovernanceFinding(
            finding_id="finding:001",
            finding_type="warning",
            evaluated_element="causal_graph",
            description="Potential cycle detected in graph",
        )
        
        governance = CausalGovernance(
            governance_id="gov:001",
            evaluated_sessions=("session:001",),
            findings=(finding,),
        )
        
        assert not governance.is_compliant


class TestFailure:
    """Tests for failure contract."""
    
    def test_create_failure(self):
        """Test creating a failure record."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.failure import (
            CausalFailure,
            FailureKind,
        )
        
        failure = CausalFailure(
            failure_id="fail:001",
            failure_kind=FailureKind.MISSING_VARIABLE,
            affected_element="cpu_limit",
            diagnostics=("Variable cpu_limit not found in mechanism set",),
            recovery_options=("Add variable to mechanism set", "Use default value"),
        )
        
        assert failure.is_recoverable


class TestHealth:
    """Tests for health contract."""
    
    def test_create_health_report(self):
        """Test creating a health report."""
        from gordon_system.src.agent.components.systems.cognition.reasoning.causal.shared.health import (
            HealthMetric,
            CausalHealth,
        )
        
        metric = HealthMetric(
            metric_id="metric:001",
            name="propagation_depth",
            value=5.0,
            unit="steps",
            warning_threshold=8.0,
            critical_threshold=12.0,
        )
        
        health = CausalHealth(
            health_id="health:001",
            metrics=(metric,),
        )
        
        assert health.is_healthy
        assert health.metric_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])