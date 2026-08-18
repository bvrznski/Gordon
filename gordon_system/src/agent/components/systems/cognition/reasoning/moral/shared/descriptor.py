# Moral Descriptor - Phase 7.49
# ==============================

"""
Canonical Moral Descriptor.

A descriptor exposes moral reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MoralKind(Enum):
    """Categories of moral reasoning operations."""
    
    DUTY_BASED = "duty_based"          # Deontological ethics (Kantian)
    CONSEQUENTIALIST = "consequentialist"  # Consequence-based (Utilitarian)
    VIRTUE_BASED = "virtue_based"      # Virtue ethics (Aristotelian)
    CONTRACTUAL = "contractual"        # Social contract theory
    CARE_ETHICS = "care_ethics"        # Care and relationship-based
    RELATIVIST = "relativist"          # Context-dependent ethics


class MoralLifecycle(Enum):
    """Moral reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    IDENTIFYING = "identifying"        # Stakeholder identification
    EVALUATING = "evaluating"          # Ethical evaluation
    BALANCING = "balancing"            # Value/duty balancing
    JUSTIFYING = "justifying"          # Ethical justification
    VALIDATING = "validating"          # Validation phase
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class MoralDescriptor:
    """
    Descriptor exposing moral reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Moral kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what moral reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Moral classification
    moral_kind: MoralKind                   # What kind of moral reasoning?
    moral_mode: Optional[str] = None        # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: MoralLifecycle = MoralLifecycle.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did moral reasoning originate?
    
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
        """Check if moral reasoning completed."""
        return self.lifecycle_state == MoralLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if moral reasoning failed."""
        return self.lifecycle_state == MoralLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        moral_kind: MoralKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> MoralDescriptor:
        """Create a new moral descriptor."""
        return cls(
            descriptor_id=f"moral_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            moral_kind=moral_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: MoralLifecycle) -> MoralDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == MoralLifecycle.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MoralDescriptor",
    "MoralKind",
    "MoralLifecycle",
]