# Memory Policy Conflict Resolution - Phase 5.1.5 Canonical Conflict Module
# ==========================================================================
"""
Memory Policy Conflict Resolution: Detect and report conflicts between policies.

Conflict Laws:
    CONFLICT-LAW-001: Conflicting recommendations remain explicit
    CONFLICT-LAW-002: Policies never silently override one another
    CONFLICT-LAW-003: Conflict evidence is preserved
    CONFLICT-LAW-004: Conflict provenance remains explicit
    CONFLICT-LAW-005: Conflict resolution authority is external
    CONFLICT-LAW-006: Conflict history is inspectable
    CONFLICT-LAW-007: Conflict reporting is observable

Conflict Types:
    DENY vs ALLOW   : One policy denies, another allows
    DIFFERENT DEFERS  : Different policies defer to different mechanisms
    INCOMPATIBLE RULES: Applied rules have conflicting requirements

Note: This module reports conflicts. It does NOT resolve them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
from enum import Enum


# =============================================================================
# CONFLICT KIND - What type of conflict is this?
# =============================================================================


class ConflictKind(Enum):
    """
    Kinds of policy conflicts.
    
    | Kind              | Description                                   |
    |-------------------|-----------------------------------------------|
    | DENY_VS_ALLOW     : One policy denies, another allows
    | INCOMPATIBLE_RULE : Applied rules have conflicting requirements
    | CONFLICTING_EVIDENCE: Policies use different evidence for same target
    | DIFFERENT_PRIORITY: Policies prioritize differently
    """
    
    DENY_VS_ALLOW = "deny_vs_allow"         # Deny vs Allow conflict
    INCOMPATIBLE_RULE = "incompatible_rule" # Rules conflict
    CONFLICTING_EVIDENCE = "conflicting_evidence"  # Evidence conflicts
    DIFFERENT_PRIORITY = "different_priority"      # Priority conflicts


# =============================================================================
# POLICY CONFLICT - Record of a detected conflict
# =============================================================================


@dataclass(frozen=True)
class PolicyConflict:
    """
    Record of a detected conflict between policy decisions.
    
    Fields:
        conflict_id:         Unique ID for this conflict record
        
        target_type:           Type of artifact/action being decided
        target_id:             ID of what's being decided
        
        # Conflict details
        kind_:                What type of conflict is this?
        
        # Conflicting parties
        first_policy:          First policy in conflict (policy_id, kind)
        second_policy:         Second policy in conflict (policy_id, kind)
        
        # Individual decisions that conflicted
        first_decision:        Decision from first policy
        second_decision:       Decision from second policy
        
        # Conflict resolution status
        reported_at_utc:       When was the conflict detected?
        resolved:              Has this conflict been resolved externally?
        resolution_method:     How was it resolved (if any)?
        
        # Evidence trail
        supporting_evidence:   Evidence supporting the conflict record
    """
    
    conflict_id: str                            # Unique ID for this conflict
    
    target_type: str                            # Type of artifact/action
    target_id: str                              # ID of what's being decided
    
    kind_: ConflictKind                         # What type of conflict?
    
    # Conflicting parties
    first_policy: Dict[str, Any]                # {policy_id, policy_kind}
    second_policy: Dict[str, Any]               # {policy_id, policy_kind}
    
    # Individual decisions
    first_decision: Dict[str, Any]              # Decision from first policy
    second_decision: Dict[str, Any]             # Decision from second policy
    
    # Resolution status
    reported_at_utc: float = field(default_factory=time.time)
    resolved: bool = False                      # Has external resolution occurred?
    resolution_method: Optional[str] = None     # How was it resolved?
    
    # Evidence trail
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    def is_deny_vs_allow(self) -> bool:
        """Check if this is a DENY vs ALLOW conflict."""
        return self.kind_ == ConflictKind.DENY_VS_ALLOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict record to dictionary representation."""
        return {
            "conflict_id": self.conflict_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "kind": self.kind_.value,
            "first_policy": dict(self.first_policy),
            "second_policy": dict(self.second_policy),
            "first_decision": dict(self.first_decision),
            "second_decision": dict(self.second_decision),
            "reported_at_utc": self.reported_at_utc,
            "resolved": self.resolved,
            "resolution_method": self.resolution_method,
            "supporting_evidence": list(self.supporting_evidence),
        }
    
    def explain(self) -> str:
        """Generate human-readable explanation of the conflict."""
        parts = [
            f"CONFLICT: {self.kind_.value.upper()}",
            f"Target: {self.target_type} ({self.target_id})",
            f"{self.first_policy.get('policy_id', 'unknown')} -> {self.first_decision.get('kind', '?')}",
            f"{self.second_policy.get('policy_id', 'unknown')} -> {self.second_decision.get('kind', '?')}",
        ]
        
        if self.resolved:
            parts.append(f"RESOLVED: {self.resolution_method}")
        else:
            parts.append("PENDING RESOLUTION")
        
        return " | ".join(parts)


