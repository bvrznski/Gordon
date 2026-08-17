# Test Counterfactual Reasoning Phase 7.6 - Phase 7.6 Part 3
# ===========================================================

"""
Tests for the Counterfactual Reasoning subsystem (Phase 7.6).

These tests verify:
    - CounterfactualDescriptor creation and lifecycle
    - World Set construction with reference world
    - Alternative world branching from interventions
    - Intervention pipeline execution
    - Divergence analysis and propagation
    - World comparison between alternatives
    - Validation of counterfactual results
    - Governance evaluation
"""

import pytest

from gordon_system.src.agent.components.systems.cognition.reasoning.counterfactual import (
    # Descriptors
    CounterfactualDescriptor,
    CounterfactualMode,
    CounterfactualLifecycle,
    
    # World Set Management
    WorldSet,
    WorldSetIdentity,
    BranchingStructure,
    
    # Reference World
    ReferenceWorld,
    WorldSnapshot,
    CausalState,
    TemporalPosition,
    
    # Alternative Worlds
    AlternativeWorld,
    WorldBranch,
    
    # Interventions
    CounterfactualIntervention,
    InterventionPipeline,
    
    # Divergence
    WorldDivergence,
    DivergencePipeline,
    
    # Comparison
    CounterfactualComparison,
    ComparisonPipeline,
    ComparisonDifference,
    
    # Refinement
    CounterfactualRefinement,
    
    # Validation
    CounterfactualValidation,
    ValidationResultKind,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
    
    # Governance
    CounterfactualGovernance,
    GovernanceRule,
    GovernanceFinding,
    GovernanceHealth,
    GovernanceFindingKind,
    
    # Failure
    CounterfactualFailure,
    FailureKind,
    FailureMode,
    
    # Health and Diagnostics
    CounterfactualHealth,
    CounterfactualDiagnostics,
)


def dataclass_replace(instance, **kwargs):
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


# =============================================================================
# TEST CLASSES
# =============================================================================


class TestCounterfactualDescriptor:
    """Tests for CounterfactualDescriptor."""
    
    def test_create_descriptor(self):
        """Test creating a new counterfactual descriptor."""
        descriptor = CounterfactualDescriptor.create(
            semantic_identity="test_counterfactual",
            reasoning_goal="Evaluate system failure scenarios",
            counterfactual_mode=CounterfactualMode.RETROSPECTIVE,
        )
        
        assert descriptor.semantic_identity == "test_counterfactual"
        assert descriptor.reasoning_goal == "Evaluate system failure scenarios"
        assert descriptor.counterfactual_mode == CounterfactualMode.RETROSPECTIVE
        assert descriptor.lifecycle_state == CounterfactualLifecycle.CREATED
    
    def test_descriptor_state_transitions(self):
        """Test state transitions."""
        descriptor = CounterfactualDescriptor.create(
            semantic_identity="test_counterfactual",
            reasoning_goal="Evaluate system failure scenarios",
        )
        
        updated = descriptor.to_state(CounterfactualLifecycle.BRANCHING)
        assert updated.lifecycle_state == CounterfactualLifecycle.BRANCHING
    
    def test_descriptor_completion(self):
        """Test completed descriptor."""
        descriptor = CounterfactualDescriptor.create(
            semantic_identity="test_counterfactual",
            reasoning_goal="Evaluate system failure scenarios",
        )
        
        completed = descriptor.to_state(CounterfactualLifecycle.COMPLETED)
        
        assert completed.is_completed
        assert not descriptor.is_completed


class TestWorldSet:
    """Tests for World Set."""
    
    def test_create_world_set(self):
        """Test creating a new world set."""
        snapshot = WorldSnapshot.create()
        reference = ReferenceWorld.create(snapshot=snapshot)
        world_set = WorldSet.create(reference_world=reference, provenance="test")
        
        assert world_set.reference_world == reference
        assert world_set.alternative_count == 0
    
    def test_add_alternative_world(self):
        """Test adding alternative worlds to a set."""
        snapshot1 = WorldSnapshot.create()
        reference = ReferenceWorld.create(snapshot=snapshot1)
        
        snapshot2 = WorldSnapshot.create()
        alternative = AlternativeWorld.create(
            originating_reference=reference,
            resulting_state=snapshot2,
        )
        
        world_set = WorldSet.create(reference_world=reference)
        world_set_with_alt = world_set.add_alternative(alternative)
        
        assert world_set_with_alt.alternative_count == 1
        assert world_set_with_alt.reference_world == reference


