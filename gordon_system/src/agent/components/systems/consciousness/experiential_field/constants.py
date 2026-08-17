# Gordon Phase 5.7.2-I: Experiential Field Constants
# ===============================================================================
#
# Constants, enumerations, and configuration defaults for the experiential field.
#

"""
Constants and Enumerations for Experiential Field Builder.

This module defines:
    - ContentKind: Types of content that can appear in the field
    - PrivacyClassification: Privacy levels for content
    - TrustClassification: Trust levels for content
    - DeduplicationPolicy: How to handle duplicate contributions
    - CapacityAction: Actions to take when capacity is exceeded
    - FieldStatus: Current state of a field snapshot
    - TransitionTrigger: What triggered a transition
"""

from __future__ import annotations

import enum


# =============================================================================
# CONTENT KINDS
# =============================================================================

class ContentKind(enum.Enum):
    """
    Types of content that can appear in the experiential field.
    
    Each kind represents a different category of current-context information
    that may be contributed by external subsystems.
    """
    
    # Workspace contributions - globally available semantic artifacts
    WORKSPACE = "workspace"
    
    # Perception projections - detected entities and events
    PERCEPTUAL = "perceptual"
    
    # Memory presentations - retrieved past content
    MEMORY = "memory"
    
    # Working memory - active task items
    WORKING_MEMORY = "working_memory"
    
    # Salience signals - attention priorities
    SALIENCE = "salience"
    
    # Attention references - focus indicators
    ATTENTION = "attention"
    
    # Personality projections - durable preferences and self-model
    PERSONALITY = "personality"
    
    # Motivation projections - active goals and drives
    MOTIVATION = "motivation"
    
    # Cognition proposals - interpretations and inferences
    COGNITION = "cognition"
    
    # Action feedback - execution results and state updates
    ACTION_FEEDBACK = "action_feedback"
    
    # Generic/contributed content from external sources
    GENERIC = "generic"


# =============================================================================
# PRIVACY CLASSIFICATIONS
# =============================================================================

class PrivacyClassification(enum.Enum):
    """
    Privacy levels for field contents.
    
    Used to control access and prevent unauthorized exposure of sensitive data.
    """
    
    # Publicly accessible (no restrictions)
    PUBLIC = "public"
    
    # Internal to the system
    INTERNAL = "internal"
    
    # Restricted to authorized components only
    RESTRICTED = "restricted"
    
    # Private - requires explicit authorization
    PRIVATE = "private"


# =============================================================================
# TRUST CLASSIFICATIONS
# =============================================================================

class TrustClassification(enum.Enum):
    """
    Trust levels for field contents.
    
    Field admission does not upgrade trust. Trust must be explicitly assigned
    by the source system and is preserved through normalization.
    """
    
    # Untrusted - external or unverified sources
    UNTRUSTED = "untrusted"
    
    # Low confidence but potentially valid
    LOW_CONFIDENCE = "low_confidence"
    
    # Medium trust - reasonably reliable
    MEDIUM = "medium"
    
    # High confidence from known reliable sources
    HIGH = "high"
    
    # Internal trusted sources (system-generated, verified)
    INTERNAL_TRUSTED = "internal_trusted"


# =============================================================================
# FRESHNESS STATES
# =============================================================================

class FreshnessState(enum.Enum):
    """
    Freshness state of a contribution or content item.
    
    Determines whether a contribution is considered current and valid.
    """
    
    # Currently fresh and valid
    CURRENT = "current"
    
    # Stale - may be acceptable but with lower priority
    STALE = "stale"
    
    # Expired - should be rejected
    EXPIRED = "expired"
    
    # Unknown freshness status
    UNKNOWN = "unknown"


# =============================================================================
# DUPLICATE HANDLING POLICIES
# =============================================================================

class DeduplicationPolicy(enum.Enum):
    """
    Policies for handling duplicate contributions.
    
    Each policy determines how to treat contributions with identical content.
    """
    
    # Reject subsequent duplicates
    REJECT_DUPLICATE = "reject_duplicate"
    
    # Merge metadata from later submissions
    MERGE_METADATA = "merge_metadata"
    
    # Replace stale content with fresh equivalent
    REPLACE_STALE = "replace_stale"
    
    # Keep both but link them as equivalents
    LINK_EQUIVALENTS = "link_equivalents"
    
    # Retain both without linking (for conflict preservation)
    RETAIN_BOTH = "retain_both"


# =============================================================================
# CAPACITY ACTIONS
# =============================================================================

class CapacityAction(enum.Enum):
    """
    Actions to take when capacity limits are exceeded.
    
    Used for enforcement policy when the field reaches its bounds.
    """
    
    # Reject new contributions entirely
    REJECT_NEW = "reject_new"
    
    # Remove lowest priority content to make room
    DROP_LOWEST_PRIORITY = "drop_lowest_priority"
    
    # Drop expired/stale content first
    DROP_EXPIRED = "drop_expired"
    
    # Truncate optional metadata
    TRUNCATE_OPTIONAL_METADATA = "truncate_optional_metadata"
    
    # Reduce relation count by dropping some relations
    REDUCE_RELATIONS = "reduce_relations"


