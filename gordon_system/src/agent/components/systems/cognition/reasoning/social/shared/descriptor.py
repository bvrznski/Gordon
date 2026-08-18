# Social Descriptor - Phase 7.32
# ==============================

"""
Canonical Social Descriptor.

A descriptor exposes social reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class SocialMode(Enum):
    """Modes of social reasoning."""
    
    THEORY_OF_MIND_CONSTRUCTION = "theory_of_mind_construction"     # Build agent models from observations
    BELIEF_INFERENCE = "belief_inference"                           # Infer beliefs from behavior
    INTENTION_INFERENCE = "intention_inference"                     # Infer intentions from actions
    RELATIONSHIP_MODELING = "relationship_modeling"                 # Model social relationships
    SOCIAL_PREDICTION = "social_prediction"                         # Predict agent behavior
    MULTI_AGENT_REASONING = "multi_agent_reasoning"                 # Reason about multiple agents


class SocialLifecycle(Enum):
    """Social session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    MODELING = "modeling"
    INFERRING = "inferring"
    PREDICTING = "predicting"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class SocialDescriptor:
    """
    Descriptor exposing social reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Social goal
        - Reasoning mode and constraints
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what social reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Social goal
    social_goal: str                          # What are we trying to understand?
    
    # Reasoning mode and constraints
    reasoning_mode: SocialMode = SocialMode.THEORY_OF_MIND_CONSTRUCTION
    reasoning_constraints: Tuple[str, ...] = ()  # Constraints on reasoning
    
    # Lifecycle state
    lifecycle_state: SocialLifecycle = SocialLifecycle.CREATED
    
    # Observation scope
    participating_agents: List[str] = field(default_factory=lambda: [])  # Agents being modeled
    observation_scope: str = "default"                               # Context of observations
    
    # Constraints
    confidence_threshold: float = 0.5         # Minimum confidence for accepting inferences
    max_history_depth: int = 10               # Maximum history depth to consider
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did social reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if social reasoning completed."""
        return self.lifecycle_state == SocialLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if social reasoning failed."""
        return self.lifecycle_state == SocialLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if social reasoning is archived."""
        return self.lifecycle_state == SocialLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        social_goal: str,
        reasoning_mode: SocialMode = SocialMode.THEORY_OF_MIND_CONSTRUCTION,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        participating_agents: Optional[List[str]] = None,
        observation_scope: str = "default",
        confidence_threshold: float = 0.5,
    ) -> SocialDescriptor:
        """Create a new social descriptor."""
        return cls(
            descriptor_id=f"social:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            social_goal=social_goal,
            reasoning_mode=reasoning_mode,
            participating_agents=participating_agents or [],
            observation_scope=observation_scope,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: SocialLifecycle) -> SocialDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == SocialLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class SocialSessionIdentity:
    """
    Immutable identity for a social session.
    
    Allows replay and verification of social reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> SocialSessionIdentity:
        """Create a new session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialDescriptor",
    "SocialSessionIdentity", 
    "SocialMode",
    "SocialLifecycle",
]