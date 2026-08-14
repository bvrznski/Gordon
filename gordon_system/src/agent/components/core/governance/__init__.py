# Core Runtime Governance, Autonomy & Operational Control Architecture
# ====================================================================

"""
Canonical Runtime Governance Architecture for the Gordon Core.

This module provides the complete runtime governance framework:

- Runtime Governance: Continuous supervision and control of runtime behavior
- Operational Control: Authority, arbitration, intervention, and adaptation
- Governance Domains: Specialized governance areas (resource, execution, lifecycle, etc.)
- Policy Enforcement: Declarative policy evaluation and enforcement
- Decision Making: Governance decisions with evidence and audit trails

Governance Philosophy:
- Governance supervises but never replaces subsystem implementations
- Every runtime decision is governed, constrained, observable, auditable, explainable
- Runtime continuously determines: what, why, should, compliance, violations, intervention needs
- Governance exists above execution but below cognition

Architectural Separation:
- Governance: Supervision and control (this module)
- Execution: Performing operations (execution module)
- Planning: Making decisions (planning module)
- Policy: Declarative constraints (policy module)

No subsystem shall implement independent governance frameworks.
One canonical Runtime Governance Architecture shall exist throughout the repository.
"""

from .foundations import (
    GovernancePhilosophy,
    OperationalPhilosophy,
    SupervisionPhilosophy,
    GovernanceTerminology,
    GovernanceArchitectureBoundaries,
    GovernanceOwnership,
    GovernanceInvariants,
    GovernanceLifecycle,
)

from .domains import (
    RuntimeGovernanceDomain,
    ResourceGovernanceDomain,
    ExecutionGovernanceDomain,
    LifecycleGovernanceDomain,
    ConfigurationGovernanceDomain,
    SecurityGovernanceDomain,
    CommunicationGovernanceDomain,
    PersistenceGovernanceDomain,
    RecoveryGovernanceDomain,
    DeploymentGovernanceDomain,
    CapabilityGovernanceDomain,
    ServiceGovernanceDomain,
)

from .objectives import (
    OperationalObjective,
    AvailabilityObjective,
    PerformanceObjective,
    ReliabilityObjective,
    SafetyObjective,
    ResourceObjective,
    SchedulingObjective,
    ExecutionObjective,
    RecoveryObjective,
    DeploymentObjective,
)

from .constraints import (
    RuntimeConstraint,
    ResourceLimitConstraint,
    ExecutionLimitConstraint,
    SchedulingLimitConstraint,
    ConcurrencyLimitConstraint,
    CommunicationLimitConstraint,
    PersistenceLimitConstraint,
    LifecycleLimitConstraint,
    DeploymentLimitConstraint,
    PolicyLimitConstraint,
    ConstraintViolation,
    ConstraintEvaluator,
)

from .policies import (
    GovernancePolicy,
    OperationalPolicy,
    AdmissionPolicy,
    ExecutionPolicy,
    RecoveryPolicy,
    DegradationPolicy,
    InterventionPolicy,
    EscalationPolicy,
    OptimizationPolicy,
    MaintenancePolicy,
    PolicyEnforcementResult,
    PolicyEvaluationContext,
)

from .supervision import (
    RuntimeSupervisor,
    ServiceSupervisor,
    CapabilitySupervisor,
    SchedulerSupervisor,
    ExecutionSupervisor,
    ResourceSupervisor,
    CommunicationSupervisor,
    PersistenceSupervisor,
    RecoverySupervisor,
    LifecycleSupervisor,
    SupervisionResult,
    SupervisionEvent,
)

from .authority import (
    GovernanceAuthority,
    OperationalAuthority,
    SupervisoryAuthority,
    InterventionAuthority,
    RecoveryAuthority,
    EscalationAuthority,
    ShutdownAuthority,
    AuthorityChain,
    AuthorityGrant,
)

