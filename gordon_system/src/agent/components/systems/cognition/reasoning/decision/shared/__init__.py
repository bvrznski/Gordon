# Decision Reasoning Shared Contracts - Phase 7.41
# ================================================

"""
Shared contracts for Decision Reasoning.

This package provides canonical data structures for:
    * decision sessions and options
    * utility estimation
    * commitment formation
    * confidence calibration
    * decision revision and evolution
    * validation, governance, health, diagnostics
    * canonical decision contracts (Part 2)
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.descriptor import DecisionDescriptor
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.option_set import OptionSet
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.evaluation import (
    OptionEvaluation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.utility import (
    UtilityComponents,
    UtilityEstimation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.commitment import (
    DecisionCommitment,
    CommitmentFormation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.confidence import (
    ConfidenceMetrics,
    ConfidenceCalibration,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.revision import (
    DecisionRevision,
    DecisionRevisionPipeline,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.evolution import (
    DecisionEvolution,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.validation import (
    DecisionValidation,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.failure import (
    DecisionFailure,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.governance import (
    DecisionGovernance,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.health import (
    DecisionHealth,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.diagnostics import (
    DecisionDiagnostics,
)

# Phase 7.41 Canonical Contracts
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.decision_set import (
    DecisionSet,
    DecisionKind,
    DecisionState,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.pipeline import (
    DecisionPipeline,
    PipelineStage,
    PipelineStageResult,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.alternatives import (
    AlternativeAssessment,
    AlternativeManagement,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.utilities import (
    UtilityModel,
    UtilityDistribution,
    UtilityManagement,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.tradeoffs import (
    TradeoffAnalysis,
    TradeoffManagement,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.decision.shared.commitments import (
    CommitmentAnalysis,
    CommitmentManagement,
)

__all__ = [
    "DecisionDescriptor",
    "OptionSet",
    "OptionEvaluation",
    "UtilityComponents",
    "UtilityEstimation",
    "DecisionCommitment",
    "CommitmentFormation",
    "ConfidenceMetrics",
    "ConfidenceCalibration",
    "DecisionRevision",
    "DecisionRevisionPipeline",
    "DecisionEvolution",
    "DecisionValidation",
    "DecisionFailure",
    "DecisionGovernance",
    "DecisionHealth",
    "DecisionDiagnostics",
    # Phase 7.41 Canonical Contracts
    "DecisionSet",
    "DecisionKind",
    "DecisionState",
    "DecisionPipeline",
    "PipelineStage",
    "PipelineStageResult",
    "AlternativeAssessment",
    "AlternativeManagement",
    "UtilityModel",
    "UtilityDistribution",
    "UtilityManagement",
    "TradeoffAnalysis",
    "TradeoffManagement",
    "CommitmentAnalysis",
    "CommitmentManagement",
]