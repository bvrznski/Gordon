# Perception Audit Constants - Phase 5.2.6
# ==========================================

"""
Constants for the Perception Audit subsystem.
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass


# =============================================================================
# AUDIT SEVERITY LEVELS
# =============================================================================


class AuditSeverity(Enum):
    """
    Severity level for audit findings.
    
    Levels:
        CRITICAL:   Immediate action required; perception is unreliable
        HIGH:       Significant degradation; confidence reduced substantially
        MEDIUM:     Noticeable issues; requires attention
        LOW:        Minor issues; acceptable within tolerance
        INFO:       informational, no action needed
    """
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass(frozen=True)
class SeverityThresholds:
    """Severity thresholds for automated classification."""
    critical_min: float = 0.9
    high_min: float = 0.7
    medium_min: float = 0.5
    low_min: float = 0.2


SEVERITY_THRESHOLDS = SeverityThresholds()

# =============================================================================
# FINDING TYPES
# =============================================================================


class FindingType(Enum):
    """
    Types of audit findings that can be detected.
    
    Categories:
        LOW_CONFIDENCE:           Confidence below acceptable threshold
        HIGH_UNCERTAINTY:         Uncertainty above acceptable threshold
        MISSING_MODALITY:         Expected modality not present
        STALE_PERCEPTION:         Perception data too old
        SENSOR_FAILURE:           Sensor reported failure
        PIPELINE_FAILURE:         Processing pipeline failed
        INCONSISTENT_MODALITIES:  Modalities disagree significantly
        LOW_COVERAGE:             Insufficient field coverage
        PARTIAL_OCCLUSION:        Significant occlusion detected
        TEMPORAL_DISCONTINUITY:   Temporal gaps in perception
        NOISY_INPUT:              High noise levels detected
        AMBIGUOUS_OBJECT:         Object classification ambiguous
        LOW_TEXT_CONFIDENCE:      OCR text confidence low
        LOW_TRACKING_CONFIDENCE:  Tracking quality poor
        LOW_DEPTH_CONFIDENCE:     Depth estimation unreliable
        OBJECT_DISAPPEARANCE:     Expected object missing
        OBJECT_APPEARANCE:        Unexpected object detected
        SCENE_CHANGE:             Scene changed significantly
        RESOURCE_LIMITATION:      System resource constrained
        UNKNOWN_STATE:            State cannot be determined
    """
    
    # Confidence/uncertainty issues
    LOW_CONFIDENCE = "low_confidence"
    HIGH_UNCERTAINTY = "high_uncertainty"
    
    # Missing data issues
    MISSING_MODALITY = "missing_modality"
    STALE_PERCEPTION = "stale_perception"
    PARTIAL_OCCLUSION = "partial_occlusion"
    
    # Failure issues
    SENSOR_FAILURE = "sensor_failure"
    PIPELINE_FAILURE = "pipeline_failure"
    
    # Consistency issues
    INCONSISTENT_MODALITIES = "inconsistent_modalities"
    TEMPORAL_DISCONTINUITY = "temporal_discontinuity"
    
    # Quality issues
    LOW_COVERAGE = "low_coverage"
    NOISY_INPUT = "noisy_input"
    
    # Ambiguity issues
    AMBIGUOUS_OBJECT = "ambiguous_object"
    LOW_TEXT_CONFIDENCE = "low_text_confidence"
    LOW_TRACKING_CONFIDENCE = "low_tracking_confidence"
    LOW_DEPTH_CONFIDENCE = "low_depth_confidence"
    
    # Content issues
    OBJECT_DISAPPEARANCE = "object_disappearance"
    OBJECT_APPEARANCE = "object_appearance"
    SCENE_CHANGE = "scene_change"
    
    # System issues
    RESOURCE_LIMITATION = "resource_limitation"
    UNKNOWN_STATE = "unknown_state"


# =============================================================================
# MODALITY QUALITY DIMENSIONS
# =============================================================================


class ModalityQualityDimension(Enum):
    """
    Quality dimensions for each modality.
    
    Visual: vision, depth, tracking
    Audio: audio, speech, ambient sound
    OCR: text recognition quality
    """
    
    # Visual dimensions
    VISUAL_QUALITY = "visual_quality"
    DEPTH_QUALITY = "depth_quality"
    TRACKING_QUALITY = "tracking_quality"
    
    # Audio dimensions  
    AUDIO_QUALITY = "audio_quality"
    SPEECH_QUALITY = "speech_quality"
    
    # OCR dimensions
    OCR_CONFIDENCE = "ocr_confidence"
    
    # Cross-cutting
    CONFIDENCE = "confidence"
    UNCERTAINTY = "uncertainty"
    FRESHNESS = "freshness"


# =============================================================================
# AUDIT STATUS
# =============================================================================


class AuditStatus(Enum):
    """
    Status of an audit operation.
    
    States:
        PENDING:     Audit queued, not yet processed
        PROCESSING:  Audit in progress
        COMPLETED:   Audit finished successfully
        FAILED:      Audit failed to complete
        PARTIAL:     Audit completed with partial results
    """
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# =============================================================================
# CONFIDENCE POLICIES
# =============================================================================


class ConfidencePolicy(Enum):
    """
    Policy for aggregating confidence across modalities.
    
    Policies:
        AVERAGE:       Simple average of all confidences
        WEIGHTED:      Weight by modality reliability
        MINIMUM:       Conservative - use lowest confidence
        MAXIMUM:       Optimistic - use highest confidence
        DEPENDENCY_AWARE: Account for source dependencies
        MULTIPLICATIVE: Multiply confidences (joint probability)
    """
    
    AVERAGE = "average"
    WEIGHTED = "weighted"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    DEPENDENCY_AWARE = "dependency_aware"
    MULTIPLICATIVE = "multiplicative"


# =============================================================================
# UNCERTAINTY POLICIES
# =============================================================================


class UncertaintyPolicy(Enum):
    """
    Policy for aggregating uncertainty across modalities.
    
    Policies:
        AVERAGE:       Simple average of all uncertainties
        WEIGHTED:      Weight by modality reliability
        MAXIMUM:       Conservative - use highest uncertainty
        COMBINED:      Combine as independent sources
        DEPENDENCY_AWARE: Account for source dependencies
    """
    
    AVERAGE = "average"
    WEIGHTED = "weighted"
    MAXIMUM = "maximum"
    COMBINED = "combined"
    DEPENDENCY_AWARE = "dependency_aware"


# =============================================================================
# DEFAULT CONFIGURATION VALUES
# =============================================================================


DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7
DEFAULT_UNCERTAINTY_THRESHOLD: float = 0.3
DEFAULT_STALENESS_SECONDS: float = 60.0
DEFAULT_COVERAGE_THRESHOLD: float = 0.5