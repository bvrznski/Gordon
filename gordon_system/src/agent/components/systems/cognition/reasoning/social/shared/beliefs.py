# Belief Management - Phase 7.32
# =============================

"""
Canonical Belief Management.

Belief management evaluates:
- Belief consistency
- Belief uncertainty
- Knowledge gaps
- False beliefs  
- Shared beliefs
- Belief evolution

Belief management remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class BeliefManagement:
    """
    Belief management result.
    
    Represents Gordon's inferred beliefs about an agent:
        - Inferred belief statements
        - Confidence in each belief  
        - Supporting observations
        - Belief evolution history
        
    Every belief is traceable to specific observations.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    agent_id: str                            # Which agent?
    
    # Inferred beliefs
    inferred_beliefs: Tuple[Dict[str, Any], ...] = ()  # {content, confidence, type}
    
    # Belief properties
    belief_confidence: float = 0.0            # Average confidence across all beliefs
    knowledge_gaps: Tuple[str, ...] = ()      # What do we NOT know?
    
    # Evidence
    supporting_observations: Tuple[Any, ...] = ()  # Observations that support inferences
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    revision_number: int = 1
    inference_rules_applied: Tuple[str, ...] = ()
    
    @property
    def belief_count(self) -> int:
        """Count of inferred beliefs."""
        return len(self.inferred_beliefs)
    
    @property
    def has_high_confidence_beliefs(self) -> bool:
        """Check if there are high-confidence beliefs."""
        for belief in self.inferred_beliefs:
            if belief.get("confidence", 0.0) >= 0.7:
                return True
        return False
    
    def get_belief_by_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Get a specific belief by its content."""
        for belief in self.inferred_beliefs:
            if belief.get("content") == content:
                return belief
        return None
    
    @classmethod
    def create(cls, agent_id: str) -> BeliefManagement:
        """Create a new belief management result."""
        return cls(
            management_id=f"belief:{uuid.uuid4().hex[:16]}",
            agent_id=agent_id,
            created_at_utc=time.time(),
        )
    
    def with_beliefs(self, beliefs: List[Dict[str, Any]]) -> BeliefManagement:
        """Return a copy with additional beliefs."""
        return dataclass_replace(
            self,
            inferred_beliefs=tuple(list(self.inferred_beliefs) + list(beliefs)),
            revision_number=self.revision_number + 1,
        )
    
    def update_confidence(self, new_confidence: float) -> BeliefManagement:
        """Return a copy with updated average confidence."""
        return dataclass_replace(
            self,
            belief_confidence=new_confidence,
            revision_number=self.revision_number + 1,
        )


@dataclass(frozen=True)
class BeliefInference:
    """
    A single belief inference with evidence.
    
    Each inference includes:
        - The inferred belief content
        - Confidence level
        - Evidence trail (observations that support it)
        - Inference rule used
        - Timestamp
    """
    
    inference_id: str                         # Unique identifier
    agent_id: str                            # Agent being reasoned about
    timestamp_utc: float                     # When was this inferred?
    
    belief_content: str                      # What do we believe they think/feel/do?
    confidence: float = 0.5                  # Confidence in the inference
    
    evidence_trail: Tuple[Any, ...] = ()     # Raw observations supporting this
    inference_rule: str = "default"          # Rule used to make inference
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high-confidence belief."""
        return self.confidence >= 0.7
    
    def with_evidence(self, evidence: Any) -> BeliefInference:
        """Return a copy with additional evidence."""
        return dataclass_replace(
            self,
            evidence_trail=self.evidence_trail + (evidence,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "BeliefManagement",
    "BeliefInference",
]