# Gordon Phase 5.7.1-I: Consciousness Constants and Enums
# ===============================================================================

"""
Canonical constants, enums, and configuration for the Consciousness capability.

This module defines:
    - Context lifecycle states
    - Contribution and projection kinds
    - Health and degradation modes
    - Query operation modes
    - Transition result statuses
"""

from enum import Enum, auto
from typing import Tuple


# =============================================================================
# CONTEXT LIFECYCLE STATES
# =============================================================================

class ContextState(Enum):
    """
    States of the current context lifecycle.
    
    State Flow:
        CONSTRUCTED → CONFIGURED → INITIALIZED → STARTING → READY → ACTIVE
            ↓          ↓           ↓            ↓         ↓        ↘
        [FAILED]   [FAILED]    [FAILED]     [FAILED]  [STOPPED]  STOPPING
                                                          ↓            ↓
                                                      [FAILED]───┐   [FAILED]
                                                                │
                                                              [PAUSED]→RESUMING
        
    Active transitions:
        ACTIVE ↔ PAUSED         - Temporarily suspends context publication
        ACTIVE → DRAINING       - Graceful shutdown, allows in-flight completion
        ACTIVE → DEGRADED       - Operational under limitations
    
    Failed recovery paths:
        Any state → FAILED      - Error detected during operation
        FAILED → RECOVERING     - Recovery initiated
    """
    
    # Initial states - infrastructure preparation
    CONSTRUCTED = "constructed"         # Capability instance created
    CONFIGURED = "configured"           # Configuration validated
    
    # Initialization states
    INITIALIZING = "initializing"       # Runtime structures prepared
    READY = "ready"                     # All dependencies validated and ready
    
    # Activation states
    STARTING = "starting"               # First transition preparation
    ACTIVE = "active"                   # Normal operation, admits transitions
    
    # Temporary suspension states
    PAUSING = "pausing"                 # Suspending publication
    PAUSED = "paused"                   # Suspended, may resume later
    RESUMING = "resuming"               # Resuming from paused state
    
    # Shutdown states
    DRAINING = "draining"               # Allowing in-flight completion
    STOPPING = "stopping"               # Final shutdown sequence
    STOPPED = "stopped"                 # Terminal (permanently ended)
    
    # Error/recovery states
    DEGRADING = "degrading"             # Entering degraded mode
    DEGRADED = "degraded"               # Operational under limitations
    RECOVERING = "recovering"           # Restoring from failure
    FAILING = "failing"                 # Failed, cannot continue safely
    FAILED = "failed"                   # Terminal failure state


# =============================================================================
# CONTRIBUTION KINDS
# =============================================================================

class ContributionKind(Enum):
    """
    Categories of contribution that can be submitted to Consciousness.
    
    Contributions are proposals for consideration - they do not guarantee
    admission to the current context, awareness, truth, or persistence.
    """
    
    # Workspace contributions
    WORKSPACE_CANDIDATE = "workspace_candidate"     # Candidate for workspace admission
    
    # Perception contributions
    PERCEPTUAL_PROJECTION = "perceptual_projection"  # Bound perceptual input
    
    # Working Memory contributions
    WORKING_MEMORY_ACTIVATION = "working_memory_activation"  # Active item
    
    # Cognition contributions
    COGNITIVE_PROPOSAL = "cognitive_proposal"       # Interpretation or reasoning
    
    # Personality contributions
    PERSONALITY_PROJECTION = "personality_projection"  # Preference or affect
    
    # Motivation contributions
    MOTIVATIONAL_PROJECTION = "motivational_projection"  # Goal or drive
    
    # Agency contributions  
    AGENCY_INTENT = "agency_intent"                 # Intent to act
    
    # Generic contribution
    GENERIC = "generic"                             # Unspecified kind


# =============================================================================
# DEGRADATION MODES
# =============================================================================

class DegradationMode(Enum):
    """
    Modes of capability degradation during partial failure.
    
    Degradation does not fabricate missing extension state.
    It represents the actual available capacity with explicit bounds.
    """
    
    # Extension availability issues
    OPTIONAL_SOURCE_UNAVAILABLE = "optional_source_unavailable"
    """Optional source registration unavailable."""
    
    OPTIONAL_EXTENSION_UNAVAILABLE = "optional_extension_unavailable"
    """Optional extension registration unavailable."""
    
    REQUIRED_SOURCE_UNAVAILABLE = "required_source_unavailable"
    """Required source registration unavailable."""
    
    REQUIRED_EXTENSION_UNAVAILABLE = "required_extension_unavailable"
    """Required extension registration unavailable."""
    
    # Extension state issues
    FIELD_REFERENCE_UNAVAILABLE = "field_reference_unavailable"
    """Experiential field reference unavailable."""
    
    INTENTIONAL_CONTEXT_UNAVAILABLE = "intentional_context_unavailable"
    """Intentional context reference unavailable."""
    
    TEMPORAL_CONTEXT_UNAVAILABLE = "temporal_context_unavailable"
    """Temporal context reference unavailable."""
    
    PRESENCE_UNAVAILABLE = "presence_unavailable"
    """Presence state unavailable."""
    
    AWARENESS_UNAVAILABLE = "awareness_unavailable"
    """Awareness state unavailable."""
    
    PERSPECTIVE_UNAVAILABLE = "perspective_unavailable"
    """Perspective state unavailable."""
    
    SITUATED_WORLD_UNAVAILABLE = "situated_world_unavailable"
    """Situated world reference unavailable."""
    
    # Capacity issues
    LAST_VALID_CONTEXT_RETAINED = "last_valid_context_retained"
    """Previous context retained due to failure."""
    
    LIMITED_CONSUMER_VIEWS = "limited_consumer_views"
    """Consumer views filtered due to degradation."""
    
    # Operational limits
    QUERY_TIMEOUT = "query_timeout"
    """Query operation timed out."""
    
    TRANSITION_TIMEOUT = "transition_timeout"
    """Transition operation timed out."""
    
    SOURCE_TIMEOUT = "source_timeout"
    """Source registration timeout."""
    
    EXTENSION_TIMEOUT = "extension_timeout"
    """Extension registration timeout."""


