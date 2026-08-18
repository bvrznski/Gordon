# Negotiation Reasoning Shared Contracts - Phase 7.42
# =====================================================

"""
Shared contract types for the negotiation reasoning subsystem.

This module provides canonical implementations of all negotiation reasoning contracts:

    NegotiationDescriptor     - Metadata about negotiation sessions
    NegotiationSet            - Set of participating stakeholders and constraints
    NegotiationPipeline       - Pipeline from analysis to agreement
    StakeholderManagement     - Management of stakeholder models
    InterestManagement        - Management of interest analyses
    ConcessionManagement      - Management of concession analyses
    AgreementManagement       - Management of agreement construction
    CoalitionAnalysis         - Analysis of potential coalitions
    Mediation                 - Mediation services for negotiation
    NegotiationEvolution      - Evolution tracking for negotiations
    NegotiationValidation     - Validation results
    NegotiationFailure        - Failure records
    NegotiationGovernance     - Governance evaluation
    NegotiationHealth         - Health metrics
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.descriptor import (
    NegotiationDescriptor,
    NegotiationLifecycle,
    NegotiationMode,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.negotiation_set import (
    NegotiationSet,
    StakeholderReference,
    ConstraintDefinition,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.pipeline import (
    NegotiationPipeline,
    PipelineStage,
    NegotiationResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.stakeholders import (
    StakeholderModel,
    AuthorityLevel,
    TrustEstimate,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.interests import (
    InterestAnalysis,
    InterestKind,
    CompatibilityScore,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.concessions import (
    ConcessionAnalysis,
    ConcessionModel,
    ReservationLimit,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.agreements import (
    NegotiationAgreement,
    AcceptedTerm,
    RejectedTerm,
    Obligation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.coalitions import (
    CoalitionAnalysis,
    CoalitionStability,
    Membership,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.mediation import (
    Mediator,
    MediationStrategy,
    MediationOutcome,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.evolution import (
    NegotiationEvolution,
    EvolutionTrigger,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.validation import (
    NegotiationValidation,
    ValidationKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.failure import (
    NegotiationFailure,
    FailureKind,
    RecoveryOption,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.governance import (
    NegotiationGovernance,
    GovernanceFinding,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.negotiation.shared.health import (
    NegotiationHealth,
    HealthMetric,
)

__all__ = [
    # Descriptor
    "NegotiationDescriptor",
    "NegotiationLifecycle",
    "NegotiationMode",
    
    # Negotiation Set
    "NegotiationSet",
    "StakeholderReference",
    "ConstraintDefinition",
    
    # Pipeline
    "NegotiationPipeline",
    "PipelineStage",
    "NegotiationResult",
    
    # Stakeholders
    "StakeholderModel",
    "AuthorityLevel",
    "TrustEstimate",
    
    # Interests
    "InterestAnalysis",
    "InterestKind",
    "CompatibilityScore",
    
    # Concessions
    "ConcessionAnalysis",
    "ConcessionModel",
    "ReservationLimit",
    
    # Agreements
    "NegotiationAgreement",
    "AcceptedTerm",
    "RejectedTerm",
    "Obligation",
    
    # Coalitions
    "CoalitionAnalysis",
    "CoalitionStability",
    "Membership",
    
    # Mediation
    "Mediator",
    "MediationStrategy",
    "MediationOutcome",
    
    # Evolution
    "NegotiationEvolution",
    "EvolutionTrigger",
    
    # Validation
    "NegotiationValidation",
    "ValidationKind",
    
    # Failure
    "NegotiationFailure",
    "FailureKind",
    "RecoveryOption",
    
    # Governance
    "NegotiationGovernance",
    "GovernanceFinding",
    
    # Health
    "NegotiationHealth",
    "HealthMetric",
]