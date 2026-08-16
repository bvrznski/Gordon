# Identity Integration Configuration Model
# =======================================

"""
Immutable identity integration configuration model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdentityIntegrationConfig:
    """
    Immutable configuration for identity integration coordination.
    
    PROPERTIES:
        • maximum_active_episodes: Maximum concurrent identity integration episodes
        • maximum_ready_episodes: Maximum pending episodes
        • maximum_source_references: Max sources per episode
        • maximum_identity_aspects: Max aspects to consider
        • maximum_roles: Max roles to consider
        • maximum_values: Max values to consider
        • maximum_commitments: Max commitments to consider
        • maximum_capabilities: Max capabilities to assess
        • maximum_limitations: Max limitations to record
        • maximum_claims: Max claims to evaluate
        • maximum_conflicts: Max conflicts to track
        • maximum_tensions: Max tensions to track
        • maximum_gaps: Max gaps to identify
        • maximum_revision_depth: Max recursive revision depth
        • maximum_recursive_review_depth: Max recursion depth
        • require_authoritative_identity_projection: Require Identity Capability projection
        • preserve_conflicting_claims: Keep conflicting claims visible
        • minimum_proposal_confidence: Minimum confidence for proposals
        • history_capacity: How many episodes to remember
    """
    
    # Episode bounds
    maximum_active_episodes: int = 10
    """Maximum concurrent identity integration episodes."""
    
    maximum_ready_episodes: int = 20
    """Maximum pending episodes."""
    
    # Evidence bounds
    maximum_source_references: int = 100
    """Maximum source references per episode."""
    
    maximum_identity_aspects: int = 50
    """Maximum identity aspects to consider."""
    
    maximum_roles: int = 20
    """Maximum roles to consider."""
    
    maximum_values: int = 30
    """Maximum values to consider."""
    
    maximum_commitments: int = 25
    """Maximum commitments to consider."""
    
    maximum_capabilities: int = 15
    """Maximum capabilities to assess."""
    
    maximum_limitations: int = 15
    """Maximum limitations to record."""
    
    # Evaluation bounds
    maximum_claims: int = 100
    """Maximum claims to evaluate."""
    
    maximum_conflicts: int = 20
    """Maximum conflicts to track."""
    
    maximum_tensions: int = 20
    """Maximum tensions to track."""
    
    maximum_gaps: int = 30
    """Maximum gaps to identify."""
    
    # Revision bounds
    maximum_revision_depth: int = 5
    """Maximum revision depth."""
    
    maximum_recursive_review_depth: int = 3
    """Maximum recursive review depth."""
    
    # Requirements
    require_authoritative_identity_projection: bool = True
    """Require Identity Capability projection."""
    
    preserve_conflicting_claims: bool = True
    """Keep conflicting claims visible."""
    
    minimum_proposal_confidence: float = 0.6
    """Minimum confidence for proposals."""
    
    history_capacity: int = 100
    """How many episodes to remember."""