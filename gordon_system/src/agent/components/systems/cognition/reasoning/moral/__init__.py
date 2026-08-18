# Moral Reasoning - Phase 7.49
# ============================

"""
Moral reasoning module for Gordon cognitive architecture.

This module provides ethical evaluation capabilities including:
- Stakeholder analysis and management
- Duty identification and conflict resolution
- Value balancing and prioritization  
- Consequence analysis and projection
- Ethical justification generation
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared import (
    MoralDescriptor,
    MoralKind,
    MoralLifecycle,
    MoralSet,
    StakeholderEntry,
    MoralValue as SharedMoralValue,
    EthicalPrinciple,
    FactualContext,
    EthicalFramework,
    MoralPipeline,
    PipelineStage,
    PipelineStageResult,
    StakeholderType,
    StakeholderImpact,
    StakeholderAnalysis,
    StakeholderSet,
    DutyType,
    DutyStatus,
    DutyAnalysis,
    DutyConflict,
    DutySet,
    MoralValue,
    ValueConflict,
    ValueAnalysis,
    ValueSet,
    Consequence,
    ConsequenceAnalysis,
    ConsequenceSet,
)

__all__ = [
    # Shared contracts
    "MoralDescriptor",
    "MoralKind", 
    "MoralLifecycle",
    "MoralSet",
    "StakeholderEntry",
    "SharedMoralValue",
    "EthicalPrinciple",
    "FactualContext",
    "EthicalFramework",
    "MoralPipeline",
    "PipelineStage",
    "PipelineStageResult",
    
    # Stakeholders
    "StakeholderType",
    "StakeholderImpact",
    "StakeholderAnalysis",
    "StakeholderSet",
    
    # Duties
    "DutyType",
    "DutyStatus",
    "DutyAnalysis",
    "DutyConflict",
    "DutySet",
    
    # Values
    "MoralValue",
    "ValueConflict",
    "ValueAnalysis",
    "ValueSet",
    
    # Consequences
    "Consequence",
    "ConsequenceAnalysis",
    "ConsequenceSet",
]