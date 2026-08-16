# Perception Processing Transformation - Phase 5.2.2
# ==================================================

"""
Transformation Record: Tracks what happened during processing.

A TransformationRecord preserves complete information about a transformation,
enabling traceability, replay, and validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# TRANSFORMATION KIND - What type of transformation was applied?
# =============================================================================


class TransformationKind(Enum):
    """
    Kind of transformation performed.
    
    Kinds:
        ADAPTIVE:       Configuration adjustment based on conditions
        HABITUATION:    Repetition assessment with reduced emphasis
        TEMPORAL:       Timing alignment across evidence streams
        SPATIAL:        Coordinate system mapping
        IDENTITY:       Cross-source entity correspondence evaluation
        SCHEMA:         Structural schema alignment
        TRANSLATION:    Representation to canonical form conversion
        NORMALIZATION:  Convention to canonical form conversion
        VALIDATION:     Output validation before publication
    """
    
    ADAPTIVE = "adaptive"
    HABITUATION = "habituation"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    IDENTITY = "identity"
    SCHEMA = "schema"
    TRANSLATION = "translation"
    NORMALIZATION = "normalization"
    VALIDATION = "validation"


# =============================================================================
# CONFIDENCE EFFECT - How did confidence change?
# =============================================================================


class ConfidenceEffect(Enum):
    """
    Effect on confidence during transformation.
    
    Effects:
        PRESERVED:       No change (same value maintained)
        RECALIBRATED:    Changed based on calibration
        REDUCED:         Confidence decreased
        INCREASED_WITH_EVIDENCE: Increased with supporting evidence
        UNKNOWN:         Unknown effect
    """
    
    PRESERVED = "preserved"
    RECALIBRATED = "recalibrated"
    REDUCED = "reduced"
    INCREASED_WITH_EVIDENCE = "increased_with_evidence"
    UNKNOWN = "unknown"


# =============================================================================
# UNCERTAINTY EFFECT - How did uncertainty change?
# =============================================================================


class UncertaintyEffect(Enum):
    """
    Effect on uncertainty during transformation.
    
    Effects:
        PRESERVED:       Source uncertainty maintained
        INCREASED:       Additional uncertainty introduced
        REDUCED:         Uncertainty reduced through calibration
        UNKNOWN:         Unknown effect
    """
    
    PRESERVED = "preserved"
    INCREASED = "increased"
    REDUCED = "reduced"
    UNKNOWN = "unknown"


# =============================================================================
# PERCEPTUAL TRANSFORMATION - Transformation contract
# =============================================================================


@dataclass(frozen=True)
class PerceptualTransformation:
    """
    Contract for a perceptual transformation.
    
    Fields:
        transformation_identity:   Unique identifier for this transformation
        transformation_kind:       What kind of transformation?
        source_artifacts:          Which artifacts were transformed?
        output_artifacts:          What artifacts were produced?
        transformation_parameters: Parameters used in the transformation
        information_loss:          Declared information loss
        confidence_effect:         How did confidence change?
        uncertainty_effect:        How did uncertainty change?
    """
    
    transformation_identity: str           # Unique ID
    
    transformation_kind: TransformationKind  # What kind of transform?
    
    source_artifacts: Tuple[str, ...]      # Source artifact IDs
    output_artifacts: Tuple[str, ...]      # Output artifact IDs
    
    transformation_parameters: Dict[str, Any] = field(default_factory=dict)
    
    information_loss: Optional["ProcessingInformationLoss"] = None  # noqa
    
    confidence_effect: ConfidenceEffect = ConfidenceEffect.PRESERVED
    uncertainty_effect: UncertaintyEffect = UncertaintyEffect.PRESERVED


# =============================================================================
# PROCESSING TRANSFORMATION RECORD - Complete transformation trace
# =============================================================================


@dataclass(frozen=True)
class ProcessingTransformationRecord:
    """
    Complete record of a single transformation in processing.
    
    Fields:
        transformation_identity:   Unique identifier for this record
        stage_identity:            Which stage performed the transformation?
        stage_revision:            Revision of that stage
        source_artifacts:          Input artifact identities
        output_artifacts:          Output artifact identities
        parameters:                Transformation parameters used
        configuration_revision:    Configuration version at time of transform
        calibration_revision:      Calibration version at time of transform
        confidence_effect:         How did confidence change?
        uncertainty_effect:        How did uncertainty change?
        information_loss:          What was lost?
        validation_result:         Did output pass validation?
        provenance:                Origin tracking with transformation history
    """
    
    transformation_identity: str           # Unique record ID
    
    stage_identity: str                    # Which stage performed it?
    stage_revision: int = 1                # Stage revision used
    
    source_artifacts: Tuple[str, ...]      # Input artifact IDs
    output_artifacts: Tuple[str, ...]      # Output artifact IDs
    
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    configuration_revision: Optional[int] = None
    calibration_revision: Optional[int] = None
    
    confidence_effect: ConfidenceEffect = ConfidenceEffect.PRESERVED
    uncertainty_effect: UncertaintyEffect = UncertaintyEffect.PRESERVED
    information_loss: Optional["ProcessingInformationLoss"] = None  # noqa
    
    validation_result: bool = True         # Did output pass validation?
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Traceability data