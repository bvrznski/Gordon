# Precision Propagation Engine - Phase 4.9.4
# ===========================================

"""
Propagation engine for hierarchical precision estimation.

Defines how precision propagates through the hierarchy:
    Sensory → Contextual → Abstract
"""

from __future__ import annotations


class HierarchicalPropagationPolicy:
    """
    Policy for hierarchical precision propagation.
    
    Rules:
        - Propagation preserves originating estimates
        - Acyclic (no circular dependencies)
        - Deterministic ordering
    """
    
    def propagate(
        self,
        source_precision: float,
        source_uncertainty: float | None = None,
        hierarchy_level: str = "contextual",
        target_level: str = "abstract"
    ) -> float:
        """
        Compute propagated precision at a higher hierarchy level.
        
        Args:
            source_precision: Precision from lower level
            source_uncertainty: Uncertainty at source (optional)
            hierarchy_level: Current hierarchy level
            target_level: Target hierarchy level
            
        Returns:
            Propagated precision in [0.0, 1.0]
        """
        if not (0.0 <= source_precision <= 1.0):
            raise ValueError("Source precision must be in [0.0, 1.0]")
        
        # Base propagation factor
        base_factor = 0.85
        
        # Adjust for hierarchy gap
        level_mapping = {
            "sensory": 0,
            "contextual": 1,
            "abstract": 2
        }
        
        source_idx = level_mapping.get(hierarchy_level, 0)
        target_idx = level_mapping.get(target_level, 1)
        
        gap = max(0, target_idx - source_idx)
        
        # Decay factor based on propagation distance
        decay_factor = base_factor ** min(gap, 2)
        
        propagated = source_precision * decay_factor
        
        # If there's uncertainty, reduce precision accordingly
        if source_uncertainty is not None:
            propagated *= (1.0 - min(source_uncertainty, 0.5))
        
        return max(0.0, min(1.0, propagated))