# Evidence Fusion Pipeline - Phase 7.7
# =====================================

"""
Canonical evidence fusion contracts.

Fusion integrates multiple evidence sources while preserving uncertainty.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class FusionStrategy(Enum):
    """Strategies for combining evidence."""
    
    WEIGHTED_AVERAGE = "weighted_average"           # Weighted mean of values
    BAYESIAN_UPDATE = "bayesian_update"             # Bayesian combination
    MAX_VOTE = "max_vote"                           # Take most probable option
    MIN_CONFIDENCE = "min_confidence"               # Conservative estimate
    PRODUCT_RULE = "product_rule"                   # Multiply likelihoods


@dataclass(frozen=True)
class FusedDistribution:
    """
    Result of fusing multiple probability distributions.
    
    Represents the combined belief after considering all sources.
    """
    
    # Identity
    fusion_id: str                        # Unique identifier
    
    # Fusion parameters
    variable_name: str                    # What variable is described?
    fusion_strategy: FusionStrategy       # Which strategy was used?
    
    # Result distribution
    distribution_params: Dict[str, float] = field(default_factory=dict)  # value → probability
    
    # Source statistics
    num_sources_fused: int = 0            # How many sources contributed?
    source_confidence_average: float = 0.5  # Avg confidence of contributing sources
    
    # Fusion quality
    consensus_measure: float = 1.0        # How agreement was there? (0-1)
    entropy_after_fusion: float = 0.0     # Resulting uncertainty
    
    # Metadata
    fused_at_utc: float = field(default_factory=time.time)
    
    def get_probability(self, value: str) -> float:
        """Get probability of a specific value."""
        return self.distribution_params.get(value, 0.0)


@dataclass(frozen=True)
class EvidenceFusionPipeline:
    """
    Pipeline for fusing multiple evidence sources.
    
    Fuses:
        - Sensor evidence
        - Reasoning evidence  
        - Memory evidence
        - Tool evidence
        - Simulation evidence
    
    Fusion preserves uncertainty throughout the process.
    """
    
    # Identity
    pipeline_id: str                      # Unique identifier
    
    # Input
    participating_sources: Tuple[str, ...] = ()  # Source IDs involved
    fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE
    
    # Weights used
    source_weights: Dict[str, float] = field(default_factory=dict)
    
    # Output
    fused_distribution: Optional[FusedDistribution] = None
    
    # Fusion metadata
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if fusion produced a result."""
        return self.fused_distribution is not None
    
    @classmethod
    def create(
        cls,
        source_ids: List[str],
        weights: Optional[Dict[str, float]] = None,
        strategy: FusionStrategy = FusionStrategy.WEIGHTED_AVERAGE,
    ) -> EvidenceFusionPipeline:
        """Create a new fusion pipeline."""
        weight_dict = weights or {}
        
        # Normalize weights if provided
        if weight_dict:
            total_weight = sum(weight_dict.values())
            if total_weight > 0:
                weight_dict = {k: v / total_weight for k, v in weight_dict.items()}
        
        return cls(
            pipeline_id=f"fusion_pipeline:{uuid.uuid4().hex[:16]}",
            participating_sources=tuple(source_ids),
            fusion_strategy=strategy,
            source_weights=weight_dict,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvidenceFusionPipeline",
    "FusionStrategy", 
    "FusedDistribution",
]