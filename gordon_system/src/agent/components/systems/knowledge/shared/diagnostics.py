# Knowledge Diagnostics - Phase 5.4
# ==================================

"""
Knowledge Diagnostics: Diagnostic services for knowledge artifacts.

Diagnostics provide in-depth analysis of semantic artifacts, identifying issues,
patterns, and potential improvements to the knowledge base.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# DIAGNOSTIC FINDING - A single diagnostic observation
# =============================================================================


@dataclass(frozen=True)
class DiagnosticFinding:
    """
    A single finding from diagnostic analysis.
    
    Fields:
        finding_identity:      Unique identifier for this finding
        category:              Category of the issue (e.g., "consistency", "completeness")
        severity:              Severity level ("error", "warning", "info")
        message:               Human-readable description of the finding
        artifact_reference:    Reference to the affected artifact
        suggested_action:      Recommended action to resolve
    """
    
    finding_identity: str             # Unique ID for this finding
    
    category: str = ""                # e.g., "consistency", "completeness"
    severity: str = "info"            # error, warning, info
    
    message: str = ""                 # Human-readable description
    artifact_reference: str = ""      # Reference to affected artifact
    suggested_action: str = ""        # How to fix


# =============================================================================
# DIAGNOSTIC REPORT - Complete diagnostic analysis report
# =============================================================================


@dataclass(frozen=True)
class KnowledgeDiagnosticReport:
    """
    Complete diagnostic report for the knowledge system.
    
    Fields:
        report_identity:       Unique identifier for this report
        timestamp_utc:         When diagnostics were run
        artifact_type:         Type of artifact analyzed
        artifact_count:        Number of artifacts analyzed
        findings:              List of all diagnostic findings
        summary:               Summary statistics
    """
    
    # Identity and metadata (required)
    report_identity: str              # Unique ID for this report
    
    timestamp_utc: float              # When diagnostics were run
    
    artifact_type: str = "general"    # e.g., "concept", "belief", "relation"
    artifact_count: int = 0
    
    findings: Tuple[DiagnosticFinding, ...] = field(default_factory=tuple)
    
    summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def error_count(self) -> int:
        """Count of error-level findings."""
        return sum(1 for f in self.findings if f.severity == "error")
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level findings."""
        return sum(1 for f in self.findings if f.severity == "warning")
    
    @property
    def info_count(self) -> int:
        """Count of info-level findings."""
        return sum(1 for f in self.findings if f.severity == "info")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "report_identity": self.report_identity,
            "timestamp_utc": self.timestamp_utc,
            "artifact_type": self.artifact_type,
            "artifact_count": self.artifact_count,
            "findings": [
                {
                    "finding_identity": f.finding_identity,
                    "category": f.category,
                    "severity": f.severity,
                    "message": f.message,
                    "artifact_reference": f.artifact_reference,
                    "suggested_action": f.suggested_action,
                }
                for f in self.findings
            ],
            "summary": dict(self.summary),
        }


# =============================================================================
# DIAGNOSTIC ENGINE
# =============================================================================


class KnowledgeDiagnosticsEngine:
    """
    Performs diagnostics on Gordon's knowledge system.
    
    Provides comprehensive diagnostic services for evaluating semantic integrity.
    """
    
    def __init__(
        self,
        check_consistency: bool = True,
        check_completeness: bool = True,
        check_circularity: bool = True,
    ):
        """
        Initialize the diagnostics engine.
        
        Args:
            check_consistency: Check for logical consistency
            check_completeness: Check for missing data
            check_circularity: Check for circular references
        """
        self._check_consistency = check_consistency
        self._check_completeness = check_completeness
        self._check_circularity = check_circularity
    
    def run_diagnostics(
        self,
        artifact_type: str,
        artifacts_data: List[Dict[str, Any]],
    ) -> KnowledgeDiagnosticReport:
        """
        Run diagnostics on a collection of artifacts.
        
        Args:
            artifact_type: Type of artifacts being analyzed
            artifacts_data: List of artifact data dictionaries
            
        Returns:
            Diagnostic report with findings
        """
        findings = []
        
        # Perform consistency check
        if self._check_consistency:
            for i, artifact in enumerate(artifacts_data):
                identity = artifact.get("identity", f"artifact_{i}")
                
                confidence = artifact.get("confidence", 0.5)
                uncertainty = artifact.get("uncertainty", 0.5)
                total = confidence + uncertainty
                
                if not (0.8 <= total <= 1.2):
                    findings.append(DiagnosticFinding(
                        finding_identity=f"finding:{uuid.uuid4().hex[:8]}",
                        category="consistency",
                        severity="warning",
                        message=(
                            f"Confidence-uncertainty imbalance: {total:.2f} "
                            f"(expected ~1.0)"
                        ),
                        artifact_reference=identity,
                        suggested_action="Review evidence quality and update confidence/uncertainty",
                    ))
        
        # Perform completeness check
        if self._check_completeness:
            for i, artifact in enumerate(artifacts_data):
                identity = artifact.get("identity", f"artifact_{i}")
                
                required_fields = ["statement"] if "statement" in str(artifact) else []
                missing = [f for f in required_fields if not artifact.get(f)]
                
                for field_name in missing:
                    findings.append(DiagnosticFinding(
                        finding_identity=f"finding:{uuid.uuid4().hex[:8]}",
                        category="completeness",
                        severity="error",
                        message=f"Missing required field: {field_name}",
                        artifact_reference=identity,
                        suggested_action=f"Add {field_name} to the artifact",
                    ))
        
        # Perform circularity check
        if self._check_circularity:
            # Simplified - would need graph structure in practice
            pass
        
        return KnowledgeDiagnosticReport(
            report_identity=f"diagnostic:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            artifact_type=artifact_type,
            artifact_count=len(artifacts_data),
            findings=tuple(findings),
            summary={
                "errors": len([f for f in findings if f.severity == "error"]),
                "warnings": len([f for f in findings if f.severity == "warning"]),
                "info": len([f for f in findings if f.severity == "info"]),
            },
        )


__all__ = [
    "DiagnosticFinding",
    "KnowledgeDiagnosticReport",
    "KnowledgeDiagnosticsEngine",
]