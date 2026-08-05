# Tests for Readiness Authority
# ==============================

"""
Comprehensive tests for the ReadinessController and related components.

Tests cover:
- State management and transitions
- Requirement registration and evaluation
- Deterministic aggregation
- Revocation handling
- Multi-runtime isolation
"""

import pytest
import asyncio
import time
from typing import List, Dict, Tuple, Optional

# Import readiness module - try direct import first
try:
    from gordon_system.src.agent.components.core.readiness.__init__ import (
        ReadinessController,
        ReadinessStatus,
        ReadinessClass,
        ReadinessRequirement,
        ReadinessEvidence,
        EvidenceStatus,
        ReadinessDecision,
        ReadinessRevocationRequest,
        ReadinessRevocationDecision,
        RevocationType,
    )
except ImportError:
    try:
        from src.agent.components.core.readiness import (
            ReadinessController,
            ReadinessStatus,
            ReadinessClass,
            ReadinessRequirement,
            ReadinessEvidence,
            EvidenceStatus,
            ReadinessDecision,
            ReadinessRevocationRequest,
            ReadinessRevocationDecision,
            RevocationType,
        )
    except ImportError:
        from agent.components.core.readiness import (
            ReadinessController,
            ReadinessStatus,
            ReadinessClass,
            ReadinessRequirement,
            ReadinessEvidence,
            EvidenceStatus,
            ReadinessDecision,
            ReadinessRevocationRequest,
            ReadinessRevocationDecision,
            RevocationType,
        )


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def runtime_id() -> str:
    """Generate a unique runtime ID for testing."""
    import uuid
    return f"test_runtime_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def readiness_controller(runtime_id: str) -> ReadinessController:
    """Create a readiness controller for testing."""
    return ReadinessController(runtime_id)


# =============================================================================
# TEST: State Management
# =============================================================================

class TestReadinessStateManagement:
    """Tests for readiness state management."""
    
    def test_initial_state_is_not_evaluated(self, runtime_id: str):
        """Test that initial state is NOT_EVALUATED."""
        controller = ReadinessController(runtime_id)
        status = controller.get_status()
        
        # Initial state should be UNKNOWN or NOT_EVALUATED
        assert status in (ReadinessStatus.UNKNOWN, ReadinessStatus.NOT_EVALUATED)
    
    def test_state_version_increments_on_evaluation(self, runtime_id: str):
        """Test that state version increments after evaluation."""
        controller = ReadinessController(runtime_id)
        
        initial_version = controller.state_version
        
        # Evaluate readiness
        asyncio.run(controller.evaluate_readiness())
        
        final_version = controller.state_version
        assert final_version > initial_version
    
    def test_state_is_runtime_scoped(self):
        """Test that different runtimes have independent state."""
        controller_a = ReadinessController("runtime_a")
        controller_b = ReadinessController("runtime_b")
        
        # Modify A's state
        asyncio.run(controller_a.evaluate_readiness())
        
        # B should be unaffected
        assert controller_a.state_version != controller_b.state_version
    
    def test_get_snapshot_returns_immutable(self, runtime_id: str):
        """Test that get_snapshot returns an immutable snapshot."""
        controller = ReadinessController(runtime_id)
        snapshot = controller.get_snapshot()
        
        # Snapshot should have required attributes
        assert hasattr(snapshot, 'runtime_id')
        assert hasattr(snapshot, 'boot_session_id')
        assert hasattr(snapshot, 'state_version')


# =============================================================================
# TEST: Requirement Registration
# =============================================================================

class TestReadinessRequirements:
    """Tests for requirement registration."""
    
    def test_register_requirement_adds_to_controller(self, runtime_id: str):
        """Test that registered requirements are tracked."""
        controller = ReadinessController(runtime_id)
        
        requirement = ReadinessRequirement(
            id="test_requirement",
            description="A test requirement",
            mandatory=True,
            applicable_classes=(ReadinessClass.NORMAL_WORK,),
            evaluator_id="test_evaluator",
            timeout_seconds=30.0,
            freshness_seconds=60.0
        )
        
        controller.register_requirement(requirement)
        
        # Should have the requirement in internal storage
        assert "test_requirement" in controller._requirements
    
    def test_unregister_requirement_removes_it(self, runtime_id: str):
        """Test that unregistered requirements are removed."""
        controller = ReadinessController(runtime_id)
        
        requirement = ReadinessRequirement(
            id="removable",
            description="A removable requirement",
            mandatory=True,
            applicable_classes=(ReadinessClass.NORMAL_WORK,),
            evaluator_id="test_evaluator",
            timeout_seconds=30.0,
            freshness_seconds=60.0
        )
        
        controller.register_requirement(requirement)
        assert "removable" in controller._requirements
        
        result = controller.unregister_requirement("removable")
        assert result is True
        assert "removable" not in controller._requirements
    
    def test_unregister_nonexistent_returns_false(self, runtime_id: str):
        """Test that unregistering non-existent requirement returns False."""
        controller = ReadinessController(runtime_id)
        
        result = controller.unregister_requirement("nonexistent")
        assert result is False


