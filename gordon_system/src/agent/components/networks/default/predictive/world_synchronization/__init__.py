# Canonical World Synchronization Package - Phase 4.9.6
# =======================================================
"""
World Model Synchronization Engine for Gordon Cognitive Architecture.

This package provides the semantic world model synchronization subsystem.
It synchronizes the canonical world model with the revised belief state
produced by the belief revision phase.

No Planning, Attention, or Executive Control occurs here.

Synchronization only:
- Materializes semantic knowledge from beliefs
- Updates entity representations
- Synchronizes relationship graphs
- Produces immutable world snapshots
"""
from __future__ import annotations

from gordon_system.src.agent.networks.default.predictive.world_synchronization.request import (
    WorldModelSynchronizationRequest,
    WorldModelSynchronizationResult,
    SynchronizationPolicy,
    AcceptanceCriteria,
    TransactionSummary,
    ValidationFinding,
    WorldRevisionReference,
    SynchronizationEngine,
)
from gordon_system.src.agent.networks.default.predictive.world_synchronization.validation import (
    ValidationResult,
    SynchronizationValidator,
)
from gordon_system.src.agent.networks.default.predictive.world_synchronization.transaction import (
    TransactionCheckpoint,
    Transaction,
    TransactionEngine,
    RollbackEngine,
)
from gordon_system.src.agent.networks.default.predictive.world_synchronization.snapshot import (
    WorldSnapshot,
    WorldRevisionGraph,
    SnapshotEngine,
    RevisionGraphEngine,
)
from gordon_system.src.agent.networks.default.predictive.world_synchronization.serialization import (
    Serializer,
    Deserializer,
    SerializationEngine,
)

__all__ = [
    # Request/Result
    "WorldModelSynchronizationRequest",
    "WorldModelSynchronizationResult",
    "SynchronizationPolicy",
    "AcceptanceCriteria",
    "TransactionSummary",
    "ValidationFinding",
    "WorldRevisionReference",
    "SynchronizationEngine",
    # Validation
    "ValidationResult",
    "SynchronizationValidator",
    # Transaction
    "TransactionCheckpoint",
    "Transaction",
    "TransactionEngine",
    "RollbackEngine",
    # Snapshot
    "WorldSnapshot",
    "WorldRevisionGraph",
    "SnapshotEngine",
    "RevisionGraphEngine",
    # Serialization
    "Serializer",
    "Deserializer",
    "SerializationEngine",
]