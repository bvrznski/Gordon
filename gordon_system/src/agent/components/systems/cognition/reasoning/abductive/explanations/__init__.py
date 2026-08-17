# Abduction Explanations Module - Phase 7.3
# =========================================

"""
Explanation generation and comparison for abductive reasoning.

This module provides:
    - Explanation candidate definitions
    - Generation strategies
    - Comparison and ranking mechanisms
"""

from agent.components.systems.cognition.reasoning.abductive.explanations.candidate import (
    ExplanationCandidate,
    ExplanationGeneration,
    ExplanationStrategy,
)

from agent.components.systems.cognition.reasoning.abductive.explanations.comparison import (
    HypothesisComparison,
    ExplanationRanking,
    RankingStrategy,
)

__all__ = [
    "ExplanationCandidate",
    "ExplanationGeneration", 
    "ExplanationStrategy",
    "HypothesisComparison",
    "ExplanationRanking",
    "RankingStrategy",
]