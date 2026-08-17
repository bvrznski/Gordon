# Perception Audit Models - Phase 5.2.6
# ======================================

"""
Immutable models for the Perception Audit subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PERCEPTION SNAPSHOT - Input to audit (immutable view of perception state)
# =============================================================================


@dataclass(frozen=True)
class PerceptionSnapshot:
    """
    Immutable snapshot of perceptual state at a point in time.
    
    This represents the output from perception that will be audited.
    
    Fields:
        snapshot_id:         Unique identifier for this snapshot
        generation_timestamp: When was this snapshot generated?
        projection_kind:     Kind of projection (percept, scene, event)
        
        # Per-modality data
        visual_data:        Visual modality data
        audio_data:         Audio modality data  
        ocr_data:           OCR modality data
        
        # Quality metrics per modality
        visual_confidence:   Overall visual confidence (0.0-1.0)
        audio_confidence:    Overall audio confidence (0.0-1.0)
        ocr_confidence:      Overall OCR confidence (0.0-1.0)
        
        uncertainty:         Known uncertainty (0.0-1.0)
        limitations:         Known limitations affecting the snapshot
        
        # Metadata
        source_artifact_ids: Source artifacts this snapshot is based on
        temporal_scope:      Temporal boundaries
        spatial_scope:       Spatial boundaries
    """
    
    snapshot_id: str
    
    generation_timestamp_utc: float = field(default_factory=time.time)
    projection_kind: str = "percept"
    
    # Per-modality data containers (dictionaries for extensibility)
    visual_data: Dict[str, Any] = field(default_factory=dict)
    audio_data: Dict[str, Any] = field(default_factory=dict)
    ocr_data: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    visual_confidence: float = 1.0
    audio_confidence: float = 1.0
    ocr_confidence: float = 1.0
    
    uncertainty: float = 0.0
    
    limitations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    source_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    temporal_scope: Optional[Dict[str, Any]] = None
    spatial_scope: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        projection_kind: str = "percept",
        visual_confidence: float = 1.0,
        audio_confidence: float = 1.0,
        ocr_confidence: float = 1.0,
        snapshot_id: Optional[str] = None,
    ) -> "PerceptionSnapshot":
        """Create a new PerceptionSnapshot."""
        return cls(
            snapshot_id=snapshot_id or f"snapshot:{uuid.uuid4().hex[:24]}",
            projection_kind=projection_kind,
            visual_confidence=visual_confidence,
            audio_confidence=audio_confidence,
            ocr_confidence=ocr_confidence,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if snapshot has valid data."""
        return 0.0 <= self.visual_confidence <= 1.0 and \
               0.0 <= self.audio_confidence <= 1.0 and \
               0.0 <= self.ocr_confidence <= 1.0 and \
               0.0 <= self.uncertainty <= 1.0


# =============================================================================
# MODALITY ASSESSMENT - Quality assessment for a single modality
# =============================================================================


@dataclass(frozen=True)
class ModalityAssessment:
    """
    Assessment of a single modality's quality.
    
    Fields:
        modality:          Which modality was assessed?
        confidence:        Confidence in this modality (0.0-1.0)
        uncertainty:       Uncertainty about this modality (0.0-1.0)
        quality_score:     Overall quality score (0.0-1.0)
        
        # Dimension scores
        visual_quality:    Visual-specific quality (if applicable)
        audio_quality:     Audio-specific quality (if applicable)
        ocr_quality:       OCR-specific quality (if applicable)
        
        freshness_seconds: How fresh is this data? (-1 if unknown)
        coverage:          Field of view coverage (0.0-1.0)
        noise_level:       Detected noise level (0.0-1.0)
        
        # Health indicators
        sensor_health:     Sensor operational health (0.0-1.0)
        pipeline_health:   Pipeline processing health (0.0-1.0)
        
        issues:            List of identified issues
    """
    
    modality: str  # "visual", "audio", "ocr", etc.
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    quality_score: float = 1.0
    
    # Dimension scores
    visual_quality: Optional[float] = None
    audio_quality: Optional[float] = None
    ocr_quality: Optional[float] = None
    
    freshness_seconds: Optional[float] = None
    coverage: float = 1.0
    noise_level: float = 0.0
    
    sensor_health: float = 1.0
    pipeline_health: float = 1.0
    
    issues: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# QUALITY ASSESSMENT - Overall quality evaluation
