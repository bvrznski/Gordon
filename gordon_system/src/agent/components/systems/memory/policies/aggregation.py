# Memory Policy Aggregation - Phase 5.1.5 Canonical Aggregation Module
# =======================================================================
"""
Memory Policy Aggregation: Combine multiple policy decisions into a final recommendation.

Aggregation Laws:
    AGGREGATION-LAW-001: Aggregation combines recommendations only
    AGGREGATION-LAW-002: Aggregation never executes Memory actions
    AGGREGATION-LAW-003: Aggregation preserves participating recommendations
    AGGREGATION-LAW-004: Aggregation preserves confidence metrics
    AGGREGATION-LAW-005: Aggregation exposes supporting evidence
    AGGREGATION-LAW-006: Aggregation remains inspectable
    AGGREGATION-LAW-007: Aggregation is deterministic

Aggregation Strategy:
    1. Collect all policy recommendations for a single evaluation
    2. Analyze recommendations (allow, deny, defer, etc.)
    3. Apply conflict resolution if needed
    4. Compute final confidence and uncertainty
    5. Produce aggregated recommendation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# AGGREGATION RESULT - Final decision after aggregating multiple policies
# =============================================================================


@dataclass(frozen=True)
class AggregatedDecision:
    """
    Decision produced by aggregating multiple policy recommendations.
    
    Fields:
        aggregation_id:      Unique ID for this aggregation result
        target_type:           Type of artifact/action being decided
        target_id:             ID of what's being decided
        
        # Recommendations from each policy
        individual_decisions:  Tuple of individual decisions that contributed
        policy_count:          Number of policies that participated
        
        # Aggregated recommendation
        final_decision:        Final decision after aggregation (ALLOW/DENY/DEFER/ESCALATE)
        confidence:            Confidence in the aggregated decision (0.0-1.0)
        uncertainty:           Uncertainty about the aggregated decision (0.0-1.0)
        
        # Aggregation details
        aggregation_method:    How were decisions combined?
        participating_policies: List of policy IDs that participated
        conflicts_resolved:    Were there any conflicts to resolve?
        
        # Timing
        timestamp_utc:         When was the aggregation performed?
    """
    
    aggregation_id: str                         # Unique ID for this aggregation
    
    target_type: str                            # Type of artifact/action
    target_id: str                              # ID of what's being decided
    
    # Individual decisions that contributed
    individual_decisions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    policy_count: int = 0                       # Number of policies that participated
    
    # Aggregated recommendation
    final_decision: Optional[str] = None        # ALLOW, DENY, DEFER, ESCALATE, etc.
    confidence: float = 1.0                     # 0.0 to 1.0
    uncertainty: float = 0.0                    # 0.0 to 1.0
    
    # Aggregation details
    aggregation_method: str = "majority_vote"   # How decisions were combined
    participating_policies: Tuple[str, ...] = field(default_factory=tuple)
    conflicts_resolved: bool = False            # Were there conflicts?
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated decision to dictionary representation."""
        return {
            "aggregation_id": self.aggregation_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "individual_decisions": [d if isinstance(d, dict) else getattr(d, 'to_dict', lambda: {})() for d in self.individual_decisions],
            "policy_count": self.policy_count,
            "final_decision": self.final_decision,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "aggregation_method": self.aggregation_method,
            "participating_policies": list(self.participating_policies),
            "conflicts_resolved": self.conflicts_resolved,
            "timestamp_utc": self.timestamp_utc,
        }
    
    def explain(self) -> str:
        """Generate human-readable explanation of the aggregation."""
        parts = [
            f"Aggregation: {self.final_decision or 'NO DECISION'}",
            f"Policies: {self.policy_count}",
            f"Method: {self.aggregation_method}",
            f"Confidence: {self.confidence:.2%}",
            f"Uncertainty: {self.uncertainty:.2%}",
        ]
        
        if self.conflicts_resolved:
            parts.append("CONFLICTS RESOLVED")
        
        return " | ".join(parts)


# =============================================================================
# POLICY AGGREGATOR - Aggregate decisions from multiple policies
# =============================================================================


