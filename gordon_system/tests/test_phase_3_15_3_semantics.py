# Test Suite - Phase 3.15.3: Immutable & Mutable State Semantics
# =================================================================

"""
Test suite for Phase 3.15.3 immutable and mutable state semantics.

Tests cover:
    - Mutability classifications (immutable vs mutable)
    - Mutation authority and authorization
    - Mutation boundaries
    - Evidence generation
    - Audit records
    - Snapshot immutability
    - View immutability
    - Derived/cached state reconstruction
    - Append-only semantics
"""

import unittest
import sys
import os

# Add src to path for imports - gordon_system is in parent directory
gordon_src = os.path.join(os.path.dirname(__file__), '..', 'src', 'agent')
if gordon_src not in sys.path:
    sys.path.insert(0, gordon_src)


class TestStateMutabilityEnum(unittest.TestCase):
    """Tests for StateMutability enum."""
    
    def test_all_mutability_classes_exist(self):
        """Test that all mutability classes are defined."""
        from components.core.state.semantics import StateMutability
        
        # Immutable classes
        self.assertEqual(StateMutability.VALUE_OBJECT.value, "value_object")
        self.assertEqual(StateMutability.METADATA.value, "metadata")
        self.assertEqual(StateMutability.SNAPSHOT.value, "snapshot")
        self.assertEqual(StateMutability.VIEW.value, "view")
        
        # Mutable classes
        self.assertEqual(StateMutability.OWNER_MUTABLE.value, "owner_mutable")
        self.assertEqual(StateMutability.APPEND_ONLY.value, "append_only")
        self.assertEqual(StateMutability.TRANSACTIONAL.value, "transactional")
        
        # Reconstructible classes
        self.assertEqual(StateMutability.DERIVED.value, "derived")
        self.assertEqual(StateMutability.CACHED.value, "cached")
        self.assertEqual(StateMutability.EPHEMERAL.value, "ephemeral")
    
    def test_mutability_is_immutable(self):
        """Test that mutability enum values cannot be changed."""
        from agent.components.core.state.semantics import StateMutability
        
        with self.assertRaises(AttributeError):
            StateMutability.VALUE_OBJECT = "changed"


class TestMutationAuthorityTypeEnum(unittest.TestCase):
    """Tests for MutationAuthorityType enum."""
    
    def test_authority_types_exist(self):
        """Test that all authority types are defined."""
        from agent.components.core.state.semantics import MutationAuthorityType
        
        self.assertEqual(MutationAuthorityType.EXCLUSIVE_MUTATION.value, "exclusive_mutation")
        self.assertEqual(MutationAuthorityType.OBSERVATION.value, "observation")
        self.assertEqual(MutationAuthorityType.VALIDATION.value, "validation")
        self.assertEqual(MutationAuthorityType.RECONSTRUCTION.value, "reconstruction")


class TestMutationBoundaryEnum(unittest.TestCase):
    """Tests for MutationBoundary enum."""
    
    def test_boundary_types_exist(self):
        """Test that all boundary types are defined."""
        from agent.components.core.state.semantics import MutationBoundary
        
        self.assertEqual(MutationBoundary.AGGREGATE_ROOT.value, "aggregate_root")
        self.assertEqual(MutationBoundary.FIELD_LEVEL.value, "field_level")
        self.assertEqual(MutationBoundary.TRANSACTIONAL.value, "transactional")


class TestMutationResultEnum(unittest.TestCase):
    """Tests for MutationResult enum."""
    
    def test_result_types_exist(self):
        """Test that all result types are defined."""
        from agent.components.core.state.semantics import MutationResult
        
        # Success results
        self.assertEqual(MutationResult.CREATED.value, "created")
        self.assertEqual(MutationResult.UPDATED.value, "updated")
        self.assertEqual(MutationResult.APPENDED.value, "append")
        self.assertEqual(MutationResult.TRANSITIONED.value, "transitioned")
        
        # Rejection results
        self.assertEqual(MutationResult.REJECTED.value, "rejected")
        self.assertEqual(MutationResult.CONFLICTED.value, "conflicted")
        self.assertEqual(MutationResult.STALE.value, "stale_version")
        self.assertEqual(MutationResult.UNAUTHORIZED.value, "unauthorized")
        self.assertEqual(MutationResult.INVALID.value, "invalid_operation")


