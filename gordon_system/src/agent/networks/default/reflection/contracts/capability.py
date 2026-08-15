# Reflection Capability Contracts
# ===============================

"""
Immutable request and result models for capability invocation boundaries.

These contracts define the interface between reflection coordination and
external capability owners without containing implementation details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# CAPABILITY REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionCapabilityRequest:
    """
    Immutable request to a reflection capability owner.
    
    The coordination layer produces requests but must not directly invoke
    concrete capability implementations. A separate integration layer
    resolves requests to implementations.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • episode_id: Which episode this request belongs to
        • step_id: Which plan step triggered this request
        • purpose: What kind of reflection is requested
        • subject: What is being reflected upon
        • expected_products: Product kinds expected from capability
        • constraints: Bounded constraints on the operation
        
    BOUNDEDNESS:
        All fields must be bounded. No unbounded collections.
        
    NOT RESPONSIBLE FOR:
        - Invoking capability implementations directly
        - Allocating runtime resources
        - Deciding which capability instance to use
    """
    
    request_id: str
    """Unique identifier for this request."""
    
    episode_id: str
    """ID of the reflection episode this request belongs to."""
    
    step_id: Optional[str] = None
    """ID of the plan step that triggered this request (optional)."""
    
    # Purpose and scope
    purpose_kind: str  # ReflectionPurposeKind.*
    """What kind of reflection is requested."""
    
    subject_kind: str  # ReflectionSubjectKind.*
    """What is being reflected upon."""
    
    expected_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product kinds the capability should attempt to produce."""
    
    # Constraints
    maximum_evidence_items: int = 100
    """Maximum evidence items to process."""
    
    maximum_products_returned: int = 15
    """Maximum products to return."""
    
    minimum_confidence_required: float = 0.5
    """Minimum confidence threshold for products."""
    
    recursion_depth_limit: int = 3
    """Maximum recursive depth allowed."""
    
    # Correlation and tracing
    correlation_id: str = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if this results from another event."""
    
    provenance: Optional[str] = None
    """Provenance reference (where request type is documented)."""
    
    # Idempotency safety
    idempotency_key: Optional[str] = None
    """Key for safe retries (same key = same result expected)."""
    
    @classmethod
    def new(
        cls,
        request_id: str,
        episode_id: str,
        purpose_kind: str,
        subject_kind: str,
    ) -> ReflectionCapabilityRequest:
        """
        Create a new capability request.
        
        Args:
            request_id: Unique identifier for this request
            episode_id: ID of the reflection episode
            purpose_kind: What kind of reflection is requested
            subject_kind: What is being reflected upon
            
        Returns:
            New ReflectionCapabilityRequest instance
        """
        return cls(
            request_id=request_id,
            episode_id=episode_id,
            purpose_kind=purpose_kind,
            subject_kind=subject_kind,
        )


# =============================================================================
# CAPABILITY RESULT
# =============================================================================

class CapabilityResultStatus:
    """
    Status of a capability result.
    """
    
    SUCCESS = "success"
    """Capability completed successfully."""
    
    FAILURE = "failure"
    """Capability failed to complete."""
    
    CANCELLED = "cancelled"
    """Capability was cancelled."""
    
    PARTIAL = "partial"
    """Capability produced partial results."""
    
    TIMEOUT = "timeout"
    """Capability timed out."""


@dataclass(frozen=True, slots=True)
class ReflectionCapabilityResult:
    """
    Immutable result from a reflection capability owner.
    
    Results should be projected into the coordination episode. Do not
    inject live implementation return objects directly into episode state.
    
    PROPERTIES:
        • result_id: Unique identifier for this result
        • originating_request_id: Which request produced this result
        • episode_id: Which episode the result belongs to
        • status: Success, failure, partial, or cancelled
        • products: Reflective products generated by capability
        • confidence: Quality assessment of results
        
    BOUNDEDNESS:
        Product collections must be bounded. No unbounded growth.
        
    NOT RESPONSIBLE FOR:
        - Mutating episode state directly
        - Creating runtime tasks or threads
        - Scheduling further processing
    """
    
    result_id: str
    """Unique identifier for this result."""
    
    originating_request_id: str
    """ID of the request that produced this result."""
    
    episode_id: str
    """ID of the episode this result belongs to."""
    
    # Status
    status: str  # CapabilityResultStatus.*
    """Result status."""
    
    # Products generated by capability
    products: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of reflective products produced (insights, patterns, etc.)."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to evidence items supporting products."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence in the results (0.0 to 1.0)."""
    
    completeness: str = "unknown"
    """Completeness status of results."""
    
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
    """Provenance reference (where result type is documented)."""
    
    produced_at_utc: str = ""
    """When the result was produced (ISO format string)."""
    
    @classmethod
    def success(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
        products: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> ReflectionCapabilityResult:
        """Create a successful capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status=CapabilityResultStatus.SUCCESS,
            products=products,
            confidence=confidence,
            completeness="complete" if confidence >= 0.7 else "sufficient",
        )
    
    @classmethod
    def partial(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
        products: Tuple[str, ...],
        missing_count: int = 0,
    ) -> ReflectionCapabilityResult:
        """Create a partial capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status=CapabilityResultStatus.PARTIAL,
            products=products,
            confidence=0.3 + (len(products) / 15) * 0.2,
            completeness="partial",
        )
    
    @classmethod
    def failure(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
        error_category: str,
        retry_safe: bool = False,
    ) -> ReflectionCapabilityResult:
        """Create a failed capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status=CapabilityResultStatus.FAILURE,
            error_category=error_category,
            retry_safe=retry_safe,
            confidence=0.0,
            completeness="invalid",
        )
    
    @classmethod
    def cancelled(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
    ) -> ReflectionCapabilityResult:
        """Create a cancelled capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status=CapabilityResultStatus.CANCELLED,
            confidence=0.0,
            completeness="invalid",
        )
    
    @classmethod
    def timeout(
        cls,
        result_id: str,
        request_id: str,
        episode_id: str,
    ) -> ReflectionCapabilityResult:
        """Create a timeout capability result."""
        return cls(
            result_id=result_id,
            originating_request_id=request_id,
            episode_id=episode_id,
            status=CapabilityResultStatus.TIMEOUT,
            confidence=0.0,
            completeness="invalid",
        )
    
    def is_success(self) -> bool:
        """Check if this result represents successful completion."""
        return self.status == CapabilityResultStatus.SUCCESS
    
    def is_terminal(self) -> bool:
        """Check if this result is terminal (no retry recommended)."""
        return self.status in {
            CapabilityResultStatus.FAILURE,
            CapabilityResultStatus.CANCELLED,
            CapabilityResultStatus.TIMEOUT,
        }