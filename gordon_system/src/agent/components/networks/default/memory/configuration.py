# Memory Integration Configuration
# ================================

"""
Configuration models for memory integration.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# MEMORY INTEGRATION CONFIGURATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationConfig:
    """
    Immutable configuration for memory integration episodes.
    
    Configuration controls the behavior of memory integration without
    containing runtime resources or implementation details.
    
    PROPERTIES:
        • request_bounds: Limits on request properties
        • projection_limits: Maximum projections to process
        • memory_kind_limits: Max records per kind
        • temporal_scope: Time range constraints
        • relevance_thresholds: Minimum relevance scores
        • freshness_thresholds: Minimum freshness scores
        • factuality_constraints: Allowed factuality classes
        • source_authority_requirements: Required authority levels
        • association_limits: Max associations to identify
        • link_limits: Max links to establish
        • cluster_limits: Max clusters to form
        • conflict_limits: Max conflicts to record
        • gap_limits: Max gaps to identify
        • duplication_limits: Max duplicates to detect
        • inconsistency_limits: Max inconsistencies to identify
        • consolidation_limits: Max consolidation candidates
        • abstraction_limits: Max abstraction candidates
        • retrieval_cue_limits: Max retrieval cue proposals
        • update_proposal_limits: Max update proposals
        • recursion_controls: Repeated-retrieval safeguards
        • history_capacity: History record capacity
        • privacy_constraints: Privacy requirements
        • provenance_requirements: Provenance tracking needs
        
    MUST NOT CONTAIN:
        - Concrete stores
        - Database connections
        - Embedding models
        - Vector-store clients
        - Storage adapters
        - Scheduler objects
    """
    
    # Request bounds
    maximum_active_episodes: int = 100
    """Maximum active memory integration episodes."""
    
    maximum_ready_episodes: int = 50
    """Maximum ready memory integration episodes."""
    
    # Projection limits
    maximum_projection_references: int = 1000
    """Maximum projection references per request."""
    
    maximum_records_per_kind: int = 200
    """Maximum records per memory kind."""
    
    # Memory kind-specific limits
    maximum_episodic_records: int = 100
    """Maximum episodic memory records."""
    
    maximum_semantic_records: int = 200
    """Maximum semantic memory records."""
    
    maximum_autobiographical_records: int = 50
    """Maximum autobiographical memory records."""
    
    # Relationship limits
    maximum_associations: int = 300
    """Maximum associations to identify."""
    
    maximum_links: int = 150
    """Maximum links to establish."""
    
    # Cluster limits
    maximum_cluster_size: int = 20
    """Maximum members per cluster."""
    
    maximum_clusters: int = 30
    """Maximum clusters to form."""
    
    # Defect analysis limits
    maximum_conflicts: int = 50
    """Maximum conflicts to record."""
    
    maximum_gaps: int = 30
    """Maximum gaps to identify."""
    
    maximum_duplicates: int = 50
    """Maximum duplicates to detect."""
    
    maximum_inconsistencies: int = 30
    """Maximum inconsistencies to identify."""
    
    # Proposal limits
    maximum_consolidation_candidates: int = 20
    """Maximum consolidation candidates."""
    
    maximum_abstraction_candidates: int = 15
    """Maximum abstraction candidates."""
    
    maximum_retrieval_cues: int = 30
    """Maximum retrieval cue proposals."""
    
    maximum_update_proposals: int = 20
    """Maximum update proposals."""
    
    # Recursion controls
    maximum_retrieval_rounds: int = 3
    """Maximum rounds of retrieval allowed."""
    
    maximum_context_refreshes: int = 2
    """Maximum context refreshes allowed."""
    
    minimum_relevance: float = 0.1
    """Minimum relevance threshold (0.0 to 1.0)."""
    
    minimum_confidence: float = 0.3
    """Minimum confidence threshold (0.0 to 1.0)."""
    
    # Factuality constraints
    require_factuality_labels: bool = True
    """Require factuality labels for all memories."""
    
    require_source_authority_labels: bool = True
    """Require source authority labels for all memories."""
    
    preserve_conflicting_records: bool = True
    """Keep conflicting records visible."""
    
    preserve_reconstruction_classification: bool = True
    """Preserve reconstruction classifications."""
    
    strict_revision_mode: bool = False
    """Strict revision checking mode."""
    
    # History capacity
    maximum_history_entries: int = 1000
    """Maximum history entries to retain."""
    
    @classmethod
    def surface_level(cls) -> MemoryIntegrationConfig:
        """Create a configuration for shallow memory integration."""
        return cls(
            maximum_projection_references=200,
            maximum_records_per_kind=50,
            maximum_associations=100,
            maximum_links=50,
            maximum_conflicts=10,
            maximum_gaps=10,
        )
    
    @classmethod
    def standard_level(cls) -> MemoryIntegrationConfig:
        """Create a configuration for normal memory integration."""
        return cls(
            maximum_projection_references=1000,
            maximum_records_per_kind=200,
            maximum_associations=300,
            maximum_links=150,
            maximum_conflicts=50,
            maximum_gaps=30,
        )
    
    @classmethod
    def thorough_level(cls) -> MemoryIntegrationConfig:
        """Create a configuration for thorough memory integration."""
        return cls(
            maximum_projection_references=3000,
            maximum_records_per_kind=600,
            maximum_associations=1000,
            maximum_links=500,
            maximum_conflicts=100,
            maximum_gaps=50,
        )
    
    def allows_factuality(self, factuality: str) -> bool:
        """Check if a factuality class is allowed."""
        return factuality in {
            "observed",
            "recorded",
            "reported",
            "inferred",
            "simulated",
            "counterfactual",
            "hypothetical",
            "predicted",
        }