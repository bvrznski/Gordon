# Integrity Evaluation - Governance Subsystem

"""
Integrity Evaluator: Evaluates structural correctness of Memory.

The IntegrityEvaluator implements the Integrity Laws:
    
    INTEGRITY-LAW-001: Verify Memory consistency
    INTEGRITY-LAW-002: Preserve artifact identity
    INTEGRITY-LAW-003: Preserve provenance
    INTEGRITY-LAW-004: Preserve revision graphs
    INTEGRITY-LAW-005: Violations remain explicit
    INTEGRITY-LAW-006: Never repair Memory (detection only)
    INTEGRITY-LAW-007: Evaluations remain inspectable
    INTEGRITY-LAW-008: Evaluation remains deterministic

Integrity Checks:
    
    - Identity consistency across revisions
    - Provenance completeness (origin, timestamps, processing history)
    - Revision graph integrity (chain connectivity)
    - Semantic consistency within artifacts
    - Relationship validity between artifacts
    - Ontology compliance

Example Usage:
    
    evaluator = IntegrityEvaluator(session=governance_session)
    violations, diagnostics = evaluator.evaluate(artifacts)
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time
import hashlib

# Import governance types (runtime to avoid circular deps)
try:
    from .. import (
        MemoryGovernanceSession,
        GovernanceViolation,
        GovernanceSeverity,
        GovernanceEvidence,
    )
except ImportError:
    pass


# =============================================================================
# INTEGRITY EVALUATOR - Evaluates structural correctness
# =============================================================================


class IntegrityEvaluator:
    """
    Evaluates integrity of memory artifacts.
    
    This evaluator checks:
        - Artifact identity preservation across revisions
        - Provenance completeness
        - Revision graph connectivity
        - Semantic consistency
        - Relationship validity
        
    The evaluator never modifies memory - it only detects issues and reports them.
    
    Determinism: Given the same artifacts, this will always produce the same
    results. No randomness or timing-dependent logic is used in evaluation.
    
    Evaluation Flow:
        
        1. Observe artifact set
        2. Check identity consistency (same ID across revisions)
        3. Check provenance completeness
        4. Check revision graph integrity
        5. Check semantic consistency
        6. Check relationships validity
        7. Record findings and evidence
        8. Return violations and diagnostics
        
    Anti-Patterns Rejected:
        
        - Automatically repairing issues (detection only)
        - Suppressing violations silently
        - Non-deterministic evaluation
        - Hidden evaluation criteria
    """
    
    def __init__(self, session: Optional[MemoryGovernanceSession] = None):
        """
        Initialize the integrity evaluator.
        
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
    
    @property
    def evidence_records(self) -> Tuple[GovernanceEvidence, ...]:
        """Get all evidence records (immutable copy)."""
        return tuple(self._evidence_records)
    
    # --------------------------------------------------------------------------
    # MAIN EVALUATION ENTRY POINT
    # --------------------------------------------------------------------------
    
    def evaluate(
        self,
        artifacts: Tuple[Any, ...],
    ) -> Tuple[Tuple[GovernanceViolation, ...], Dict[str, Any]]:
        """
        Evaluate integrity of memory artifacts.
        
        Args:
            artifacts: Memory artifacts to evaluate
            
        Returns:
            Tuple of (violations, diagnostics)
        """
        start_time = time.time()
        
        # Reset evaluation state
        self._violations = []
        self._evidence_records = []
        
        if not artifacts:
            return (), {"artifact_count": 0, "duration_seconds": 0}
        
        # Record observation evidence
        artifact_ids = tuple(
            str(getattr(a, 'artifact_id', getattr(a, 'id', str(a))))
            for a in artifacts
        )
        
        evidence = GovernanceEvidence.create(
            evaluation_type="integrity_evaluation",
            result={"artifacts_evaluated": len(artifacts)},
            source_artifacts=artifact_ids,
        )
        self._evidence_records.append(evidence)
        
        if self._session:
            self._session.record_audit_event(
                event_type="integrity_evaluation_started",
                details={
                    "artifact_count": len(artifacts),
                    "start_time_utc": start_time,
                },
            )
        
        # Run all integrity checks
        identity_violations = self._check_identity_consistency(artifacts)
        provenance_violations = self._check_provenance_completeness(artifacts)
        revision_violations = self._check_revision_graph(artifacts)
        semantic_violations = self._check_semantic_consistency(artifacts)
        relation_violations = self._check_relation_validity(artifacts)
        
        # Combine all violations
        all_violations = (
            tuple(identity_violations) +
            tuple(provenance_violations) +
            tuple(revision_violations) +
            tuple(semantic_violations) +
            tuple(relation_violations)
        )
        
        end_time = time.time()
        
        # Record audit completion
        if self._session:
            self._session.record_audit_event(
                event_type="integrity_evaluation_complete",
                details={
                    "artifact_count": len(artifacts),
                    "violation_count": len(all_violations),
                    "duration_seconds": end_time - start_time,
                },
            )
        
        # Build diagnostics
        diagnostics = {
            "artifact_count": len(artifacts),
            "identity_check_count": len(identity_violations),
            "provenance_check_count": len(provenance_violations),
            "revision_check_count": len(revision_violations),
            "semantic_check_count": len(semantic_violations),
            "relation_check_count": len(relation_violations),
            "total_violation_count": len(all_violations),
            "duration_seconds": end_time - start_time,
        }
        
        return all_violations, diagnostics
    
    # --------------------------------------------------------------------------
    # IDENTITY CONSISTENCY CHECKS
    # --------------------------------------------------------------------------
    
    def _check_identity_consistency(
        self,
        artifacts: Tuple[Any, ...],
    ) -> List[GovernanceViolation]:
        """Check that identity is preserved across revisions."""
        violations = []
        
        # Group artifacts by their base ID (before revision suffix)
        by_base_id: Dict[str, List[Any]] = {}
        
        for artifact in artifacts:
            artifact_id = getattr(artifact, 'artifact_id', None)
            if not artifact_id:
                continue
            
            # Extract base ID (remove :rN suffix if present)
            base_id = str(artifact_id).split(':r')[0]
            
            if base_id not in by_base_id:
                by_base_id[base_id] = []
            by_base_id[base_id].append(artifact)
        
        # Check each group has consistent identity
        for base_id, artifact_group in by_base_id.items():
            if len(artifact_group) < 2:
                continue  # Only one revision - no consistency check needed
            
            # All artifacts with same base ID should have same semantic identity
            semantic_identities = set()
            
            for art in artifact_group:
                sem_id = getattr(art, 'semantic_identity', None)
                if sem_id:
                    semantic_identities.add(str(sem_id))
            
            if len(semantic_identities) > 1:
                violations.append(GovernanceViolation(
                    violation_id=f"violation:{hashlib.md5(base_id.encode()).hexdigest()[:16]}",
                    violation_type="integrity_violation",
                    location="identity_consistency",
                    rule_name="INTEGRITY-LAW-002",
                    severity=GovernanceSeverity.ERROR,
                    description=f"Inconsistent semantic identities for artifact {base_id}",
                    source_artifact_ids=tuple(
                        str(getattr(a, 'artifact_id', '')) for a in artifact_group
                    ),
                ))
        
        return violations
    
    # --------------------------------------------------------------------------
    # PROVENANCE COMPLETENESS CHECKS
    # --------------------------------------------------------------------------
    
    def _check_provenance_completeness(
        self,
        artifacts: Tuple[Any, ...],
    ) -> List[GovernanceViolation]:
        """Check that provenance information is complete."""
        violations = []
        
        for artifact in artifacts:
            provenance = getattr(artifact, 'provenance', None)
            if not provenance:
                violations.append(GovernanceViolation(
                    violation_id=f"violation:{hashlib.md5(str(getattr(artifact, 'artifact_id', '')).encode()).hexdigest()[:16]}",
                    violation_type="integrity_violation",
                    location="provenance_completeness",
                    rule_name="INTEGRITY-LAW-003",
                    severity=GovernanceSeverity.WARNING,
                    description=f"Missing provenance for artifact {getattr(artifact, 'artifact_id', 'unknown')}",
                    source_artifact_ids=(str(getattr(artifact, 'artifact_id', '')),),
                ))
                continue
            
            # Check required provenance fields
            origin = getattr(provenance, 'origin', None)
            created_at = getattr(provenance, 'created_at_utc', None)
            
            if not origin or (isinstance(created_at, (int, float)) and created_at <= 0):
                violations.append(GovernanceViolation(
                    violation_id=f"violation:{hashlib.md5(str(getattr(artifact, 'artifact_id', '')).encode()).hexdigest()[:16]}",
                    violation_type="integrity_violation",
                    location="provenance_completeness",
                    rule_name="INTEGRITY-LAW-003",
                    severity=GovernanceSeverity.WARNING,
                    description=f"Incomplete provenance for artifact {getattr(artifact, 'artifact_id', 'unknown')}",
                    source_artifact_ids=(str(getattr(artifact, 'artifact_id', '')),),
                ))
        
        return violations
    
    # --------------------------------------------------------------------------
    # REVISION GRAPH CHECKS
    # --------------------------------------------------------------------------
    
    def _check_revision_graph(
        self,
        artifacts: Tuple[Any, ...],
    ) -> List[GovernanceViolation]:
        """Check that revision graph is properly connected."""
        violations = []
        
        # Group by base ID
        by_base_id: Dict[str, List[Any]] = {}
        
        for artifact in artifacts:
            artifact_id = getattr(artifact, 'artifact_id', None)
            if not artifact_id:
                continue
            
            base_id = str(artifact_id).split(':r')[0]
            
            if base_id not in by_base_id:
                by_base_id[base_id] = []
            by_base_id[base_id].append(artifact)
        
        # Check each revision chain
        for base_id, artifact_group in by_base_id.items():
            revisions: List[Tuple[int, Any]] = []
            
            for art in artifact_group:
                rev_num = getattr(art, 'revision_number', 1)
                if isinstance(rev_num, int) and rev_num >= 1:
                    revisions.append((rev_num, art))
            
            # Sort by revision number
            revisions.sort(key=lambda x: x[0])
            
            if len(revisions) < 2:
                continue
            
            # Check for gaps in revision sequence
            prev_rev = None
            for rev_num, art in revisions:
                if prev_rev is not None and rev_num > prev_rev + 1:
                    violations.append(GovernanceViolation(
                        violation_id=f"violation:{hashlib.md5(base_id.encode()).hexdigest()[:16]}",
                        violation_type="integrity_violation",
                        location="revision_graph",
                        rule_name="INTEGRITY-LAW-004",
                        severity=GovernanceSeverity.ERROR,
                        description=f"Gaps in revision sequence for {base_id}: "
                                   f"found revisions {prev_rev} and {rev_num}",
                        source_artifact_ids=(str(getattr(art, 'artifact_id', '')),),
                    ))
                prev_rev = rev_num
        
        return violations
    
    # --------------------------------------------------------------------------
    # SEMANTIC CONSISTENCY CHECKS
    # --------------------------------------------------------------------------
    
    def _check_semantic_consistency(
        self,
        artifacts: Tuple[Any, ...],
    ) -> List[GovernanceViolation]:
        """Check for semantic inconsistencies within artifacts."""
        violations = []
        
        for artifact in artifacts:
            # Check validity field exists and is valid
            validity = getattr(artifact, 'validity', None)
            if validity is not None:
                status = getattr(validity, 'status', None) if hasattr(validity, 'status') else validity.get('status') if isinstance(validity, dict) else None
                if status in ('invalid', 'corrupted'):
                    violations.append(GovernanceViolation(
                        violation_id=f"violation:{hashlib.md5(str(getattr(artifact, 'artifact_id', '')).encode()).hexdigest()[:16]}",
                        violation_type="integrity_violation",
                        location="semantic_consistency",
                        rule_name="INTEGRITY-LAW-001",
                        severity=GovernanceSeverity.WARNING,
                        description=f"Artifact {getattr(artifact, 'artifact_id', 'unknown')} has invalid status",
                        source_artifact_ids=(str(getattr(artifact, 'artifact_id', '')),),
                    ))
        
        return violations
    
    # --------------------------------------------------------------------------
    # RELATION VALIDITY CHECKS
    # --------------------------------------------------------------------------
    
    def _check_relation_validity(
        self,
        artifacts: Tuple[Any, ...],
    ) -> List[GovernanceViolation]:
        """Check that relationships between artifacts are valid."""
        violations = []
        
        for artifact in artifacts:
            relations = getattr(artifact, 'relations', None)
            if not relations:
                continue
            
            # Check each relation exists
            for rel in relations:
                target_id = getattr(rel, 'target_artifact_id', None)
                
                if target_id:
                    # Verify target artifact exists (simplified - would need full lookup in real implementation)
                    target_exists = any(
                        str(getattr(a, 'artifact_id', '')) == str(target_id)
                        for a in artifacts
                    )
                    
                    if not target_exists:
                        violations.append(GovernanceViolation(
                            violation_id=f"violation:{hashlib.md5(str(getattr(artifact, 'artifact_id', '')).encode()).hexdigest()[:16]}",
                            violation_type="integrity_violation",
                            location="relation_validity",
                            rule_name="INTEGRITY-LAW-001",
                            severity=GovernanceSeverity.WARNING,
                            description=f"Relation points to non-existent artifact {target_id}",
                            source_artifact_ids=(str(getattr(artifact, 'artifact_id', '')),),
                        ))
        
        return violations


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "IntegrityEvaluator",
]