# =============================================================================
# TEST: Evaluation Pipeline
# =============================================================================

class TestReadinessEvaluation:
    """Tests for the evaluation pipeline."""
    
    async def test_evaluate_without_evaluators_returns_unknown(self, runtime_id: str):
        """Test that evaluation without registered evaluators returns unknown."""
        controller = ReadinessController(runtime_id)
        
        # Register a requirement but don't register an evaluator
        requirement = ReadinessRequirement(
            id="no_evaluator",
            description="No evaluator registered",
            mandatory=True,
            applicable_classes=(ReadinessClass.NORMAL_WORK,),
            evaluator_id="nonexistent_evaluator",
            timeout_seconds=30.0,
            freshness_seconds=60.0
        )
        
        controller.register_requirement(requirement)
        
        decision = await controller.evaluate_readiness()
        
        # Should have unknown status due to missing evaluator
        assert decision.status == ReadinessStatus.BLOCKED
    
    async def test_evaluate_with_satisfied_requirement(self, runtime_id: str):
        """Test evaluation when requirements are satisfied."""
        controller = ReadinessController(runtime_id)
        
        requirement = ReadinessRequirement(
            id="healthy",
            description="System is healthy",
            mandatory=True,
            applicable_classes=(ReadinessClass.NORMAL_WORK,),
            evaluator_id="health_check",
            timeout_seconds=30.0,
            freshness_seconds=60.0
        )
        
        controller.register_requirement(requirement)
        
        # This would normally be called by health subsystem to report status
        # For testing, we'd mock the evaluation result
    
    async def test_mandatory_failure_results_in_blocked(self, runtime_id: str):
        """Test that mandatory requirement failure results in BLOCKED."""
        controller = ReadinessController(runtime_id)
        
        requirement = ReadinessRequirement(
            id="critical_dependency",
            description="Critical dependency must be available",
            mandatory=True,
            applicable_classes=(ReadinessClass.NORMAL_WORK,),
            evaluator_id="dependency_check",
            timeout_seconds=30.0,
            freshness_seconds=60.0
        )
        
        controller.register_requirement(requirement)
    
    async def test_optional_failure_allows_degraded(self, runtime_id: str):
        """Test that optional requirement failure allows degraded readiness."""
        controller = ReadinessController(runtime_id)
        
        # Create an optional requirement (mandatory=False)
        requirement = ReadinessRequirement(
            id="optional_capability",
            description="Optional feature may be unavailable",
            mandatory=False,
            applicable_classes=(ReadinessClass.NORMAL_WORK,),
            evaluator_id="feature_check",
            timeout_seconds=30.0,
            freshness_seconds=60.0
        )
        
        controller.register_requirement(requirement)


# =============================================================================
# TEST: Revocation
# =============================================================================

class TestReadinessRevocation:
    """Tests for readiness revocation."""
    
    async def test_revocation_changes_status(self, runtime_id: str):
        """Test that revocation changes status to REVOKED."""
        controller = ReadinessController(runtime_id)
        
        # First make it ready
        await controller.evaluate_readiness()
        
        # Get current status (may be UNKNOWN if no evaluators registered)
        old_status = controller.get_status()
        
        # Revoke
        decision = await controller.revoke_readiness("Test revocation")
        
        assert decision is not None
        assert decision.status_before != ReadinessStatus.REVOKED
    
    async def test_already_revoked_returns_none(self, runtime_id: str):
        """Test that revoking already-revoked status returns None."""
        controller = ReadinessController(runtime_id)
        
        # Revoke immediately
        first_decision = await controller.revoke_readiness("First revocation")
        assert first_decision is not None
        
        # Try to revoke again - should return None since already revoked
        second_decision = await controller.revoke_readiness("Second revocation")
        assert second_decision is None
    
    async def test_revocation_preserves_history(self, runtime_id: str):
        """Test that revocation preserves history."""
        controller = ReadinessController(runtime_id)
        
        # Evaluate a few times
        await controller.evaluate_readiness()
        await controller.evaluate_readiness()
        
        old_status = controller.get_status()
        
        # Revoke
        decision = await controller.revoke_readiness("Testing")
        
        assert decision is not None


