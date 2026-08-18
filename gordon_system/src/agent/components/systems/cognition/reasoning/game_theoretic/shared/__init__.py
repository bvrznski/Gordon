# Game-Theoretic Reasoning Shared - Phase 7.43
# ==============================================

"""
Shared infrastructure for Game-Theoretic Reasoning.

This module contains shared contracts, data structures, and utilities
used across the game-theoretic reasoning subsystem.
"""

from .descriptor import (
    GameReasoningKind,
    GameSessionState,
    GameDescriptor,
)
from .game_set import GameSet
from .pipeline import (
    PipelineStage,
    GamePipelineResult,
    GamePipeline,
)
from .games import (
    GameIdentity,
    GameModel,
    GameTrace,
)
from .strategies import (
    StrategyIdentity,
    StrategyAnalysis,
    StrategyManagement,
)
from .equilibria import (
    EquilibriumIdentity,
    EquilibriumAnalysis,
    EquilibriumManagement,
)
from .payoffs import (
    PayoffIdentity,
    PayoffAnalysis,
    PayoffManagement,
)
from .incentives import (
    IncentiveIdentity,
    IncentiveAnalysis,
    IncentiveManagement,
)
from .adversarial import AdversarialAnalysis
from .cooperative import CooperativeAnalysis
from .evolution import GameEvolution, EvolutionTrigger
from .validation import ValidationResult, GameValidation
from .failure import GameFailure, FailureKind
from .governance import GovernanceFindings, GameGovernance
from .health import GameHealth, HealthMetrics
from .diagnostics import DiagnosticRecord, Diagnostics

__all__ = [
    # Descriptors
    "GameReasoningKind",
    "GameSessionState",
    "GameDescriptor",
    # Game sets
    "GameSet",
    # Pipeline
    "PipelineStage",
    "GamePipelineResult",
    "GamePipeline",
    # Games
    "GameIdentity",
    "GameModel",
    "GameTrace",
    # Strategies
    "StrategyIdentity",
    "StrategyAnalysis",
    "StrategyManagement",
    # Equilibria
    "EquilibriumIdentity",
    "EquilibriumAnalysis",
    "EquilibriumManagement",
    # Payoffs
    "PayoffIdentity",
    "PayoffAnalysis",
    "PayoffManagement",
    # Incentives
    "IncentiveIdentity",
    "IncentiveAnalysis",
    "IncentiveManagement",
    # Adversarial
    "AdversarialAnalysis",
    # Cooperative
    "CooperativeAnalysis",
    # Evolution
    "GameEvolution",
    "EvolutionTrigger",
    # Validation
    "ValidationResult",
    "GameValidation",
    # Failure
    "GameFailure",
    "FailureKind",
    # Governance
    "GovernanceFindings",
    "GameGovernance",
    # Health
    "GameHealth",
    "HealthMetrics",
    # Diagnostics
    "DiagnosticRecord",
    "Diagnostics",
]