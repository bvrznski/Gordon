# Economic Reasoning - Phase 7.48
# ================================

"""
Economic Reasoning module.

This package implements Gordon's resource intelligence architecture.

Economic Reasoning determines:
    * How resources should be valued
    * How scarce resources should be allocated
    * Whether incentives are properly aligned
    * Whether economic efficiency is achieved

It never substitutes intuition for explicit economic analysis.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared import (
    EconomicSessionDescriptor,
    EconomicReasoningKind,
    EconomicLifecycleState,
    EconomicSet,
    EconomicSetKind,
    ResourceEntry,
    AgentEntry,
    AllocationConstraint,
    UtilityFunction,
    MarketAssumptions,
    EconomicPipeline,
    PipelineStage,
    PipelineStageResult,
    ResourceAnalysis,
    ResourceAssessment,
    ResourceInventory,
)

__all__ = [
    # Shared contracts
    "EconomicSessionDescriptor",
    "EconomicReasoningKind",
    "EconomicLifecycleState",
    
    "EconomicSet",
    "EconomicSetKind",
    "ResourceEntry",
    "AgentEntry",
    "AllocationConstraint",
    "UtilityFunction",
    "MarketAssumptions",
    
    "EconomicPipeline",
    "PipelineStage",
    "PipelineStageResult",
    
    "ResourceAnalysis",
    "ResourceAssessment",
    "ResourceInventory",
]