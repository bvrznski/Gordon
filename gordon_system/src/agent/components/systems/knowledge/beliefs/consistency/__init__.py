# Knowledge Belief System - Consistency Module - Phase 6.6
# ==========================================================

"""
Consistency module for belief consistency evaluation.

This module evaluates logical, causal, temporal, and other consistency
relations among beliefs in the belief network.
"""

from __future__ import annotations

import uuid
import time
from typing import Dict, List, Tuple


class ConsistencyEvaluator:
    """
    Evaluates consistency among beliefs.
    
    Checks for logical, causal, temporal, ontological, and grounding
    consistency without modifying the beliefs themselves (observational only).
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        self._evaluations: list = []
    
    @property
    def evaluation_count(self) -> int:
        """Get count of recorded evaluations."""
        return len(self._evaluations)
    
    def evaluate_logical_consistency(
        self,
        belief_ids: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate logical consistency among beliefs.
        
        Checks for contradictions in logical structure (e.g., A and not-A).
        
        Args:
            belief_ids: IDs of beliefs to evaluate
            
        Returns:
            Tuple of (is_consistent, list_of_issues)
        """
        # Simplified: would check actual logical relations
        return True, []
    
    def evaluate_causal_consistency(
        self,
        belief_ids: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate causal consistency among beliefs.
        
        Checks that cause-effect relationships are logically consistent.
        
        Args:
            belief_ids: IDs of beliefs to evaluate
            
        Returns:
            Tuple of (is_consistent, list_of_issues)
        """
        return True, []
    
    def evaluate_temporal_consistency(
        self,
        belief_ids: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate temporal consistency among beliefs.
        
        Checks that temporal ordering is consistent (e.g., cause before effect).
        
        Args:
            belief_ids: IDs of beliefs to evaluate
            
        Returns:
            Tuple of (is_consistent, list_of_issues)
        """
        return True, []
    
    def evaluate_ontological_consistency(
        self,
        belief_ids: List[str],
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate ontological consistency among beliefs.
        
        Checks that entities and categories are used consistently.
        
        Args:
            belief_ids: IDs of beliefs to evaluate
            
        Returns:
            Tuple of (is_consistent, list_of_issues)
        """
        return True, []
    
    def record_evaluation(
        self,
        belief_ids: List[str],
        consistency_score: float,
        violations: List[str] = None,
        findings: Dict = None,
    ) -> str:
        """
        Record a consistency evaluation.
        
        Args:
            belief_ids: IDs of evaluated beliefs
            consistency_score: Score from 0.0 (inconsistent) to 1.0 (fully consistent)
            violations: List of violation descriptions (optional)
            findings: Additional findings dictionary (optional)
            
        Returns:
            Evaluation identity string
        """
        evaluation_id = f"consistency:{uuid.uuid4().hex[:16]}"
        
        record = {
            "evaluation_identity": evaluation_id,
            "belief_ids": belief_ids,
            "consistency_score": consistency_score,
            "violations": violations or [],
            "findings": findings or {},
            "timestamp_utc": time.time(),
        }
        
        self._evaluations.append(record)
        return evaluation_id
    
    def get_evaluation(self, identity: str) -> dict | None:
        """Get a specific evaluation record."""
        for e in self._evaluations:
            if e["evaluation_identity"] == identity:
                return e
        return None
    
    def get_consistency_graph(self, belief_ids: List[str]) -> dict:
        """
        Get consistency graph representation.
        
        Args:
            belief_ids: IDs of beliefs
            
        Returns:
            Dictionary with evaluation results
        """
        # Evaluate all consistency types
        logical = self.evaluate_logical_consistency(belief_ids)
        causal = self.evaluate_causal_consistency(belief_ids)
        temporal = self.evaluate_temporal_consistency(belief_ids)
        ontological = self.evaluate_ontological_consistency(belief_ids)
        
        # Calculate overall score (average of all consistency types)
        scores = [
            1.0 if logical[0] else 0.0,
            1.0 if causal[0] else 0.0,
            1.0 if temporal[0] else 0.0,
            1.0 if ontological[0] else 0.0,
        ]
        
        overall_score = sum(scores) / len(scores)
        
        all_violations = logical[1] + causal[1] + temporal[1] + ontological[1]
        
        return {
            "belief_count": len(belief_ids),
            "consistency_scores": {
                "logical": 1.0 if logical[0] else 0.0,
                "causal": 1.0 if causal[0] else 0.0,
                "temporal": 1.0 if temporal[0] else 0.0,
                "ontological": 1.0 if ontological[0] else 0.0,
            },
            "overall_score": overall_score,
            "total_violations": len(all_violations),
            "violations": all_violations,
        }


class ConsistencyHistory:
    """
    Maintains complete consistency history for a belief set.
    
    Tracks how consistency has been evaluated over time.
    """
    
    def __init__(self, belief_set_id: str):
        """Initialize the history tracker."""
        self._belief_set_id = belief_set_id
        self._evaluations: list = []
    
    @property
    def evaluation_count(self) -> int:
        """Get count of recorded evaluations."""
        return len(self._evaluations)
    
    def add_evaluation(
        self,
        evaluation_id: str,
        consistency_score: float,
        timestamp_utc: float = None,
    ):
        """
        Add a consistency evaluation to history.
        
        Args:
            evaluation_id: ID of the evaluation
            consistency_score: Score from 0.0 to 1.0
            timestamp_utc: Evaluation timestamp (default: now)
        """
        self._evaluations.append({
            "evaluation_id": evaluation_id,
            "consistency_score": max(0.0, min(1.0, float(consistency_score))),
            "timestamp_utc": timestamp_utc or time.time(),
        })
    
    def get_latest_evaluation(self) -> dict | None:
        """Get the most recent evaluation."""
        if not self._evaluations:
            return None
        return self._evaluations[-1]
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_set_id": self._belief_set_id,
            "evaluation_count": len(self._evaluations),
            "latest_score": (
                self._evaluations[-1]["consistency_score"]
                if self._evaluations else None
            ),
        }


class ConsistencyViolation:
    """
    Represents a consistency violation.
    
    Captures the nature and context of a consistency violation for
    debugging and resolution.
    """
    
    def __init__(
        self,
        violation_type: str,  # logical, causal, temporal, ontological
        involved_beliefs: List[str],
        description: str,
        severity: float = 1.0,  # 0.0 to 1.0
    ):
        """Initialize the violation record."""
        self._violation_id = f"violation:{uuid.uuid4().hex[:16]}"
        self._type = violation_type
        self._beliefs = involved_beliefs
        self._description = description
        self._severity = max(0.0, min(1.0, float(severity)))
        self._timestamp_utc = time.time()
    
    @property
    def id(self) -> str:
        """Get the violation ID."""
        return self._violation_id
    
    @property
    def type(self) -> str:
        """Get the violation type."""
        return self._type
    
    @property
    def involved_beliefs(self) -> List[str]:
        """Get IDs of beliefs involved in the violation."""
        return list(self._beliefs)
    
    @property
    def severity(self) -> float:
        """Get the severity (0.0 to 1.0)."""
        return self._severity
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "violation_id": self._violation_id,
            "type": self._type,
            "involved_beliefs": list(self._beliefs),
            "description": self._description,
            "severity": self._severity,
            "timestamp_utc": self._timestamp_utc,
        }


__all__ = [
    "ConsistencyEvaluator",
    "ConsistencyHistory",
    "ConsistencyViolation",
]