# Core Persistence Infrastructure
# ================================

"""
Core persistence, serialization, checkpointing, and state management.

Provides:
- PersistenceManager: Canonical runtime persistence authority
- SerializationManager: Canonical serialization authority  
- SnapshotManager: Snapshot capture and storage authority
- JournalManager: Append-only journal authority
- CheckpointManager: Checkpoint lifecycle authority
- RestoreManager: Restore and rehydration authority
- MigrationManager: Schema evolution authority
- TransactionManager: Canonical transaction authority (NEW)
- UnitOfWork: Unit of work pattern for batch operations (NEW)

Core principles:
- Persistence ≠ Serialization (serialization transforms, persistence stores)
- Snapshots ≠ Checkpoints (snapshots capture state, checkpoints enable recovery)
- Checkpoints ≠ Journals (checkpoints package state, journals record changes)
- Restore ≠ Replay (restore loads state, replay reconstructs from events)
"""

from .manager import (
    PersistenceManager,
    PersistenceRequest,
    RestoreRequest as PersistenceRestoreRequest,
    PersistResult,
    PersistenceResult,
)

from .domains import (
    StateDomain,
    StateDomainId,
    DurabilityClass,
    StateOwner,
    RuntimeId,
    BootSessionId,
    OwnerIdentity,
    StateDomainRegistry,
    DurabilityRequirements,
)

from .serialization import (
    SerializationManager,
    SchemaId,
    SchemaInfo,
    SerializationFormat,
    SerializationLimits,
    UnsafeTypeError,
    UnsupportedTypeError,
    DecodingError,
    is_unsafe_type,
    check_unsafe_types_recursive,
    CanonicalJsonCodec,
)

from .participants import (
    PersistenceParticipantProtocol,
    PersistenceDescriptor,
    CaptureMode,
    CaptureContext,
    CapturedState,
    StateVersion,
)

from .snapshots import (
    SnapshotManager,
    SnapshotType,
    SnapshotMode,
    SnapshotId,
    ParentSnapshotRef,
    SnapshotManifest,
    SnapshotSection,
    SnapshotRequest,
    SnapshotResult,
    SnapshotStatus,
)

from .journal import (
    JournalManager,
    JournalId,
    JournalRecordId,
    JournalRecordKind,
    JournalRecord,
    JournalSegment,
    JournalCursor,
    JournalAppendRequest,
    JournalAppendResult,
    JournalReplayRequest,
    JournalReplayResult,
    GapInfo,
    JournalStatus,
)

from .checkpoints import (
    CheckpointManager,
    CheckpointType,
    CheckpointMode,
    CheckpointId,
    CheckpointChainRef,
    CheckpointManifest,
    CheckpointParticipant,
    CheckpointBarrier,
    CheckpointRequest,
    CheckpointResult,
    CheckpointStatus,
)

from .restore import (
    RestoreManager,
    RestoreMode,
    SelectionPolicy,
    RestoreId,
    CheckpointSelection,
    SnapshotSelection,
    JournalRangeSelection,
    RestoreRequest as RestoreRestoreRequest,
    RestoreResult,
    RestoreStatus,
)

from .migration import (
    MigrationManager,
    MigrationId,
    SchemaVersion,
    MigrationType,
    MigrationDirection,
    MigrationEdge,
    MigrationGraph,
    MigrationRequest,
    MigrationResult,
    MigrationStatus,
    CompatibilityResult,
)

from .consistent_cut import (
    ConsistentCutPlan,
    ConsistentCutBoundary,
    ConsistentCutResult,
    QuiescentBarrier,
    CopyOnWriteSnapshot,
    CaptureVersionBoundary,
    CaptureConsistencyLevel,
)

from .retention import (
    RetentionPolicy,
    RetentionClass,
    RetentionDecision,
    GarbageCollectionPlan,
    GarbageCollectionResult,
)

from .events import (
    StateCaptureStarted,
    StateCaptureCompleted,
    SnapshotCreated,
    JournalRecordAppended,
    CheckpointRequested,
    CheckpointCommitted,
    RestoreRequested,
    RestoreCompleted,
    PersistenceDriftDetected,
    PersistenceCorruptionDetected,
    RetentionApplied,
)

from .integrity import (
    ContentDigest,
    ChecksumAlgorithm,
    IntegrityMetadata,
)

