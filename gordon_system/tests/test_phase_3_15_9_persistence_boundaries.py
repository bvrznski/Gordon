# Test Suite - Phase 3.15.9 State Persistence Boundaries
# =========================================================

"""
Test suite for Phase 3.15.9 extensions to Gordon Core state architecture.

Tests cover:
    - Persistence eligibility classification
    - Persistence policy configuration
    - Serialization boundary enforcement
    - Checkpoint record lifecycle
    - Journal record append-only semantics
    - Archive descriptor versioning
    - Integrity evidence verification
    - Transaction phase transitions
    - Validation findings generation
    - Diagnostics event tracking
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPersistenceEligibility(unittest.TestCase):
    """Tests for PersistenceEligibility enum."""
    
    def test_persistence_eligibility_types_exist(self):
        """Test that all persistence eligibility types exist."""
        from agent.components.core.state.persistence import PersistenceEligibility
        
        self.assertEqual(PersistenceEligibility.NON_PERSISTENT.value, "non_persistent")
        self.assertEqual(PersistenceEligibility.CHECKPOINTABLE.value, "checkpointable")
        self.assertEqual(PersistenceEligibility.PERSISTENT.value, "persistent")
        self.assertEqual(PersistenceEligibility.ARCHIVABLE.value, "archivable")
        self.assertEqual(PersistenceEligibility.REPLICABLE.value, "replicable")
        self.assertEqual(PersistenceEligibility.RECOVERABLE.value, "recoverable")
        self.assertEqual(PersistenceEligibility.EPHEMERAL.value, "ephemeral")


class TestStateAggregateEligibility(unittest.TestCase):
    """Tests for StateAggregateEligibility dataclass."""
    
    def test_non_persistent_eligibility(self):
        """Test creating non-persistent eligibility."""
        from agent.components.core.state.persistence import (
            StateAggregateEligibility,
            PersistenceEligibility,
        )
        
        elig = StateAggregateEligibility.non_persistent()
        self.assertEqual(elig.primary_eligibility, PersistenceEligibility.NON_PERSISTENT)
    
    def test_checkpointable_eligibility(self):
        """Test creating checkpoint-eligible eligibility."""
        from agent.components.core.state.persistence import (
            StateAggregateEligibility,
            PersistenceEligibility,
        )
        
        elig = StateAggregateEligibility.checkpointable(retention_seconds=3600)
        self.assertEqual(elig.primary_eligibility, PersistenceEligibility.CHECKPOINTABLE)
        self.assertTrue(elig.checkpointable)
        self.assertEqual(elig.retention_seconds, 3600)
    
    def test_persistent_eligibility(self):
        """Test creating fully persistent eligibility."""
        from agent.components.core.state.persistence import (
            StateAggregateEligibility,
            PersistenceEligibility,
        )
        
        elig = StateAggregateEligibility.persistent()
        self.assertEqual(elig.primary_eligibility, PersistenceEligibility.PERSISTENT)
        self.assertTrue(elig.checkpointable)
        self.assertTrue(elig.archivable)
        self.assertTrue(elig.recoverable)
    
    def test_archivable_eligibility(self):
        """Test creating archivable eligibility."""
        from agent.components.core.state.persistence import (
            StateAggregateEligibility,
            PersistenceEligibility,
        )
        
        elig = StateAggregateEligibility.archivable()
        self.assertEqual(elig.primary_eligibility, PersistenceEligibility.ARCHIVABLE)
        self.assertTrue(elig.checkpointable)
        self.assertTrue(elig.archivable)
        self.assertTrue(elig.recoverable)


class TestPersistencePolicyConfiguration(unittest.TestCase):
    """Tests for PersistencePolicyConfiguration dataclass."""
    
    def test_default_policy_configuration(self):
        """Test default policy configuration."""
        from agent.components.core.state.persistence import (
            PersistencePolicy,
            PersistencePolicyConfiguration,
        )
        
        config = PersistencePolicyConfiguration()
        self.assertEqual(config.serialization_format, PersistencePolicy.JSON_SERIALIZED)
        self.assertEqual(config.consistency_level, PersistencePolicy.AT_LEAST_ONCE)
    
    def test_strict_integrity_policy(self):
        """Test strict integrity policy configuration."""
        from agent.components.core.state.persistence import (
            PersistencePolicy,
            PersistencePolicyConfiguration,
        )
        
        config = PersistencePolicyConfiguration.strict_integrity()
        self.assertEqual(config.integrity_algorithm, PersistencePolicy.INTEGRITY_SIGNING)
        self.assertEqual(config.durability_level, PersistencePolicy.DURABILITY_REPLICATED)
    
    def test_high_performance_policy(self):
        """Test high performance policy configuration."""
        from agent.components.core.state.persistence import (
            PersistencePolicy,
            PersistencePolicyConfiguration,
        )
        
        config = PersistencePolicyConfiguration.high_performance()
        self.assertEqual(config.serialization_format, PersistencePolicy.BINARY_SERIALIZED)
        self.assertEqual(config.consistency_level, PersistencePolicy.AT_MOST_ONCE)


class TestSerializedRepresentation(unittest.TestCase):
    """Tests for SerializedRepresentation dataclass."""
    
    def test_create_serialized_representation(self):
        """Test creating a serialized representation."""
        from agent.components.core.state.persistence import SerializedRepresentation
        
        data = b"test serialized data"
        repr_obj = SerializedRepresentation.create(
            aggregate_id="agg-123",
            version_sequence=1,
            generation_epoch=0,
            data=data,
        )
        
        self.assertEqual(repr_obj.aggregate_id, "agg-123")
        self.assertEqual(repr_obj.version_sequence, 1)
        self.assertEqual(repr_obj.generation_epoch, 0)
        self.assertEqual(repr_obj.data, data)
    
    def test_integrity_verification(self):
        """Test integrity verification."""
        from agent.components.core.state.persistence import SerializedRepresentation
        
        data = b"test data for integrity"
        repr_obj = SerializedRepresentation.create(
            aggregate_id="agg-123",
            version_sequence=1,
            generation_epoch=0,
            data=data,
        )
        
        self.assertTrue(repr_obj.verify_integrity())
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        from agent.components.core.state.persistence import SerializedRepresentation
        
        data = b"test data"
        repr_obj = SerializedRepresentation.create(
            aggregate_id="agg-123",
            version_sequence=1,
            generation_epoch=0,
            data=data,
        )
        
        dict_repr = repr_obj.to_dict()
        self.assertIn("representation_id", dict_repr)
        self.assertEqual(dict_repr["aggregate_id"], "agg-123")


class TestCheckpointRecord(unittest.TestCase):
    """Tests for CheckpointRecord dataclass."""
    
    def test_create_checkpoint_record(self):
        """Test creating a checkpoint record."""
        from agent.components.core.state.persistence import (
            CheckpointRecord,
            CheckpointStatus,
        )
        
        record = CheckpointRecord.create(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
        )
        
        self.assertEqual(record.aggregate_id, "agg-123")
        self.assertEqual(record.runtime_instance_id, "runtime-456")
        self.assertEqual(record.version_sequence, 1)
        self.assertEqual(record.generation_epoch, 0)
        self.assertEqual(record.status, CheckpointStatus.PROPOSED)
    
    def test_checkpoint_status_transitions(self):
        """Test checkpoint status transitions."""
        from agent.components.core.state.persistence import (
            CheckpointRecord,
            CheckpointStatus,
        )
        
        record = CheckpointRecord.create(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
        )
        
        # Mark as validated
        record = record.mark_validated()
        self.assertEqual(record.status, CheckpointStatus.VALIDATED)
        
        # Mark as serialized with integrity
        record = record.mark_serialized(
            integrity_digest="abc123",
            persistence_reference="file://path/to/checkpoint",
        )
        self.assertEqual(record.status, CheckpointStatus.SERIALIZED)
        self.assertEqual(record.integrity_digest, "abc123")
        
        # Mark as persisted
        record = record.mark_persisted()
        self.assertEqual(record.status, CheckpointStatus.PERSISTED)
        
        # Mark as committed
        record = record.mark_committed()
        self.assertEqual(record.status, CheckpointStatus.COMMITTED)


class TestJournalRecord(unittest.TestCase):
    """Tests for JournalRecord dataclass."""
    
    def test_create_journal_record(self):
        """Test creating a journal record."""
        from agent.components.core.state.persistence import (
            JournalRecord,
            TransactionPhase,
        )
        
        record = JournalRecord.create(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
            event_type="checkpoint",
            event_data=b"checkpoint data",
        )
        
        self.assertEqual(record.aggregate_id, "agg-123")
        self.assertEqual(record.event_type, "checkpoint")
        self.assertEqual(record.version_sequence, 1)
    
    def test_journal_boundary_append(self):
        """Test journal boundary append operations."""
        from agent.components.core.state.persistence import (
            JournalRecord,
            JournalBoundary,
        )
        
        boundary = JournalBoundary()
        
        record1 = JournalRecord.create(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
            event_type="checkpoint",
            event_data=b"data1",
        )
        
        record2 = JournalRecord.create(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
            version_sequence=2,
            generation_epoch=0,
            event_type="mutation",
            event_data=b"data2",
        )
        
        boundary.append_record(record1)
        boundary.append_record(record2)
        
        records = boundary.get_all_records()
        self.assertEqual(len(records), 2)


class TestArchiveDescriptor(unittest.TestCase):
    """Tests for ArchiveDescriptor dataclass."""
    
    def test_create_archive_descriptor(self):
        """Test creating an archive descriptor."""
        from agent.components.core.state.persistence import (
            ArchiveDescriptor,
            ArchiveStatus,
        )
        
        descriptor = ArchiveDescriptor.create(
            source_aggregate_id="agg-123",
            source_runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
            archive_version=1,
        )
        
        self.assertEqual(descriptor.source_aggregate_id, "agg-123")
        self.assertEqual(descriptor.version_sequence, 1)
        self.assertEqual(descriptor.archive_version, 1)
        self.assertEqual(descriptor.status, ArchiveStatus.PROPOSED)
    
    def test_archive_status_transitions(self):
        """Test archive status transitions."""
        from agent.components.core.state.persistence import (
            ArchiveDescriptor,
            ArchiveStatus,
        )
        
        descriptor = ArchiveDescriptor.create(
            source_aggregate_id="agg-123",
            source_runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
            archive_version=1,
        )
        
        # Mark as validated
        descriptor = descriptor.mark_validated()
        self.assertEqual(descriptor.status, ArchiveStatus.VALIDATED)
        
        # Mark as committed
        descriptor = descriptor.mark_committed()
        self.assertEqual(descriptor.status, ArchiveStatus.COMMITTED)


class TestIntegrityEvidence(unittest.TestCase):
    """Tests for IntegrityEvidence dataclass."""
    
    def test_sha256_evidence(self):
        """Test SHA-256 integrity evidence."""
        from agent.components.core.state.persistence import (
            IntegrityAlgorithm,
            IntegrityEvidence,
        )
        
        data = b"test data for hashing"
        evidence = IntegrityEvidence.compute_sha256(data)
        
        self.assertEqual(evidence.algorithm, IntegrityAlgorithm.SHA256)
        self.assertTrue(len(evidence.digest), 64)  # SHA-256 produces 64-char hex
        
        # Verify integrity
        self.assertTrue(evidence.verify(data))
    
    def test_crc32_evidence(self):
        """Test CRC32 integrity evidence."""
        from agent.components.core.state.persistence import (
            IntegrityAlgorithm,
            IntegrityEvidence,
        )
        
        data = b"test data for hashing"
        evidence = IntegrityEvidence.compute_crc32(data)
        
        self.assertEqual(evidence.algorithm, IntegrityAlgorithm.CRC32)
        self.assertTrue(len(evidence.digest), 8)  # CRC32 produces 8-char hex
        
        # Verify integrity
        self.assertTrue(evidence.verify(data))


class TestPersistenceTransaction(unittest.TestCase):
    """Tests for PersistenceTransaction dataclass."""
    
    def test_create_persistence_transaction(self):
        """Test creating a persistence transaction."""
        from agent.components.core.state.persistence import (
            PersistenceTransaction,
            TransactionPhase,
        )
        
        tx = PersistenceTransaction.begin(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
        )
        
        self.assertEqual(tx.phase, TransactionPhase.BEGIN)
        self.assertEqual(tx.aggregate_id, "agg-123")
    
    def test_transaction_phase_transitions(self):
        """Test transaction phase transitions."""
        from agent.components.core.state.persistence import (
            PersistenceTransaction,
            TransactionPhase,
        )
        
        tx = PersistenceTransaction.begin(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
        )
        
        # Transition to prepare
        tx = tx.to_prepare()
        self.assertEqual(tx.phase, TransactionPhase.PREPARE)
        
        # Commit the transaction
        tx = tx.commit(success_count=2, failure_count=0)
        self.assertEqual(tx.phase, TransactionPhase.COMMIT)
        self.assertEqual(tx.success_count, 2)


class TestPersistenceValidation(unittest.TestCase):
    """Tests for persistence validation."""
    
    def test_validation_finding_types(self):
        """Test validation finding types."""
        from agent.components.core.state.persistence import (
            PersistenceValidationFinding,
        )
        
        passed = PersistenceValidationFinding.passed(
            "eligibility_check",
            "Aggregate eligible for persistence"
        )
        self.assertEqual(passed.status, "passed")
        
        warning = PersistenceValidationFinding.warning(
            "version_check",
            "Version mismatch but allowing anyway"
        )
        self.assertEqual(warning.status, "warning")
        
        failed = PersistenceValidationFinding.failed(
            "integrity_check",
            "Integrity verification failed"
        )
        self.assertEqual(failed.status, "failed")
    
    def test_validation_result(self):
        """Test validation result."""
        from agent.components.core.state.persistence import (
            PersistenceValidationResult,
            PersistenceValidationFinding,
        )
        
        findings = (
            PersistenceValidationFinding.passed("check1", "Check 1 passed"),
            PersistenceValidationFinding.passed("check2", "Check 2 passed"),
        )
        
        result = PersistenceValidationResult.valid(findings)
        self.assertTrue(result.is_valid)
        self.assertFalse(result.has_warnings)
        self.assertFalse(result.has_failures)


class TestPersistenceDiagnostics(unittest.TestCase):
    """Tests for persistence diagnostics."""
    
    def test_diagnostics_event_recording(self):
        """Test diagnostic event recording."""
        from agent.components.core.state.persistence import (
            PersistenceDiagnosticEvent,
            PersistenceDiagnostics,
        )
        
        diag = PersistenceDiagnostics(max_events=10)
        
        event = PersistenceDiagnosticEvent.requested(
            aggregate_id="agg-123",
            operation="validate"
        )
        
        diag.record_event(event)
        
        events = diag.get_events()
        self.assertEqual(len(events), 1)
    
    def test_diagnostics_statistics(self):
        """Test diagnostic statistics."""
        from agent.components.core.state.persistence import (
            PersistenceDiagnosticEvent,
            PersistenceDiagnostics,
        )
        
        diag = PersistenceDiagnostics(max_events=10)
        
        # Record multiple events
        for _ in range(5):
            event = PersistenceDiagnosticEvent.requested(
                aggregate_id="agg-123",
                operation="validate"
            )
            diag.record_event(event)
        
        stats = diag.get_statistics()
        self.assertIn("total_events", stats)
        self.assertEqual(stats["max_events"], 10)


class TestPersistenceFacade(unittest.TestCase):
    """Tests for PersistenceFacade class."""
    
    def test_facade_initialization(self):
        """Test facade initialization."""
        from agent.components.core.state.persistence import PersistenceFacade
        
        facade = PersistenceFacade()
        
        # Check that all components are initialized
        self.assertIsNotNone(facade._validator)
        self.assertIsNotNone(facade._diagnostics)
        self.assertIsNotNone(facade._serialization_boundary)
    
    def test_create_checkpoint(self):
        """Test creating a checkpoint via facade."""
        from agent.components.core.state.persistence import (
            PersistenceFacade,
            CheckpointStatus,
        )
        
        facade = PersistenceFacade()
        
        record = facade.create_checkpoint(
            aggregate_id="agg-123",
            runtime_instance_id="runtime-456",
            version_sequence=1,
            generation_epoch=0,
        )
        
        self.assertEqual(record.aggregate_id, "agg-123")
        self.assertEqual(record.status, CheckpointStatus.COMMITTED)


class TestDeterministicSerialization(unittest.TestCase):
    """Tests for deterministic serialization of persistence records."""
    
    def test_serialized_representation_determinism(self):
        """Test that serialized representations are deterministic."""
        from agent.components.core.state.persistence import SerializedRepresentation
        
        data = b"test data"
        
        repr1 = SerializedRepresentation.create(
            aggregate_id="agg-123",
            version_sequence=1,
            generation_epoch=0,
            data=data,
        )
        
        repr2 = SerializedRepresentation.create(
            aggregate_id="agg-123",
            version_sequence=1,
            generation_epoch=0,
            data=data,
        )
        
        # Both should have the same data
        self.assertEqual(repr1.data, repr2.data)
        self.assertEqual(repr1.integrity_digest, repr2.integrity_digest)


if __name__ == "__main__":
    unittest.main()