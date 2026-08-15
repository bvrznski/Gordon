# Reflection Coordination Configuration
# ====================================

"""
Immutable configuration for reflection coordination.

ARCHITECTURAL PRINCIPLES:
    - Configuration is immutable (deeply frozen)
    - No runtime dependencies or live objects
    - All limits are explicit and bounded
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ReflectionCoordinationConfig:
    """
    Immutable configuration for reflection coordination.
    
    This configuration controls the bounds of reflection activities.
    """
    
    # Active reflection limits
    maximum_active_reflections: int = 5
    """Maximum concurrent active reflections."""
    
    maximum_ready_reflections: int = 10
    """Maximum ready-to-process reflections."""
    
    # Context requirements
    minimum_context_completeness: str = "sufficient"
    """Minimum completeness for context (complete/sufficient/partial/insufficient)."""
    
    # Recursion rules
    default_recursion_depth_limit: int = 3
    """Default maximum recursion depth."""
    
    require_new_evidence_for_recursion: bool = True
    """If true, child reflections need new evidence."""
    
    maximum_no_result_sequence: int = 3
    """Max consecutive no-result reflections before attenuation."""
    
    # Evidence limits
    maximum_evidence_per_reflection: int = 100
    """Maximum evidence items to collect per reflection."""
    
    maximum_products_per_reflection: int = 15
    """Maximum products expected per reflection."""
    
    minimum_confidence_threshold: float = 0.5
    """Minimum confidence for accepted products."""
    
    # History limits
    max_recent_purposes_history: int = 25
    """Max purpose summaries to retain."""
    
    max_recent_subjects_history: int = 25
    """Max subject references to retain."""
    
    @classmethod
    def standard(cls) -> ReflectionCoordinationConfig:
        """Create a standard configuration."""
        return cls(
            maximum_active_reflections=5,
            maximum_ready_reflections=10,
            minimum_context_completeness="sufficient",
            default_recursion_depth_limit=3,
            require_new_evidence_for_recursion=True,
            maximum_no_result_sequence=3,
            maximum_evidence_per_reflection=100,
            maximum_products_per_reflection=15,
        )
    
    @classmethod
    def strict(cls) -> ReflectionCoordinationConfig:
        """Create a strict configuration for sensitive work."""
        return cls(
            maximum_active_reflections=2,
            maximum_ready_reflections=5,
            minimum_context_completeness="complete",
            default_recursion_depth_limit=2,
            require_new_evidence_for_recursion=True,
            maximum_no_result_sequence=1,
            maximum_evidence_per_reflection=25,
            maximum_products_per_reflection=5,
        )
    
    @classmethod
    def permissive(cls) -> ReflectionCoordinationConfig:
        """Create a permissive configuration for exploratory work."""
        return cls(
            maximum_active_reflections=10,
            maximum_ready_reflections=20,
            minimum_context_completeness="partial",
            default_recursion_depth_limit=5,
            require_new_evidence_for_recursion=False,
            maximum_no_result_sequence=5,
            maximum_evidence_per_reflection=200,
            maximum_products_per_reflection=30,
        )