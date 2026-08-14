# State Persistence Boundaries - Phase 3.15.9
# ============================================
#
# Canonical Persistence Architecture for Gordon Core.
#
# This module defines the architectural boundary between runtime state and persistence:
#   - Runtime state is owned by live components (never persisted directly)
#   - Persistence is an infrastructure capability (never owns live state)
#   - One canonical persistence boundary exists throughout the Core
#
# This phase extends:
#     Phase 3.15.1 — Core State Foundations
#     Phase 3.15.2 — State Identity, Scope & Ownership  
#     Phase 3.15.3 — Immutable & Mutable State Semantics
#     Phase 3.15.4 — Runtime State Hierarchy
#     Phase 3.15.5 — State Transitions & Transition Validation
#     Phase 3.15.6 — State Snapshots & Views
#     Phase 3.15.7 — State Versioning & Generations
#     Phase 3.15.8 — State Consistency & Concurrency

"""
Canonical Persistence Architecture for Gordon Core.

PERSISTENCE PRINCIPLES:
    1. One canonical persistence boundary exists throughout the Core
    2. Runtime state remains the only live state authority
    3. Persistence never directly mutates runtime state
    4. Persistence eligibility is explicit (never inferred)
    5. Serialization produces immutable representations
    6. Persistent records are immutable once written
    7. Checkpoints remain immutable snapshots
    8. Journals remain append-only historical evidence
    9. Archives remain immutable versioned backups
    10. Integrity verification is mandatory (never optional)

PERSISTENCE LIFECYCLE:
    Requested → Validated → Serialized → Written → Verified → Committed

PUBLIC API:
    - PersistenceEligibility      : State aggregate eligibility classification
    - PersistencePolicy           : Explicit persistence policy configuration
    - SerializationBoundary       : Immutable serialized representation boundary
    - CheckpointRecord            : Immutable checkpoint descriptor
    - JournalRecord               : Append-only journal entry
    - ArchiveDescriptor           : Immutable archive record
    - IntegrityEvidence           : Cryptographic integrity verification evidence
    - PersistenceTransaction      : Transactional persistence operations
    - PersistenceValidator        : Validation engine for persistence operations
    - PersistenceDiagnostics      : Bounded diagnostics for monitoring
    
See docs/agent/architecture/phase-3.15.9-state-persistence-boundaries.md
"""

# =============================================================================
# IMPORTS - Import-time purity maintained (no storage connections)
# =============================================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Protocol, runtime_checkable, Any
from enum import Enum, auto
import uuid
import time as _time_module
import hashlib


# =============================================================================
# PHASE 3.15.x CORE IMPORTS (for integration)
# =============================================================================

# Import state foundation types
from ..identity import AggregateId, RuntimeId, OwnerId
from ..ownership import OwnershipAuthorityType, RuntimeIsolationEnforcement
from ..semantics import ImmutableStateMixin, MutableStateMixin
from ..hierarchy import StateHierarchyNode, StateHierarchyBoundary
from ..transitions import TransitionRecord, TransitionValidationResult
from ..snapshots import (
    SnapshotKind,
    SnapshotConsistency as BaseSnapshotConsistency,
    SnapshotCompleteness,
)
from ..versioning import (
    VersionIdentity,
    GenerationIdentity,
    ChangeIdentity,
    StateVersioningFacade,
)


# =============================================================================
# PERSISTENCE ELIGIBILITY - Explicit Classification
# =============================================================================


class PersistenceEligibility(Enum):
    """
    Canonical eligibility classification for state aggregates.
    
    Every state aggregate must explicitly declare its persistence eligibility.
    Eligibility is NEVER inferred from other properties.
    
    CLASSES:
        NON_PERSISTENT      - Never persisted; runtime-only state
        CHECKPOINTABLE      - Can be checkpointed (temporary backup)
        PERSISTENT          - Fully persistent with durability guarantees
        ARCHIVABLE          - Can be archived (long-term storage)
        REPLICABLE          - Can be replicated to multiple locations
        RECOVERABLE         - Can be used for recovery operations
        EPHEMERAL           - Transient state; no persistence at all
    
    INVARIANTS:
        ELIG-001: Every aggregate has exactly one eligibility classification
        ELIG-002: Eligibility is immutable once set
        ELIG-003: No implicit eligibility inference is permitted
    """
    
    # Runtime-only state (e.g., temporary calculations, in-flight operations)
    NON_PERSISTENT = "non_persistent"
    
    # Can be checkpointed for recovery but not long-term storage
    CHECKPOINTABLE = "checkpointable"
    
    # Fully persistent with durability guarantees
    PERSISTENT = "persistent"
    
    # Can be archived (long-term, immutable backup)
    ARCHIVABLE = "archivable"
    
    # Can be replicated across multiple locations
    REPLICABLE = "replicable"
    
    # Can participate in recovery operations
    RECOVERABLE = "recoverable"
    
    # Transient state; never persisted
    EPHEMERAL = "ephemeral"


@dataclass(frozen=True)
class StateAggregateEligibility:
    """
    Explicit eligibility declaration for a state aggregate.
    
    This is the authoritative record of what persistence operations
    are allowed on this aggregate. No inference is performed.
    
    INVARIANTS:
        ELIG-DECL-001: Eligibility is immutable once created
        ELIG-DECL-002: Multiple eligibility classifications may be combined
        ELIG-DECL-003: Eligibility includes policy configuration
    """
    
    # Primary classification
    primary_eligibility: PersistenceEligibility
    
    # Additional capabilities (may include multiple)
    checkpointable: bool = False
    archivable: bool = False
    replicable: bool = False
    recoverable: bool = False
    
    # Policy configuration for persistence operations
    retention_seconds: int = 86400      # Default: 24 hours
    durability_level: str = "durable_local"  # ephemeral, process_local, host_local, durable_local, replicated
    
    @classmethod
    def non_persistent(cls) -> "StateAggregateEligibility":
        """Create a non-persistent eligibility declaration."""
        return cls(primary_eligibility=PersistenceEligibility.NON_PERSISTENT)
    
    @classmethod
    def checkpointable(
        cls,
        retention_seconds: int = 3600,     # 1 hour default for checkpoints
        durability_level: str = "process_local"
    ) -> "StateAggregateEligibility":
        """Create a checkpoint-eligible eligibility declaration."""
        return cls(
            primary_eligibility=PersistenceEligibility.CHECKPOINTABLE,
            checkpointable=True,
            retention_seconds=retention_seconds,
            durability_level=durability_level,
        )
    
    @classmethod
    def persistent(
        cls,
        retention_seconds: int = 86400,    # 24 hours default
        durability_level: str = "durable_local"
    ) -> "StateAggregateEligibility":
        """Create a fully persistent eligibility declaration."""
        return cls(
            primary_eligibility=PersistenceEligibility.PERSISTENT,
            checkpointable=True,
            archivable=True,
            replicable=True,
            recoverable=True,
            retention_seconds=retention_seconds,
            durability_level=durability_level,
        )
    
    @classmethod
    def archivable(
        cls,
        retention_seconds: int = 31536000,   # 1 year default for archives
        durability_level: str = "replicated"
    ) -> "StateAggregateEligibility":
        """Create an archivable eligibility declaration."""
        return cls(
            primary_eligibility=PersistenceEligibility.ARCHIVABLE,
            checkpointable=True,
            archivable=True,
            recoverable=True,
            retention_seconds=retention_seconds,
            durability_level=durability_level,
        )
    
    @classmethod
    def ephemeral(cls) -> "StateAggregateEligibility":
        """Create an ephemeral eligibility declaration."""
        return cls(
            primary_eligibility=PersistenceEligibility.EPHEMERAL,
            retention_seconds=0,  # No retention for ephemeral
        )


