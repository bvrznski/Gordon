# Default Network Request Models
# ===============================

"""
Canonical DefaultNetwork request models for runtime-neutral coordination.

All request models are deeply immutable to ensure deterministic behavior,
replayability, and thread safety. No live objects, callbacks, or runtime
handles may be embedded in these models.

PHASE 4.3.12: Runtime-Neutral Request Contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Any
from datetime import datetime


# =============================================================================
# REQUEST IDENTITY TYPES
# =============================================================================

DefaultNetworkRequestId = str
"""Stable identifier for a DefaultNetwork request instance."""

CorrelationId = str
"""Identifier for distributed tracing correlation."""

CausationId = Optional[str]
"""Identifier for causation chain (optional)."""

SemanticTime = datetime
"""Canonical time reference for semantic operations."""


# =============================================================================
# DEFAULT NETWORK REQUEST PROVENANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkRequestProvenance:
    """
    Complete provenance record for a DefaultNetwork request.
    
    Tracks origin and chain of custody without embedding runtime references.
    """
    
    # Origin identity
    created_by: str  # Component or system that initiated the request
    
    # Timestamping
    created_at_utc: SemanticTime
    
    # Version tracking
    configuration_revision: Optional[str] = None
    
    # External correlation
    external_request_id: Optional[CorrelationId] = None
    
    # Processing metadata
    processing_version: str = "1.0.0"
    
    @classmethod
    def new(
        cls,
        created_by: str,
        created_at_utc: SemanticTime,
    ) -> DefaultNetworkRequestProvenance:
        """Create a new provenance record."""
        return cls(
            created_by=created_by,
            created_at_utc=created_at_utc,
            configuration_revision=None,
            external_request_id=None,
            processing_version="1.0.0",
        )


# =============================================================================
# DEFAULT NETWORK REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkRequest:
    """
    Canonical request contract for Default Network coordination.
    
    This is the primary input contract for one bounded semantic progression.
    
    ARCHITECTURAL INVARIANTS:
        DEFAULT-REQ-INV-001: Request identity is stable across replays
        DEFAULT-REQ-INV-002: Request purpose determines valid paths and outputs
        DEFAULT-REQ-INV-003: Context reference binds to one InternalContext revision
        DEFAULT-REQ-INV-004: Episode reference may be absent (new episode) or present (continuation)
        DEFAULT-REQ-INV-005: Request does not embed runtime references (no threads, no callbacks)
        DEFAULT-REQ-INV-006: Request is fully bounded (no unbounded growth possible)
        DEFAULT-REQ-INV-007: All semantic inputs are immutable
    
    PROPERTIES:
        • request_id: Unique identifier for this request instance
        • purpose: Semantic coordination goal
        • subject: What is being processed
        • context_reference: Which InternalContext to use
        • episode_reference: Optional continuation of existing episode
        
    COORDINATION:
        • requested_path: Optional explicit path (network may infer)
        • requested_products: Desired output products
        
    BOUNDS:
        • scope: Breadth of the coordination task
        • completion_requirements: When this request is satisfied
        
    ORIGIN:
        • originating_thread_reference: Source ExecutionThread (if any)
        • originating_cycle_reference: Source ExecutionCycle (if any)
        
    CHAINING:
        • correlation_id: For distributed tracing
        • causation_id: For causation chain
        • requested_at: When this request was created
        
    PROVENANCE:
        • provenance: Complete origin and custody record
    
    NOT RESPONSIBLE FOR:
        • Executing any capability
        • Creating runtime threads or tasks
        • Waiting for results
        • Scheduling continuation
        • Mutating external state
    """
    
    # Identity
    request_id: DefaultNetworkRequestId
    """Unique identifier for this request instance."""
    
    # Purpose (what kind of coordination)
    purpose: str  # DefaultNetworkPurpose.*
    
    # Subject (what is being processed)
    subject: str  # DefaultNetworkSubject.*
    
    # Context binding
    context_reference: InternalContextReference
    """Which InternalContext to use for this request."""
    
    # Episode handling
    episode_reference: Optional[InternalEpisodeReference]
    """Optional existing episode to continue, or None to create new."""
    
    # Path selection
    requested_path: Optional[str]  # DefaultNetworkPath.* or None (infer)
    """Explicit path if known, or None for automatic inference."""
    
    # Product requirements
    requested_products: frozenset[str]
    """Desired output product kinds."""
    
    # Scope and bounds
    scope: str  # DefaultNetworkScope.*
    """Breadth of the coordination task."""
    
    completion_requirements: DefaultNetworkCompletionRequirements
    """When this request should be considered complete."""
    
    # Origin (for traceability)
    originating_thread_reference: Optional[ExecutionThreadReference]
    """Source ExecutionThread if from an execution loop."""
    
    originating_cycle_reference: Optional[ExecutionCycleReference]
    """Source ExecutionCycle if from an execution loop."""
    
    # Chaining and timing
    correlation_id: CorrelationId
    """For distributed tracing."""
    
    causation_id: CausationId
    """Causation chain reference (optional)."""
    
    requested_at_utc: SemanticTime
    """When this request was created."""
    
    provenance: DefaultNetworkRequestProvenance
    """Complete origin and custody record."""
    
    @staticmethod
    def _generate_request_id(purpose: str, subject: str, context_ref: InternalContextReference, path: Optional[str], products: frozenset) -> DefaultNetworkRequestId:
        """Generate a stable deterministic request ID from inputs."""
        import hashlib
        combined = f"{purpose}:{subject}:{context_ref.context_id}:{context_ref.revision}:{path or ''}:{sorted(products)}"
        hash_value = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return f"request:{hash_value}"
    
    @classmethod
    def new(
        cls,
        purpose: str,
        subject: str,
        context_reference: InternalContextReference,
        scope: str = "narrow",
        requested_path: Optional[str] = None,
        requested_products: Optional[frozenset[str]] = None,
        episode_reference: Optional[InternalEpisodeReference] = None,
        originating_thread_reference: Optional[ExecutionThreadReference] = None,
        originating_cycle_reference: Optional[ExecutionCycleReference] = None,
        correlation_id: Optional[CorrelationId] = None,
        causation_id: Optional[CausationId] = None,
        requested_at_utc: Optional[SemanticTime] = None,
        provenance: Optional[DefaultNetworkRequestProvenance] = None,
    ) -> DefaultNetworkRequest:
        """
        Create a new DefaultNetwork request.
        
        Args:
            purpose: Semantic coordination goal
            subject: What is being processed
            context_reference: Which InternalContext to use
            scope: Breadth of the task (default: narrow)
            requested_path: Explicit path if known (default: None for inference)
            requested_products: Desired output products
            episode_reference: Optional existing episode to continue
            originating_thread_reference: Source thread reference
            originating_cycle_reference: Source cycle reference
            correlation_id: Correlation ID for tracing
            causation_id: Causation chain reference
            requested_at_utc: Request creation time (optional, default: current UTC)
            provenance: Origin record
            
        Returns:
            New DefaultNetworkRequest instance
        
        NOTE: For deterministic replay, provide explicit timestamps.
              Request IDs are generated deterministically from content only
              (purpose, subject, context_id, context_revision, path, products).
              Timestamps do not affect request_id generation.
        """
        # DefaultNetworkCompletionRequirements is defined in this module (request.py)
        # for proper module organization - it's a request-level concept
        
        products = frozenset(requested_products or [])
        request_id = cls._generate_request_id(purpose, subject, context_reference, requested_path, products)
        
        return cls(
            request_id=request_id,
            purpose=purpose,
            subject=subject,
            context_reference=context_reference,
            episode_reference=episode_reference,
            requested_path=requested_path,
            requested_products=frozenset(requested_products or []),
            scope=scope,
            completion_requirements=DefaultNetworkCompletionRequirements.standard(),
            originating_thread_reference=originating_thread_reference,
            originating_cycle_reference=originating_cycle_reference,
            correlation_id=correlation_id or "",
            causation_id=causation_id,
            requested_at_utc=requested_at_utc,
            provenance=provenance or DefaultNetworkRequestProvenance.new(
                created_by="DefaultNetwork",
                created_at_utc=requested_at_utc if requested_at_utc is not None else datetime.utcnow(),
            ),
        )


# =============================================================================
# INTERNAL CONTEXT REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalContextReference:
    """
    Stable reference to an InternalContext without embedding the full context.
    
    Allows referencing external state without ownership or runtime coupling.
    """
    
    context_id: str
    """Stable identifier for the context."""
    
    revision: int
    """Context revision number at time of reference."""
    
    source_type: Optional[str] = None
    """Source system type (for tracing)."""
    
    captured_at_utc: Optional[SemanticTime] = None
    """When this context snapshot was taken (optional)."""
    
    @classmethod
    def from_context(cls, context_id: str, revision: int) -> InternalContextReference:
        """Create a reference from context identity and revision."""
        return cls(
            context_id=context_id,
            revision=revision,
            source_type=None,
            captured_at_utc=None,
        )


# =============================================================================
# INTERNAL EPISODE REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalEpisodeReference:
    """
    Stable reference to an InternalEpisode without embedding the full episode.
    
    Allows continuation of existing coordination without ownership or runtime coupling.
    """
    
    episode_id: str
    """Stable identifier for the episode."""
    
    revision: int
    """Episode revision number at time of reference."""
    
    lifecycle_state: Optional[str] = None
    """Current lifecycle state (for validation)."""
    
    @classmethod
    def from_episode(cls, episode_id: str, revision: int) -> InternalEpisodeReference:
        """Create a reference from episode identity and revision."""
        return cls(
            episode_id=episode_id,
            revision=revision,
            lifecycle_state=None,
        )


# =============================================================================
# EXECUTION THREAD AND CYCLE REFERENCES
# =============================================================================

@dataclass(frozen=True, slots=True)
class ExecutionThreadReference:
    """
    Stable reference to an ExecutionThread without embedding the full thread.
    
    Used only for traceability and provenance - no runtime access.
    """
    
    thread_id: str
    """Stable identifier for the thread."""
    
    @classmethod
    def new(cls, thread_id: str) -> ExecutionThreadReference:
        """Create a new execution thread reference."""
        return cls(thread_id=thread_id)


@dataclass(frozen=True, slots=True)
class ExecutionCycleReference:
    """
    Stable reference to an ExecutionCycle without embedding the full cycle.
    
    Used only for traceability and provenance - no runtime access.
    """
    
    cycle_id: str
    """Stable identifier for the cycle."""
    
    @classmethod
    def new(cls, cycle_id: str) -> ExecutionCycleReference:
        """Create a new execution cycle reference."""
        return cls(cycle_id=cycle_id)


# =============================================================================
# DEFAULT NETWORK COMPLETION REQUIREMENTS
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkCompletionRequirements:
    """
    Requirements that must be satisfied for request completion.
    
    These define when the network may consider one semantic progression complete.
    """
    
    minimum_products: int = 0
    """Minimum number of products required."""
    
    maximum_local_steps: int = 100
    """Maximum local semantic steps in one invocation."""
    
    require_external_results: bool = False
    """Whether external capability results are required."""
    
    completion_confidence_threshold: float = 0.5
    """Minimum confidence for completion."""
    
    @classmethod
    def standard(cls) -> DefaultNetworkCompletionRequirements:
        """Create standard completion requirements."""
        return cls(
            minimum_products=0,
            maximum_local_steps=100,
            require_external_results=False,
            completion_confidence_threshold=0.5,
        )
    
    @classmethod
    def strict(cls) -> DefaultNetworkCompletionRequirements:
        """Create strict completion requirements (for critical tasks)."""
        return cls(
            minimum_products=1,
            maximum_local_steps=100,
            require_external_results=True,
            completion_confidence_threshold=0.8,
        )