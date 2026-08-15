# Identity Integration State Model
# ================================

"""
Immutable identity integration state model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityIntegrationState:
    """
    Immutable representation of identity integration coordination state.
    
    PROPERTIES:
        • active_episode_id: Current active episode (if any)
        • ready_episodes: Episodes waiting to start
        • waiting_episodes: Episodes waiting for resources
        • current_identity_projection_revision: Current revision of identity projection
        • recent_purpose_summaries: Recent purposes used
        • recent_subject_summaries: Recent subjects integrated
        • recent_product_digests: Recent products generated
        • unresolved_conflict_count: Number of unresolved conflicts
        • unresolved_tension_count: Number of unresolved tensions
        • unresolved_gap_count: Number of unresolved gaps
        • pending_proposal_ids: Proposal IDs awaiting action
        • continuity_summary: Summary of continuity assessments
        • consistency_summary: Summary of consistency assessments
        • coherence_summary: Summary of coherence assessments
        • recursive_review_depth: Current recursion depth
        • context_revision: Context revision at time of state capture
        • state_revision: State revision number
        • no_result_count: Number of consecutive no-result outcomes
    """
    
    active_episode_id: str = ""
    """Current active episode (if any)."""
    
    ready_episodes: Tuple[str, ...] = field(default_factory=tuple)
    """Episode IDs waiting to start."""
    
    waiting_episodes: Tuple[str, ...] = field(default_factory=tuple)
    """Episode IDs waiting for resources."""
    
    current_identity_projection_revision: str = "1"
    """Current revision of identity projection."""
    
    recent_purpose_summaries: Tuple[str, ...] = field(default_factory=tuple)
    """Recent purposes used."""
    
    recent_subject_summaries: Tuple[str, ...] = field(default_factory=tuple)
    """Recent subjects integrated."""
    
    recent_product_digests: Tuple[str, ...] = field(default_factory=tuple)
    """Recent products generated."""
    
    unresolved_conflict_count: int = 0
    """Number of unresolved conflicts."""
    
    unresolved_tension_count: int = 0
    """Number of unresolved tensions."""
    
    unresolved_gap_count: int = 0
    """Number of unresolved gaps."""
    
    pending_proposal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Proposal IDs awaiting action."""
    
    continuity_summary: str = ""
    """Summary of continuity assessments."""
    
    consistency_summary: str = ""
    """Summary of consistency assessments."""
    
    coherence_summary: str = ""
    """Summary of coherence assessments."""
    
    recursive_review_depth: int = 0
    """Current recursion depth."""
    
    context_revision: str = "1"
    """Context revision at time of state capture."""
    
    state_revision: int = 1
    """State revision number."""
    
    no_result_count: int = 0
    """Number of consecutive no-result outcomes."""