from .arbitration import (
    RuntimeArbitrator,
    ResourceConflictResolver,
    SchedulingConflictResolver,
    ExecutionConflictResolver,
    LifecycleConflictResolver,
    DeploymentConflictResolver,
    CommunicationConflictResolver,
    PolicyConflictResolver,
    ArbitrationDecision,
)

from .intervention import (
    InterventionStrategy,
    ExecutionSuspension,
    ExecutionTermination,
    CapabilityDisablement,
    ResourceThrottling,
    CommunicationRestriction,
    RuntimeQuarantine,
    EmergencyStop,
    GracefulIntervention,
    InterventionResult,
)

from .modes import (
    OperationalMode,
    NormalMode,
    SafeMode,
    RecoveryMode,
    MaintenanceMode,
    DiagnosticMode,
    SimulationMode,
    OfflineMode,
    EmergencyMode,
    MinimalMode,
    ModeTransition,
)

from .adaptation import (
    RuntimeAdaptor,
    WorkloadAdaptationPolicy,
    ResourceAdaptationPolicy,
    SchedulingAdaptationPolicy,
    DeploymentAdaptationPolicy,
    RecoveryAdaptationPolicy,
    OperationalAdaptationPolicy,
    AdaptationDecision,
)

from .decisions import (
    GovernanceDecision,
    ApprovalDecision,
    RejectionDecision,
    PostponementDecision,
    EscalationDecision,
    InterventionDecision,
    OptimizationDecision,
    RecoveryInitiationDecision,
    DegradationApprovalDecision,
    DecisionEvidence,
)

from .coordination import (
    LifecycleCoordinator,
    ExecutionCoordinator,
    SchedulingCoordinator,
    RecoveryCoordinator,
    CommunicationCoordinator,
    PersistenceCoordinator,
    SecurityCoordinator,
    ObservabilityCoordinator,
    GovernanceCoordinator,
)

from .diagnostics import (
    GovernanceTimeline,
    PolicyEvaluationHistory,
    InterventionHistory,
    OperationalDecisionHistory,
    ArbitrationHistory,
    AdaptationHistory,
    AuthorityDecisionHistory,
    GovernanceMetrics,
)

from .integrity import (
    GovernanceValidator,
    PolicyValidator,
    AuthorityChainValidator,
    InterventionValidator,
    ObjectiveValidator,
    AdaptationValidator,
    ArbitrationValidator,
    ConsistencyChecker,
)

from .governance_engine import (
    RuntimeGovernanceEngine,
    GovernanceSession,
    GovernanceReport,
    EvidenceStorage,
)

