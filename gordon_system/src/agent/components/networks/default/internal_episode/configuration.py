# Internal Episode Configuration
# =============================

"""
Immutable configuration for InternalEpisode handling.

Configuration controls how episodes are managed without containing provider
implementations or runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class InternalEpisodeConfig:
    """
    Immutable configuration for internal episode management.
    
    Configuration controls the episode lifecycle and validation but does NOT contain:
        • Provider implementations
        • Runtime state
        • Live references to subsystems
        
    CONFIGURATION GROUPS:
        
        lifecycle:
            • maximum_active_episodes: Max episodes in active states
            • minimum_context_confidence: Minimum confidence for valid context
            
        scope limits:
            • maximum_evidence_items: Hard limit on evidence items per episode
            • maximum_capability_requests: Max requests during coordination
            • maximum_plan_steps: Max steps in plan
            • maximum_child_episodes: Max derived child episodes
            
        plan limits:
            • maximum_step_count: Max total steps allowed
            • require_valid_dependencies: Whether to validate dependency graph
            
        evidence limits:
            • maximum_conflicts_per_episode: Max conflict records
            • record_all_evidence: Whether to keep all evidence items
            
        relationship limits:
            • maximum_relationship_depth: Max parent-child depth
            • maximum_descendants_per_root: Max descendants per root episode
            
        context refresh:
            • maximum_context_age_seconds: Oldest acceptable context age
            • require_refresh_on_lifecycle_change: Whether to refresh context
            
        confidence and completeness:
            • minimum_confidence_required: Minimum confidence for completion
            • minimum_completeness_required: Minimum completeness level
            
        history:
            • maximum_history_entries: How many episode snapshots to keep in memory
            
        provenance:
            • record_all_provenance: Whether to track full provenance
            
        validation:
            • strict_mode: Whether to fail on any validation issue
            • verify_outcome_validity: Whether to validate outcomes
            
        diagnostics:
            • enable_diagnostics: Whether to collect episode metrics
    """
    
    # Lifecycle limits
    maximum_active_episodes: int = 50
    """Maximum episodes in active states at once."""
    
    minimum_context_confidence: float = 0.3
    """Minimum confidence level for valid context."""
    
    # Scope limits
    maximum_evidence_items: int = 500
    """Hard limit on evidence items per episode."""
    
    maximum_capability_requests: int = 100
    """Maximum capability requests during coordination."""
    
    maximum_plan_steps: int = 50
    """Maximum steps in plan."""
    
    maximum_child_episodes: int = 10
    """Maximum child episodes that may be derived."""
    
    # Plan limits
    maximum_step_count: int = 50
    """Max total steps allowed in any episode."""
    
    require_valid_dependencies: bool = True
    """Whether to validate dependency graph (no cycles, etc.)."""
    
    # Evidence limits
    maximum_conflicts_per_episode: int = 100
    """Maximum conflict records per episode."""
    
    record_all_evidence: bool = False
    """Whether to keep all evidence items or truncate."""
    
    # Relationship limits
    maximum_relationship_depth: int = 5
    """Maximum parent-child relationship depth."""
    
    maximum_descendants_per_root: int = 100
    """Maximum descendants per root episode."""
    
    # Context refresh policy
    maximum_context_age_seconds: float = 3600.0  # 1 hour
    """Oldest acceptable context age in seconds."""
    
    require_refresh_on_lifecycle_change: bool = False
    """Whether to automatically refresh context on state changes."""
    
    # Quality thresholds
    minimum_confidence_required: float = 0.5
    """Minimum confidence for completion."""
    
    minimum_completeness_required: str = "partial"
    """Minimum completeness level required (complete, sufficient, partial)."""
    
    # History constraints
    maximum_history_entries: int = 100
    """How many episode snapshots to keep in memory."""
    
    # Provenance
    record_all_provenance: bool = True
    """Whether to track full provenance of all episodes."""
    
    # Validation
    strict_mode: bool = False
    """Whether to fail on any validation issue (vs. warning and proceeding)."""
    
    verify_outcome_validity: bool = True
    """Whether to validate outcomes before accepting them."""
    
    # Diagnostics
    enable_diagnostics: bool = False
    """Whether to collect episode metrics for diagnostics."""
    
    @classmethod
    def strict_config(cls) -> InternalEpisodeConfig:
        """Create a configuration with stricter limits for sensitive work."""
        return cls(
            maximum_active_episodes=25,
            minimum_context_confidence=0.6,
            maximum_evidence_items=100,
            maximum_capability_requests=25,
            maximum_plan_steps=20,
            maximum_child_episodes=3,
            maximum_relationship_depth=3,
            maximum_context_age_seconds=1800.0,  # 30 minutes
            minimum_confidence_required=0.7,
            strict_mode=True,
        )
    
    @classmethod
    def permissive_config(cls) -> InternalEpisodeConfig:
        """Create a configuration with relaxed limits for exploratory work."""
        return cls(
            maximum_active_episodes=100,
            minimum_context_confidence=0.2,
            maximum_evidence_items=1000,
            maximum_capability_requests=200,
            maximum_plan_steps=100,
            maximum_child_episodes=20,
            maximum_relationship_depth=10,
            maximum_context_age_seconds=7200.0,  # 2 hours
            minimum_confidence_required=0.3,
        )


def is_internal_episode_config(value: object) -> bool:
    """Check if a value is an InternalEpisodeConfig instance."""
    return isinstance(value, InternalEpisodeConfig)