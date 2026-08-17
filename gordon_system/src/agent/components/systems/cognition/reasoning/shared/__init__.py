# Reasoning Shared Contracts - Phase 7.0
# =======================================

"""
Shared contract types for the reasoning subsystem.

This module provides canonical implementations of all reasoning contracts:

    Descriptor       - Metadata about reasoning operations
    Inference        - Deriving conclusions from knowledge
    Hypothesis       - Candidate explanations under evaluation
    Alternatives     - Candidate solutions under consideration
    Deliberation     - Comparing and selecting alternatives
    Conclusion       - Summarizing reasoning results
    Pipeline         - Complete reasoning execution flow
    Validation       - Evaluating reasoning without modification
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.descriptor import (
    ReasoningDescriptor,
    ReasoningKind,
    ReasoningState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.inference import (
    Inference,
    InferenceTrace,
    InferenceStrategy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.hypothesis import (
    ReasoningHypothesis,
    HypothesisEvaluation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.alternatives import (
    ReasoningAlternative,
    AlternativeComparison,
    AlternativeRanking,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.deliberation import (
    Deliberation,
    DeliberationPipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.conclusion import (
    ReasoningConclusion,
    ConclusionTrace,
    ConclusionEvaluation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.pipeline import (
    ReasoningPipeline,
    ReasoningSession,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.shared.validation import (
    ReasoningValidation,
    ReasoningFailure,
    ReasoningGovernance,
)

__all__ = [
    # Descriptor
    "ReasoningDescriptor",
    "ReasoningKind", 
    "ReasoningState",
    
    # Inference
    "Inference",
    "InferenceTrace",
    "InferenceStrategy",
    
    # Hypothesis
    "ReasoningHypothesis",
    "HypothesisEvaluation",
    
    # Alternatives
    "ReasoningAlternative",
    "AlternativeComparison",
    "AlternativeRanking",
    
    # Deliberation
    "Deliberation",
    "DeliberationPipeline",
    
    # Conclusion
    "ReasoningConclusion",
    "ConclusionTrace",
    "ConclusionEvaluation",
    
    # Pipeline
    "ReasoningPipeline",
    "ReasoningSession",
    
    # Validation
    "ReasoningValidation",
    "ReasoningFailure",
    "ReasoningGovernance",
]