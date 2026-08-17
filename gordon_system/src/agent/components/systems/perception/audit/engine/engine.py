# Perception Audit Engine - Phase 5.2.6
# ======================================

"""
Main audit engine for Perception Audit subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid

from gordon_system.src.agent.components.systems.perception.audit.constants import (
    AuditSeverity,
    FindingType,
    ConfidencePolicy as ConfigConfidencePolicy,
    UncertaintyPolicy as ConfigUncertaintyPolicy,
)
from gordon_system.src.agent.components.systems.perception.audit.models import (
    PerceptionSnapshot,
    ModalityAssessment,
    QualityAssessment,
    ConsistencyAssessment,
    CompletenessAssessment,
    ConfidenceAssessment,
    AuditFinding,
    PerceptionAuditReport,
    PerceptionAuditHealth,
    AuditStatistics,
)
from gordon_system.src.agent.components.systems.perception.audit.findings.detector import (
    FindingDetector,
)


# =============================================================================
# AUDIT REQUEST - What audit to perform
# =============================================================================


@dataclass(frozen=True)
class PerceptionAuditRequest:
    """
    Request for a perception audit.
    
    Fields:
        request_id:            Unique identifier for this request
        snapshot_id:           Snapshot to audit
        requested_at_utc:     When was the request made?
        
        # What to assess
        assess_quality:        Assess quality dimensions?
        assess_consistency:    Assess cross-modal consistency?
        assess_completeness:   Assess completeness?
        assess_health:         Assess system health?
        
        # Policies
        confidence_policy:     Policy for confidence aggregation
        uncertainty_policy:    Policy for uncertainty aggregation
        
        # Thresholds
        confidence_threshold:  Confidence below this is considered low
        uncertainty_threshold: Uncertainty above this is considered high
        
        # Provenance
        requestor_id:          Who requested the audit?
        provenance:            Request origin tracking
    """
    
    request_id: str
    
    snapshot_id: str
    requested_at_utc: float = field(default_factory=time.time)
    
    # Assessment flags
    assess_quality: bool = True
    assess_consistency: bool = True
    assess_completeness: bool = True
    assess_health: bool = True
    
    # Policies
    confidence_policy: ConfigConfidencePolicy = ConfigConfidencePolicy.WEIGHTED
    uncertainty_policy: ConfigUncertaintyPolicy = ConfigUncertaintyPolicy.MAXIMUM
    
    # Thresholds
    confidence_threshold: float = 0.7
    uncertainty_threshold: float = 0.3
    
    # Provenance
    requestor_id: str = "system"
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        snapshot_id: str,
        assess_quality: bool = True,
        assess_consistency: bool = True,
        assess_completeness: bool = True,
        assess_health: bool = True,
    ) -> "PerceptionAuditRequest":
        """Create a new audit request."""
        return cls(
            request_id=f"audit:{uuid.uuid4().hex[:16]}",
            snapshot_id=snapshot_id,
            assess_quality=assess_quality,
            assess_consistency=assess_consistency,
            assess_completeness=assess_completeness,
            assess_health=assess_health,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if request has minimal required data."""
        return len(self.request_id) > 0 and len(self.snapshot_id) > 0


# =============================================================================
# AUDIT PIPELINE - Stages of the audit process
# =============================================================================


class AuditPipelineStage:
    """
    A single stage in the audit pipeline.
    
    Subclasses should implement the process method.
    """
    
    def __init__(self, name: str):
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    def process(
        self,
        snapshot: PerceptionSnapshot,
        request: PerceptionAuditRequest,
        context: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[AuditFinding]]:
        """Process this stage. Returns (results, findings)."""
        raise NotImplementedError