class TestMutationEvidence(unittest.TestCase):
    """Tests for MutationEvidence dataclass."""
    
    def test_mutation_evidence_creation(self):
        """Test creating mutation evidence."""
        from agent.components.core.state.semantics import MutationEvidence
        
        evidence = MutationEvidence.record(
            state_id="state_123",
            previous_version_sequence=0,
            resulting_version_sequence=1,
            initiating_authority="owner_abc",
            operation_kind="update",
            affected_fields=("field1", "field2"),
        )
        
        self.assertIsNotNone(evidence.evidence_id)
        self.assertEqual(evidence.state_id, "state_123")
        self.assertEqual(evidence.previous_version_sequence, 0)
        self.assertEqual(evidence.resulting_version_sequence, 1)
        self.assertEqual(evidence.initiating_authority, "owner_abc")
    
    def test_mutation_evidence_is_frozen(self):
        """Test that MutationEvidence is immutable."""
        from agent.components.core.state.semantics import MutationEvidence
        
        evidence = MutationEvidence.record(
            state_id="state_123",
            previous_version_sequence=0,
            resulting_version_sequence=1,
            initiating_authority="owner_abc",
            operation_kind="update",
        )
        
        with self.assertRaises(Exception):
            evidence.state_id = "changed"


class TestMutationAuditRecord(unittest.TestCase):
    """Tests for MutationAuditRecord dataclass."""
    
    def test_audit_record_creation(self):
        """Test creating an audit record."""
        from agent.components.core.state.semantics import (
            MutationAuditRecord,
            MutationResult,
        )
        
        audit = MutationAuditRecord.record_authorization(
            initiating_authority="owner_abc",
            requested_at_utc=1000.0,
            authorized=True,
        )
        
        self.assertIsNotNone(audit.audit_id)
        self.assertEqual(audit.initiating_authority, "owner_abc")
        self.assertTrue(audit.authorization_result in ("granted", "denied"))
    
    def test_audit_record_is_frozen(self):
        """Test that MutationAuditRecord is immutable."""
        from agent.components.core.state.semantics import MutationAuditRecord
        
        audit = MutationAuditRecord.record_authorization(
            initiating_authority="owner_abc",
            requested_at_utc=1000.0,
            authorized=True,
        )
        
        with self.assertRaises(Exception):
            audit.authorization_result = "changed"


class TestMutationAuthorization(unittest.TestCase):
    """Tests for MutationAuthorization dataclass."""
    
    def test_authorization_request_creation(self):
        """Test creating an authorization request."""
        from agent.components.core.state.semantics import MutationAuthorization
        
        auth = MutationAuthorization.request(
            state_id="state_123",
            authority_token="token_xyz",
            authority_kind="owner",
            requested_operation="update",
        )
        
        self.assertIsNotNone(auth.authorization_id)
        self.assertEqual(auth.state_id, "state_123")
        self.assertFalse(auth.is_authorized)  # Default is ungranted
    
    def test_authorization_grant_deny(self):
        """Test granting and denying authorization."""
        from agent.components.core.state.semantics import MutationAuthorization
        
        auth = MutationAuthorization.request(
            state_id="state_123",
            authority_token="token_xyz",
            authority_kind="owner",
            requested_operation="update",
        )
        
        # Grant
        granted_auth = auth.grant("owned by requester")
        self.assertTrue(granted_auth.is_authorized)
        self.assertEqual(granted_auth.authorization_reason, "owned by requester")
        
        # Deny
        denied_auth = auth.deny("not the owner")
        self.assertFalse(denied_auth.is_authorized)
        self.assertEqual(denied_auth.authorization_reason, "not the owner")


