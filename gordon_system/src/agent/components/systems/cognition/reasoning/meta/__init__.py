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

__all__ = [
    "MetaReasoningDescriptor",
    "ReasonerSet",
    "StrategySelection", 
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