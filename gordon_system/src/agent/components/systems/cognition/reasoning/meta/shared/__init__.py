# Meta-Reasoning Shared Components - Phase 7.27
# ==============================================

"""
Shared components for the Meta-Reasoning subsystem.

This module provides canonical contracts, utilities, and infrastructure
for meta-reasoning in Gordon Cognitive Architecture.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.descriptor import (
    MetaReasoningDescriptor,
    MetaReasoningState,
    OrchestrationMode,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.reasoner_set import ReasonerSet

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.strategy_selection import (
    StrategySelection,
    StrategyKind,
    SelectionRationale,
    StrategyEvaluation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.orchestration import (
    ReasoningOrchestration,
    ExecutionGraph,
    ExecutionStep,
    SynchronizationPoint,
    OrchestrationPolicy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.resources import ReasoningResourceAllocation

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.monitoring import ReasoningMonitoring

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.adaptation import AdaptiveOrchestration, StrategyAdaptation

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.refinement import MetaReasoningRefinement

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.validation import (
    MetaReasoningValidation,
    ValidationStatus,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.failure import (
    MetaReasoningFailure,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.governance import (
    MetaReasoningGovernance,
    GovernanceFindings,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.health import (
    MetaReasoningHealth,
    HealthMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.diagnostics import MetaReasoningDiagnostics

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.pipeline import (
    MetaReasoningPipelineResult,
    MetaReasoningState as PipelineMetaState,
    ReasoningObservation,
    StrategySelectionResult,
    ReasoningRegulation,
    ReasonerCoordination,
    EscalationDecision,
    TerminationDecision,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.anti_patterns import (
    AntiPatternDetector,
    DetectedAntiPattern,
    AntiPatternCategory,
    AntiPatternSeverity,
    detect_implicit_strategy_selection,
    detect_hidden_coordination_dependencies,
    detect_unjustified_escalation,
    detect_arbitrary_termination,
    detect_validation_bypass,
    detect_governance_bypass,
    detect_provenance_loss,
    detect_deterministic_violation,
)

__all__ = [
    # Core descriptors
    "MetaReasoningDescriptor",
    "MetaReasoningState",
    "OrchestrationMode",
    
    # Reasoner management
    "ReasonerSet",
    
    # Strategy management  
    "StrategySelection",
    "StrategyKind",
    "SelectionRationale",
    "StrategyEvaluation",
    
    # Orchestration
    "ReasoningOrchestration",
    "ExecutionGraph",
    "ExecutionStep", 
    "SynchronizationPoint",
    "OrchestrationPolicy",
    
    # Resources
    "ReasoningResourceAllocation",
    
    # Monitoring
    "ReasoningMonitoring",
    
    # Adaptation
    "AdaptiveOrchestration",
    "StrategyAdaptation",
    
    # Refinement
    "MetaReasoningRefinement",
    
    # Validation
    "MetaReasoningValidation",
    "ValidationStatus",
    
    # Failure handling
    "MetaReasoningFailure", 
    "FailureKind",
    
    # Governance
    "MetaReasoningGovernance",
    "GovernanceFindings",
    
    # Health
    "MetaReasoningHealth",
    "HealthMetrics",
    
    # Diagnostics
    "MetaReasoningDiagnostics",
    
    # Pipeline contracts (Part 3)
    "MetaReasoningPipelineResult",
    "PipelineMetaState",
    "ReasoningObservation",
    "StrategySelectionResult",
    "ReasoningRegulation",
    "ReasonerCoordination",
    "EscalationDecision",
    "TerminationDecision",
    
    # Anti-pattern detection (Part 3)
    "AntiPatternDetector",
    "DetectedAntiPattern", 
    "AntiPatternCategory",
    "AntiPatternSeverity",
    "detect_implicit_strategy_selection",
    "detect_hidden_coordination_dependencies",
    "detect_unjustified_escalation",
    "detect_arbitrary_termination",
    "detect_validation_bypass",
    "detect_governance_bypass",
    "detect_provenance_loss",
    "detect_deterministic_violation",
]