# Integration Module for Reward Evaluation & Value Integration Engine (Phase 4.10.3)
# ==================================================================================================

"""
Integration subsystems for reward evaluation.

This module provides benefit integrators, cost integrators, expected/realized
reward estimators, and value integration logic.
"""

from __future__ import annotations

from .base import (
    BaseBenefitIntegrator,
    BaseCostIntegrator,
)

from .benefit import (
    GoalBenefitIntegrator,
    KnowledgeBenefitIntegrator,
    EfficiencyBenefitIntegrator,
    ResourceBenefitIntegrator,
    StabilityBenefitIntegrator,
    SocialBenefitIntegrator,
)

from .cost import (
    TimeCostIntegrator,
    EnergyCostIntegrator,
    ComputeCostIntegrator,
    MemoryCostIntegrator,
    AttentionCostIntegrator,
    OpportunityCostIntegrator,
    RiskCostIntegrator,
)

from .expected import ExpectedRewardEstimator, MultiTimescaleExpectedReward
from .realized import RealizedRewardEstimator, MultiTimescaleRealizedReward
from .value import ValueIntegrator, ValueIntegrationResult, MixedValue
from .normalization import RewardNormalizer, NormalizationPolicy

__all__ = [
    # Base classes
    "BaseBenefitIntegrator",
    "BaseCostIntegrator",
    
    # Benefit integrators
    "GoalBenefitIntegrator",
    "KnowledgeBenefitIntegrator",
    "EfficiencyBenefitIntegrator",
    "ResourceBenefitIntegrator",
    "StabilityBenefitIntegrator",
    "SocialBenefitIntegrator",
    
    # Cost integrators
    "TimeCostIntegrator",
    "EnergyCostIntegrator",
    "ComputeCostIntegrator",
    "MemoryCostIntegrator",
    "AttentionCostIntegrator",
    "OpportunityCostIntegrator",
    "RiskCostIntegrator",
    
    # Estimators
    "ExpectedRewardEstimator",
    "MultiTimescaleExpectedReward",
    "RealizedRewardEstimator",
    "MultiTimescaleRealizedReward",
    
    # Value integration
    "ValueIntegrator",
    "ValueIntegrationResult", 
    "MixedValue",
    
    # Normalization
    "RewardNormalizer",
    "NormalizationPolicy",
]
