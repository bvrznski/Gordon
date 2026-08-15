# Internal Context Request Model
# ===============================

"""
Context request model for specifying what context should be assembled.

The request describes requirements without containing provider implementations.
It's the contract between context consumers and the assembler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, FrozenSet, TYPE_CHECKING


if TYPE_CHECKING:
    from .enums import InternalContextScope

InternalContextRequestId = str
"""Unique identifier for a context request."""


@dataclass(frozen=True, slots=True)
class InternalContextRequest:
    """
    Immutable request describing what context should be assembled.
    
    The request specifies requirements but does NOT contain provider implementations.
    It is the contract between context consumers and the assembler.
    
    PROPERTIES:
        • request_id: Unique identifier for this request
        • purpose: Why the context is being assembled (determines required projections)
        • scope: Constraints on what's included/excluded
        
    FIELDS:
        • required_projection_kinds: Projections that MUST be present
        • optional_projection_kinds: Projections that are nice to have
        • minimum_confidence: Lower bound for acceptable confidence
        • maximum_age: Oldest acceptable projection age (None = no constraint)
        • maximum_total_items: Hard limit on total items across all projections
        
    NOT INCLUDED:
        • Provider implementations (those are passed separately during assembly)
        • Runtime state or live references
        • Mutable collections
    """
    
    request_id: InternalContextRequestId
    """Unique identifier for this request."""
    
    purpose: str  # InternalContextPurpose.*
    """Why the context is being assembled."""
    
    scope: "InternalContextScope | None" = field(default=None)
    """Constraints on what's included/excluded."""
    
    required_projection_kinds: FrozenSet[str] = field(default_factory=frozenset)
    """Projection kinds that MUST be present."""
    
    optional_projection_kinds: FrozenSet[str] = field(default_factory=frozenset)
    """Projection kinds that are desirable but not required."""
    
    minimum_confidence: float = 0.3
    """Lower bound for acceptable confidence (0.0 to 1.0)."""
    
    maximum_age_seconds: float | None = None
    """Oldest acceptable projection age in seconds (None = no constraint)."""
    
    maximum_total_items: int = 500
    """Hard limit on total items across all projections."""
    
    # Correlation and causation tracking
    correlation_id: str = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: str | None = None
    """Causation ID if this request results from another event."""
    
    @classmethod
    def create(
        cls,
        purpose: str,
        required_kinds: Tuple[str, ...] = (),
        optional_kinds: Tuple[str, ...] = (),
        **kwargs,
    ) -> InternalContextRequest:
        """
        Create a new context request with specified parameters.
        
        Args:
            purpose: Why the context is being assembled
            required_kinds: Projection kinds that must be present
            optional_kinds: Projection kinds that are desirable
            **kwargs: Other parameter overrides
            
        Returns:
            New InternalContextRequest instance
        """
        scope_val = kwargs.get("scope")
        if scope_val is None:
            from .enums import InternalContextScope
            scope_val = InternalContextScope.default_scope()
        
        return cls(
            request_id=f"request_{id(cls)}",
            purpose=purpose,
            required_projection_kinds=frozenset(required_kinds),
            optional_projection_kinds=frozenset(optional_kinds),
            scope=scope_val,
            **{k: v for k, v in kwargs.items() if k != "scope"},
        )


def is_internal_context_request(value: object) -> bool:
    """Check if a value is an InternalContextRequest instance."""
    return isinstance(value, InternalContextRequest)