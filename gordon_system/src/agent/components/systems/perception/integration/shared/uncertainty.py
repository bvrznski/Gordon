# Perception Integrated Uncertainty - Phase 5.2.3
# ================================================

"""
Integrated Uncertainty: Uncertainty aggregation across integration sources.

Integration uncertainty tracks various sources of uncertainty including
source uncertainty, dependency uncertainty, correspondence uncertainty,
and binding uncertainty.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# INTEGRATED UNCERTAINTY - Aggregated uncertainty from integration
# =============================================================================


@dataclass(frozen=True)
class IntegratedPerceptualUncertainty:
    """
    Uncertainty result after integrating multiple evidence sources.
    
    Fields:
        source_uncertainties: Original uncertainties from each source
        dependency_uncertainty: Uncertainty about dependencies
        correspondence_uncertainty: Uncertainty about correspondences
        temporal_binding_uncertainty: Uncertainty about temporal bindings
        spatial_binding_uncertainty: Uncertainty about spatial bindings
        fusion_uncertainty: Uncertainty introduced by fusion strategy
        conflict_uncertainty: Uncertainty due to unresolved conflicts
        missing_modality_uncertainty: Uncertainty from missing modalities
        visibility_uncertainty: Uncertainty from limited visibility
        
        resulting_uncertainty: Final integrated uncertainty (0.0-1.0)
    """
    
    source_uncertainties: Tuple[float, ...]  # Original uncertainty values
    
    dependency_uncertainty: float = 0.0     # Uncertainty about dependencies
    correspondence_uncertainty: float = 0.0 # Uncertainty about correspondences
    temporal_binding_uncertainty: float = 0.0  # Uncertainty about temporal bindings
    spatial_binding_uncertainty: float = 0.0   # Uncertainty about spatial bindings
    
    fusion_uncertainty: float = 0.0         # Fusion strategy uncertainty
    conflict_uncertainty: float = 0.0       # Conflict-related uncertainty
    missing_modality_uncertainty: float = 0.0  # Missing modality effect
    visibility_uncertainty: float = 0.0     # Limited visibility effect
    
    resulting_uncertainty: float = 0.0      # Final value (0.0-1.0)
    
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)  # Which sources?
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate resulting uncertainty."""
        if not 0.0 <= self.resulting_uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {self.resulting_uncertainty}")
    
    @classmethod
    def aggregate(
        cls,
        source_uncertainties: List[float],
        dependency_factor: float = 0.0,
        correspondence_score: float = 1.0,
        binding_scores: Optional[Dict[str, float]] = None,
    ) -> "IntegratedPerceptualUncertainty":
        """
        Aggregate uncertainty from multiple sources.
        
        Args:
            source_uncertainties: Uncertainty values from each source
            dependency_factor: How much dependencies increase uncertainty (0.0-1.0)
            correspondence_score: Strength of correspondence evidence
            binding_scores: Temporal/spatial binding quality scores
            
        Returns:
            Integrated uncertainty
        """
        if not source_uncertainties:
            return cls(
                source_uncertainties=tuple(),
                resulting_uncertainty=0.5,
            )
        
        # Base average uncertainty
        base_uncertainty = sum(source_uncertainties) / len(source_uncertainties)
        
        # Apply dependency increase
        dependent_uncertainty = base_uncertainty + (dependency_factor * 0.3)
        
        # Apply correspondence penalty
        if correspondence_score < 1.0:
            dependent_uncertainty += (1.0 - correspondence_score) * 0.2
        
        # Apply binding penalties
        binding_scores = binding_scores or {}
        temporal_penalty = (1.0 - binding_scores.get("temporal", 1.0)) * 0.15
        spatial_penalty = (1.0 - binding_scores.get("spatial", 1.0)) * 0.15
        
        integrated = min(1.0, dependent_uncertainty + temporal_penalty + spatial_penalty)
        
        sources = ["sources"]
        if dependency_factor > 0:
            sources.append("dependencies")
        if correspondence_score < 1.0:
            sources.append("correspondence")
        
        return cls(
            source_uncertainties=tuple(source_uncertainties),
            dependency_uncertainty=dependency_factor,
            correspondence_uncertainty=max(0.0, (1.0 - correspondence_score) * 0.5),
            temporal_binding_uncertainty=temporal_penalty,
            spatial_binding_uncertainty=spatial_penalty,
            resulting_uncertainty=integrated,
            uncertainty_sources=tuple(sources),
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert integrated uncertainty to dictionary."""
        return {
            "source_uncertainties": list(self.source_uncertainties),
            "dependency_uncertainty": self.dependency_uncertainty,
            "correspondence_uncertainty": self.correspondence_uncertainty,
            "temporal_binding_uncertainty": self.temporal_binding_uncertainty,
            "spatial_binding_uncertainty": self.spatial_binding_uncertainty,
            "fusion_uncertainty": self.fusion_uncertainty,
            "conflict_uncertainty": self.conflict_uncertainty,
            "missing_modality_uncertainty": self.missing_modality_uncertainty,
            "visibility_uncertainty": self.visibility_uncertainty,
            "resulting_uncertainty": self.resulting_uncertainty,
            "uncertainty_sources": list(self.uncertainty_sources),
            "provenance": dict(self.provenance),
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def normalize_integration_uncertainty(value: float) -> float:
    """Normalize a value to 0.0-1.0 range for integration uncertainty."""
    return max(0.0, min(1.0, float(value)))