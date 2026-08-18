# Theory-of-Mind Management - Phase 7.32
# ======================================

"""
Canonical Theory-of-Mind Management.

Theory-of-Mind management evaluates:
- Agent identity
- Agent knowledge  
- Agent beliefs
- Agent goals
- Agent capabilities
- Agent uncertainty

Theory-of-Mind remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class TheoryOfMindManagement:
    """
    Theory-of-Mind management result.
    
    Represents Gordon's current understanding of another cognitive agent's mind:
        - Modeled identity estimate
        - Modeled knowledge estimate  
        - Modeled beliefs
        - Modeled goals
        - Modeled capabilities
        - Confidence in the model
        - Uncertainty estimates
        
    All inferred states remain explicit and traceable to observations.
    """
    
    # Identity
    management_id: str                        # Unique identifier for this management result
    modeled_agent_id: str                     # Which agent's mind is being modeled?
    
    # Modeled mental state (inferred)
    modeled_identity: str                     # Estimated identity of the agent
    modeled_beliefs: Tuple[Any, ...] = ()     # Inferred beliefs
    modeled_goals: Tuple[str, ...] = ()       # Inferred goals
    modeled_capabilities: Tuple[str, ...] = ()  # Inferred capabilities
    
    # Theory model
    theory_model: str = "basic"               # Which theory-of-mind theory?
    uncertainty_estimate: float = 0.5         # How uncertain are we?
    
    # Confidence and provenance
    confidence: float = 0.0                   # Overall confidence in the model
    supporting_observations: Tuple[Any, ...] = ()  # Raw observations that support this
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    revision_number: int = 1                  # For evolution tracking
    
    @property
    def is_confident(self) -> bool:
        """Check if model confidence meets threshold."""
        return self.confidence >= 0.5
    
    def has_belief(self, belief_content: str) -> bool:
        """Check if a specific belief is in the modeled set."""
        for belief in self.modeled_beliefs:
            if isinstance(belief, dict):
                if belief.get("content") == belief_content:
                    return True
            elif str(belief) == belief_content:
                return True
        return False
    
    @classmethod
    def create(
        cls,
        modeled_agent_id: str,
        modeled_identity: str,
    ) -> TheoryOfMindManagement:
        """Create a new theory-of-mind management result."""
        return cls(
            management_id=f"tom:{uuid.uuid4().hex[:16]}",
            modeled_agent_id=modeled_agent_id,
            modeled_identity=modeled_identity,
            created_at_utc=time.time(),
        )
    
    def with_beliefs(self, beliefs: List[Any]) -> TheoryOfMindManagement:
        """Return a copy with additional beliefs."""
        return dataclass_replace(
            self,
            modeled_beliefs=tuple(list(self.modeled_beliefs) + list(beliefs)),
        )
    
    def with_goals(self, goals: List[str]) -> TheoryOfMindManagement:
        """Return a copy with additional goals."""
        return dataclass_replace(
            self,
            modeled_goals=tuple(list(self.modeled_goals) + list(goals)),
        )
    
    def with_capabilities(self, capabilities: List[str]) -> TheoryOfMindManagement:
        """Return a copy with additional capabilities."""
        return dataclass_replace(
            self,
            modeled_capabilities=tuple(list(self.modeled_capabilities) + list(capabilities)),
        )
    
    def update_confidence(self, new_confidence: float) -> TheoryOfMindManagement:
        """Return a copy with updated confidence."""
        return dataclass_replace(
            self,
            confidence=new_confidence,
            revision_number=self.revision_number + 1,
        )


@dataclass(frozen=True)
class AgentMentalState:
    """
    A complete mental state estimate for an agent.
    
    Combines all inference results into a coherent picture of the agent's mind.
    """
    
    mental_state_id: str                      # Unique identifier
    agent_id: str                            # Which agent?
    timestamp_utc: float                     # When was this estimated?
    
    identity_estimate: str                   # Estimated identity
    beliefs: Tuple[Any, ...] = ()            # Inferred beliefs  
    goals: Tuple[str, ...] = ()              # Inferred goals
    intentions: Tuple[Any, ...] = ()         # Inferred intentions
    capabilities: Tuple[str, ...] = ()       # Inferred capabilities
    knowledge_state: str = "unknown"         # Estimated knowledge state
    
    confidence: float = 0.0                  # Overall confidence in this model
    uncertainty: float = 1.0                 # Uncertainty estimate
    
    @property
    def is_complete(self) -> bool:
        """Check if mental state has core components."""
        return len(self.identity_estimate) > 0 and self.confidence > 0.0
    
    def to_summary(self) -> Dict[str, Any]:
        """Create a summary dict of the mental state."""
        return {
            "agent_id": self.agent_id,
            "identity_estimate": self.identity_estimate,
            "belief_count": len(self.beliefs),
            "goal_count": len(self.goals),
            "intentions": len(self.intentions),
            "capabilities": list(self.capabilities),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TheoryOfMindManagement",
    "AgentMentalState",
]