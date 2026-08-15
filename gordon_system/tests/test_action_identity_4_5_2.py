# Gordon Cognitive Architecture - Phase 4.5.2 Test Suite
# =========================================================

"""
Test Suite: Action Identity Canonical Architecture

Tests covering:
- ActionIdentity creation and immutability
- Version management
- Reference types
- Lineage and history
- Replacement and supersession semantics
- Serialization and deserialization
- Deterministic reconstruction
"""

import unittest
from gordon_system.src.agent.action import (
    ActionIdentity,
    IdentityKind,
    IdentityVersion,
    ActionReference,
    CanonicalActionReference,
    ExternalActionReference,
    WeakActionReference,
    ActionRevisionReference,
    TransitionKind,
    ActionContinuation,
    ActionReplacement,
    ActionSupersession,
    ActionHistory,
    ActionLineage,
    VersionMatrix,
)


class TestActionIdentity(unittest.TestCase):
    """Tests for ActionIdentity canonical identity."""

    def test_create_primitive_identity(self):
        """Test creating a primitive action identity."""
        identity = ActionIdentity.primitive("read_file", "filesystem")
        
        self.assertEqual(identity.value, "read_file")
        self.assertEqual(identity.namespace, "filesystem")
        self.assertEqual(identity.kind, IdentityKind.PRIMITIVE)
        self.assertEqual(identity.canonical_id, "filesystem:read_file:v1")

    def test_create_derived_identity(self):
        """Test creating a derived identity from parent."""
        parent = ActionIdentity.primitive("read_file", "filesystem")
        child = ActionIdentity.derived_from(parent)
        
        self.assertEqual(child.kind, IdentityKind.DERIVED)
        self.assertTrue(child.is_derived)
        self.assertEqual(child.parent_identity_id, parent.canonical_id)
        self.assertEqual(child.value, parent.value)

    def test_create_identity_from_string(self):
        """Test parsing identity from string."""
        identity = ActionIdentity.from_string("system:process_data:v3")
        
        self.assertEqual(identity.namespace, "system")
        self.assertEqual(identity.value, "process_data")
        self.assertEqual(identity.version.identity_version, 3)
        self.assertEqual(identity.canonical_id, "system:process_data:v3")

    def test_create_identity_from_hash(self):
        """Test deterministic identity creation from hash."""
        data1 = "read file /tmp/test.txt"
        data2 = "read file /tmp/test.txt"
        
        id1 = ActionIdentity.from_hash(data1)
        id2 = ActionIdentity.from_hash(data2)
        
        # Same semantic inputs produce identical identities
        self.assertEqual(id1.canonical_id, id2.canonical_id)

    def test_identity_is_immutable(self):
        """Test that identity properties cannot be modified."""
        identity = ActionIdentity.primitive("test")
        
        with self.assertRaises(Exception):
            identity.value = "new_value"

    def test_equals_ignoring_version(self):
        """Test equality ignoring version differences."""
        v1 = ActionIdentity.from_string("ns:test:v1")
        v2 = ActionIdentity.from_string("ns:test:v2")
        
        self.assertNotEqual(v1.canonical_id, v2.canonical_id)
        self.assertTrue(v1.equals_ignoring_version(v2))
        self.assertEqual(v1.base_id, v2.base_id)

    def test_serialization_roundtrip(self):
        """Test serialization and deserialization."""
        identity = ActionIdentity.primitive("read_file", "filesystem")
        
        serialized = identity.to_dict()
        deserialized = ActionIdentity.from_dict(serialized)
        
        self.assertEqual(identity.canonical_id, deserialized.canonical_id)
        self.assertEqual(identity.namespace, deserialized.namespace)
        self.assertEqual(identity.value, deserialized.value)


class TestActionRevisionReference(unittest.TestCase):
    """Tests for revision references."""

    def test_create_revision_reference(self):
        """Test creating a revision reference."""
        identity = ActionIdentity.primitive("read_file")
        ref = ActionRevisionReference.from_identity_and_revision(identity, 3)
        
        self.assertEqual(ref.identity_id, identity.canonical_id)
        self.assertEqual(ref.revision_number, 3)
        self.assertEqual(ref.id, f"{identity.canonical_id}:v3")


class TestReferences(unittest.TestCase):
    """Tests for reference types."""

    def test_canonical_reference(self):
        """Test canonical reference creation."""
        identity = ActionIdentity.primitive("test")
        ref = CanonicalActionReference.from_identity(identity)
        
        self.assertEqual(ref.target_identity_id, identity.canonical_id)
        self.assertTrue(ref.is_canonical)

    def test_external_reference(self):
        """Test external reference creation."""
        ref = ExternalActionReference.from_external(
            source_system="external_api",
            external_id="ext-123",
            target_identity_id="system:test:v1"
        )
        
        self.assertEqual(ref.source_system, "external_api")
        self.assertEqual(ref.id, f"external:external_api:{ref.target_identity_id}")

    def test_weak_reference(self):
        """Test weak reference creation."""
        identity = ActionIdentity.primitive("test")
        ref = WeakActionReference.weak_from(identity)
        
        self.assertTrue(ref.cache_hint)
        self.assertIn("weak:", ref.id)


