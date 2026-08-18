# Intention Management - Phase 7.32
# ================================

"""
Canonical Intention Management.

Intention management evaluates:
- Immediate objectives
- Future objectives
- Decision tendencies
- Behavioral constraints  
- Commitment strength
- Expected plans

Intentions remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class IntentionManagement:
    """
    Intention management result.
    
    Represents Gordon's inferred intentions about an agent:
        - Inferred intention statements  
        - Confidence in each intention
        - Supporting evidence (behavioral observations)
        - Alternative intentions considered
        
    Intentions are always traceable to observable behavior.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    agent_id: str                            # Which agent?
    
    # Inferred intentions  
    inferred_intentions: Tuple[Dict[str, Any], ...] = ()  # {objective, confidence, timeline}
    
    # Intention model
    intention_model: str = "sequential"       # How are intentions structured?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    revision_number: int = 1
    
    @property
    def intention_count(self) -> int:
        """Count of inferred intentions."""
        return len(self.inferred_intentions)
    
    @property
    def has_high_confidence_intention(self) -> bool:
        """Check if there are high-confidence intentions."""
        for intention in self.inferred_intentions:
            if intention.get("confidence", 0.0) >= 0.7:
                return True
        return False
    
    def get_intention_by_objective(self, objective: str) -> Optional[Dict[str, Any]]:
        """Get a specific intention by its objective."""
        for intention in self.inferred_intentions:
            if intention.get("objective") == objective:
                return intention
        return None
    
    @classmethod
    def create(cls, agent_id: str) -> IntentionManagement:
        """Create a new intention management result."""
        return cls(
            management_id=f"intention:{uuid.uuid4().hex[:16]}",
            agent_id=agent_id,
            created_at_utc=time.time(),
        )
    
    def with_intentions(self, intentions: List[Dict[str, Any]]) -> IntentionManagement:
        """Return a copy with additional intentions."""
        return dataclass_replace(
            self,
            inferred_intentions=tuple(list(self.inferred_intentions) + list(intentions)),
            revision_number=self.revision_number + 1,
        )
    
    def update_confidence(self, new_confidence: float) -> IntentionManagement:
        """Return a copy with updated average confidence."""
        return dataclass_replace(
            self,
            revision_number=self.revision_number + 1,
        )


@dataclass(frozen=True)
class IntentionInference:
    """
    A single intention inference with evidence.
    
    Each inference includes:
        - The inferred intention objective
        - Confidence level  
        - Supporting behavioral evidence
        - Inference rule used
        - Timestamp
    """
    
    inference_id: str                         # Unique identifier
    agent_id: str                            # Agent being reasoned about
    timestamp_utc: float                     # When was this inferred?
    
    intention_objective: str                 # What do we believe they're trying to do?
    confidence: float = 0.5                  # Confidence in the inference
    
    supporting_evidence: Tuple[Any, ...] = ()   # Behavioral evidence supporting inference
    inference_rule: str = "default"          # Rule used to make inference
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence intention."""
        return self.confidence >= 0.7
    
    def with_evidence(self, evidence: Any) -> IntentionInference:
        """Return a copy with additional evidence."""
        return dataclass_replace(
            self,
            supporting_evidence=self.supporting_evidence + (evidence,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntentionManagement",
    "IntentionInference",
]