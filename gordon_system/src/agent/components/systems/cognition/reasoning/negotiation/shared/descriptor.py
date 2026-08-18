# Negotiation Descriptor - Phase 7.42
# ====================================

"""
Canonical Negotiation Descriptor.

A descriptor exposes negotiation reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class NegotiationMode(Enum):
    """Modes of negotiation reasoning."""
    
    BARGAINING = "bargaining"                              # Distributive bargaining
    COMPROMISE = "compromise"                             # Finding middle ground
    COALITION_FORMATION = "coalition_formation"           # Building alliances
    CONFLICT_RESOLUTION = "conflict_resolution"           # Resolving disputes
    AGREEMENT_CONSTRUCTION = "agreement_construction"     # Crafting mutual agreement


class NegotiationLifecycle(Enum):
    """Negotiation session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    BARGAINING = "bargaining"
    NEGOTIATING = "negotiating"
    AGREEING = "agreeing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class NegotiationDescriptor:
    """
    Descriptor exposing negotiation reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Negotiation goal
        - Reasoning mode and constraints
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what negotiation occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                          # Unique descriptor identifier
    semantic_identity: str                      # Semantic identity (stable across runs)
    
    # Negotiation goal
    negotiation_goal: str                       # What are we trying to achieve?
    
    # Reasoning mode and constraints
    reasoning_mode: NegotiationMode = NegotiationMode.BARGAINING
    reasoning_constraints: Tuple[str, ...] = ()  # Constraints on reasoning
    
    # Lifecycle state
    lifecycle_state: NegotiationLifecycle = NegotiationLifecycle.CREATED
    
    # Participating agents
    participating_agents: List[str] = field(default_factory=lambda: [])  # Agents involved
    stakeholder_count: int = 0                              # Number of stakeholders
    
    # Constraints
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did negotiation originate?
    
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
        """Check if negotiation completed."""
        return self.lifecycle_state == NegotiationLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if negotiation failed."""
        return self.lifecycle_state == NegotiationLifecycle.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if negotiation is archived."""
        return self.lifecycle_state == NegotiationLifecycle.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        negotiation_goal: str,
        reasoning_mode: NegotiationMode = NegotiationMode.BARGAINING,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        participating_agents: Optional[List[str]] = None,
        stakeholder_count: int = 0,
    ) -> NegotiationDescriptor:
        """Create a new negotiation descriptor."""
        return cls(
            descriptor_id=f"negotiation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            negotiation_goal=negotiation_goal,
            reasoning_mode=reasoning_mode,
            participating_agents=participating_agents or [],
            stakeholder_count=stakeholder_count,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: NegotiationLifecycle) -> NegotiationDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == NegotiationLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class NegotiationSessionIdentity:
    """
    Immutable identity for a negotiation session.
    
    Allows replay and verification of negotiation reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> NegotiationSessionIdentity:
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
    "NegotiationDescriptor",
    "NegotiationSessionIdentity", 
    "NegotiationMode",
    "NegotiationLifecycle",
]