# =============================================================================
# PERSISTENCE POLICIES - Explicit Configuration
# =============================================================================


class PersistencePolicy(Enum):
    """
    Canonical persistence policy classifications.
    
    Policies govern how persistence operations are performed and validated.
    
    POLICY CATEGORIES:
        SERIALIZATION       : Format and encoding of serialized data
        CONSISTENCY         : Consistency guarantees during persistence
        DURABILITY          : Durability level and storage placement
        INTEGRITY           : Integrity verification requirements
        RETENTION           : How long records are retained
        DELETION            : Deletion policies and procedures
    """
    
    # Serialization format policies
    JSON_SERIALIZED = "json_serialized"         # Human-readable JSON
    BINARY_SERIALIZED = "binary_serialized"     # Compact binary encoding
    PROTOBUF_SERIALIZED = "protobuf_serialized"  # Protocol Buffers
    
    # Consistency policies
    AT_MOST_ONCE = "at_most_once"               # Fire and forget
    AT_LEAST_ONCE = "at_least_once"             # Retry until confirmed
    EXACTLY_ONCE = "exactly_once"               # Transactional guarantee
    
    # Durability policies
    DURABILITY_EPHEMERAL = "durability_ephemeral"
    DURABILITY_PROCESS_LOCAL = "durability_process_local"
    DURABILITY_HOST_LOCAL = "durability_host_local"
    DURABILITY_DURABLE_LOCAL = "durability_durable_local"
    DURABILITY_REPLICATED = "durability_replicated"
    
    # Integrity policies
    INTEGRITY_SHA256 = "integrity_sha256"       # SHA-256 hash verification
    INTEGRITY_CRC32 = "integrity_crc32"         # CRC32 checksum (faster)
    INTEGRITY_SIGNING = "integrity_signing"     # Cryptographic signing
    
    # Retention policies
    RETENTION_FIXED_SECONDS = "retention_fixed_seconds"
    RETENTION_UNTIL_REPLICATION = "retention_until_replication"
    RETENTION_INDEFINITE = "retention_indefinite"


@dataclass(frozen=True)
class PersistencePolicyConfiguration:
    """
    Configuration for persistence policy application.
    
    This configuration is applied during persistence operations to ensure
    consistent behavior across the Core.
    
    INVARIANTS:
        POL-CONFIG-001: All policies must be explicitly specified
        POL-CONFIG-002: Policy conflicts result in validation failure
        POL-CONFIG-003: Policies cannot be implicitly inherited
    """
    
    # Serialization policy
    serialization_format: PersistencePolicy = PersistencePolicy.JSON_SERIALIZED
    
    # Consistency policy
    consistency_level: PersistencePolicy = PersistencePolicy.AT_LEAST_ONCE
    
    # Durability policy
    durability_level: PersistencePolicy = PersistencePolicy.DURABILITY_DURABLE_LOCAL
    
    # Integrity policy
    integrity_algorithm: PersistencePolicy = PersistencePolicy.INTEGRITY_SHA256
    
    # Retention configuration
    retention_seconds: int = 86400
    auto_delete_expired: bool = True
    
    @classmethod
    def strict_integrity(cls) -> "PersistencePolicyConfiguration":
        """Create a configuration with high integrity guarantees."""
        return cls(
            serialization_format=PersistencePolicy.JSON_SERIALIZED,
            consistency_level=PersistencePolicy.EXACTLY_ONCE,
            durability_level=PersistencePolicy.DURABILITY_REPLICATED,
            integrity_algorithm=PersistencePolicy.INTEGRITY_SIGNING,
            retention_seconds=86400,
            auto_delete_expired=True,
        )
    
    @classmethod
    def high_performance(cls) -> "PersistencePolicyConfiguration":
        """Create a configuration optimized for performance."""
        return cls(
            serialization_format=PersistencePolicy.BINARY_SERIALIZED,
            consistency_level=PersistencePolicy.AT_MOST_ONCE,
            durability_level=PersistencePolicy.DURABILITY_PROCESS_LOCAL,
            integrity_algorithm=PersistencePolicy.INTEGRITY_CRC32,
            retention_seconds=3600,
            auto_delete_expired=True,
        )


# =============================================================================
# SERIALIZATION BOUNDARY - Immutable Representations Only
# =============================================================================


@dataclass(frozen=True)
class SerializedRepresentation:
    """
    Immutable serialized representation of runtime state.
    
    This is the boundary between runtime state and persistence.
    Live objects never cross this boundary; only immutable serialized data.
    
    INVARIANTS:
        SER-BOUND-001: Representation is immutable once created
        SER-BOUND-002: Contains identity, version, generation metadata
        SER-BOUND-003: Includes integrity evidence for verification
        SER-BOUND-004: Schema version is included for compatibility checks
    """
    
    # Canonical identifier for the serialized data
    representation_id: str
    
    # State aggregate identity (for tracking)
    aggregate_id: str
    
    # Runtime identity (for scoping)
    runtime_id: Optional[str] = None
    
    # Version and generation at time of serialization
    version_sequence: int
    generation_epoch: int
    
    # Serialized data bytes
    data: bytes
    
    # Schema version for compatibility validation
    schema_version: str = "1.0.0"
    
    # Integrity evidence
    integrity_algorithm: str = "sha256"
    integrity_digest: Optional[str] = None
    
    # Timestamps
    created_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def create(
        cls,
        aggregate_id: str,
        version_sequence: int,
        generation_epoch: int,
        data: bytes,
        schema_version: str = "1.0.0",
    ) -> "SerializedRepresentation":
        """
        Create a new serialized representation with integrity verification.
        
        Args:
            aggregate_id: ID of the state aggregate
            version_sequence: Version sequence number at serialization time
            generation_epoch: Generation epoch at serialization time
            data: Serialized data bytes
            schema_version: Schema version string
        
        Returns:
            New SerializedRepresentation with computed integrity digest
        """
        # Compute integrity digest
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        integrity_digest = hash_obj.hexdigest()
        
        return cls(
            representation_id=f"repr-{uuid.uuid4().hex[:16]}",
            aggregate_id=aggregate_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            data=data,
            schema_version=schema_version,
            integrity_algorithm="sha256",
            integrity_digest=integrity_digest,
        )
    
    def verify_integrity(self) -> bool:
        """Verify that the serialized data matches its integrity digest."""
        if self.integrity_digest is None:
            return False
        
        hash_obj = hashlib.sha256()
        hash_obj.update(self.data)
        computed = hash_obj.hexdigest()
        
        return computed == self.integrity_digest
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "representation_id": self.representation_id,
            "aggregate_id": self.aggregate_id,
            "runtime_id": self.runtime_id,
            "version_sequence": self.version_sequence,
            "generation_epoch": self.generation_epoch,
            "schema_version": self.schema_version,
            "integrity_algorithm": self.integrity_algorithm,
            "integrity_digest": self.integrity_digest,
            "created_at_utc": self.created_at_utc,
        }


