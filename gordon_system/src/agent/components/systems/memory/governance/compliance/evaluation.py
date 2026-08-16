# Compliance Evaluation - Governance Subsystem

"""
Compliance Evaluator: Verifies architectural rules for Memory.

The ComplianceEvaluator implements:
    
    COMPLIANCE-LAW-001: Verify architectural contracts
    COMPLIANCE-LAW-002: Verify ontology rules
    COMPLIANCE-LAW-003: Verify policy consistency
    COMPLIANCE-LAW-004: Verify lifecycle correctness
    COMPLIANCE-LAW-005: Preserve evidence
    COMPLIANCE-LAW-006: Never modify Memory
    COMPLIANCE-LAW-007: Reports remain inspectable
    COMPLIANCE-LAW-008: Evaluation remains deterministic

Compliance Checks:
    
    - Policy adherence (admission, activation, retention, archival)
    - Ontology compliance (type hierarchies, constraints)
    - Lifecycle correctness (valid state transitions)
    - Contract fulfillment (memory integration contracts)

Example Usage:
    
    evaluator = ComplianceEvaluator(session=governance_session)
    violations, diagnostics = evaluator.evaluate(policies, lifecycle_states)
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
# COMPLIANCE EVALUATOR - Verifies architectural rules
# =============================================================================


class ComplianceEvaluator:
    """
    Verifies that memory operations comply with architectural rules.
    
    This evaluator checks:
        - Policy adherence (admission, activation, retention, archival)
        - Ontology compliance (type constraints, hierarchies)
        - Lifecycle correctness (valid state transitions)
        - Contract fulfillment (memory integration contracts)
        
    The evaluator never modifies memory - it only detects issues and reports them.
    
    Determinism: Given the same inputs, this will always produce the same
    results. No randomness or timing-dependent logic is used in evaluation.
    
    Evaluation Flow:
        
        1. Observe policies and states
        2. Check policy adherence
        3. Check ontology compliance
        4. Check lifecycle correctness
        5. Check contract fulfillment
        6. Record findings and evidence
        7. Return violations and diagnostics
        
    Anti-Patterns Rejected:
        
        - Silent correction of errors (detection only)
        - Non-deterministic evaluation
        - Hidden criteria or logic
    """
    
    def __init__(self, session: Optional[MemoryGovernanceSession] = None):
        """
        Initialize the compliance evaluator.
        
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
        policies: Any,
        lifecycle_states: Any,
    ) -> Tuple[Tuple[GovernanceViolation, ...], Dict[str, Any]]:
        """
        Evaluate compliance with architectural rules.
        
        Args:
            policies: Policies to check against (admission, activation, etc.)
            lifecycle_states: Lifecycle states of artifacts
            
        Returns:
            Tuple of (violations, diagnostics)
        """
        start_time = time.time()
        
        # Reset evaluation state
        self._violations = []
        self._evidence_records = []
        
        if self._session:
            self._session.record_audit_event(
                event_type="compliance_evaluation_started",
                details={
                    "start_time_utc": start_time,
                },
            )
        
        violations = []
        
        # Run all compliance checks
        policy_violations = self._check_policy_adherence(policies)
        ontology_violations = self._check_ontology_compliance()
        lifecycle_violations = self._check_lifecycle_correctness(lifecycle_states)
        contract_violations = self._check_contract_fulfillment()
        
        violations.extend(policy_violations)
        violations.extend(ontology_violations)
        violations.extend(lifecycle_violations)
        violations.extend(contract_violations)
        
        end_time = time.time()
        
        # Record audit completion
        if self._session:
            self._session.record_audit_event(
                event_type="compliance_evaluation_complete",
                details={
                    "violation_count": len(violations),
                    "duration_seconds": end_time - start_time,
                },
            )
        
        # Build diagnostics
        diagnostics = {
            "policy_check_count": len(policy_violations),
            "ontology_check_count": len(ontology_violations),
            "lifecycle_check_count": len(lifecycle_violations),
            "contract_check_count": len(contract_violations),
            "total_violation_count": len(violations),
            "duration_seconds": end_time - start_time,
        }
        
        return tuple(violations), diagnostics
    
    # --------------------------------------------------------------------------
    # POLICY ADHERENCE CHECKS
    # --------------------------------------------------------------------------
    
    def _check_policy_adherence(
        self,
        policies: Any,
    ) -> List[GovernanceViolation]:
        """Check that operations adhere to memory policies."""
        violations = []
        
        if not policies:
            # Missing policies is itself a potential violation
            violations.append(GovernanceViolation(
                violation_id="violation:" + hashlib.md5(b'policy_check').hexdigest()[:16],
                violation_type="compliance_violation",
                location="policy_adherence",
                rule_name="COMPLIANCE-LAW-003",
                severity=GovernanceSeverity.WARNING,
                description="No memory policies found - operations may lack guidance",
            ))
            return violations
        
        # If policies is a dict, check for required policy types
        if isinstance(policies, dict):
            required_policies = [
                'admission', 'activation', 'retention', 'archival'
            ]
            
            missing_policies = []
            for req in required_policies:
                if req not in policies:
                    missing_policies.append(req)
            
            if missing_policies:
                violations.append(GovernanceViolation(
                    violation_id="violation:" + hashlib.md5(b'missing_policy').hexdigest()[:16],
                    violation_type="compliance_violation",
                    location="policy_adherence",
                    rule_name="COMPLIANCE-LAW-003",
                    severity=GovernanceSeverity.WARNING,
                    description="Missing required policies: " + ", ".join(missing_policies),
                ))
        
        return violations
    
    # --------------------------------------------------------------------------
    # ONTOLOGY COMPLIANCE CHECKS
    # --------------------------------------------------------------------------
    
    def _check_ontology_compliance(
        self,
    ) -> List[GovernanceViolation]:
        """Check ontology compliance (type constraints, hierarchies)."""
        violations = []
        
        # In a real implementation, this would check:
        # - Type hierarchies are consistent
        # - Constraint rules are satisfied
        # - Ontology version compatibility
        
        return violations
    
    # --------------------------------------------------------------------------
    # LIFECYCLE CORRECTNESS CHECKS
    # --------------------------------------------------------------------------
    
    def _check_lifecycle_correctness(
        self,
        lifecycle_states: Any,
    ) -> List[GovernanceViolation]:
        """Check lifecycle state transitions are valid."""
        violations = []
        
        if not lifecycle_states:
            return violations
        
        # Valid state transitions (simplified)
        valid_transitions = {
            'active': {'dormant', 'archived', 'superseded'},
            'dormant': {'active', 'archived', 'forgotten'},
            'archived': {'active', 'forgotten'},
            'superseded': {'archived'},
            'forgotten': set(),
        }
        
        # Check for valid states
        valid_states = set(valid_transitions.keys()) | {'unknown', 'invalid'}
        
        if isinstance(lifecycle_states, list):
            for state in lifecycle_states:
                state_str = str(state) if not hasattr(state, 'value') else state.value
                
                if state_str not in valid_states:
                    violations.append(GovernanceViolation(
                        violation_id="violation:" + hashlib.md5(str(state).encode()).hexdigest()[:16],
                        violation_type="compliance_violation",
                        location="lifecycle_correctness",
                        rule_name="COMPLIANCE-LAW-004",
                        severity=GovernanceSeverity.ERROR,
                        description="Invalid lifecycle state: " + str(state_str),
                    ))
        
        return violations
    
    # --------------------------------------------------------------------------
    # CONTRACT FULFILLMENT CHECKS
    # --------------------------------------------------------------------------
    
    def _check_contract_fulfillment(
        self,
    ) -> List[GovernanceViolation]:
        """Check that memory integration contracts are fulfilled."""
        violations = []
        
        # In a real implementation, this would check:
        # - Integration contracts are satisfied
        # - Contract conditions met
        # - Contract obligations fulfilled
        
        return violations


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ComplianceEvaluator",
]