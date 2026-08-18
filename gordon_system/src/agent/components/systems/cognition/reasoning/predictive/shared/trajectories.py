# Trajectory Model - Phase 7.40
# ==============================

"""
Trajectory model represents predicted state evolution over time.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class TrajectoryIdentity:
    """Unique identity for a trajectory."""
    
    trajectory_id: str
    semantic_identity: str
    
    @classmethod
    def create(cls) -> TrajectoryIdentity:
        """Create a new trajectory identity."""
        return cls(
            trajectory_id=f"trajectory:{uuid.uuid4().hex[:16]}",
            semantic_identity="trajectory-identity",
        )


@dataclass(frozen=True)
class TransitionSequence:
    """Sequence of state transitions in a trajectory."""
    
    transition_id: str
    source_state: Dict[str, Any]
    target_state: Dict[str, Any]
    transition_probability: float
    time_step: float
    
    @classmethod
    def create(
        cls,
        source_state: Dict[str, Any],
        target_state: Dict[str, Any],
        probability: float = 1.0,
        time_step: float = 1.0,
    ) -> TransitionSequence:
        """Create a transition sequence."""
        return cls(
            transition_id=f"trans:{uuid.uuid4().hex[:16]}",
            source_state=source_state,
            target_state=target_state,
            transition_probability=probability,
            time_step=time_step,
        )


@dataclass(frozen=True)
class TrajectoryConfidence:
    """Confidence assessment for a trajectory."""
    
    point_confidence: float  # Confidence at each point
    sequence_consistency: float  # How consistent is the whole sequence?
    critical_milestone_confidence: Dict[str, float]  # Confidence for key milestones
    
    @classmethod
    def create(
        cls,
        point_confidence: float = 0.5,
        sequence_consistency: float = 0.6,
        milestone_confidences: Dict[str, float] = None,
    ) -> TrajectoryConfidence:
        """Create trajectory confidence assessment."""
        return cls(
            point_confidence=point_confidence,
            sequence_consistency=sequence_consistency,
            critical_milestone_confidence=milestone_confidences or {},
        )


@dataclass(frozen=True)
class TrajectoryModel:
    """
    Trajectory model represents predicted state evolution.
    
    A trajectory contains:
        - Trajectory identity
        - Predicted path through state space
        - Transition sequence
        - Confidence estimates
        - Critical milestones
    """
    
    # Identity
    trajectory_identity: str
    
    # Predicted path
    initial_state: Dict[str, Any]
    predicted_states: List[Dict[str, Any]]
    time_steps: List[float]
    
    # Transitions
    transition_sequence: Tuple[TransitionSequence, ...] = ()
    
    # Confidence
    confidence: TrajectoryConfidence
    
    # Critical milestones
    critical_milestones: Dict[str, int] = field(default_factory=dict)  # milestone -> time step index
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    based_on_forecasts: List[str] = field(default_factory=list)  # Forecast IDs this is based on
    
    @classmethod
    def create(
        cls,
        initial_state: Dict[str, Any],
        predicted_states: List[Dict[str, Any]],
        time_steps: List[float],
        confidence: TrajectoryConfidence = None,
        critical_milestones: Dict[str, int] = None,
    ) -> TrajectoryModel:
        """Create a new trajectory model."""
        return cls(
            trajectory_identity=f"trajectory:{uuid.uuid4().hex[:16]}",
            initial_state=initial_state,
            predicted_states=predicted_states,
            time_steps=time_steps,
            confidence=confidence or TrajectoryConfidence.create(),
            critical_milestones=critical_milestones or {},
        )


__all__ = [
    "TrajectoryModel",
    "TrajectoryIdentity",
    "TransitionSequence",
    "TrajectoryConfidence",
]