class PolicyAggregator:
    """
    Aggregate policy recommendations into a final decision.
    
    Aggregation follows these rules:
        1. If ANY policy says DENY -> overall DENY (conservative)
        2. If ALL policies agree on ALLOW -> overall ALLOW
        3. If policies disagree -> DEFER to coordination system
        4. If ESCALATE from any policy -> overall ESCALATE
    
    The aggregator never executes actions; it only produces recommendations.
    """
    
    def __init__(
        self,
        aggregator_id: Optional[str] = None,
        method: str = "conservative",  # conservative, majority_vote, weighted
    ):
        """
        Initialize the aggregator.
        
        Args:
            aggregator_id: Unique ID for this aggregator
            method: Aggregation method (conservative, majority_vote, weighted)
        """
        self.aggregator_id: str = aggregator_id or f"aggregator:{time.time()}"
        self.method: str = method
        
    def aggregate(
        self,
        decisions: List[Dict[str, Any]],
        target_type: str,
        target_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AggregatedDecision:
        """
        Aggregate multiple policy decisions into a final recommendation.
        
        Args:
            decisions: List of individual decision dictionaries from policies
                Each should have: kind_, confidence, uncertainty, policy_id
            target_type: Type of artifact/action being decided
            target_id: ID of what's being decided
            context: Additional context for aggregation
            
        Returns:
            AggregatedDecision with final recommendation
        """
        if not decisions:
            # No decisions to aggregate - DEFER
            return self._create_aggregated_decision(
                target_type=target_type,
                target_id=target_id,
                final_decision="defer",
                confidence=0.5,
                uncertainty=0.5,
                participating_policies=tuple(),
                conflicts_resolved=False,
            )
        
        # Parse decisions and extract key information
        parsed = []
        policy_ids = set()
        approvals = 0
        denials = 0
        deferrals = 0
        escalations = 0
        
        for decision in decisions:
            kind_ = decision.get("kind", "")
            confidence = decision.get("confidence", 1.0)
            uncertainty = decision.get("uncertainty", 0.0)
            policy_id = decision.get("policy_id", "unknown")
            
            parsed.append({
                "kind": kind_,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "policy_id": policy_id,
            })
            
            policy_ids.add(policy_id)
            
            if kind_ == "allow":
                approvals += 1
            elif kind_ == "deny":
                denials += 1
            elif kind_ == "defer":
                deferrals += 1
            elif kind_ == "escalate":
                escalations += 1
        
        # Apply aggregation method
        final_decision, confidence, uncertainty = self._apply_aggregation(
            approvals=approvals,
            denials=denials,
            deferrals=deferrals,
            escalations=escalations,
            total=len(parsed),
        )
        
        return self._create_aggregated_decision(
            target_type=target_type,
            target_id=target_id,
            final_decision=final_decision,
            confidence=confidence,
            uncertainty=uncertainty,
            participating_policies=tuple(policy_ids),
            conflicts_resolved=(denials > 0 and approvals > 0),
            individual_decisions=tuple(parsed),
        )
    
    def _apply_aggregation(
        self,
        approvals: int,
        denials: int,
        deferrals: int,
        escalations: int,
        total: int,
    ) -> Tuple[str, float, float]:
        """
        Apply the aggregation method to produce final decision.
        
        Returns:
            Tuple of (final_decision, confidence, uncertainty)
        """
        if self.method == "conservative":
            # Conservative: DENY if any policy says DENY
            if escalations > 0:
                return ("escalate", 1.0 - (deferrals + escalations) / total, deferrals / total)
            elif denials > 0:
                return ("deny", 1.0 - denials / total, denials / total)
            elif approvals == total:
                return ("allow", 1.0, 0.0)
            else:
                return ("defer", 0.5, 0.5)
                
        elif self.method == "majority_vote":
            # Majority vote
            if approvals > total // 2:
                confidence = approvals / total
                return ("allow", confidence, 1.0 - confidence)
            elif denials > total // 2:
                confidence = denials / total
                return ("deny", confidence, 1.0 - confidence)
            else:
                return ("defer", 0.5, 0.5)
                
        else:  # weighted
            # Weight by confidence
            total_confidence = sum(d.get("confidence", 1.0) for d in [{}] * total)
            
            if escalations > 0:
                return ("escalate", 1.0 - deferrals / total, deferrals / total)
            elif denials > approvals:
                return ("deny", denials / total, 1.0 - denials / total)
            else:
                confidence = approvals / total
                return ("allow", confidence, 1.0 - confidence)
    
    def _create_aggregated_decision(
        self,
        target_type: str,
        target_id: str,
        final_decision: Optional[str],
        confidence: float,
        uncertainty: float,
        participating_policies: Tuple[str, ...],
        conflicts_resolved: bool,
        individual_decisions: Tuple[Dict[str, Any], ...] = tuple(),
    ) -> AggregatedDecision:
        """Create an aggregated decision record."""
        import uuid
        
        return AggregatedDecision(
            aggregation_id=f"aggregation:{uuid.uuid4().hex[:12]}",
            target_type=target_type,
            target_id=target_id,
            individual_decisions=individual_decisions,
            policy_count=len(participating_policies),
            final_decision=final_decision,
            confidence=confidence,
            uncertainty=uncertainty,
            aggregation_method=self.method,
            participating_policies=participating_policies,
            conflicts_resolved=conflicts_resolved,
            timestamp_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Aggregation result
    "AggregatedDecision",
    
    # Aggregator class
    "PolicyAggregator",
]