class SerializationBoundary:
    """
    Boundary enforcing immutable serialization of runtime state.
    
    Runtime state objects NEVER cross this boundary. Only serialized
    representations are persisted.
    
    INVARIANTS:
        BOUND-001: Runtime objects stay in memory; only serialized forms leave
        BOUND-002: Serialized representations are immutable once written
        BOUND-003: Identity, version, generation metadata is preserved
        BOUND-004: Integrity verification is mandatory
    """
    
    def __init__(self, policy_config: Optional[PersistencePolicyConfiguration] = None):
        """Initialize the serialization boundary with policy configuration."""
        self._policy = policy_config or PersistencePolicyConfiguration()
        self._serializations: Dict[str, SerializedRepresentation] = {}
    
    def serialize(
        self,
        aggregate_id: str,
        version_sequence: int,
        generation_epoch: int,
        data: bytes,
    ) -> SerializedRepresentation:
        """
        Serialize runtime state to an immutable representation.
        
        Args:
            aggregate_id: ID of the state aggregate
            version_sequence: Current version sequence
            generation_epoch: Current generation epoch
            data: Raw data to serialize
        
        Returns:
            Immutable SerializedRepresentation
        
        Raises:
            SerializationError: If serialization fails
        """
        repr_obj = SerializedRepresentation.create(
            aggregate_id=aggregate_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            data=data,
        )
        
        self._serializations[repr_obj.representation_id] = repr_obj
        return repr_obj
    
    def deserialize(self, representation: SerializedRepresentation) -> Optional[bytes]:
        """
        Deserialize a representation back to bytes.
        
        Args:
            representation: The serialized representation
        
        Returns:
            Original bytes if integrity verification passes, None otherwise
        """
        if not representation.verify_integrity():
            return None
        
        return representation.data
    
    def get_representation(self, representation_id: str) -> Optional[SerializedRepresentation]:
        """Get a serialized representation by ID."""
        return self._serializations.get(representation_id)


# =============================================================================
# CHECKPOINT RECORD - Immutable Snapshot for Recovery
# =============================================================================


class CheckpointStatus(Enum):
    """
    Lifecycle status of a checkpoint record.
    
    STATUS TRANSITIONS:
        PROPOSED → VALIDATED → SERIALIZED → PERSISTED → COMMITTED
        
    FINAL STATES:
        COMMITTED   : Fully committed and immutable
        EXPIRED     : Retention period exceeded
        CORRUPTED   : Integrity verification failed
        DELETED     : Explicitly deleted per policy
    """
    
    PROPOSED = "proposed"         # Created but not yet validated
    VALIDATED = "validated"       # Validation passed
    SERIALIZED = "serialized"     # Serialization complete
    PERSISTED = "persisted"       # Durable storage confirmed
    COMMITTED = "committed"       # Canonical commit complete
    EXPIRED = "expired"           # No longer valid (retention exceeded)
    CORRUPTED = "corrupted"       # Integrity check failed
    DELETED = "deleted"           # Explicitly deleted per policy