class TestMutationValidator(unittest.TestCase):
    """Tests for MutationValidator class."""
    
    def test_validate_immutable_target(self):
        """Test validation of immutable targets."""
        from agent.components.core.state.semantics import (
            MutationValidator,
            StateMutability,
        )
        
        # Immutable target should fail
        valid, reason = MutationValidator.validate_immutable_target(
            StateMutability.SNAPSHOT
        )
        self.assertFalse(valid)
        self.assertIn("immutable", reason or "")
        
        # Mutable target should pass
        valid, reason = MutationValidator.validate_immutable_target(
            StateMutability.OWNER_MUTABLE
        )
        self.assertTrue(valid)
    
    def test_validate_ownership(self):
        """Test ownership validation."""
        from agent.components.core.state.semantics import MutationValidator
        
        # Owner matches - pass
        valid, reason = MutationValidator.validate_ownership("owner1", "owner1")
        self.assertTrue(valid)
        
        # Owner doesn't match - fail
        valid, reason = MutationValidator.validate_ownership("owner1", "owner2")
        self.assertFalse(valid)
    
    def test_validate_authorization(self):
        """Test authorization validation."""
        from agent.components.core.state.semantics import MutationValidator
        
        # Authorized passes
        valid, reason = MutationValidator.validate_authorization(True)
        self.assertTrue(valid)
        
        # Not authorized fails
        valid, reason = MutationValidator.validate_authorization(False, "reason")
        self.assertFalse(valid)


class TestMutationBoundaryEnforcement(unittest.TestCase):
    """Tests for MutationBoundaryEnforcement class."""
    
    def test_enforce_aggregate_root_boundary(self):
        """Test aggregate root boundary enforcement."""
        from agent.components.core.state.semantics import (
            MutationBoundary,
            MutationBoundaryEnforcement,
        )
        
        # Aggregate-level operations allowed
        valid, reason = MutationBoundaryEnforcement.enforce_boundary(
            MutationBoundary.AGGREGATE_ROOT,
            "update",
            None  # No field access
        )
        self.assertTrue(valid)
    
    def test_check_transaction_boundary(self):
        """Test transaction boundary check."""
        from agent.components.core.state.semantics import (
            MutationBoundary,
            MutationBoundaryEnforcement,
        )
        
        valid, reason = MutationBoundaryEnforcement.check_transaction_boundary(
            "update",
            False  # Not transactional state
        )
        self.assertTrue(valid)


class TestCoreImmutableStateProtocol(unittest.TestCase):
    """Tests for CoreImmutableState protocol."""
    
    def test_protocol_is_runtime_checkable(self):
        """Test that the protocol can be checked at runtime."""
        from agent.components.core.state.semantics import (
            CoreImmutableState,
            ImmutableSnapshotView,
        )
        
        snapshot = ImmutableSnapshotView.capture(
            state_id="state_123",
            version_sequence=5,
            data={"key": "value"},
        )
        
        # Should be checkable at runtime
        self.assertIsInstance(snapshot, CoreImmutableState)


class TestOwnerMutableAggregate(unittest.TestCase):
    """Tests for OwnerMutableAggregate class."""
    
    def test_owner_mutable_creation(self):
        """Test creating an owner-mutable aggregate."""
        from agent.components.core.state.semantics import (
            OwnerMutableAggregate,
            StateMutability,
        )
        
        agg = OwnerMutableAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        self.assertEqual(agg.state_id, "agg_123")
        self.assertEqual(agg.owner_identity, "owner_xyz")
        self.assertEqual(agg.mutability_class, StateMutability.OWNER_MUTABLE)
    
    def test_mutation_authorization(self):
        """Test that only owner can mutate."""
        from agent.components.core.state.semantics import (
            OwnerMutableAggregate,
            MutationResult,
        )
        
        agg = OwnerMutableAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        # Owner should be able to update
        result, new_version = agg.apply_mutation(
            "update",
            "owner_xyz",
            updates={"key": "value"},
        )
        
        self.assertEqual(result, MutationResult.UPDATED)
        self.assertEqual(new_version, 1)  # Version incremented
    
    def test_unauthorized_mutation_rejected(self):
        """Test that unauthorized mutation is rejected."""
        from agent.components.core.state.semantics import (
            OwnerMutableAggregate,
            MutationResult,
        )
        
        agg = OwnerMutableAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        # Non-owner should be rejected
        result, new_version = agg.apply_mutation(
            "update",
            "non_owner_abc",
            updates={"key": "value"},
        )
        
        self.assertEqual(result, MutationResult.UNAUTHORIZED)
    
    def test_get_data_returns_snapshot(self):
        """Test that get_data returns a snapshot (copy)."""
        from agent.components.core.state.semantics import OwnerMutableAggregate
        
        agg = OwnerMutableAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        # Set some data
        agg.apply_mutation("update", "owner_xyz", updates={"key": "value"})
        
        # Get snapshot
        data = agg.get_data()
        data["new_key"] = "new_value"
        
        # Original should not be affected (snapshot is copy)
        original_data = agg.get_data()
        self.assertNotIn("new_key", original_data)


