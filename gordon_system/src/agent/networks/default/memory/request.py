# Memory Integration Request Models
# ===================================

"""
Immutable models for memory integration requests and related concepts.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies (no imports from Core or Execution)
    - Bounded by explicit limits
    - Semantic content only (no live objects)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, FrozenSet
from datetime import datetime


# =============================================================================
# ID TYPES
# =============================================================================

MemoryIntegrationRequestId = str
"""Unique identifier for a memory integration request."""

InternalContextId = str
"""Reference to an InternalContext instance."""

InternalContextRevision = int
"""Revision number of the bound context."""

InternalEpisodeId = str
"""Reference to an InternalEpisode instance."""

InternalThoughtId = str
"""Reference to an InternalThought instance."""

CorrelationId = str
"""Correlation ID for distributed tracing."""

CausationId = Optional[str]
"""Causation ID if request results from another event."""


# =============================================================================
# MEMORY INTEGRATION SOURCE REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationSourceReference:
    """
    Immutable reference to a source of memory integration.
    
    This identifies where the request originated without embedding live objects.
    """
    
    # Source identity
    source_id: str
    """Unique identifier for the source."""
    
    source_kind: str  # MemoryIntegrationRequester.*
    """Kind of source (e.g., 'reflection', 'simulation')."""
    
    source_revision: int = 1
    """Revision of the source at time of request."""
    
    # Timestamps
    referenced_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When this source was referenced."""
    
    @classmethod
    def from_reflection(cls, reflection_id: str) -> MemoryIntegrationSourceReference:
        """Create a reference to a reflection episode."""
        return cls(
            source_id=reflection_id,
            source_kind="reflection",
        )
    
    @classmethod
    def from_simulation(cls, simulation_id: str) -> MemoryIntegrationSourceReference:
        """Create a reference to a simulation episode."""
        return cls(
            source_id=simulation_id,
            source_kind="simulation",
        )
    
    @classmethod
    def from_identity(cls, identity_id: str) -> MemoryIntegrationSourceReference:
        """Create a reference to an identity coordination episode."""
        return cls(
            source_id=identity_id,
            source_kind="identity",
        )
    
    @classmethod
    def from_narrative(cls, narrative_id: str) -> MemoryIntegrationSourceReference:
        """Create a reference to a narrative episode."""
        return cls(
            source_id=narrative_id,
            source_kind="narrative",
        )


