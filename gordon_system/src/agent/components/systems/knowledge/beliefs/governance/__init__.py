# Knowledge Belief System - Governance Module - Phase 6.6
# =========================================================

"""
Governance module for belief governance evaluation.

This module evaluates beliefs against governance rules, identifying
unsupported, stale, redundant, conflicting, or unstable beliefs.
"""

from __future__ import annotations

import uuid
import time


class BeliefGovernanceEngine:
    """
    Evaluates beliefs against governance rules.
    
    Observational only - identifies issues without modifying beliefs
    directly. Reports findings and recommendations for action.
    """
    
    def __init__(self):
        """Initialize the governance engine."""
        self._evaluations: list = []
    
    @property
    def evaluation_count(self) -> int:
        """Get count of recorded evaluations."""
        return len(self._evaluations)
    
    def evaluate_belief(
        self,
        belief_id: str,
        acceptance_state: str,
        confidence: float,
        uncertainty: float,
        support_count: int,
        revision_count: int = 0,
    ) -> dict:
        """
        Evaluate a single belief for governance issues.
        
        Args:
            belief_id: ID of the belief
            acceptance_state: Current acceptance state
            confidence: Confidence measure (0.0-1.0)
            uncertainty: Uncertainty measure (0.0-1.0)
            support_count: Number of supporting evidence items
            revision_count: Number of revisions
            
        Returns:
            Evaluation result dictionary
        """
        violations = []
        recommendations = []
        
        # Rule 1: Unsupported beliefs
        if acceptance_state in ("accepted", "suspended") and support_count == 0:
            violations.append("unsupported_evidence")
            recommendations.append("add_supporting_evidence_or_reject")
        
        # Rule 2: Unstable beliefs (frequent revisions)
        if revision_count > 10:
            violations.append("excessive_revisions")
            recommendations.append("review_stability_concerns")
        
        # Rule 3: Very low confidence with high uncertainty
        if confidence < 0.2 and uncertainty > 0.8:
            violations.append("epistemic_instability")
            recommendations.append("evaluate_evidence_or_suspend")
        
        # Rule 4: Suspended beliefs without expected resolution
        if acceptance_state == "suspended" and not revision_count:
            recommendations.append("review_suspension_status")
        
        score = max(0.0, 1.0 - (len(violations) * 0.2))
        
        return {
            "belief_id": belief_id,
            "score": score,
            "violations": violations,
            "recommendations": recommendations,
            "metrics": {
                "acceptance_state": acceptance_state,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "support_count": support_count,
                "revision_count": revision_count,
            },
            "timestamp_utc": time.time(),
        }
    
    def evaluate_belief_set(
        self,
        belief_ids: list[str],
        metrics: dict,  # {belief_id -> {metrics}}
    ) -> dict:
        """
        Evaluate a set of beliefs for governance issues.
        
        Args:
            belief_ids: IDs of beliefs to evaluate
            metrics: Metrics for each belief
            
        Returns:
            Aggregate evaluation result dictionary
        """
        all_violations = []
        all_recommendations = []
        total_score = 0.0
        
        for bid in belief_ids:
            m = metrics.get(bid, {})
            result = self.evaluate_belief(
                belief_id=bid,
                acceptance_state=m.get("acceptance_state", "unknown"),
                confidence=m.get("confidence", 0.5),
                uncertainty=m.get("uncertainty", 0.5),
                support_count=m.get("supporting_evidence_count", 0),
                revision_count=m.get("revision_count", 0),
            )
            
            all_violations.extend(result["violations"])
            all_recommendations.extend(result["recommendations"])
            total_score += result["score"]
        
        avg_score = total_score / len(belief_ids) if belief_ids else 0.0
        
        return {
            "belief_count": len(belief_ids),
            "avg_score": avg_score,
            "total_violations": len(all_violations),
            "unique_violations": list(set(all_violations)),
            "recommendations": list(set(all_recommendations)),
            "detailed_results": {
                bid: metrics.get(bid, {})
                for bid in belief_ids
            },
            "timestamp_utc": time.time(),
        }
    
    def record_evaluation(
        self,
        evaluation_id: str,
        belief_ids: list[str],
        score: float,
        violations: list[str],
    ):
        """Record a governance evaluation."""
        self._evaluations.append({
            "evaluation_identity": evaluation_id,
            "belief_ids": belief_ids,
            "score": score,
            "violations": violations,
            "timestamp_utc": time.time(),
        })
    
    def get_evaluations(self, belief_id: str = None) -> list:
        """Get recorded evaluations."""
        if belief_id is None:
            return list(self._evaluations)
        return [
            e for e in self._evaluations
            if belief_id in e.get("belief_ids", [])
        ]