# =============================================================================


@dataclass(frozen=True)
class QualityAssessment:
    """
    Overall quality assessment across all modalities.
    
    Fields:
        overall_quality_score:   Combined quality score (0.0-1.0)
        
        # Per-modality scores
        visual_quality_score:    Visual modality quality (0.0-1.0)
        audio_quality_score:     Audio modality quality (0.0-1.0)
        ocr_quality_score:       OCR modality quality (0.0-1.0)
        
        # Dimension breakdowns
        coverage_score:          Field coverage quality (0.0-1.0)
        confidence_score:        Confidence reliability (0.0-1.0)
        uncertainty_score:       Uncertainty reliability (0.0-1.0)
        freshness_score:         Data freshness quality (0.0-1.0)
        
        total_issues:            Total number of issues found
        critical_issues:         Number of critical issues
        high_priority_issues:    Number of high priority issues
        
        modality_assessments:   Per-modality assessments
        assessment_timestamp_utc: When was this assessed?
    """
    
    overall_quality_score: float = 1.0
    
    visual_quality_score: float = 1.0
    audio_quality_score: float = 1.0
    ocr_quality_score: float = 1.0
    
    coverage_score: float = 1.0
    confidence_score: float = 1.0
    uncertainty_score: float = 1.0
    freshness_score: float = 1.0
    
    total_issues: int = 0
    critical_issues: int = 0
    high_priority_issues: int = 0
    
    modality_assessments: Tuple[ModalityAssessment, ...] = field(default_factory=tuple)
    
    assessment_timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# CONSISTENCY ASSESSMENT - Cross-modal agreement evaluation
# =============================================================================


@dataclass(frozen=True)
class ConsistencyAssessment:
    """
    Assessment of consistency between modalities.
    
    Fields:
        overall_consistency_score: Combined consistency score (0.0-1.0)
        
        # Pairwise consistency
        visual_audio_consistency: Visual vs audio agreement (0.0-1.0)
        visual_ocr_consistency:   Visual vs OCR agreement (0.0-1.0)
        audio_ocr_consistency:    Audio vs OCR agreement (0.0-1.0)
        
        # Temporal consistency
        temporal_coherence:       Temporal continuity quality (0.0-1.0)
        
        # Spatial consistency
        spatial_alignment_score:  Spatial alignment quality (0.0-1.0)
        
        conflicts_detected:      Number of conflicts found
        conflicts:               Conflict details
        
        modalities_agreeing:     How many modalities agree?
        total_modalities:        Total modalities considered
    """
    
    overall_consistency_score: float = 1.0
    
    visual_audio_consistency: float = 1.0
    visual_ocr_consistency: float = 1.0
    audio_ocr_consistency: float = 1.0
    
    temporal_coherence: float = 1.0
    spatial_alignment_score: float = 1.0
    
    conflicts_detected: int = 0
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    modalities_agreeing: int = 0
    total_modalities: int = 0


# =============================================================================
# COMPLETENESS ASSESSMENT - Coverage and completeness evaluation
# =============================================================================


@dataclass(frozen=True)
class CompletenessAssessment:
    """
    Assessment of perceptual completeness.
    
    Fields:
        overall_completeness_score: Combined completeness score (0.0-1.0)
        
        # Coverage metrics
        visual_coverage:      Visual field coverage (0.0-1.0)
        audio_coverage:       Audio field coverage (0.0-1.0)
        ocr_coverage:         OCR field coverage (0.0-1.0)
        
        expected_modalities:   Which modalities were expected?
        present_modalities:    Which modalities are actually present?
        
        # Content completeness
        objects_detected_ratio: Ratio of expected to detected objects
        
        missing_data_summary:  What data is missing? (reason -> count)
        stale_data_count:      How much stale data exists?
        
        assessment_timestamp_utc: When was this assessed?
    """
    
    overall_completeness_score: float = 1.0
    
    visual_coverage: float = 1.0
    audio_coverage: float = 1.0
    ocr_coverage: float = 1.0
    
    expected_modalities: Tuple[str, ...] = field(default_factory=tuple)
    present_modalities: Tuple[str, ...] = field(default_factory=tuple)
    
    objects_detected_ratio: float = 1.0
    
    missing_data_summary: Dict[str, int] = field(default_factory=dict)
    stale_data_count: int = 0
    
    assessment_timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# CONFIDENCE ASSESSMENT - Confidence aggregation and evaluation