# =============================================================================
# MEMORY INTEGRATION REQUEST - Main request type
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationRequest:
    """
    Immutable request to perform one bounded memory integration episode.
    
    The request is semantic - it contains references to data but does not
    contain live objects or runtime handles. It defines WHAT should be
    integrated, not HOW the integration should be implemented.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: What kind of memory integration is being requested
        • subject: What is being integrated
        • scope: Bounded constraints on the integration
        • context_id: Reference to InternalContext revision
        • context_revision: Context version at request time
        • memory_projection_references: References to memory projections needed
        • source_references: Sources triggering this integration
        • expected_products: Which products are desired
        • completion_requirements: Success criteria
        • originating_episode_id: Parent episode if derived
        • originating_thought_ids: Thoughts that triggered this request
        • requested_by: Who/what made the request
        • correlation_id: For distributed tracing
        • causation_id: If results from another event
        • provenance: Where this request originated
    
    BOUNDEDNESS:
        Every limit is explicit. Overflow must be recorded.
    
    NOT RESPONSIBLE FOR:
        - Executing memory integration algorithms
        - Allocating runtime resources
        - Scheduling execution
        - Storing persistent results
    """
    
    # Identity and metadata
    request_id: MemoryIntegrationRequestId
    """Unique identifier for this request."""
    
    purpose: str  # MemoryIntegrationPurposeKind.*
    """What kind of memory integration is being requested."""
    
    subject: str  # MemoryIntegrationSubjectKind.*
    """What is being integrated."""
    
    scope: str  # Serialized MemoryIntegrationScope as JSON-compatible dict or string
    """Bounded constraints on the integration (serialized)."""
    
    # Context binding
    context_id: InternalContextId
    """Reference to InternalContext revision."""
    
    context_revision: int = 1
    """Context version at request time."""
    
    # Memory projection references (bounded)
    memory_projection_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to memory projections needed for integration."""
    
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to sources triggering this integration."""
    
    # Product expectations
    expected_products: FrozenSet[str] = field(default_factory=frozenset)
    """Product kinds expected from this integration."""
    
    completion_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit conditions for successful completion."""
    
    # Origin tracking
    originating_episode_id: Optional[InternalEpisodeId] = None
    """ID of parent episode if derived from one."""
    
    originating_thought_ids: Tuple[InternalThoughtId, ...] = field(
        default_factory=tuple
    )
    """Thought IDs that triggered this request."""
    
    # Coordination metadata
    requested_by: str = "DEFAULT_NETWORK"
    """Who/what made the request (MemoryIntegrationRequester.*)."""
    
    correlation_id: CorrelationId = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[CausationId] = None
    """Causation ID if this results from another event."""
    
    provenance: str = "canonical"
    """Provenance reference (where request type is documented)."""
    
    # Timestamps
    requested_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When the request was created."""
    
    @classmethod
    def new(
        cls,
        purpose: str,
        subject: str,
        scope_serialized: str,
        context_id: str,
        request_id: Optional[str] = None,
        memory_projection_references: Tuple[str, ...] = (),
        source_references: Tuple[str, ...] = (),
        expected_products: FrozenSet[str] = frozenset(),
        completion_requirements: Tuple[str, ...] = (),
    ) -> MemoryIntegrationRequest:
        """
        Create a new memory integration request with default metadata.
        
        Args:
            purpose: The purpose kind (MemoryIntegrationPurposeKind.*)
            subject: The subject kind (MemoryIntegrationSubjectKind.*)
            scope_serialized: Serialized scope constraints
            context_id: Reference to the InternalContext revision
            request_id: Optional explicit ID (auto-generated if None)
            memory_projection_references: References to needed projections
            source_references: Sources triggering this integration
            expected_products: Product kinds expected
            completion_requirements: Success criteria
            
        Returns:
            New MemoryIntegrationRequest instance with valid metadata
        """
        return cls(
            request_id=request_id or f"memory_integration_request_{id(cls)}",
            purpose=purpose,
            subject=subject,
            scope=scope_serialized,
            context_id=context_id,
            context_revision=1,
            memory_projection_references=memory_projection_references,
            source_references=source_references,
            expected_products=expected_products,
            completion_requirements=completion_requirements,
        )
    
    def exceeds_scope_limits(
        self,
        projection_count: int,
        record_count: int,
        association_count: int,
        link_count: int,
    ) -> Tuple[str, ...]:
        """
        Check if counts exceed scope limits.
        
        Args:
            projection_count: Number of memory projections
            record_count: Number of full records loaded
            association_count: Number of associations identified
            link_count: Number of links established
            
        Returns:
            List of exceeded limits (empty if within bounds)
        """
        violations = []
        # In a real implementation, scope would be parsed and checked
        # For now, return empty - actual checking happens in validation layer
        return tuple(violations)


# =============================================================================
# MEMORY PROJECTION REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryProjectionReference:
    """
    Immutable reference to a memory projection.
    
    This identifies what memory is needed without exposing full records or
    live database handles.
    """
    
    # Reference identity
    projection_id: str
    """Unique identifier for this projection."""
    
    owner_id: str
    """ID of the Memory owner (external system)."""
    
    source_revision: int = 1
    """Source revision at time of projection."""
    
    memory_kind: str = "unknown"  # MemoryKind.*
    """Kind of memory being referenced."""
    
    subject_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to subjects (entities) in this memory."""
    
    capture_time_utc: datetime = field(default_factory=datetime.utcnow)
    """When the memory was captured."""
    
    confidence: float = 0.5
    """Confidence in this projection (0.0 to 1.0)."""
    
    completeness: str = "partial"
    """Completeness classification."""
    
    freshness: str = "unknown"
    """Freshness classification."""
    
    privacy_classification: str = "internal"
    """Privacy level for disclosure control."""
    
    provenance: Optional[str] = None
    """Provenance reference (how this projection was created)."""
    
    artifact_reference: Optional[str] = None
    """Optional artifact reference for full record."""
    
    @classmethod
    def new(
        cls,
        projection_id: str,
        owner_id: str,
        memory_kind: str,
        subject_references: Tuple[str, ...] = (),
        confidence: float = 0.5,
    ) -> MemoryProjectionReference:
        """Create a new memory projection reference."""
        return cls(
            projection_id=projection_id,
            owner_id=owner_id,
            source_revision=1,
            memory_kind=memory_kind,
            subject_references=subject_references,
            confidence=confidence,
        )
    
    def is_factual(self) -> bool:
        """Check if this projection represents factual content."""
        # In a real implementation, this would check factuality
        return True  # Placeholder - actual check in validation


# =============================================================================
# MEMORY PROJECTION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryProjectionRequest:
    """
    Immutable request to retrieve memory projections from Memory authority.
    
    This is used by the Default Network to obtain projections without
    direct database access.
    """
    
    # Request identity
    request_id: str
    """Unique identifier for this projection request."""
    
    episode_id: Optional[str] = None
    """ID of the memory integration episode making this request."""
    
    step_id: Optional[str] = None
    """ID of the plan step triggering this request (optional)."""
    
    # Projection specifications
    memory_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Memory kinds to retrieve."""
    
    subject_references: Tuple[str, ...] = field(default_factory=tuple)
    """Subject references to match."""
    
    temporal_scope_start_utc: Optional[datetime] = None
    """Start of temporal scope (inclusive)."""
    
    temporal_scope_end_utc: Optional[datetime] = None
    """End of temporal scope (exclusive)."""
    
    # Constraints
    maximum_results: int = 100
    """Maximum results to return."""
    
    minimum_relevance: float = 0.0
    """Minimum relevance threshold (0.0 to 1.0)."""
    
    minimum_confidence: float = 0.5
    """Minimum confidence threshold (0.0 to 1.0)."""
    
    factuality_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Allowed factuality classes."""
    
    privacy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Allowed privacy classifications."""
    
    # Correlation and tracing
    correlation_id: str = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[CausationId] = None
    """Causation ID if this results from another event."""
    
    provenance: Optional[str] = None
    """Provenance reference (where request type is documented)."""
    
    @classmethod
    def new(
        cls,
        request_id: str,
        memory_kinds: Tuple[str, ...],
        maximum_results: int = 100,
    ) -> MemoryProjectionRequest:
        """
        Create a new projection request.
        
        Args:
            request_id: Unique identifier for this request
            memory_kinds: Kinds of memory to retrieve
            maximum_results: Maximum number of results
            
        Returns:
            New MemoryProjectionRequest instance
        """
        return cls(
            request_id=request_id,
            memory_kinds=memory_kinds,
            maximum_results=maximum_results,
        )