class GovernanceRecommendationEngine:
    """
    Generates recommendations based on governance findings.
    
    Suggests actions to address issues identified by the governance engine.
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self._recommendations: dict = {
            "unsupported_evidence": [
                "Add supporting evidence or reconsider acceptance",
                "Document why evidence is insufficient",
            ],
            "excessive_revisions": [
                "Review underlying assumptions",
                "Consider consolidating related revisions",
            ],
            "epistemic_instability": [
                "Evaluate evidence quality",
                "Consider suspension until more evidence available",
            ],
            "suspension_without_resolution": [
                "Set clear resolution criteria",
                "Schedule re-evaluation date",
            ],
        }
    
    def get_recommendations(self, violation_types: list[str]) -> list[str]:
        """
        Get recommendations for given violation types.
        
        Args:
            violation_types: List of violation type strings
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        for vtype in violation_types:
            if vtype in self._recommendations:
                recommendations.extend(self._recommendations[vtype])
        return list(set(recommendations))
    
    def generate_action_plan(
        self,
        violations: list[str],
        priority_threshold: float = 0.5,
    ) -> dict:
        """
        Generate an action plan based on violations.
        
        Args:
            violations: List of violation type strings
            priority_threshold: Score threshold for prioritization
            
        Returns:
            Action plan dictionary with priorities
        """
        recommendations = self.get_recommendations(violations)
        
        return {
            "violation_count": len(violations),
            "recommendation_count": len(recommendations),
            "priority_level": (
                "high" if len(violations) > 2 else
                "medium" if len(violations) > 0 else
                "low"
            ),
            "violations": violations,
            "recommendations": recommendations,
        }


class GovernanceHistory:
    """
    Maintains complete governance evaluation history for a belief.
    
    Tracks all governance evaluations over the lifetime of a belief,
    enabling trend analysis and audit trails.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the history tracker."""
        self._belief_id = belief_id
        self._entries: list = []
    
    @property
    def entry_count(self) -> int:
        """Get count of recorded entries."""
        return len(self._entries)
    
    def add_entry(
        self,
        evaluation_id: str,
        score: float,
        violations: list[str],
        timestamp_utc: float = None,
    ):
        """
        Add a governance history entry.
        
        Args:
            evaluation_id: ID of the evaluation
            score: Governance score (0.0-1.0)
            violations: List of violation types
            timestamp_utc: Entry timestamp (default: now)
        """
        self._entries.append({
            "evaluation_id": evaluation_id,
            "score": max(0.0, min(1.0, float(score))),
            "violations": list(violations),
            "timestamp_utc": timestamp_utc or time.time(),
        })
    
    def get_all_entries(self) -> list:
        """Get all history entries in order."""
        return list(self._entries)
    
    def get_latest_entry(self) -> dict | None:
        """Get the most recent entry."""
        if not self._entries:
            return None
        return self._entries[-1]
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_id": self._belief_id,
            "entry_count": len(self._entries),
            "latest_score": (
                self._entries[-1]["score"] if self._entries else 0.0
            ),
            "entries": self._entries,
        }


__all__ = [
    "BeliefGovernanceEngine",
    "GovernanceRecommendationEngine",
    "GovernanceHistory",
]