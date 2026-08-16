# Precision Estimation Engine - Phase 4.9.4
# ==========================================
"""
Precision Estimation Engine for the Gordon Cognitive Architecture.

This module implements canonical precision estimation:
    * Reliability estimation of prediction errors
    * Modality-specific reliability assessment
    * Contextual and hierarchical precision
    * Latent and structural reliability
    * Temporal stability assessment

ARCHITECTURAL RESPONSIBILITY:
    This subsystem owns:
        - Precision estimates (reliability weights for prediction errors)
        - Reliability sources (explicit evidence for trustworthiness)
        - Hierarchy-aware precision propagation
        - Timescale-specific precision
        - Cross-modal agreement/disagreement tracking
        
    This subsystem NEVER owns:
        - Prediction generation
        - Observation comparison  
        - Belief revision
        - Action selection
        - Learning

INPUTS (immutable):
    PredictionErrorState: Pre-computed error signals
    ContextProjection: External context information
    PolicyConstraints: Combination and propagation policies
    
OUTPUTS (immutable):
    PrecisionLandscape: Complete reliability assessment
    PrecisionEstimate: Per-error reliability weights
    ReliabilityEvidence: Decomposed evidence sources

All computations are deterministic, stateless, and explainable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# CANONICAL EXPORTS - Phase 4.9.4 precision models
# =============================================================================

__all__ = [
    # Canonical models
    "PrecisionEstimate",
    "PrecisionLandscape",
    
    # Reliability evidence
    "ReliabilitySource",
    
    # Request/Result contracts
    "PrecisionRequest",
    "PrecisionResult",
    
    # Policy types
    "PrecisionCombinationPolicy",
    "PropagationPolicy",
]

# =============================================================================
# CANONICAL MODELS
# =============================================================================


@dataclass(frozen=True, slots=True)
class PrecisionEstimate:
    """
    Canonical immutable precision estimate model.
    
    Represents reliability weight for a single prediction error.
    
    Fields:
        identity:                       Unique identifier for this estimate
        target_prediction_error:        Reference to the PredictionError
        precision:                      Reliability value [0.0, 1.0]
        confidence:                     Confidence in this precision
        uncertainty:                    Uncertainty decomposition
        sources:                        Explicit reliability evidence
        provenance:                     How this estimate was computed
        revision:                       Estimate version number
        
    Rules:
        - Exactly one canonical PrecisionEstimate model exists
        - Deeply immutable with frozen dataclass
        - Never modifies PredictionError it references
        - Preserves provenance of all contributing factors
    """
    identity: str  # PrecisionEstimateIdentity or string code
    target_prediction_error: str  # Reference to PredictionError identity
    precision: float  # Reliability weight [0.0, 1.0]
    confidence: float = 0.5  # Confidence in this estimate [0.0, 1.0]
    uncertainty: dict[str, Any] | None = None  # Uncertainty decomposition
    sources: tuple[dict[str, Any], ...] = field(default_factory=tuple)  # ReliabilitySource dicts
    provenance: str | None = None  # Trace of estimation process
    revision: int = 1
    
    def __post_init__(self) -> None:
        if not (0.0 <= self.precision <= 1.0):
            raise ValueError("Precision must be in [0.0, 1.0]")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be in [0.0, 1.0]")


@dataclass(frozen=True, slots=True)
class PrecisionLandscape:
    """
    Canonical immutable precision landscape aggregate.
    
    Contains complete reliability state across all dimensions.
    
    Fields:
        estimates:                      All precision estimates
        hierarchy:                      Hierarchical structure (sensory→contextual→abstract)
        modalities:                     Modality-specific breakdown
        timescales:                     Timescale-specific breakdown
        cross_level_precision:          Cross-level relationships
        trace:                          Structural trace of construction
        findings:                       Aggregate findings
        limitations:                    Aggregate limitations
        
    Rules:
        - Exactly one canonical PrecisionLandscape exists
        - Immutable aggregate
        - Preserves all precision estimates unchanged
        - No belief updates included
    """
    estimates: tuple[PrecisionEstimate, ...] = field(default_factory=tuple)
    hierarchy: dict[str, Any] | None = None  # Hierarchy mapping
    modalities: dict[str, tuple[PrecisionEstimate, ...]] = field(
        default_factory=dict
    )  # Modality → estimates
    timescales: dict[str, tuple[PrecisionEstimate, ...]] = field(
        default_factory=dict
    )  # TimespanKind → estimates
    cross_level_precision: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    trace: dict[str, Any] | None = None
    findings: tuple[str, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# RELIABILITY EVIDENCE
# =============================================================================


@dataclass(frozen=True, slots=True)
class ReliabilitySource:
    """
    Canonical reliability evidence source.
    
    Represents one factor contributing to precision estimation.
    
    Fields:
        source_type:                    Category of evidence (sensor, context, etc.)
        value:                          Raw evidence value [0.0, 1.0]
        weight:                         Weight in combination [0.0, 1.0]
        provenance:                     Source identification
        uncertainty:                    Uncertainty about this source
        
    Rules:
        - Evidence remains explicit and decomposed
        - Each source preserves its identity
        - Sources combine deterministically
    """
    source_type: str  # ReliabilitySourceType enum value
    value: float = 0.5  # Raw evidence [0.0, 1.0]
    weight: float = 1.0  # Combination weight [0.0, 1.0]
    provenance: str | None = None
    uncertainty: float | None = None


# =============================================================================
# REQUEST/RESULT CONTRACTS
# =============================================================================


@dataclass(frozen=True, slots=True)
class PrecisionRequest:
    """
    Immutable precision estimation request.
    
    Consumes PredictionErrorState and context to produce estimates.
    
    Fields:
        identity:                       Request identifier
        prediction_error_state:         Pre-computed error state (external)
        context:                        External context projection
        policy:                         Combination/propagation policy reference
        semantic_time:                  External semantic time reference
        
    Rules:
        - All inputs are immutable and external
        - No runtime references in request
        - Deterministic inputs produce deterministic outputs
    """
    identity: str  # PrecisionRequestIdentity or string code
    prediction_error_state: dict[str, Any]  # Reference to PredictionErrorState
    context: dict[str, Any] | None = None  # ContextProjection
    policy: str | None = None  # Policy reference
    semantic_time: str | None = None  # External time reference


@dataclass(frozen=True, slots=True)
class PrecisionResult:
    """
    Immutable precision estimation result.
    
    Contains complete precision assessment with traceability.
    
    Fields:
        request_identity:               Source request identifier
        landscape:                      Complete precision landscape
        findings:                       Result-level findings
        limitations:                    Result-level limitations
        trace:                          Estimation process trace
        status:                         Completion status
        
    Rules:
        - No modifications to input state
        - Traceable provenance of all estimates
        - Deterministic output for deterministic inputs
    """
    request_identity: str
    landscape: PrecisionLandscape
    findings: tuple[str, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    trace: dict[str, Any] | None = None
    status: str = "completed"  # StatusCode enum value


# =============================================================================
# POLICIES
# =============================================================================


class PrecisionCombinationPolicy:
    """
    Policy interface for combining reliability evidence.
    
    Defines the contract for precision combination strategies.
    
    Rules:
        - Combination remains deterministic
        - Evidence sources preserve identity
        - No belief revision occurs
    """
    
    def combine(
        self, sources: tuple[ReliabilitySource, ...]
    ) -> float:
        """
        Combine reliability sources into a single precision value.
        
        Args:
            sources: Tuple of reliability evidence sources
            
        Returns:
            Combined precision value in [0.0, 1.0]
            
        Rules:
            - Deterministic output
            - Preserves source evidence
            - No modification of inputs
        """
        raise NotImplementedError


class PropagationPolicy:
    """
    Policy interface for hierarchical precision propagation.
    
    Defines how precision propagates through the hierarchy.
    
    Rules:
        - Propagation preserves originating estimates
        - Acyclic (no circular dependencies)
        - Deterministic ordering
    """
    
    def propagate(
        self, 
        source_precision: float,
        source_uncertainty: float | None,
        hierarchy_level: str
    ) -> float:
        """
        Compute propagated precision at a hierarchy level.
        
        Args:
            source_precision: Source estimate precision
            source_uncertainty: Uncertainty at source
            hierarchy_level: Target hierarchy level
            
        Returns:
            Propagated precision value
            
        Rules:
            - Deterministic output
            - Preserves source uncertainty
        """
        raise NotImplementedError