class TestCounterfactualIntervention:
    """Tests for Counterfactual Interventions."""
    
    def test_create_intervention(self):
        """Test creating a new intervention."""
        intervention = CounterfactualIntervention.create(
            modified_variables={"component_state": "operational"},
            intervention_scope=("component_a",),
        )
        
        assert intervention.is_hypothetical()
        assert intervention.modified_variables["component_state"] == "operational"
    
    def test_intervention_pipeline(self):
        """Test intervention pipeline."""
        intervention = CounterfactualIntervention.create(
            modified_variables={"memory": 1024},
        )
        
        pipeline = InterventionPipeline.create(intervention)
        pipeline_with_mod = pipeline.add_modification("memory", 512, 1024)
        
        assert "memory" in pipeline_with_mod.modified_variables


class TestDivergence:
    """Tests for Divergence Analysis."""
    
    def test_create_divergence(self):
        """Test creating a divergence record."""
        divergence = WorldDivergence.create(
            divergence_point="intervention_x",
            affected_mechanisms=("memory_allocation",),
        )
        
        assert divergence.divergence_point == "intervention_x"
        assert len(divergence.affected_mechanisms) == 1
    
    def test_divergence_pipeline(self):
        """Test divergence pipeline."""
        root = WorldDivergence.create(
            divergence_point="initial_intervention",
        )
        
        pipeline = DivergencePipeline.create(root)
        
        # Add a secondary effect
        secondary = WorldDivergence.create(
            divergence_point="secondary_effect_1",
        )
        pipeline_with_step = pipeline.add_propagation(secondary)
        
        assert len(pipeline_with_step.propagated_changes) == 1


class TestCounterfactualComparison:
    """Tests for Counterfactual Comparison."""
    
    def test_create_comparison(self):
        """Test creating a comparison between worlds."""
        ref = ReferenceWorld.create(WorldSnapshot.create())
        
        snapshot1 = WorldSnapshot.create()
        world1 = AlternativeWorld.create(originating_reference=ref, resulting_state=snapshot1)
        
        snapshot2 = WorldSnapshot.create()
        world2 = AlternativeWorld.create(originating_reference=ref, resulting_state=snapshot2)
        
        comparison = CounterfactualComparison.create(world1, world2)
        
        assert comparison.comparison_id.startswith("comparison:")
    
    def test_comparison_difference(self):
        """Test comparison difference."""
        diff = ComparisonDifference.create(
            variable_name="response_time",
            values_by_world={"world1": 100, "world2": 50},
        )
        
        assert diff.variable_name == "response_time"
        assert diff.values_by_world["world1"] == 100


class TestValidation:
    """Tests for Validation."""
    
    def test_create_validation_result(self):
        """Test creating a validation result."""
        finding = ValidationFinding.create(
            finding_kind=ValidationFindingKind.INCONSISTENT_STATE,
            description="State inconsistency detected",
        )
        
        record = CounterfactualValidation.create("alternative_world", "world1")
        record_with_finding = record.add_finding(finding)
        
        assert len(record_with_finding.findings) == 1
    
    def test_validation_trace(self):
        """Test validation trace."""
        trace = ValidationTrace.create()
        trace_with_step = trace.with_step(
            step_name="integrity_check",
            findings=(),
        )
        
        assert "integrity_check" in trace_with_step.validation_steps


class TestGovernance:
    """Tests for Governance."""
    
    def test_create_governance(self):
        """Test creating a governance evaluation record."""
        finding = GovernanceFinding.create(
            finding_kind=GovernanceFindingKind.PROVENANCE_INCOMPLETE,
            description="Provenance tracking incomplete",
        )
        
        governance = CounterfactualGovernance.create("session1")
        governance_with_finding = governance.with_finding(finding)
        
        assert len(governance_with_finding.findings) == 1
    
    def test_governance_health(self):
        """Test governance health metrics."""
        health = GovernanceHealth.create()
        
        updated = dataclass_replace(
            health,
            total_sessions_evaluated=10,
            successful_evaluations=8,
            failed_evaluations=2,
        )
        
        assert updated.total_sessions_evaluated == 10
        assert updated.evaluation_rate == 0.8


class TestFailure:
    """Tests for Failure Handling."""
    
    def test_create_failure(self):
        """Test creating a failure record."""
        failure = CounterfactualFailure.create(
            failure_kind=FailureKind.INVALID_INTERVENTION,
            diagnostics="Intervention variable not found in world state",
        )
        
        assert failure.failure_kind == FailureKind.INVALID_INTERVENTION
    
    def test_failure_mode(self):
        """Test failure mode definition."""
        fm = FailureMode.create(
            failure_name="Branch Explosion",
            failure_description="Too many alternative worlds generated",
        )
        
        assert fm.failure_name == "Branch Explosion"


class TestHealth:
    """Tests for Health Metrics."""
    
    def test_counterfactual_health(self):
        """Test health metrics."""
        health = CounterfactualHealth.create()
        
        updated = dataclass_replace(
            health,
            worlds_generated=5,
            branch_count=3,
            max_branch_depth=2,
        )
        
        assert updated.worlds_generated == 5
        assert updated.branch_count == 3


def dataclass_replace_test(instance, **kwargs):
    """Test helper for dataclass replace."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