# =============================================================================


@dataclass(frozen=True)
class ConfidenceAssessment:
    """
    Assessment of confidence levels and their reliability.
    
    Fields:
        overall_confidence:      Combined confidence (0.0-1.0)
        
        # Per-modality confidence
        visual_confidence:       Visual modality confidence (0.0-1.0)
        audio_confidence:        Audio modality confidence (0.0-1.0)
        ocr_confidence:          OCR modality confidence (0.0-1.0)
        
        # Aggregated values
        aggregated_confidence:   Confidence after aggregation (0.0-1.0)
        confidence_aggregation_policy: Policy used for aggregation
        
        # Confidence quality indicators
        source_count:            Number of sources contributing
        independent_sources:     Number of independent sources
        dependency_factor:       Dependency between sources (0.0-1.0)
        
        confidence_basis:        Why is this confidence level?
    """
    
    overall_confidence: float = 1.0
    
    visual_confidence: float = 1.0
    audio_confidence: float = 1.0
    ocr_confidence: float = 1.0
    
    aggregated_confidence: float = 1.0
    confidence_aggregation_policy: str = "average"
    
    source_count: int = 0
    independent_sources: int = 0
    dependency_factor: float = 0.0
    
    confidence_basis: str = "aggregated_from_modalities"


# =============================================================================
# AUDIT FINDING - Individual finding from the audit
# =============================================================================


@dataclass(frozen=True)
class AuditFinding:
    """
    An individual finding detected during an audit.
    
    Fields:
        finding_id:          Unique identifier for this finding
        finding_type:        Type of finding (see FindingType enum)
        
        severity:            Severity level of the finding
        confidence:          Confidence in the finding assessment (0.0-1.0)
        uncertainty:         Uncertainty about this finding (0.0-1.0)
        
        modality_affected:   Which modality is affected? (optional)
        description:         Human-readable description
        
        # Evidence
        supporting_evidence: Evidence supporting this finding
        counter_evidence:    Evidence against this finding
        
        # Context
        timestamp_utc:       When was the finding detected?
        provenance:          How was this finding determined?
        
        # Recommendations
        recommendation:      What should be done about this finding?
    """
    
    finding_id: str
    
    finding_type: str  # String form of FindingType enum value
    
    severity: str  # String form of AuditSeverity enum value
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    modality_affected: Optional[str] = None
    description: str = ""
    
    supporting_evidence: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    counter_evidence: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "finding_id": self.finding_id,
            "finding_type": self.finding_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "modality_affected": self.modality_affected,
            "description": self.description,
            "supporting_evidence_count": len(self.supporting_evidence),
            "counter_evidence_count": len(self.counter_evidence),
            "timestamp_utc": self.timestamp_utc,
            "provenance": dict(self.provenance),
            "recommendation": self.recommendation,
        }


# =============================================================================
# PERCEPTION AUDIT REPORT - Output of an audit
# =============================================================================


