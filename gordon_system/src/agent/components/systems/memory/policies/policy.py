# Memory Policy Base Class - Phase 5.1.5 Canonical Policy Interface
# ==================================================================
"""
Memory Policy: The interface for all memory policy evaluations.

Policy Laws:
    POLICY-LAW-001: Every Memory Policy performs exactly one evaluation
    POLICY-LAW-002: Memory Policies never execute Memory Operations
    POLICY-LAW-003: Memory Policies never perform Lifecycle transitions
    POLICY-LAW-004: Memory Policies preserve Memory semantics
    POLICY-LAW-005: Memory Policies preserve provenance
    POLICY-LAW-006: Memory Policies expose explicit recommendations
    POLICY-LAW-007: Memory Policy behavior is independently testable
    POLICY-LAW-008: Memory Policy behavior remains deterministic

Policy Contract:
    Operation Proposal
         ↓
    Policy Evaluation (policy.evaluate(proposal))
         ↓
    Decision (recommendation)
    
Policies evaluate. They never execute.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid
from enum import Enum

# Import decision types from local module to avoid circular dependency issues
try:
    from .decision import DecisionKind, DecisionStatus, MemoryDecision
except ImportError:
    # Fallback for when running directly
    from decision import DecisionKind, DecisionStatus, MemoryDecision


# =============================================================================
# POLICY KINDS - What kinds of policies exist?
# =============================================================================


class PolicyKind(Enum):
    """
    Kinds of memory policies.
    
    | Kind         | Purpose                                         |
    |--------------|-------------------------------------------------|
    | ADMISSION    : Evaluate if artifact should be admitted
    | ACTIVATION   : Evaluate if artifact should become active
    | RETENTION    : Evaluate if artifact should be retained
    | ARCHIVAL     : Evaluate if artifact should be archived
    | SUPERSESSION : Evaluate if revision should supersede another
    | FORGETTING   : Evaluate if accessibility should decrease
    | COMPRESSION  : Evaluate if compression should occur
    | RECONSTRUCTION : Evaluate if reconstruction should occur
    | RECOVERY     : Evaluate if recovery should be attempted
    """
    
    ADMISSION = "admission"
    ACTIVATION = "activation"
    RETENTION = "retention"
    ARCHIVAL = "archival"
    SUPERSESSION = "supersession"
    FORGETTING = "forgetting"
    COMPRESSION = "compression"
    RECONSTRUCTION = "reconstruction"
    RECOVERY = "recovery"


# =============================================================================
# POLICY METRICS - Statistics about policy evaluation
# =============================================================================


@dataclass(frozen=True)
class PolicyMetrics:
    """
    Metrics about policy evaluation behavior.
    
    Fields:
        evaluations:      Total evaluations performed
        approvals:        Number of ALLOW decisions
        denials:          Number of DENY decisions
        deferrals:        Number of DEFER decisions
        escalations:      Number of ESCALATE decisions
        
        # Timing
        total_evaluation_time_ms: Total time spent evaluating (ms)
        avg_evaluation_time_ms:   Average evaluation time (ms)
        
        # Health
        last_evaluation_time_utc: When was the last evaluation?
    """
    
    evaluations: int = 0
    approvals: int = 0
    denials: int = 0
    deferrals: int = 0
    escalations: int = 0
    
    total_evaluation_time_ms: float = 0.0
    avg_evaluation_time_ms: float = 0.0
    
    last_evaluation_time_utc: float = field(default_factory=time.time)


# =============================================================================
# POLICY DIAGNOSTICS - Runtime diagnostics for a policy
# =============================================================================


@dataclass(frozen=True)
class PolicyDiagnostics:
    """
    Diagnostic information about policy evaluation.
    
    Fields:
        evaluation_id:     Unique ID for this evaluation
        policy_id:         Which policy is evaluating?
        start_time_utc:    When did the evaluation start?
        end_time_utc:      When did the evaluation complete?
        duration_ms:       How long did it take? (ms)
        
        # Context
        input_hash:        Hash of the input for traceability
        context:           Evaluation context
        
        # Diagnostics
        warnings:          Any warnings during evaluation
        errors:            Any errors encountered
    """
    
    evaluation_id: str
    policy_id: str
    start_time_utc: float
    end_time_utc: float
    duration_ms: float
    
    input_hash: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    errors: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# POLICY - Abstract base class for all memory policies
# =============================================================================


class MemoryPolicy(ABC):
    """
    Abstract base class for all memory policies.
    
    Every policy must implement the evaluate method.
    Policies NEVER execute actions; they only evaluate and recommend.
    
    Lifecycle:
        1. Policy is initialized with configuration
        2. Operation proposal is submitted to policy
        3. Policy.evaluate(proposal) is called
        4. Decision is produced with recommendation
        5. Executor decides whether to act on the decision
        
    Policy Contract:
        Proposal → Evaluation → Decision → Execution → Observation
    """
    
    def __init__(
        self,
        policy_id: Optional[str] = None,
        name: str = "unnamed",
        kind_: Optional[PolicyKind] = None,
    ):
        """
        Initialize the policy.
        
        Args:
            policy_id: Unique ID for this policy instance
            name: Human-readable name
            kind_: What kind of policy is this?
        """
        self.policy_id: str = policy_id or f"policy:{uuid.uuid4().hex[:12]}"
        self.name: str = name
        self.kind_: PolicyKind = kind_ or PolicyKind.ADMISSION
        
        # Metrics tracking
        self._metrics: PolicyMetrics = PolicyMetrics()
        
        # Revision info
        self.revision: int = 1
        
    @property
    def identity(self) -> Dict[str, Any]:
        """Get policy identity information."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "kind": self.kind_.value,
            "revision": self.revision,
        }
    
    @abstractmethod
    def evaluate(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> MemoryDecision:
        """
        Evaluate a policy proposal and produce a decision.
        
        This is the core method that all policies must implement.
        
        Args:
            proposal: The proposed action/transition to evaluate
                Required fields:
                    - target_type: What type of artifact/action?
                    - target_id: ID of what's being decided
                    - kind_: What kind of policy decision? (admission, retention, etc.)
                    
                Optional fields:
                    - artifact: Reference to the memory artifact
                    - current_state: Current lifecycle state
                    - proposed_state: Proposed new state
                    - evidence: Supporting evidence for evaluation
            context: Additional context for evaluation
                Workspace state, active goals, importance signals
            
        Returns:
            MemoryDecision with recommendation (ALLOW/DENY/DEFER/ESCALATE/PRIORITIZE/IGNORE/RETRY)
            
        Policy Laws:
            POLICY-LAW-001: Exactly one decision is produced per evaluation
            POLICY-LAW-002: No memory operations are executed
            POLICY-LAW-003: No lifecycle transitions are performed
            POLICY-LAW-006: Decision exposes explicit recommendation
        """
        pass
    
    def evaluate_with_diagnostics(
        self,
        proposal: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[MemoryDecision, PolicyDiagnostics]:
        """
        Evaluate with diagnostic information.
        
        Args:
            proposal: The policy proposal
            context: Additional evaluation context
            
        Returns:
            Tuple of (decision, diagnostics)
        """
        import hashlib
        
        start_time = time.time()
        
        # Create input hash for traceability
        input_str = str(proposal) + str(context)
        input_hash = hashlib.md5(input_str.encode()).hexdigest()
        
        try:
            decision = self.evaluate(proposal, context)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Update metrics
            self._metrics.evaluations += 1
            self._metrics.total_evaluation_time_ms += duration_ms
            self._metrics.avg_evaluation_time_ms = (
                self._metrics.total_evaluation_time_ms / self._metrics.evaluations
            )
            self._metrics.last_evaluation_time_utc = end_time
            
            # Track decision kind for approvals/denials
            if decision.is_allowed():
                self._metrics.approvals += 1
            elif decision.kind_ == DecisionKind.DENY:
                self._metrics.denials += 1
            elif decision.kind_ == DecisionKind.DEFER:
                self._metrics.deferrals += 1
            elif decision.kind_ == DecisionKind.ESCALATE:
                self._metrics.escalations += 1
            
            diagnostics = PolicyDiagnostics(
                evaluation_id=decision.decision_id,
                policy_id=self.policy_id,
                start_time_utc=start_time,
                end_time_utc=end_time,
                duration_ms=duration_ms,
                input_hash=input_hash,
                context=dict(context) if context else {},
                warnings=tuple(),
                errors=tuple(),
            )
            
            return decision, diagnostics
            
        except Exception as e:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            error_diagnostics = PolicyDiagnostics(
                evaluation_id=f"error:{uuid.uuid4().hex[:12]}",
                policy_id=self.policy_id,
                start_time_utc=start_time,
                end_time_utc=end_time,
                duration_ms=duration_ms,
                input_hash=input_hash,
                context=dict(context) if context else {},
                warnings=tuple(),
                errors=(f"Evaluation failed: {str(e)}",),
            )
            
            # Create a DENY decision with error info
            decision = MemoryDecision(
                decision_id=f"error:{uuid.uuid4().hex[:12]}",
                policy_id=self.policy_id,
                policy_kind=self.kind_.value,
                kind_=DecisionKind.DENY,
                target_type=proposal.get("target_type", "unknown"),
                target_id=proposal.get("target_id", "unknown"),
                confidence=0.0,
                uncertainty=1.0,
                supporting_evidence=tuple(),
                applied_rules=tuple(),
                diagnostics=(
                    f"Evaluation error: {str(e)}",
                    f"Duration: {duration_ms:.2f}ms",
                ),
            )
            
            return decision, error_diagnostics
    
    def get_metrics(self) -> PolicyMetrics:
        """Get current policy metrics."""
        return self._metrics
    
    def reset_metrics(self) -> None:
        """Reset all metrics to zero."""
        self._metrics = PolicyMetrics()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.policy_id}, name={self.name}, kind={self.kind_.value})"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def create_policy_decision(
    policy: MemoryPolicy,
    kind_: DecisionKind,
    target_type: str,
    target_id: str,
    confidence: float = 1.0,
    uncertainty: float = 0.0,
    supporting_evidence: Tuple[str, ...] = tuple(),
    applied_rules: Tuple[str, ...] = tuple(),
) -> MemoryDecision:
    """
    Helper function to create a decision from a policy.
    
    This is the canonical way policies produce decisions.
    
    Args:
        policy: The evaluating policy
        kind_: The decision kind (ALLOW/DENY/etc.)
        target_type: Type of artifact/action being decided
        target_id: ID of what's being decided
        confidence: Confidence in this decision (0.0-1.0)
        uncertainty: Uncertainty about this decision (0.0-1.0)
        supporting_evidence: References to evidence used
        applied_rules: Rules that were applied
        
    Returns:
        New MemoryDecision with all required fields populated
    """
    import uuid
    
    return MemoryDecision(
        decision_id=f"decision:{uuid.uuid4().hex[:12]}",
        policy_id=policy.policy_id,
        policy_kind=policy.kind_.value,
        kind_=kind_,
        target_type=target_type,
        target_id=target_id,
        confidence=confidence,
        uncertainty=uncertainty,
        importance=None,
        supporting_evidence=supporting_evidence,
        applied_rules=applied_rules,
        timestamp_utc=time.time(),
        status=DecisionStatus.EVALUATED,
        context={},
        diagnostics=tuple(),
    )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Policy kinds
    "PolicyKind",
    
    # Metrics
    "PolicyMetrics",
    
    # Diagnostics
    "PolicyDiagnostics",
    
    # Base class
    "MemoryPolicy",
    
    # Helper functions
    "create_policy_decision",
]