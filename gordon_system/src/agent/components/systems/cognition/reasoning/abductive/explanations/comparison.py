# Abduction Comparison - Phase 7.3
# ===============================

"""
Hypothesis comparison and ranking for abductive reasoning.

This module provides:
    - Hypothesis comparison mechanisms
    - Ranking strategies
    - Information gain estimation
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class RankingStrategy(Enum):
    """Strategies for ranking explanations."""
    
    COVERAGE_FIRST = "coverage_first"             # Maximize evidence coverage
    CONFIDENCE_FIRST = "confidence_first"         # Maximize confidence
    OCCAM = "occam"                               # Simplest explanation wins
    CAUSAL_COMPLETENESS = "causal_completeness"  # Most complete causal story
    BALANCED = "balanced"                         # Weighted combination


@dataclass(frozen=True)
class InformationGainEstimate:
    """
    Estimated information gain from acquiring new evidence.
    
    Helps prioritize which observations would most discriminally distinguish
    between competing hypotheses.
    """
    
    # Identity
    estimate_id: str                        # Unique identifier
    
    # Observation details
    candidate_observation: Dict[str, Any]   # What could we observe?
    affected_hypotheses: Tuple[str, ...]    # Which hypotheses does this affect?
    
    # Gain metrics
    expected_gain: float = 0.0              # Expected reduction in uncertainty
    discrimination_power: float = 0.5       # Ability to distinguish hypotheses
    
    # Cost factors
    acquisition_cost: float = 1.0           # Resource cost (lower is better)
    time_sensitive: bool = False            # Is timing important?
    
    @property
    def net_value(self) -> float:
        """Calculate net value (gain - cost)."""
        return self.expected_gain - (self.acquisition_cost * 0.1)
    
    @classmethod
    def create(
        cls,
        candidate_observation: Dict[str, Any],
        affected_hypothesis_ids: List[str],
        expected_gain: float = 0.5,
        discrimination_power: float = 0.5,
        acquisition_cost: float = 1.0,
    ) -> InformationGainEstimate:
        """Create a new information gain estimate."""
        return cls(
            estimate_id=f"info_gain:{uuid.uuid4().hex[:16]}",
            candidate_observation=candidate_observation,
            affected_hypotheses=tuple(affected_hypothesis_ids),
            expected_gain=expected_gain,
            discrimination_power=discrimination_power,
            acquisition_cost=acquisition_cost,
        )


@dataclass(frozen=True)
class EvidenceAcquisitionPlan:
    """
    Plan for acquiring missing evidence to improve abductive reasoning.
    
    This provides:
        - Priority list of acquisitions
        - Expected information gain per acquisition
        - Resource requirements
    
    Acquisition plans remain recommendations, not commitments.
    """
    
    # Identity
    plan_id: str                            # Unique identifier
    
    # Missing evidence targets
    missing_evidence_items: Tuple[Dict[str, Any], ...]  # What's missing?
    
    # Acquisition steps
    acquisition_steps: Tuple[Dict[str, Any], ...]       # How to get it?
    expected_information_gain: float = 0.5              # Total expected gain
    
    # Prioritization
    priority_scores: Dict[str, float] = field(default_factory=dict)  # item_id -> score
    
    @property
    def step_count(self) -> int:
        """Number of acquisition steps."""
        return len(self.acquisition_steps)
    
    def get_highest_priority_item(self) -> Optional[Dict[str, Any]]:
        """Get the highest priority missing evidence item."""
        if not self.missing_evidence_items:
            return None
        return max(
            self.missing_evidence_items,
            key=lambda m: self.priority_scores.get(m.get("missing_id", ""), 0)
        )
    
    @classmethod
    def create(
        cls,
        missing_evidence_items: List[Dict[str, Any]],
        acquisition_steps: List[Dict[str, Any]],
        expected_information_gain: float = 0.5,
    ) -> EvidenceAcquisitionPlan:
        """Create a new acquisition plan."""
        priority_scores = {}
        for i, item in enumerate(missing_evidence_items):
            priority_scores[item.get("missing_id", f"item_{i}")] = len(missing_evidence_items) - i
        
        return cls(
            plan_id=f"acquisition_plan:{uuid.uuid4().hex[:16]}",
            missing_evidence_items=tuple(missing_evidence_items),
            acquisition_steps=tuple(acquisition_steps),
            expected_information_gain=expected_information_gain,
            priority_scores=priority_scores,
        )


@dataclass(frozen=True)
class CausalExplanationGraph:
    """
    Graph representation of causal explanations.
    
    Nodes represent:
        - Evidence (observations)
        - Causes (potential causes)
        - Mechanisms (how effects occur)
        - Effects (observed outcomes)
        - Assumptions (underlying premises)
    
    Edges represent:
        - Causal dependencies
        - Support relationships
        - Contradiction relationships
    """
    
    # Identity
    graph_id: str                           # Unique identifier
    
    # Nodes
    explanation_nodes: Tuple[Dict[str, Any], ...]  # All nodes in the graph
    node_labels: Dict[str, str] = field(default_factory=dict)  # id -> label
    
    # Edges
    causal_edges: Tuple[Tuple[str, str], ...] = ()  # (source, target)
    support_edges: Tuple[Tuple[str, str], ...] = ()  # supports relationships
    
    # Assessment
    confidence: float = 0.5                 # Overall graph confidence
    complexity_score: float = 1.0           # Graph complexity
    
    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return len(self.explanation_nodes)
    
    @property
    def edge_count(self) -> int:
        """Total number of edges."""
        return len(self.causal_edges) + len(self.support_edges)
    
    @classmethod
    def create(
        cls,
        nodes: List[Dict[str, Any]],
        causal_connections: Optional[List[Tuple[str, str]]] = None,
        support_connections: Optional[List[Tuple[str, str]]] = None,
        confidence: float = 0.5,
    ) -> CausalExplanationGraph:
        """Create a new causal explanation graph."""
        node_labels = {n.get("node_id", f"node_{i}"): n.get("label", "") for i, n in enumerate(nodes)}
        
        return cls(
            graph_id=f"causal_graph:{uuid.uuid4().hex[:16]}",
            explanation_nodes=tuple(nodes),
            node_labels=node_labels,
            causal_edges=tuple(causal_connections or []),
            support_edges=tuple(support_connections or []),
            confidence=confidence,
            complexity_score=len(causal_connections or []) + len(support_connections or []),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RankingStrategy",
    "InformationGainEstimate",
    "EvidenceAcquisitionPlan",
    "CausalExplanationGraph",
]