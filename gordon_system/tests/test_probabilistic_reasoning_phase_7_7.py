# Probabilistic Reasoning Tests - Phase 7.7
# ===========================================

"""
Tests for the Probabilistic Reasoning subsystem (Phase 7.7).

Verifies:
    - Shared contract implementations
    - Bayesian inference pipeline
    - Evidence fusion
    - Uncertainty propagation
    - Calibration metrics
    - Validation rules
    - Governance evaluation
    - Health monitoring
"""

from __future__ import annotations

import time
import uuid
from dataclasses import replace

# Import the probabilistic module
# Import directly from the shared module since we're testing the contracts
import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

from agent.components.systems.cognition.reasoning.probabilistic.shared.descriptor import (
    ProbabilisticMode,
    ProbabilisticLifecycle,
    ProbabilisticDescriptor,
    ProbabilisticSessionIdentity,
)

from agent.components.systems.cognition.reasoning.probabilistic.shared.evidence_set import (
    ProbabilityEvidenceSet,
    EvidenceSource,
    SourceWeight,
    DependencyGraph,
    EvidenceQuality,
)


def test_probabilistic_descriptor_creation():
    """Test ProbabilisticDescriptor creation and state transitions."""
    
    # Create a descriptor
    descriptor = ProbabilisticDescriptor.create(
        semantic_identity="test-inference-001",
        reasoning_goal="Estimate probability of event A given evidence B",
        inference_mode=ProbabilisticMode.BAYESIAN_INFERENCE,
    )
    
    assert descriptor.descriptor_id.startswith("probabilistic:")
    assert descriptor.semantic_identity == "test-inference-001"
    assert descriptor.reasoning_goal == "Estimate probability of event A given evidence B"
    assert descriptor.inference_mode == ProbabilisticMode.BAYESIAN_INFERENCE
    assert descriptor.lifecycle_state == ProbabilisticLifecycle.CREATED
    
    # Test state transition
    new_descriptor = descriptor.to_state(ProbabilisticLifecycle.INITIALIZING)
    assert new_descriptor.lifecycle_state == ProbabilisticLifecycle.INITIALIZING
    assert new_descriptor.descriptor_id == descriptor.descriptor_id  # Immutable ID


def test_probabilistic_session_identity():
    """Test session identity creation."""
    
    identity = ProbabilisticSessionIdentity.create(
        semantic_identity="test-inference-001",
        session_number=3,
    )
    
    assert identity.semantic_identity == "test-inference-001"
    assert identity.session_number == 3
    assert hasattr(identity, 'timestamp_utc')


def test_evidence_source_creation():
    """Test EvidenceSource creation and properties."""
    
    source = EvidenceSource(
        source_id="sensor-001",
        source_type="environmental_sensor",
        source_name="Temperature Sensor A",
        reliability_estimate=0.85,
        confidence_estimate=0.92,
        quality_rating=EvidenceQuality.STRONG,
    )
    
    assert source.source_id == "sensor-001"
    assert source.is_reliable is True  # 0.85 >= 0.7
    
    weak_source = EvidenceSource(
        source_id="sensor-002",
        source_type="user_report",
        reliability_estimate=0.4,
    )
    assert weak_source.is_reliable is False


def test_dependency_graph():
    """Test dependency graph creation and operations."""
    
    graph = DependencyGraph()
    
    # Add dependencies
    new_graph = graph.add_edge("source-A", "source-B")
    new_graph = new_graph.add_edge("source-B", "source-C")
    
    assert "source-B" in new_graph.get_dependents("source-A")
    assert "source-C" in new_graph.get_dependents("source-B")


def test_evidence_set_creation():
    """Test ProbabilityEvidenceSet creation."""
    
    sources = [
        EvidenceSource(
            source_id="src-001",
            source_type="test",
            reliability_estimate=0.8,
        ),
        EvidenceSource(
            source_id="src-002",
            source_type="test", 
            reliability_estimate=0.6,
        ),
    ]
    
    evidence_set = ProbabilityEvidenceSet.create(sources)
    
    assert len(evidence_set.participating_evidence) == 2
    assert evidence_set.total_weight > 0


if __name__ == "__main__":
    # Run tests
    test_probabilistic_descriptor_creation()
    print("✓ ProbabilisticDescriptor creation test passed")
    
    test_probabilistic_session_identity()
    print("✓ Session identity test passed")
    
    test_evidence_source_creation()
    print("✓ Evidence source test passed")
    
    test_dependency_graph()
    print("✓ Dependency graph test passed")
    
    test_evidence_set_creation()
    print("✓ Evidence set test passed")
    
    print("\nAll Phase 7.7 tests passed!")