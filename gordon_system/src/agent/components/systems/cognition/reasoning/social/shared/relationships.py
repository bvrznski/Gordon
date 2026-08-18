# Relationship Management - Phase 7.32
# ====================================

"""
Canonical Relationship Management.

Relationship management evaluates:
- Cooperation
- Competition
- Authority  
- Dependency
- Trust
- Influence

Relationship management remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class RelationshipManagement:
    """
    Relationship management result.
    
    Represents Gordon's inferred relationships between agents:
        - Relationship type (cooperation, competition, etc.)
        - Relationship strength estimate
        - Participating agents  
        - Confidence in the relationship
        
    Relationships are traceable to interaction history.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    
    # Relationship details
    participating_agents: Tuple[str, ...]     # Agents in the relationship
    relationship_type: str = "neutral"        # cooperation, competition, authority, etc.
    relationship_strength: float = 0.0        # Estimate of strength (-1 to 1)
    
    # Confidence and provenance
    relationship_confidence: float = 0.0      # Confidence in the relationship estimate
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    revision_number: int = 1
    
    @property
    def is_positive_relationship(self) -> bool:
        """Check if this is a positive (cooperative) relationship."""
        return self.relationship_strength > 0.3 and self.relationship_type == "cooperation"
    
    @property
    def is_competitive_relationship(self) -> bool:
        """Check if this is a competitive relationship."""
        return self.relationship_type == "competition" or self.relationship_strength < -0.3
    
    def has_agent(self, agent_id: str) -> bool:
        """Check if an agent is participating in this relationship."""
        return agent_id in self.participating_agents
    
    @classmethod
    def create(
        cls,
        agents: List[str],
        relationship_type: str = "neutral",
    ) -> RelationshipManagement:
        """Create a new relationship management result."""
        return cls(
            management_id=f"relationship:{uuid.uuid4().hex[:16]}",
            participating_agents=tuple(agents),
            relationship_type=relationship_type,
            created_at_utc=time.time(),
        )
    
    def update_strength(self, new_strength: float) -> RelationshipManagement:
        """Return a copy with updated strength estimate."""
        return dataclass_replace(
            self,
            relationship_strength=new_strength,
            revision_number=self.revision_number + 1,
        )
    
    def with_confidence(self, confidence: float) -> RelationshipManagement:
        """Return a copy with updated confidence."""
        return dataclass_replace(
            self,
            relationship_confidence=confidence,
            revision_number=self.revision_number + 1,
        )


@dataclass(frozen=True)
class RelationshipModel:
    """
    A single relationship model with evidence.
    
    Each model includes:
        - Type of relationship
        - Estimated strength  
        - Evidence trail (interactions supporting this)
        - Timestamp
    """
    
    model_id: str                             # Unique identifier
    agent_a: str                             # First agent
    agent_b: str                             # Second agent
    timestamp_utc: float                     # When was this modeled?
    
    relationship_type: str = "neutral"       # cooperation, competition, etc.
    strength_estimate: float = 0.0           # Estimated strength (-1 to 1)
    
    evidence_trail: Tuple[Any, ...] = ()     # Interaction history supporting model
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence relationship."""
        return abs(self.strength_estimate) >= 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Create a dictionary representation."""
        return {
            "agent_a": self.agent_a,
            "agent_b": self.agent_b,
            "relationship_type": self.relationship_type,
            "strength": self.strength_estimate,
            "interaction_count": len(self.evidence_trail),
        }


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationshipManagement",
    "RelationshipModel",
]