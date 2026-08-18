# Forecast Uncertainty Model - Phase 7.40
# =======================================

"""
Uncertainty model represents forecast uncertainty estimation.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class UncertaintyIdentity:
    """Unique identity for an uncertainty model."""
    
    uncertainty_id: str
    semantic_identity: str
    
    @classmethod
    def create(cls) -> UncertaintyIdentity:
        """Create a new uncertainty identity."""
        return cls(
            uncertainty_id=f"uncertainty:{uuid.uuid4().hex[:16]}",
            semantic_identity="uncertainty-identity",
        )


@dataclass(frozen=True)
class EpistemicUncertainty:
    """
    Epistemic (reducible) uncertainty.
    
    Represents uncertainty due to lack of knowledge or information
    that could be reduced with more data.
    """
    
    uncertainty_id: str
    source_description: str
    estimated_reduction_with_data: float  # How much would uncertainty reduce?
    current_confidence: float
    
    @classmethod
    def create(
        cls,
        source_description: str,
        current_confidence: float = 0.5,
    ) -> EpistemicUncertainty:
        """Create epistemic uncertainty."""
        return cls(
            uncertainty_id=f"epistemic:{uuid.uuid4().hex[:16]}",
            source_description=source_description,
            estimated_reduction_with_data=min(0.9 - current_confidence, 0.5),
            current_confidence=current_confidence,
        )


@dataclass(frozen=True)
class AleatoricUncertainty:
    """
    Aleatoric (irreducible) uncertainty.
    
    Represents inherent randomness in the system that cannot be
    reduced with more data.
    """
    
    uncertainty_id: str
    source_description: str
    irreducible_limit: float  # Minimum achievable uncertainty
    
    @classmethod
    def create(
        cls,
        source_description: str,
        minimum_uncertainty: float = 0.2,
    ) -> AleatoricUncertainty:
        """Create aleatoric uncertainty."""
        return cls(
            uncertainty_id=f"aleatoric:{uuid.uuid4().hex[:16]}",
            source_description=source_description,
            irreducible_limit=minimum_uncertainty,
        )


@dataclass(frozen=True)
class ConfidenceInterval:
    """Confidence interval for a prediction."""
    
    interval_id: str
    variable_name: str
    lower_bound: float
    upper_bound: float
    confidence_level: float  # e.g., 0.95
    
    @classmethod
    def create(
        cls,
        variable_name: str,
        estimate: float,
        margin_of_error: float,
        confidence_level: float = 0.95,
    ) -> ConfidenceInterval:
        """Create a confidence interval."""
        return cls(
            interval_id=f"ci:{uuid.uuid4().hex[:16]}",
            variable_name=variable_name,
            lower_bound=max(estimate - margin_of_error, 0),
            upper_bound=min(estimate + margin_of_error, 1),
            confidence_level=confidence_level,
        )


@dataclass(frozen=True)
class ForecastUncertainty:
    """
    Comprehensive forecast uncertainty model.
    
    Combines epistemic and aleatoric uncertainty with
    confidence distributions for forecasts.
    """
    
    # Identity
    uncertainty_identity: str
    
    # Uncertainty decomposition
    epistemic_uncertainty: EpistemicUncertainty
    aleatoric_uncertainty: AleatoricUncertainty
    
    # Combined metrics
    total_uncertainty: float
    calibration_quality: float  # How well do confidence levels match actual outcomes?
    
    # Confidence intervals
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    
    # Uncertainty sources
    uncertainty_sources: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    forecast_reference: Optional[str] = None  # Forecast ID this uncertainty applies to
    
    @classmethod
    def create(
        cls,
        epistemic_uncertainty: EpistemicUncertainty,
        aleatoric_uncertainty: AleatoricUncertainty,
        calibration_quality: float = 0.5,
        confidence_intervals: Dict[str, Tuple[float, float]] = None,
        uncertainty_sources: List[str] = None,
        forecast_reference: Optional[str] = None,
    ) -> ForecastUncertainty:
        """Create a new forecast uncertainty model."""
        total_uncertainty = (
            epistemic_uncertainty.current_confidence + aleatoric_uncertainty.irreducible_limit
        ) / 2
        
        return cls(
            uncertainty_identity=f"uncertainty:{uuid.uuid4().hex[:16]}",
            epistemic_uncertainty=epistemic_uncertainty,
            aleatoric_uncertainty=aleatoric_uncertainty,
            total_uncertainty=total_uncertainty,
            calibration_quality=calibration_quality,
            confidence_intervals=confidence_intervals or {},
            uncertainty_sources=uncertainty_sources or [],
            forecast_reference=forecast_reference,
        )


__all__ = [
    "ForecastUncertainty",
    "UncertaintyIdentity",
    "EpistemicUncertainty",
    "AleatoricUncertainty",
    "ConfidenceInterval",
]