from .memory import (
    MemoryRepository,
    InMemoryMemoryRepository,
    MemoryRecord,
    MemoryQueryFilters,
    RetrievalRequest,
    RetrievalResult,
    MemoryRetriever,
    IndexCoordinator,
    MemoryExpirationManager,
    MemoryTombstone,
    MemoryAuthorization,
    PrivacyFilter,
)

from .transactions import (
    TransactionManager,
    TransactionId,
    TransactionContext,
    TransactionStatus,
    TransactionRequest,
    TransactionResult,
    SavepointId,
    Savepoint,
    OptimisticConflictError,
    PessimisticLockAcquisitionError,
    RetryBoundaries,
)

from .context import (
    PersistenceContext,
    UnitOfWork,
)

__all__ = [
    "PersistenceManager",
    "SerializationManager",
    "SnapshotManager",
    "JournalManager",
    "CheckpointManager",
    "RestoreManager",
    "MigrationManager",
    "TransactionManager",
    "UnitOfWork",
    "StateDomain",
    "StateDomainId",
    "DurabilityClass",
    "StateOwner",
    "RuntimeId",
    "BootSessionId",
    "OwnerIdentity",
    "StateDomainRegistry",
    "DurabilityRequirements",
    "SchemaId",
    "SchemaInfo",
    "SerializationFormat",
    "SerializationLimits",
    "UnsafeTypeError",
    "UnsupportedTypeError",
    "DecodingError",
    "is_unsafe_type",
    "check_unsafe_types_recursive",
    "CanonicalJsonCodec",
    "PersistenceParticipantProtocol",
    "PersistenceDescriptor",
    "CaptureMode",
    "CaptureContext",
    "CapturedState",
    "StateVersion",
    "SnapshotType",
    "SnapshotMode",
    "SnapshotId",
    "ParentSnapshotRef",
    "SnapshotManifest",
    "SnapshotSection",
    "SnapshotRequest",
    "SnapshotResult",
    "SnapshotStatus",
    "JournalId",
    "JournalRecordId",
    "JournalRecordKind",
    "JournalRecord",
    "JournalSegment",
    "JournalCursor",
    "JournalAppendRequest",
    "JournalAppendResult",
    "JournalReplayRequest",
    "JournalReplayResult",
    "GapInfo",
    "JournalStatus",
    "CheckpointType",
    "CheckpointMode",
    "CheckpointId",
    "CheckpointChainRef",
    "CheckpointManifest",
    "CheckpointParticipant",
    "CheckpointBarrier",
    "CheckpointRequest",
    "CheckpointResult",
    "CheckpointStatus",
    "RestoreMode",
    "SelectionPolicy",
    "RestoreId",
    "CheckpointSelection",
    "SnapshotSelection",
    "JournalRangeSelection",
    "RestoreRestoreRequest",
    "RestoreResult",
    "RestoreStatus",
    "MigrationType",
    "MigrationDirection",
    "MigrationEdge",
    "MigrationGraph",
    "MigrationRequest",
    "MigrationResult",
    "MigrationStatus",
    "CompatibilityResult",
    "ConsistentCutPlan",
    "ConsistentCutBoundary",
    "ConsistentCutResult",
    "QuiescentBarrier",
    "CopyOnWriteSnapshot",
    "CaptureVersionBoundary",
    "CaptureConsistencyLevel",
    "RetentionPolicy",
    "RetentionClass",
    "RetentionDecision",
    "GarbageCollectionPlan",
    "GarbageCollectionResult",
    "StateCaptureStarted",
    "StateCaptureCompleted",
    "SnapshotCreated",
    "JournalRecordAppended",
    "CheckpointRequested",
    "CheckpointCommitted",
    "RestoreRequested",
    "RestoreCompleted",
    "PersistenceDriftDetected",
    "PersistenceCorruptionDetected",
    "RetentionApplied",
    "ContentDigest",
    "ChecksumAlgorithm",
    "IntegrityMetadata",
    "MemoryRepository",
    "InMemoryMemoryRepository",
    "MemoryRecord",
    "MemoryQueryFilters",
    "RetrievalRequest",
    "RetrievalResult",
    "MemoryRetriever",
    "IndexCoordinator",
    "MemoryExpirationManager",
    "MemoryTombstone",
    "MemoryAuthorization",
    "PrivacyFilter",
    "TransactionId",
    "TransactionContext",
    "TransactionStatus",
    "TransactionRequest",
    "TransactionResult",
    "SavepointId",
    "Savepoint",
    "OptimisticConflictError",
    "PessimisticLockAcquisitionError",
    "RetryBoundaries",
    "PersistenceContext",
]