# =============================================================================
# MEMORY PROJECTION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryProjectionResult:
    """
    Immutable result from a Memory projection request.
    
    This contains the projections without live database objects or
    implementation details.
    """
    
    # Result identity
    result_id: str
    """Unique identifier for this result."""
    
    originating_request_id: str
    """ID of the request that produced this result."""
    
    episode_id: Optional[str] = None
    """ID of the episode this result belongs to."""
    
    # Status (must come after optional fields)
    status: str = "unknown"  # MemoryProjectionResultStatus.*
    """Result status."""
    
    # Projections included in result
    projection_references: Tuple[MemoryProjectionReference, ...] = field(
        default_factory=tuple
    )
    """References to projections returned."""
    
    record_projections: Tuple[str, ...] = field(default_factory=tuple)
    """Serialized record projections (summary only)."""
    
    # Summary information
    omitted_count: int = 0
    """Number of results omitted due to bounds."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence in the result set (0.0 to 1.0)."""
    
    completeness: str = "unknown"
    """Completeness classification."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this result."""
    
    # Failure information
    failure_reason: Optional[str] = None
    """Human-readable failure description (if status != success)."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference (where result type is documented)."""
    
    produced_at_utc: str = ""
    """When the result was produced (ISO format string)."""
    
    @classmethod
    def success(
        cls,
        result_id: str,
        request_id: str,
        projection_references: Tuple[MemoryProjectionReference, ...],
        confidence: float = 0.5,
    ) -> MemoryProjectionResult:
        """Create a successful projection result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            status="success",
            projection_references=projection_references,
            confidence=confidence,
            completeness="complete" if confidence >= 0.7 else "sufficient",
        )
    
    @classmethod
    def partial(
        cls,
        result_id: str,
        request_id: str,
        projection_references: Tuple[MemoryProjectionReference, ...],
        omitted_count: int = 0,
    ) -> MemoryProjectionResult:
        """Create a partial projection result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            status="partial",
            projection_references=projection_references,
            omitted_count=omitted_count,
            confidence=0.3 + (len(projection_references) / 100) * 0.2,
            completeness="partial",
        )
    
    @classmethod
    def failure(
        cls,
        result_id: str,
        request_id: str,
        failure_reason: str,
    ) -> MemoryProjectionResult:
        """Create a failed projection result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            status="failure",
            failure_reason=failure_reason,
            confidence=0.0,
            completeness="invalid",
        )
    
    def is_success(self) -> bool:
        """Check if this result represents successful completion."""
        return self.status == "success"
    
    def has_omissions(self) -> bool:
        """Check if some results were omitted due to bounds."""
        return self.omitted_count > 0


class MemoryProjectionResultStatus:
    """
    Status codes for projection results.
    """
    
    SUCCESS = "success"
    """Projections retrieved successfully."""
    
    PARTIAL = "partial"
    """Some projections returned, but bounds limited others."""
    
    FAILURE = "failure"
    """Request failed."""
    
    TIMEOUT = "timeout"
    """Request timed out."""
    
    @classmethod
    def is_terminal(cls, status: str) -> bool:
        """Check if status represents terminal state."""
        return status in {cls.SUCCESS, cls.FAILURE, cls.TIMEOUT}