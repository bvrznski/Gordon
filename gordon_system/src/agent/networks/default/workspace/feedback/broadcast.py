# Workspace Broadcast Result Models
# ==================================

"""
Broadcast result models for workspace candidates.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# WORKSPACE BROADCAST RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceBroadcastResult:
    """
    Immutable broadcast result from external workspace authority.
    
    This is externally supplied feedback. The Default Network does not perform
    broadcast.
    
    PROPERTIES:
        • broadcast_id: Unique identifier for this broadcast
        • workspace_item_id: ID of the broadcast item in workspace
        • candidate_id: ID of the original candidate
        • candidate_revision: Revision that was broadcast
        • audience_reached: Audience kinds that received the broadcast
        • unavailable_consumers: Consumers that were unavailable
        • delivery_status: Status of delivery to each consumer
        • broadcast_time_utc: When broadcast occurred (ISO format string)
        • workspace_revision: Workspace state revision after broadcast
    """
    
    broadcast_id: str
    """Unique identifier for this broadcast."""
    
    workspace_item_id: Optional[str] = None
    """ID of the broadcast item in workspace."""
    
    candidate_id: str
    """ID of the original candidate."""
    
    candidate_revision: int = 1
    """Revision that was broadcast."""
    
    audience_reached: Tuple[str, ...] = field(default_factory=tuple)
    """Audience kinds that received the broadcast."""
    
    unavailable_consumers: Tuple[str, ...] = field(default_factory=tuple)
    """Consumers that were unavailable."""
    
    delivery_status: str = "delivered"
    """Status of delivery (delivered, partial, failed)."""
    
    broadcast_time_utc: str = ""
    """When broadcast occurred (ISO format string)."""
    
    workspace_revision: int = 1
    """Workspace state revision after broadcast."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Limitations on the broadcast content."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def successful_broadcast(
        cls,
        workspace_item_id: Optional[str],
        candidate_id: str,
        audience_reached: Tuple[str, ...] = (),
    ) -> WorkspaceBroadcastResult:
        """
        Create a broadcast result for a successful broadcast.
        
        Args:
            workspace_item_id: ID of the item in workspace (if assigned)
            candidate_id: ID of the original candidate
            audience_reached: Audience kinds that received the broadcast
            
        Returns:
            New WorkspaceBroadcastResult instance
        """
        return cls(
            broadcast_id=f"broadcast_{workspace_item_id or candidate_id}",
            workspace_item_id=workspace_item_id,
            candidate_id=candidate_id,
            audience_reached=audience_reached,
            delivery_status="delivered",
            broadcast_time_utc="",
        )
    
    @classmethod
    def partial_broadcast(
        cls,
        workspace_item_id: Optional[str],
        candidate_id: str,
        unavailable_consumers: Tuple[str, ...] = (),
    ) -> WorkspaceBroadcastResult:
        """
        Create a broadcast result for partial delivery.
        
        Args:
            workspace_item_id: ID of the item in workspace
            candidate_id: ID of the original candidate
            unavailable_consumers: Consumers that were unavailable
            
        Returns:
            New WorkspaceBroadcastResult instance (delivery_status=partial)
        """
        return cls(
            broadcast_id=f"broadcast_{workspace_item_id or candidate_id}",
            workspace_item_id=workspace_item_id,
            candidate_id=candidate_id,
            unavailable_consumers=unavailable_consumers,
            delivery_status="partial",
            broadcast_time_utc="",
        )


