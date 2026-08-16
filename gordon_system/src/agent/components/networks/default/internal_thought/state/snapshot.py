# Internal Thought State Snapshot
# ===============================

"""
State snapshot for InternalThought instances.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Any
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InternalThoughtStateSnapshot:
    """
    Immutable state snapshot of an InternalThought at a point in time.
    
    Used for serialization, history tracking, and state reconstruction.
    """
    
    thought_id: str
    """Unique identifier for the thought."""
    
    concept: str
    """Core semantic content."""
    
    purpose: str
    """Cognitive purpose."""
    
    lifecycle_state: str
    """Current lifecycle state."""
    
    revision: int = 1
    """Thought revision number."""
    
    assessment_confidence: float = 0.5
    """Confidence level from assessment."""
    
    generated_at_utc: Optional[str] = None
    """ISO format timestamp of generation."""
    
    @classmethod
    def from_thought(cls, thought: Any) -> InternalThoughtStateSnapshot:
        """
        Create a state snapshot from an InternalThought instance.
        
        Args:
            thought: The thought to snapshot
            
        Returns:
            New InternalThoughtStateSnapshot instance
        """
        return cls(
            thought_id=thought.thought_id,
            concept=thought.concept,
            purpose=thought.purpose,
            lifecycle_state=thought.lifecycle_state,
            revision=thought.revision,
            assessment_confidence=thought.assessment.confidence,
            generated_at_utc=thought.provenance.generated_at_utc.isoformat() if thought.provenance.generated_at_utc else None,
        )