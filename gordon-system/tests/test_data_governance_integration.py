# Data Governance Integration Tests
# ==================================
#
# Phase 3.7.21-I: Data Governance, Privacy, Provenance & Information Lifecycle
#
# Integration tests for the canonical data governance architecture.
# These tests validate that records own their semantics with proper authority support.

import pytest
import asyncio
import time
from typing import Dict, List, Optional

from agent.components.core.data_governance import (
    # Authorities (one per domain)
    InformationRegistry,
    LifecycleCoordinator,
    ClassificationAuthority,
    PrivacyControls,
    RetentionCoordinator,
    ArchiveManager,
    DisposalAuthority,
    
    # Models
    OwnerType,
    OwnerIdentity,
    ClassificationLevel,
    LifecycleState,
    MetadataSchema,
    RetentionPolicy,
    DisposalMethod,
    InformationRecord,
)

from agent.components.core.data_governance.exceptions import DataGovernanceError

# Keep this for compatibility - remove if not used later


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Test Suite 1: Canonical Authority Uniqueness
# =============================================================================

class TestCanonicalAuthorityUniqueness:
    """Test that exactly one canonical authority exists per domain type."""
    
    def test_information_registry_exists(self):
        """Verify InformationRegistry can be instantiated."""
        registry = InformationRegistry()
        assert registry is not None
    
    def test_lifecycle_coordinator_exists(self):
        """Verify LifecycleCoordinator can be instantiated."""
        coordinator = LifecycleCoordinator()
        assert coordinator is not None
    
    def test_classification_authority_exists(self):
        """Verify ClassificationAuthority can be instantiated."""
        authority = ClassificationAuthority()
        assert authority is not None
    
    def test_privacy_controls_exists(self):
        """Verify PrivacyControls can be instantiated."""
        controls = PrivacyControls()
        assert controls is not None
    
    def test_retention_coordinator_exists(self):
        """Verify RetentionCoordinator can be instantiated."""
        coordinator = RetentionCoordinator()
        assert coordinator is not None
    
    def test_archive_manager_exists(self):
        """Verify ArchiveManager can be instantiated."""
        manager = ArchiveManager()
        assert manager is not None
    
    def test_disposal_authority_exists(self):
        """Verify DisposalAuthority can be instantiated."""
        authority = DisposalAuthority()
        assert authority is not None


# =============================================================================
# Test Suite 2: Records Own Their Semantics (PHASE 3.7.21 REMEDIATION)
# =============================================================================

