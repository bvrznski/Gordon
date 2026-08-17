# Knowledge Governance - Phase 6.1
# ================================

"""
Knowledge Governance: Semantic integrity evaluation in Gordon's knowledge system.

Governance evaluates semantic integrity and produces findings about:
    * Identity uniqueness
    * Revision consistency  
    * Provenance completeness
    * Compatibility consistency
    * Scope consistency
    * Authority consistency
    
Governance is read-only - it never modifies artifacts, only observes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# GOVERNANCE FINDING TYPES - Evaluation categories
# =============================================================================


class GovernanceFindingKind(Enum):
    """
    Kinds of governance findings.
    
    Categories of issues that governance can identify:
        IDENTITY_ISSUE       -> Problems with semantic identity
        REVISION_ISSUE       -> Problems with revision history  
        PROVENANCE_ISSUE     -> Problems with provenance trail
        COMPATIBILITY_ISSUE  -> Problems with compatibility evaluation
        SCOPE_ISSUE          -> Problems with scope definition
        AUTHORITY_ISSUE      -> Problems with authority assignment
    """
    
    IDENTITY_ISSUE = "identity_issue"
    REVISION_ISSUE = "revision_issue"
    PROVENANCE_ISSUE = "provenance_issue"
    COMPATIBILITY_ISSUE = "compatibility_issue"
    SCOPE_ISSUE = "scope_issue"
    AUTHORITY_ISSUE = "authority_issue"


# =============================================================================
# GOVERNANCE FINDING - Individual finding record
# =============================================================================


@dataclass(frozen=True)
class GovernanceFinding:
    """
    Individual governance finding.
    
    Records a specific issue detected during semantic integrity evaluation.
    
    Fields:
        finding_identity:      Unique identifier for this finding
        finding_kind:          Category of issue detected
        affected_artifacts:    IDs of artifacts involved
        severity:              How serious the finding is (low/medium/high)
        explanation:           Description of the issue
        recommendation:        How to fix it
        timestamp_utc:         When finding was made
    """
    
    # Identity and metadata (required)
    finding_identity: str                 # Unique finding ID
    
    finding_kind: GovernanceFindingKind   # Category of issue
    
    affected_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Affected IDs
    
    severity: str = "low"                 # low/medium/high
    explanation: Optional[str] = None     # Issue description
    recommendation: Optional[str] = None  # Fix suggestion
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_critical(self) -> bool:
        """Check if finding is critical."""
        return self.severity == "critical"
    
    @property
    def is_valid(self) -> bool:
        """Check if finding has valid data."""
        return (
            len(self.finding_identity) > 0 and
            self.finding_kind != GovernanceFindingKind.IDENTITY_ISSUE or len(self.affected_artifacts) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary for serialization."""
        return {
            "finding_identity": self.finding_identity,
            "finding_kind": self.finding_kind.value,
            "affected_artifacts": list(self.affected_artifacts),
            "severity": self.severity,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
            "timestamp_utc": self.timestamp_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceFinding":
        """Create finding from dictionary."""
        return cls(
            finding_identity=data.get("finding_identity", str(uuid.uuid4())),
            finding_kind=GovernanceFindingKind(data.get("finding_kind", "identity_issue")),
            affected_artifacts=tuple(data.get("affected_artifacts", [])),
            severity=data.get("severity", "low"),
            explanation=data.get("explanation"),
            recommendation=data.get("recommendation"),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
        )


# =============================================================================
# GOVERNANCE EVALUATION - Complete evaluation result
# =============================================================================


@dataclass(frozen=True)
class GovernanceEvaluation:
    """
    Complete governance evaluation of semantic integrity.
    
    Aggregates all findings into a comprehensive assessment.
    
    Fields:
        evaluation_identity:  Unique identifier for this evaluation
        evaluation_scope:     What was evaluated (artifact, revision, system-wide)
        findings:             All findings from the evaluation
        violations:           Critical issues that violate rules
        recommendations:      Suggested actions
        timestamp_utc:        When evaluation completed
    """
    
    # Identity and metadata (required)
    evaluation_identity: str              # Unique evaluation ID
    
    evaluation_scope: str = "system"      # Artifact/Revision/System
    
    findings: Tuple[GovernanceFinding, ...] = field(default_factory=tuple)  # All findings
    violations: Tuple[str, ...] = field(default_factory=tuple)             # Rule violations
    recommendations: Tuple[str, ...] = field(default_factory=tuple)        # Suggestions
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def finding_count(self) -> int:
        """Get total number of findings."""
        return len(self.findings)
    
    @property
    def violation_count(self) -> int:
        """Get count of violations."""
        return len(self.violations)
    
    @property
    def is_valid(self) -> bool:
        """Check if evaluation has valid data."""
        return len(self.evaluation_identity) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation to dictionary for serialization."""
        return {
            "evaluation_identity": self.evaluation_identity,
            "evaluation_scope": self.evaluation_scope,
            "findings": [f.to_dict() for f in self.findings],
            "violation_count": len(self.violations),
            "recommendations": list(self.recommendations),
            "timestamp_utc": self.timestamp_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceEvaluation":
        """Create evaluation from dictionary."""
        findings = []
        for f_data in data.get("findings", []):
            findings.append(GovernanceFinding.from_dict(f_data))
        
        return cls(
            evaluation_identity=data.get("evaluation_identity", str(uuid.uuid4())),
            evaluation_scope=data.get("evaluation_scope", "system"),
            findings=tuple(findings),
            violations=tuple(data.get("violations", [])),
            recommendations=tuple(data.get("recommendations", [])),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
        )


# =============================================================================
# GOVERNANCE ENGINE - Integrity evaluation
# =============================================================================


class GovernanceEngine:
    """
    Engine for evaluating semantic integrity.
    
    Performs read-only governance checks on knowledge artifacts without
    modifying them. Produces detailed findings for inspection and action.
    """
    
    def __init__(
        self,
        check_identity_uniqueness: bool = True,
        check_revision_consistency: bool = True,
        check_provenance_completeness: bool = True,
    ):
        """
        Initialize the governance engine.
        
        Args:
            check_identity_uniqueness: Whether to check for duplicate identities
            check_revision_consistency: Whether to verify revision lineage
            check_provenance_completeness: Whether to validate provenance chains
        """
        self._check_identity = check_identity_uniqueness
        self._check_revisions = check_revision_consistency
        self._check_provenance = check_provenance_completeness
    
    def evaluate_artifact(
        self,
        artifact_data: Dict[str, Any],
    ) -> Tuple[bool, List[GovernanceFinding]]:
        """
        Evaluate a single artifact for governance compliance.
        
        Args:
            artifact_data: Artifact to evaluate
            
        Returns:
            (is_valid, list_of_findings)
        """
        findings = []
        
        # Check identity
        if self._check_identity:
            semantic_id = artifact_data.get("semantic_identity", "")
            if not semantic_id or len(semantic_id) == 0:
                findings.append(GovernanceFinding(
                    finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
                    finding_kind=GovernanceFindingKind.IDENTITY_ISSUE,
                    affected_artifacts=(artifact_data.get("semantic_identity", "unknown"),),
                    severity="high",
                    explanation="Artifact missing semantic identity",
                    recommendation="Assign unique semantic identity using proper prefix format",
                ))
        
        # Check revision consistency
        if self._check_revisions:
            revision = artifact_data.get("semantic_revision")
            if revision is not None and not isinstance(revision, int):
                findings.append(GovernanceFinding(
                    finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
                    finding_kind=GovernanceFindingKind.REVISION_ISSUE,
                    affected_artifacts=(artifact_data.get("semantic_identity", "unknown"),),
                    severity="medium",
                    explanation="Revision must be an integer value",
                    recommendation="Ensure semantic_revision is a valid positive integer",
                ))
        
        # Check provenance completeness
        if self._check_provenance:
            provenance = artifact_data.get("semantic_provenance")
            if isinstance(provenance, (list, tuple)) and len(provenance) == 0:
                findings.append(GovernanceFinding(
                    finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
                    finding_kind=GovernanceFindingKind.PROVENANCE_ISSUE,
                    affected_artifacts=(artifact_data.get("semantic_identity", "unknown"),),
                    severity="low",
                    explanation="Artifact has empty provenance trail",
                    recommendation="Add provenance record documenting artifact origin",
                ))
        
        return len(findings) == 0, findings
    
    def evaluate_artifact_set(
        self,
        artifact_datas: List[Dict[str, Any]],
    ) -> Tuple[bool, GovernanceEvaluation]:
        """
        Evaluate multiple artifacts for governance compliance.
        
        Args:
            artifact_datas: List of artifacts to evaluate
            
        Returns:
            (is_valid, evaluation_result)
        """
        all_findings = []
        
        # Track identities for uniqueness check
        seen_identities = set()
        
        for i, data in enumerate(artifact_datas):
            is_valid, findings = self.evaluate_artifact(data)
            
            if not is_valid:
                all_findings.extend(findings)
                
                # Check for duplicate identity
                semantic_id = data.get("semantic_identity", "")
                if self._check_identity and semantic_id in seen_identities:
                    all_findings.append(GovernanceFinding(
                        finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
                        finding_kind=GovernanceFindingKind.IDENTITY_ISSUE,
                        affected_artifacts=(semantic_id,),
                        severity="critical",
                        explanation=f"Duplicate semantic identity detected: {semantic_id}",
                        recommendation="Resolve duplicate identities - ensure each artifact has unique identity",
                    ))
                else:
                    seen_identities.add(semantic_id)
        
        evaluation = GovernanceEvaluation(
            evaluation_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluation_scope="artifact_set",
            findings=tuple(all_findings),
            timestamp_utc=time.time(),
        )
        
        return len([f for f in all_findings if f.severity == "critical"]) == 0, evaluation
    
    def evaluate_artifact_integrity(
        self,
        artifact_data: Dict[str, Any],
    ) -> Tuple[bool, List[GovernanceFinding]]:
        """
        Evaluate internal integrity of an artifact.
        
        Checks that required fields are present and properly formatted.
        
        Args:
            artifact_data: Artifact to evaluate
            
        Returns:
            (is_valid, list_of_findings)
        """
        findings = []
        
        required_fields = [
            "semantic_identity",
            "semantic_authority", 
            "semantic_scope",
            "semantic_revision",
        ]
        
        for field_name in required_fields:
            value = artifact_data.get(field_name)
            if not self._is_valid_field(value, field_name):
                findings.append(GovernanceFinding(
                    finding_identity=f"finding:{uuid.uuid4().hex[:16]}",
                    finding_kind=GovernanceFindingKind.IDENTITY_ISSUE,
                    affected_artifacts=(artifact_data.get("semantic_identity", "unknown"),),
                    severity="high",
                    explanation=f"Required field missing or invalid: {field_name}",
                    recommendation=f"Ensure '{field_name}' is properly populated",
                ))
        
        return len(findings) == 0, findings
    
    def _is_valid_field(
        self,
        value: Any,
        field_name: str,
    ) -> bool:
        """Check if a field has valid data."""
        if value is None:
            return False
        
        # String fields must not be empty
        if isinstance(value, str):
            return len(value.strip()) > 0
        
        # List/tuple fields must have items
        if isinstance(value, (list, tuple)):
            return len(value) > 0
        
        # Dict fields must have content
        if isinstance(value, dict):
            return len(value) > 0
        
        # Other types are valid if not None
        return True


__all__ = [
    # Finding categories
    "GovernanceFindingKind",
    # Record types
    "GovernanceFinding",
    "GovernanceEvaluation",
    # Engine
    "GovernanceEngine",
]