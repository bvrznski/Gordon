# Agentic Reward Network - Phase 4.10.1
# ========================================

"""
Canonical Agentic Reward Network (Phase 4.10.1).

The Reward Network evaluates cognitive and behavioral outcomes by estimating:

    * expected benefit
    * realized benefit  
    * expected cost
    * realized cost
    * goal progress
    * drive satisfaction
    * resource expenditure
    * outcome quality

It transforms cognitive outcomes into reward representations.

CRITICAL DISTINCTION:
    - Truth belongs to Predictive Processing
    - Importance belongs to Salience  
    - Decision belongs to Executive Control
    - Reward belongs to Outcome Evaluation

This is a PURE semantic evaluation layer.
No learning. No decision making. No action selection.

The Reward Network produces immutable reward estimates that downstream systems
(Prediction, Planning, Executive Control) consume for their own computations.
"""

from __future__ import annotations

# Core models
from .outcome import (
    Outcome,
    OutcomeCategory,
    OutcomeSourceSubsystem,
)

from .reward import (
    RewardEstimate,
    Valence,
    RewardSources,
)

from .benefit import BenefitEstimate

from .cost import CostEstimate

from .confidence import ConfidenceEstimate

from .uncertainty import UncertaintyEstimate

# Landscape
from .landscape import (
    RewardLandscape,
    MultiTimescaleReward,
    HierarchicalReward,
)

# Baseline and dynamics
from .baseline import RewardBaseline

from .dynamics import RewardDynamics

# State
from .state import RewardState

# Engine
from .engine import RewardEvaluationEngine

# Requests/Results
from .request import RewardEvaluationRequest

from .result import RewardEvaluationResult

# Validation
from .validation import (
    RewardValidation,
    ValidationErrorType,
)

__all__ = [
    # Core models
    "Outcome",
    "OutcomeCategory", 
    "OutcomeSourceSubsystem",
    "RewardEstimate",
    "Valence",
    "RewardSources",
    "BenefitEstimate",
    "CostEstimate",
    "ConfidenceEstimate",
    "UncertaintyEstimate",
    # Landscape
    "RewardLandscape",
    "MultiTimescaleReward", 
    "HierarchicalReward",
    # Baseline and dynamics
    "RewardBaseline",
    "RewardDynamics",
    # State
    "RewardState",
    # Engine
    "RewardEvaluationEngine",
    # Requests/Results
    "RewardEvaluationRequest",
    "RewardEvaluationResult",
    # Validation
    "RewardValidation",
    "ValidationErrorType",
]