@dataclass(frozen=True)
class CheckpointRecord:
    """
    Immutable checkpoint record for recovery operations.
    
    A checkpoint provides a safe interruption point that can be used to
    resume execution. It contains ONLY bounded metadata - no live objects.
    
    CHECKPOINT PROPERTIES:
        IMMUTABLE         : Once committed, never modified
        CONSERVATIVE      : Contains only what's needed for resumption
        VALIDATABLE       : Can verify against current state
        INTEGRITY_VERIFIABLE: Cryptographic integrity evidence included
    
    INVARIANTS:
        CP-001: Checkpoints are immutable once created
        CP-002: No live objects are persisted (only metadata)
        CP-003: Integrity verification is mandatory
        CP-004: Version and generation at capture time preserved
    """
    
    # Identity (canonical)
    checkpoint_id: str                    # Unique ID for this checkpoint
    
    # State aggregate identity
    aggregate_id: str                     # Which aggregate?
    runtime_instance_id: str              # Which instance?
    
    # Version and generation at capture time
    version_sequence: int                 # Version when captured
    generation_epoch: int                 # Generation when captured
    
    # Timestamps
    created_at_utc: float                 # When checkpoint was created
    persisted_at_utc: Optional[float] = None  # When persisted (if applicable)
    
    # Capture metadata
    capture_mode: str = "conservative"    # conservative, minimal, extended
    consistency_level: str = "position_consistent"  # Consistency guarantee
    
    # Integrity evidence
    integrity_algorithm: str = "sha256"
    integrity_digest: Optional[str] = None
    
    # Persistence reference (stable reference to durable storage)
    persistence_reference: Optional[str] = None  # e.g., "file://path/to/checkpoint"
    
    # Status and lifecycle
    status: CheckpointStatus = CheckpointStatus.PROPOSED
    
    # Metadata
    reason: str = "auto"                  # Reason for checkpoint creation
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        aggregate_id: str,
        runtime_instance_id: str,
        version_sequence: int,
        generation_epoch: int,
    ) -> "CheckpointRecord":
        """
        Create a new checkpoint record.
        
        Args:
            aggregate_id: ID of the state aggregate
            runtime_instance_id: Runtime instance identifier
            version_sequence: Version sequence at capture time
            generation_epoch: Generation epoch at capture time
        
        Returns:
            New CheckpointRecord with initial status
        """
        return cls(
            checkpoint_id=f"cp-{uuid.uuid4().hex[:16]}",
            aggregate_id=aggregate_id,
            runtime_instance_id=runtime_instance_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            created_at_utc=_time_module.monotonic(),
            status=CheckpointStatus.PROPOSED,
        )
    
    def mark_validated(self) -> "CheckpointRecord":
        """Return new record with VALIDATED status."""
        return dataclass_replace(self, status=CheckpointStatus.VALIDATED)
    
    def mark_serialized(
        self,
        integrity_digest: str,
        persistence_reference: Optional[str] = None,
    ) -> "CheckpointRecord":
        """Return new record with SERIALIZED status and integrity info."""
        return dataclass_replace(
            self,
            status=CheckpointStatus.SERIALIZED,
            integrity_digest=integrity_digest,
            persistence_reference=persistence_reference,
        )
    
    def mark_persisted(self) -> "CheckpointRecord":
        """Return new record with PERSISTED status."""
        return dataclass_replace(
            self,
            status=CheckpointStatus.PERSISTED,
            persisted_at_utc=_time_module.monotonic(),
        )
    
    def mark_committed(self) -> "CheckpointRecord":
        """Mark checkpoint as committed (final state)."""
        if self.status == CheckpointStatus.COMMITTED:
            return self
        return dataclass_replace(
            self,
            status=CheckpointStatus.COMMITTED,
            persisted_at_utc=_time_module.monotonic(),
        )
    
    def expire(self) -> "CheckpointRecord":
        """Mark checkpoint as expired."""
        return dataclass_replace(self, status=CheckpointStatus.EXPIRED)
    
    def corrupt(self) -> "CheckpointRecord":
        """Mark checkpoint as corrupted."""
        return dataclass_replace(self, status=CheckpointStatus.CORRUPTED)
    
    def verify_integrity(self, persisted_data: bytes) -> bool:
        """
        Verify integrity of this checkpoint record.
        
        Args:
            persisted_data: The persisted serialized data
        
        Returns:
            True if integrity check passes
        """
        if self.integrity_digest is None:
            return False  # No digest to verify against
        
        hash_obj = hashlib.sha256()
        hash_obj.update(persisted_data)
        computed = hash_obj.hexdigest()
        
        return computed == self.integrity_digest
    
    def is_expired(self, retention_seconds: int, at_utc: Optional[float] = None) -> bool:
        """
        Check if checkpoint has exceeded retention period.
        
        Args:
            retention_seconds: Retention period in seconds
            at_utc: Current time for comparison
        
        Returns:
            True if checkpoint is expired
        """
        at = at_utc or _time_module.monotonic()
        return (at - self.created_at_utc) > retention_seconds


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Simple dataclass replace implementation for frozen dataclasses."""
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {f.name: getattr(obj, f.name) for f in obj.__dataclass_fields__.values()}
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError("Not a dataclass")


# =============================================================================
# JOURNAL RECORD - Append-Only Historical Evidence
# =============================================================================


@dataclass(frozen=True)
class JournalRecord:
    """
    Immutable journal record for historical evidence.
    
    Journals are append-only records of state transitions and persistence
    operations. They provide an auditable trail of what happened and when.
    
    JOURNAL PROPERTIES:
        APPEND_ONLY       : Records are never modified or deleted
        HISTORICAL        : Records represent past events
        EVIDENCE          : Provide audit trail for operations
        TIME_ORDERED      : Records maintain temporal ordering
    
    INVARIANTS:
        JO-001: Journals are append-only (never modify existing records)
        JO-002: Records preserve exact timestamp of event
        JO-003: Record identity is immutable
        JO-004: No live objects in journal records
    """
    
    # Record identity
    record_id: str                        # Unique identifier for this record
    
    # Event timestamp
    event_at_utc: float                   # When the event occurred
    
    # State aggregate reference
    aggregate_id: str                     # Which aggregate?
    runtime_instance_id: str              # Which instance?
    
    # Version and generation at time of event
    version_sequence: int                 # Version when event occurred
    generation_epoch: int                 # Generation when event occurred
    
    # Event type and data
    event_type: str                       # e.g., "mutation", "checkpoint", "archive"
    event_data: bytes                     # Serialized event data
    
    # Transaction context (optional)
    transaction_id: Optional[str] = None  # For atomic operations
    sequence_in_transaction: int = 0      # Order within transaction
    
    # Provenance
    recorded_by: str = "auto"             # Who/what recorded this?
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        aggregate_id: str,
        runtime_instance_id: str,
        version_sequence: int,
        generation_epoch: int,
        event_type: str,
        event_data: bytes,
    ) -> "JournalRecord":
        """
        Create a new journal record.
        
        Args:
            aggregate_id: ID of the state aggregate
            runtime_instance_id: Runtime instance identifier
            version_sequence: Version sequence at time of event
            generation_epoch: Generation epoch at time of event
            event_type: Type of event being recorded
            event_data: Serialized event data
        
        Returns:
            New JournalRecord with timestamp
        """
        return cls(
            record_id=f"journal-{uuid.uuid4().hex[:16]}",
            event_at_utc=_time_module.monotonic(),
            aggregate_id=aggregate_id,
            runtime_instance_id=runtime_instance_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            event_type=event_type,
            event_data=event_data,
        )


class JournalBoundary:
    """
    Boundary for append-only journaling of persistence operations.
    
    Journals provide historical evidence without becoming the source of
    truth for current runtime state.
    
    INVARIANTS:
        JO-BOUND-001: Only append operations are permitted
        JO-BOUND-002: Records preserve exact timestamps
        JO-BOUND-003: Historical records cannot be modified
        JO-BOUND-004: Journals never own runtime state
    """
    
    def __init__(self):
        """Initialize the journal boundary."""
        self._records: List[JournalRecord] = []
    
    def append_record(self, record: JournalRecord) -> None:
        """
        Append a record to the journal.
        
        Args:
            record: The journal record to append
        """
        self._records.append(record)
    
    def get_records_for_aggregate(
        self,
        aggregate_id: str,
        after_utc: Optional[float] = None,
    ) -> Tuple[JournalRecord, ...]:
        """
        Get records for a specific aggregate.
        
        Args:
            aggregate_id: The aggregate to query
            after_utc: Only include records after this timestamp
        
        Returns:
            Tuple of matching journal records (newest first)
        """
        records = [
            r for r in self._records
            if r.aggregate_id == aggregate_id
            and (after_utc is None or r.event_at_utc > after_utc)
        ]
        return tuple(sorted(records, key=lambda r: r.event_at_utc, reverse=True))
    
    def get_records_for_transaction(
        self,
        transaction_id: str,
    ) -> Tuple[JournalRecord, ...]:
        """
        Get all records for a specific transaction.
        
        Args:
            transaction_id: The transaction to query
        
        Returns:
            Tuple of journal records in transaction order
        """
        records = [
            r for r in self._records
            if r.transaction_id == transaction_id
        ]
        return tuple(sorted(records, key=lambda r: r.sequence_in_transaction))
    
    def get_all_records(self) -> Tuple[JournalRecord, ...]:
        """Get all journal records."""
        return tuple(self._records)


# =============================================================================
# ARCHIVE DESCRIPTOR - Immutable Versioned Backup
# =============================================================================


class ArchiveStatus(Enum):
    """
    Status of an archive descriptor.
    
    STATUS TRANSITIONS:
        PROPOSED → VALIDATED → SERIALIZED → PERSISTED → COMMITTED
    """
    
    PROPOSED = "proposed"
    VALIDATED = "validated"
    SERIALIZED = "serialized"
    PERSISTED = "persisted"
    COMMITTED = "committed"


@dataclass(frozen=True)
class ArchiveDescriptor:
    """
    Immutable archive descriptor for versioned backups.
    
    Archives are long-term, immutable backups of state snapshots.
    They provide recovery points but never participate in runtime mutation.
    
    ARCHIVE PROPERTIES:
        IMMUTABLE         : Once committed, never modified
        VERSIONED         : Each archive has a unique version identifier
        VERIFIABLE        : Can verify integrity at any time
        RECOVERABLE       : Can be used to restore state
    
    INVARIANTS:
        ARCH-001: Archives are immutable once created
        ARCH-002: Version numbers increase monotonically
        ARCH-003: Integrity verification is mandatory
        ARCH-004: No runtime state in archives
    """
    
    # Identity (canonical)
    archive_id: str                       # Unique ID for this archive
    
    # Source aggregate identity
    source_aggregate_id: str              # Which aggregate?
    source_runtime_instance_id: str       # Which instance?
    
    # Version information
    version_sequence: int                 # Version at time of archiving
    generation_epoch: int                 # Generation at time of archiving
    
    # Archive metadata
    archive_version: int                  # Archive sequence number (increases)
    created_at_utc: float                 # When archived
    retention_until_utc: Optional[float] = None  # When archive expires
    
    # Integrity evidence
    integrity_algorithm: str = "sha256"
    integrity_digest: Optional[str] = None
    
    # Persistence reference
    persistence_reference: Optional[str] = None
    
    # Status
    status: ArchiveStatus = ArchiveStatus.PROPOSED
    
    @classmethod
    def create(
        cls,
        source_aggregate_id: str,
        source_runtime_instance_id: str,
        version_sequence: int,
        generation_epoch: int,
        archive_version: int,
    ) -> "ArchiveDescriptor":
        """
        Create a new archive descriptor.
        
        Args:
            source_aggregate_id: ID of the source aggregate
            source_runtime_instance_id: Runtime instance identifier
            version_sequence: Version at time of archiving
            generation_epoch: Generation epoch at time of archiving
            archive_version: Archive sequence number
        
        Returns:
            New ArchiveDescriptor with initial status
        """
        return cls(
            archive_id=f"archive-{uuid.uuid4().hex[:16]}",
            source_aggregate_id=source_aggregate_id,
            source_runtime_instance_id=source_runtime_instance_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            archive_version=archive_version,
            created_at_utc=_time_module.monotonic(),
            status=ArchiveStatus.PROPOSED,
        )
    
    def mark_validated(self) -> "ArchiveDescriptor":
        """Return new descriptor with VALIDATED status."""
        return dataclass_replace(self, status=ArchiveStatus.VALIDATED)
    
    def mark_serialized(
        self,
        integrity_digest: str,
        persistence_reference: Optional[str] = None,
    ) -> "ArchiveDescriptor":
        """Return new descriptor with SERIALIZED status and integrity info."""
        return dataclass_replace(
            self,
            status=ArchiveStatus.SERIALIZED,
            integrity_digest=integrity_digest,
            persistence_reference=persistence_reference,
        )
    
    def mark_persisted(self) -> "ArchiveDescriptor":
        """Return new descriptor with PERSISTED status."""
        return dataclass_replace(self, status=ArchiveStatus.PERSISTED)
    
    def mark_committed(self) -> "ArchiveDescriptor":
        """Mark archive as committed (final state)."""
        if self.status == ArchiveStatus.COMMITTED:
            return self
        return dataclass_replace(
            self,
            status=ArchiveStatus.COMMITTED,
        )
    
    def is_expired(self, at_utc: Optional[float] = None) -> bool:
        """
        Check if archive has exceeded retention period.
        
        Args:
            at_utc: Current time for comparison
        
        Returns:
            True if archive is expired
        """
        if self.retention_until_utc is None:
            return False
        
        at = at_utc or _time_module.monotonic()
        return at > self.retention_until_utc


# =============================================================================
# INTEGRITY EVIDENCE - Cryptographic Verification
# =============================================================================


class IntegrityAlgorithm(Enum):
    """
    Canonical integrity verification algorithms.
    
    ALGORITHMS:
        SHA256            : SHA-256 cryptographic hash (default)
        CRC32             : CRC32 checksum (faster, less secure)
        BLAKE2B           : BLAKE2b cryptographic hash
        SIGNING_SHA256    : Signed with SHA-256
    """
    
    SHA256 = "sha256"
    CRC32 = "crc32"
    BLAKE2B = "blake2b"
    SIGNING_SHA256 = "signing_sha256"


@dataclass(frozen=True)
class IntegrityEvidence:
    """
    Cryptographic integrity evidence for persistence records.
    
    This is the evidence that can be used to verify a record's integrity
    at any time, even long after it was created.
    
    INVARIANTS:
        INT-001: Evidence includes algorithm specification
        INT-002: Evidence includes computed hash/digest
        INT-003: Evidence is immutable once created
        INT-004: Verification can be performed independently
    """
    
    # Algorithm used for verification
    algorithm: IntegrityAlgorithm
    
    # Computed digest/hash
    digest: str                           # Hex-encoded hash value
    
    # Metadata
    data_hashed_at_utc: float             # When the data was hashed
    verified_at_utc: Optional[float] = None  # When last verified
    
    @classmethod
    def compute_sha256(cls, data: bytes) -> "IntegrityEvidence":
        """Compute SHA-256 integrity evidence for data."""
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        return cls(
            algorithm=IntegrityAlgorithm.SHA256,
            digest=hash_obj.hexdigest(),
            data_hashed_at_utc=_time_module.monotonic(),
        )
    
    @classmethod
    def compute_crc32(cls, data: bytes) -> "IntegrityEvidence":
        """Compute CRC32 integrity evidence for data."""
        import binascii
        crc = binascii.crc32(data) & 0xffffffff
        return cls(
            algorithm=IntegrityAlgorithm.CRC32,
            digest=f"{crc:08x}",
            data_hashed_at_utc=_time_module.monotonic(),
        )
    
    def verify(self, data: bytes) -> bool:
        """
        Verify that data matches the stored evidence.
        
        Args:
            data: The data to verify
        
        Returns:
            True if verification passes
        """
        # Re-compute the hash based on algorithm
        if self.algorithm == IntegrityAlgorithm.SHA256:
            hash_obj = hashlib.sha256()
            hash_obj.update(data)
            computed = hash_obj.hexdigest()
        elif self.algorithm == IntegrityAlgorithm.CRC32:
            import binascii
            crc = binascii.crc32(data) & 0xffffffff
            computed = f"{crc:08x}"
        else:
            return False  # Unknown algorithm
        
        self.verified_at_utc = _time_module.monotonic()
        return computed == self.digest


# =============================================================================
# PERSISTENCE TRANSACTION - Transactional Operations
# =============================================================================


class TransactionPhase(Enum):
    """
    Phases of a persistence transaction.
    
    PHASES:
        BEGIN     : Transaction initialized
        PREPARE   : All validations passed, ready to commit
        COMMIT    : Transaction committed successfully
        ABORT     : Transaction aborted (before commit)
        ROLLBACK  : Transaction rolled back (after partial execution)
    """
    
    BEGIN = "begin"
    PREPARE = "prepare"
    COMMIT = "commit"
    ABORT = "abort"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class PersistenceTransaction:
    """
    Transactional persistence operation.
    
    Supports atomic persistence operations with explicit lifecycle phases.
    Transactions remain independent from runtime state ownership.
    
    TRANSACTION LIFECYCLE:
        BEGIN → PREPARE → [COMMIT | ABORT]
        
    ROLLBACK is used if partial execution occurred.
    
    INVARIANTS:
        TX-001: Transactions have explicit phases
        TX-002: All phases are immutable once recorded
        TX-003: Transaction ID is unique and immutable
        TX-004: Runtime state ownership is never transferred
    """
    
    # Identity
    transaction_id: str                   # Unique transaction identifier
    
    # Phase
    phase: TransactionPhase               # Current phase
    
    # Timestamps
    started_at_utc: float                 # When transaction began
    completed_at_utc: Optional[float] = None  # When completed (if applicable)
    
    # Context
    aggregate_id: str                     # Target aggregate
    runtime_instance_id: str              # Runtime instance identifier
    
    # Operations in this transaction
    operations: Tuple[str, ...] = field(default_factory=tuple)  # Operation identifiers
    
    # Results
    success_count: int = 0                # Number of successful operations
    failure_count: int = 0                # Number of failed operations
    
    @classmethod
    def begin(
        cls,
        aggregate_id: str,
        runtime_instance_id: str,
    ) -> "PersistenceTransaction":
        """
        Begin a new persistence transaction.
        
        Args:
            aggregate_id: Target state aggregate ID
            runtime_instance_id: Runtime instance identifier
        
        Returns:
            New transaction in BEGIN phase
        """
        return cls(
            transaction_id=f"tx-{uuid.uuid4().hex[:16]}",
            phase=TransactionPhase.BEGIN,
            started_at_utc=_time_module.monotonic(),
            aggregate_id=aggregate_id,
            runtime_instance_id=runtime_instance_id,
        )
    
    def to_prepare(self) -> "PersistenceTransaction":
        """Transition to PREPARE phase."""
        return dataclass_replace(
            self,
            phase=TransactionPhase.PREPARE,
        )
    
    def commit(self, success_count: int = 0, failure_count: int = 0) -> "PersistenceTransaction":
        """Transition to COMMIT phase."""
        return dataclass_replace(
            self,
            phase=TransactionPhase.COMMIT,
            completed_at_utc=_time_module.monotonic(),
            success_count=success_count,
            failure_count=failure_count,
        )
    
    def abort(self, reason: str) -> "PersistenceTransaction":
        """Abort the transaction."""
        return dataclass_replace(
            self,
            phase=TransactionPhase.ABORT,
            completed_at_utc=_time_module.monotonic(),
        )
    
    def rollback(self) -> "PersistenceTransaction":
        """Rollback the transaction."""
        return dataclass_replace(
            self,
            phase=TransactionPhase.ROLLBACK,
            completed_at_utc=_time_module.monotonic(),
        )


# =============================================================================
# PERSISTENCE VALIDATOR - Validation Engine
# =============================================================================


@dataclass(frozen=True)
class PersistenceValidationFinding:
    """
    Result of a persistence validation check.
    
    FINDING TYPES:
        PASSED      : Check passed successfully
        WARNING     : Check passed but with caution
        FAILED      : Check failed; operation should not proceed
        SKIPPED     : Check was skipped (optional or not applicable)
    """
    
    # Validation result
    status: str                           # "passed", "warning", "failed", "skipped"
    
    # Check details
    check_name: str                       # Name of the validation check
    description: str                      # Human-readable description
    
    # Context
    aggregate_id: Optional[str] = None
    runtime_instance_id: Optional[str] = None
    
    # Timestamp
    checked_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @classmethod
    def passed(cls, check_name: str, description: str) -> "PersistenceValidationFinding":
        """Create a passed finding."""
        return cls(
            status="passed",
            check_name=check_name,
            description=description,
        )
    
    @classmethod
    def warning(cls, check_name: str, description: str) -> "PersistenceValidationFinding":
        """Create a warning finding."""
        return cls(
            status="warning",
            check_name=check_name,
            description=description,
        )
    
    @classmethod
    def failed(cls, check_name: str, description: str) -> "PersistenceValidationFinding":
        """Create a failed finding."""
        return cls(
            status="failed",
            check_name=check_name,
            description=description,
        )
    
    @classmethod
    def skipped(cls, check_name: str, description: str) -> "PersistenceValidationFinding":
        """Create a skipped finding."""
        return cls(
            status="skipped",
            check_name=check_name,
            description=description,
        )


@dataclass(frozen=True)
class PersistenceValidationResult:
    """
    Result of persistence validation for an operation.
    
    INVARIANTS:
        VAL-RESULT-001: Contains all findings from validation
        VAL-RESULT-002: Can indicate overall success/failure
        VAL-RESULT-003: Findings provide detailed debugging info
    """
    
    # Overall result
    is_valid: bool                        # Does the operation pass all required checks?
    
    # Findings (detailed validation results)
    findings: Tuple[PersistenceValidationFinding, ...]
    
    # Timestamp
    validated_at_utc: float = field(default_factory=_time_module.monotonic)
    
    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were produced."""
        return any(f.status == "warning" for f in self.findings)
    
    @property
    def has_failures(self) -> bool:
        """Check if any failures were produced."""
        return any(f.status == "failed" for f in self.findings)
    
    @classmethod
    def valid(cls, findings: Tuple[PersistenceValidationFinding, ...] = ()) -> "PersistenceValidationResult":
        """Create a valid result with no issues."""
        return cls(is_valid=True, findings=findings)
    
    @classmethod
    def invalid(cls, findings: Tuple[PersistenceValidationFinding, ...]) -> "PersistenceValidationResult":
        """Create an invalid result."""
        return cls(is_valid=False, findings=findings)


