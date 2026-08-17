# Knowledge Belief System - Revision Module - Phase 6.6
# =======================================================

"""
Revision module for belief revision tracking.

This module handles the evolution of beliefs over time, preserving full
history and provenance for traceability and debugging.
"""

from __future__ import annotations

import uuid
import time


class BeliefRevisionManager:
    """
    Manages revision history for beliefs.
    
    Tracks all revisions of a belief, including changes to confidence,
    uncertainty, acceptance state, and other metrics.
    """
    
    def __init__(self):
        """Initialize the revision manager."""
        self._revisions: dict = {}  # belief_id -> list of revisions
    
    @property
    def total_revisions(self) -> int:
        """Get total number of tracked revisions."""
        return sum(len(r) for r in self._revisions.values())
    
    def create_revision(
        self,
        belief_id: str,
        revision_reason: str,
        new_state: dict,
        previous_state_ref: str = None,
    ) -> str:
        """
        Create a new revision record.
        
        Args:
            belief_id: ID of the belief being revised
            revision_reason: Description of why this revision occurred
            new_state: The new state of the belief
            previous_state_ref: Reference to previous revision (optional)
            
        Returns:
            Revision identity string
        """
        if belief_id not in self._revisions:
            self._revisions[belief_id] = []
        
        revision_id = f"revision:{uuid.uuid4().hex[:16]}"
        
        revision_record = {
            "revision_identity": revision_id,
            "belief_id": belief_id,
            "previous_revision": previous_state_ref,
            "new_state": new_state,
            "revision_reason": revision_reason,
            "timestamp_utc": time.time(),
            "provenance": {},
        }
        
        self._revisions[belief_id].append(revision_record)
        return revision_id
    
    def get_revisions(self, belief_id: str) -> list:
        """
        Get all revisions for a belief.
        
        Args:
            belief_id: ID of the belief
            
        Returns:
            List of revision records in chronological order
        """
        return list(self._revisions.get(belief_id, []))
    
    def get_latest_revision(self, belief_id: str) -> dict | None:
        """
        Get the most recent revision for a belief.
        
        Args:
            belief_id: ID of the belief
            
        Returns:
            Latest revision record or None
        """
        revisions = self.get_revisions(belief_id)
        if not revisions:
            return None
        return revisions[-1]
    
    def link_to_previous(
        self,
        revision_id: str,
        previous_revision_ref: str,
    ) -> bool:
        """
        Link a revision to its previous state.
        
        Args:
            revision_id: ID of the current revision
            previous_revision_ref: Reference to the previous revision
            
        Returns:
            True if linking succeeded, False otherwise
        """
        for belief_revisions in self._revisions.values():
            for rev in belief_revisions:
                if rev["revision_identity"] == revision_id:
                    rev["previous_revision"] = previous_revision_ref
                    return True
        return False
    
    def get_history_chain(self, belief_id: str) -> list[dict]:
        """
        Get a complete history chain for a belief.
        
        Args:
            belief_id: ID of the belief
            
        Returns:
            List of revision records in reverse chronological order
        """
        revisions = self.get_revisions(belief_id)
        return list(reversed(revisions))


class RevisionStrategyEngine:
    """
    Selects and applies revision strategies for beliefs.
    
    Supports different strategies like Bayesian update, evidence accumulation,
    and confidence adjustment.
    """
    
    def __init__(self):
        """Initialize the strategy engine."""
        self._strategies: dict = {}
    
    def register_strategy(
        self,
        strategy_name: str,
        apply_func: callable,
        applicability_conditions: list[str] = None,
    ):
        """
        Register a revision strategy.
        
        Args:
            strategy_name: Name of the strategy
            apply_func: Function that applies the strategy
            applicability_conditions: Conditions under which this strategy applies
        """
        self._strategies[strategy_name] = {
            "apply": apply_func,
            "conditions": applicability_conditions or [],
        }
    
    def select_strategy(
        self,
        conditions: list[str],
    ) -> tuple[str, callable] | None:
        """
        Select a strategy based on given conditions.
        
        Args:
            conditions: Current situation conditions
            
        Returns:
            Tuple of (strategy_name, apply_function) or None
        """
        for name, strategy in self._strategies.items():
            if not strategy["conditions"]:
                return name, strategy["apply"]
            
            if any(c in strategy["conditions"] for c in conditions):
                return name, strategy["apply"]
        
        # Default to first available strategy
        if self._strategies:
            name = next(iter(self._strategies))
            return name, self._strategies[name]["apply"]
        
        return None
    
    def apply_strategy(
        self,
        strategy_name: str,
        belief_state: dict,
        evidence: list[dict] = None,
    ) -> dict:
        """
        Apply a revision strategy to a belief state.
        
        Args:
            strategy_name: Name of the strategy to apply
            belief_state: Current belief state dictionary
            evidence: Optional evidence items for update
            
        Returns:
            Revised belief state dictionary
        """
        if strategy_name not in self._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy_func = self._strategies[strategy_name]["apply"]
        return strategy_func(belief_state, evidence or [])