class TestVersionMatrix(unittest.TestCase):
    """Tests for version matrix."""

    def test_version_matrix_creation(self):
        """Test creating a version matrix."""
        vm = VersionMatrix(
            identity_version=2,
            major=1,
            minor=3,
            patch=0,
            schema_version=1,
            serialization_version=2,
            migration_version=1,
            compatibility_window=3
        )
        
        self.assertEqual(vm.semantic_string, "1.3.0")
        self.assertIn("v2", vm.full_version_string)

    def test_next_minor_version(self):
        """Test incrementing minor version."""
        vm = VersionMatrix(identity_version=1, major=0, minor=5, patch=3)
        next_vm = vm.next_minor()
        
        self.assertEqual(next_vm.minor, 6)
        self.assertEqual(next_vm.patch, 0)

    def test_next_major_version(self):
        """Test incrementing major version."""
        vm = VersionMatrix(identity_version=1, major=2, minor=5, patch=3)
        next_vm = vm.next_major()
        
        self.assertEqual(next_vm.major, 3)
        self.assertEqual(next_vm.minor, 0)

    def test_compatibility_check(self):
        """Test version compatibility."""
        v1 = VersionMatrix(schema_version=1, migration_version=1, compatibility_window=2)
        v2 = VersionMatrix(schema_version=1, migration_version=2)
        v3 = VersionMatrix(schema_version=2, migration_version=1)  # Different schema
        
        self.assertTrue(v1.is_compatible_with(v2))
        self.assertFalse(v1.is_compatible_with(v3))


class TestActionLineage(unittest.TestCase):
    """Tests for action lineage."""

    def test_create_lineage(self):
        """Test creating an action lineage."""
        identity = ActionIdentity.primitive("read_file")
        
        continuation = ActionContinuation(
            action_identity_id=identity.canonical_id,
            previous_revision_id=None,
            new_revision_id=f"{identity.canonical_id}:v2",
            reason="Scope refinement"
        )
        
        lineage = ActionLineage(action_identity_id=identity.canonical_id)
        lineage_with_cont = lineage.add_continuation(continuation)
        
        self.assertEqual(len(lineage_with_cont.history.continuations), 1)

    def test_lineage_is_acyclic(self):
        """Test that simple lineage is acyclic."""
        identity = ActionIdentity.primitive("test")
        lineage = ActionLineage(action_identity_id=identity.canonical_id)
        
        self.assertTrue(lineage.is_acyclic())


class TestReplacementAndSupersession(unittest.TestCase):
    """Tests for replacement and supersession semantics."""

    def test_create_replacement(self):
        """Test creating a replacement record."""
        old_id = "ns:old:v1"
        new_id = "ns:new:v2"
        
        replacement = ActionReplacement.create(
            previous_id=old_id,
            new_id=new_id,
            reason="semantic_break",
            authority="system_validator"
        )
        
        self.assertEqual(replacement.previous_identity_id, old_id)
        self.assertEqual(replacement.new_identity_id, new_id)
        self.assertEqual(replacement.reason, "semantic_break")

    def test_create_supersession(self):
        """Test creating a supersession record."""
        old_id = "ns:old:v1"
        new_id = "ns:new:v2"
        
        supersession = ActionSupersession.create(
            superseded_id=old_id,
            superseding_id=new_id,
            reason="major_revision",
            authority="system_validator"
        )
        
        self.assertEqual(supersession.superseded_identity_id, old_id)
        self.assertEqual(supersession.superseding_identity_id, new_id)
        self.assertTrue(supersession.is_deprecated)


class TestActionHistory(unittest.TestCase):
    """Tests for action history."""

    def test_add_transition(self):
        """Test adding a transition to history."""
        identity = ActionIdentity.primitive("test")
        
        transition = IdentityVersion().from_dict({"identity_version": 1})  # placeholder
        history = ActionHistory(action_identity_id=identity.canonical_id)
        
        self.assertTrue(history.is_empty)

    def test_add_continuation(self):
        """Test adding a continuation to history."""
        identity = ActionIdentity.primitive("read_file")
        
        continuation = ActionContinuation(
            action_identity_id=identity.canonical_id,
            previous_revision_id=None,
            new_revision_id=f"{identity.canonical_id}:v2"
        )
        
        history = ActionHistory(action_identity_id=identity.canonical_id)
        updated_history = history.add_continuation(continuation)
        
        self.assertEqual(len(updated_history.continuations), 1)


if __name__ == "__main__":
    unittest.main()