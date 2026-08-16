# Internal Context Freshness Model
# ================================

"""
Structured freshness assessment for internal context.

Freshness evaluates temporal relevance of context items without requiring
wall-clock access during assembly (uses injected time).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class InternalContextFreshness:
    """
    Structured freshness assessment for internal context.
    
    Freshness evaluates temporal relevance of context items without requiring
    wall-clock access during assembly (uses injected time).
    
    FRESHNESS STATES:
        • fresh: Recent and current (within acceptable window)
        • recent: Somewhat recent, still relevant
        • stale: Older information, may need verification
        • expired: Beyond acceptable age for this context
    
    PROPERTIES:
        • status: One of the freshness states above
        • oldest_projection_age_seconds: Age of oldest projection in seconds
        • newest_projection_age_seconds: Age of newest projection in seconds
        • stale_projections: List of projection kinds considered stale
        • freshness_score: Numerical score from 0.0 to 1.0
    """
    
    status: str = "fresh"
    """Freshness state."""
    
    oldest_projection_age_seconds: float = 0.0
    """Age of the oldest projection in seconds (0.0 = just captured)."""
    
    newest_projection_age_seconds: float = 0.0
    """Age of the newest projection in seconds."""
    
    stale_projections: Tuple[str, ...] = field(default_factory=tuple)
    """Projection kinds considered too old for their purpose."""
    
    freshness_score: float = 1.0
    """Numerical freshness score from 0.0 to 1.0."""
    
    maximum_allowed_age_seconds: float = 3600.0  # Default: 1 hour
    """Maximum acceptable age in seconds for any projection."""
    
    @classmethod
    def fresh(cls) -> InternalContextFreshness:
        """Create a fresh context record."""
        return cls(
            status="fresh",
            oldest_projection_age_seconds=0.0,
            newest_projection_age_seconds=0.0,
            stale_projections=(),
            freshness_score=1.0,
        )
    
    @classmethod
    def recent(cls, age_seconds: float = 3600.0) -> InternalContextFreshness:
        """Create a recent context record."""
        score = max(0.5, 1.0 - (age_seconds / 7200.0))  # Decay to 0.5 after 2 hours
        return cls(
            status="recent",
            oldest_projection_age_seconds=age_seconds,
            newest_projection_age_seconds=age_seconds * 0.9,
            stale_projections=(),
            freshness_score=score,
        )
    
    @classmethod
    def stale(cls, age_seconds: float = 7200.0) -> InternalContextFreshness:
        """Create a stale context record."""
        score = max(0.1, 1.0 - (age_seconds / 14400.0))  # Decay to 0.1 after 4 hours
        return cls(
            status="stale",
            oldest_projection_age_seconds=age_seconds,
            newest_projection_age_seconds=age_seconds * 0.95,
            stale_projections=("memory", "workspace"),
            freshness_score=score,
        )
    
    @classmethod
    def expired(cls, age_seconds: float = 86400.0) -> InternalContextFreshness:
        """Create an expired context record."""
        return cls(
            status="expired",
            oldest_projection_age_seconds=age_seconds,
            newest_projection_age_seconds=age_seconds * 0.99,
            stale_projections=("memory", "workspace", "prediction"),
            freshness_score=0.0,
        )
    
    @classmethod
    def with_max_age(cls, age_seconds: float) -> InternalContextFreshness:
        """Create a fresh record with specified max allowed age."""
        return cls(
            status="fresh",
            maximum_allowed_age_seconds=age_seconds,
        )
    
    def is_acceptable(self) -> bool:
        """Check if freshness level is acceptable for use."""
        return self.status in ("fresh", "recent")
    
    def is_stale(self) -> bool:
        """Check if any projections are considered stale."""
        return len(self.stale_projections) > 0
    
    def get_staleness_ratio(self) -> float:
        """
        Calculate the staleness ratio.
        
        Returns a value from 0.0 (fresh) to 1.0 (expired).
        """
        if self.maximum_allowed_age_seconds <= 0:
            return 0.5
        
        ratio = min(1.0, self.oldest_projection_age_seconds / self.maximum_allowed_age_seconds)
        return ratio