class QualityAssessmentStage(AuditPipelineStage):
    """Quality assessment stage."""
    
    def __init__(self):
        super().__init__("quality_assessment")
    
    def process(
        self,
        snapshot: PerceptionSnapshot,
        request: PerceptionAuditRequest,
        context: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[AuditFinding]]:
        """Assess quality of the snapshot."""
        findings = []
        
        # Assess visual quality
        if snapshot.visual_confidence < request.confidence_threshold:
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.LOW_CONFIDENCE.value,
                severity=AuditSeverity.HIGH.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected="visual",
                description=f"Visual confidence {snapshot.visual_confidence:.2f} is below threshold {request.confidence_threshold}",
                provenance={"stage": "quality_assessment"},
            ))
        
        # Assess audio quality
        if snapshot.audio_confidence < request.confidence_threshold:
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.LOW_CONFIDENCE.value,
                severity=AuditSeverity.HIGH.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected="audio",
                description=f"Audio confidence {snapshot.audio_confidence:.2f} is below threshold {request.confidence_threshold}",
                provenance={"stage": "quality_assessment"},
            ))
        
        # Assess OCR quality
        if snapshot.ocr_confidence < request.confidence_threshold:
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.LOW_CONFIDENCE.value,
                severity=AuditSeverity.HIGH.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected="ocr",
                description=f"OCR confidence {snapshot.ocr_confidence:.2f} is below threshold {request.confidence_threshold}",
                provenance={"stage": "quality_assessment"},
            ))
        
        # Calculate quality scores
        overall_quality = (
            snapshot.visual_confidence +
            snapshot.audio_confidence +
            snapshot.ocr_confidence
        ) / 3
        
        results = {
            "overall_quality_score": overall_quality,
            "visual_quality_score": snapshot.visual_confidence,
            "audio_quality_score": snapshot.audio_confidence,
            "ocr_quality_score": snapshot.ocr_confidence,
        }
        
        return results, findings


class ConsistencyAssessmentStage(AuditPipelineStage):
    """Cross-modal consistency assessment stage."""
    
    def __init__(self):
        super().__init__("consistency_assessment")
    
    def process(
        self,
        snapshot: PerceptionSnapshot,
        request: PerceptionAuditRequest,
        context: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[AuditFinding]]:
        """Assess consistency between modalities."""
        findings = []
        
        # Calculate consistency scores (simplified)
        visual_audio_consistency = 1.0 - abs(snapshot.visual_confidence - snapshot.audio_confidence)
        visual_ocr_consistency = 1.0 - abs(snapshot.visual_confidence - snapshot.ocr_confidence)
        audio_ocr_consistency = 1.0 - abs(snapshot.audio_confidence - snapshot.ocr_confidence)
        
        overall_consistency = (
            visual_audio_consistency +
            visual_ocr_consistency +
            audio_ocr_consistency
        ) / 3
        
        # Check for inconsistencies (confidence differences > threshold)
        confidence_diff = max(
            abs(snapshot.visual_confidence - snapshot.audio_confidence),
            abs(snapshot.visual_confidence - snapshot.ocr_confidence),
            abs(snapshot.audio_confidence - snapshot.ocr_confidence),
        )
        
        if confidence_diff > 0.3:
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.INCONSISTENT_MODALITIES.value,
                severity=AuditSeverity.MEDIUM.value,
                confidence=0.9,
                uncertainty=0.1,
                modality_affected=None,
                description=f"Significant confidence differences between modalities (max diff: {confidence_diff:.2f})",
                provenance={"stage": "consistency_assessment"},
            ))
        
        results = {
            "overall_consistency_score": overall_consistency,
            "visual_audio_consistency": visual_audio_consistency,
            "visual_ocr_consistency": visual_ocr_consistency,
            "audio_ocr_consistency": audio_ocr_consistency,
        }
        
        return results, findings


class CompletenessAssessmentStage(AuditPipelineStage):
    """Completeness assessment stage."""
    
    def __init__(self):
        super().__init__("completeness_assessment")
    
    def process(
        self,
        snapshot: PerceptionSnapshot,
        request: PerceptionAuditRequest,
        context: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[AuditFinding]]:
        """Assess completeness of the snapshot."""
        findings = []
        
        # Calculate coverage scores
        visual_coverage = 1.0 - snapshot.uncertainty * 0.5
        audio_coverage = 1.0 - snapshot.uncertainty * 0.5
        ocr_coverage = 1.0 - snapshot.uncertainty * 0.5
        
        overall_completeness = (
            visual_coverage +
            audio_coverage +
            ocr_coverage
        ) / 3
        
        results = {
            "overall_completeness_score": overall_completeness,
            "visual_coverage": visual_coverage,
            "audio_coverage": audio_coverage,
            "ocr_coverage": ocr_coverage,
            "expected_modalities": ["visual", "audio", "ocr"],
            "present_modalities": self._get_present_modalities(snapshot),
        }
        
        return results, findings
    
    def _get_present_modalities(self, snapshot: PerceptionSnapshot) -> Tuple[str, ...]:
        """Get list of present modalities."""
        present = []
        if snapshot.visual_confidence > 0:
            present.append("visual")
        if snapshot.audio_confidence > 0:
            present.append("audio")
        if snapshot.ocr_confidence > 0:
            present.append("ocr")
        return tuple(present)