# =============================================================================
# HEALTH STATES
# =============================================================================

class HealthState(Enum):
    """
    Canonical health states for the Consciousness capability.
    
    Health reflects operational readiness, not context population.
    A populated context is not automatically healthy.
    An empty context may be valid during initialization or controlled operation.
    """
    
    # Initialization states
    UNCONFIGURED = "unconfigured"     # No configuration applied
    CONFIGURED = "configured"         # Configuration validated
    
    # Runtime states
    INITIALIZED = "initialized"       # Runtime structures ready
    STARTING = "starting"             # Starting up
    READY = "ready"                   # Ready for operations
    ACTIVE = "active"                 # Fully operational
    
    # Degradation states
    DEGRADED = "degraded"             # Operational under limitations
    STALE = "stale"                   # Context stale, needs refresh
    
    # Dependency issues
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    """Required dependency unavailable."""
    
    PRIVACY_DEGRADED = "privacy_degraded"
    """Privacy boundaries compromised."""
    
    TRUST_DEGRADED = "trust_degraded"
    """Trust boundaries compromised."""
    
    # Failure states
    TRANSITIONING = "transitioning"   # Transition in progress
    FAILED = "failed"                 # Terminal failure
    
    # Shutdown states
    STOPPING = "stopping"             # Stopping down
    STOPPED = "stopped"               # Stopped


# =============================================================================
# QUERY MODES
# =============================================================================

class QueryMode(Enum):
    """
    Modes of current context query access.
    
    Consumer views may filter private content, restricted sources,
    untrusted material, and security-sensitive state.
    """
    
    CURRENT_REFERENCE = "current_reference"
    """Return the current context reference."""
    
    CURRENT_COMPOSITE_SNAPSHOT = "current_composite_snapshot"
    """Return the full composite snapshot (filtered by policy)."""
    
    GENERATION_REFERENCE = "generation_reference"
    """Return only the generation reference."""
    
    HEALTH_ONLY = "health_only"
    """Return only health status."""
    
    DIAGNOSTICS_ONLY = "diagnostics_only"
    """Return only diagnostics snapshot."""
    
    CONSUMER_FILTERED_VIEW = "consumer_filtered_view"
    """Return filtered view based on consumer policy."""


# =============================================================================
# TRANSITION STATUSES
# =============================================================================

class TransitionStatus(Enum):
    """
    Status codes for context transitions.
    """
    
    PENDING = "pending"               # Transition initiated, not committed
    VALIDATING = "validating"         # Validation in progress
    COMMITTING = "committing"         # Commit in progress
    
    COMPLETED = "completed"           # Transition completed successfully
    ROLLED_BACK = "rolled_back"       # Failed transition rolled back
    PARTIAL = "partial"               # Partial success with degradation
    
    TIMEOUT = "timeout"               # Transition timed out
    CANCELLED = "cancelled"           # Transition cancelled
    
    CONFLICT = "conflict"             # Concurrent transition conflict
    INCOMPATIBLE = "incompatible"     # Extension incompatible
    
    # Validation failures
    INVALID_SOURCE = "invalid_source"
    """Source identity invalid."""
    
    INVALID_PROJECTION = "invalid_projection"
    """Projection structure invalid."""
    
    GENERATION_MISMATCH = "generation_mismatch"
    """Extension generation mismatch."""
    
    PRIVACY_VIOLATION = "privacy_violation"
    """Privacy boundary violation."""
    
    TRUST_VIOLATION = "trust_violation"
    """Trust boundary violation."""


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

MAXIMUM_SOURCES: int = 100
"""Maximum number of registered sources."""

MAXIMUM_EXTENSIONS: int = 25
"""Maximum number of registered extensions."""

MAXIMUM_PENDING_CONTRIBUTIONS: int = 1000
"""Maximum pending contributions before backpressure."""

MAXIMUM_TRANSITION_HISTORY: int = 100
"""Maximum transition records retained."""

MAXIMUM_SNAPSHOT_AGE_SECONDS: float = 60.0
"""Maximum age of current snapshot before considered stale."""

TRANSITION_TIMEOUT_SECONDS: float = 30.0
"""Timeout for transition operations."""

SOURCE_TIMEOUT_SECONDS: float = 5.0
"""Timeout for source registration."""

EXTENSION_TIMEOUT_SECONDS: float = 10.0
"""Timeout for extension registration."""

QUERY_TIMEOUT_SECONDS: float = 5.0
"""Timeout for query operations."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Context lifecycle states
    "ContextState",
    # Contribution kinds
    "ContributionKind",
    # Degradation modes
    "DegradationMode",
    # Health states
    "HealthState",
    # Query modes
    "QueryMode",
    # Transition statuses
    "TransitionStatus",
    # Configuration constants
    "MAXIMUM_SOURCES",
    "MAXIMUM_EXTENSIONS",
    "MAXIMUM_PENDING_CONTRIBUTIONS",
    "MAXIMUM_TRANSITION_HISTORY",
    "MAXIMUM_SNAPSHOT_AGE_SECONDS",
    "TRANSITION_TIMEOUT_SECONDS",
    "SOURCE_TIMEOUT_SECONDS",
    "EXTENSION_TIMEOUT_SECONDS",
    "QUERY_TIMEOUT_SECONDS",
)