# =============================================================================
# CONFLICT DETECTOR - Detect conflicts between policy decisions
# =============================================================================


class ConflictDetector:
    """
    Detect conflicts between multiple policy decisions.
    
    The detector analyzes a set of policy recommendations and identifies
    any conflicts that require external resolution.
    
    Policy Contract:
        Multiple policies evaluate the same target
             ↓
        ConflictDetector analyzes all decisions
             ↓
        Conflicts are reported (not resolved)
             ↓
        External authority resolves the conflict
        
    The detector NEVER modifies decisions or policies.
    """
    
    def __init__(
        self,
        detector_id: Optional[str] = None,
    ):
        """Initialize the conflict detector."""
        self.detector_id: str = detector_id or f"detector:{time.time()}"
        
    def detect_conflicts(
        self,
        decisions: List[Dict[str, Any]],
    ) -> Tuple[PolicyConflict, ...]:
        """
        Detect conflicts between multiple policy decisions.
        
        Args:
            decisions: List of individual decision dictionaries from policies
                Each should have: kind_, policy_id, policy_kind
            
        Returns:
            Tuple of detected PolicyConflict records (may be empty)
        """
        conflicts = []
        
        # Compare all pairs of decisions
        for i in range(len(decisions)):
            for j in range(i + 1, len(decisions)):
                conflict = self._analyze_pair(
                    decision_a=decisions[i],
                    decision_b=decisions[j],
                )
                
                if conflict is not None:
                    conflicts.append(conflict)
        
        return tuple(conflicts)
    
    def _analyze_pair(
        self,
        decision_a: Dict[str, Any],
        decision_b: Dict[str, Any],
    ) -> Optional[PolicyConflict]:
        """
        Analyze a pair of decisions for conflicts.
        
        Args:
            decision_a: First decision dictionary
            decision_b: Second decision dictionary
            
        Returns:
            PolicyConflict if conflict detected, None otherwise
        """
        kind_a = decision_a.get("kind", "")
        kind_b = decision_b.get("kind", "")
        
        policy_a = {
            "policy_id": decision_a.get("policy_id", "unknown"),
            "policy_kind": decision_a.get("policy_kind", "unknown"),
        }
        policy_b = {
            "policy_id": decision_b.get("policy_id", "unknown"),
            "policy_kind": decision_b.get("policy_kind", "unknown"),
        }
        
        target_type = decision_a.get("target_type", decision_b.get("target_type", "unknown"))
        target_id = decision_a.get("target_id", decision_b.get("target_id", "unknown"))
        
        # Check for DENY vs ALLOW conflict
        if self._is_deny_vs_allow(kind_a, kind_b):
            return PolicyConflict(
                conflict_id=f"conflict:{time.time()}-{id(policy_a)}-{id(policy_b)}",
                target_type=target_type,
                target_id=target_id,
                kind_=ConflictKind.DENY_VS_ALLOW,
                first_policy=policy_a,
                second_policy=policy_b,
                first_decision={"kind": kind_a, "confidence": decision_a.get("confidence", 1.0)},
                second_decision={"kind": kind_b, "confidence": decision_b.get("confidence", 1.0)},
                supporting_evidence=tuple(),
            )
        
        # Check for conflicting evidence (different policies with different confidence)
        if self._is_conflicting_evidence(decision_a, decision_b):
            return PolicyConflict(
                conflict_id=f"conflict:{time.time()}-{id(policy_a)}-{id(policy_b)}",
                target_type=target_type,
                target_id=target_id,
                kind_=ConflictKind.CONFLICTING_EVIDENCE,
                first_policy=policy_a,
                second_policy=policy_b,
                first_decision=decision_a,
                second_decision=decision_b,
                supporting_evidence=tuple(),
            )
        
        # No conflict detected
        return None
    
    def _is_deny_vs_allow(self, kind_a: str, kind_b: str) -> bool:
        """Check if we have a DENY vs ALLOW conflict."""
        return (kind_a == "deny" and kind_b == "allow") or (kind_a == "allow" and kind_b == "deny")
    
    def _is_conflicting_evidence(self, decision_a: Dict[str, Any], decision_b: Dict[str, Any]) -> bool:
        """Check if decisions have conflicting evidence patterns."""
        # If both policies give the same recommendation with very different confidence,
        # that might indicate conflicting evidence sources
        kind_a = decision_a.get("kind", "")
        kind_b = decision_b.get("kind", "")
        
        if kind_a != kind_b:
            return False
        
        conf_a = decision_a.get("confidence", 1.0)
        conf_b = decision_b.get("confidence", 1.0)
        
        # High confidence difference for same recommendation
        return abs(conf_a - conf_b) > 0.5
    
    def report_conflict(
        self,
        policy_id: str,
        policy_kind: str,
        target_type: str,
        target_id: str,
        reason: str,
        supporting_evidence: Tuple[str, ...] = tuple(),
    ) -> PolicyConflict:
        """
        Report a conflict that was detected externally.
        
        This is used when an external system detects a conflict
        and wants to register it in the conflict tracking system.
        
        Args:
            policy_id: ID of the policy involved
            policy_kind: Kind of policy involved
            target_type: Type of artifact/action being decided
            target_id: ID of what's being decided
            reason: Description of why this is a conflict
            supporting_evidence: Evidence supporting the conflict
            
        Returns:
            New PolicyConflict record
        """
        import uuid
        
        return PolicyConflict(
            conflict_id=f"conflict:{uuid.uuid4().hex[:12]}",
            target_type=target_type,
            target_id=target_id,
            kind_=ConflictKind.INCOMPATIBLE_RULE,  # Default for externally reported
            first_policy={"policy_id": policy_id, "policy_kind": policy_kind},
            second_policy={
                "policy_id": "external_reporter",
                "policy_kind": "coordination_system",
            },
            first_decision={"kind": "conflict_report", "reason": reason},
            second_decision={},
            supporting_evidence=supporting_evidence,
        )


