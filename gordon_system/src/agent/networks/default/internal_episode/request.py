# Internal Episode Request Model
# ==============================

"""
Request model for specifying what episode should be created.

The request describes requirements without containing provider implementations.
It's the contract between episode consumers and the coordinator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, FrozenSet, Optional
from datetime import datetime


InternalEpisodeRequestId = str
"""Unique identifier for an episode request."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeRequest:
    """
    Immutable request describing what episode should be created.
    
    The request specifies requirements but does NOT contain provider implementations.
    It is the contract between episode consumers and the coordinator.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • episode_type: Category of internal cognition requested
        • purpose_statement: What this episode will do
        • context_id: Which context to use
        • context_revision: Expected context revision
        
    FIELDS:
        • requester: Who/what is making the request (InternalEpisodeRequester.*)
        • priority_hint: Advisory priority level (0.0 to 1.0)
        • urgency_hint: Advisory urgency level (0.0 to 1.0)
        • correlation_id: For distributed tracing
        • causation_id: If this request results from another event
        
    NOT INCLUDED:
        • Provider implementations (those are passed separately during coordination)
        • Runtime state or live references
        • Mutable collections
    """
    
    # Identity
    request_id: InternalEpisodeRequestId
    """Unique identifier for this request."""
    
    # Episode definition
    episode_type: str  # InternalEpisodeType.*
    """Category of internal cognition being requested."""
    
    purpose_statement: str
    """What this episode will do (human-readable)."""
    
    scope_json: Optional[str] = None
    """JSON-encoded scope constraints (optional, for boundedness)."""
    
    # Context binding
    context_id: str
    """The context ID to use."""
    
    context_revision: int
    """Expected revision of the bound context."""
    
    # Request metadata
    requester: str  # InternalEpisodeRequester.*
    """Who/what is making the request."""
    
    priority_hint: Optional[float] = None
    """Advisory priority level (0.0 to 1.0). Does not guarantee scheduler priority."""
    
    urgency_hint: Optional[float] = None
    """Advisory urgency level (0.0 to 1.0)."""
    
    # Correlation and causation
    correlation_id: Optional[str] = None
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if this request results from another event."""
    
    parent_request_id: Optional[str] = None
    """ID of the parent request (if derived)."""
    
    @classmethod
    def create(
        cls,
        episode_type: str,
        purpose_statement: str,
        context_id: str,
        context_revision: int,
        requester: str,
        **kwargs,
    ) -> InternalEpisodeRequest:
        """
        Create a new episode request.
        
        Args:
            episode_type: Category of internal cognition
            purpose_statement: Description of what the episode will do
            context_id: ID of the bound context
            context_revision: Expected revision of the bound context
            requester: Who is making the request (InternalEpisodeRequester.*)
            **kwargs: Other parameter overrides
            
        Returns:
            New InternalEpisodeRequest instance
        """
        return cls(
            request_id=f"request_{id(cls)}",
            episode_type=episode_type,
            purpose_statement=purpose_statement,
            context_id=context_id,
            context_revision=context_revision,
            requester=requester,
            **{k: v for k, v in kwargs.items() if k != "scope_json"},
        )
    
    @classmethod
    def from_episode(
        cls,
        episode_type: str,
        purpose_statement: str,
        context_id: str,
        context_revision: int,
        requester: str,
    ) -> InternalEpisodeRequest:
        """
        Create a request from an episode definition.
        
        Args:
            episode_type: Category of internal cognition
            purpose_statement: Description of what the episode will do
            context_id: ID of the bound context
            context_revision: Expected revision of the bound context
            requester: Who is making the request
            
        Returns:
            New InternalEpisodeRequest instance
        """
        return cls(
            request_id=f"request_{context_id}",
            episode_type=episode_type,
            purpose_statement=purpose_statement,
            context_id=context_id,
            context_revision=context_revision,
            requester=requester,
            priority_hint=None,
            urgency_hint=None,
        )


def is_internal_episode_request(value: object) -> bool:
    """Check if a value is an InternalEpisodeRequest instance."""
    return isinstance(value, InternalEpisodeRequest)