# Default Network Inputs
# ======================

"""
Canonical input models for Default Network coordination.

All input models are deeply immutable to ensure deterministic behavior,
replayability, and thread safety. No live objects, callbacks, or runtime
handles may be embedded in these models.

PHASE 4.3.12: Runtime-Neutral Input Contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# DEFAULT NETWORK INPUTS (legacy types for Phase 4.3 compatibility)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultProvenance:
    """
    Provenance tracking for inputs and outputs.
    
    Records where data came from without embedding implementation details.
    """
    
    # Input source identity
    source_id: str
    
    # Processing metadata
    timestamp_utc: datetime  # When input was created (not processed)
    
    # Configuration version (for reproducibility)
    config_version: Optional[str] = None
    
    # Optional caller reference (for traceability)
    caller_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class DefaultInputContext:
    """
    Context information for the DefaultNetwork.
    
    This represents state owned by higher layers (Memory, Consciousness, etc.).
    The DefaultNetwork consumes this but does NOT own or modify it.
    """
    
    # Current cognitive state
    active_focus_strength: Optional[float] = None  # 0.0 to 1.0
    
    # Task-related information
    current_task_criticality: Optional[float] = None  # 0.0 to 1.0
    unresolved_goal_count: int = 0
    
    # Memory state
    recent_memory_reactivation_count: int = 0
    memory_continuity_score: Optional[float] = None  # 0.0 to 1.0
    
    # Narrative context
    current_narrative_id: Optional[str] = None
    narrative_continuity: Optional[float] = None  # 0.0 to 1.0


@dataclass(frozen=True, slots=True)
class DefaultInput:
    """
    A single input unit for DefaultNetwork assessment.
    
    This is the canonical input contract. All fields must be provided or
    explicitly set to None (for optionals).
    
    Requirements:
        - Immutable
        - Validated (see validation module)
        - Bounded (no arbitrary growth)
        - Serialization-ready
        - No live objects, callbacks, or service handles
    """
    
    # Identity
    input_id: str
    
    # Source information
    source_id: str
    source_type: str  # e.g., "memory", "cognition", "consciousness"
    
    # Timestamp (required)
    timestamp_utc: datetime
    
    # Input category
    category: str  # e.g., "memory_reactivation", "reflection_candidate"
    
    # Content reference (pointer to actual content, not embedded)
    content_ref: Optional[str] = None
    
    # Semantic weight (0.0 to 1.0)
    semantic_weight: float = 0.5
    
    # Context hint
    context_hint: Optional[DefaultInputContext] = None
    
    # Provenance
    provenance: Optional[DefaultProvenance] = None


# =============================================================================
# DEFAULT NETWORK INPUT BATCH
# =============================================================================

DefaultInputBatch = Tuple[DefaultInput, ...]
"""
Bounded batch of inputs to the Default Network.

This is a tuple of DefaultInput records. The size is bounded by the
request's configuration (typically 10-100 inputs).

ARCHITECTURAL INVARIANTS:
    DEFAULT-BATCH-INV-001: Batch is immutable (tuple of frozen dataclasses)
    DEFAULT-BATCH-INV-002: No runtime references in batch items
    DEFAULT-BATCH-INV-003: Bounded by configuration
"""

# =============================================================================
# DEFAULT NETWORK INPUTS (Phase 4.3.12 canonical input contract)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkInputs:
    """
    Canonical inputs to one Default Network processing cycle.
    
    This is the complete set of inputs that may affect a single bounded
    semantic progression. All inputs must be supplied up front - the network
    never reaches out for additional data.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-INPUTS-INV-001: Inputs are immutable (deeply frozen)
        DEFAULT-INPUTS-INV-002: No live objects or runtime references
        DEFAULT-INPUTS-INV-003: All required data must be supplied up front
        
    CONTENT:
      - internal_context: The bound InternalContext for this request
      - existing_episode: Optional continuation of existing episode

    SPECIALIZED RESULTS:
      - capability_results: External capability results already supplied
      - projection_results: Projection results from external systems
      - external_decisions: Decisions from external authorities

    FEEDBACK:
      - feedback: Feedback items from previous processing cycles

    TIMESTAMPING:
      - evaluation_time: Canonical time for semantic operations
      - configuration_revision: Configuration version at evaluation time

    NOT INCLUDES:
      - Live Thread, Cycle, or Loop references
      - Runtime scheduling handles
      - Provider implementations
      - Callbacks or futures
      - Database connections

    NOT RESPONSIBLE FOR:
      - Fetching external results
      - Creating runtime tasks
      - Waiting for conditions
    """
    
    # Required fields (no defaults)
    internal_context_ref: str
    """Reference to the InternalContext."""
    
    context_revision: int
    """InternalContext revision at time of binding."""
    
    evaluation_time_utc: datetime
    """Canonical time reference for semantic operations."""
    
    # Optional fields with defaults - must come after required fields
    existing_episode_ref: Optional[str] = None
    """Optional reference to an existing InternalEpisode."""
    
    episode_state: Optional[str] = None
    """Current episode state (if continuation)."""
    
    identity_provider_state_ref: Optional[str] = None
    """Reference to identity provider state snapshot."""
    
    configuration_revision: Optional[str] = None
    """Configuration version at evaluation time."""
    
    capability_results: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of external capability results already provided."""
    
    projection_results: Tuple[str, ...] = field(default_factory=tuple)
    """Projection result IDs from external systems."""
    
    external_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """External authority decision IDs."""
    
    feedback: Tuple[str, ...] = field(default_factory=tuple)
    """Feedback items from previous processing cycles."""
    
    @classmethod
    def new(
        cls,
        internal_context_ref: str,
        context_revision: int,
        evaluation_time_utc: datetime,
        capability_results: Optional[Tuple[str, ...]] = None,
        projection_results: Optional[Tuple[str, ...]] = None,
        external_decisions: Optional[Tuple[str, ...]] = None,
        feedback: Optional[Tuple[str, ...]] = None,
    ) -> DefaultNetworkInputs:
        """Create a new inputs instance."""
        return cls(
            internal_context_ref=internal_context_ref,
            context_revision=context_revision,
            evaluation_time_utc=evaluation_time_utc,
            existing_episode_ref=None,
            episode_state=None,
            identity_provider_state_ref=None,
            configuration_revision=None,
            capability_results=capability_results or (),
            projection_results=projection_results or (),
            external_decisions=external_decisions or (),
            feedback=feedback or (),
        )
