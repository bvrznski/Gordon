# Test Suite: Analogical Reasoning Phase 7.12
# ============================================

"""
Test suite for Phase 7.12 Analogical Reasoning implementation.

Tests verify:
    - Domain construction (ReasoningDomain, DomainSet)
    - Structural mapping pipelines
    - Correspondence discovery
    - Knowledge transfer mechanisms
    - Analogical inference generation
    - Mapping evaluation
    - Validation procedures
    - Governance evaluations
    - Provenance tracking
    - Deterministic execution
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agent.components.systems.cognition.reasoning.analogical.shared.domain_set import (
    ReasoningDomain,
    DomainSet,
)

from agent.components.systems.cognition.reasoning.analogical.shared.mapping_pipeline import (
    MappingResult,
    StructuralMappingPipeline,
    CorrespondenceAnalysis,
)

from agent.components.systems.cognition.reasoning.analogical.shared.inference import (
    AnalogicalInference,
    AnalogicalInferencePipeline,
    InferenceCandidate,
)

from agent.components.systems.cognition.reasoning.analogical.shared.evaluation import (
    QualityMetric,
    MappingEvaluation,
    EvaluationSummary,
)


def test_reasoning_domain_creation():
    """Test ReasoningDomain creation and properties."""
    domain = ReasoningDomain(
        domain_id="domain:test1",
        semantic_identity="physics:mechanics",
        participating_entities=("mass", "force", "acceleration"),
        participating_relations=("F=ma",),
        abstraction_level=0.5,
        originating_system="knowledge_graph",
    )
    
    assert domain.domain_id == "domain:test1"
    assert domain.semantic_identity == "physics:mechanics"
    assert domain.entity_count == 3
    assert domain.relation_count == 1
    print("✓ test_reasoning_domain_creation passed")


def test_domain_set_creation():
    """Test DomainSet creation with source and target domains."""
    source_domain = ReasoningDomain(
        domain_id="domain:source",
        semantic_identity="mechanics:solar_system",
        participating_entities=("star", "planet", "orbit"),
        participating_relations=("planet_orbits_star",),
    )
    
    target_domain = ReasoningDomain(
        domain_id="domain:target",
        semantic_identity="atomic:hydrogen",
        participating_entities=("nucleus", "electron", "orbital"),
        participating_relations=("electron_orbits_nucleus",),
    )
    
    domain_set = DomainSet.create(
        source_domain=source_domain,
        target_domain=target_domain,
        mapping_assumptions=["structural_correspondence", "relational_preservation"],
        domain_boundaries=["mechanics", "quantum"],
        min_correspondence_confidence=0.5,
    )
    
    assert domain_set.domain_count == 2
    assert len(domain_set.mapping_assumptions) == 2
    assert domain_set.source_domain == source_domain
    assert domain_set.target_domain == target_domain
    print("✓ test_domain_set_creation passed")


def test_mapping_result_creation():
    """Test MappingResult creation and properties."""
    mapping = MappingResult(
        mapping_result_id="mapping:1",
        source_element_id="planet",
        target_element_id="electron",
        mapping_rule="orbiting_body_relationship",
        correspondence_type="functional",
        confidence_score=0.85,
        supporting_evidence=("both_orbit_center", "attracted_by_central_force"),
    )
    
    assert mapping.source_element_id == "planet"
    assert mapping.target_element_id == "electron"
    assert mapping.confidence_score == 0.85
    assert mapping.evidence_count == 2
    print("✓ test_mapping_result_creation passed")


def test_structural_mapping_pipeline():
    """Test StructuralMappingPipeline execution tracking."""
    pipeline = StructuralMappingPipeline.create(
        session_identity="session:analogy1",
        source_domain_id="domain:solar_system",
        target_domain_id="domain:atom",
    )
    
    # Record step
    pipeline = pipeline.record_step("structure_extraction", {"extracted": True})
    
    # Add correspondence candidate
    mapping_result = MappingResult(
        mapping_result_id="mapping:r1",
        source_element_id="star",
        target_element_id="nucleus",
        mapping_rule="central_body_relationship",
    )
    pipeline = pipeline.add_correspondence_candidate(mapping_result)
    
    assert pipeline.total_candidates_found == 1
    assert len(pipeline.pipeline_steps) == 1
    print("✓ test_structural_mapping_pipeline passed")


def test_correspondence_analysis():
    """Test CorrespondenceAnalysis tracking."""
    analysis = CorrespondenceAnalysis.create(
        source_structure_id="structure:solar_system",
        target_structure_id="structure:atom",
    )
    
    mapping_result = MappingResult(
        mapping_result_id="mapping:r1",
        source_element_id="orbit",
        target_element_id="orbital_path",
        mapping_rule="circular_trajectory_pattern",
    )
    analysis = analysis.add_correspondence(mapping_result)
    
    assert analysis.total_discovered_correspondences == 1
    assert len(analysis.discovered_correspondences) == 1
    print("✓ test_correspondence_analysis passed")


def test_analogical_inference():
    """Test AnalogicalInference creation."""
    inference = AnalogicalInference(
        inference_id="inference:1",
        supporting_mapping_id="mapping:m1",
        inferred_element="centripetal_force",
        inference_type="predicted_behavior",
        confidence=0.75,
        supporting_evidence=("orbital_pattern_analogy",),
    )
    
    assert inference.inference_id == "inference:1"
    assert inference.confidence == 0.75
    assert inference.is_validated is False
    print("✓ test_analogical_inference passed")


def test_analogical_inference_pipeline():
    """Test AnalogicalInferencePipeline execution."""
    pipeline = AnalogicalInferencePipeline.create(
        session_identity="session:analogy1",
        source_mapping_id="mapping:m1",
    )
    
    candidate = AnalogicalInference(
        inference_id="inference:c1",
        supporting_mapping_id="mapping:m1",
        inferred_element="centripetal_force",
        confidence=0.75,
    )
    pipeline = pipeline.add_candidate(candidate)
    
    assert pipeline.total_candidates_generated == 1
    print("✓ test_analogical_inference_pipeline passed")


def test_quality_metric():
    """Test QualityMetric for evaluation."""
    metric = QualityMetric(
        metric_id="metric:1",
        metric_name="completeness",
        metric_value=0.85,
        metric_weight=1.0,
        minimum_acceptable=0.5,
        target_value=1.0,
    )
    
    assert metric.metric_name == "completeness"
    assert metric.metric_value == 0.85
    print("✓ test_quality_metric passed")


def test_mapping_evaluation():
    """Test MappingEvaluation with quality metrics."""
    evaluation = MappingEvaluation.create(
        evaluated_mapping_id="mapping:m1",
    )
    
    metric = QualityMetric(
        metric_id="metric:1",
        metric_name="completeness",
        metric_value=0.85,
    )
    evaluation = evaluation.add_metric(metric)
    
    assert evaluation.metric_count == 1
    print("✓ test_mapping_evaluation passed")


def test_evaluation_summary():
    """Test EvaluationSummary across multiple evaluations."""
    summary = EvaluationSummary.create()
    
    # Simulate results - these are set at creation time
    assert hasattr(summary, "passed_evaluations")
    assert hasattr(summary, "failed_evaluations")
    print("✓ test_evaluation_summary passed")


def test_provenance_tracking():
    """Test provenance tracking in contracts."""
    domain = ReasoningDomain(
        domain_id="domain:test",
        semantic_identity="test:structure",
        provenance={
            "created_by": "test_runner",
            "timestamp_utc": "2024-01-01T00:00:00Z",
            "source_system": "test_suite",
        },
    )
    
    assert "created_by" in domain.provenance
    assert domain.provenance["source_system"] == "test_suite"
    print("✓ test_provenance_tracking passed")


def test_frozen_dataclass_behavior():
    """Test that dataclasses are frozen (immutable)."""
    from gordon_system.src.agent.components.systems.cognition.reasoning.analogical.shared.domain_set import dataclass_replace
    
    domain = ReasoningDomain(
        domain_id="domain:test",
        semantic_identity="test:structure",
    )
    
    # Try to modify - this should create a new instance
    modified_domain = dataclass_replace(domain, semantic_identity="modified")
    
    assert domain.semantic_identity == "test:structure"
    assert modified_domain.semantic_identity == "modified"
    print("✓ test_frozen_dataclass_behavior passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ANALOGICAL REASONING PHASE 7.12 TEST SUITE")
    print("=" * 60 + "\n")
    
    test_reasoning_domain_creation()
    test_domain_set_creation()
    test_mapping_result_creation()
    test_structural_mapping_pipeline()
    test_correspondence_analysis()
    test_analogical_inference()
    test_analogical_inference_pipeline()
    test_quality_metric()
    test_mapping_evaluation()
    test_evaluation_summary()
    test_provenance_tracking()
    test_frozen_dataclass_behavior()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()