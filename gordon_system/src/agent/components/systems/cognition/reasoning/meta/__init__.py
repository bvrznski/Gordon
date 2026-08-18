# Meta-Reasoning - Phase 7.13
# ==============================

"""
Meta-Reasoning subsystem for Gordon Cognitive Architecture.

This module provides the reasoning operating system that coordinates all
specialized reasoning subsystems without replacing them.

Meta-Reasoning manages:
    - Reasoning strategy selection
    - Reasoning orchestration  
    - Reasoning monitoring
    - Reasoning evaluation
    - Reasoning adaptation
    - Reasoning composition
    - Reasoning optimization
    - Compute allocation
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.descriptor import MetaReasoningDescriptor
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.reasoner_set import ReasonerSet
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.strategy_selection import StrategySelection
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.orchestration import ReasoningOrchestration
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.resources import ReasoningResourceAllocation
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.monitoring import ReasoningMonitoring
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.adaptation import AdaptiveOrchestration, StrategyAdaptation
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.refinement import MetaReasoningRefinement
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.validation import MetaReasoningValidation, ValidationStatus
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.failure import MetaReasoningFailure, FailureKind
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.governance import MetaReasoningGovernance, GovernanceFindings
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.health import MetaReasoningHealth, HealthMetrics
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.diagnostics import MetaReasoningDiagnostics
from gordon_system.src.agent.components.systems.cognition.reasoning.meta.shared.pipeline import (
    MetaReasoningPipelineResult,
    MetaReasoningState,  # Canonical state enum from Part 3
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
    "MetaReasoningDescriptor",
    "ReasonerSet",
    "StrategySelection",
    
    # Pipeline contracts (Part 3)
    "MetaReasoningPipelineResult",
    "MetaReasoningState",  # Canonical state enum from Part 3 pipeline module
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
    
    "ReasoningOrchestration",
    "ReasoningResourceAllocation",
    "ReasoningMonitoring",
    "AdaptiveOrchestration",
    "StrategyAdaptation",
    "MetaReasoningRefinement",
    "MetaReasoningValidation",
    "ValidationStatus",
    "MetaReasoningFailure",
    "FailureKind",
    "MetaReasoningGovernance",
    "GovernanceFindings",
    "MetaReasoningHealth",
    "HealthMetrics",
    "MetaReasoningDiagnostics",
]