class BayesianUpdateStrategy:
    """
    Implements Bayesian-style belief revision.
    
    Updates belief confidence based on new evidence using a simplified
    Bayesian update formula.
    """
    
    @staticmethod
    def calculate_posterior(
        prior_confidence: float,
        likelihood: float,  # P(evidence|belief) - how well the belief explains the evidence
        alternative_likelihood: float = None,  # P(evidence|not belief)
    ) -> float:
        """
        Calculate posterior confidence using Bayes' rule.
        
        Args:
            prior_confidence: Current confidence before new evidence
            likelihood: Probability of evidence given the belief is true
            alternative_likelihood: Probability of evidence given belief is false
            
        Returns:
            Posterior confidence after considering evidence
        """
        # Default alternative likelihood to 1 - likelihood if not specified
        if alternative_likelihood is None:
            alternative_likelihood = max(0.0, 1.0 - likelihood)
        
        # Bayes' rule: P(B|E) = P(E|B) * P(B) / [P(E|B) * P(B) + P(E|~B) * P(~B)]
        numerator = likelihood * prior_confidence
        denominator = (
            likelihood * prior_confidence +
            alternative_likelihood * (1.0 - prior_confidence)
        )
        
        if denominator == 0:
            return prior_confidence
        
        posterior = numerator / denominator
        return max(0.0, min(1.0, posterior))


class RevisionResultRecorder:
    """
    Records and tracks the results of belief revisions.
    
    Maintains complete records of what changed during each revision,
    enabling analysis of revision patterns over time.
    """
    
    def __init__(self):
        """Initialize the recorder."""
        self._results: list = []
    
    @property
    def total_records(self) -> int:
        """Get count of recorded revision results."""
        return len(self._results)
    
    def record_revision(
        self,
        belief_id: str,
        previous_state: dict,
        revised_state: dict,
        supporting_changes: list[str] = None,
    ) -> dict:
        """
        Record the result of a revision.
        
        Args:
            belief_id: ID of the belief that was revised
            previous_state: State before revision
            revised_state: State after revision
            supporting_changes: List of changes that triggered this revision
            
        Returns:
            Revision result record dictionary
        """
        # Calculate changes
        confidence_change = (
            revised_state.get("confidence", 0) - 
            previous_state.get("confidence", 0)
        )
        uncertainty_change = (
            revised_state.get("uncertainty", 0) -
            previous_state.get("uncertainty", 0)
        )
        
        record = {
            "belief_id": belief_id,
            "previous_state": previous_state.copy(),
            "revised_state": revised_state.copy(),
            "confidence_change": confidence_change,
            "uncertainty_change": uncertainty_change,
            "supporting_changes": supporting_changes or [],
            "timestamp_utc": time.time(),
        }
        
        self._results.append(record)
        return record
    
    def get_belief_revisions(self, belief_id: str) -> list:
        """
        Get all revision results for a specific belief.
        
        Args:
            belief_id: ID of the belief
            
        Returns:
            List of revision result records
        """
        return [
            r for r in self._results 
            if r["belief_id"] == belief_id
        ]
    
    def get_statistics(self) -> dict:
        """Get aggregate statistics about all revisions."""
        if not self._results:
            return {
                "total_revisions": 0,
                "avg_confidence_change": 0,
                "avg_uncertainty_change": 0,
            }
        
        confidence_changes = [r["confidence_change"] for r in self._results]
        uncertainty_changes = [r["uncertainty_change"] for r in self._results]
        
        return {
            "total_revisions": len(self._results),
            "avg_confidence_change": sum(confidence_changes) / len(confidence_changes),
            "avg_uncertainty_change": sum(uncertainty_changes) / len(uncertainty_changes),
            "max_confidence_increase": max(confidence_changes),
            "max_confidence_decrease": min(confidence_changes),
        }


__all__ = [
    "BeliefRevisionManager",
    "RevisionStrategyEngine",
    "BayesianUpdateStrategy",
    "RevisionResultRecorder",
]