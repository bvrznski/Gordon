# Core Resources Infrastructure
# =============================
"""
Phase 3.7.13 - Resource Management, Allocation, Leasing & Contention

Provides:
- Canonical ResourceManager (single runtime-wide authority)
- Immutable resource descriptors with stable identity
- Explicit capacity accounting and tracking
- Reservation, allocation, lease lifecycle models
- Domain-specific allocators for non-overlapping resources
- Lease manager as sole lease authority
- Deterministic contention resolution
- Fairness enforcement
- Quota management
- Preemption under policy
- Pressure handling
- Reclamation
- Split-brain fencing

Key Invariants:
1. Exactly one canonical ResourceManager per runtime
2. Every allocation has an owner
3. Every lease has owner and expiration
4. Capacity accounting never negative
5. No direct acquisition bypasses ResourceManager
6. Reservations, allocations, leases remain distinct
7. Release always reconciled with capacity
8. Expired leases cannot authorize use
9. Stale fencing tokens rejected
10. Runtime isolation enforced

Resource Lifecycle:
    Discovery → Inventory → Classification → Capacity Evaluation → 
    Reservation → Allocation → Lease → Binding → Usage → Monitoring → 
    Release → Reconciliation

Separation of Concerns:
- ResourceManager: owns resource state, inventory, capacity truth
- ResourceAllocator: makes allocation decisions for a domain(s)
- LeaseManager: creates/renews/revokes leases with proper lifecycle
- ResourceReclaimer: coordinates reclamation per policy

This module implements Phase 3.7.13 of the Gordon cognitive agent architecture.

Phase 3.8.3 - Canonical Resource Interface Hierarchy and Provider Architecture

New components:
- Resource, ResourceHandle, ResourceOwner interfaces (Protocol-based)
- ResourcePool with warm/idle resources and recycling
- ResourceMonitor for health evaluation, accounting, metrics, tracing
- CPU/GPU/Memory/Storage/Network providers with ProviderRegistry
"""

from .manager import (
    ResourceManager,
    ResourceManagerConfig,
)

from .inventory import (
    ResourceInventory,
    ResourceInventorySnapshot,
    ResourceDescriptor,
    ResourceState,
    ResourceDomainId,
    ResourceId,
)

from .capacity import (
    CapacityModel,
    CapacitySnapshot,
    CapacityLedger,
    CapacityVersion,
)

from .reservations import (
    ReservationRequest,
    ReservationRequirement,
    ReservationDecision,
    Reservation,
    ReservationStatus,
    ReservationRelease,
    ReservationExpiration,
)

from .allocations import (
    AllocationRequest,
    AllocationCandidate,
    AllocationDecision,
    AllocationFailure,
    AllocationReceipt,
    AllocationResult,
    Allocation,
    AllocationState,
    AllocationId,
)

from .leases import (
    ResourceLease,
    LeaseStatus,
    LeaseCreationResult,
    LeaseRenewalResult,
    LeaseRevocationResult,
    LeaseManager,
    FencingToken,
    LeaseId,
)

from .ownership import (
    ResourceOwnership,
    OwnershipKind,
    OwnershipTransfer,
    OwnershipConflict,
    OwnerId,
    GenerationEpoch,
)

from .bindings import (
    ResourceBindingRequest,
    ResourceBinding,
    ResourceBindingResult,
    ResourceBindingFailure,
    BindingId,
)

from .contention import (
    ResourceContention,
    ContentionKind,
    ContentionState,
    ContentionDecision,
    ContentionQueue,
    ContentionSnapshot,
)

from .fairness import (
    FairnessPolicy,
    FairnessKey,
    FairnessAssessment,
    FairnessResult,
)

from .quotas import (
    ResourceQuota,
    QuotaScope,
    QuotaLimit,
    QuotaUsage,
    QuotaDecision,
    QuotaViolation,
)

from .preemption import (
    PreemptionRequest,
    PreemptionEligibility,
    PreemptionCandidate,
    PreemptionPlan,
    PreemptionResult,
    PreemptionFailure,
)

from .pressure import (
    ResourcePressure,
    PressureLevel,
    ResourcePressureObservation,
    ResourcePressureDecision,
)

from .reclamation import (
    ReclamationRequest,
    ReclamationCandidate,
    ReclamationPlan,
    ReclamationAction,
    ReclamationResult,
    ReclamationVerification,
)

from .verification import (
    VerificationStatus,
    AccountingViolation,
    CorruptedAccounting,
    SplitBrainDetection,
)

from .diagnostics import (
    ResourceManagerDiagnostics,
    ResourceReport,
    EventLogSnapshot,
)

from .shutdown_integration import (
    ShutdownPhase,
    ResourceManagerShutdownIntegration,
)

# =============================================================================
# Phase 3.8.3 - New Canonical Interfaces
# =============================================================================

from .interfaces import (
    # Identity types
    ResourceId as InterfaceResourceId,
    ResourceDomain as InterfaceResourceDomain,

    # States and capabilities
    ResourceState as InterfaceResourceState,
    ResourceCapability,
    ResourceCapabilities,
    ResourceMetadata,

    # Core interfaces (Protocols)
    Resource,
    ResourceHandle,
    ResourceOwner,
    ResourcePool as InterfaceResourcePool,
    ResourceAllocator as InterfaceResourceAllocator,
    ResourceRegistry as InterfaceResourceRegistry,
    ResourceProvider as InterfaceResourceProvider,
)