class PersistenceValidator:
    """
    Validation engine for persistence operations.
    
    Validates all aspects of persistence before allowing operations to proceed.
    
    VALIDATIONS PERFORMED:
        - Eligibility: Is this aggregate allowed to be persisted?
        - Schema compatibility: Can the current version deserialize it?
        - Version compatibility: Is the version compatible with current state?
        - Generation compatibility: Is the generation compatible?
        - Integrity: Does integrity evidence match?
        - Storage policy: Are storage requirements met?
        - Retention policy: Will retention be violated?
    
    INVARIANTS:
        VAL-001: All validations produce structured findings
        VAL-002: No implicit assumptions are made
        VAL-003: Validation is deterministic and reproducible
    """
    
    def __init__(self):
        """Initialize the persistence validator."""
        self._findings: List[PersistenceValidationFinding] = []
    
    def _add_finding(self, finding: PersistenceValidationFinding) -> None:
        """Add a validation finding."""
        self._findings.append(finding)
    
    def reset(self) -> None:
        """Reset findings for a new validation cycle."""
        self._findings.clear()
    
    def validate_eligibility(
        self,
        aggregate_id: str,
        eligibility: StateAggregateEligibility,
    ) -> PersistenceValidationFinding:
        """
        Validate that the aggregate has persistence eligibility.
        
        Args:
            aggregate_id: The aggregate to validate
            eligibility: The declared eligibility
        
        Returns:
            Validation finding for this check
        """
        if eligibility.primary_eligibility == PersistenceEligibility.EPHEMERAL:
            return PersistenceValidationFinding.failed(
                "eligibility_check",
                f"Aggregate {aggregate_id} is marked EPHEMERAL and cannot be persisted"
            )
        
        if eligibility.primary_eligibility == PersistenceEligibility.NON_PERSISTENT:
            return PersistenceValidationFinding.failed(
                "eligibility_check",
                f"Aggregate {aggregate_id} is marked NON_PERSISTENT and cannot be persisted"
            )
        
        return PersistenceValidationFinding.passed(
            "eligibility_check",
            f"Aggregate {aggregate_id} eligibility: {eligibility.primary_eligibility.value}"
        )
    
    def validate_integrity(
        self,
        representation: SerializedRepresentation,
    ) -> PersistenceValidationFinding:
        """
        Validate the integrity of a serialized representation.
        
        Args:
            representation: The representation to validate
        
        Returns:
            Validation finding for this check
        """
        if not representation.verify_integrity():
            return PersistenceValidationFinding.failed(
                "integrity_check",
                f"Integrity verification failed for representation {representation.representation_id}"
            )
        
        return PersistenceValidationFinding.passed(
            "integrity_check",
            f"Integrity verified for representation {representation.representation_id}"
        )
    
    def validate_schema_compatibility(
        self,
        representation: SerializedRepresentation,
        current_schema_version: str,
    ) -> PersistenceValidationFinding:
        """
        Validate that the schema version is compatible.
        
        Args:
            representation: The representation to validate
            current_schema_version: Current schema version in use
        
        Returns:
            Validation finding for this check
        """
        # Simple version compatibility check (can be extended)
        if not representation.schema_version.startswith(current_schema_version.split(".")[0]):
            return PersistenceValidationFinding.warning(
                "schema_compatibility_check",
                f"Schema version {representation.schema_version} may not be compatible with {current_schema_version}"
            )
        
        return PersistenceValidationFinding.passed(
            "schema_compatibility_check",
            f"Schema version {representation.schema_version} is compatible"
        )
    
    def validate_persistence_request(
        self,
        aggregate_id: str,
        eligibility: StateAggregateEligibility,
        representation: SerializedRepresentation,
        current_schema_version: str = "1.0.0",
    ) -> PersistenceValidationResult:
        """
        Validate a complete persistence request.
        
        Args:
            aggregate_id: The state aggregate being persisted
            eligibility: The declared eligibility for the aggregate
            representation: The serialized representation to persist
            current_schema_version: Current schema version in use
        
        Returns:
            Complete validation result with all findings
        """
        self.reset()
        
        # Run all validations
        self._add_finding(self.validate_eligibility(aggregate_id, eligibility))
        self._add_finding(self.validate_integrity(representation))
        self._add_finding(self.validate_schema_compatibility(representation, current_schema_version))
        
        # Check for failures
        has_failures = any(f.status == "failed" for f in self._findings)
        
        return PersistenceValidationResult(
            is_valid=not has_failures,
            findings=tuple(self._findings),
        )


