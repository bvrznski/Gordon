# Thread Delta Tests
# ===================

"""
Tests for Thread semantic delta model.
"""

import pytest
from agent.execution.threads import (
    DeltaValidationResult,
    ThreadSemanticDelta,
)


class TestDeltaValidationResult:
    """Test DeltaValidationResult enum."""
    
    def test_all_results_exist(self):
        """All expected validation results should be defined."""
        results = list(DeltaValidationResult)
        
        assert len(results) == 5
        result_values = {r.value for r in results}
        assert "valid" in result_values
        assert "stale_version" in result_values
        assert "invalid_content" in result_values
        assert "unauthorized" in result_values
        assert "pending_validation" in result_values


class TestThreadSemanticDelta:
    """Test ThreadSemanticDelta class."""
    
    def test_delta_creation(self):
        """Create and validate a semantic delta."""
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-123",
            loop_id="loop-456",
            expected_thread_version=5,
            change_type="objective_added",
            changes={"objective_id": "obj-789", "description": "Test objective"},
            provenance="cycle_outcome",
        )
        
        assert delta.source_cycle_id == "cycle-123"
        assert delta.loop_id == "loop-456"
        assert delta.expected_thread_version == 5
        assert delta.change_type == "objective_added"
        assert "objective_id" in delta.changes
        assert delta.provenance == "cycle_outcome"
    
    def test_is_stale_returns_true_for_mismatch(self):
        """is_stale should return True when versions don't match."""
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-123",
            expected_thread_version=5,
            change_type="state_transition",
            changes={},
        )
        
        assert delta.is_stale(current_version=4) is True
        assert delta.is_stale(current_version=6) is True
    
    def test_is_stale_returns_false_for_match(self):
        """is_stale should return False when versions match."""
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-123",
            expected_thread_version=5,
            change_type="state_transition",
            changes={},
        )
        
        assert delta.is_stale(current_version=5) is False
    
    def test_to_dict_serializable(self):
        """to_dict should return a serializable dictionary."""
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-123",
            expected_thread_version=5,
            change_type="objective_added",
            changes={"objective_id": "obj-789"},
        )
        
        result = delta.to_dict()
        
        assert isinstance(result, dict)
        assert result["source_cycle_id"] == "cycle-123"
        assert result["expected_thread_version"] == 5
        assert result["change_type"] == "objective_added"


class TestThreadDeltaBatch:
    """Test ThreadDeltaBatch class."""
    
    def test_batch_creation(self):
        """Create and validate a delta batch."""
        from agent.execution.threads import (
            ThreadSemanticDelta,
            ThreadDeltaBatch,
        )
        
        delta1 = ThreadSemanticDelta(
            source_cycle_id="cycle-1",
            expected_thread_version=5,
            change_type="objective_added",
            changes={},
        )
        delta2 = ThreadSemanticDelta(
            source_cycle_id="cycle-2",
            expected_thread_version=5,
            change_type="state_transition",
            changes={},
        )
        
        batch = ThreadDeltaBatch(
            thread_id="thread-123",
            deltas=(delta1, delta2),
            batch_version=1,
        )
        
        assert batch.thread_id == "thread-123"
        assert len(batch.deltas) == 2
        assert batch.batch_version == 1
    
    def test_expected_version(self):
        """expected_version should return version from first delta."""
        from agent.execution.threads import (
            ThreadSemanticDelta,
            ThreadDeltaBatch,
        )
        
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-1",
            expected_thread_version=5,
            change_type="state_transition",
            changes={},
        )
        
        batch = ThreadDeltaBatch(
            thread_id="thread-123",
            deltas=(delta,),
        )
        
        assert batch.expected_version() == 5
    
    def test_expected_version_none_for_empty_batch(self):
        """expected_version should return None for empty batch."""
        from agent.execution.threads import (
            ThreadDeltaBatch,
        )
        
        batch = ThreadDeltaBatch(
            thread_id="thread-123",
            deltas=(),
        )
        
        assert batch.expected_version() is None


class TestThreadDeltaValidator:
    """Test ThreadDeltaValidator class."""
    
    def test_validate_delta_stale_version(self):
        """validate_delta should return STALE_VERSION for mismatch."""
        from agent.execution.threads import (
            ThreadSemanticDelta,
            DeltaValidationResult,
            ThreadDeltaValidator,
        )
        
        validator = ThreadDeltaValidator(current_version=5)
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-1",
            expected_thread_version=3,  # Stale!
            change_type="state_transition",
            changes={},
        )
        
        result = validator.validate_delta(delta)
        
        assert result == DeltaValidationResult.STALE_VERSION
    
    def test_validate_delta_valid(self):
        """validate_delta should return VALID for matching version."""
        from agent.execution.threads import (
            ThreadSemanticDelta,
            DeltaValidationResult,
            ThreadDeltaValidator,
        )
        
        validator = ThreadDeltaValidator(current_version=5)
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-1",
            expected_thread_version=5,  # Matches!
            change_type="state_transition",
            changes={},
        )
        
        result = validator.validate_delta(delta)
        
        assert result == DeltaValidationResult.VALID
    
    def test_apply_delta_success(self):
        """apply_delta should increment version on success."""
        from agent.execution.threads import (
            ThreadSemanticDelta,
            ThreadDeltaValidator,
        )
        
        validator = ThreadDeltaValidator(current_version=5)
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-1",
            expected_thread_version=5,
            change_type="state_transition",
            changes={},
        )
        
        success, new_version, error = validator.apply_delta(delta, 5)
        
        assert success is True
        assert new_version == 6
        assert error is None
    
    def test_apply_delta_fails_with_stale(self):
        """apply_delta should fail with stale delta."""
        from agent.execution.threads import (
            ThreadSemanticDelta,
            ThreadDeltaValidator,
        )
        
        validator = ThreadDeltaValidator(current_version=5)
        delta = ThreadSemanticDelta(
            source_cycle_id="cycle-1",
            expected_thread_version=3,  # Stale
            change_type="state_transition",
            changes={},
        )
        
        success, new_version, error = validator.apply_delta(delta, 5)
        
        assert success is False
        assert new_version == 5  # No version change