class FindingsDetectionStage(AuditPipelineStage):
    """Findings detection stage using detector."""
    
    def __init__(self):
        super().__init__("findings_detection")
    
    def process(
        self,
        snapshot: PerceptionSnapshot,
        request: PerceptionAuditRequest,
        context: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[AuditFinding]]:
        """Detect findings from the snapshot."""
        # Use FindingDetector to detect issues
        detector = FindingDetector()
        
        return detector.detect(snapshot, request)


# =============================================================================
# PERCEPTION AUDIT ENGINE - Main engine orchestrating audit pipeline
# =============================================================================


class PerceptionAuditEngine:
    """
    Engine that orchestrates perception audits.
    
    Responsibilities:
        - Validate audit requests
        - Execute audit pipeline stages
        - Aggregate assessment results
        - Generate audit reports
        
    Example:
        engine = PerceptionAuditEngine()
        
        request = PerceptionAuditRequest.create(
            snapshot_id="snapshot:abc123"
        )
        
        report = engine.audit(request)
        
        if not report.is_system_healthy:
            print("Issues found:", report.critical_findings)
    """
    
    def __init__(self):
        """Initialize the audit engine."""
        self._pipeline: List[AuditPipelineStage] = [
            QualityAssessmentStage(),
            ConsistencyAssessmentStage(),
            CompletenessAssessmentStage(),
            FindingsDetectionStage(),
        ]
        self._last_audit_stats: Optional[AuditStatistics] = None
        self._health_status = PerceptionAuditHealth()
    
    @property
    def last_statistics(self) -> Optional[AuditStatistics]:
        """Get statistics from the last audit."""
        return self._last_audit_stats
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Get current health status of the engine."""
        return {
            "availability": self._health_status.availability,
            "overall_health": self._health_status.overall_health,
            "is_healthy": self._health_status.is_healthy,
            "degradation_level": self._health_status.degradation_level,
        }
    
    def validate_request(
        self,
        request: PerceptionAuditRequest,
    ) -> Tuple[bool, List[str]]:
        """Validate an audit request."""
        errors = []
        
        if not request.request_id:
            errors.append("Request ID is required")
        
        if not request.snapshot_id:
            errors.append("Snapshot ID is required")
        
        return len(errors) == 0, errors
    
    def audit(self, request: PerceptionAuditRequest) -> PerceptionAuditReport:
        """
        Execute an audit for the given request.
        
        Args:
            request: The audit request
            
        Returns:
            Audit report with assessment results and findings
        """
        # For now, we'll create a snapshot from request or use defaults
        snapshot = self._get_snapshot_for_audit(request)
        
        start_time = time.time()
        
        all_findings: List[AuditFinding] = []
        all_results: Dict[str, Any] = {}
        context: Dict[str, Any] = {}
        
        # Execute each pipeline stage
        for stage in self._pipeline:
            results, findings = stage.process(snapshot, request, context)
            
            # Merge results
            all_results.update(results)
            all_findings.extend(findings)
            
            # Update context with stage results
            context[stage.name] = {
                "results": results,
                "findings_count": len(findings),
            }
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Build report from results and findings
        report = self._build_report(
            request=request,
            snapshot=snapshot,
            all_results=all_results,
            all_findings=all_findings,
            elapsed_ms=elapsed_ms,
        )
        
        # Update statistics
        self._update_statistics(report, elapsed_ms)
        
        return report
    
    def _get_snapshot_for_audit(self, request: PerceptionAuditRequest) -> PerceptionSnapshot:
        """Get or create a snapshot for audit (placeholder implementation)."""
        return PerceptionSnapshot.create(
            visual_confidence=0.85,
            audio_confidence=0.90,
            ocr_confidence=0.75,
            uncertainty=0.1,
        )
    
    def _build_report(
        self,
        request: PerceptionAuditRequest,
        snapshot: PerceptionSnapshot,
        all_results: Dict[str, Any],
        all_findings: List[AuditFinding],
        elapsed_ms: float,
    ) -> PerceptionAuditReport:
        """Build the final audit report."""
        # Filter findings by severity
        critical = [f for f in all_findings if f.severity == AuditSeverity.CRITICAL.value]
        high_priority = [f for f in all_findings if f.severity in (AuditSeverity.HIGH.value, AuditSeverity.CRITICAL.value)]
        
        # Calculate overall health score
        quality_score = all_results.get("overall_quality_score", 1.0)
        consistency_score = all_results.get("overall_consistency_score", 1.0)
        completeness_score = all_results.get("overall_completeness_score", 1.0)
        
        overall_health = (quality_score + consistency_score + completeness_score) / 3
        
        # Build recommendations based on findings
        recommendations: List[Dict[str, Any]] = []
        if len(critical) > 0:
            recommendations.append({
                "priority": "critical",
                "action": "immediate_re_audit",
                "reason": f"{len(critical)} critical issues found",
            })
        elif len(high_priority) > 2:
            recommendations.append({
                "priority": "high",
                "action": "review_findings",
                "reason": f"{len(high_priority)} high-priority issues found",
            })
        
        return PerceptionAuditReport(
            report_id=request.request_id,
            snapshot_id=request.snapshot_id,
            audit_timestamp_utc=time.time(),
            quality_summary={
                "overall_score": all_results.get("overall_quality_score", 1.0),
                "visual_score": all_results.get("visual_quality_score", 1.0),
                "audio_score": all_results.get("audio_quality_score", 1.0),
                "ocr_score": all_results.get("ocr_quality_score", 1.0),
            },
            confidence_summary={
                "overall_confidence": quality_score,
                "visual_confidence": snapshot.visual_confidence,
                "audio_confidence": snapshot.audio_confidence,
                "ocr_confidence": snapshot.ocr_confidence,
            },
            uncertainty_summary={
                "overall_uncertainty": snapshot.uncertainty,
                "assessment_uncertainty": 0.1,
            },
            completeness_summary={
                "overall_score": all_results.get("overall_completeness_score", 1.0),
                "visual_coverage": all_results.get("visual_coverage", 1.0),
                "audio_coverage": all_results.get("audio_coverage", 1.0),
                "ocr_coverage": all_results.get("ocr_coverage", 1.0),
            },
            findings=tuple(f.to_dict() if hasattr(f, 'to_dict') else {"finding_id": f.finding_id} for f in all_findings),
            critical_findings=tuple(f.to_dict() if hasattr(f, 'to_dict') else {"finding_id": f.finding_id} for f in critical),
            high_priority_findings=tuple(f.to_dict() if hasattr(f, 'to_dict') else {"finding_id": f.finding_id} for f in high_priority),
            consistency_summary={
                "overall_score": all_results.get("overall_consistency_score", 1.0),
            },
            conflicts_summary={},
            overall_health_score=overall_health,
            is_system_healthy=len(critical) == 0 and overall_health >= 0.8,
            degradation_level=1.0 - overall_health,
            recommendations=tuple(recommendations),
            statistics={
                "findings_count": len(all_findings),
                "elapsed_ms": elapsed_ms,
            },
            diagnostics={
                "stages_executed": [s.name for s in self._pipeline],
                "context": context,
            },
        )
    
    def _update_statistics(self, report: PerceptionAuditReport, elapsed_ms: float):
        """Update audit statistics."""
        if self._last_audit_stats is None:
            self._last_audit_stats = AuditStatistics()
        
        stats = self._last_audit_stats
        
        # Update counters
        total_audits = stats.total_audits + 1
        successful_audits = stats.successful_audits + (1 if report.is_system_healthy else 0)
        partial_audits = stats.partial_audits + (0 if report.is_system_healthy else 1)
        
        # Update timing averages
        avg_duration = (
            (stats.average_duration_ms * stats.total_audits + elapsed_ms) / total_audits
        )
        
        self._last_audit_stats = AuditStatistics(
            total_audits=total_audits,
            successful_audits=successful_audits,
            partial_audits=partial_audits,
            failed_audits=stats.failed_audits,
            average_duration_ms=avg_duration,
            min_duration_ms=min(stats.min_duration_ms, elapsed_ms) if stats.total_audits > 0 else elapsed_ms,
            max_duration_ms=max(stats.max_duration_ms, elapsed_ms),
            total_findings_detected=stats.total_findings_detected + len(report.findings),
            critical_findings_count=stats.critical_findings_count + len(report.critical_findings),
            high_priority_count=stats.high_priority_count + len(report.high_priority_findings),
            medium_priority_count=stats.medium_priority_count,
            low_priority_count=stats.low_priority_count,
            visual_audits=stats.visual_audits + 1,
            audio_audits=stats.audio_audits,
            ocr_audits=stats.ocr_audits,
        )


__all__ = [
    "PerceptionAuditEngine",
    "PerceptionAuditRequest",
    "AuditPipelineStage",
]