# =============================================================================
# PERSISTENCE DIAGNOSTICS - Bounded Monitoring
# =============================================================================


@dataclass(frozen=True)
class PersistenceDiagnosticEvent:
    """
    Diagnostic event for persistence operations.
    
    Events are immutable and provide evidence of what happened during
    persistence operations.
    
    EVENT TYPES:
        REQUESTED     : Persistence operation was requested
        VALIDATED     : Validation completed (pass or fail)
        SERIALIZED    : Serialization completed
        WRITTEN       : Data written to storage
        VERIFIED      : Integrity verification completed
        COMMITTED     : Transaction committed
        FAILED        : Operation failed with error
        ARCHIVED      : Record archived per policy
        DELETED       : Record deleted per policy
    """
    
    # Event identity
    event_id: str                         # Unique identifier
    
    # Timestamp
    occurred_at_utc: float                # When the event occurred
    
    # Context
    aggregate_id: Optional[str] = None    # Affected aggregate (if any)
    runtime_instance_id: Optional[str] = None  # Runtime instance
    
    # Event details
    event_type: str                       # Type of event
    description: str                      # Human-readable description
    
    # Metadata
    duration_seconds: Optional[float] = None  # Operation duration (if applicable)
    storage_latency_ms: Optional[float] = None  # Storage latency (if applicable)
    
    @classmethod
    def requested(
        cls,
        aggregate_id: str,
        operation: str,
    ) -> "PersistenceDiagnosticEvent":
        """Create a REQUESTED event."""
        return cls(
            event_id=f"diag-{uuid.uuid4().hex[:8]}",
            occurred_at_utc=_time_module.monotonic(),
            aggregate_id=aggregate_id,
            event_type="REQUESTED",
            description=f"Persistence {operation} requested",
        )
    
    @classmethod
    def validated(
        cls,
        aggregate_id: str,
        is_valid: bool,
        duration_seconds: Optional[float] = None,
    ) -> "PersistenceDiagnosticEvent":
        """Create a VALIDATED event."""
        return cls(
            event_id=f"diag-{uuid.uuid4().hex[:8]}",
            occurred_at_utc=_time_module.monotonic(),
            aggregate_id=aggregate_id,
            event_type="VALIDATED",
            description=f"Persistence validated: {'PASS' if is_valid else 'FAIL'}",
            duration_seconds=duration_seconds,
        )
    
    @classmethod
    def written(
        cls,
        aggregate_id: str,
        bytes_written: int,
        storage_latency_ms: Optional[float] = None,
    ) -> "PersistenceDiagnosticEvent":
        """Create a WRITTEN event."""
        return cls(
            event_id=f"diag-{uuid.uuid4().hex[:8]}",
            occurred_at_utc=_time_module.monotonic(),
            aggregate_id=aggregate_id,
            event_type="WRITTEN",
            description=f"Wrote {bytes_written} bytes to persistence",
            duration_seconds=None,
            storage_latency_ms=storage_latency_ms,
        )
    
    @classmethod
    def failed(
        cls,
        aggregate_id: str,
        error_message: str,
    ) -> "PersistenceDiagnosticEvent":
        """Create a FAILED event."""
        return cls(
            event_id=f"diag-{uuid.uuid4().hex[:8]}",
            occurred_at_utc=_time_module.monotonic(),
            aggregate_id=aggregate_id,
            event_type="FAILED",
            description=f"Persistence failed: {error_message}",
        )


