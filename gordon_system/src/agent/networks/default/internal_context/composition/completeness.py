# Internal Context Completeness Model
# ====================================

"""
Structured completeness assessment for internal context.

Completeness is distinct from confidence:
    • Complete = all required projections present with sufficient content
    • High confidence = strong supporting evidence (even if partial)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class InternalContextCompleteness:
    """
    Structured completeness assessment for internal context.
    
    Completeness is distinct from confidence. A context can be:
        • Complete but low confidence (all items present, uncertain about quality)
        • Partial but high confidence (few items, very certain about them)
        • Insufficient (missing required items for the purpose)
    
    COMPLETENESS LEVELS:
        • COMPLETE: All required projections present with sufficient content
        • SUFFICIENT: Satisfactory despite some optional omissions
        • PARTIAL: Some required or optional projections missing/incomplete
        • INSUFFICIENT: Missing critical required projections for the purpose
        • INVALID: Context failed validation
    
    PROPERTIES:
        • status: One of the completeness levels above
        • required_count: Total number of required projection kinds
        • supplied_required_count: Number of required projections that were found
        • missing_required_kinds: List of missing required projection kinds
        • optional_supplied_count: Optional projections that were found
        • incomplete_details: Details about what's incomplete
        • overall_score: Numerical score 0.0 to 1.0
    """
    
    status: str  # ContextCompleteness.*
    """Status level of completeness."""
    
    required_count: int = 0
    """Total number of required projection kinds for the purpose."""
    
    supplied_required_count: int = 0
    """Number of required projections that were successfully included."""
    
    missing_required_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds that are required but missing."""
    
    optional_supplied_count: int = 0
    """Optional projection kinds that were included."""
    
    incomplete_details: Tuple[str, ...] = field(default_factory=tuple)
    """Details about incomplete projections or partial content."""
    
    overall_score: float = 1.0
    """Numerical completeness score from 0.0 to 1.0."""
    
    @classmethod
    def complete(cls) -> InternalContextCompleteness:
        """Create a completeness record for a complete context."""
        return cls(
            status="complete",
            required_count=0,
            supplied_required_count=0,
            missing_required_kinds=(),
            optional_supplied_count=0,
            incomplete_details=(),
            overall_score=1.0,
        )
    
    @classmethod
    def sufficient(cls, optional_count: int = 0) -> InternalContextCompleteness:
        """Create a completeness record for a sufficient context."""
        return cls(
            status="sufficient",
            required_count=0,
            supplied_required_count=0,
            missing_required_kinds=(),
            optional_supplied_count=optional_count,
            incomplete_details=("Some optional projections omitted"),
            overall_score=0.9,
        )
    
    @classmethod
    def partial(cls, missing: Tuple[str, ...], details: Tuple[str, ...] = ()) -> InternalContextCompleteness:
        """Create a completeness record for a partial context."""
        score = max(0.1, 1.0 - (len(missing) * 0.2))
        return cls(
            status="partial",
            required_count=len(missing),
            supplied_required_count=0,
            missing_required_kinds=missing,
            incomplete_details=details,
            overall_score=score,
        )
    
    @classmethod
    def insufficient(cls, missing: Tuple[str, ...]) -> InternalContextCompleteness:
        """Create a completeness record for an insufficient context."""
        return cls(
            status="insufficient",
            required_count=len(missing),
            supplied_required_count=0,
            missing_required_kinds=missing,
            overall_score=0.0,
        )
    
    @classmethod
    def invalid(cls, reasons: Tuple[str, ...]) -> InternalContextCompleteness:
        """Create a completeness record for an invalid context."""
        return cls(
            status="invalid",
            required_count=0,
            supplied_required_count=0,
            missing_required_kinds=(),
            incomplete_details=reasons,
            overall_score=0.0,
        )
    
    def is_usable(self) -> bool:
        """Check if this completeness level represents a usable context."""
        return self.status in ("complete", "sufficient")
    
    def is_acceptable_for_reflection(self) -> bool:
        """Check if completeness is acceptable for reflection purposes."""
        # Reflection can proceed with partial information
        return self.status in ("complete", "sufficient", "partial")
    
    def is_acceptable_for_simulation(self) -> bool:
        """Check if completeness is acceptable for simulation purposes."""
        # Simulation requires more complete context
        return self.status in ("complete", "sufficient")