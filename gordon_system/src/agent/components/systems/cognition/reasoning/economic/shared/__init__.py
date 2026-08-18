# Economic Reasoning Shared Contracts - Phase 7.48
# ===============================================

"""
Shared contracts for Economic Reasoning.

This package provides canonical data structures for:
    * economic sessions and reasoning descriptors
    * economic sets (resources, agents, constraints)
    * pipeline stages and results
    * resource management
    * valuation management
    * allocation management
    * incentive management
    * markets and pricing
    * optimization
    * validation
    * governance
    * observability

Economic Reasoning determines how Gordon allocates scarce resources to maximize
long-term value while respecting explicit constraints.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.descriptor import (
    EconomicSessionDescriptor,
    EconomicReasoningKind,
    EconomicLifecycleState,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.economic_set import (
    EconomicSet,
    EconomicSetKind,
    ResourceEntry,
    AgentEntry,
    AllocationConstraint,
    UtilityFunction,
    MarketAssumptions,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.pipeline import (
    EconomicPipeline,
    PipelineStage,
    PipelineStageResult,
)

# Import remaining shared contracts
from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.resources import (
    ResourceAnalysis,
    ResourceAssessment,
    ResourceInventory,
)

__all__ = [
    # Descriptors and lifecycle
    "EconomicSessionDescriptor",
    "EconomicReasoningKind",
    "EconomicLifecycleState",
    
    # Economic set components
    "EconomicSet",
    "EconomicSetKind",
    "ResourceEntry",
    "AgentEntry",
    "AllocationConstraint",
    "UtilityFunction",
    "MarketAssumptions",
    
    # Pipeline components
    "EconomicPipeline",
    "PipelineStage",
    "PipelineStageResult",
    
    # Resource analysis
    "ResourceAnalysis",
    "ResourceAssessment",
    "ResourceInventory",
]