@dataclass(frozen=True)
class PerceptionAuditReport:
    """
    Complete audit report for a perception snapshot.
    
    Fields:
        report_id:              Unique identifier for this report
        
        # Input reference
        snapshot_id:            Snapshot that was audited
        audit_timestamp_utc:   When was the audit performed?
        
        # Quality assessment
        quality_summary:       Overall quality assessment
        confidence_summary:    Confidence evaluation
        uncertainty_summary:   Uncertainty evaluation
        completeness_summary:  Completeness evaluation
        
        # Findings
        findings:              List of detected issues
        critical_findings:     Critical findings (subset)
        high_priority_findings: High priority findings (subset)
        
        # Cross-modal analysis
        consistency_summary:   Consistency assessment
        conflicts_summary:     Conflict summary
        
        # Health and status
        overall_health_score:  Overall system health (0.0-1.0)
        is_system_healthy:     Is the system healthy?
        degradation_level:     Level of degraded operation (0.0-1.0)
        
        # Recommendations
        recommendations:       Actionable recommendations
        
        # Statistics and metadata
        statistics:            Audit statistics
        diagnostics:           Diagnostic information
    """
    
    report_id: str
    
    snapshot_id: str
    audit_timestamp_utc: float = field(default_factory=time.time)
    
    # Summaries
    quality_summary: Dict[str, Any] = field(default_factory=dict)
    confidence_summary: Dict[str, Any] = field(default_factory=dict)
    uncertainty_summary: Dict[str, Any] = field(default_factory=dict)
    completeness_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    critical_findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    high_priority_findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Cross-modal
    consistency_summary: Dict[str, Any] = field(default_factory=dict)
    conflicts_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Health and status
    overall_health_score: float = 1.0
    is_system_healthy: bool = True
    degradation_level: float = 0.0
    
    # Recommendations
    recommendations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Metadata
    statistics: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# PERCEPTION AUDIT HEALTH - System health status
# =============================================================================


@dataclass(frozen=True)
class PerceptionAuditHealth:
    """
    Health status of the perception audit system.
    
    Fields:
        availability:          Is the audit system available?
        
        # Component health (0.0-1.0)
        quality_assessment_health:  Quality assessment component
        consistency_assessment_health: Cross-modal assessment component
        confidence_aggregation_health: Confidence aggregation component
        completeness_assessment_health: Completeness assessment component
        findings_detection_health: Findings detection component
        report_generation_health: Report generation component
        
        # Degradation
        degradation_level:     Current degradation (0.0 = healthy, 1.0 = fully degraded)
        
        # Last check
        last_check_utc:        When was health last checked?
        health_status:         Detailed health status per component
    """
    
    availability: bool = True
    
    quality_assessment_health: float = 1.0
    consistency_assessment_health: float = 1.0
    confidence_aggregation_health: float = 1.0
    completeness_assessment_health: float = 1.0
    findings_detection_health: float = 1.0
    report_generation_health: float = 1.0
    
    degradation_level: float = 0.0
    
    last_check_utc: float = field(default_factory=time.time)
    health_status: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def overall_health(self) -> float:
        """Calculate overall health as average of component health."""
        components = [
            self.quality_assessment_health,
            self.consistency_assessment_health,
            self.confidence_aggregation_health,
            self.completeness_assessment_health,
            self.findings_detection_health,
            self.report_generation_health,
        ]
        return sum(components) / len(components)
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is fully healthy."""
        return self.availability and self.overall_health >= 0.95
    
    @property
    def is_degraded(self) -> bool:
        """Check if system is operating in degraded mode."""
        return not self.is_healthy and self.availability


# =============================================================================
# AUDIT STATISTICS - Audit operation statistics
# =============================================================================


@dataclass(frozen=True)
class AuditStatistics:
    """
    Statistics from audit operations.
    
    Fields:
        total_audits:          Total number of audits performed
        successful_audits:     Number of completed successfully
        partial_audits:        Number of partial completions
        failed_audits:         Number that failed
        
        # Timing
        average_duration_ms:   Average audit duration in milliseconds
        min_duration_ms:       Minimum duration
        max_duration_ms:       Maximum duration
        
        # Findings statistics
        total_findings_detected: Total findings across all audits
        critical_findings_count: Critical findings count
        high_priority_count:     High priority findings count
        medium_priority_count:   Medium priority findings count
        low_priority_count:      Low priority findings count
        
        # Per-modality counts
        visual_audits:         Number of visual audits
        audio_audits:          Number of audio audits  
        ocr_audits:            Number of OCR audits
        
        last_audit_timestamp_utc: When was the last audit performed?
    """
    
    total_audits: int = 0
    successful_audits: int = 0
    partial_audits: int = 0
    failed_audits: int = 0
    
    average_duration_ms: float = 0.0
    min_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    
    total_findings_detected: int = 0
    critical_findings_count: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    
    visual_audits: int = 0
    audio_audits: int = 0
    ocr_audits: int = 0
    
    last_audit_timestamp_utc: float = field(default_factory=time.time)