# =============================================================================
# FIELD STATUSES
# =============================================================================

class FieldStatus(enum.Enum):
    """
    Current state of a field snapshot.
    
    Reflects the lifecycle stage and validity of a particular snapshot.
    """
    
    # Being constructed, not yet valid for consumers
    BUILDING = "building"
    
    # Valid and available for consumption
    VALID = "valid"
    
    # Degraded due to missing optional sources or partial failures
    DEGRADED = "degraded"
    
    # Superseded by a newer generation (may still be readable via history)
    SUPERSEDED = "superseded"
    
    # Invalid - should never be published or consumed
    INVALID = "invalid"


# =============================================================================
# TRANSITION TRIGGERS
# =============================================================================

class TransitionTrigger(enum.Enum):
    """
    What triggered a field transition.
    
    Used for logging, diagnostics, and policy decisions about transitions.
    """
    
    # Workspace update cycle triggered the build
    WORKSPACE_UPDATE = "workspace_update"
    
    # Perception update cycle triggered the build
    PERCEPTION_UPDATE = "perception_update"
    
    # Working memory transition triggered the build
    WORKING_MEMORY_TRANSITION = "working_memory_transition"
    
    # Agentic cycle boundary triggered the build
    AGENTIC_CYCLE_BOUNDARY = "agentic_cycle_boundary"
    
    # Action feedback triggered the build
    ACTION_FEEDBACK = "action_feedback"
    
    # Explicit refresh request triggered the build
    EXPLICIT_REFRESH = "explicit_refresh"
    
    # Recovery rebuild after failure
    RECOVERY_REBUILD = "recovery_rebuild"


# =============================================================================
# DEGRADATION MODES
# =============================================================================

class DegradationMode(enum.Enum):
    """
    Modes of degraded operation for the experiential field.
    
    Indicates which optional components or sources are unavailable.
    """
    
    # Optional perception source missing
    PERCEPTION_UNAVAILABLE = "perception_unavailable"
    
    # Optional memory presentation missing
    MEMORY_UNAVAILABLE = "memory_unavailable"
    
    # Optional working memory projection missing
    WORKING_MEMORY_UNAVAILABLE = "working_memory_unavailable"
    
    # Personality projection unavailable
    PERSONALITY_UNAVAILABLE = "personality_unavailable"
    
    # Motivation projection unavailable
    MOTIVATION_UNAVAILABLE = "motivation_unavailable"
    
    # Optional cognition proposals unavailable
    COGNITION_UNAVAILABLE = "cognition_unavailable"
    
    # Optional action feedback unavailable
    ACTION_FEEDBACK_UNAVAILABLE = "action_feedback_unavailable"
    
    # Capacity reduced due to limits
    CAPACITY_REDUCED = "capacity_reduced"
    
    # Relations reduced or simplified
    RELATIONS_REDUCED = "relations_reduced"


# =============================================================================
# DEFAULT CONFIGURATION VALUES
# =============================================================================

DEFAULT_MAX_CONTENT_COUNT: int = 1000
"""Maximum number of content items in a field snapshot."""

DEFAULT_MAX_RELATION_COUNT: int = 5000
"""Maximum number of relations in a field snapshot."""

DEFAULT_MAX_PAYLOAD_SIZE_BYTES: int = 1_048_576  # 1MB
"""Maximum total payload size in bytes."""

DEFAULT_MAX_PER_SOURCE_COUNT: int = 200
"""Maximum content items per source."""

DEFAULT_MAX_UNTRUSTED_CONTENT_COUNT: int = 100
"""Maximum untrusted content items allowed."""

DEFAULT_MAX_PRIVATE_CONTENT_COUNT: int = 50
"""Maximum private content items allowed."""

DEFAULT_MAX_PENDING_CONTRIBUTIONS: int = 1000
"""Maximum pending contributions in queue."""

DEFAULT_MAX_TRANSITION_HISTORY: int = 100
"""Maximum transition history entries to retain."""

DEFAULT_CAPACITY_ACTION: CapacityAction = CapacityAction.REJECT_NEW
"""Default action when capacity is exceeded."""

DEFAULT_DEDUPLICATION_POLICY: DeduplicationPolicy = DeduplicationPolicy.REJECT_DUPLICATE
"""Default policy for handling duplicates."""

# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "ContentKind",
    "PrivacyClassification",
    "TrustClassification",
    "FreshnessState",
    "DeduplicationPolicy",
    "CapacityAction",
    "FieldStatus",
    "TransitionTrigger",
    "DegradationMode",
    "DEFAULT_MAX_CONTENT_COUNT",
    "DEFAULT_MAX_RELATION_COUNT",
    "DEFAULT_MAX_PAYLOAD_SIZE_BYTES",
    "DEFAULT_MAX_PER_SOURCE_COUNT",
    "DEFAULT_MAX_UNTRUSTED_CONTENT_COUNT",
    "DEFAULT_MAX_PRIVATE_CONTENT_COUNT",
    "DEFAULT_MAX_PENDING_CONTRIBUTIONS",
    "DEFAULT_MAX_TRANSITION_HISTORY",
    "DEFAULT_CAPACITY_ACTION",
    "DEFAULT_DEDUPLICATION_POLICY",
)