class TestAppendOnlyAggregate(unittest.TestCase):
    """Tests for AppendOnlyAggregate class."""
    
    def test_append_operation(self):
        """Test appending to append-only aggregate."""
        from agent.components.core.state.semantics import (
            AppendOnlyAggregate,
            MutationResult,
        )
        
        agg = AppendOnlyAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        result, new_version = agg.apply_mutation(
            "append",
            "owner_xyz",
            key="item1",
            value={"data": "value"},
        )
        
        self.assertEqual(result, MutationResult.APPENDED)
        self.assertEqual(new_version, 1)
    
    def test_append_only_allows_append(self):
        """Test that append-only rejects non-append operations."""
        from agent.components.core.state.semantics import (
            AppendOnlyAggregate,
            MutationValidator,
        )
        
        agg = AppendOnlyAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        valid, reason = agg.validate_mutation("update", "owner_xyz", True)
        self.assertFalse(valid)
    
    def test_get_items_returns_snapshot(self):
        """Test that get_items returns a snapshot."""
        from agent.components.core.state.semantics import AppendOnlyAggregate
        
        agg = AppendOnlyAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        # Add item
        agg.apply_mutation("append", "owner_xyz", key="item1", value={"data": "value"})
        
        items = agg.get_items()
        self.assertIn("item1", items)


class TestDerivedState(unittest.TestCase):
    """Tests for DerivedState class."""
    
    def test_derived_state_creation(self):
        """Test creating derived state."""
        from agent.components.core.state.semantics import (
            DerivedState,
            StateMutability,
        )
        
        derived = DerivedState(
            state_id="derived_123",
            derived_from_state_ids=("source_1", "source_2"),
        )
        
        self.assertEqual(derived.state_id, "derived_123")
        self.assertEqual(derived.mutability_class, StateMutability.DERIVED)
    
    def test_derived_state_computation(self):
        """Test computing derived value."""
        from agent.components.core.state.semantics import DerivedState
        
        class CounterDerived(DerivedState):
            def _compute_from_sources(self, sources):
                return sum(sources.values())
        
        derived = CounterDerived(
            state_id="counter_123",
            derived_from_state_ids=("source_1",),
        )
        
        result = derived.compute({"count": 5})
        
        self.assertEqual(result, 5)
        self.assertEqual(derived.get_value(), 5)
    
    def test_derived_state_invalidation(self):
        """Test invalidating derived state."""
        from agent.components.core.state.semantics import DerivedState
        
        class CounterDerived(DerivedState):
            def _compute_from_sources(self, sources):
                return sum(sources.values())
        
        derived = CounterDerived(
            state_id="counter_123",
            derived_from_state_ids=("source_1",),
        )
        
        # Compute and invalidate
        derived.compute({"count": 5})
        self.assertIsNotNone(derived.get_value())
        
        derived.invalidate()
        self.assertIsNone(derived.get_value())


