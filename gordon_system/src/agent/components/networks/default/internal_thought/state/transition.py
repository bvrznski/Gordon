# Internal Thought State Transition
# ==================================

"""
State transition record for InternalThought instances.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InternalThoughtStateTransition:
    """
    Immutable record of a state transition for an InternalThought.
    """
    
    thought_id: str
    """Unique identifier for the thought."""
    
    from_state: str
    """Previous lifecycle state."""
    
    to_state: str
    """New lifecycle state."""
    
    transition_time_utc: datetime
    """When transition occurred."""
    
    reason: str = ""
    """Reason for the transition."""
    
    metadata: Tuple[str, ...] = field(default_factory=tuple)
    """Additional metadata as strings."""