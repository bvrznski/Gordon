# Knowledge Audit Interfaces - Phase 6.10
# ========================================

"""
Interfaces and base classes for the Knowledge Audit subsystem.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Tuple,
    Optional,
    Any,
    Callable,
    Iterator,
)

# Import core knowledge models using relative imports
from ..shared.assertion import KnowledgeAssertion, AssertionState
from ..shared.belief import KnowledgeBelief, BeliefState
from ..shared.evidence import KnowledgeEvidence, EvidenceKind
from ..shared.concept import KnowledgeConcept
from ..shared.relation import KnowledgeRelation


# =============================================================================
# KNOWLEDGE ARTIFACT PROVIDER - Interface for accessing knowledge artifacts
# =============================================================================

class KnowledgeArtifactProvider(ABC):
    """
    Interface for providing access to knowledge artifacts during audit.
    
    Audit engines use this interface to retrieve and analyze artifacts
    without knowing the underlying storage mechanism.
    """
    
    @abstractmethod
    def get_assertion(self, assertion_id: str) -> Optional[KnowledgeAssertion]:
        """Retrieve an assertion by its ID."""
        pass
    
    @abstractmethod
    def get_belief(self, belief_id: str) -> Optional[KnowledgeBelief]:
        """Retrieve a belief by its ID."""
        pass
    
    @abstractmethod
    def get_evidence(self, evidence_id: str) -> Optional[KnowledgeEvidence]:
        """Retrieve evidence by its ID."""
        pass
    
    @abstractmethod
    def get_concept(self, concept_id: str) -> Optional[KnowledgeConcept]:
        """Retrieve a concept by its ID."""
        pass
    
    @abstractmethod
    def get_relation(self, relation_id: str) -> Optional[KnowledgeRelation]:
        """Retrieve a relation by its ID."""
        pass
    
    @abstractmethod
    def list_assertions(self, limit: int = 100) -> List[KnowledgeAssertion]:
        """List assertions with optional limit."""
        pass
    
    @abstractmethod
    def list_beliefs(self, limit: int = 100) -> List[KnowledgeBelief]:
        """List beliefs with optional limit."""
        pass
    
    @abstractmethod
    def filter_by_state(
        self,
        artifact_type: str,
        states: List[str],
    ) -> Iterator[Any]:
        """Filter artifacts by state(s)."""
        pass


# =============================================================================
# KNOWLEDGE AUDIT ENGINE - Core audit interface
# =============================================================================

class KnowledgeAuditEngine(ABC):
    """
    Interface for knowledge audit engines.
    
    Each engine audits one dimension of knowledge quality:
        - consistency
        - contradiction
        - redundancy
        - evidence
        - provenance
        - freshness
        - coverage
        - dependency
        - usage
        - confidence
        - uncertainty
        - completeness
        - integrity
    
    Engines are independently executable and produce findings for a given target.
    """
    
    # Unique engine identifier (matches AuditDimension)
    dimension: str = "unknown"
    
    def __init__(
        self,
        *,
        configuration: Dict[str, Any] | None = None,
        artifact_provider: Optional[KnowledgeArtifactProvider] = None,
    ):
        """
        Initialize the audit engine.
        
        Args:
            configuration: Engine-specific configuration parameters
            artifact_provider: Provider for accessing knowledge artifacts
        """
        self.configuration = configuration or {}
        self.artifact_provider = artifact_provider
        self._engine_id = f"engine:{uuid.uuid4().hex[:16]}"
    
    @property
    def engine_id(self) -> str:
        """Get the unique engine ID."""
        return self._engine_id
    
    @abstractmethod
    def audit(
        self,
        target: KnowledgeAuditTarget,
    ) -> List[KnowledgeAuditFinding]:
        """
        Perform audit on a single target.
        
        Args:
            target: The knowledge artifact to audit
            
        Returns:
            List of findings for this audit (empty if no issues found)
        """
        pass
    
    @abstractmethod
    def batch_audit(
        self,
        targets: List[KnowledgeAuditTarget],
    ) -> Dict[str, List[KnowledgeAuditFinding]]:
        """
        Perform batch audit on multiple targets.
        
        Args:
            targets: List of knowledge artifacts to audit
            
        Returns:
            Mapping from target ID to list of findings
        """
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.configuration.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.configuration[key] = value


# =============================================================================
# AUDIT SESSION HANDLER - Manages audit sessions
# =============================================================================

class KnowledgeAuditSessionHandler(ABC):
    """
    Interface for managing audit sessions.
    
    Handles creation, tracking, and completion of audit sessions.
    """
    
    @abstractmethod
    def create_session(
        self,
        request: KnowledgeAuditRequest,
    ) -> KnowledgeAuditSession:
        """
        Create a new audit session from a request.
        
        Args:
            request: The audit request to base the session on
            
        Returns:
            New audit session in PENDING state
        """
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[KnowledgeAuditSession]:
        """Get an existing audit session by ID."""
        pass
    
    @abstractmethod
    def start_session(self, session_id: str) -> None:
        """Start an audit session."""
        pass
    
    @abstractmethod
    def complete_session(
        self,
        session_id: str,
        report: KnowledgeAuditReport,
    ) -> None:
        """
        Mark a session as completed with its final report.
        
        Args:
            session_id: ID of the session to complete
            report: The audit report produced by the session
        """
        pass
    
    @abstractmethod
    def fail_session(
        self,
        session_id: str,
        error: KnowledgeAuditError,
    ) -> None:
        """
        Mark a session as failed.
        
        Args:
            session_id: ID of the session to mark as failed
            error: The error that caused the failure
        """
        pass
    
    @abstractmethod
    def cancel_session(self, session_id: str) -> None:
        """Cancel an active audit session."""
        pass


# =============================================================================
# AUDIT REPORT GENERATOR - Generates final reports
# =============================================================================

class AuditReportGenerator(ABC):
    """
    Interface for generating final audit reports from findings.
    
    Aggregates findings and produces comprehensive reports with metrics.
    """
    
    @abstractmethod
    def generate_report(
        self,
        session: KnowledgeAuditSession,
        all_findings: Dict[str, List[KnowledgeAuditFinding]],
        health_metrics: KnowledgeHealth,
    ) -> KnowledgeAuditReport:
        """
        Generate a final audit report.
        
        Args:
            session: The completed audit session
            all_findings: Mapping from target ID to its findings
            health_metrics: Computed health metrics
            
        Returns:
            Complete audit report
        """
        pass
    
    @abstractmethod
    def compute_health(
        self,
        all_findings: Dict[str, List[KnowledgeAuditFinding]],
        targets_count: int,
    ) -> KnowledgeHealth:
        """
        Compute overall health metrics from findings.
        
        Args:
            all_findings: Mapping from target ID to its findings
            targets_count: Total number of targets audited
            
        Returns:
            Computed health metrics
        """
        pass


# =============================================================================
# AUDIT SESSION - Active audit execution context
# =============================================================================

@dataclass(frozen=True)
class KnowledgeAuditSession:
    """
    Represents an active or completed audit session.
    
    A session encapsulates:
        - The original request
        - All targets to be audited
        - Execution state and timing
        - Final report (if completed)
    """
    
    # Identity
    session_id: str                       # Unique session identifier
    
    # Request context
    request_id: str                       # Original request ID
    audit_request: KnowledgeAuditRequest  # The original request
    
    # Targets to audit
    target_ids: Tuple[str, ...]           # IDs of all targets
    target_types: Dict[str, str]          # target_id -> type mapping
    
    # Execution state
    status: AuditStatus                   # Current session status
    started_at_utc: float = 0.0           # When audit started (0 if not started)
    completed_at_utc: float = 0.0         # When audit completed (0 if not completed)
    
    # Results
    findings: Dict[str, Tuple[KnowledgeAuditFinding, ...]] = field(default_factory=dict)  # target_id -> findings
    report: Optional[KnowledgeAuditReport] = None  # Final report if completed
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently running."""
        return self.status == AuditStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """Check if session completed successfully."""
        return self.status == AuditStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if session failed."""
        return self.status in (AuditStatus.FAILED, AuditStatus.TIMEOUT, AuditStatus.CANCELLED)
    
    @classmethod
    def create_pending(
        cls,
        request: KnowledgeAuditRequest,
        target_ids: List[str],
        target_types: Dict[str, str],
    ) -> "KnowledgeAuditSession":
        """
        Create a new pending audit session.
        
        Args:
            request: The audit request
            target_ids: List of target artifact IDs to audit
            target_types: Mapping from ID to type
            
        Returns:
            New session in PENDING state
        """
        return cls(
            session_id=f"session:{uuid.uuid4().hex[:16]}",
            request_id=request.request_id,
            audit_request=request,
            target_ids=tuple(target_ids),
            target_types=dict(target_types),
            status=AuditStatus.PENDING,
            started_at_utc=0.0,
            completed_at_utc=0.0,
            findings={},
        )


# =============================================================================
# AUDIT REQUEST - Request to perform an audit
# =============================================================================

@dataclass(frozen=True)
class KnowledgeAuditRequest:
    """
    Represents a request to perform knowledge audit.
    
    Specifies what, when, and how to audit knowledge artifacts.
    """
    
    # Identity
    request_id: str                       # Unique request identifier
    
    # What to audit
    target_ids: Tuple[str, ...]           # Specific IDs to audit (empty = all)
    target_types: Tuple[str, ...] = ()    # Filter by types (empty = all)
    
    # Which dimensions to audit
    dimensions: Tuple[AuditDimension, ...] = field(default_factory=tuple)  # All if empty
    
    # Configuration
    timeout_seconds: int = DEFAULT_SESSION_TIMEOUT_SECONDS
    include_recommendations: bool = True
    generate_report: bool = True
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    created_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate request after creation."""
        if self.timeout_seconds < 1:
            raise InvalidAuditRequest(
                "Timeout must be at least 1 second",
                invalid_fields={"timeout_seconds": self.timeout_seconds},
            )
        if len(self.target_ids) > MAX_AUDIT_TARGETS_PER_REQUEST:
            raise InvalidAuditRequest(
                f"Too many targets (max {MAX_AUDIT_TARGETS_PER_REQUEST})",
                invalid_fields={"target_count": len(self.target_ids)},
            )
    
    @classmethod
    def create_all(cls, context: Optional[Dict[str, Any]] = None) -> "KnowledgeAuditRequest":
        """Create a request to audit all knowledge."""
        return cls(
            request_id=f"request:{uuid.uuid4().hex[:16]}",
            target_ids=(),
            dimensions=(),  # Empty = all dimensions
            context=context or {},
        )
    
    @classmethod
    def create_for_targets(
        cls,
        target_ids: List[str],
        dimensions: Optional[List[AuditDimension]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeAuditRequest":
        """
        Create a request to audit specific targets.
        
        Args:
            target_ids: IDs of artifacts to audit
            dimensions: Dimensions to audit (empty = all)
            context: Optional context information
        """
        return cls(
            request_id=f"request:{uuid.uuid4().hex[:16]}",
            target_ids=tuple(target_ids),
            dimensions=tuple(dimensions or []),
            context=context or {},
        )


# =============================================================================
# AUDIT FINDING - A single audit observation
# =============================================================================

@dataclass(frozen=True)
class KnowledgeAuditFinding:
    """
    Represents a single finding from an audit engine.
    
    A finding documents:
        - What was observed about a target
        - Why it matters (the issue type)
        - Supporting evidence
        - Recommended action
    """
    
    # Identity
    finding_id: str                       # Unique finding identifier
    
    # Target context
    target_id: str                        # ID of audited artifact
    target_type: str                      # Type of artifact
    
    # Finding details
    finding_type: FindingType             # What type of issue was found?
    
    # Assessment
    severity: float = 0.5                 # Severity (0.0-1.0)
    confidence: float = 0.5               # Confidence in the finding itself
    uncertainty: float = 0.5              # Uncertainty about the finding
    
    # Evidence for the finding
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)  # Supporting evidence IDs
    supporting_context: Dict[str, Any] = field(default_factory=dict)
    
    # Recommendation (if applicable)
    recommendation: Optional[KnowledgeAuditRecommendation] = None
    
    # Timing
    detected_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_critical(self) -> bool:
        """Check if this finding is critical."""
        return self.severity >= 0.8
    
    @property
    def is_warning(self) -> bool:
        """Check if this finding is a warning."""
        return 0.3 <= self.severity < 0.8
    
    @property
    def is_info(self) -> bool:
        """Check if this finding is informational."""
        return self.severity < 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary for serialization."""
        return {
            "finding_id": self.finding_id,
            "target_id": self.target_id,
            "target_type": self.target_type,
            "finding_type": self.finding_type.value if self.finding_type else None,
            "severity": self.severity,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "evidence_references": list(self.evidence_references),
            "supporting_context": dict(self.supporting_context),
            "recommendation": self.recommendation.to_dict() if self.recommendation else None,
            "detected_at_utc": self.detected_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAuditFinding":
        """Create finding from dictionary."""
        finding_type_value = data.get("finding_type", "unknown")
        try:
            finding_type = FindingType(finding_type_value)
        except ValueError:
            finding_type = FindingType.UNSUPPORTED
        
        recommendation_data = data.get("recommendation")
        recommendation = None
        if recommendation_data:
            recommendation = KnowledgeAuditRecommendation.from_dict(recommendation_data)
        
        return cls(
            finding_id=data.get("finding_id", str(uuid.uuid4())),
            target_id=data.get("target_id", ""),
            target_type=data.get("target_type", "unknown"),
            finding_type=finding_type,
            severity=float(data.get("severity", 0.5)),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            evidence_references=tuple(data.get("evidence_references", [])),
            supporting_context=dict(data.get("supporting_context", {})),
            recommendation=recommendation,
            detected_at_utc=float(data.get("detected_at_utc", time.time())),
        )


# =============================================================================
# AUDIT RECOMMENDATION - Suggested action for a finding
# =============================================================================

@dataclass(frozen=True)
class KnowledgeAuditRecommendation:
    """
    Represents a recommended action to address an audit finding.
    
    Recommendations never directly modify knowledge;
    they are requests that other subsystems may act on.
    """
    
    # Identity
    recommendation_id: str                # Unique identifier
    
    # What is recommended
    recommendation_type: RecommendationType  # Type of action requested
    
    # Details
    rationale: str = ""                   # Why this recommendation?
    priority: float = 0.5                 # Priority (0.0-1.0)
    
    # Required context
    required_context: Dict[str, Any] = field(default_factory=dict)
    
    # Optional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type.value if self.recommendation_type else None,
            "rationale": self.rationale,
            "priority": self.priority,
            "required_context": dict(self.required_context),
            "metadata": dict(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAuditRecommendation":
        """Create recommendation from dictionary."""
        rec_type_value = data.get("recommendation_type", "verify")
        try:
            recommendation_type = RecommendationType(rec_type_value)
        except ValueError:
            recommendation_type = RecommendationType.VERIFY
        
        return cls(
            recommendation_id=data.get("recommendation_id", str(uuid.uuid4())),
            recommendation_type=recommendation_type,
            rationale=data.get("rationale", ""),
            priority=float(data.get("priority", 0.5)),
            required_context=dict(data.get("required_context", {})),
            metadata=dict(data.get("metadata", {})),
        )


# =============================================================================
# AUDIT REPORT - Complete audit results
# =============================================================================

@dataclass(frozen=True)
class KnowledgeAuditReport:
    """
    Represents the complete results of an audit session.
    
    An audit report includes:
        - Session metadata
        - All findings organized by target
        - Health metrics
        - Summary statistics
        - Recommendations
    """
    
    # Identity and session info
    report_id: str                        # Unique report identifier
    session_id: str                       # Source session ID
    
    # Metadata
    created_at_utc: float                 # When report was generated
    audit_dimensions: Tuple[str, ...]     # Dimensions audited
    total_targets: int                    # Number of targets audited
    
    # Findings
    all_findings: Tuple[KnowledgeAuditFinding, ...]  # All findings
    
    # Health metrics
    health_metrics: KnowledgeHealth       # Overall health assessment
    
    # Summary statistics
    summary: Dict[str, Any]               # Aggregated statistics
    
    @property
    def finding_count(self) -> int:
        """Total number of findings."""
        return len(self.all_findings)
    
    @property
    def critical_finding_count(self) -> int:
        """Number of critical findings."""
        return sum(1 for f in self.all_findings if f.is_critical)
    
    @property
    def warning_finding_count(self) -> int:
        """Number of warning findings."""
        return sum(1 for f in self.all_findings if f.is_warning)
    
    @property
    def info_finding_count(self) -> int:
        """Number of informational findings."""
        return sum(1 for f in self.all_findings if f.is_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "created_at_utc": self.created_at_utc,
            "audit_dimensions": list(self.audit_dimensions),
            "total_targets": self.total_targets,
            "all_findings": [f.to_dict() for f in self.all_findings],
            "health_metrics": self.health_metrics.to_dict(),
            "summary": dict(self.summary),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAuditReport":
        """Create report from dictionary."""
        findings = []
        for f_data in data.get("all_findings", []):
            findings.append(KnowledgeAuditFinding.from_dict(f_data))
        
        health_data = data.get("health_metrics", {})
        health = KnowledgeHealth.from_dict(health_data) if health_data else None
        
        return cls(
            report_id=data.get("report_id", str(uuid.uuid4())),
            session_id=data.get("session_id", ""),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            audit_dimensions=tuple(data.get("audit_dimensions", [])),
            total_targets=int(data.get("total_targets", 0)),
            all_findings=tuple(findings),
            health_metrics=health or KnowledgeHealth.empty(),
            summary=dict(data.get("summary", {})),
        )


# =============================================================================
# HEALTH METRICS - Overall knowledge health assessment
# =============================================================================

@dataclass(frozen=True)
class KnowledgeHealth:
    """
    Represents overall health metrics for audited knowledge.
    
    Combines assessments from all audit dimensions into a cohesive health picture.
    """
    
    # Identity and timing
    health_id: str                        # Unique health identifier
    timestamp_utc: float                  # When assessed
    
    # Overall scores (0.0-1.0)
    overall_score: float = 0.5            # Combined health score
    coverage_score: float = 0.5           # Coverage completeness
    consistency_score: float = 0.5        # Logical consistency
    evidence_score: float = 0.5           # Evidence quality
    
    # Problem counts
    total_findings: int = 0               # Total findings count
    critical_count: int = 0               # Critical issues
    warning_count: int = 0                # Warnings
    info_count: int = 0                   # Informational findings
    
    # Dimension scores
    consistency_assessment: KnowledgeConsistencyAssessment | None = None
    coverage_assessment: KnowledgeCoverage | None = None
    freshness_assessment: KnowledgeFreshnessAssessment | None = None
    confidence_assessment: KnowledgeConfidenceAssessment | None = None
    
    @property
    def is_healthy(self) -> bool:
        """Check if overall health is acceptable."""
        return self.overall_score >= 0.7 and self.critical_count == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "health_id": self.health_id,
            "timestamp_utc": self.timestamp_utc,
            "overall_score": self.overall_score,
            "coverage_score": self.coverage_score,
            "consistency_score": self.consistency_score,
            "evidence_score": self.evidence_score,
            "total_findings": self.total_findings,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "consistency_assessment": self.consistency_assessment.to_dict() if self.consistency_assessment else None,
            "coverage_assessment": self.coverage_assessment.to_dict() if self.coverage_assessment else None,
            "freshness_assessment": self.freshness_assessment.to_dict() if self.freshness_assessment else None,
            "confidence_assessment": self.confidence_assessment.to_dict() if self.confidence_assessment else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeHealth":
        """Create health record from dictionary."""
        return cls(
            health_id=data.get("health_id", str(uuid.uuid4())),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            overall_score=float(data.get("overall_score", 0.5)),
            coverage_score=float(data.get("coverage_score", 0.5)),
            consistency_score=float(data.get("consistency_score", 0.5)),
            evidence_score=float(data.get("evidence_score", 0.5)),
            total_findings=int(data.get("total_findings", 0)),
            critical_count=int(data.get("critical_count", 0)),
            warning_count=int(data.get("warning_count", 0)),
            info_count=int(data.get("info_count", 0)),
        )
    
    @classmethod
    def empty(cls) -> "KnowledgeHealth":
        """Create an empty health record."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
        )


