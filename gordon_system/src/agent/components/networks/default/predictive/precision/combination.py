# Precision Combination Engine - Phase 4.9.4
# ===========================================

"""
Combination engine for precision estimation.

Defines policies for combining reliability evidence from multiple sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WeightedAveragePolicy:
    """
    Combine reliability sources using weighted average.
    
    Rules:
        - Deterministic combination
        - Preserves source identity
        - No modification of inputs
    """
    
    def combine(self, sources: list[dict[str, Any]]) -> float:
        """
        Combine sources using weighted average.
        
        Args:
            sources: List of reliability source dictionaries
            
        Returns:
            Combined precision in [0.0, 1.0]
        """
        if not sources:
            return 0.5
        
        total_weight = sum(float(s.get("weight", 1.0)) for s in sources)
        if total_weight == 0:
            return 0.5
        
        weighted_sum = sum(
            float(s.get("value", 0.5)) * float(s.get("weight", 1.0))
            for s in sources
        )
        
        return max(0.0, min(1.0, weighted_sum / total_weight))


@dataclass(frozen=True)
class MinPolicy:
    """
    Combine reliability sources using minimum.
    
    Conservative approach that takes the lowest confidence estimate.
    """
    
    def combine(self, sources: list[dict[str, Any]]) -> float:
        """Combine using minimum value."""
        if not sources:
            return 0.5
        values = [float(s.get("value", 0.5)) for s in sources]
        return max(0.0, min(values))


@dataclass(frozen=True)
class MaxPolicy:
    """
    Combine reliability sources using maximum.
    
    Optimistic approach that takes the highest confidence estimate.
    """
    
    def combine(self, sources: list[dict[str, Any]]) -> float:
        """Combine using maximum value."""
        if not sources:
            return 0.5
        values = [float(s.get("value", 0.5)) for s in sources]
        return min(1.0, max(values))