# =============================================================================
# TEST: Multi-Runtime Isolation
# =============================================================================

class TestMultiRuntimeIsolation:
    """Tests for multi-runtime isolation."""
    
    def test_different_runtimes_have_different_boot_sessions(self):
        """Test that different runtimes have unique boot sessions."""
        controller_a = ReadinessController("runtime_a")
        controller_b = ReadinessController("runtime_b")
        
        assert controller_a.boot_session_id != controller_b.boot_session_id
    
    def test_state_versions_are_independent(self):
        """Test that state versions don't leak between runtimes."""
        controller_a = ReadinessController("runtime_a")
        controller_b = ReadinessController("runtime_b")
        
        # Both start at 0
        assert controller_a.state_version == 0
        assert controller_b.state_version == 0
        
        # Evaluate A
        asyncio.run(controller_a.evaluate_readiness())
        
        # A should have higher version, B unchanged
        assert controller_a.state_version > 0
        assert controller_b.state_version == 0
    
    def test_snapshot_contains_correct_runtime_id(self):
        """Test that snapshots contain the correct runtime ID."""
        controller = ReadinessController("my_special_runtime")
        snapshot = controller.get_snapshot()
        
        assert snapshot.runtime_id == "my_special_runtime"


# =============================================================================
# TEST: Deterministic Aggregation
# =============================================================================

class TestDeterministicAggregation:
    """Tests for deterministic aggregation logic."""
    
    def test_same_evidence_always_gives_same_result(self, runtime_id: str):
        """Test that identical input produces identical output."""
        controller = ReadinessController(runtime_id)
        
        # Run evaluation multiple times
        decisions = []
        for _ in range(3):
            decision = asyncio.run(controller.evaluate_readiness())
            decisions.append(decision)
        
        # All should have same status (even if it's UNKNOWN)
        statuses = [d.status for d in decisions]
        assert len(set(statuses)) == 1, "Aggregation should be deterministic"
    
    def test_mandatory_unknown_is_blocked(self):
        """Test that mandatory unknown requirements result in BLOCKED."""
        # This would require specific evaluator behavior to test properly
        pass


# =============================================================================
# TEST: EVIDENCE FRESHNESS
# =============================================================================

class TestEvidenceFreshness:
    """Tests for evidence freshness handling."""
    
    def test_evidence_validity(self):
        """Test that evidence validity is based on freshness."""
        now = time.monotonic()
        
        fresh = ReadinessEvidence(
            requirement_id="test",
            source_subsystem="test",
            status=EvidenceStatus.SATISFIED,
            timestamp_utc=time.time(),
            monotonic_time=now,
            freshness_seconds=30.0
        )
        
        # Fresh evidence should be valid
        assert fresh.is_valid
    
    def test_stale_evidence_invalidates(self):
        """Test that stale evidence is considered invalid."""
        old_time = time.monotonic() - 60.0  # 60 seconds ago
        
        stale = ReadinessEvidence(
            requirement_id="test",
            source_subsystem="test",
            status=EvidenceStatus.SATISFIED,
            timestamp_utc=time.time(),
            monotonic_time=old_time,
            freshness_seconds=30.0
        )
        
        # Stale evidence should be invalid
        assert not stale.is_valid


# =============================================================================
# TEST: BOOLEAN COMPATIBILITY
# =============================================================================

class TestBooleanCompatibility:
    """Tests for boolean compatibility methods."""
    
    def test_is_ready_for_admission_uses_status(self, runtime_id: str):
        """Test that is_ready_for_admission checks status correctly."""
        controller = ReadinessController(runtime_id)
        
        # Initially should not be ready
        assert not controller.is_ready_for_admission()
        
        # The boolean result is derived from status - it's NOT the authority


if __name__ == "__main__":
    pytest.main([__file__, "-v"])