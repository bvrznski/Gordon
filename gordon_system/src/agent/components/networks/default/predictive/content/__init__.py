# Canonical Predictive Content Types
# ====================================
"""
Immutable content types for the Predictive Processing Network Phase 4.9.1.

This module provides:

    - ConfidenceEstimate: Immutable confidence estimates with bounded scores
    - PredictiveUncertainty: Decomposed uncertainty tracking
    - PredictiveAssumption: Explicit assumption tracking
    - PredictiveConstraint: Typed constraint specifications

PHASE BOUNDARY:
    This module defines content types ONLY. No computation, no learning,
    no runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import (
        ConfidenceLevel,
        UncertaintyLevel,
        PredictiveAssumptionKind,
        PredictiveConstraintKind,
    )

# =============================================================================
# CONFIDENCE ESTIMATE (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConfidenceEstimate:
    """
    Immutable confidence estimate with bounded semantics.
    
    Fields:
        level:         Qualitative confidence level
        score:         Optional numeric score (0.0 to 1.0 where applicable)
        scale:         Reference to the confidence scale used
        calibration:   Optional calibration reference for calibrated probabilities
        basis:         Evidence supporting this confidence
        limitations:   Known limitations on this confidence
        
    Rules:
        - Confidence is distinct from Precision and Uncertainty
        - Scores are bounded [0.0, 1.0] where applicable
        - NaN and infinity are rejected at construction
        - Unknown confidence remains semantically distinct from low
    """
    level: ConfidenceLevel
    score: float | None = None  # Bounded if present, 0.0 to 1.0
    scale: str | None = None  # Scale identifier (e.g., "gordon.confidence.scale.v1")
    calibration: str | None = None  # Calibration reference where applicable
    basis: tuple[str, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        if self.score is not None:
            if not (0.0 <= self.score <= 1.0):
                raise ValueError("Confidence score must be between 0.0 and 1.0")
            # NaN check
            import math
            if math.isnan(self.score) or math.isinf(self.score):
                raise ValueError("Confidence score cannot be NaN or infinity")


# =============================================================================
# PREDICTIVE UNCERTAINTY (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictiveUncertainty:
    """
    Immutable decomposed uncertainty estimate.
    
    Fields:
        model:         Model/algorithm uncertainty
        observation:   Observation/noise uncertainty  
        context:       Context/relevance uncertainty
        temporal:      Temporal uncertainty (if supported)
        structural:    Structural/model-form uncertainty (if supported)
        total:         Composite total uncertainty
        decomposition_policy: Reference to the policy used for decomposition
        
    Rules:
        - Uncertainty is distinct from Confidence
        - Unknown uncertainty remains semantically distinct from low
        - Decomposition is deterministic and policy-defined
        - Phase 4.9.1 does NOT perform adaptive precision learning
    """
    model: float | None = None  # Bounded where applicable
    observation: float | None = None  # Bounded where applicable
    context: float | None = None  # Bounded where applicable
    temporal: float | None = None  # Optional temporal component
    structural: float | None = None  # Optional structural component
    total: float | None = None  # Composite (may be sum or weighted)
    decomposition_policy: str | None = None
    
    def __post_init__(self) -> None:
        # Validate bounded values if present
        import math
        for field_name in ['model', 'observation', 'context', 'temporal', 'structural']:
            value = getattr(self, field_name)
            if value is not None:
                if not (0.0 <= value <= 1.0):
                    raise ValueError(f"Uncertainty {field_name} must be between 0.0 and 1.0")
                if math.isnan(value) or math.isinf(value):
                    raise ValueError(f"Uncertainty {field_name} cannot be NaN or infinity")


# =============================================================================
# PREDICTIVE ASSUMPTION (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictiveAssumption:
    """
    Immutable predictive assumption with material evidence.
    
    Fields:
        identity:      Unique assumption identifier
        kind:          Kind of assumption (world state, causal, temporal, etc.)
        proposition:   The assumed proposition (semantic description)
        authority:     Source of the assumption (external reference)
        confidence:    Confidence in this assumption
        uncertainty:   Uncertainty about this assumption
        provenance:    Provenance tracking for this assumption
        
    Rules:
        - Material assumptions must be explicit, not hidden
        - Conflicting assumptions remain explicit
        - Missing assumptions are represented as absence, not fabrication
    """
    identity: str  # Simplified for now; use SemanticIdentity in full implementation
    kind: str  # PredictiveAssumptionKind or string code
    proposition: str
    authority: str | None = None
    confidence: ConfidenceEstimate | None = None
    uncertainty: PredictiveUncertainty | None = None
    provenance: dict[str, str] | None = None


# =============================================================================
# PREDICTIVE CONSTRAINT (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictiveConstraint:
    """
    Immutable predictive constraint specification.
    
    Fields:
        identity:      Unique constraint identifier
        kind:          Kind of constraint (physical, causal, temporal, etc.)
        specification: Constraint specification (semantic description)
        authority:     Source of the constraint
        provenance:    Provenance tracking for this constraint
        
    Rules:
        - Constraints are externally supplied or derived from projections
        - Goal constraints do not transfer Goal ownership
        - Policy constraints are immutable
    """
    identity: str  # Simplified; use SemanticIdentity in full implementation
    kind: str  # PredictiveConstraintKind or string code
    specification: str
    authority: str | None = None
    provenance: dict[str, str] | None = None


# =============================================================================
# PREDICTION SOURCE REFERENCE (IMMUTABLE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class PredictionSourceReference:
    """
    Reference to the source of a prediction.
    
    Fields:
        kind:          Source kind (world model, belief state, etc.)
        identity:      Source identifier where applicable
        authority:     Authority over the source
        
    Rules:
        - Source identifies origin, not ownership
        - No authority transfer via reference
    """
    kind: str  # PredictionSourceKind or string code
    identity: str | None = None
    authority: str | None = None


__all__: list[str] = [
    "ConfidenceEstimate",
    "PredictiveUncertainty",
    "PredictiveAssumption",
    "PredictiveConstraint",
    "PredictionSourceReference",
]