class TestCachedState(unittest.TestCase):
    """Tests for CachedState class."""
    
    def test_cache_creation(self):
        """Test creating cached state."""
        from agent.components.core.state.semantics import (
            CachedState,
            StateMutability,
        )
        
        cache = CachedState(
            state_id="cache_123",
            cache_key="key_xyz",
            ttl_seconds=60.0,
        )
        
        self.assertEqual(cache.state_id, "cache_123")
        self.assertEqual(cache.cache_key, "key_xyz")
        self.assertEqual(cache.mutability_class, StateMutability.CACHED)
    
    def test_cache_set_and_get(self):
        """Test setting and getting cached value."""
        from agent.components.core.state.semantics import CachedState
        
        cache = CachedState(
            state_id="cache_123",
            cache_key="key_xyz",
            ttl_seconds=60.0,
        )
        
        # Set value
        cache.set_value("cached_data")
        self.assertEqual(cache.get_value(), "cached_data")
    
    def test_cache_invalidation(self):
        """Test invalidating cache."""
        from agent.components.core.state.semantics import CachedState
        
        cache = CachedState(
            state_id="cache_123",
            cache_key="key_xyz",
            ttl_seconds=60.0,
        )
        
        # Set and invalidate
        cache.set_value("cached_data")
        cache.invalidate()
        self.assertIsNone(cache.get_value())


class TestTransientState(unittest.TestCase):
    """Tests for TransientState class."""
    
    def test_transient_state_creation(self):
        """Test creating transient state."""
        from agent.components.core.state.semantics import (
            TransientState,
            StateMutability,
        )
        
        ts = TransientState(
            state_id="transient_123",
        )
        
        self.assertEqual(ts.state_id, "transient_123")
        self.assertEqual(ts.mutability_class, StateMutability.EPHEMERAL)
    
    def test_transient_state_set_get(self):
        """Test setting and getting transient value."""
        from agent.components.core.state.semantics import TransientState
        
        ts = TransientState(state_id="transient_123")
        
        ts.set_value("transient_data")
        self.assertEqual(ts.get_value(), "transient_data")


class TestImmutableSnapshotView(unittest.TestCase):
    """Tests for ImmutableSnapshotView dataclass."""
    
    def test_snapshot_capture(self):
        """Test creating a snapshot."""
        from agent.components.core.state.semantics import ImmutableSnapshotView
        
        snapshot = ImmutableSnapshotView.capture(
            state_id="state_123",
            version_sequence=5,
            data={"key": "value"},
        )
        
        self.assertIsNotNone(snapshot.view_id)
        self.assertEqual(snapshot.state_id, "state_123")
        self.assertEqual(snapshot.version_sequence, 5)
    
    def test_snapshot_is_frozen(self):
        """Test that snapshot is immutable."""
        from agent.components.core.state.semantics import ImmutableSnapshotView
        
        snapshot = ImmutableSnapshotView.capture(
            state_id="state_123",
            version_sequence=5,
            data={"key": "value"},
        )
        
        with self.assertRaises(Exception):
            snapshot.data["new_key"] = "new_value"
    
    def test_snapshot_field_access(self):
        """Test field access in snapshot."""
        from agent.components.core.state.semantics import ImmutableSnapshotView
        
        snapshot = ImmutableSnapshotView.capture(
            state_id="state_123",
            version_sequence=5,
            data={"key": "value", "other": "data"},
        )
        
        self.assertTrue(snapshot.has_field("key"))
        self.assertFalse(snapshot.has_field("nonexistent"))
        
        self.assertEqual(snapshot.get_field("key"), "value")
        self.assertIsNone(snapshot.get_field("nonexistent"))


class TestImmutableViewProjection(unittest.TestCase):
    """Tests for ImmutableViewProjection dataclass."""
    
    def test_view_projection_creation(self):
        """Test creating a view projection."""
        from agent.components.core.state.semantics import ImmutableViewProjection
        
        view = ImmutableViewProjection.project(
            source_state_id="state_123",
            source_version_sequence=5,
            included_fields=("field1", "field2"),
            excluded_fields=("secret_field",),
        )
        
        self.assertIsNotNone(view.view_id)
        self.assertEqual(view.source_state_id, "state_123")
    
    def test_view_projection_application(self):
        """Test applying view projection to data."""
        from agent.components.core.state.semantics import ImmutableViewProjection
        
        # Test with exclusions
        view = ImmutableViewProjection.project(
            source_state_id="state_123",
            source_version_sequence=5,
            excluded_fields=("secret",),
        )
        
        data = {"public": "value", "secret": "hidden"}
        result = view.apply_to_data(data)
        
        self.assertIn("public", result)
        self.assertNotIn("secret", result)