@dataclass(frozen=True)
class KnowledgeConsistencyAssessment:
    """Assessment of knowledge consistency."""
    
    consistency_id: str
    score: float = 0.5  # 0.0-1.0 (higher = more consistent)
    contradiction_count: int = 0
    conflict_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "consistency_id": self.consistency_id,
            "score": self.score,
            "contradiction_count": self.contradiction_count,
            "conflict_count": self.conflict_count,
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeConsistencyAssessment":
        return cls(consistency_id=f"consistency:{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class KnowledgeCoverageAssessment:
    """Assessment of knowledge coverage."""
    
    coverage_id: str
    score: float = 0.5  # 0.0-1.0 (higher = more complete)
    total_concepts: int = 0
    covered_concepts: int = 0
    missing_concepts: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coverage_id": self.coverage_id,
            "score": self.score,
            "total_concepts": self.total_concepts,
            "covered_concepts": self.covered_concepts,
            "missing_concepts": list(self.missing_concepts),
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeCoverageAssessment":
        return cls(coverage_id=f"coverage:{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class KnowledgeFreshnessAssessment:
    """Assessment of knowledge freshness."""
    
    freshness_id: str
    score: float = 0.5  # 0.0-1.0 (higher = more fresh)
    average_age_days: float = 0.0
    obsolete_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "freshness_id": self.freshness_id,
            "score": self.score,
            "average_age_days": self.average_age_days,
            "obsolete_count": self.obsolete_count,
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeFreshnessAssessment":
        return cls(freshness_id=f"freshness:{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class KnowledgeConfidenceAssessment:
    """Assessment of confidence calibration."""
    
    confidence_id: str
    average_confidence: float = 0.5
    calibration_status: ConfidenceCalibration = ConfidenceCalibration.UNCALIBRATED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence_id": self.confidence_id,
            "average_confidence": self.average_confidence,
            "calibration_status": self.calibration_status.value if self.calibration_status else None,
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeConfidenceAssessment":
        return cls(confidence_id=f"confidence:{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class KnowledgeCoverage:
    """Detailed coverage information for audit report."""
    
    coverage_id: str
    dimension: str  # Audit dimension name
    score: float = 0.5
    target_count: int = 0
    covered_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coverage_id": self.coverage_id,
            "dimension": self.dimension,
            "score": self.score,
            "target_count": self.target_count,
            "covered_count": self.covered_count,
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeCoverage":
        return cls(coverage_id=f"coverage:{uuid.uuid4().hex[:16]}")


# =============================================================================
# DEPENDENCY GRAPH - Tracks artifact dependencies
# =============================================================================

@dataclass(frozen=True)
class KnowledgeDependencyGraph:
    """Represents dependency relationships between knowledge artifacts."""
    
    graph_id: str
    nodes: Tuple[str, ...] = field(default_factory=tuple)  # Artifact IDs
    edges: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)  # (from, to) pairs
    
    def has_cycle(self) -> bool:
        """Check if the graph contains a cycle."""
        # Simplified cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        adj: Dict[str, List[str]] = {}
        for src, dst in self.edges:
            adj.setdefault(src, []).append(dst)
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "graph_id": self.graph_id,
            "nodes": list(self.nodes),
            "edges": [list(e) for e in self.edges],
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeDependencyGraph":
        return cls(graph_id=f"dependency:{uuid.uuid4().hex[:16]}")


# =============================================================================
# EVIDENCE SUMMARY - Summary of evidence for an artifact
# =============================================================================

@dataclass(frozen=True)
class KnowledgeEvidenceSummary:
    """Summary of evidence supporting or challenging a knowledge artifact."""
    
    summary_id: str
    total_evidence_count: int = 0
    supporting_count: int = 0
    contradicting_count: int = 0
    neutral_count: int = 0
    
    average_confidence: float = 0.5
    average_uncertainty: float = 0.5
    
    quality_distribution: Dict[EvidenceKind, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "total_evidence_count": self.total_evidence_count,
            "supporting_count": self.supporting_count,
            "contradicting_count": self.contradicting_count,
            "neutral_count": self.neutral_count,
            "average_confidence": self.average_confidence,
            "average_uncertainty": self.average_uncertainty,
            "quality_distribution": {k.value: v for k, v in self.quality_distribution.items()},
        }
    
    @classmethod
    def empty(cls) -> "KnowledgeEvidenceSummary":
        return cls(summary_id=f"evidence_summary:{uuid.uuid4().hex[:16]}")


# =============================================================================
# AUDIT TARGET - A target artifact to be audited
# =============================================================================

@dataclass(frozen=True)
class KnowledgeAuditTarget:
    """
    Represents a single knowledge artifact targeted for audit.
    
    Includes metadata about how to access and what type of artifact it is.
    """
    
    # Identity
    target_id: str                        # Artifact ID
    
    # Type information
    target_type: str                      # e.g., "assertion", "belief", "concept"
    
    # Location/access information
    location_uri: Optional[str] = None    # URI to access the artifact
    provider_ref: Optional[str] = None    # Reference to provider-specific info
    
    def __post_init__(self) -> None:
        """Validate target after creation."""
        if not self.target_id:
            raise ValueError("target_id cannot be empty")
        if not self.target_type:
            raise ValueError("target_type cannot be empty")
    
    @property
    def is_resolvable(self) -> bool:
        """Check if this target can be resolved to an artifact."""
        return self.location_uri is not None or self.provider_ref is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "target_id": self.target_id,
            "target_type": self.target_type,
            "location_uri": self.location_uri,
            "provider_ref": self.provider_ref,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAuditTarget":
        """Create target from dictionary."""
        return cls(
            target_id=data.get("target_id", ""),
            target_type=data.get("target_type", "unknown"),
            location_uri=data.get("location_uri"),
            provider_ref=data.get("provider_ref"),
        )
    
    @classmethod
    def for_assertion(cls, assertion: KnowledgeAssertion) -> "KnowledgeAuditTarget":
        """Create a target from an assertion."""
        return cls(
            target_id=assertion.assertion_identity,
            target_type="assertion",
            location_uri=f"assertion:{assertion.assertion_identity}",
        )
    
    @classmethod
    def for_belief(cls, belief: KnowledgeBelief) -> "KnowledgeAuditTarget":
        """Create a target from a belief."""
        return cls(
            target_id=belief.belief_identity,
            target_type="belief",
            location_uri=f"belief:{belief.belief_identity}",
        )
    
    @classmethod
    def for_concept(cls, concept: KnowledgeConcept) -> "KnowledgeAuditTarget":
        """Create a target from a concept."""
        return cls(
            target_id=concept.concept_identity,
            target_type="concept",
            location_uri=f"concept:{concept.concept_identity}",
        )
    
    @classmethod
    def for_relation(cls, relation: KnowledgeRelation) -> "KnowledgeAuditTarget":
        """Create a target from a relation."""
        return cls(
            target_id=relation.relation_identity,
            target_type="relation",
            location_uri=f"relation:{relation.relation_identity}",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Provider interfaces
    "KnowledgeArtifactProvider",
    
    # Engine interfaces
    "KnowledgeAuditEngine",
    "KnowledgeAuditSessionHandler",
    "AuditReportGenerator",
    
    # Core models
    "KnowledgeAuditSession",
    "KnowledgeAuditRequest",
    "KnowledgeAuditFinding",
    "KnowledgeAuditRecommendation",
    "KnowledgeAuditReport",
    
    # Health metrics
    "KnowledgeHealth",
    "KnowledgeConsistencyAssessment",
    "KnowledgeCoverageAssessment",
    "KnowledgeFreshnessAssessment",
    "KnowledgeConfidenceAssessment",
    "KnowledgeCoverage",
    
    # Dependency and evidence
    "KnowledgeDependencyGraph",
    "KnowledgeEvidenceSummary",
    
    # Audit target
    "KnowledgeAuditTarget",
]