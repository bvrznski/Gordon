# Memory Governance - Phase 5.1.8 Constitutional Layer
# ======================================================

"""
Memory Governance: The constitutional supervision subsystem of Gordon.

Governs the Memory System by evaluating:

    - Is Memory correct?
    - Is Memory consistent?
    - Is Memory trustworthy?
    - Can Memory evolve?
    - Can Memory be certified?

Governance Philosophy:
    
    Observation → Evaluation → Certification → Recommendation → Execution

Governance owns:

    - Integrity evaluation
    - Certification
    - Compliance
    - Auditing
    - Governance diagnostics
    - Governance health

Governance NEVER owns:

    - Memory Artifacts
    - Memory Forms
    - Operations
    - Access
    - Lifecycle
    - Policies
    - Knowledge
    - Reasoning
    - Learning

Governance is meta-architectural: it evaluates the system as a whole, not
participates in memory execution.

Architecture Dependencies:

    - Foundation (MemoryArtifact, Identity, Provenance)
    - Forms (Core, Semantic, Episodic, etc.)
    - Operations (Encoding, Retrieval, Association, etc.)
    - Access (Session, Authorization, Visibility)
    - Lifecycle (States, History, Contracts)
    - Policies (Decision, Evidence, Admission, Activation, Retention, etc.)
    - Derived Memory (Derivation, Evidence, Provenance)
    - Integration (Contract, Request, Response, Compatibility)

Governance Components:

    integrity/   Structural correctness evaluation
    compliance/  Architectural rules verification
    auditing/     Governance history maintenance
    repair/       Restoration strategy proposal
    evolution/    Architectural change evaluation
    migration/    Version transition evaluation
    certification/ Complete system certification

Shared Contracts:

    governance.py   Core governance interface and session management
    audit.py        Audit record generation and storage
    certification.py Certification evaluation and evidence
    report.py       Governance reports with recommendations
    diagnostics.py  Governance health and diagnostic information
    statistics.py   Governance metrics collection
    health.py       Governance health scoring and reporting

Governance Laws (see individual modules):

    GOVERNANCE-LAW-001 through GOVERNANCE-LAW-008: Meta-governance
    INTEGRITY-LAW-001 through INTEGRITY-LAW-008: Integrity constraints
    COMPLIANCE-LAW-001 through COMPLIANCE-LAW-008: Compliance constraints
    AUDIT-LAW-001 through AUDIT-LAW-008: Audit constraints
    REPAIR-LAW-001 through REPAIR-LAW-008: Repair constraints
    EVOLUTION-LAW-001 through EVOLUTION-LAW-008: Evolution constraints
    MIGRATION-LAW-001 through MIGRATION-LAW-008: Migration constraints
    CERTIFICATION-LAW-001 through CERTIFICATION-LAW-008: Certification constraints
    REPORT-LAW-001 through REPORT-LAW-008: Report constraints
    VALIDATION-LAW-001 through VALIDATION-LAW-008: Validation constraints
    DETERMINISM-LAW-001 through DETERMINISM-LAW-008: Determinism guarantees

Global Invariants:

    - Governance never performs Memory execution
    - Integrity precedes certification
    - Compliance precedes certification
    - Audits are immutable
    - Repair remains advisory
    - Evolution remains advisory
    - Migration remains advisory
    - Certification preserves evidence
    - Provenance is preserved
    - Deterministic guarantees hold

Anti-Patterns Rejected:

    - Governance modifying Memory directly
    - Integrity automatically repairing violations
    - Compliance silently correcting errors
    - Mutable audit logs
    - Hidden certification criteria
    - Undocumented migrations
    - Governance-specific Memory ownership
    - Duplicated integrity mechanisms
    - Opaque certification logic
    - Non-deterministic governance

"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import time
import uuid

# Import governance types (runtime to avoid circular deps)
try:
    from .audit import AuditRecord
except ImportError:
    pass

# Import memory system components (runtime to avoid circular deps)
try:
    from ..foundations.artifact import MemoryArtifact, MemoryArtifactKind
except ImportError:
    pass


# =============================================================================
# GOVERNANCE STATES
# =============================================================================


class GovernanceState(Enum):
    """Current state of governance evaluation."""
    
    INITIAL = "initial"              # Just created
    OBSERVING = "observing"          # Observing memory state
    EVALUATING = "evaluating"        # Evaluating integrity/compliance
    CERTIFYING = "certifying"        # Producing certification
    REPORTING = "reporting"          # Generating report
    COMPLETE = "complete"            # Evaluation finished
    FAILED = "failed"                # Evaluation failed


class GovernanceViolationType(Enum):
    """Types of governance violations."""
    
    INTEGRITY_VIOLATION = "integrity_violation"
    COMPLIANCE_VIOLATION = "compliance_violation"
    AUDIT_VIOLATION = "audit_violation"
    CERTIFICATION_VIOLATION = "certification_violation"
    REPAIR_VIOLATION = "repair_violation"
    EVOLUTION_VIOLATION = "evolution_violation"
    MIGRATION_VIOLATION = "migration_violation"


class GovernanceSeverity(Enum):
    """Severity levels for governance issues."""
    
    DEBUG = "debug"           # Informational only
    INFO = "info"            # General information
    WARNING = "warning"      # Potential issue
    ERROR = "error"          # Actual violation
    CRITICAL = "critical"    # System-critical issue


# =============================================================================
# GOVERNANCE EVIDENCE - Immutable proof of evaluation
# =============================================================================


@dataclass(frozen=True)
class GovernanceEvidence:
    """
    Immutable evidence supporting a governance decision.
    
    Every governance evaluation produces evidence that can be inspected,
    verified, and traced back to the original memory state.
    
    Fields:
        evidence_id:      Unique identifier for this evidence record
        evaluation_type:  What was evaluated (integrity, compliance, etc.)
        timestamp_utc:    When evaluation occurred
        result:           The outcome of evaluation
        supporting_data:  Additional data supporting the decision
        source_artifacts: Which memory artifacts were involved
        revision_id:      Memory system revision at time of evaluation
    """
    
    evidence_id: str                        # Unique evidence identifier
    evaluation_type: str                    # Type of evaluation performed
    timestamp_utc: float                   # When evaluation occurred
    
    result: Dict[str, Any]                 # Evaluation result (status, findings)
    
    # Supporting information
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    source_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Artifact IDs
    revision_id: str = ""                  # Memory system revision identifier
    
    @property
    def is_pass(self) -> bool:
        """Check if evaluation passed."""
        return self.result.get("status", "fail") == "pass"
    
    @property
    def is_fail(self) -> bool:
        """Check if evaluation failed."""
        return not self.is_pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary representation."""
        return {
            "evidence_id": self.evidence_id,
            "evaluation_type": self.evaluation_type,
            "timestamp_utc": self.timestamp_utc,
            "result": dict(self.result),
            "supporting_data": dict(self.supporting_data),
            "source_artifacts": list(self.source_artifacts),
            "revision_id": self.revision_id,
        }
    
    @classmethod
    def create(
        cls,
        evaluation_type: str,
        result: Dict[str, Any],
        supporting_data: Optional[Dict[str, Any]] = None,
        source_artifacts: Optional[Tuple[str, ...]] = None,
        revision_id: str = "",
    ) -> "GovernanceEvidence":
        """
        Create new governance evidence.
        
        Args:
            evaluation_type: What was evaluated (integrity, compliance, etc.)
            result: The outcome of evaluation
            supporting_data: Additional data supporting the decision
            source_artifacts: Which memory artifacts were involved
            revision_id: Memory system revision at time of evaluation
            
        Returns:
            New GovernanceEvidence instance
        """
        return cls(
            evidence_id=f"evidence:{uuid.uuid4().hex[:16]}",
            evaluation_type=evaluation_type,
            timestamp_utc=time.time(),
            result=dict(result),
            supporting_data=dict(supporting_data) if supporting_data else {},
            source_artifacts=source_artifacts or (),
            revision_id=revision_id,
        )


