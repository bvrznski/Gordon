# Perception Integrated Confidence - Phase 5.2.3
# ===============================================

"""
Integrated Confidence: Confidence aggregation across integration sources.

Integration confidence accounts for source confidences, dependencies,
correspondence strength, and binding quality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# INTEGRATED CONFIDENCE - Aggregated confidence from integration
# =============================================================================


@dataclass(frozen=True)
class IntegratedPerceptualConfidence:
    """
    Confidence result after integrating multiple evidence sources.
    
    Fields:
        source_confidences: Original confidences from each source
        source_dependencies: Dependency relationships between sources
        correspondence_effect: How correspondence affected confidence
        temporal_binding_effect: How temporal binding affected confidence
        spatial_binding_effect: How spatial binding affected confidence
        conflict_effect: How conflicts affected confidence
        missing_evidence_effect: How missing evidence affected confidence
        processing_quality_effect: How processing quality affected confidence
        fusion_strategy_effect: How fusion strategy affected confidence
        resulting_confidence: Final integrated confidence (0.0-1.0)
    """
    
    source_confidences: Tuple[float, ...]  # Original confidence values
    
    source_dependencies: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Dependency info
    
    correspondence_effect: float = 1.0     # Multiplicative effect from correspondence
    temporal_binding_effect: float = 1.0   # Multiplicative effect from binding
    spatial_binding_effect: float = 1.0    # Multiplicative effect from binding
    
    conflict_effect: float = 1.0           # Reduces confidence if conflicts detected
    missing_evidence_effect: float = 1.0   # Reduces confidence if evidence missing
    
    processing_quality_effect: float = 1.0 # Effect of processing degradation
    
    fusion_strategy_effect: float = 1.0    # Strategy-specific effect
    
    resulting_confidence: float = 1.0      # Final value (0.0-1.0)
    
    confidence_basis: str = "integration"  # Why this confidence?
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate resulting confidence."""
        if not 0.0 <= self.resulting_confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.resulting_confidence}")
    
    @classmethod
    def aggregate(
        cls,
        source_confidences: List[float],
        dependency_factors: Optional[List[float]] = None,  # Reduction factors for dependencies
        correspondence_score: float = 1.0,
        binding_score: float = 1.0,
        conflict_penalty: float = 0.0,
        missing_evidence_penalty: float = 0.0,
    ) -> "IntegratedPerceptualConfidence":
        """
        Aggregate confidence from multiple sources.
        
        Args:
            source_confidences: Confidence values from each source
            dependency_factors: Dependency reduction factors (optional)
            correspondence_score: How strong is the correspondence?
            binding_score: How strong are the bindings?
            conflict_penalty: Penalty for detected conflicts (0.0-1.0)
            missing_evidence_penalty: Penalty for missing evidence (0.0-1.0)
            
        Returns:
            Integrated confidence
        """
        if not source_confidences:
            return cls(
                source_confidences=tuple(),
                resulting_confidence=0.5,
                provenance={"reason": "no sources"},
            )
        
        # Base average
        base_confidence = sum(source_confidences) / len(source_confidences)
        
        # Apply dependency reduction if provided
        if dependency_factors:
            for factor in dependency_factors:
                if factor < 1.0:  # Dependent sources reduce effective confidence
                    base_confidence *= (1.0 - (1.0 - base_confidence) * (1.0 - factor))
        
        # Apply effects
        integrated = (
            base_confidence
            * correspondence_score
            * binding_score
            * (1.0 - conflict_penalty)
            * (1.0 - missing_evidence_penalty)
            * 0.95  # Default processing quality effect
            * 0.98  # Default fusion strategy effect
        )
        
        return cls(
            source_confidences=tuple(source_confidences),
            correspondence_effect=correspondence_score,
            temporal_binding_effect=binding_score,
            spatial_binding_effect=binding_score,
            conflict_effect=1.0 - conflict_penalty,
            missing_evidence_effect=1.0 - missing_evidence_penalty,
            resulting_confidence=max(0.0, min(1.0, integrated)),
            confidence_basis="aggregated_from_sources",
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )
    
    @classmethod
    def from_corroborative_sources(
        cls,
        source_confidences: List[float],
        independence_scores: List[float],  # How independent is each source?
    ) -> "IntegratedPerceptualConfidence":
        """
        Aggregate confidence from corroborative (independent) sources.
        
        More independent confirmations should increase confidence, but
        only if the sources are truly independent.
        
        Args:
            source_confidences: Confidence values
            independence_scores: Independence assessment for each source
            
        Returns:
            Integrated confidence with dependency awareness
        """
        if not source_confidences:
            return cls(source_confidences=tuple(), resulting_confidence=0.5)
        
        # Weight by independence - independent sources count more
        total_weight = sum(independence_scores) if independence_scores else len(source_confidences)
        weighted_sum = sum(
            conf * (ind if i < len(independence_scores) else 1.0)
            for i, conf in enumerate(source_confidences)
        )
        
        base_confidence = weighted_sum / max(total_weight, 1.0)
        
        # Boost from multiple independent confirmations
        boost = min(0.3, len(source_confidences) * 0.1 * sum(independence_scores) / max(len(independence_scores), 1))
        
        return cls(
            source_confidences=tuple(source_confidences),
            resulting_confidence=min(1.0, base_confidence + boost),
            confidence_basis="corroborative_sources",
            provenance={"independence_aware": True},
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert integrated confidence to dictionary."""
        return {
            "source_confidences": list(self.source_confidences),
            "source_dependencies_count": len(self.source_dependencies),
            "correspondence_effect": self.correspondence_effect,
            "temporal_binding_effect": self.temporal_binding_effect,
            "spatial_binding_effect": self.spatial_binding_effect,
            "conflict_effect": self.conflict_effect,
            "missing_evidence_effect": self.missing_evidence_effect,
            "processing_quality_effect": self.processing_quality_effect,
            "fusion_strategy_effect": self.fusion_strategy_effect,
            "resulting_confidence": self.resulting_confidence,
            "confidence_basis": self.confidence_basis,
            "provenance": dict(self.provenance),
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def normalize_integration_confidence(value: float) -> float:
    """Normalize a value to 0.0-1.0 range for integration confidence."""
    return max(0.0, min(1.0, float(value)))