from .pooling import (
    PoolResourceState,
    PoolResourceEntry,
    ResourcePoolConfig,
    PoolAcquisitionResult,
    ResourcePool,
    PoolBackedResource,
    ResourcePoolManager,
)

from .monitoring import (
    HealthState as InterfaceHealthState,
    HealthTransition,
    HealthObservation,
    HealthEvaluator,
    AllocationEvent as InterfaceAllocationEvent,
    AllocationRecord,
    ResourceAccounting,
    MetricPoint,
    ResourceMetrics,
    LogSeverity,
    ResourceEvent,
    ResourceLogger,
    TraceSpan,
    ResourceTracer,
)

from .providers import (
    ProviderType,
    ProviderState,
    ProviderIdentity,
    ProviderConfig,
    CPUResource,
    GPUDevice,
    MemoryResource,
    StorageDevice,
    NetworkInterface,
    CPUProvider,
    GPUProvider,
    MemoryProvider,
    StorageProvider,
    NetworkProvider,
    ProviderRegistry,
)

# Re-export core types for convenience
__all__ = [
    # Manager & Inventory
    "ResourceManager",
    "ResourceManagerConfig",
    "ResourceInventory",
    "ResourceInventorySnapshot",
    "ResourceDescriptor",
    "ResourceState",
    "ResourceDomainId",
    "ResourceId",

    # Capacity
    "CapacityModel",
    "CapacitySnapshot",
    "CapacityLedger",
    "CapacityVersion",

    # Reservations
    "ReservationRequest",
    "ReservationRequirement",
    "ReservationDecision",
    "Reservation",
    "ReservationStatus",
    "ReservationRelease",
    "ReservationExpiration",

    # Allocations
    "AllocationRequest",
    "AllocationCandidate",
    "AllocationDecision",
    "AllocationFailure",
    "AllocationReceipt",
    "AllocationResult",
    "Allocation",
    "AllocationState",
    "AllocationId",

    # Leases
    "ResourceLease",
    "LeaseStatus",
    "LeaseCreationResult",
    "LeaseRenewalResult",
    "LeaseRevocationResult",
    "LeaseManager",
    "FencingToken",
    "LeaseId",

    # Ownership
    "ResourceOwnership",
    "OwnershipKind",
    "OwnershipTransfer",
    "OwnershipConflict",
    "OwnerId",
    "GenerationEpoch",

    # Bindings
    "ResourceBindingRequest",
    "ResourceBinding",
    "ResourceBindingResult",
    "ResourceBindingFailure",
    "BindingId",

    # Contention
    "ResourceContention",
    "ContentionKind",
    "ContentionState",
    "ContentionDecision",
    "ContentionQueue",
    "ContentionSnapshot",

    # Fairness
    "FairnessPolicy",
    "FairnessKey",
    "FairnessAssessment",
    "FairnessResult",

    # Quotas
    "ResourceQuota",
    "QuotaScope",
    "QuotaLimit",
    "QuotaUsage",
    "QuotaDecision",
    "QuotaViolation",

    # Preemption
    "PreemptionRequest",
    "PreemptionEligibility",
    "PreemptionCandidate",
    "PreemptionPlan",
    "PreemptionResult",
    "PreemptionFailure",

    # Pressure
    "ResourcePressure",
    "PressureLevel",
    "ResourcePressureObservation",
    "ResourcePressureDecision",

    # Reclamation
    "ReclamationRequest",
    "ReclamationCandidate",
    "ReclamationPlan",
    "ReclamationAction",
    "ReclamationResult",
    "ReclamationVerification",

    # Verification
    "VerificationStatus",
    "AccountingViolation",
    "CorruptedAccounting",
    "SplitBrainDetection",

    # Diagnostics
    "ResourceManagerDiagnostics",
    "ResourceReport",
    "EventLogSnapshot",

    # Shutdown Integration
    "ShutdownPhase",
    "ResourceManagerShutdownIntegration",

    # Phase 3.8.3 - Canonical Interfaces
    "InterfaceResourceId",
    "InterfaceResourceDomain",
    "InterfaceResourceState",
    "ResourceCapability",
    "ResourceCapabilities",
    "ResourceMetadata",
    "Resource",
    "ResourceHandle",
    "ResourceOwner",

    # Pooling
    "PoolResourceState",
    "PoolResourceEntry",
    "ResourcePoolConfig",
    "PoolAcquisitionResult",
    "ResourcePool",
    "PoolBackedResource",
    "ResourcePoolManager",

    # Monitoring
    "InterfaceHealthState",
    "HealthTransition",
    "HealthObservation",
    "HealthEvaluator",
    "InterfaceAllocationEvent",
    "AllocationRecord",
    "ResourceAccounting",
    "MetricPoint",
    "ResourceMetrics",
    "LogSeverity",
    "ResourceEvent",
    "ResourceLogger",
    "TraceSpan",
    "ResourceTracer",

    # Provider Architecture
    "ProviderType",
    "ProviderState",
    "ProviderIdentity",
    "ProviderConfig",
    "InterfaceResourceProvider",
    "CPUResource",
    "GPUDevice",
    "MemoryResource",
    "StorageDevice",
    "NetworkInterface",
    "CPUProvider",
    "GPUProvider",
    "MemoryProvider",
    "StorageProvider",
    "NetworkProvider",
    "ProviderRegistry",
]
