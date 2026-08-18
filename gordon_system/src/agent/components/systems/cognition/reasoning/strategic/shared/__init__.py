# Strategic Reasoning Shared Contracts - Phase 7.18
# ================================================

"""
Shared contract types for the strategic reasoning subsystem.

This module provides canonical implementations of all strategic reasoning contracts:
    StrategicDescriptor     - Metadata about strategic operations
    Objective               - Individual objective definition
    ObjectiveSet            - Set of objectives with constraints and priorities
    StrategyFormation       - Result of strategy formation pipeline
    StrategicPolicy         - Behavioral policy definition
    PolicyConstruction      - Constructed policy set
    StrategicTradeoff       - Trade-off analysis result
    TradeoffAnalysis        - Comprehensive trade-off evaluation
    ObjectivePrioritization - Prioritized objective order
    StrategicAdaptation     - Strategy adaptation record
    StrategicEvolution      - Evolution history of a strategy
    StrategicValidation     - Validation results
    StrategicFailure        - Failure record with diagnostics
    StrategicGovernance     - Governance evaluation
    StrategicHealth         - Health metrics
    StrategicDiagnostics    - Diagnostic information

Phase 7.37 Part 2 additions:
    MissionManagement       - Mission analysis and management
    ResourceManagement      - Resource allocation and tracking
    OpportunityManagement   - Opportunity assessment and tracking  
    PortfolioManagement     - Portfolio construction and balance
    Pipeline                - Canonical strategic reasoning pipeline
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.descriptor import (
    StrategicDescriptor,
    StrategicState,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.objective_set import (
    Objective,
    ObjectiveSet,
    ObjectivePrioritization,
    ObjectivePriority,
    ObjectiveConstraintType,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.mission import (
    MissionIdentity,
    MissionObjective,
    MissionConstraint,
    MissionDependency,
    MissionAnalysis,
    MissionEvolution,
    MissionModel,
    MissionManagement,
    MissionPortfolioAlignment,
    MissionState,
    MissionQuality,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.resources import (
    ResourceIdentity,
    ResourceCapacity,
    ResourceAllocation,
    ResourceAnalysis,
    ResourceEvolution,
    ResourceModel,
    ResourceManagement,
    ResourcePortfolio,
    ResourceType,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.opportunities import (
    OpportunityIdentity,
    OpportunityAssessment,
    OpportunityConstraint,
    OpportunityRisk,
    OpportunityAnalysis,
    OpportunityEvolution,
    OpportunityModel,
    OpportunityManagement,
    OpportunityPortfolio,
    OpportunityType,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.portfolios import (
    PortfolioIdentity,
    StrategicProject,
    PortfolioConstraint,
    PortfolioAnalysis,
    PortfolioEvolution,
    PortfolioModel,
    PortfolioManagement,
    PortfolioResourceAllocation,
    PortfolioBalanceMetrics,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.pipeline import (
    PipelineStage,
    PipelineIdentity,
    PipelineResult,
    StrategicPipeline,
    PipelineMetrics,
    PipelineContext,
    PipelineObservability,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.formation import (
    StrategyFormation,
    StrategyFormationFailure,
    StrategyFormationProgress,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.policies import (
    StrategicPolicy,
    PolicyConstruction,
    PolicyConflict,
    PolicyAdaptation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.tradeoffs import (
    StrategicTradeoff,
    TradeoffAnalysis,
    TradeoffMetrics,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.prioritization import (
    ObjectivePrioritization as PrioritizationResult,
    PrioritizationFailure,
    PrioritizationMetrics,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.adaptation import (
    StrategicAdaptation,
    StrategicAdaptationPipeline,
    AdaptationFailure,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.evolution import (
    StrategicEvolution,
    EvolutionStep,
    EvolutionFailure,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.validation import (
    StrategicValidation,
    ValidationFailure,
    ValidationTrace,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.failure import (
    StrategicFailure,
    FailureCategory,
    FailureRecoveryPlan,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.governance import (
    StrategicGovernance,
    GovernanceFinding,
    GovernanceReport,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.health import (
    StrategicHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.strategic.shared.diagnostics import (
    StrategicDiagnostics,
    DiagnosticEvent,
    DiagnosticTrace,
)

__all__ = [
    # Descriptor
    "StrategicDescriptor",
    "StrategicState",
    
    # Objective Set
    "Objective",
    "ObjectiveSet",
    "ObjectivePrioritization",
    "ObjectivePriority",
    "ObjectiveConstraintType",
    
    # Mission (Phase 7.37 Part 2)
    "MissionIdentity",
    "MissionObjective",
    "MissionConstraint",
    "MissionDependency",
    "MissionAnalysis",
    "MissionEvolution",
    "MissionModel",
    "MissionManagement",
    "MissionPortfolioAlignment",
    "MissionState",
    "MissionQuality",
    
    # Resources (Phase 7.37 Part 2)
    "ResourceIdentity",
    "ResourceCapacity",
    "ResourceAllocation",
    "ResourceAnalysis",
    "ResourceEvolution",
    "ResourceModel",
    "ResourceManagement",
    "ResourcePortfolio",
    "ResourceType",
    
    # Opportunities (Phase 7.37 Part 2)
    "OpportunityIdentity",
    "OpportunityAssessment",
    "OpportunityConstraint",
    "OpportunityRisk",
    "OpportunityAnalysis",
    "OpportunityEvolution",
    "OpportunityModel",
    "OpportunityManagement",
    "OpportunityPortfolio",
    "OpportunityType",
    
    # Portfolios (Phase 7.37 Part 2)
    "PortfolioIdentity",
    "StrategicProject",
    "PortfolioConstraint",
    "PortfolioAnalysis",
    "PortfolioEvolution",
    "PortfolioModel",
    "PortfolioManagement",
    "PortfolioResourceAllocation",
    "PortfolioBalanceMetrics",
    
    # Pipeline (Phase 7.37 Part 2)
    "PipelineStage",
    "PipelineIdentity",
    "PipelineResult",
    "StrategicPipeline",
    "PipelineMetrics",
    "PipelineContext",
    "PipelineObservability",
    
    # Strategy Formation
    "StrategyFormation",
    "StrategyFormationFailure",
    "StrategyFormationProgress",
    
    # Policies
    "StrategicPolicy",
    "PolicyConstruction",
    "PolicyConflict",
    "PolicyAdaptation",
    
    # Trade-offs
    "StrategicTradeoff",
    "TradeoffAnalysis",
    "TradeoffMetrics",
    
    # Prioritization
    "PrioritizationResult",
    "PrioritizationFailure",
    "PrioritizationMetrics",
    
    # Adaptation
    "StrategicAdaptation",
    "StrategicAdaptationPipeline",
    "AdaptationFailure",
    
    # Evolution
    "StrategicEvolution",
    "EvolutionStep",
    "EvolutionFailure",
    
    # Validation
    "StrategicValidation",
    "ValidationFailure",
    "ValidationTrace",
    
    # Failure
    "StrategicFailure",
    "FailureCategory",
    "FailureRecoveryPlan",
    
    # Governance
    "StrategicGovernance",
    "GovernanceFinding",
    "GovernanceReport",
    
    # Health
    "StrategicHealth",
    "HealthMetricsSnapshot",
    "HealthAlert",
    
    # Diagnostics
    "StrategicDiagnostics",
    "DiagnosticEvent",
    "DiagnosticTrace",
]