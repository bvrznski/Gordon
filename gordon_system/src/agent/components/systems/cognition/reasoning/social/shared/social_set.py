# Social Set - Phase 7.32
# =======================

"""
Canonical Social Set.

A social set defines:
- Observed agents
- Available observations
- Modeling constraints  
- Privacy constraints
- Prediction policies

Social Sets remain immutable during reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SocialSet:
    """
    Social Set - defines the scope of social reasoning.
    
    A Social Set contains:
        - Participating agents being modeled
        - Available observations (raw data)
        - Reasoning constraints (confidence thresholds, etc.)
        - Privacy constraints (what can be shared)
        - Prediction policies (how predictions are generated)
        
    The set remains immutable during a single reasoning session.
    """
    
    # Identity
    social_set_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Participating agents
    participating_agents: Tuple[str, ...]     # Agents being modeled
    agent_observation_scope: Dict[str, str]   # Per-agent observation scope
    
    # Available observations (raw data)
    available_observations: Tuple[Any, ...] = ()  # Raw observation records
    
    # Reasoning constraints
    confidence_threshold: float = 0.5         # Minimum confidence for inferences
    max_history_depth: int = 10               # Maximum history to consider
    reasoning_mode: str = "default"           # Mode of reasoning
    
    # Privacy constraints
    privacy_policy: str = "confidentiality"   # Confidentiality level
    shareable_data_types: Tuple[str, ...] = ()  # What can be shared
    
    # Prediction policies
    prediction_horizon: int = 5               # How far ahead to predict
    prediction_confidence_threshold: float = 0.7  # Threshold for accepting predictions
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def agent_count(self) -> int:
        """Count of participating agents."""
        return len(self.participating_agents)
    
    def has_agent(self, agent_id: str) -> bool:
        """Check if an agent is in this social set."""
        return agent_id in self.participating_agents
    
    def get_observation_scope(self, agent_id: str) -> str:
        """Get the observation scope for a specific agent."""
        return self.agent_observation_scope.get(agent_id, "default")
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        participating_agents: List[str],
        confidence_threshold: float = 0.5,
        max_history_depth: int = 10,
    ) -> SocialSet:
        """Create a new social set."""
        return cls(
            social_set_id=f"socialset:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            participating_agents=tuple(participating_agents),
            agent_observation_scope={agent: "default" for agent in participating_agents},
            confidence_threshold=confidence_threshold,
            max_history_depth=max_history_depth,
        )
    
    def with_agent(self, agent_id: str) -> SocialSet:
        """Return a copy with an additional agent."""
        new_agents = list(self.participating_agents)
        if agent_id not in new_agents:
            new_agents.append(agent_id)
        return dataclass_replace(
            self,
            participating_agents=tuple(new_agents),
            agent_observation_scope={**self.agent_observation_scope, agent_id: "default"},
        )
    
    def without_agent(self, agent_id: str) -> SocialSet:
        """Return a copy with an agent removed."""
        new_agents = [a for a in self.participating_agents if a != agent_id]
        new_scope = {k: v for k, v in self.agent_observation_scope.items() if k != agent_id}
        return dataclass_replace(
            self,
            participating_agents=tuple(new_agents),
            agent_observation_scope=new_scope,
        )


@dataclass(frozen=True)
class SocialObservation:
    """
    An observation about an agent's behavior.
    
    Observations are the raw input to social reasoning. They can include:
        - Actions taken
        - Verbal statements
        - Facial expressions (if applicable)
        - Temporal patterns
        - Contextual information
    
    Each observation references its source and provides evidence for inference.
    """
    
    observation_id: str                       # Unique identifier
    timestamp_utc: float                      # When observed
    agent_id: str                            # Agent being observed
    observation_type: str                    # Type of observation (action, statement, etc.)
    observation_content: Any                 # The actual observation data
    source_context: str                      # Where it was observed
    confidence: float = 1.0                  # Confidence in the observation itself
    
    @classmethod
    def create(
        cls,
        agent_id: str,
        observation_type: str,
        observation_content: Any,
        source_context: str = "unknown",
        confidence: float = 1.0,
    ) -> SocialObservation:
        """Create a new social observation."""
        return cls(
            observation_id=f"observation:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            agent_id=agent_id,
            observation_type=observation_type,
            observation_content=observation_content,
            source_context=source_context,
            confidence=confidence,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SocialSet",
    "SocialObservation",
]