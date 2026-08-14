"""Architecture layer - structural patterns and organization.

Phase 3.7.1: Architecture Discovery Framework
=============================================

Phase 3.7.2: Authority, Dependency, Package, Import, Ownership
===============================================================

Phase 3.14.12: Synchronization & Coordination Architecture
==========================================================

Phase 3.20: Concurrency, Synchronization & Coordination Architecture
===================================================================

This package provides deterministic, repository-driven architecture discovery
and immutable architecture modeling capabilities for Gordon Core.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .discovery import (
        PackageDiscoveryManager,
        ModuleDiscoveryManager,
        AuthorityDiscoveryManager,
        DependencyDiscoveryManager,
        ImportGraphManager,
        RuntimeTopologyManager,
        ArchitectureReportManager,
        MetricsManager,
    )
    
    from .authority import (
        AuthorityKind,
        AuthorityScope,
        AuthorityId,
        RuntimeIdentity,
        AuthorityDescriptor,
        MutationRights,
        AuthorityReference,
        RegistrationStatus,
        RegistrationRequest,
        RegistrationResult,
        AuthorityRelationship,
        AuthorityRelationshipEntry,
        AuthoritySnapshot,
        AuthorityFinding,
        AuthorityReport,
        AuthorityRegistry,
    )
    
    from .duplicate_detection import (
        DuplicateAuthorityType,
        DuplicateAuthorityFinding,
        AuthorityConflict,
        HiddenAuthorityKind,
        HiddenAuthorityFinding,
        ServiceLocatorPattern,
        ServiceLocatorFinding,
        DuplicateAuthorityReport,
        HiddenAuthorityReport,
        ServiceLocatorReport,
        DuplicateAuthorityDetector,
        HiddenAuthorityDetector,
        ServiceLocatorDetector,
        detect_architecture_issues,
    )
    
    from .snapshot import (
        AuthoritySnapshotEntry,
        OwnershipGraphSnapshot,
        DependencyGraphSnapshot,
        RegistrySnapshotEntry,
        StateOwnerSnapshot,
        ArchitectureSnapshot,
        ArchitectureIntegrityManager,
    )
    
    from .synchronization import (
        SyncId,
        SyncEventId,
        SyncState,
        SyncMode,
        SyncPrimitive,
        BarrierSync,
        GateSync,
        LatchSync,
        RendezvousSync,
        CompletionGroupSync,
        CheckpointSync,
        SyncEvent,
        SyncContract,
        SyncPrimitiveFactory,
        BarrierSynchronization,
        GateSynchronization,
        LatchSynchronization,
        RendezvousSynchronization,
        CompletionGroupSynchronization,
        CheckpointSynchronization,
        SyncOwnership,
    )
    
    from .coordination import (
        CoordId,
        CoordEventId,
        CoordState,
        CoordMode,
        ParticipantDeclaration,
        CoordPrimitive,
        CoordinatorCoord,
        OrchestratorCoord,
        ArbiterCoord,
        AggregatorCoord,
        DispatcherCoord,
        SchedulerInterfaceCoord,
        AdmissionControllerCoord,
        CoordEvent,
        CoordContract,
        CoordOwnership,
        CoordObservability,
        CoordFailureType,
        CoordFailure,
        CoordinatorCoordination,
        OrchestratorCoordination,
        ArbiterCoordination,
        AggregatorCoordination,
        DispatcherCoordination,
        SchedulerInterfaceCoordination,
        AdmissionControllerCoordination,
    )
    
    from .concurrency import (
        ConcurrencyId,
        TaskGroupId,
        ConcurrencyEventId,
        ConcurrencyState,
        ExecutionDomain,
        CancellationMode,
        ExecutionContext,
        ContextPropagation,
        ExecutionScope,
        ExecutionOwnership,
        CancellationTokenSource,
        CancellationToken,
        CancellationRequestedError,
        TaskGroupConfig,
        TaskGroup,
        ConcurrencySynchronizationConfig,
        ConcurrencyCoordinationConfig,
        FairnessPolicy,
        FairnessConfig,
        MemoryOrder,
        VisibilityContract,
        DeadlockPrevention,
        LivelockPrevention,
        DeadlockPreventionConfig,
        LivelockPreventionConfig,
        BackpressureConfig,
        WorkerPoolConfig,
        ExecutorType,
        ExecutorConfig,
        ConcurrencyEvent,
        ConcurrencyDiagnostic,
        ConcurrencyPrimitive,
        ConcurrencyPrimitiveFactory,
        ConcurrencyScope,
    )

__all__ = [
    "discovery",
    "authority",
    "duplicate_detection",
    "snapshot",
    "synchronization",
    "coordination",
    "concurrency",
]