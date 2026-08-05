# Runtime Continuity Infrastructure
# =================================

"""
Runtime continuity infrastructure for Gordon Phase 3.7.36.

This package provides checkpoint-based crash recovery and runtime continuation:

Core Responsibilities:
    - Checkpoint coordination (creation, storage, validation)
    - Continuity ledger management (append-only operational transitions)
    - Participant registration and fragment collection
    - Restoration planning and execution
    - Interruption reconciliation
    - Post-restoration verification

Architecture Boundaries:
    This owns:
        - Checkpoint transaction protocol
        - Ledger record structure and ordering
        - Fragment schemas and validation
        - Participant contract enforcement
        - Storage contracts (atomic operations, retention)
        
    This does NOT own:
        - When continuity operations occur (entrypoint's responsibility)
        - Subsystem-specific state semantics
        - Live runtime object serialization
        - Determining what Gordon should remember or think
        
Ownership Split:
    Entrypoint Continuity  → when continuity occurs (startup/shutdown/trigger)
    Core Continuity         → how checkpoints, ledgers, restoration work
    Subsystems              → own their fragment state semantics

Phase: 3.7.36-I - Runtime Continuity & Crash-Recovery Integration
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import contracts, types, exceptions, config
    from . import facade, coordinator, registry
    from . import checkpoint, ledger, recovery, storage

# Import storage backend
from .storage import (
    CheckpointStorage,
    StorageOperation,
    StorageMetrics,
    CheckpointInfo,
    StorageResult,
)

# Import ledger writer
from .ledger import (
    ContinuityLedgerWriter,
    ContinuityLedgerRecordKind,
    LedgerRecord,
    LedgerTail,
)

# Import public contracts first (no dependencies)
from .contracts import (
    ContinuityParticipant,
    ParticipantId,
    CheckpointId,
    RuntimeGeneration,
    LedgerPosition,
)

# Import exceptions
from .exceptions import (
    ContinuityError,
    CheckpointNotFound,
    CheckpointCorrupt,
    ParticipantUnavailable,
    LedgerCorrupt,
)

# Import configuration
from .config import (
    ContinuityConfig,
    DEFAULT_CHECKPOINT_INTERVAL_SECONDS as DEFAULT_CHECKPOINT_INTERVAL,
    MAXIMUM_CHECKPOINT_DURATION_SECONDS as MAXIMUM_CHECKPOINT_DURATION,
)

# Import facade (main entry point for Core continuity)
from .facade import (
    ContinuityFacade,
)

# Import types that are part of the public API
from .types import (
    CheckpointConsistencyMode,
    CheckpointReason,
    LedgerRecordKind,
    CheckpointStatus,
    RestorationStatus,
    InterruptionClassification,
    ContinuityHealth,
)

# Import coordinator for internal orchestration
from .coordinator import (
    ContinuityCoordinator,
    CheckpointPlan,
    RestorationPlan,
    CheckpointTransaction,
    RestorationTransaction,
)

# Import registry for participant management
from .registry import (
    ParticipantRegistry,
    RegisteredParticipant,
    DependencyGraph,
    build_dependency_graph,
    get_restoration_order,
)

__all__ = [
    # Contracts
    "ContinuityParticipant",
    
    # Types
    "ParticipantId",
    "CheckpointId",
    "RuntimeGeneration",
    "LedgerPosition",
    
    # Exceptions
    "ContinuityError",
    "CheckpointNotFound",
    "CheckpointCorrupt",
    "ParticipantUnavailable",
    "LedgerCorrupt",
    
    # Configuration
    "ContinuityConfig",
    "DEFAULT_CHECKPOINT_INTERVAL",
    "MAXIMUM_CHECKPOINT_DURATION",
    
    # Storage backend
    "CheckpointStorage",
    "StorageOperation",
    "StorageMetrics",
    "CheckpointInfo",
    "StorageResult",
    
    # Ledger writer
    "ContinuityLedgerWriter",
    "ContinuityLedgerRecordKind",
    "LedgerRecord",
    "LedgerTail",
    
    # Facade (public API)
    "ContinuityFacade",
    
    # Types
    "CheckpointConsistencyMode",
    "CheckpointReason",
    "LedgerRecordKind",
    "CheckpointStatus",
    "RestorationStatus",
    "InterruptionClassification",
    "ContinuityHealth",
    
    # Coordinator
    "ContinuityCoordinator",
    "CheckpointPlan",
    "RestorationPlan",
    "CheckpointTransaction",
    "RestorationTransaction",
    
    # Registry
    "ParticipantRegistry",
    "RegisteredParticipant",
    "DependencyGraph",
    "build_dependency_graph",
    "get_restoration_order",
]
