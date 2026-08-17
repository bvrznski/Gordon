"""
Foundation tests for the Experiential Field Builder package.

This module verifies:
    - Package structure and imports
    - Immutable dataclass contracts
    - Identity class behavior  
    - Snapshot immutability
    - Transition atomicity
    - Validation boundaries
"""

import pytest


# =============================================================================
# PACKAGE STRUCTURE TESTS
# =============================================================================

def test_experiential_field_package_exists():
    """Verify the experiential_field package is importable."""
    from agent.capabilities.consciousness.experiential_field import ExperientialFieldBuilder
    
    assert ExperientialFieldBuilder is not None


def test_public_api_exports():
    """Verify all expected public exports are available."""
    from agent.capabilities.consciousness.experiential_field import (
        ExperientialFieldBuilder,
        FieldBuildResult,
        FieldBuildRequest,
        ExperientialFieldSnapshot,
        FieldContent,
        FieldRelation,
        FieldTransition,
        FieldTransitionAuthority,
        TransitionCommitResult,
        ContributionNormalizer,
        NormalizationAction,
        ContributionValidator,
        ValidationOutcome,
        RejectionReason,
        FieldCapacityPolicy,
        CapacityEnforcementResult,
        DeterministicOrderer,
        OrderingKey,
        FieldIntegrityChecker,
        IntegrityCheckResult,
    )
    
    assert ExperientialFieldBuilder is not None
    assert ExperientialFieldSnapshot is not None
    assert FieldTransitionAuthority is not None


# =============================================================================
# IMMUTABLE DATACLASS TESTS
# =============================================================================

def test_field_content_is_frozen():
    """Verify FieldContent uses frozen dataclass for immutability."""
    from agent.capabilities.consciousness.experiential_field import FieldContent
    
    content = FieldContent(
        content_id="test-001",
        source_id="source-001",
        content_kind="workspace"
    )
    
    with pytest.raises((AttributeError, TypeError)):
        content.content_id = "modified"


def test_field_relation_is_frozen():
    """Verify FieldRelation uses frozen dataclass for immutability."""
    from agent.capabilities.consciousness.experiential_field import FieldRelation
    
    relation = FieldRelation(
        relation_id="rel-001",
        source_content_id="content-001",
        target_content_id="content-002",
        relation_kind="same_object"
    )
    
    with pytest.raises((AttributeError, TypeError)):
        relation.relation_id = "modified"


def test_experiential_field_snapshot_is_frozen():
    """Verify ExperientialFieldSnapshot uses frozen dataclass."""
    from agent.capabilities.consciousness.experiential_field import (
        ExperientialFieldSnapshot
    )
    
    snapshot = ExperientialFieldSnapshot(
        field_id="field-001",
        generation=0,
        created_at_utc=0.0
    )
    
    with pytest.raises((AttributeError, TypeError)):
        snapshot.generation = 1


def test_transition_is_frozen():
    """Verify FieldTransition uses frozen dataclass."""
    from agent.capabilities.consciousness.experiential_field import FieldTransition
    
    transition = FieldTransition(
        transition_id="transition-001",
        field_id="field-001",
        previous_generation=0,
        new_generation=1
    )
    
    with pytest.raises((AttributeError, TypeError)):
        transition.status = "modified"


# =============================================================================
# IDENTITY CLASS TESTS (imported from types.py directly)
# =============================================================================

def test_experiential_field_id_generates_unique_values():
    """Verify FieldId generates unique identifiers."""
    from agent.capabilities.consciousness.experiential_field.types import (
        ExperientialFieldId
    )
    
    id1 = ExperientialFieldId()
    id2 = ExperientialFieldId()
    
    assert id1.value != id2.value


def test_transition_id_is_unique():
    """Verify TransitionId generates unique identifiers."""
    from agent.capabilities.consciousness.experiential_field.types import TransitionId
    
    tid1 = TransitionId()
    tid2 = TransitionId()
    
    assert tid1.value != tid2.value


# =============================================================================
# SNAPSHOT CONSTRUCTION TESTS
# =============================================================================

def test_snapshot_initial_creation():
    """Verify initial snapshot creation."""
    from agent.capabilities.consciousness.experiential_field import (
        ExperientialFieldSnapshot
    )
    
    snapshot = ExperientialFieldSnapshot.initial("test-field")
    
    assert snapshot.field_id == "test-field"
    assert snapshot.generation == 0
    assert snapshot.is_empty is True


def test_snapshot_next_generation():
    """Verify generation increment works correctly."""
    from agent.capabilities.consciousness.experiential_field import (
        ExperientialFieldSnapshot
    )
    
    snapshot1 = ExperientialFieldSnapshot.initial("test-field")
    snapshot2 = snapshot1.next_generation("transition-001")
    
    assert snapshot2.generation == 1
    assert snapshot2.previous_generation == 0


# =============================================================================
# VALIDATION TESTS
# =============================================================================

def test_rejection_reason_enum():
    """Verify rejection reasons are properly defined."""
    from agent.capabilities.consciousness.experiential_field import (
        RejectionReason
    )
    
    assert hasattr(RejectionReason, "UNKNOWN_SOURCE")
    assert hasattr(RejectionReason, "EXPIRED")
    assert hasattr(RejectionReason, "PAYLOAD_TOO_LARGE")
    assert hasattr(RejectionReason, "UNSUPPORTED_CONTENT_KIND")
    assert hasattr(RejectionReason, "DUPLICATE_ID")


# =============================================================================
# CAPACITY TESTS
# =============================================================================

def test_capacity_policy_exists():
    """Verify capacity policy can be instantiated."""
    from agent.capabilities.consciousness.experiential_field import (
        FieldCapacityPolicy
    )
    
    policy = FieldCapacityPolicy()
    
    assert policy is not None


def test_validation_outcome_accept():
    """Verify ValidationOutcome accept method works."""
    from agent.capabilities.consciousness.experiential_field import (
        ValidationOutcome
    )
    
    outcome = ValidationOutcome.accept("test warning")
    
    assert outcome.succeeded is True
    assert len(outcome.warnings) == 1


def test_validation_outcome_reject():
    """Verify ValidationOutcome reject method works."""
    from agent.capabilities.consciousness.experiential_field import (
        ValidationOutcome,
        RejectionReason
    )
    
    outcome = ValidationOutcome.reject(RejectionReason.EXPIRED)
    
    assert outcome.succeeded is False
    assert outcome.is_rejected is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])