class TestMutationBoundaryValidator(unittest.TestCase):
    """Tests for MutationBoundaryValidator class."""
    
    def test_validate_aggregate_root_boundary(self):
        """Test aggregate root boundary validation."""
        from agent.components.core.state.semantics import (
            MutationBoundary,
            MutationBoundaryValidator,
        )
        
        valid, reason = MutationBoundaryValidator.validate_boundary_for_operation(
            MutationBoundary.AGGREGATE_ROOT,
            "update",
            tuple(),  # No fields
        )
        self.assertTrue(valid)
    
    def test_validate_field_access(self):
        """Test field access validation."""
        from agent.components.core.state.semantics import (
            MutationBoundary,
            MutationBoundaryValidator,
        )
        
        valid, reason = MutationBoundaryValidator.validate_field_access(
            MutationBoundary.FIELD_LEVEL,
            "field1",
            True,  # Has token
        )
        self.assertTrue(valid)


class TestUtilityFunctions(unittest.TestCase):
    """Tests for utility functions."""
    
    def test_validate_mutation_authorization(self):
        """Test validate_mutation_authorization function."""
        from agent.components.core.state.semantics import (
            StateMutability,
            validate_mutation_authorization,
        )
        
        # Valid mutation
        valid, reason = validate_mutation_authorization(
            target_state_mutability=StateMutability.OWNER_MUTABLE,
            requesting_authority="owner_xyz",
            state_owner="owner_xyz",
            is_authorized=True,
        )
        self.assertTrue(valid)
        
        # Immutable target rejected
        valid, reason = validate_mutation_authorization(
            target_state_mutability=StateMutability.SNAPSHOT,
            requesting_authority="anyone",
            state_owner=None,
            is_authorized=True,
        )
        self.assertFalse(valid)
    
    def test_create_mutation_audit_record(self):
        """Test create_mutation_audit_record function."""
        from agent.components.core.state.semantics import (
            MutationResult,
            create_mutation_audit_record,
        )
        
        audit = create_mutation_audit_record(
            initiating_authority="owner_xyz",
            requested_at_utc=1000.0,
            authorized=True,
            pre_validation_passed=True,
            invariant_validation_passed=True,
            result_code=MutationResult.UPDATED,
        )
        
        self.assertIsNotNone(audit.audit_id)
        self.assertEqual(audit.authorization_result, "granted")
        self.assertEqual(audit.result_code, MutationResult.UPDATED)


class TestIntegration(unittest.TestCase):
    """Integration tests for the semantics module."""
    
    def test_complete_mutation_lifecycle(self):
        """Test complete mutation lifecycle from request to evidence."""
        from agent.components.core.state.semantics import (
            OwnerMutableAggregate,
            MutationAuthorization,
            MutationValidator,
            MutationAuditRecord,
            MutationResult,
        )
        
        # 1. Create aggregate
        agg = OwnerMutableAggregate(
            state_id="agg_123",
            owner_identity="owner_xyz",
        )
        
        # 2. Create authorization request
        auth = MutationAuthorization.request(
            state_id="agg_123",
            authority_token="token_abc",
            authority_kind="owner",
            requested_operation="update",
        )
        
        # 3. Grant authorization (simulating validation)
        granted_auth = auth.grant("owned by requester")
        
        # 4. Validate mutation
        is_authorized, reason = MutationValidator.validate_authorization(
            granted_auth.is_authorized
        )
        
        self.assertTrue(is_authorized)
        
        # 5. Apply mutation
        result, new_version = agg.apply_mutation(
            "update",
            "owner_xyz",
            updates={"key": "value"},
        )
        
        self.assertEqual(result, MutationResult.UPDATED)
        self.assertEqual(new_version, 1)
        
        # 6. Create audit record
        audit = create_mutation_audit_record(
            initiating_authority="owner_xyz",
            requested_at_utc=1000.0,
            authorized=True,
            pre_validation_passed=True,
            invariant_validation_passed=True,
            result_code=result,
        )
        
        self.assertEqual(audit.result_code, MutationResult.UPDATED)


if __name__ == "__main__":
    unittest.main()