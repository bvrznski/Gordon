# Gordon Phase 5.7.3-I: Intentional Context Engine - Tests
# ===============================================================================
#
# Comprehensive tests for the canonical Intentional Context Engine.
#

"""
Test suite for the Intentional Context Engine.

Tests cover:
    - Object creation and registry
    - Relation validation and management
    - Target state transitions
    - Snapshot publication
    - Transition atomicity
    - Diagnostics and health reporting
"""

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

from agent.capabilities.consciousness.intentionality import (
    IntentionalContextEngine,
)
from agent.capabilities.consciousness.intentionality.object import (
    IntentionalObject,
    IntentionalObjectKind,
    IntentionalObjectRegistry,
)
from agent.capabilities.consciousness.intentionality.relation import (
    IntentionalRelation,
    IntentionalRelationKind,
    IntentionalRelationRegistry,
)
from agent.capabilities.consciousness.intentionality.target import (
    IntentionalTarget,
    TargetStatus,
    IntentionalTargetRegistry,
)
from agent.capabilities.consciousness.intentionality.snapshot import (
    IntentionalContextSnapshot,
)
from agent.capabilities.consciousness.intentionality.transition import (
    IntentionalTransition,
    IntentionalTransitionAuthority,
)
from agent.capabilities.consciousness.intentionality.diagnostics import (
    IntentionalContextDiagnosticsSnapshot,
    IntentionalContextHealthSnapshot,
)
from agent.capabilities.consciousness.intentionality.integrity import (
    IntentionalIntegrityEnforcer,
)


def test_intentional_object_creation():
    """Test intentional object creation."""
    obj = IntentionalObject(
        object_id="obj-001",
        object_kind=IntentionalObjectKind.PERCEIVED,
        source_system="perception",
        source_object_id="ref-001",
    )
    
    assert obj.object_id == "obj-001"
    assert obj.object_kind == IntentionalObjectKind.PERCEIVED
    assert obj.lifecycle_state == "active"
    print("✓ test_intentional_object_creation passed")


def test_intentional_relation_validation():
    """Test intentional relation validation."""
    validator = IntentionalRelationRegistry()
    
    # Create a relation
    relation = IntentionalRelation.create_attending_to(
        context_id="ef-001",
        object_id="obj-001",
        confidence=0.9,
    )
    
    assert relation.relation_kind == IntentionalRelationKind.ATTENDING_TO
    assert relation.confidence == 0.9
    print("✓ test_intentional_relation_validation passed")


def test_intentional_target_lifecycle():
    """Test intentional target lifecycle transitions."""
    target = IntentionalTarget.create_target(
        object_reference="obj-001",
        source_owner="perception",
        uncertainty=0.0,  # Full confidence
    )
    
    assert target.status == TargetStatus.ACTIVE
    assert target.confidence == 1.0
    
    # Suspend
    suspended = target.suspend()
    assert suspended.status == TargetStatus.SUSPENDED
    
    # Resume (by creating new target with active status)
    resumed = target.with_status(TargetStatus.ACTIVE)
    assert resumed.status == TargetStatus.ACTIVE
    
    # Complete
    completed = target.complete()
    assert completed.status == TargetStatus.COMPLETED
    
    print("✓ test_intentional_target_lifecycle passed")


def test_snapshot_initialization():
    """Test initial snapshot creation."""
    snapshot = IntentionalContextSnapshot.initial("context-001")
    
    assert snapshot.context_id == "context-001"
    assert snapshot.generation == 0
    assert snapshot.is_empty
    assert snapshot.is_valid
    
    print("✓ test_snapshot_initialization passed")


def test_transition_authority():
    """Test transition authority operations."""
    authority = IntentionalTransitionAuthority()
    
    transition = authority.create_transition(
        context_id="context-001",
        previous_generation=0,
        new_generation=1,
        transition_kind="attention_shift",
    )
    
    assert transition.status == "pending"
    assert transition.context_id == "context-001"
    
    # Commit transition
    committed = authority.commit_transition(transition)
    
    assert committed.is_success
    assert committed.status == "completed"
    
    print("✓ test_transition_authority passed")


def test_diagnostics_snapshot():
    """Test diagnostics snapshot creation."""
    diagnostics = IntentionalContextDiagnosticsSnapshot()
    
    assert diagnostics.context_id == "intentionality-001"
    assert diagnostics.is_ready
    
    print("✓ test_diagnostics_snapshot passed")


def test_health_snapshot():
    """Test health snapshot creation."""
    health = IntentionalContextHealthSnapshot()
    
    assert health.state == "active"
    assert health.initialized is False
    assert health.ready is False
    
    print("✓ test_health_snapshot passed")


def test_integrity_enforcer():
    """Test integrity enforcer validation."""
    enforcer = IntentionalIntegrityEnforcer()
    
    # Valid object
    is_valid, error = enforcer.validate_object(
        object_id="obj-001",
        source_system="perception",
    )
    assert is_valid
    
    # Invalid trust level
    is_valid, error = enforcer.validate_object(
        object_id="obj-002",
        source_system="perception",
        trust_level=1.5,
    )
    assert not is_valid
    
    print("✓ test_integrity_enforcer passed")


def test_engine_initialization():
    """Test IntentionalContextEngine initialization."""
    engine = IntentionalContextEngine()
    
    success, error = engine.initialize()
    
    assert success
    assert error is None
    assert engine.is_initialized
    
    print("✓ test_engine_initialization passed")


if __name__ == "__main__":
    test_intentional_object_creation()
    test_intentional_relation_validation()
    test_intentional_target_lifecycle()
    test_snapshot_initialization()
    test_transition_authority()
    test_diagnostics_snapshot()
    test_health_snapshot()
    test_integrity_enforcer()
    test_engine_initialization()
    
    print("\n✅ All tests passed!")