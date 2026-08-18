# Test Dialectical Reasoning Phase 7.17
# ======================================

"""
Test cases for the Dialectical Reasoning subsystem.

These tests verify the canonical contracts for:
    - Argument construction
    - Counterargument analysis
    - Conflict resolution
    - Synthesis construction
    - Consensus discovery
"""

import pytest
from time import time

# Import dialectical contracts
from agent.components.systems.cognition.reasoning.dialectical.shared import (
    DialecticalDescriptor,
    DialecticalState,
    ArgumentSet,
    ArgumentConstruction,
    CounterArgumentAnalysis,
    ConflictResolution,
    SynthesisConstruction,
    ConsensusDiscovery,
    DialecticalRefinement,
    DialecticalValidationResult,
    DialecticalFailure,
    DialecticalGovernance,
    DialecticalHealth,
    DialecticalDiagnostics,
)


class TestDialecticalDescriptor:
    """Test dialectical descriptor creation and state transitions."""

    def test_create_descriptor(self):
        """Test creating a new dialectical descriptor."""
        descriptor = DialecticalDescriptor.create(
            semantic_identity="dialectics:test:example",
            reasoning_goal="Resolve competing explanations for X",
        )
        assert descriptor.descriptor_id is not None
        assert descriptor.semantic_identity == "dialectics:test:example"
        assert descriptor.reasoning_goal == "Resolve competing explanations for X"
        assert descriptor.lifecycle_state == DialecticalState.CREATED

    def test_descriptor_state_transition(self):
        """Test state transition on a descriptor."""
        descriptor = DialecticalDescriptor.create(
            semantic_identity="dialectics:test",
            reasoning_goal="Test goal",
        )
        new_descriptor = descriptor.to_state(DialecticalState.INITIALIZING)
        assert new_descriptor.lifecycle_state == DialecticalState.INITIALIZING
        assert descriptor.lifecycle_state == DialecticalState.CREATED  # Original unchanged

    def test_descriptor_properties(self):
        """Test descriptor properties."""
        descriptor = DialecticalDescriptor.create(
            semantic_identity="dialectics:test",
            reasoning_goal="Test goal",
        )
        assert descriptor.is_completed is False
        assert descriptor.is_failed is False
        assert descriptor.is_archived is False

    def test_descriptor_completion(self):
        """Test completing a descriptor."""
        descriptor = DialecticalDescriptor.create(
            semantic_identity="dialectics:test",
            reasoning_goal="Test goal",
        )
        completed = descriptor.to_state(DialecticalState.COMPLETED)
        assert completed.lifecycle_state == DialecticalState.COMPLETED
        assert completed.is_completed is True


class TestArgumentSet:
    """Test argument set creation and management."""

    def test_create_argument_set(self):
        """Test creating an argument set."""
        argument_ids = ["arg1", "arg2", "arg3"]
        argument_set = ArgumentSet.create(
            participating_arguments=argument_ids,
        )
        assert len(argument_set.participating_arguments) == 3
        assert "arg1" in argument_set.participating_arguments

    def test_argument_set_with_evidence(self):
        """Test adding evidence to an argument set."""
        argument_set = ArgumentSet.create(
            participating_arguments=["arg1"],
        )
        new_set = argument_set.with_evidence({"type": "evidence", "data": "test"})
        assert len(new_set.shared_evidence) == 1
        assert len(argument_set.shared_evidence) == 0  # Original unchanged


class TestArgumentConstruction:
    """Test argument construction records."""

    def test_create_argument_construction(self):
        """Test creating an argument construction record."""
        argument = {"claim": "X", "premises": ["P1", "P2"]}
        construction = ArgumentConstruction.create(
            construction_strategy="deductive",
            resulting_argument=argument,
        )
        assert construction.construction_id is not None
        assert construction.construction_strategy == "deductive"
        assert construction.resulting_argument["claim"] == "X"

    def test_construction_duration(self):
        """Test argument construction duration."""
        construction = ArgumentConstruction.create(
            construction_strategy="deductive",
            resulting_argument={"claim": "test"},
        )
        assert construction.duration_seconds >= 0


class TestCounterArgumentAnalysis:
    """Test counterargument analysis records."""

    def test_create_counterargument_analysis(self):
        """Test creating a counterargument analysis."""
        challenged = {"claim": "X", "premises": ["P1"]}
        counter = {"criticism": "Not all premises hold", "evidence": "E1"}
        analysis = CounterArgumentAnalysis.create(
            challenged_argument=challenged,
            counterargument=counter,
            justification="Premise P2 is not universally true",
        )
        assert analysis.analysis_id is not None
        assert analysis.justification == "Premise P2 is not universally true"


class TestConflictResolution:
    """Test conflict resolution records."""

    def test_create_conflict_resolution(self):
        """Test creating a conflict resolution."""
        conflict = ConflictResolution.create(
            participating_arguments=["arg1", "arg2"],
        )
        assert conflict.resolution_id is not None
        assert conflict.is_resolved is False

    def test_conflict_resolution_strategy(self):
        """Test setting conflict resolution strategy."""
        conflict = ConflictResolution.create(
            participating_arguments=["arg1", "arg2"],
        )
        resolved = conflict.with_resolution_strategy("synthesis")
        assert resolved.resolution_strategy == "synthesis"
        assert resolved.is_resolved is True


