# Perception Audit Findings Detector - Phase 5.2.6
# ================================================

"""
Findings detection module for Perception Audit subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid

from gordon_system.src.agent.components.systems.perception.audit.constants import (
    AuditSeverity,
    FindingType,
)
from gordon_system.src.agent.components.systems.perception.audit.models import (
    PerceptionSnapshot,
    AuditFinding,
)


# =============================================================================
# FINDING DETECTION RESULT - Result from findings detection
# =============================================================================


@dataclass(frozen=True)
class FindingDetectionResult:
    """
    Result from a findings detection operation.
    
    Fields:
        detected_findings:     List of findings that were detected
        detection_timestamp:   When was detection performed?
        detection_duration_ms: How long did detection take?
        detection_statistics:  Statistics about the detection process
    """
    
    detected_findings: Tuple[Dict[str, Any], ...]
    detection_timestamp_utc: float = field(default_factory=time.time)
    detection_duration_ms: float = 0.0
    detection_statistics: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# FINDING DETECTOR - Detect audit findings from snapshots
# =============================================================================


class FindingDetector:
    """
    Detector for finding issues in perception snapshots.
    
    Responsibilities:
        - Detect low confidence findings
        - Detect high uncertainty findings
        - Detect stale perception
        - Detect missing modalities
        - Detect inconsistencies between modalities
        
    Example:
        detector = FindingDetector()
        
        snapshot = PerceptionSnapshot.create(visual_confidence=0.5)
        
        findings = detector.detect(snapshot, request)
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        uncertainty_threshold: float = 0.3,
        staleness_seconds: float = 60.0,
    ):
        """
        Initialize the finding detector.
        
        Args:
            confidence_threshold: Confidence below this is considered low
            uncertainty_threshold: Uncertainty above this is considered high
            staleness_seconds: Data older than this is considered stale
        """
        self._confidence_threshold = confidence_threshold
        self._uncertainty_threshold = uncertainty_threshold
        self._staleness_seconds = staleness_seconds
    
    def detect(
        self,
        snapshot: PerceptionSnapshot,
        request: Optional[Any] = None,  # Audit request (optional)
    ) -> Tuple[Dict[str, Any], List[AuditFinding]]:
        """
        Detect findings from a perception snapshot.
        
        Args:
            snapshot: The snapshot to analyze
            request: Optional audit request with thresholds
            
        Returns:
            Tuple of (results_dict, list_of_findings)
        """
        start_time = time.time()
        findings: List[AuditFinding] = []
        
        # Detect low confidence findings
        self._detect_low_confidence(snapshot, findings)
        
        # Detect high uncertainty findings
        self._detect_high_uncertainty(snapshot, findings)
        
        # Detect stale perception
        self._detect_stale_perception(snapshot, findings)
        
        # Detect missing modalities
        self._detect_missing_modalities(snapshot, findings)
        
        # Detect inconsistent modalities
        self._detect_inconsistent_modalities(snapshot, findings)
        
        duration_ms = (time.time() - start_time) * 1000
        
        results = {
            "findings_count": len(findings),
            "detection_duration_ms": duration_ms,
        }
        
        return results, findings
    
    def _detect_low_confidence(
        self,
        snapshot: PerceptionSnapshot,
        findings: List[AuditFinding],
    ) -> None:
        """Detect low confidence issues."""
        # Visual confidence
        if snapshot.visual_confidence < self._confidence_threshold:
            severity = AuditSeverity.HIGH if snapshot.visual_confidence < 0.5 else AuditSeverity.MEDIUM
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.LOW_CONFIDENCE.value,
                severity=severity.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected="visual",
                description=f"Visual confidence {snapshot.visual_confidence:.2f} is below threshold {self._confidence_threshold}",
                provenance={"detector": "FindingDetector", "dimension": "confidentiality"},
            ))
        
        # Audio confidence
        if snapshot.audio_confidence < self._confidence_threshold:
            severity = AuditSeverity.HIGH if snapshot.audio_confidence < 0.5 else AuditSeverity.MEDIUM
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.LOW_CONFIDENCE.value,
                severity=severity.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected="audio",
                description=f"Audio confidence {snapshot.audio_confidence:.2f} is below threshold {self._confidence_threshold}",
                provenance={"detector": "FindingDetector", "dimension": "confidentiality"},
            ))
        
        # OCR confidence
        if snapshot.ocr_confidence < self._confidence_threshold:
            severity = AuditSeverity.HIGH if snapshot.ocr_confidence < 0.5 else AuditSeverity.MEDIUM
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.LOW_CONFIDENCE.value,
                severity=severity.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected="ocr",
                description=f"OCR confidence {snapshot.ocr_confidence:.2f} is below threshold {self._confidence_threshold}",
                provenance={"detector": "FindingDetector", "dimension": "confidentiality"},
            ))
    
    def _detect_high_uncertainty(
        self,
        snapshot: PerceptionSnapshot,
        findings: List[AuditFinding],
    ) -> None:
        """Detect high uncertainty issues."""
        if snapshot.uncertainty > self._uncertainty_threshold:
            severity = AuditSeverity.HIGH if snapshot.uncertainty > 0.6 else AuditSeverity.MEDIUM
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.HIGH_UNCERTAINTY.value,
                severity=severity.value,
                confidence=0.9,
                uncertainty=0.1,
                modality_affected=None,
                description=f"Overall uncertainty {snapshot.uncertainty:.2f} exceeds threshold {self._uncertainty_threshold}",
                provenance={"detector": "FindingDetector", "dimension": "uncertainty"},
            ))
    
    def _detect_stale_perception(
        self,
        snapshot: PerceptionSnapshot,
        findings: List[AuditFinding],
    ) -> None:
        """Detect stale perception issues."""
        current_time = time.time()
        age_seconds = current_time - snapshot.generation_timestamp_utc
        
        if age_seconds > self._staleness_seconds:
            severity = AuditSeverity.HIGH if age_seconds > self._staleness_seconds * 2 else AuditSeverity.MEDIUM
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.STALE_PERCEPTION.value,
                severity=severity.value,
                confidence=0.95,
                uncertainty=0.05,
                modality_affected=None,
                description=f"Perception data is {age_seconds:.1f} seconds old (threshold: {self._staleness_seconds}s)",
                provenance={"detector": "FindingDetector", "dimension": "freshness"},
            ))
    
    def _detect_missing_modalities(
        self,
        snapshot: PerceptionSnapshot,
        findings: List[AuditFinding],
    ) -> None:
        """Detect missing modality issues."""
        expected_modalities = ["visual", "audio", "ocr"]
        
        for modality in expected_modalities:
            confidence = getattr(snapshot, f"{modality}_confidence", 0)
            if confidence == 0:
                findings.append(AuditFinding(
                    finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                    finding_type=FindingType.MISSING_MODALITY.value,
                    severity=AuditSeverity.HIGH.value,
                    confidence=0.9,
                    uncertainty=0.1,
                    modality_affected=modality,
                    description=f"{modality} modality has zero confidence - data may be missing",
                    provenance={"detector": "FindingDetector", "dimension": "coverage"},
                ))
    
    def _detect_inconsistent_modalities(
        self,
        snapshot: PerceptionSnapshot,
        findings: List[AuditFinding],
    ) -> None:
        """Detect inconsistency issues between modalities."""
        confidences = [
            snapshot.visual_confidence,
            snapshot.audio_confidence,
            snapshot.ocr_confidence,
        ]
        
        # Check for significant confidence differences
        max_diff = 0
        for i in range(len(confidences)):
            for j in range(i + 1, len(confidences)):
                diff = abs(confidences[i] - confidences[j])
                max_diff = max(max_diff, diff)
        
        if max_diff > 0.4:
            findings.append(AuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                finding_type=FindingType.INCONSISTENT_MODALITIES.value,
                severity=AuditSeverity.MEDIUM.value,
                confidence=0.85,
                uncertainty=0.15,
                modality_affected=None,
                description=f"Significant confidence differences between modalities (max diff: {max_diff:.2f})",
                provenance={"detector": "FindingDetector", "dimension": "consistency"},
            ))


__all__ = [
    "FindingDetector",
    "FindingDetectionResult",
]