# =============================================================================
# GOVERNANCE VIOLATION - A governance rule violation
# =============================================================================


@dataclass(frozen=True)
class GovernanceViolation:
    """
    A governance rule violation.
    
    Every violation contains:
        - Location (which module/system part)
        - Rule violated (the specific law/constraint)
        - Severity level
        - Evidence (what caused the violation)
        - Recommendation (how to fix it)
        
    Violations are immutable and can be inspected but never hidden.
    """
    
    violation_id: str                       # Unique identifier
    violation_type: GovernanceViolationType  # Category of violation
    location: str                          # Where violation occurred
    rule_name: str                         # Which governance law was violated
    severity: GovernanceSeverity           # How serious is this?
    
    description: str                      # Human-readable explanation
    
    evidence: Any = None                   # Supporting evidence (artifacts, data)
    recommendation: Optional[str] = None   # Suggested fix
    
    timestamp_utc: float = field(default_factory=time.time)  # When detected
    source_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)  # Affected artifacts
    
    @property
    def is_critical(self) -> bool:
        """Check if this violation is critical."""
        return self.severity == GovernanceSeverity.CRITICAL
    
    @property
    def is_error(self) -> bool:
        """Check if this violation is an error."""
        return self.severity == GovernanceSeverity.ERROR
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary representation."""
        return {
            "violation_id": self.violation_id,
            "violation_type": self.violation_type.value,
            "location": self.location,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "description": self.description,
            "evidence": str(self.evidence) if self.evidence else None,
            "recommendation": self.recommendation,
            "timestamp_utc": self.timestamp_utc,
            "source_artifact_ids": list(self.source_artifact_ids),
        }


# =============================================================================
# GOVERNANCE REPORT - Complete governance evaluation summary
# =============================================================================


@dataclass(frozen=True)
class GovernanceReport:
    """
    Complete governance evaluation report.
    
    Reports summarize the entire governance evaluation process, including:
        - What was evaluated
        - What passed/failed
        - Violations found
        - Recommendations made
        - Certification status
    
    Reports are immutable and serve as official records of governance state.
    """
    
    # Report identification
    report_id: str                          # Unique report identifier
    evaluation_scope: str                  # What was evaluated (full, integrity_only, etc.)
    timestamp_utc: float                   # When report was generated
    
    # Evaluation results
    status: GovernanceState                # Overall governance state
    certification_status: Optional[str] = None  # Certification result (pass/fail/conditional)
    
    # Findings
    violations: Tuple[GovernanceViolation, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Evidence and diagnostics
    evidence_records: Tuple[GovernanceEvidence, ...] = field(default_factory=tuple)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Revision information
    revision_id: str = ""                  # Memory system revision at time of report
    
    @property
    def is_certified(self) -> bool:
        """Check if memory passed certification."""
        return self.certification_status == "pass" and len(self.violations) == 0
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    @property
    def critical_count(self) -> int:
        """Count of critical severity violations."""
        return sum(1 for v in self.violations if v.is_critical)
    
    @property
    def error_count(self) -> int:
        """Count of error severity violations."""
        return sum(1 for v in self.violations if v.severity == GovernanceSeverity.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return len(self.warnings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "evaluation_scope": self.evaluation_scope,
            "timestamp_utc": self.timestamp_utc,
            "status": self.status.value,
            "certification_status": self.certification_status,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": list(self.warnings),
            "recommendations": list(self.recommendations),
            "evidence_records": [e.to_dict() for e in self.evidence_records],
            "diagnostics": dict(self.diagnostics),
            "revision_id": self.revision_id,
        }
    
    @classmethod
    def create(
        cls,
        evaluation_scope: str,
        status: GovernanceState = GovernanceState.COMPLETE,
        certification_status: Optional[str] = None,
        violations: Optional[Tuple[GovernanceViolation, ...]] = None,
        warnings: Optional[Tuple[str, ...]] = None,
        recommendations: Optional[Tuple[str, ...]] = None,
        evidence_records: Optional[Tuple[GovernanceEvidence, ...]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        revision_id: str = "",
    ) -> "GovernanceReport":
        """
        Create a new governance report.
        
        Args:
            evaluation_scope: What was evaluated (full, integrity_only, etc.)
            status: Overall governance state
            certification_status: Certification result (pass/fail/conditional)
            violations: Any violations found
            warnings: Warning messages
            recommendations: Suggested improvements
            evidence_records: Evidence records from evaluation
            diagnostics: Diagnostic information
            revision_id: Memory system revision identifier
            
        Returns:
            New GovernanceReport instance
        """
        return cls(
            report_id=f"report:{uuid.uuid4().hex[:16]}",
            evaluation_scope=evaluation_scope,
            timestamp_utc=time.time(),
            status=status,
            certification_status=certification_status,
            violations=violations or (),
            warnings=warnings or (),
            recommendations=recommendations or (),
            evidence_records=evidence_records or (),
            diagnostics=dict(diagnostics) if diagnostics else {},
            revision_id=revision_id,
        )


# =============================================================================
# GOVERNANCE SESSION - A single governance evaluation session
# =============================================================================


class MemoryGovernanceSession:
    """
    Manages a single governance evaluation session.
    
    A governance session coordinates all governance activities for evaluating
    the memory system state. It produces certification and reports but never
    modifies memory directly.
    
    Session Flow:
        
        1. Initialize (set target, start time)
        2. Observe memory state
        3. Run integrity evaluations
        4. Run compliance evaluations  
        5. Record audit events
        6. Produce certification decision
        7. Generate final report
        
    The session is read-only with respect to memory - it only observes,
    evaluates, and reports.
    
    Session Properties:
        
        - Deterministic: Same input state → same output evaluation
        - Immutable: Cannot modify memory during evaluation
        - Transparent: All decisions are auditable
        - Complete: Must evaluate all applicable governance rules
        
    Session Contracts:
        
        - Integrity evaluation must complete before certification
        - Compliance evaluation must complete before certification
        - Audit records must be immutable once written
        - Violations cannot be suppressed
        - Evidence must be preserved for inspection
        
    Session Lifecycle:
        
        INIT → OBSERVING → EVALUATING → CERTIFYING → REPORTING → COMPLETE/FAILED
    """
    
    # Session identification
    _session_id: str
    _evaluation_target: str
    
    # State tracking
    _state: GovernanceState
    _start_time_utc: float
    
    # Evaluation results
    _violations: List[GovernanceViolation]
    _warnings: List[str]
    _recommendations: List[str]
    
    # Evidence and audit
    _evidence_records: List[GovernanceEvidence]
    _audit_log: List[Dict[str, Any]]
    
    def __init__(
        self,
        evaluation_target: str = "memory_system",
    ):
        """
        Initialize a new governance session.
        
        Args:
            evaluation_target: What is being evaluated (full system, specific module, etc.)
        """
        self._session_id = f"sess:{uuid.uuid4().hex[:16]}"
        self._evaluation_target = evaluation_target
        self._state = GovernanceState.INITIAL
        self._start_time_utc = time.time()
        
        self._violations = []
        self._warnings = []
        self._recommendations = []
        
        self._evidence_records = []
        self._audit_log = []
    
    @property
    def session_id(self) -> str:
        """Get the session ID."""
        return self._session_id
    
    @property
    def state(self) -> GovernanceState:
        """Get current session state."""
        return self._state
    
    @property
    def violations(self) -> Tuple[GovernanceViolation, ...]:
        """Get all recorded violations (immutable copy)."""
        return tuple(self._violations)
    
    @property
    def warnings(self) -> Tuple[str, ...]:
        """Get all recorded warnings (immutable copy)."""
        return tuple(self._warnings)
    
    @property
    def recommendations(self) -> Tuple[str, ...]:
        """Get all recorded recommendations (immutable copy)."""
        return tuple(self._recommendations)
    
    # --------------------------------------------------------------------------
    # STATE TRANSITIONS
    # --------------------------------------------------------------------------
    
    def transition_to_observing(self) -> None:
        """Transition to observing state."""
        self._state = GovernanceState.OBSERVING
    
    def transition_to_evaluating(self) -> None:
        """Transition to evaluating state."""
        self._state = GovernanceState.EVALUATING
    
    def transition_to_certifying(self) -> None:
        """Transition to certifying state."""
        self._state = GovernanceState.CERTIFYING
    
    def transition_to_reporting(self) -> None:
        """Transition to reporting state."""
        self._state = GovernanceState.REPORTING
    
    # --------------------------------------------------------------------------
    # OBSERVATION
    # --------------------------------------------------------------------------
    
    def observe_memory_state(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> None:
        """
        Observe memory state for evaluation.
        
        Args:
            artifacts: Memory artifacts to evaluate
        """
        self.transition_to_observing()
        
        # Record observation evidence
        artifact_ids = tuple(a.artifact_id if hasattr(a, 'artifact_id') else str(a) 
                           for a in artifacts)
        
        evidence = GovernanceEvidence.create(
            evaluation_type="memory_state_observation",
            result={"artifacts_observed": len(artifacts)},
            source_artifacts=artifact_ids,
        )
        self._evidence_records.append(evidence)
    
    # --------------------------------------------------------------------------
    # AUDIT RECORDING
    # --------------------------------------------------------------------------
    
    def record_audit_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        source_artifact_id: Optional[str] = None,
    ) -> GovernanceEvidence:
        """
        Record an audit event during evaluation.
        
        Audit events are immutable and cannot be removed.
        
        Args:
            event_type: Type of event (integrity_check, compliance_check, etc.)
            details: Event-specific information
            source_artifact_id: Optional artifact that triggered this event
            
        Returns:
            GovernanceEvidence for the audit record
        """
        evidence = GovernanceEvidence.create(
            evaluation_type=event_type,
            result={"details": dict(details)},
            source_artifacts=(source_artifact_id,) if source_artifact_id else (),
        )
        self._audit_log.append(evidence.to_dict())
        self._evidence_records.append(evidence)
        
        return evidence
    
    # --------------------------------------------------------------------------
    # INTEGRITY EVALUATION
    # --------------------------------------------------------------------------
    
    def evaluate_integrity(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> Tuple[Tuple[GovernanceViolation, ...], Dict[str, Any]]:
        """
        Evaluate integrity of memory artifacts.
        
        Integrity checks:
            - Artifact consistency
            - Identity preservation
            - Revision graph integrity
            - Provenance completeness
            
        Args:
            artifacts: Memory artifacts to evaluate
            
        Returns:
            Tuple of (violations, diagnostics)
        """
        from .integrity.evaluation import IntegrityEvaluator
        
        self.transition_to_evaluating()
        
        evaluator = IntegrityEvaluator(session=self)
        violations, diagnostics = evaluator.evaluate(artifacts)
        
        return tuple(violations), diagnostics
    
    # --------------------------------------------------------------------------
    # COMPLIANCE EVALUATION
    # --------------------------------------------------------------------------
    
    def evaluate_compliance(
        self,
        policies: Any,
        lifecycle_states: Any,
    ) -> Tuple[Tuple[GovernanceViolation, ...], Dict[str, Any]]:
        """
        Evaluate compliance with architectural rules.
        
        Compliance checks:
            - Policy adherence
            - Lifecycle correctness
            - Contract fulfillment
            
        Args:
            policies: Active policies to check against
            lifecycle_states: Current lifecycle states of artifacts
            
        Returns:
            Tuple of (violations, diagnostics)
        """
        from .compliance.evaluation import ComplianceEvaluator
        
        self.transition_to_evaluating()
        
        evaluator = ComplianceEvaluator(session=self)
        violations, diagnostics = evaluator.evaluate(policies, lifecycle_states)
        
        return tuple(violations), diagnostics
    
    # --------------------------------------------------------------------------
    # CERTIFICATION
    # --------------------------------------------------------------------------
    
    def produce_certification(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> GovernanceReport:
        """
        Produce final certification and report.
        
        Certification aggregates all evaluation results and produces a final
        decision on memory system correctness.
        
        Args:
            artifacts: Memory artifacts being evaluated
            
        Returns:
            GovernanceReport with certification status
        """
        from .certification.evaluation import CertificationEvaluator
        
        self.transition_to_certifying()
        
        evaluator = CertificationEvaluator(session=self)
        report = evaluator.evaluate(artifacts)
        
        self.transition_to_reporting()
        
        return report
    
    # --------------------------------------------------------------------------
    # REPORT GENERATION
    # --------------------------------------------------------------------------
    
    def generate_report(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> GovernanceReport:
        """
        Generate a complete governance report.
        
        This is the main entry point for governance evaluation. It orchestrates
        all evaluation phases and produces a final report.
        
        Args:
            artifacts: Memory artifacts to evaluate
            
        Returns:
            Complete GovernanceReport with all findings
        """
        self.transition_to_observing()
        
        # Observe memory state
        self.observe_memory_state(artifacts)
        
        # Evaluate integrity
        integrity_violations, integrity_diagnostics = self.evaluate_integrity(artifacts)
        
        # Evaluate compliance
        # (placeholder - would need actual policies and lifecycle data)
        compliance_violations, compliance_diagnostics = self.evaluate_compliance(
            policies=None,
            lifecycle_states=None,
        )
        
        # Combine violations and diagnostics
        all_violations = tuple(integrity_violations) + tuple(compliance_violations)
        all_diagnostics = {
            "integrity": integrity_diagnostics,
            "compliance": compliance_diagnostics,
        }
        
        # Produce certification
        report = self.produce_certification(artifacts)
        
        # Add violations and diagnostics to report
        if all_violations:
            report_data = report.to_dict()
            report_data["violations"] = tuple(report_data.get("violations", [])) + all_violations
            report_data["diagnostics"].update(all_diagnostics)
        
        self.transition_to_complete()
        
        return report
    
    def transition_to_complete(self) -> None:
        """Transition to complete state."""
        self._state = GovernanceState.COMPLETE


# =============================================================================
# GOVERNANCE INTERFACE - Main entry point for governance evaluation
# =============================================================================


class MemoryGovernance:
    """
    Main interface for memory governance evaluation.
    
    This is the public API that other systems use to request governance
    evaluations. It never modifies memory directly - it only evaluates,
    certifies, and reports.
    
    Governance Interface Methods:
        
        evaluate(artifacts) → GovernanceReport
            Perform complete governance evaluation
            
        certify(artifacts) → CertificationResult
            Produce certification decision only
            
        inspect_integrity(artifacts) → IntegrityReport
            Evaluate integrity specifically
            
        inspect_compliance(policies, lifecycle) → ComplianceReport
            Evaluate compliance specifically
            
        audit(event_type, details) → GovernanceEvidence
            Record an audit event
        
        get_health() → HealthMetrics
            Get current governance health metrics
            
    Example Usage:
        
        # Initialize governance (with memory system dependencies)
        governance = MemoryGovernance()
        
        # Get artifacts to evaluate (from memory storage)
        artifacts = tuple(memory_storage.get_all_artifacts())
        
        # Perform full evaluation
        report = governance.evaluate(artifacts)
        
        if report.is_certified:
            print("Memory is certified correct")
        else:
            print(f"Found {len(report.violations)} violations")
            
    Architecture Constraints:
        
        - Never modifies memory (read-only with respect to artifacts)
        - Always produces immutable evidence and reports
        - Deterministic: same input → same output
        - Transparent: all decisions are auditable
        - Complete: evaluates all applicable rules
        
    Error Handling:
        
        - Evaluations may fail gracefully with error status
        - Errors are recorded as violations with severity ERROR
        - Failed evaluations still produce reports for inspection
    """
    
    _session_factory = MemoryGovernanceSession
    
    def __init__(
        self,
        evaluation_target: str = "memory_system",
    ):
        """
        Initialize the governance system.
        
        Args:
            evaluation_target: What is being governed (full system, module, etc.)
        """
        self._evaluation_target = evaluation_target
    
    @property
    def evaluation_target(self) -> str:
        """Get the evaluation target description."""
        return self._evaluation_target
    
    # --------------------------------------------------------------------------
    # MAIN EVALUATION METHOD
    # --------------------------------------------------------------------------
    
    def evaluate(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> GovernanceReport:
        """
        Perform complete governance evaluation.
        
        This is the primary entry point for governance. It orchestrates all
        evaluation phases and produces a final certified report.
        
        Args:
            artifacts: Memory artifacts to evaluate
            
        Returns:
            Complete GovernanceReport with certification status
        """
        session = self._session_factory(
            evaluation_target=self._evaluation_target,
        )
        
        return session.generate_report(artifacts)
    
    def certify(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> Dict[str, Any]:
        """
        Produce certification decision only.
        
        Args:
            artifacts: Memory artifacts to certify
            
        Returns:
            Certification result dictionary
        """
        report = self.evaluate(artifacts)
        
        return {
            "certified": report.is_certified,
            "status": report.certification_status or "unknown",
            "violations_count": len(report.violations),
            "timestamp_utc": report.timestamp_utc,
        }
    
    # --------------------------------------------------------------------------
    # SPECIFIC EVALUATIONS
    # --------------------------------------------------------------------------
    
    def inspect_integrity(
        self,
        artifacts: Tuple[MemoryArtifact, ...],
    ) -> Dict[str, Any]:
        """
        Evaluate integrity specifically.
        
        Args:
            artifacts: Memory artifacts to evaluate
            
        Returns:
            Integrity evaluation results
        """
        from .integrity.evaluation import IntegrityEvaluator
        
        session = self._session_factory(
            evaluation_target=f"integrity:{self._evaluation_target}",
        )
        
        violations, diagnostics = session.evaluate_integrity(artifacts)
        
        return {
            "status": "pass" if len(violations) == 0 else "fail",
            "violations_count": len(violations),
            "diagnostics": diagnostics,
            "timestamp_utc": time.time(),
        }
    
    def inspect_compliance(
        self,
        policies: Any,
        lifecycle_states: Any,
    ) -> Dict[str, Any]:
        """
        Evaluate compliance specifically.
        
        Args:
            policies: Policies to check against
            lifecycle_states: Lifecycle states to verify
            
        Returns:
            Compliance evaluation results
        """
        from .compliance.evaluation import ComplianceEvaluator
        
        session = self._session_factory(
            evaluation_target=f"compliance:{self._evaluation_target}",
        )
        
        violations, diagnostics = session.evaluate_compliance(policies, lifecycle_states)
        
        return {
            "status": "pass" if len(violations) == 0 else "fail",
            "violations_count": len(violations),
            "diagnostics": diagnostics,
            "timestamp_utc": time.time(),
        }
    
    def audit(
        self,
        event_type: str,
        details: Dict[str, Any],
    ) -> GovernanceEvidence:
        """
        Record an audit event.
        
        Args:
            event_type: Type of audit event
            details: Event-specific information
            
        Returns:
            Evidence record for the audit
        """
        evidence = GovernanceEvidence.create(
            evaluation_type=event_type,
            result={"details": dict(details)},
        )
        
        return evidence


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # States and types
    "GovernanceState",
    "GovernanceViolationType",
    "GovernanceSeverity",
    
    # Core classes
    "MemoryGovernance",
    "MemoryGovernanceSession",
    
    # Data models
    "GovernanceEvidence",
    "GovernanceViolation",
    "GovernanceReport",
]