# =============================================================================
# WORKSPACE CONSUMPTION FEEDBACK
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceConsumptionFeedback:
    """
    Immutable consumption feedback from workspace consumers.
    
    Consumption feedback may inform future candidate preparation. It must not
    become surveillance of unrestricted downstream cognition.
    
    PROPERTIES:
        • feedback_id: Unique identifier for this feedback
        • workspace_item_id: ID of the consumed item
        • consumer_category: Category of consuming system
        • consumer_reference: Consumer reference (where permitted)
        • consumption_status: Status of consumption
        • acknowledged_value: Value acknowledged by consumer
        • produced_follow_up: Follow-up action taken (optional)
        • rejection_reason: Reason for rejection/ignore (if applicable)
    """
    
    feedback_id: str
    """Unique identifier for this feedback."""
    
    workspace_item_id: str
    """ID of the consumed item."""
    
    consumer_category: str = ""
    """Category of consuming system."""
    
    consumer_reference: Optional[str] = None
    """Consumer reference (where permitted)."""
    
    consumption_status: str = "consumed"
    """Status of consumption (consumed, ignored, rejected)."""
    
    acknowledged_value: float = 0.0
    """Value acknowledged by consumer (0.0 to 1.0)."""
    
    produced_follow_up_reference: Optional[str] = None
    """Follow-up action reference (if any)."""
    
    rejection_reason: Optional[str] = None
    """Reason for rejection or ignore."""
    
    consumed_at_utc: str = ""
    """When consumption occurred (ISO format string)."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def consumed(
        cls,
        workspace_item_id: str,
        consumer_category: str,
        acknowledged_value: float = 0.5,
    ) -> WorkspaceConsumptionFeedback:
        """
        Create consumption feedback for a consumed item.
        
        Args:
            workspace_item_id: ID of the consumed item
            consumer_category: Category of consuming system
            acknowledged_value: Value acknowledged by consumer
            
        Returns:
            New WorkspaceConsumptionFeedback instance (status=consumed)
        """
        return cls(
            feedback_id=f"feedback_{workspace_item_id}_{consumer_category}",
            workspace_item_id=workspace_item_id,
            consumer_category=consumer_category,
            consumption_status="consumed",
            acknowledged_value=acknowledged_value,
        )
    
    @classmethod
    def ignored(
        cls,
        workspace_item_id: str,
        consumer_category: str,
        reason: Optional[str] = None,
    ) -> WorkspaceConsumptionFeedback:
        """
        Create consumption feedback for an ignored item.
        
        Args:
            workspace_item_id: ID of the consumed item
            consumer_category: Category of consuming system
            reason: Reason for ignoring
            
        Returns:
            New WorkspaceConsumptionFeedback instance (status=ignored)
        """
        return cls(
            feedback_id=f"feedback_{workspace_item_id}_{consumer_category}",
            workspace_item_id=workspace_item_id,
            consumer_category=consumer_category,
            consumption_status="ignored",
            rejection_reason=reason or "No matching consumer criteria",
        )


# =============================================================================
# WORKSPACE EXPIRATION FEEDBACK
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceExpirationFeedback:
    """
    Immutable expiration feedback from workspace authority.
    
    PROPERTIES:
        • feedback_id: Unique identifier for this feedback
        • workspace_item_id: ID of the expired item
        • candidate_id: Original candidate ID
        • expiry_reason: Reason for expiration
        • expiry_time_utc: When expiration occurred (ISO format string)
    """
    
    feedback_id: str
    """Unique identifier for this feedback."""
    
    workspace_item_id: Optional[str] = None
    """ID of the expired item."""
    
    candidate_id: str
    """Original candidate ID."""
    
    expiry_reason: str = ""
    """Reason for expiration."""
    
    expiry_time_utc: str = ""
    """When expiration occurred (ISO format string)."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def expired_lifetime(
        cls,
        workspace_item_id: Optional[str],
        candidate_id: str,
    ) -> WorkspaceExpirationFeedback:
        """
        Create expiration feedback for lifetime expiration.
        
        Args:
            workspace_item_id: ID of the expired item (if assigned)
            candidate_id: Original candidate ID
            
        Returns:
            New WorkspaceExpirationFeedback instance
        """
        return cls(
            feedback_id=f"expiration_{workspace_item_id or candidate_id}",
            workspace_item_id=workspace_item_id,
            candidate_id=candidate_id,
            expiry_reason="lifetime_expired",
        )


# =============================================================================
# WORKSPACE EVICTION FEEDBACK
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceEvictionFeedback:
    """
    Immutable eviction feedback from workspace authority.
    
    PROPERTIES:
        • feedback_id: Unique identifier for this feedback
        • workspace_item_id: ID of the evicted item
        • candidate_id: Original candidate ID
        • eviction_reason: Reason for eviction
        • workspace_revision: Workspace state revision after eviction
    """
    
    feedback_id: str
    """Unique identifier for this feedback."""
    
    workspace_item_id: Optional[str] = None
    """ID of the evicted item."""
    
    candidate_id: str
    """Original candidate ID."""
    
    eviction_reason: str = ""
    """Reason for eviction."""
    
    workspace_revision: int = 1
    """Workspace state revision after eviction."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def evicted_capacity(
        cls,
        workspace_item_id: Optional[str],
        candidate_id: str,
    ) -> WorkspaceEvictionFeedback:
        """
        Create eviction feedback for capacity-based eviction.
        
        Args:
            workspace_item_id: ID of the evicted item (if assigned)
            candidate_id: Original candidate ID
            
        Returns:
            New WorkspaceEvictionFeedback instance
        """
        return cls(
            feedback_id=f"eviction_{workspace_item_id or candidate_id}",
            workspace_item_id=workspace_item_id,
            candidate_id=candidate_id,
            eviction_reason="capacity_exceeded",
        )


# =============================================================================
# WORKSPACE FEEDBACK PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceFeedbackProjection:
    """
    Immutable projection of all feedback for a workspace integration episode.
    
    The projection must not expose mutable workspace internals.
    
    PROPERTIES:
        • projection_id: Unique identifier for this projection
        • request_id: ID of the originating integration request
        • admission_decisions: All admission decisions received
        • broadcast_results: All broadcast results
        • consumption_feedback: All consumption feedback
        • expiration_feedback: All expiration feedback
        • eviction_feedback: All eviction feedback
        • unresolved_revision_requests: Unresolved revision requests
        • projected_at_utc: When projection was created (ISO format string)
    """
    
    projection_id: str
    """Unique identifier for this projection."""
    
    request_id: str
    """ID of the originating integration request."""
    
    admission_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of all admission decisions received."""
    
    broadcast_results: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of all broadcast results."""
    
    consumption_feedback: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of all consumption feedback items."""
    
    expiration_feedback: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of all expiration feedback items."""
    
    eviction_feedback: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of all eviction feedback items."""
    
    unresolved_revision_requests: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of unresolved revision requests."""
    
    projected_at_utc: str = ""
    """When projection was created (ISO format string)."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    @classmethod
    def new_projection(
        cls,
        request_id: str,
    ) -> WorkspaceFeedbackProjection:
        """
        Create a new feedback projection.
        
        Args:
            request_id: ID of the originating integration request
            
        Returns:
            New WorkspaceFeedbackProjection instance with empty collections
        """
        return cls(
            projection_id=f"projection_{request_id}",
            request_id=request_id,
            projected_at_utc="",
        )