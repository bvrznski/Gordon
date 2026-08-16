# Tests for Reward Evaluation Engine - Phase 4.10.3
# ==================================================================================================

"""
Test suite for Phase 4.10.3 reward evaluation engine.
"""

from gordon_system.src.agent.components.networks.reward.engine import (
    RewardEvaluationEngine,
    RewardLandscape,
)


def test_engine_empty_evidence():
    """Test engine handles empty evidence gracefully."""
    engine = RewardEvaluationEngine()
    
    trace, landscape = engine.evaluate({})
    
    assert len(trace) >= 2
    assert "REQUEST_RECEIVED" in trace
    # Empty landscape should have zero estimates
    assert landscape.estimate_count == 0


def test_engine_with_evidence():
    """Test engine processes evidence correctly."""
    engine = RewardEvaluationEngine()
    
    # Create simple evidence state with sample evidence
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "test-evidence-1",
                "semantic_content": "task completed successfully",
                "relationship": "supports_reward",
                "confidence": 0.9,
                "uncertainty": 0.1,
                "timescale": "immediate",
            },
        )
    }
    
    trace, landscape = engine.evaluate(evidence_state)
    
    assert len(trace) >= 4
    # Landscape should have at least one estimate ref
    assert landscape.estimate_count == 1


def test_engine_preserves_expected_vs_realized():
    """Test engine keeps expected and realized rewards separate."""
    engine = RewardEvaluationEngine()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "test-evidence-1",
                "semantic_content": "knowledge acquired",
                "relationship": "supports_reward",
                "confidence": 0.85,
                "uncertainty": 0.2,
                "timescale": "short_term",
            },
        )
    }
    
    trace, landscape = engine.evaluate(evidence_state)
    
    # Expected and realized should both be present (even if zero initially)
    assert hasattr(landscape.expected_rewards, "immediate")
    assert hasattr(landscape.realized_rewards, "immediate")


def test_landscape_properties():
    """Test reward landscape properties."""
    landscape = RewardLandscape(
        landscape_id="test-landscape",
        estimate_refs=("estimate-1", "estimate-2"),
    )
    
    assert landscape.estimate_count == 2
    assert "test-landscape" in str(landscape)


def test_engine_deterministic():
    """Test engine produces same output for same input."""
    engine = RewardEvaluationEngine()
    
    evidence_state = {
        "evidences": (
            {
                "evidence_id": "determinism-test",
                "semantic_content": "positive outcome",
                "relationship": "supports_reward",
                "confidence": 0.9,
                "uncertainty": 0.1,
            },
        )
    }
    
    trace1, landscape1 = engine.evaluate(evidence_state)
    trace2, landscape2 = engine.evaluate(evidence_state)
    
    # Same input should produce same output (excluding trace which may vary slightly)
    assert landscape1.estimate_count == landscape2.estimate_count
    assert landscape1.total_magnitude == landscape2.total_magnitude


if __name__ == "__main__":
    test_engine_empty_evidence()
    test_engine_with_evidence()
    test_engine_preserves_expected_vs_realized()
    test_landscape_properties()
    test_engine_deterministic()
    
    print("All engine tests passed!")