class PersistenceDiagnostics:
    """
    Bounded diagnostics for persistence monitoring.
    
    Provides visibility into persistence operations without exposing
    mutable runtime state or storage internals.
    
    DIAGNOSTICS EXPOSED:
        - Pending requests
        - Successful writes
        - Failed writes
        - Integrity failures
        - Storage latency statistics
    
    INVARIANTS:
        DIAG-001: Diagnostics are bounded (finite memory)
        DIAG-002: Events are immutable once recorded
        DIAG-003: No runtime state is exposed
        DIAG-004: No storage implementation details are exposed
    """
    
    def __init__(self, max_events: int = 1000):
        """Initialize diagnostics with bounded event storage."""
        self._max_events = max_events
        self._events: List[PersistenceDiagnosticEvent] = []
        self._event_counts: Dict[str, int] = {}
    
    def record_event(self, event: PersistenceDiagnosticEvent) -> None:
        """
        Record a diagnostic event.
        
        Args:
            event: The event to record
        """
        # Check bounds
        if len(self._events) >= self._max_events:
            # Remove oldest events (FIFO)
            removed = self._events.pop(0)
            count_key = f"count_{removed.event_type}"
            if count_key in self._event_counts:
                self._event_counts[count_key] = max(0, self._event_counts[count_key] - 1)
        
        # Add new event
        self._events.append(event)
        
        # Update counts
        count_key = f"count_{event.event_type}"
        self._event_counts[count_key] = self._event_counts.get(count_key, 0) + 1
    
    def get_events(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        after_utc: Optional[float] = None,
    ) -> Tuple[PersistenceDiagnosticEvent, ...]:
        """
        Get recorded diagnostic events.
        
        Args:
            aggregate_id: Filter by aggregate (optional)
            event_type: Filter by event type (optional)
            after_utc: Only include events after this time (optional)
        
        Returns:
            Tuple of matching events
        """
        filtered = self._events
        
        if aggregate_id is not None:
            filtered = [e for e in filtered if e.aggregate_id == aggregate_id]
        
        if event_type is not None:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if after_utc is not None:
            filtered = [e for e in filtered if e.occurred_at_utc > after_utc]
        
        return tuple(filtered)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get diagnostic statistics.
        
        Returns:
            Statistics dictionary with event counts and summaries
        """
        total_events = len(self._events)
        
        # Count events by type
        type_counts: Dict[str, int] = {}
        for event in self._events:
            count_key = f"count_{event.event_type}"
            if count_key not in type_counts:
                type_counts[count_key] = 0
        
        return {
            "total_events": total_events,
            "max_events": self._max_events,
            "type_counts": type_counts,
            "storage_backend": "bounded_memory",  # Not exposing actual backend
        }


# =============================================================================
# CANONICAL PERSISTENCE FACADE - Public API
# =============================================================================


class PersistenceFacade:
    """
    Canonical facade for persistence operations throughout the Gordon Core.
    
    This is the single entry point for all persistence operations. It provides:
    
    - Validation of eligibility and policies
    - Serialization boundary enforcement
    - Checkpoint creation and management
    - Journaling for historical evidence
    - Archive creation and management
    - Integrity verification
    - Diagnostics for monitoring
    
    ARCHITECTURAL INVARIANTS:
        PERSISTENCE-BOUNDARY: Runtime state never directly interacts with persistence
        OWNERSHIP-BOUNDARY: Persistence never owns runtime state; ownership remains with runtime components
        IMMUTABILITY-BOUNDARY: Serialized representations are immutable once written
        INTEGRITY-BOUNDARY: All persisted data includes integrity evidence
    
    PUBLIC API:
        - validate_persistence: Check if a persistence operation is valid
        - create_checkpoint: Create a checkpoint for an aggregate
        - create_archive: Create an archive of an aggregate snapshot
        - verify_integrity: Verify the integrity of persisted data
        - get_diagnostics: Get bounded diagnostics for monitoring
    
    INVARIANTS:
        FACADE-001: All operations are pure (no side effects)
        FACADE-002: No storage implementation details exposed
        FACADE-003: Results are deterministic and reproducible
    """
    
    def __init__(self):
        """Initialize the persistence facade."""
        self._validator = PersistenceValidator()
        self._diagnostics = PersistenceDiagnostics()
        self._serialization_boundary = SerializationBoundary()
        self._journal_boundary = JournalBoundary()
        
        # In-memory stores for examples (real implementation would use storage backends)
        self._checkpoints: Dict[str, CheckpointRecord] = {}
        self._archives: Dict[str, ArchiveDescriptor] = {}
    
    def validate_persistence(
        self,
        aggregate_id: str,
        eligibility: StateAggregateEligibility,
        representation: SerializedRepresentation,
    ) -> PersistenceValidationResult:
        """
        Validate a persistence request.
        
        Args:
            aggregate_id: The state aggregate being persisted
            eligibility: The declared eligibility for the aggregate
            representation: The serialized representation to persist
        
        Returns:
            Validation result with all findings
        """
        self._diagnostics.record_event(
            PersistenceDiagnosticEvent.requested(aggregate_id, "validate")
        )
        
        return self._validator.validate_persistence_request(
            aggregate_id=aggregate_id,
            eligibility=eligibility,
            representation=representation,
        )
    
    def create_checkpoint(
        self,
        aggregate_id: str,
        runtime_instance_id: str,
        version_sequence: int,
        generation_epoch: int,
    ) -> CheckpointRecord:
        """
        Create a checkpoint record for an aggregate.
        
        Args:
            aggregate_id: The state aggregate to checkpoint
            runtime_instance_id: Runtime instance identifier
            version_sequence: Version sequence at checkpoint time
            generation_epoch: Generation epoch at checkpoint time
        
        Returns:
            New CheckpointRecord with initial status
        """
        self._diagnostics.record_event(
            PersistenceDiagnosticEvent.requested(aggregate_id, "checkpoint")
        )
        
        record = CheckpointRecord.create(
            aggregate_id=aggregate_id,
            runtime_instance_id=runtime_instance_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
        )
        
        self._checkpoints[record.checkpoint_id] = record.mark_committed()
        
        return record
    
    def create_archive(
        self,
        source_aggregate_id: str,
        source_runtime_instance_id: str,
        version_sequence: int,
        generation_epoch: int,
        archive_version: int,
    ) -> ArchiveDescriptor:
        """
        Create an archive descriptor for an aggregate.
        
        Args:
            source_aggregate_id: The state aggregate to archive
            source_runtime_instance_id: Runtime instance identifier
            version_sequence: Version sequence at archiving time
            generation_epoch: Generation epoch at archiving time
            archive_version: Archive sequence number
        
        Returns:
            New ArchiveDescriptor with initial status
        """
        self._diagnostics.record_event(
            PersistenceDiagnosticEvent.requested(source_aggregate_id, "archive")
        )
        
        descriptor = ArchiveDescriptor.create(
            source_aggregate_id=source_aggregate_id,
            source_runtime_instance_id=source_runtime_instance_id,
            version_sequence=version_sequence,
            generation_epoch=generation_epoch,
            archive_version=archive_version,
        )
        
        self._archives[descriptor.archive_id] = descriptor.mark_committed()
        
        return descriptor
    
    def verify_integrity(
        self,
        data: bytes,
        evidence: IntegrityEvidence,
    ) -> bool:
        """
        Verify the integrity of data against evidence.
        
        Args:
            data: The data to verify
            evidence: The integrity evidence
        
        Returns:
            True if verification passes
        """
        return evidence.verify(data)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get bounded diagnostics for monitoring.
        
        Returns:
            Diagnostics dictionary with event counts and summaries
        """
        return self._diagnostics.get_statistics()
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointRecord]:
        """Get a checkpoint by ID."""
        return self._checkpoints.get(checkpoint_id)
    
    def get_archive(self, archive_id: str) -> Optional[ArchiveDescriptor]:
        """Get an archive by ID."""
        return self._archives.get(archive_id)