__all__ = [
    # Foundations
    "GovernancePhilosophy",
    "OperationalPhilosophy",
    "SupervisionPhilosophy",
    "GovernanceTerminology",
    "GovernanceArchitectureBoundaries",
    "GovernanceOwnership",
    "GovernanceInvariants",
    "GovernanceLifecycle",
    # Domains
    "RuntimeGovernanceDomain",
    "ResourceGovernanceDomain",
    "ExecutionGovernanceDomain",
    "LifecycleGovernanceDomain",
    "ConfigurationGovernanceDomain",
    "SecurityGovernanceDomain",
    "CommunicationGovernanceDomain",
    "PersistenceGovernanceDomain",
    "RecoveryGovernanceDomain",
    "DeploymentGovernanceDomain",
    "CapabilityGovernanceDomain",
    "ServiceGovernanceDomain",
    # Objectives
    "OperationalObjective",
    "AvailabilityObjective",
    "PerformanceObjective",
    "ReliabilityObjective",
    "SafetyObjective",
    "ResourceObjective",
    "SchedulingObjective",
    "ExecutionObjective",
    "RecoveryObjective",
    "DeploymentObjective",
    # Constraints
    "RuntimeConstraint",
    "ResourceLimitConstraint",
    "ExecutionLimitConstraint",
    "SchedulingLimitConstraint",
    "ConcurrencyLimitConstraint",
    "CommunicationLimitConstraint",
    "PersistenceLimitConstraint",
    "LifecycleLimitConstraint",
    "DeploymentLimitConstraint",
    "PolicyLimitConstraint",
    "ConstraintViolation",
    "ConstraintEvaluator",
    # Policies
    "GovernancePolicy",
    "OperationalPolicy",
    "AdmissionPolicy",
    "ExecutionPolicy",
    "RecoveryPolicy",
    "DegradationPolicy",
    "InterventionPolicy",
    "EscalationPolicy",
    "OptimizationPolicy",
    "MaintenancePolicy",
    "PolicyEnforcementResult",
    "PolicyEvaluationContext",
    # Supervision
    "RuntimeSupervisor",
    "ServiceSupervisor",
    "CapabilitySupervisor",
    "SchedulerSupervisor",
    "ExecutionSupervisor",
    "ResourceSupervisor",
    "CommunicationSupervisor",
    "PersistenceSupervisor",
    "RecoverySupervisor",
    "LifecycleSupervisor",
    "SupervisionResult",
    "SupervisionEvent",
    # Authority
    "GovernanceAuthority",
    "OperationalAuthority",
    "SupervisoryAuthority",
    "InterventionAuthority",
    "RecoveryAuthority",
    "EscalationAuthority",
    "ShutdownAuthority",
    "AuthorityChain",
    "AuthorityGrant",
    # Arbitration
    "RuntimeArbitrator",
    "ResourceConflictResolver",
    "SchedulingConflictResolver",
    "ExecutionConflictResolver",
    "LifecycleConflictResolver",
    "DeploymentConflictResolver",
    "CommunicationConflictResolver",
    "PolicyConflictResolver",
    "ArbitrationDecision",
    # Intervention
    "InterventionStrategy",
    "ExecutionSuspension",
    "ExecutionTermination",
    "CapabilityDisablement",
    "ResourceThrottling",
    "CommunicationRestriction",
    "RuntimeQuarantine",
    "EmergencyStop",
    "GracefulIntervention",
    "InterventionResult",
    # Modes
    "OperationalMode",
    "NormalMode",
    "SafeMode",
    "RecoveryMode",
    "MaintenanceMode",
    "DiagnosticMode",
    "SimulationMode",
    "OfflineMode",
    "EmergencyMode",
    "MinimalMode",
    "ModeTransition",
    # Adaptation
    "RuntimeAdaptor",
    "WorkloadAdaptationPolicy",
    "ResourceAdaptationPolicy",
    "SchedulingAdaptationPolicy",
    "DeploymentAdaptationPolicy",
    "RecoveryAdaptationPolicy",
    "OperationalAdaptationPolicy",
    "AdaptationDecision",
    # Decisions
    "GovernanceDecision",
    "ApprovalDecision",
    "RejectionDecision",
    "PostponementDecision",
    "EscalationDecision",
    "InterventionDecision",
    "OptimizationDecision",
    "RecoveryInitiationDecision",
    "DegradationApprovalDecision",
    "DecisionEvidence",
    # Coordination
    "LifecycleCoordinator",
    "ExecutionCoordinator",
    "SchedulingCoordinator",
    "RecoveryCoordinator",
    "CommunicationCoordinator",
    "PersistenceCoordinator",
    "SecurityCoordinator",
    "ObservabilityCoordinator",
    "GovernanceCoordinator",
    # Diagnostics
    "GovernanceTimeline",
    "PolicyEvaluationHistory",
    "InterventionHistory",
    "OperationalDecisionHistory",
    "ArbitrationHistory",
    "AdaptationHistory",
    "AuthorityDecisionHistory",
    "GovernanceMetrics",
    # Integrity
    "GovernanceValidator",
    "PolicyValidator",
    "AuthorityChainValidator",
    "InterventionValidator",
    "ObjectiveValidator",
    "AdaptationValidator",
    "ArbitrationValidator",
    "ConsistencyChecker",
    # Engine
    "RuntimeGovernanceEngine",
    "GovernanceSession",
    "GovernanceReport",
    "EvidenceStorage",
]