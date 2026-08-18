# Moral Reasoning Shared Contracts - Phase 7.49
# ==============================================

"""
Shared contract definitions for the Moral Reasoning subsystem.

This module exports canonical contracts that define the moral reasoning architecture:
- Descriptors: Metadata about moral reasoning sessions
- Sets: Immutable contexts for moral evaluation
- Pipeline: Deterministic reasoning flow
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.descriptor import (
    MoralDescriptor,
    MoralKind,
    MoralLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.moral_set import (
    MoralSet,
    StakeholderEntry,
    MoralValue,
    EthicalPrinciple,
    FactualContext,
    EthicalFramework,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.pipeline import (
    MoralPipeline,
    PipelineStage,
    PipelineStageResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.stakeholders import (
    StakeholderType,
    StakeholderImpact,
    StakeholderAnalysis,
    StakeholderSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.duties import (
    DutyType,
    DutyStatus,
    DutyAnalysis,
    DutyConflict,
    DutySet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.values import (
    MoralValue,
    ValueConflict,
    ValueAnalysis,
    ValueSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.moral.shared.consequences import (
    Consequence,
    ConsequenceAnalysis,
    ConsequenceSet,
)

__all__ = [
    # Descriptors
    "MoralDescriptor",
    "MoralKind", 
    "MoralLifecycle",
    
    # Sets
    "MoralSet",
    "StakeholderEntry",
    "MoralValue",
    "EthicalPrinciple",
    "FactualContext",
    "EthicalFramework",
    
    # Pipeline
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