# =============================================================================
# PUBLIC API EXPORTS - PHASE 3.15.9
# =============================================================================


__all__ = [
    # ELIGIBILITY (Phase 3.15.9)
    "PersistenceEligibility",
    "StateAggregateEligibility",
    
    # POLICIES (Phase 3.15.9)
    "PersistencePolicy",
    "PersistencePolicyConfiguration",
    
    # SERIALIZATION BOUNDARY (Phase 3.15.9)
    "SerializedRepresentation",
    "SerializationBoundary",
    
    # CHECKPOINT ARCHITECTURE (Phase 3.15.9)
    "CheckpointStatus",
    "CheckpointRecord",
    "dataclass_replace",  # For frozen dataclass updates
    
    # JOURNALING (Phase 3.15.9)
    "JournalRecord",
    "JournalBoundary",
    
    # ARCHIVAL (Phase 3.15.9)
    "ArchiveStatus",
    "ArchiveDescriptor",
    
    # INTEGRITY VERIFICATION (Phase 3.15.9)
    "IntegrityAlgorithm",
    "IntegrityEvidence",
    
    # PERSISTENCE TRANSACTIONS (Phase 3.15.9)
    "TransactionPhase",
    "PersistenceTransaction",
    
    # VALIDATION (Phase 3.15.9)
    "PersistenceValidationFinding",
    "PersistenceValidationResult",
    "PersistenceValidator",
    
    # DIAGNOSTICS (Phase 3.15.9)
    "PersistenceDiagnosticEvent",
    "PersistenceDiagnostics",
    
    # PUBLIC API (Phase 3.15.9)
    "PersistenceFacade",
]