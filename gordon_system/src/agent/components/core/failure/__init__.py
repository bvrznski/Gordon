# Core Failure Recovery Architecture - Phase 3.14.14
# ===================================================

"""
Core failure recovery architecture for Gordon agent.

This package provides:
- Immutable failure artifacts with deterministic serialization  
- Canonical failure taxonomy and lifecycle
- Propagation, containment, escalation semantics
- Recovery architecture with rollback and degradation policies
- Observability contracts for audit and replay

PHASE 3.14.14 - FAILURE PROPAGATION & RECOVERY ARCHITECTURE
============================================================

The canonical failure model established in this phase:

    Execution
            |
            V
    Failure Detection
            |
            V
    Classification  
            |
            V
    Containment
            |
            V
    Propagation
            |
            V
    Recovery
            |
            V
    Certification

Key Principles:
- Failures are first-class architectural events
- Failures shall never be hidden or silently propagated  
- Recovery shall be deterministic and preserve integrity
- Ownership boundaries shall never be violated during failure handling

FAILURE TAXONOMY (Canonical)
============================
    
- VALIDATION: Input or constraint validation failed
- ADMISSION: Request not admitted by authority boundary  
- SCHEDULING: Scheduling decision could not be made
- EXECUTION: Execution operation encountered error
- STREAM: Stream transport encountered error
- INTERACTION: Interaction contract violated
- NETWORK: Network connectivity or protocol failure
- CAPABILITY: Capability invocation failed
- SYSTEM: System state management failure
- RESOURCE: Resource allocation or access failure
- DEPENDENCY: External dependency unavailable or failed
- SECURITY: Security policy violation detected
- PRIVACY: Privacy constraint violation detected
- INTEGRITY: Data or state integrity violation detected
- TIMEOUT: Operation exceeded time budget
- CANCELLATION: Operation was cancelled (graceful)
- RECOVERY: Recovery operation itself failed

FAILURE LIFECYCLE
=================

Detected -> Classified -> Contained -> Propagated -> Recovered -> Verified -> Closed

Alternative terminal states:
    - Escalated
    - Aborted  
    - Unrecoverable

SEVERITY LEVELS
===============

- INFO: Informational event, no action needed
- NOTICE: Notable event, may need attention
- WARNING: Potential problem, monitor closely
- RECOVERABLE: Can be recovered with effort
- SERIOUS: Significant impact requiring escalation
- CRITICAL: Major system impact, immediate action required
- FATAL: Terminal condition, no recovery possible

RECOVERY STRATEGIES
===================

- RETRY: Attempt operation again
- ROLLBACK: Restore to previous verified state
- RESTART: Restart component or service
- REINITIALIZE: Reinitialize without full restart
- DEGRADE: Accept degraded operational mode
- FAILOVER: Switch to backup system
- RESTORE_CHECKPOINT: Restore from verified checkpoint
- COMPENSATING: Execute compensating transaction
- GRACEFUL_SHUTDOWN: Perform graceful shutdown
- TERMINATE: Force termination of failing component

OWNERSHIP & AUTHORITY
=====================

Each architectural component owns recovery within its responsibility:
    - Execution owns execution recovery
    - Streams own transport recovery  
    - Networks own network recovery
    - Capabilities own computation recovery
    - Systems own state recovery

Ownership shall never migrate during failure handling.
Recovery shall never grant additional authority.

This module re-exports the canonical Failure Propagation & Recovery
architecture while maintaining backward compatibility with existing types.
"""

from .classifier import FailureClassifier, FailureClassificationResult
from .coordinator import FailureCoordinator
from .containment import (
    ContainmentRequest,
    ContainmentPlan,
    ContainmentAction,
    ContainmentBarrier,
    ContainmentResult,
)
from .domains import (
    FailureDomain,
    DomainHierarchy,
    ContainmentBoundary,
    TransitionDirection,
    Transition,
    DomainRecoveryCapabilities,
    get_domain_hierarchy,
    get_parent_domain,
    get_ancestor_chain,
    get_containment_boundaries,
    get_recovery_capabilities,
    determine_propagation_path,
    find_common_ancestor,
    domains_are_siblings,
    calculate_propagation_delay,
)
from .events import (
    RuntimeFailureEvent,
    FailureDetectedEvent,
    FailureClassifiedEvent,
    FailureContainedEvent,
    RollbackRequestedEvent,
    RecoveryStartedEvent,
    RecoverySucceededEvent,
    RecoveryFailedEvent,
)
from .propagation import (
    PropagationEvent,
    PropagationPath,
    PropagationAnalysis,
    ContainmentBoundaryInfo,
    PropagationPathBuilder,
    PropagationResult,
    PropagationSimulator,
    find_propagation_path,
    get_containment_points_for_failure,
    predict_failure_scope,
    get_propagation_delay_matrix,
)
from .types import (
    FailureKind,
    RuntimeFailure,
)
from .verification import (
    VerificationResult,
    RecoveryVerificationResult,
    RollbackVerificationResult,
    VerificationStatus,
    VerificationType,
    StateSnapshot,
    EntityState,
    EntityStatus,
    RecoveryVerifier,
    RollbackVerifier,
    StateComparisonEngine,
    StabilityWindow,
    StabilityWindowValidator,
    IndependentVerificationCoordinator,
    FaultInjectionVerifier,
    verify_state_version_compatibility,
    calculate_verification_confidence,
    get_verification_summary,
)
from .reconciliation import (
    ReconciliationResult,
    ReconciliationAction,
    ReconciliationType,
    StateSource,
    SystemStateObserver,
    ReconciliationRequest,
    ExternalStateReconciler,
    DriftReport,
    DriftType,
    DriftDetector,
    determine_reconciliation_priority,
    format_reconciliation_summary,
)
from .compensation import (
    CompensationContract,
    CompensationAction,
    CompensationType,
    RetryPolicy,
    Condition,
    ConditionType,
    StateRestoreContract,
    FailureAction,
    CompensatingTransaction,
    TransactionAction,
    CompensationCoordinator,
    build_compensating_transaction,
    validate_compensation_plan,
)
from .architecture import (
    # Enums (Canonical)
    FailureCategory,
    FailureSeverity,
    FailureLifecycleState,
    FailurePropagationPath,
    RecoveryStrategy,
    FailureOrigin,
    
    # Core types
    FailureArtifact,
    FailureClassifier,  # Canonical classifier (already named correctly)
    FailureContainer,
    FailurePropagator,
    FailureContainmentScope,
    
    # Policy and planning
    EscalationPolicy,
    RecoveryPlanner,
    RecoveryCoordinator,  # Canonical coordinator
    
    # Observability  
    FailureObservabilityData,
)

