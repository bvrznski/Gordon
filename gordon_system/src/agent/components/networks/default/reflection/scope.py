# Reflection Scope Models
# ========================

"""
Immutable models for reflection scope constraints.

ARCHITECTURAL PRINCIPLES:
    - Scopes define bounded limits on reflection activities
    - All constraints must be explicit and bounded
    - No runtime dependencies in domain objects
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ReflectionScope:
    """
    Immutable scope definition for a reflection.
    
    The scope defines the bounded constraints on what the reflection
    can access and process. This ensures reflections remain bounded.
    """
    
    maximum_evidence_items: int = 100
    """Maximum evidence items to collect."""
    
    maximum_prior_thoughts: int = 50
    """Maximum prior thoughts to examine."""
    
    maximum_memory_references: int = 30
    """Maximum memory references to use."""
    
    maximum_temporal_range_seconds: int = 86400  # 24 hours
    """Maximum temporal range for evidence (in seconds)."""
    
    maximum_plan_steps: int = 50
    """Maximum plan steps to examine."""
    
    maximum_capability_requests: int = 10
    """Maximum capability requests allowed."""
    
    maximum_products_expected: int = 15
    """Maximum products expected from reflection."""
    
    maximum_follow_up_proposals: int = 5
    """Maximum follow-up proposals allowed."""
    
    maximum_child_episodes: int = 3
    """Maximum child episodes that can be derived."""
    
    maximum_reflection_depth: int = 3
    """Maximum recursion depth allowed."""
    
    maximum_revisions: int = 10
    """Maximum context revisions allowed."""
    
    excluded_subject_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Subject kinds that should be excluded."""
    
    permitted_product_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Product kinds that are permitted (empty = all)."""
    
    required_confidence: float = 0.5
    """Minimum confidence threshold for products."""
    
    @classmethod
    def bounded(cls) -> ReflectionScope:
        """Create a bounded scope with standard limits."""
        return cls(
            maximum_evidence_items=100,
            maximum_prior_thoughts=50,
            maximum_memory_references=30,
            maximum_temporal_range_seconds=86400,
            maximum_plan_steps=50,
            maximum_capability_requests=10,
            maximum_products_expected=15,
        )
    
    @classmethod
    def strict(cls) -> ReflectionScope:
        """Create a strict scope for sensitive work."""
        return cls(
            maximum_evidence_items=25,
            maximum_prior_thoughts=20,
            maximum_memory_references=10,
            maximum_temporal_range_seconds=3600,  # 1 hour
            maximum_plan_steps=20,
            maximum_capability_requests=3,
            maximum_products_expected=5,
            maximum_reflection_depth=2,
        )
    
    @classmethod
    def expansive(cls) -> ReflectionScope:
        """Create an expansive scope for comprehensive analysis."""
        return cls(
            maximum_evidence_items=200,
            maximum_prior_thoughts=100,
            maximum_memory_references=50,
            maximum_temporal_range_seconds=604800,  # 7 days
            maximum_plan_steps=100,
            maximum_capability_requests=20,
            maximum_products_expected=30,
        )
    
    def is_within_bounds(self) -> bool:
        """Check if all bounds are within valid ranges."""
        return (
            self.maximum_evidence_items >= 0 and
            self.maximum_prior_thoughts >= 0 and
            self.maximum_memory_references >= 0 and
            self.maximum_temporal_range_seconds >= 0 and
            self.maximum_plan_steps >= 0 and
            self.maximum_capability_requests >= 0 and
            self.maximum_products_expected >= 0 and
            self.maximum_follow_up_proposals >= 0 and
            self.maximum_child_episodes >= 0 and
            self.maximum_reflection_depth >= 1 and
            self.maximum_revisions >= 0 and
            0.0 <= self.required_confidence <= 1.0
        )