# =============================================================================
# CONFLICT RESOLUTION REPORT - Record of resolution
# =============================================================================


@dataclass(frozen=True)
class ConflictResolutionReport:
    """
    Report of how a conflict was resolved.
    
    Fields:
        resolution_id:       Unique ID for this resolution
        
        original_conflict_id:  ID of the conflict that was resolved
        resolution_timestamp_utc: When was it resolved?
        
        # Resolution details
        resolver_type:         Who/what resolved it? (governance, coordination, etc.)
        resolution_method:     How was it resolved?
        final_decision:        What decision was reached?
        
        # Evidence trail
        supporting_evidence:   Evidence supporting the resolution
    """
    
    resolution_id: str                          # Unique ID for this resolution
    
    original_conflict_id: str                   # ID of resolved conflict
    resolution_timestamp_utc: float = field(default_factory=time.time)
    
    # Resolution details
    resolver_type: Optional[str] = None         # governance, coordination, etc.
    resolution_method: Optional[str] = None     # How was it resolved?
    final_decision: Optional[str] = None        # What decision was reached
    
    # Evidence trail
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resolution report to dictionary representation."""
        return {
            "resolution_id": self.resolution_id,
            "original_conflict_id": self.original_conflict_id,
            "resolution_timestamp_utc": self.resolution_timestamp_utc,
            "resolver_type": self.resolver_type,
            "resolution_method": self.resolution_method,
            "final_decision": self.final_decision,
            "supporting_evidence": list(self.supporting_evidence),
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Conflict kinds
    "ConflictKind",
    
    # Conflict record
    "PolicyConflict",
    
    # Detector
    "ConflictDetector",
    
    # Resolution report
    "ConflictResolutionReport",
]