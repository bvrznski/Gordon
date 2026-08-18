# Adaptation Shared Module - Phase 7.25
# =====================================

"""
Shared contracts and utilities for the Adaptation Reasoning subsystem.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.descriptor import (
    AdaptationDescriptor,
    AdaptationMode,
    AdaptationState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.adaptation_set import (
    AdaptationSet,
    AdaptationCandidate,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.pipeline import (
    AdaptationPipeline,
    AdaptationStage,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.behavior import (
    BehaviorAdaptation,
    BehaviorManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.context import (
    ContextAdaptation,
    ContextManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.configuration import (
    ConfigurationRefinement,
    ConfigurationManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.integration import (
    AdaptationIntegration,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.evolution import (
    AdaptationEvolution,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.validation import (
    AdaptationValidation,
    ValidationResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.failure import (
    AdaptationFailure,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.governance import (
    AdaptationGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.health import (
    AdaptationHealth,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared.diagnostics import (
    AdaptationTrace,
    AdaptationDiagnostic,
)

__all__ = [
    # Descriptors
    "AdaptationDescriptor",
    "AdaptationMode",
    "AdaptationState",
    
    # Sets and Candidates
    "AdaptationSet",
    "AdaptationCandidate",
    
    # Pipeline
    "AdaptationPipeline",
    "AdaptationStage",
    
    # Behavior
    "BehaviorAdaptation",
    "BehaviorManagement",
    
    # Context
    "ContextAdaptation",
    "ContextManagement",
    
    # Configuration
    "ConfigurationRefinement",
    "ConfigurationManagement",
    
    # Integration
    "AdaptationIntegration",
    
    # Evolution
    "AdaptationEvolution",
    
    # Validation
    "AdaptationValidation",
    "ValidationResult",
    
    # Failure
    "AdaptationFailure",
    "FailureKind",
    
    # Governance
    "AdaptationGovernance",
    
    # Health
    "AdaptationHealth",
    
    # Diagnostics and Trace
    "AdaptationTrace",
    "AdaptationDiagnostic",
]