class TestSynthesisConstruction:
    """Test synthesis construction records."""

    def test_create_synthesis(self):
        """Test creating a synthesis."""
        synthesis = SynthesisConstruction.create(
            synthesized_arguments=["arg1", "arg2"],
        )
        assert synthesis.synthesis_id is not None
        assert synthesis.is_complete is False

    def test_synthesis_completion(self):
        """Test completing a synthesis."""
        synthesis = SynthesisConstruction.create(
            synthesized_arguments=["arg1", "arg2"],
        )
        completed = synthesis.with_strategy("higher_order_abstraction").complete()
        assert completed.synthesis_strategy == "higher_order_abstraction"
        assert completed.is_complete is True


class TestConsensusDiscovery:
    """Test consensus discovery records."""

    def test_create_consensus(self):
        """Test creating a consensus record."""
        consensus = ConsensusDiscovery.create(
            participating_arguments=["arg1", "arg2"],
        )
        assert consensus.consensus_id is not None
        assert consensus.confidence == 0.0

    def test_consensus_with_shared_elements(self):
        """Test adding shared elements to consensus."""
        consensus = ConsensusDiscovery.create(
            participating_arguments=["arg1", "arg2"],
        )
        consensus = consensus.with_shared_assumption({"type": "assumption", "name": "A"})
        consensus = consensus.with_shared_evidence({"type": "evidence", "data": "E"})
        assert len(consensus.shared_assumptions) == 1
        assert len(consensus.shared_evidence) == 1

    def test_consensus_confidence(self):
        """Test setting consensus confidence."""
        consensus = ConsensusDiscovery.create(
            participating_arguments=["arg1", "arg2"],
        )
        consensus = consensus.with_confidence(0.75)
        assert consensus.confidence == 0.75


class TestDialecticalRefinement:
    """Test dialectical refinement records."""

    def test_create_refinement(self):
        """Test creating a refinement."""
        previous = {"model": "v1"}
        refined = {"model": "v2", "improved": True}
        refinement = DialecticalRefinement.create(
            previous_model=previous,
            refined_model=refined,
        )
        assert refinement.refinement_id is not None


class TestDialecticalValidationResult:
    """Test validation result records."""

    def test_create_validation(self):
        """Test creating a validation record."""
        validation = DialecticalValidationResult.create()
        assert validation.validation_id is not None

    def test_validation_check_results(self):
        """Test recording validation check results."""
        validation = DialecticalValidationResult.create()
        validation = validation.with_check("argument_quality", True, {"score": 0.9})
        assert len(validation.check_results) == 1
        assert validation.check_results[0]["passed"] is True


class TestDialecticalFailure:
    """Test failure records."""

    def test_create_failure(self):
        """Test creating a failure record."""
        failure = DialecticalFailure.create(
            failure_kind="insufficient_evidence",
            affected_reasoning="argument_construction",
        )
        assert failure.failure_id is not None
        assert failure.is_recoverable is False

    def test_failure_with_recovery_options(self):
        """Test failure with recovery options."""
        failure = DialecticalFailure.create(
            failure_kind="resource_exhaustion",
            affected_reasoning="synthesis",
            recovery_options=["reduce_scope", "increase_resources"],
        )
        assert failure.is_recoverable is True


class TestDialecticalGovernance:
    """Test governance evaluation records."""

    def test_create_governance(self):
        """Test creating a governance record."""
        governance = DialecticalGovernance.create()
        assert governance.governance_id is not None

    def test_governance_violation(self):
        """Test recording a governance violation."""
        governance = DialecticalGovernance.create()
        governance = governance.record_violation({"type": "invalid_argument"})
        assert len(governance.violations) == 1
        assert governance.violation_count == 1


class TestDialecticalHealth:
    """Test health metric records."""

    def test_create_health(self):
        """Test creating a health record."""
        health = DialecticalHealth.create()
        assert health.health_id is not None

    def test_health_metrics(self):
        """Test health metrics accumulation."""
        health = DialecticalHealth.create()
        health = (health
                  .with_argument_analyzed()
                  .with_counterargument_generated()
                  .with_conflict_identified())
        assert health.arguments_analyzed == 1
        assert health.counterarguments_generated == 1
        assert health.conflicts_identified == 1

    def test_overall_health_score(self):
        """Test overall health score calculation."""
        health = DialecticalHealth.create()
        score = health.overall_score
        # Score should be between 0 and 1
        assert 0.0 <= score <= 1.0


class TestDialecticalDiagnostics:
    """Test diagnostics records."""

    def test_create_diagnostics(self):
        """Test creating a diagnostics record."""
        diagnostics = DialecticalDiagnostics.create()
        assert diagnostics.diagnostics_id is not None

    def test_timing_breakdown(self):
        """Test timing breakdown recording."""
        diagnostics = DialecticalDiagnostics.create()
        diagnostics = diagnostics.with_timing("argument_generation", 1.5)
        assert "argument_generation" in diagnostics.timing_breakdown
        assert diagnostics.timing_breakdown["argument_generation"] == 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])