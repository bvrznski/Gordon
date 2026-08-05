# Core Failure Recovery Architecture
# ===================================

"""
Core failure recovery architecture for Gordon agent.

This package provides:
- Immutable failure artifacts with deterministic serialization
- Failure taxonomy (kinds, severities, domains, dispositions)
- Failure detection adapters and classifiers
- Canonical authorities: FailureCoordinator, RollbackCoordinator, RecoveryCoordinator
- Containment, rollback, retry, restart protocols
- Independent verification for recovery/rollback
- Propagation analysis and containment boundaries

The architecture enforces:

1. ONE canonical authority per responsibility:
   - FailureCoordinator: failure intake, classification, containment
   - RollbackCoordinator: global rollback planning and coordination  
   - RecoveryCoordinator: global recovery planning and execution

2. FAILURE state remains truthful throughout handling:
   - No silent swallowing of failures
   - No optimistic recovery without verification
   - No unknown integrity reported as healthy

3. Recovery is a governed runtime protocol:
   - Not random retries or exception swallowing
   - Bounded budgets with backoff strategies
   - Independent verification before declaring success

4. Generations are fenced to prevent split-brain:
   - One authoritative generation per managed entity
   - Stale generations rejected automatically

5. Rollback and recovery require independent verification:
   - Component execution does not declare success alone
   - Target state must be verified by separate verifier

6. Propagation analysis for failure impact assessment:
   - Domain hierarchy with containment boundaries
   - Propagation path prediction
   - Stability window validation
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
    FailureSeverity,
    FailureDisposition,
    RollbackMode,
    RollbackScope,
    RecoveryPolicy,
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

# RecoveryCoordinator is the canonical authority from recovery_v2 package
from ..recovery_v2.coordinator import RecoveryCoordinator

__all__ = [
    # Types
    "FailureKind",
    "FailureSeverity", 
    "FailureDisposition",
    "RollbackMode",
    "RollbackScope",
    "RecoveryPolicy",
    "RuntimeFailure",
    
    # Classification
    "FailureClassifier",
    "FailureClassificationResult",
    
    # Coordination (canonical authorities)
    "FailureCoordinator",
    "RecoveryCoordinator",
    
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
    
    # Verification (independent verification layer)
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