# Capability Request and Result Models
# =====================================

"""
Immutable request and result models for capability invocation boundaries.

These contracts define the interface between episode coordination and
capability owners without containing implementation details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


InternalCapabilityRequestId = str
"""Unique identifier for a capability request."""

InternalCapabilityResultId = str
"""Unique identifier for a capability result."""


@dataclass(frozen=True, slots=True)
class InternalCapabilityRequest:
    """
    Immutable request to a capability owner.
    
    The DefaultNetwork may produce requests but must not directly invoke concrete
    capability implementations from the episode model. A separate integration or
    composition layer resolves requests to implementations.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • episode_id: Which episode this request belongs to
        • step_id: Which plan step triggered this request
        • capability_category: What type of capability is needed
        • operation_kind: What operation to perform
        • input_references: What inputs the capability needs
        • expected_result_schema: What output contract is expected
        
    BOUNDEDNESS:
        • constraints: Explicit limits on the request
        • idempotency_key: For safe retries
        • correlation/causation: For distributed tracing
        
    NOT RESPONSIBLE FOR:
        • Invoking capability implementations
        • Allocating runtime resources
        • Deciding which capability instance to use
    """
    
    # Identity
    request_id: InternalCapabilityRequestId
    """Unique identifier for this request."""
    
    episode_id: str
    """ID of the episode this request belongs to."""
    
    step_id: Optional[str] = None
    """ID of the plan step that triggered this request (optional)."""
    
    # Capability information
    capability_category: str  # InternalCapabilityCategory.*
    """What type of capability is needed."""
    
    operation_kind: str
    """The operation to perform within the category."""
    
    # Input specification
    input_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to inputs needed (evidence IDs, context refs)."""
    
    expected_result_schema: Optional[str] = None
    """Expected output contract (schema reference or constraint)."""
    
    # Constraints
    confidence_requirement: float = 0.5
    """Minimum confidence level required for result."""
    
    max_items_returned: int = 100
    """Maximum items the capability should return."""
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Additional constraints on the request."""
    
    # Retry safety
    idempotency_key: Optional[str] = None
    """Key for idempotent retries (same key = same result)."""
    
    retry_safe: str = "unknown"  # RetrySafety.*
    """Whether it's safe to retry if failed."""
    
    # Correlation and causation
    correlation_id: Optional[str] = None
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if this request results from another event."""
    
    provenance: Optional[str] = None
    """Provenance reference (where this request type is documented)."""
    
    @classmethod
    def create(
        cls,
        request_id: str,
        episode_id: str,
        capability_category: str,
        operation_kind: str,
        input_references: Tuple[str, ...],
        confidence_requirement: float = 0.5,
    ) -> InternalCapabilityRequest:
        """
        Create a new capability request.
        
        Args:
            request_id: Unique identifier for this request
            episode_id: ID of the episode this request belongs to
            capability_category: What type of capability is needed
            operation_kind: The operation to perform
            input_references: References to inputs needed
            confidence_requirement: Minimum confidence required
            
        Returns:
            New InternalCapabilityRequest instance
        """
        return cls(
            request_id=request_id,
            episode_id=episode_id,
            capability_category=capability_category,
            operation_kind=operation_kind,
            input_references=input_references,
            expected_result_schema=None,
            confidence_requirement=confidence_requirement,
            max_items_returned=100,
        )


@dataclass(frozen=True, slots=True)
class InternalCapabilityResult:
    """
    Immutable result from a capability owner.
    
    Results should be projected into the episode. Do not inject live implementation
    return objects directly into episode state.
    
    PROPERTIES:
        • result_id: Unique identifier for this result
        • originating_request_id: Which request produced this result
        • episode_id: Which episode the result belongs to
        • status: Success, failure, cancelled
        • payload_references: Where to find the actual data
        • evidence_items: Evidence generated by this result
        • confidence: Quality of the result
        
    BOUNDEDNESS:
        • side_effect_record: Any side effects that occurred
        • provenance: Track where results came from
        
    NOT RESPONSIBLE FOR:
        • Mutating episode state directly
        • Creating runtime tasks or threads
        • Scheduling further processing
    """
    
    # Identity
    result_id: InternalCapabilityResultId
    """Unique identifier for this result."""
    
    originating_request_id: str
    """ID of the request that produced this result."""
    
    episode_id: str
    """ID of the episode this result belongs to."""
    
    # Status
    status: str  # "success", "failure", "cancelled"
    """Result status."""
    
    # Payload
    payload_references: Tuple[str, ...] = field(default_factory=tuple)
    """Where to find the actual data (not full payloads)."""
    
    evidence_items_generated: int = 0
    """Number of new evidence items this result produced."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence level in the result (0.0 to 1.0)."""
    
    completeness: str = "unknown"  # InternalOutcomeStatus.*
    """Completeness of the result."""
    
    # Failure information (if status != success)
    error_category: Optional[str] = None
    """Category of failure (FailureCategory.*)."""
    
    error_message: Optional[str] = None
    """Human-readable error description."""
    
    retry_safe: bool = False
    """Whether a retry would be safe."""
    
    # Side effects
    side_effect_recorded: bool = False
    """Whether any side effects occurred."""
    
    side_effects: Tuple[str, ...] = field(default_factory=tuple)
    """Records of side effects (if any)."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference (where this result type is documented)."""
    
    produced_at_utc: str = ""
    """When the result was produced."""
    
    @classmethod
    def success(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
        confidence: float = 0.5,
        evidence_items: int = 1,
    ) -> InternalCapabilityResult:
        """Create a successful capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status="success",
            confidence=confidence,
            completeness="complete" if confidence >= 0.7 else "sufficient",
            evidence_items_generated=evidence_items,
            side_effect_recorded=False,
        )
    
    @classmethod
    def failure(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
        error_category: str,
        retry_safe: bool = False,
    ) -> InternalCapabilityResult:
        """Create a failed capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status="failure",
            error_category=error_category,
            retry_safe=retry_safe,
            side_effect_recorded=False,
        )
    
    @classmethod
    def cancelled(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
    ) -> InternalCapabilityResult:
        """Create a cancelled capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status="cancelled",
            confidence=0.0,
            completeness="invalid",
        )