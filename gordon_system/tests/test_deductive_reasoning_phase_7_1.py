# Test Deductive Reasoning Phase 7.1 - Phase 7.1
# ==============================================

"""
Tests for the Deductive Reasoning subsystem (Phase 7.1).

These tests verify:
    - DeductionDescriptor creation and lifecycle
    - PremiseSet construction and manipulation
    - InferenceRule definition
    - RuleApplication processing
    - DeductiveProof construction
    - ProofGraph representation
    - Contradiction detection and analysis
    - ProofOptimization
    - DeductionValidation
    - DeductionGovernance
"""

import pytest

from agent.components.systems.cognition.reasoning.deductive import (
    # Descriptor
    DeductionDescriptor,
    DeductionState,
    
    PremiseSet,
    DeductionPremise,
    PremiseKind,
    
    InferenceRule,
    RuleKind,
    
    RuleApplication,
    
    DeductiveProof,
    ProofStep,
    ProofNode,
    
    ProofGraph,
    ProofEdge,
    
    DeductionContradiction,
    ContradictionAnalysis,
    
    ProofOptimization,
    
    DeductiveLemma,
    
    DeductionFailure,
    
    DeductionValidation,
    
    DeductionGovernance,
    
    DeductionHealth,
)


class TestDeductionDescriptor:
    """Tests for DeductionDescriptor."""
    
    def test_create_descriptor(self):
        """Test creating a new deduction descriptor."""
        descriptor = DeductionDescriptor.create(
            semantic_identity="test_deduction",
            reasoning_goal="Prove P → Q",
        )
        
        assert descriptor.semantic_identity == "test_deduction"
        assert descriptor.reasoning_goal == "Prove P → Q"
        assert descriptor.lifecycle_state == DeductionState.CREATED
        assert descriptor.descriptor_id.startswith("deduction_descriptor:")
    
    def test_descriptor_state_transitions(self):
        """Test state transitions."""
        descriptor = DeductionDescriptor.create(
            semantic_identity="test_deduction",
            reasoning_goal="Prove P → Q",
        )
        
        updated = descriptor.to_state(DeductionState.INITIALIZING)
        assert updated.lifecycle_state == DeductionState.INITIALIZING
    
    def test_descriptor_completion(self):
        """Test completed descriptor timing."""
        import time
        start_time = time.time()
        
        descriptor = DeductionDescriptor.create(
            semantic_identity="test_deduction",
            reasoning_goal="Prove P → Q",
        )
        
        # Simulate some processing time
        time.sleep(0.01)
        
        completed = descriptor.to_state(DeductionState.COMPLETED)
        
        assert completed.is_completed
        assert not descriptor.is_completed
        assert completed.duration_seconds >= 0


class TestPremiseSet:
    """Tests for PremiseSet."""
    
    def test_create_premise_set(self):
        """Test creating a premise set."""
        premise = DeductionPremise.create(
            premise_content="P → Q",
            premise_kind=PremiseKind.DEFINITION,
        )
        
        premise_set = PremiseSet.create(
            accepted_premises=[premise],
        )
        
        assert len(premise_set.accepted_premises) == 1
        assert premise_set.premise_count == 1
    
    def test_premise_with_assumptions(self):
        """Test adding assumptions to a premise set."""
        premise = DeductionPremise.create(
            premise_content="P → Q",
            premise_kind=PremiseKind.DEFINITION,
        )
        
        assumption = DeductionPremise.create(
            premise_content="P",
            premise_kind=PremiseKind.WORKING_ASSUMPTION,
        )
        
        premise_set = PremiseSet.create(
            accepted_premises=[premise],
        )
        
        updated = premise_set.with_assumptions([assumption])
        
        assert len(updated.all_premises) == 2
        assert len(premise_set.all_premises) == 1  # Original unchanged


class TestInferenceRule:
    """Tests for InferenceRule."""
    
    def test_create_modus_ponens(self):
        """Test creating a modus ponens rule."""
        rule = InferenceRule.create(
            rule_kind=RuleKind.MODUS_PONENS,
            required_premises=["P → Q", "P"],
            produced_conclusion="Q",
        )
        
        assert rule.rule_kind == RuleKind.MODUS_PONENS
        assert len(rule.required_premises) == 2
        assert rule.produced_conclusion == "Q"