class TestRecordsOwnSemantics:
    """Test that records own their lifecycle, classification, and other semantics."""
    
    def test_record_owns_lifecycle_state(self):
        """Verify record has lifecycle_state field."""
        record = InformationRecord(
            information_id="test-001",
            content_hash="abc123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        assert record.lifecycle_state == LifecycleState.ACTIVE
    
    def test_record_owns_classification(self):
        """Verify record has classification field."""
        record = InformationRecord(
            information_id="test-002",
            content_hash="abc123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.CONFIDENTIAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        assert record.classification == ClassificationLevel.CONFIDENTIAL
    
    def test_record_owns_owner(self):
        """Verify record has owner field."""
        record = InformationRecord(
            information_id="test-003",
            content_hash="abc123",
            owner=OwnerIdentity(OwnerType.USER, "user-1"),
            classification=ClassificationLevel.PUBLIC,
            lifecycle_state=LifecycleState.CREATED,
        )
        
        assert record.owner.id == "user-1"
        assert record.owner.type == OwnerType.USER
    
    def test_record_owns_retention_schedule(self):
        """Verify record can have retention_schedule."""
        policy = RetentionPolicy(policy_id="default", retention_days=365)
        schedule = RetentionSchedule(
            information_id="test-004",
            policy=policy,
            created_at=time.time(),
        )
        
        record = InformationRecord(
            information_id="test-004",
            content_hash="abc123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
            retention_schedule=schedule,
        )
        
        assert record.retention_schedule is not None
        assert record.retention_schedule.policy.policy_id == "default"
    
    def test_record_is_immutable(self):
        """Verify records are frozen dataclasses."""
        record = InformationRecord(
            information_id="test-005",
            content_hash="abc123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        # Should not be able to modify (frozen dataclass)
        with pytest.raises(Exception):
            record.lifecycle_state = LifecycleState.CREATED


# =============================================================================
# Test Suite 3: Authority Validation
# =============================================================================

class TestAuthorityValidation:
    """Test that authorities validate transitions and policies."""
    
    def test_lifecycle_coordinator_can_validate_transition(self):
        """Verify coordinator can validate lifecycle transitions."""
        coordinator = LifecycleCoordinator()
        
        # Valid transition
        assert coordinator.can_transition(LifecycleState.RUNNING, LifecycleState.STOPPING) is True
        
        # Invalid transition (RUNNING cannot go directly to CREATED)
        assert coordinator.can_transition(LifecycleState.RUNNING, LifecycleState.CREATED) is False
    
    def test_classification_authority_validates_level(self):
        """Verify classification authority can record decisions."""
        authority = ClassificationAuthority()
        
        decision = asyncio.run(authority.record_classification(
            information_id="test-006",
            level=ClassificationLevel.SECRET,
            classifier_id="rule-based",
        ))
        
        assert decision is not None
        assert decision.level == ClassificationLevel.SECRET
    
    def test_privacy_controls_detects_personal_data(self):
        """Verify privacy controls can detect personal data."""
        controls = PrivacyControls()
        
        # Email detection
        indicator = controls.detect("Contact: john@example.com")
        
        assert indicator.detected is True
        assert "email" in indicator.types
    
    def test_retention_coordinator_validates_policy(self):
        """Verify retention coordinator validates policies."""
        coordinator = RetentionCoordinator()
        
        policy = RetentionPolicy(policy_id="valid", retention_days=365)
        
        # Valid policy
        assert coordinator.validate_policy(policy) is True
        
        # Invalid policy (negative days would fail in actual implementation)
        invalid_policy = RetentionPolicy(policy_id="invalid", retention_days=-1)
        assert coordinator.validate_policy(invalid_policy) is False


# =============================================================================
# Test Suite 4: Registration and Cataloging
# =============================================================================

class TestRegistrationAndCataloging:
    """Test registry registration and cataloging functionality."""
    
    @pytest.mark.asyncio
    async def test_register_record(self):
        """Register a record in the information registry."""
        registry = InformationRegistry()
        
        record = InformationRecord(
            information_id="test-007",
            content_hash="abc123def456",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        registered = await registry.register(record)
        
        assert registered.information_id == "test-007"
        assert registry.total_registered == 1
    
    @pytest.mark.asyncio
    async def test_get_record_by_id(self):
        """Retrieve a record by ID."""
        registry = InformationRegistry()
        
        record = InformationRecord(
            information_id="test-008",
            content_hash="hash123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        await registry.register(record)
        
        retrieved = await registry.get("test-008")
        
        assert retrieved is not None
        assert retrieved.information_id == "test-008"
    
    @pytest.mark.asyncio
    async def test_get_by_state(self):
        """Get records by lifecycle state."""
        registry = InformationRegistry()
        
        for i in range(3):
            record = InformationRecord(
                information_id=f"state-test-{i}",
                content_hash=f"hash{i}",
                owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
                classification=ClassificationLevel.INTERNAL,
                lifecycle_state=LifecycleState.ACTIVE,
            )
            await registry.register(record)
        
        active_records = await registry.get_by_state(LifecycleState.ACTIVE)
        
        assert len(active_records) == 3
    
    @pytest.mark.asyncio
    async def test_unregister_record(self):
        """Unregister a record from the registry."""
        registry = InformationRegistry()
        
        record = InformationRecord(
            information_id="test-009",
            content_hash="hash123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        await registry.register(record)
        assert registry.total_registered == 1
        
        success = await registry.unregister("test-009")
        
        assert success is True
        assert registry.total_registered == 0


# =============================================================================
# Test Suite 5: Lifecycle Transitions (Provenance Recording)
# =============================================================================

class TestLifecycleTransitions:
    """Test lifecycle transitions produce provenance records."""
    
    @pytest.mark.asyncio
    async def test_record_transition(self):
        """Record a lifecycle transition for provenance."""
        coordinator = LifecycleCoordinator()
        
        record = await coordinator.record_transition(
            from_state=LifecycleState.RUNNING,
            to_state=LifecycleState.STOPPING,
            entity_id="service-1",
            reason="Graceful shutdown",
        )
        
        assert record.from_state == LifecycleState.RUNNING
        assert record.to_state == LifecycleState.STOPPING
        assert record.entity_id == "service-1"
    
    @pytest.mark.asyncio
    async def test_invalid_transition_raises_error(self):
        """Verify invalid transitions raise errors."""
        coordinator = LifecycleCoordinator()
        
        with pytest.raises(ValueError):
            await coordinator.record_transition(
                from_state=LifecycleState.RUNNING,
                to_state=LifecycleState.CREATED,  # Invalid transition
                entity_id="service-1",
            )


# =============================================================================
# Test Suite 6: Privacy Controls (Data-Oriented)
# =============================================================================

class TestPrivacyControls:
    """Test privacy controls are data-oriented."""
    
    def test_field_filtering(self):
        """Verify field-level filtering works."""
        controls = PrivacyControls()
        
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
            "age": 30,
        }
        
        # Filter to only allow certain fields
        allowed = {"name", "email"}
        filtered = controls.filter_fields(data, allowed)
        
        assert len(filtered) == 2
        assert "password" not in filtered
    
    def test_redaction(self):
        """Verify redaction works."""
        controls = PrivacyControls()
        
        content = "Contact: john@example.com"
        indicator = controls.detect(content)
        
        redacted = controls.redact(content, indicator)
        
        assert "[EMAIL_REDACTED]" in redacted
        assert "john@example.com" not in redacted


# =============================================================================
# Test Suite 7: Retention and Disposal
# =============================================================================

class TestRetentionAndDisposal:
    """Test retention schedules and disposal records."""
    
    @pytest.mark.asyncio
    async def test_create_retention_schedule(self):
        """Create a retention schedule for an item."""
        coordinator = RetentionCoordinator()
        
        policy = RetentionPolicy(policy_id="default", retention_days=365)
        
        schedule = await coordinator.create_schedule(
            information_id="test-010",
            policy=policy,
        )
        
        assert schedule is not None
        assert schedule.policy.policy_id == "default"
    
    @pytest.mark.asyncio
    async def test_disposal_records_evidence(self):
        """Verify disposal records evidence for provenance."""
        authority = DisposalAuthority()
        
        record = await authority.dispose(
            information_id="test-011",
            method=DisposalMethod.SOFT,
            verify=True,
        )
        
        assert record is not None
        assert record.information_id == "test-011"
        assert record.method == DisposalMethod.SOFT


# =============================================================================
# Test Suite 8: Archive Operations
# =============================================================================

class TestArchiveOperations:
    """Test archival operations and provenance."""
    
    def test_archive_manager_processes_requests(self):
        """Verify archive manager can process archive requests."""
        manager = ArchiveManager()
        
        record = asyncio.run(manager.process_archive_request(
            information_id="test-012",
            reason="Compliance archiving",
            priority=1,
            include_provenance=True,
        ))
        
        assert record is not None
        assert record.information_id == "test-012"
        assert record.provenance_preserved is True


# =============================================================================
# Test Suite 9: Statistics and Diagnostics
# =============================================================================

class TestStatisticsAndDiagnostics:
    """Test authority statistics and diagnostics."""
    
    @pytest.mark.asyncio
    async def test_registry_stats(self):
        """Get registry statistics."""
        registry = InformationRegistry()
        
        for i in range(3):
            record = InformationRecord(
                information_id=f"stat-test-{i}",
                content_hash=f"hash{i}",
                owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
                classification=ClassificationLevel.INTERNAL,
                lifecycle_state=LifecycleState.ACTIVE,
            )
            await registry.register(record)
        
        stats = registry.get_stats()
        
        assert stats["total_registered"] == 3
    
    @pytest.mark.asyncio
    async def test_authority_stats(self):
        """Get authority statistics."""
        coordinator = LifecycleCoordinator()
        
        for i in range(2):
            await coordinator.record_transition(
                from_state=LifecycleState.RUNNING,
                to_state=LifecycleState.STOPPING,
                entity_id=f"service-{i}",
            )
        
        stats = {"total_transitions": coordinator.total_transitions}
        
        assert stats["total_transitions"] == 2


# =============================================================================
# Test Suite 10: Non-Negotiable Invariants (PHASE 3.7.21)
# =============================================================================

class TestNonNegotiableInvariants:
    """Test the non-negotiable invariants from Phase 3.7.21."""
    
    def test_records_own_semantics(self):
        """Invariant: Records own their semantics."""
        record = InformationRecord(
            information_id="test-013",
            content_hash="hash123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.CONFIDENTIAL,
            lifecycle_state=LifecycleState.ACTIVE,
            created_at=time.time(),
        )
        
        # All these fields are owned by the record
        assert record.information_id == "test-013"
        assert record.owner.type == OwnerType.RUNTIME
        assert record.classification == ClassificationLevel.CONFIDENTIAL
        assert record.lifecycle_state == LifecycleState.ACTIVE
        assert record.created_at > 0
    
    def test_provenance_is_immutability(self):
        """Invariant: Provenance is recorded in immutable records."""
        record = InformationRecord(
            information_id="test-014",
            content_hash="hash123",
            owner=OwnerIdentity(OwnerType.RUNTIME, "runtime-1"),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
        )
        
        # Records are frozen dataclasses
        with pytest.raises(Exception):
            record.content_hash = "new_hash"
    
    def test_privacy_is_data_oriented(self):
        """Invariant: Privacy controls are applied at point of use."""
        controls = PrivacyControls()
        
        content = "Contact: john@example.com"
        indicator = controls.detect(content)
        
        # Detection and redaction happen locally
        assert indicator.detected is True
        
        safe_content = controls.redact(content, indicator)
        assert "[EMAIL_REDACTED]" in safe_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])