# Canonical Belief Revision Policy - Phase 4.9.5
# ================================================
"""
Policy definitions for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RevisionPolicy:
    """
    Canonical revision policy interface.
    
    Fields:
        minimum_precision:           Minimum precision for candidate acceptance
        contradiction_strategy:      How to handle contradictions (retain_both/replace/merge/defer/reject/mark_unresolved)
        confidence_threshold:        Minimum confidence for belief updates
        revision_conservatism:       Degree of conservatism in revisions
        evidence_accumulation:       Evidence accumulation policy
        schema_compatibility:        Schema compatibility requirements
    
    Rules:
        - Policy remains explicit
        - No hidden heuristics
        - Interchangeable implementations
    """
    minimum_precision: float = 0.7
    contradiction_strategy: str = "retain_both"
    confidence_threshold: float = 0.5
    revision_conservatism: float = 0.8  # Higher = more conservative
    evidence_accumulation: str = "cumulative"  # cumulative or decisive
    schema_compatibility: bool = True
    
    def __post_init__(self) -> None:
        if not (0.0 <= self.minimum_precision <= 1.0):
            raise ValueError("minimum_precision must be in [0.0, 1.0]")
        if not (0.0 <= self.confidence_threshold <= 1.0):
            raise ValueError("confidence_threshold must be in [0.0, 1.0]")
        if not (0.0 <= self.revision_conservatism <= 1.0):
            raise ValueError("revision_conservatism must be in [0.0, 1.0]")


@dataclass(frozen=True, slots=True)
class AcceptanceCriteria:
    """
    Criteria for accepting a revision candidate.
    
    Fields:
        precision_threshold:     Minimum required precision
        confidence_threshold:    Minimum required confidence
        evidence_count:          Minimum supporting evidence items
        hierarchy_level:         Accepted hierarchy levels
    
    Rules:
        - All criteria must be satisfied for acceptance
    """
    precision_threshold: float = 0.7
    confidence_threshold: float = 0.5
    evidence_count: int = 1
    hierarchy_levels: tuple[str, ...] = field(
        default_factory=lambda: ("sensory", "contextual", "conceptual", "abstract")
    )


class PolicyEnforcer:
    """
    Enforcer of revision policies.
    
    Rules:
        - Stateless enforcement
        - Deterministic output
    """
    
    def __init__(self, policy: RevisionPolicy | None = None) -> None:
        self.policy = policy or RevisionPolicy()
    
    def evaluate_candidate(
        self,
        candidate: dict[str, Any]
    ) -> AcceptanceCriteria:
        """
        Evaluate a revision candidate against the current policy.
        
        Args:
            candidate: RevisionCandidate representation
            
        Returns:
            AcceptanceCriteria with evaluation results
        """
        precision = candidate.get("confidence", 0.5)
        evidence = candidate.get("supporting_errors", [])
        
        return AcceptanceCriteria(
            precision_threshold=self.policy.minimum_precision,
            confidence_threshold=self.policy.confidence_threshold,
            evidence_count=len(evidence),
            hierarchy_levels=("sensory", "contextual", "conceptual", "abstract")
        )
    
    def should_accept(self, candidate: dict[str, Any]) -> bool:
        """
        Determine if a candidate should be accepted based on policy.
        
        Args:
            candidate: RevisionCandidate representation
            
        Returns:
            True if candidate meets all acceptance criteria
        """
        criteria = self.evaluate_candidate(candidate)
        
        precision = candidate.get("confidence", 0.5)
        
        return (
            precision >= criteria.precision_threshold and
            precision >= criteria.confidence_threshold
        )
    
    def apply_contradiction_strategy(
        self,
        contradictions: tuple[dict[str, Any], ...]
    ) -> dict[str, Any]:
        """
        Apply the policy's contradiction strategy to detected conflicts.
        
        Args:
            contradictions: Detected contradictions
            
        Returns:
            Strategy application result
        """
        if not contradictions:
            return {"action": "no_action", "reason": "no_contradictions"}
        
        if self.policy.contradiction_strategy == "retain_both":
            return {
                "action": "retain_both",
                "count": len(contradictions),
                "trace": ("policy_retain_both",)
            }
        
        elif self.policy.contradiction_strategy == "replace":
            return {
                "action": "replace",
                "count": len(contradictions),
                "trace": ("policy_replace",)
            }
        
        elif self.policy.contradiction_strategy == "merge":
            return {
                "action": "merge",
                "count": len(contradictions),
                "trace": ("policy_merge",)
            }
        
        elif self.policy.contradiction_strategy == "defer":
            return {
                "action": "defer",
                "count": len(contradictions),
                "reason": "awaiting_policy_change_or_new_evidence",
                "trace": ("policy_defer",)
            }
        
        else:
            # Default to retain_both
            return {
                "action": "retain_both",
                "count": len(contradictions),
                "trace": ("default_retain_both",)
            }


def create_policy(
    minimum_precision: float = 0.7,
    contradiction_strategy: str = "retain_both",
    confidence_threshold: float = 0.5
) -> RevisionPolicy:
    """
    Convenience function to create a revision policy.
    
    Args:
        minimum_precision: Minimum precision threshold
        contradiction_strategy: How to handle contradictions
        confidence_threshold: Minimum confidence for updates
        
    Returns:
        Configured RevisionPolicy instance
    """
    return RevisionPolicy(
        minimum_precision=minimum_precision,
        contradiction_strategy=contradiction_strategy,
        confidence_threshold=confidence_threshold
    )