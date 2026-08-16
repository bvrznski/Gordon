# Memory Policy Decision - Phase 5.1.5 Canonical Decision Model
# ===============================================================
"""
Memory Policy Decision: The canonical output of policy evaluation.

A MemoryDecision is the sole output of a policy evaluation.
It represents a recommendation, NOT an executed action.

Decision Kinds:
    ALLOW       : Policy recommends allowing the proposed action
    DENY        : Policy recommends denying the proposed action
    DEFER       : Policy defers decision to other mechanisms
    ESCALATE    : Policy escalates decision to higher authority
    PRIORITIZE  : Policy prioritizes this action above others
    IGNORE      : Policy considers this action irrelevant
    RETRY       : Policy recommends retrying after changes

Decision Laws:
    DECISION-LAW-001: Every policy evaluation produces exactly one recommendation
    DECISION-LAW-002: Recommendations are explicit and inspectable
    DECISION-LAW-003: Recommendations preserve supporting evidence
    DECISION-LAW-004: Recommendations expose confidence metrics
    DECISION-LAW-005: Recommendations expose uncertainty metrics
    DECISION-LAW-006: Recommendations never mutate Memory directly
    DECISION-LAW-007: Decisions remain inspectable for audit
    DECISION-LAW-008: Decision evaluation is deterministic

Policy Contract:
    Policy → Evaluation → Decision → Execution → Observation
    
Policies evaluate. They never execute.
Executors decide based on recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# DECISION KINDS - What can a policy recommend?
# =============================================================================


class DecisionKind(Enum):
    """
    Kinds of decisions policies can produce.
    
    | Kind       | Meaning                                           |
    |------------|---------------------------------------------------|
    | ALLOW      | Policy recommends allowing the proposed action   |
    | DENY       | Policy recommends denying the proposed action    |
    | DEFER      | Policy defers decision to other mechanisms       |
    | ESCALATE   | Policy escalates decision to higher authority    |
    | PRIORITIZE | Policy prioritizes this action above others      |
    | IGNORE     | Policy considers this action irrelevant          |
    | RETRY      | Policy recommends retrying after changes         |
    """
    
    ALLOW = "allow"           # Recommend allowing the action
    DENY = "deny"             # Recommend denying the action
    DEFER = "defer"           # Defer decision to other mechanisms
    ESCALATE = "escalate"     # Escalate to higher authority
    PRIORITIZE = "prioritize" # Prioritize this action
    IGNORE = "ignore"         # Consider irrelevant
    RETRY = "retry"           # Recommend retrying after changes


# =============================================================================
# DECISION STATUS - What is the current state of a decision?
# =============================================================================


class DecisionStatus(Enum):
    """
    Status of a policy decision.
    
    | Status      | Description                                     |
    |-------------|-------------------------------------------------|
    | PROPOSED    | Decision proposed, awaiting aggregation         |
    | PENDING     | Decision pending evaluation                     |
    | EVALUATED   | Policy has evaluated the proposal               |
    | FINALIZED   | Final decision established                      |
    | EXECUTED    | Decision executed                               |
    | REJECTED    | Decision rejected (by another policy)           |
    | CANCELLED   | Decision cancelled                              |
    """
    
    PROPOSED = "proposed"       # Awaiting evaluation
    PENDING = "pending"         # Evaluation in progress
    EVALUATED = "evaluated"     # Policy has evaluated
    FINALIZED = "finalized"     # Final decision established
    EXECUTED = "executed"       # Decision executed
    REJECTED = "rejected"       # Rejected by another policy
    CANCELLED = "cancelled"     # Cancelled


# =============================================================================
# DECISION RECORD - The output of a policy evaluation
# =============================================================================


@dataclass(frozen=True)
class MemoryDecision:
    """
    Immutable decision produced by a policy evaluation.
    
    Every policy produces exactly one Decision when evaluated.
    A decision is a RECOMMENDATION, not an executed action.
    
    Fields:
        decision_id:       Unique ID for this decision
        policy_id:         Which policy made this decision?
        kind_:             What kind of decision is this? (ALLOW, DENY, etc.)
        
        # Target of decision
        target_type:       What type of artifact/action is being decided?
        target_id:         ID of the target
        
        # Evaluation metrics
        confidence:        Belief in this recommendation (0.0-1.0)
        uncertainty:       Uncertainty about this recommendation
        importance:        Importance of this decision (optional)
        
        # Evidence trail
        supporting_evidence: Tuple of evidence references
        applied_rules:       Which rules were applied?
        
        # Lifecycle
        timestamp_utc:     When was the decision made?
        status:            Current state of this decision
        
        # Context
        context:           Evaluation context (workspace, active goals, etc.)
        diagnostics:       Any diagnostic information
    """
    
    # Identity and policy info
    decision_id: str                            # Unique ID for this decision
    policy_id: str                              # Which policy made this?
    policy_kind: str                            # Kind of policy (admission, etc.)
    kind_: DecisionKind                         # ALLOW, DENY, DEFER, etc.
    
    # Target of the decision
    target_type: str                            # Artifact, operation, etc.
    target_id: str                              # ID of what's being decided
    
    # Evaluation metrics
    confidence: float = 1.0                     # 0.0 to 1.0
    uncertainty: float = 0.0                    # 0.0 to 1.0
    importance: Optional[str] = None            # critical/high/normal/low/deferred
    
    # Evidence trail
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    applied_rules: Tuple[str, ...] = field(default_factory=tuple)
    
    # Lifecycle
    timestamp_utc: float = field(default_factory=time.time)
    status: DecisionStatus = DecisionStatus.EVALUATED
    
    # Context and diagnostics
    context: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    def is_allowed(self) -> bool:
        """Check if this decision allows the action."""
        return self.kind_ == DecisionKind.ALLOW
    
    def is_denied(self) -> bool:
        """Check if this decision denies the action."""
        return self.kind_ == DecisionKind.DENY
    
    def is_deferred(self) -> bool:
        """Check if this decision defers to other mechanisms."""
        return self.kind_ == DecisionKind.DEFER
    
    def should_execute(self) -> bool:
        """
        Determine if this decision should be executed.
        
        A decision should execute if:
            - It's ALLOW or PRIORITIZE
            - It's not DENY, DEFER, ESCALATE, IGNORE, or RETRY
        """
        return self.kind_ in (DecisionKind.ALLOW, DecisionKind.PRIORITIZE)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary representation."""
        return {
            "decision_id": self.decision_id,
            "policy_id": self.policy_id,
            "policy_kind": self.policy_kind,
            "kind": self.kind_.value,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "importance": self.importance,
            "supporting_evidence": list(self.supporting_evidence),
            "applied_rules": list(self.applied_rules),
            "timestamp_utc": self.timestamp_utc,
            "status": self.status.value,
            "context": dict(self.context),
            "diagnostics": list(self.diagnostics),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryDecision:
        """Create decision from dictionary representation."""
        return cls(
            decision_id=data["decision_id"],
            policy_id=data["policy_id"],
            policy_kind=data["policy_kind"],
            kind_=DecisionKind(data["kind"]),
            target_type=data["target_type"],
            target_id=data["target_id"],
            confidence=data.get("confidence", 1.0),
            uncertainty=data.get("uncertainty", 0.0),
            importance=data.get("importance"),
            supporting_evidence=tuple(data.get("supporting_evidence", [])),
            applied_rules=tuple(data.get("applied_rules", [])),
            timestamp_utc=data.get("timestamp_utc", time.time()),
            status=DecisionStatus(data.get("status", "evaluated")),
            context=dict(data.get("context", {})),
            diagnostics=tuple(data.get("diagnostics", [])),
        )
    
    def explain(self) -> str:
        """
        Generate human-readable explanation of this decision.
        
        Returns:
            String explaining why this decision was made
        """
        parts = [
            f"Decision: {self.kind_.value.upper()}",
            f"Policy: {self.policy_kind}",
            f"Target: {self.target_type} ({self.target_id})",
            f"Confidence: {self.confidence:.2%}",
            f"Uncertainty: {self.uncertainty:.2%}",
        ]
        
        if self.importance:
            parts.append(f"Importance: {self.importance}")
        
        if self.applied_rules:
            parts.append(f"Rules applied: {', '.join(self.applied_rules)}")
        
        return " | ".join(parts)


# =============================================================================
# DECISION BUILDER - Mutable builder for decisions
# =============================================================================


class MemoryDecisionBuilder:
    """
    Mutable builder for constructing memory decisions.
    
    Allows step-by-step construction before producing an immutable decision.
    """
    
    def __init__(
        self,
        policy_id: str,
        policy_kind: str,
        kind_: DecisionKind,
        target_type: str,
        target_id: str,
    ):
        """Initialize the builder."""
        self._policy_id = policy_id
        self._policy_kind = policy_kind
        self._kind_ = kind_
        self._target_type = target_type
        self._target_id = target_id
        
        self._confidence = 1.0
        self._uncertainty = 0.0
        self._importance: Optional[str] = None
        self._evidence: List[str] = []
        self._rules: List[str] = []
        self._context: Dict[str, Any] = {}
        self._diagnostics: List[str] = []
    
    def set_confidence(self, confidence: float) -> "MemoryDecisionBuilder":
        """Set the confidence level (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "MemoryDecisionBuilder":
        """Set the uncertainty level (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_importance(self, importance: str) -> "MemoryDecisionBuilder":
        """Set the importance level."""
        valid_levels = ("critical", "high", "normal", "low", "deferred")
        if importance not in valid_levels:
            raise ValueError(f"Invalid importance: {importance}. Must be one of {valid_levels}")
        self._importance = importance
        return self
    
    def add_evidence(self, evidence_ref: str) -> "MemoryDecisionBuilder":
        """Add a reference to supporting evidence."""
        self._evidence.append(evidence_ref)
        return self
    
    def add_rule(self, rule_name: str) -> "MemoryDecisionBuilder":
        """Add an applied rule name."""
        self._rules.append(rule_name)
        return self
    
    def set_context(self, context: Dict[str, Any]) -> "MemoryDecisionBuilder":
        """Set the evaluation context."""
        self._context = dict(context)
        return self
    
    def add_diagnostics(self, diagnostics: Tuple[str, ...]) -> "MemoryDecisionBuilder":
        """Add diagnostic information."""
        self._diagnostics.extend(diagnostics)
        return self
    
    def build(self) -> MemoryDecision:
        """
        Build an immutable MemoryDecision from this builder.
        
        Returns:
            New MemoryDecision with all settings applied
        """
        import uuid
        decision_id = f"decision:{uuid.uuid4().hex[:12]}"
        
        return MemoryDecision(
            decision_id=decision_id,
            policy_id=self._policy_id,
            policy_kind=self._policy_kind,
            kind_=self._kind_,
            target_type=self._target_type,
            target_id=self._target_id,
            confidence=self._confidence,
            uncertainty=self._uncertainty,
            importance=self._importance,
            supporting_evidence=tuple(self._evidence),
            applied_rules=tuple(self._rules),
            status=DecisionStatus.EVALUATED,
            context=dict(self._context),
            diagnostics=tuple(self._diagnostics),
        )


# =============================================================================
# DECISION COMPARISON
# =============================================================================


def decisions_equal(
    decision1: MemoryDecision,
    decision2: MemoryDecision,
) -> bool:
    """
    Check if two decisions are equivalent.
    
    Two decisions are equal if they have the same policy, target, kind_,
    and confidence/uncertainty (within tolerance).
    
    Args:
        decision1: First decision
        decision2: Second decision
        
    Returns:
        True if decisions are equivalent
    """
    return (
        decision1.policy_id == decision2.policy_id
        and decision1.target_type == decision2.target_type
        and decision1.target_id == decision2.target_id
        and decision1.kind_ == decision2.kind_
        and abs(decision1.confidence - decision2.confidence) < 0.001
        and abs(decision1.uncertainty - decision2.uncertainty) < 0.001
    )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Decision kinds
    "DecisionKind",
    
    # Status
    "DecisionStatus",
    
    # Decision model
    "MemoryDecision",
    
    # Builder
    "MemoryDecisionBuilder",
    
    # Utilities
    "decisions_equal",
]