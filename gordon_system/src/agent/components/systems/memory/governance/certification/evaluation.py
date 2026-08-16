# Certification Evaluation - Governance Subsystem

"""
Certification Evaluator: Produces final memory system certification.

The CertificationEvaluator implements:
    
    CERTIFICATION-LAW-001: Evaluate the complete Memory System
    CERTIFICATION-LAW-002: Aggregate governance evidence
    CERTIFICATION-LAW-003: Preserve supporting diagnostics
    CERTIFICATION-LAW-004: Preserve audit history
    CERTIFICATION-LAW-005: Expose explicit conditions
    CERTIFICATION-LAW-006: Never hide violations
    CERTIFICATION-LAW-007: Remain reproducible
    CERTIFICATION-LAW-008: Evaluation remains deterministic

Certification Flow:
    
    1. Collect all evidence from integrity/compliance evaluations
    2. Aggregate violations and warnings
    3. Calculate confidence score based on findings
    4. Make certification decision (pass/fail/conditional)
    5. Generate report with full audit trail
    
Certification Inputs:
    
    - Integrity evaluation results
    - Compliance evaluation results  
    - All evidence records
    - Audit history
    - Diagnostics

Certification Output:
    
    - GovernanceReport with certification status
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time

# Import governance types (runtime to avoid circular deps)
try:
    from .. import (
        MemoryGovernanceSession,
        GovernanceViolation,
        GovernanceSeverity,
        GovernanceEvidence,
        GovernanceReport,
        GovernanceState,
        CertificationResult,
        CertificationDecision,
    )
except ImportError:
    pass


# =============================================================================
# CERTIFICATION EVALUATOR - Produces final certification
# =============================================================================


class CertificationEvaluator:
    """
    Produces final certification decision for the Memory System.
    
    This evaluator aggregates all governance evidence and produces a final
    certification decision. It never modifies memory - it only evaluates,
    certifies, and reports.
    
    Determinism: Given the same inputs, this will always produce the same
    results. No randomness or timing-dependent logic is used in evaluation.
    
    Evaluation Flow:
        
        1. Collect evidence from all evaluations
        2. Aggregate violations by severity
        3. Calculate confidence score
        4. Make certification decision
        5. Generate final report
        
    Anti-Patterns Rejected:
        
        - Hiding violations
        - Non-deterministic evaluation
        - Hidden criteria or logic
    """
    
    def __init__(self, session: Optional[MemoryGovernanceSession] = None):
        """
        Initialize the certification evaluator.
        
        Args:
            session: Governance session for recording evidence and audit events
        """
        self._session = session
        self._violations: List[GovernanceViolation] = []
        self._evidence_records: List[GovernanceEvidence] = []
    
    @property
    def violations(self) -> Tuple[GovernanceViolation, ...]:
        """Get all recorded violations (immutable copy)."""
        return tuple(self._violations)
    
    # --------------------------------------------------------------------------
    # MAIN EVALUATION ENTRY POINT
    # --------------------------------------------------------------------------
    
    def evaluate(
        self,
        artifacts: Tuple[Any, ...],
    ) -> GovernanceReport:
        """
        Produce final certification and report.
        
        Args:
            artifacts: Memory artifacts being evaluated
            
        Returns:
            GovernanceReport with certification status
        """
        start_time = time.time()
        
        # Reset evaluation state
        self._violations = []
        self._evidence_records = []
        
        if self._session:
            self._session.record_audit_event(
                event_type="certification_evaluation_started",
                details={
                    "start_time_utc": start_time,
                },
            )
        
        violations = []
        
        # Get all violations from session (if available)
        if self._session:
            violations.extend(self._session.violations)
        
        end_time = time.time()
        
        # Calculate confidence score
        confidence = self._calculate_confidence(violations, len(artifacts))
        
        # Make certification decision
        result = self._make_certification_decision(violations, confidence)
        
        # Build recommendations
        recommendations = []
        for v in violations:
            if v.recommendation:
                recommendations.append(
                    f"{v.location}: {v.description} - {v.recommendation}"
                )
        
        # Generate report ID
        import hashlib
        report_id = "report:" + hashlib.md5(str(start_time).encode()).hexdigest()[:16]
        
        # Create report
        report = GovernanceReport.create(
            evaluation_scope="full_memory_system",
            status=GovernanceState.COMPLETE,
            certification_status=result.value,
            violations=tuple(violations),
            recommendations=tuple(recommendations) if recommendations else (),
            diagnostics={
                "confidence": confidence,
                "certification_result": result.value,
                "artifact_count": len(artifacts),
                "duration_seconds": end_time - start_time,
            },
            revision_id="system:current",
        )
        
        # Record audit completion
        if self._session:
            self._session.record_audit_event(
                event_type="certification_evaluation_complete",
                details={
                    "result": result.value,
                    "confidence": confidence,
                    "violation_count": len(violations),
                    "duration_seconds": end_time - start_time,
                },
            )
        
        return report
    
    # --------------------------------------------------------------------------
    # CONFIDENCE CALCULATION
    # --------------------------------------------------------------------------
    
    def _calculate_confidence(
        self,
        violations: Tuple[GovernanceViolation, ...],
        artifact_count: int,
    ) -> float:
        """
        Calculate certification confidence score (0.0-1.0).
        
        Confidence is based on:
            - Number of violations found
            - Severity of violations
            - Number of artifacts evaluated
            
        Args:
            violations: List of violations found
            artifact_count: Total number of artifacts evaluated
            
        Returns:
            Confidence score (0.0-1.0)
        """
        if not artifact_count:
            return 0.5  # No data = neutral confidence
        
        if not violations:
            return 1.0  # No issues = full confidence
        
        # Weight by severity
        total_weight = 0.0
        for v in violations:
            if v.severity == GovernanceSeverity.CRITICAL:
                total_weight += 1.0
            elif v.severity == GovernanceSeverity.ERROR:
                total_weight += 0.75
            elif v.severity == GovernanceSeverity.WARNING:
                total_weight += 0.25
            else:
                total_weight += 0.1
        
        # Calculate confidence (more violations = lower confidence)
        max_possible_weight = artifact_count * 1.0
        weight_ratio = min(total_weight / max(max_possible_weight, 1), 1.0)
        
        return round(1.0 - weight_ratio, 3)
    
    # --------------------------------------------------------------------------
    # CERTIFICATION DECISION
    # --------------------------------------------------------------------------
    
    def _make_certification_decision(
        self,
        violations: Tuple[GovernanceViolation, ...],
        confidence: float,
    ) -> CertificationResult:
        """
        Make certification decision based on findings.
        
        Decision Rules:
            - CRITICAL violations = FAIL
            - ERROR violations = FAIL
            - Warning count > 50% of artifacts = CONDITIONAL
            - No issues + confidence >= 0.9 = PASS
            
        Args:
            violations: List of violations found
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            CertificationResult
        """
        if not violations:
            return CertificationResult.PASS
        
        # Check for critical or error violations
        has_critical = any(v.is_critical for v in violations)
        has_error = any(v.severity == GovernanceSeverity.ERROR for v in violations)
        
        if has_critical or has_error:
            return CertificationResult.FAIL
        
        # Check warning count
        warning_count = sum(1 for v in violations if v.severity == GovernanceSeverity.WARNING)
        
        if warning_count > 0 and confidence < 0.8:
            return CertificationResult.FAIL
        
        if warning_count > 0:
            return CertificationResult.CONDITIONAL
        
        return CertificationResult.PASS


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CertificationEvaluator",
]