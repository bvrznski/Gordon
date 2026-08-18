# Creative Reasoning Module - Phase 7.33
# =====================================

"""
Creative Reasoning provides Gordon with the capability for novelty generation,
concept synthesis, invention, exploration, and cognitive divergence.

This module implements:

- Creative Sessions: Containers for creative reasoning processes
- Concept Synthesis: Recombining knowledge into novel ideas
- Creative Exploration: Exploring alternative designs and strategies  
- Invention: Generating new mechanisms and architectures
- Divergence Management: Controlling search breadth and novelty pressure
- Validation: Observational evaluation of creative outputs
- Governance: Quality assessment without modifying artifacts

Creative Reasoning never directly modifies Gordon's knowledge base.
It generates novel ideas for evaluation and potential adoption by other modules.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.shared.descriptor import (
    CreativeDescriptor,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.shared.creative_set import (
    CreativeSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.synthesis.concept_synthesis import (
    ConceptSynthesis,
    SynthesisStrategy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.exploration.exploration import (
    CreativeExploration,
    ExplorationStrategy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.invention.invention import (
    CreativeInvention,
    InventionStrategy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.exploration.divergence import (
    CreativeDivergence,
    DivergencePolicy,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.observability.trace import (
    CreativeTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.validation.result import (
    CreativeValidationResult,
    ValidationOutcome,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.creative.governance.governance import (
    CreativeGovernance,
)

__all__ = [
    # Shared
    "CreativeDescriptor",
    "CreativeSet",
    # Synthesis
    "ConceptSynthesis",
    "SynthesisStrategy",
    # Exploration
    "CreativeExploration",
    "ExplorationStrategy",
    # Invention
    "CreativeInvention",
    "InventionStrategy",
    # Divergence
    "CreativeDivergence",
    "DivergencePolicy",
    # Trace/Observability
    "CreativeTrace",
    # Validation
    "CreativeValidationResult",
    "ValidationOutcome",
    # Governance
    "CreativeGovernance",
]