__all__ = [
    # ========== CANONICAL FAILURE ARCHITECTURE (Phase 3.14.14) ==========
    
    # Enums
    "FailureCategory",
    "FailureSeverity",
    "FailureLifecycleState", 
    "FailurePropagationPath",
    "RecoveryStrategy",
    "FailureOrigin",
    
    # Core types
    "FailureArtifact",
    "FailureClassifier",
    "FailureContainer",
    "FailurePropagator",
    "FailureContainmentScope",
    
    # Policy and planning
    "EscalationPolicy",
    "RecoveryPlanner",
    "RecoveryCoordinator",
    
    # Observability
    "FailureObservabilityData",
    
    # ========== LEGACY TYPES (Backward Compatibility) ==========
    
    # Types from types.py
    "FailureKind",
    "RuntimeFailure",
    
    # Classification
    "FailureClassificationResult",
    
    # Coordination (legacy)
    "FailureCoordinator",
    
    # Containment
    "ContainmentRequest", 
    "ContainmentPlan",
    "ContainmentAction",
    "ContainmentBarrier",
    "ContainmentResult",
    
    # Domains  
    "FailureDomain",
    "DomainHierarchy",
    "ContainmentBoundary",
    "TransitionDirection",
    "Transition",
    "DomainRecoveryCapabilities",
    "get_domain_hierarchy",
    "get_parent_domain",
    "get_ancestor_chain",
    "get_containment_boundaries",
    "get_recovery_capabilities",
    "determine_propagation_path",
    "find_common_ancestor",
    "domains_are_siblings",
    "calculate_propagation_delay",
    
    # Propagation
    "PropagationEvent",
    "PropagationPath", 
    "PropagationAnalysis",
    "ContainmentBoundaryInfo",
    "PropagationPathBuilder",
    "PropagationResult",
    "PropagationSimulator",
    "find_propagation_path",
    "get_containment_points_for_failure",
    "predict_failure_scope",
    "get_propagation_delay_matrix",
    
    # Events
    "RuntimeFailureEvent",
    "FailureDetectedEvent",
    "FailureClassifiedEvent",
    "FailureContainedEvent",
    "RollbackRequestedEvent", 
    "RecoveryStartedEvent",
    "RecoverySucceededEvent",
    "RecoveryFailedEvent",
    
    # Verification
    "VerificationResult",
    "RecoveryVerificationResult",
    "RollbackVerificationResult",
    "VerificationStatus",
    "VerificationType",
    "StateSnapshot",
    "EntityState",
    "EntityStatus",
    "RecoveryVerifier",
    "RollbackVerifier",
    "StateComparisonEngine",
    "StabilityWindow",
    "StabilityWindowValidator",
    "IndependentVerificationCoordinator",
    "FaultInjectionVerifier",
    
    # Reconciliation
    "ReconciliationResult",
    "ReconciliationAction",
    "ReconciliationType",
    "StateSource",
    "SystemStateObserver",
    "ReconciliationRequest", 
    "ExternalStateReconciler",
    "DriftReport",
    "DriftType",
    "DriftDetector",
    "determine_reconciliation_priority",
    "format_reconciliation_summary",
    
    # Compensation contracts
    "CompensationContract",
    "CompensationAction",
    "CompensationType",
    "RetryPolicy",
    "Condition",
    "ConditionType",
    "StateRestoreContract",
    "FailureAction",
    "CompensatingTransaction",
    "TransactionAction",
    "CompensationCoordinator",
    "build_compensating_transaction",
    "validate_compensation_plan",
]