class TestRuleApplication:
    """Tests for RuleApplication."""
    
    def test_create_rule_application(self):
        """Test creating a rule application."""
        rule = InferenceRule.create(
            rule_kind=RuleKind.MODUS_PONENS,
            required_premises=["P → Q", "P"],
            produced_conclusion="Q",
        )
        
        application = RuleApplication.create(
            inference_rule=rule,
            participating_premises=["P → Q", "P"],
            resulting_conclusion="Q",
        )
        
        assert application.is_valid
        assert len(application.participating_premises) == 2


class TestDeductiveProof:
    """Tests for DeductiveProof."""
    
    def test_create_simple_proof(self):
        """Test creating a simple proof with modus ponens."""
        # Create premises
        premise1 = ProofStep.create_premise("P → Q", step_number=0)
        premise2 = ProofStep.create_premise("P", step_number=1)
        
        # Create rule application
        rule = InferenceRule.create(
            rule_kind=RuleKind.MODUS_PONENS,
            required_premises=["P → Q", "P"],
            produced_conclusion="Q",
        )
        
        conclusion = ProofStep.create_application(
            rule_identity=rule.semantic_identity,
            input_statements=["P → Q", "P"],
            conclusion_statement="Q",
            step_number=2,
        )
        
        # Create proof
        proof = DeductiveProof.create(
            premises=["P → Q", "P"],
            inference_steps=[premise1, premise2, conclusion],
            final_conclusion="Q",
        )
        
        assert proof.is_complete
        assert len(proof.inference_steps) == 3


class TestProofGraph:
    """Tests for ProofGraph."""
    
    def test_create_proof_graph(self):
        """Test creating a proof graph."""
        node1 = ProofNode(
            node_id="node1",
            statement="P → Q",
            node_kind=NodeKind.PREMISE,
        )
        
        node2 = ProofNode(
            node_id="node2",
            statement="P",
            node_kind=NodeKind.PREMISE,
        )
        
        node3 = ProofNode(
            node_id="node3",
            statement="Q",
            node_kind=NodeKind.FINAL_CONCLUSION,
        )
        
        edge1 = ProofEdge(
            edge_id="edge1",
            source_node="node1",
            target_node="node2",
            edge_kind=EdgeKind.DEPENDENCY,
        )
        
        graph = ProofGraph.create(
            proof_nodes=[node1, node2, node3],
            proof_edges=[edge1],
        )
        
        assert graph.node_count == 3
        assert len(graph.root_nodes) > 0


class TestContradiction:
    """Tests for Contradiction."""
    
    def test_create_contradiction(self):
        """Test creating a contradiction record."""
        contradiction = DeductionContradiction.create(
            conflicting_premises=["P", "NOT P"],
            supporting_proofs=["proof1", "proof2"],
            contradiction_type="direct",
        )
        
        assert len(contradiction.conflicting_premises) == 2
        assert contradiction.premise_count == 2


class TestValidation:
    """Tests for DeductionValidation."""
    
    def test_create_validation(self):
        """Test creating a validation record."""
        validation = DeductionValidation.create(
            evaluated_proof="proof1",
            check_names=["rule_correctness", "trace_complete"],
        )
        
        assert validation.check_count == 2
        
        # Record some checks
        validation = validation.record_check("rule_correctness", True)
        assert validation.validation_checks["rule_correctness"] is True


class TestGovernance:
    """Tests for DeductionGovernance."""
    
    def test_create_governance(self):
        """Test creating a governance record."""
        governance = DeductionGovernance.create(
            session_ids=["session1"],
        )
        
        assert len(governance.evaluated_sessions) == 1


class TestHealth:
    """Tests for DeductionHealth."""
    
    def test_record_proof(self):
        """Test recording a proof in health metrics."""
        health = DeductionHealth.create()
        
        health = health.increment_proof(depth=5)
        
        assert health.proof_count == 1
        assert health.max_proof_depth == 5
    
    def test_record_validation(self):
        """Test recording validation results."""
        health = DeductionHealth.create()
        
        health = health.record_validation(passed=True)
        health = health.record_validation(passed=False)
        
        assert health.validation_success_count == 1
        assert health.validation_failure_count == 1
        assert health.validation_rate == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

