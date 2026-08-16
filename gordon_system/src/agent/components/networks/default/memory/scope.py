# Memory Integration Scope
# =========================

"""
Immutable scope constraints for memory integration episodes.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - All limits are explicit and bounded
    - No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# MEMORY INTEGRATION SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationScope:
    """
    Immutable scope constraints for a memory integration episode.
    
    Scope prevents one integration from becoming unbounded by imposing
    explicit limits on resources and evidence.
    
    PROPERTIES:
        • maximum_projection_references: Hard limit on projection references
        • maximum_full_records: Max full records to load
        • maximum_episodic_records: Max episodic memory records
        • maximum_semantic_records: Max semantic memory records
        • maximum_autobiographical_records: Max autobiographical memory records
        • maximum_procedural_references: Max procedural memory references
        • maximum_recent_experiences: Max recent experience projections
        • maximum_associations: Max associations to identify
        • maximum_links: Max links to establish
        • maximum_clusters: Max clusters to form
        • maximum_conflicts: Max conflicts to record
        • maximum_gaps: Max gaps to identify
        • maximum_duplicates: Max duplicates to detect
        • maximum_inconsistencies: Max inconsistencies to identify
        • maximum_consolidation_candidates: Max consolidation candidates
        • maximum_abstraction_candidates: Max abstraction candidates
        • maximum_proposals: Max proposals to generate
        • temporal_range_seconds: Maximum age of relevant memories
        • minimum_relevance: Minimum relevance threshold (0.0 to 1.0)
        • minimum_confidence: Minimum confidence threshold (0.0 to 1.0)
        • factuality_constraints: Allowed factuality classes
        • privacy_constraints: Required privacy levels
        
    BOUNDEDNESS:
        Every limit is explicit. Overflow must be recorded.
    """
    
    # Projection limits
    maximum_projection_references: int = 500
    """Maximum memory projection references to consider."""
    
    maximum_full_records: int = 100
    """Maximum full records to load into memory."""
    
    # Memory kind-specific limits
    maximum_episodic_records: int = 50
    """Maximum episodic memory records."""
    
    maximum_semantic_records: int = 100
    """Maximum semantic memory records."""
    
    maximum_autobiographical_records: int = 30
    """Maximum autobiographical memory records."""
    
    maximum_procedural_references: int = 20
    """Maximum procedural memory references."""
    
    # Recent experience limits
    maximum_recent_experiences: int = 25
    """Maximum recent experience projections."""
    
    # Relationship limits
    maximum_associations: int = 200
    """Maximum associations to identify."""
    
    maximum_links: int = 100
    """Maximum links to establish."""
    
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
    
    maximum_corrections: int = 15
    """Maximum correction proposals."""
    
    maximum_retention_proposals: int = 10
    """Maximum retention/de-emphasis proposals."""
    
    # Temporal constraints
    temporal_range_seconds: float = 604800.0  # 7 days default
    """Maximum age of relevant memories (in seconds)."""
    
    # Quality thresholds
    minimum_relevance: float = 0.1
    """Minimum relevance threshold (0.0 to 1.0)."""
    
    minimum_confidence: float = 0.3
    """Minimum confidence threshold (0.0 to 1.0)."""
    
    # Factuality constraints
    factuality_constraints: Tuple[str, ...] = field(
        default_factory=lambda: (
            "observed",
            "recorded",
            "reported",
            "inferred",
            "simulated",  # For simulation support purposes
            "counterfactual",  # For simulation support purposes
        )
    )
    """Allowed factuality classes."""
    
    # Privacy constraints
    privacy_constraints: Tuple[str, ...] = field(
        default_factory=lambda: ("internal", "restricted")
    )
    """Required privacy levels for included memories."""
    
    # Recursion controls
    maximum_retrieval_rounds: int = 3
    """Maximum rounds of retrieval allowed."""
    
    maximum_context_refreshes: int = 2
    """Maximum context refreshes allowed."""
    
    maximum_integration_depth: int = 5
    """Maximum integration depth (nested episodes)."""
    
    @classmethod
    def surface_level(cls) -> MemoryIntegrationScope:
        """Create a scope for shallow memory integration."""
        return cls(
            maximum_projection_references=100,
            maximum_full_records=20,
            maximum_episodic_records=10,
            maximum_semantic_records=20,
            maximum_associations=50,
            maximum_links=30,
            temporal_range_seconds=3600.0,  # 1 hour
        )
    
    @classmethod
    def standard_level(cls) -> MemoryIntegrationScope:
        """Create a scope for normal memory integration."""
        return cls(
            maximum_projection_references=500,
            maximum_full_records=100,
            maximum_episodic_records=50,
            maximum_semantic_records=100,
            maximum_associations=200,
            maximum_links=100,
            temporal_range_seconds=86400.0,  # 1 day
        )
    
    @classmethod
    def deep_level(cls) -> MemoryIntegrationScope:
        """Create a scope for thorough memory integration."""
        return cls(
            maximum_projection_references=2000,
            maximum_full_records=500,
            maximum_episodic_records=200,
            maximum_semantic_records=400,
            maximum_associations=800,
            maximum_links=400,
            temporal_range_seconds=604800.0,  # 7 days
        )
    
    def exceeds_projection_limit(self, count: int) -> bool:
        """Check if projection count exceeds limit."""
        return count > self.maximum_projection_references
    
    def exceeds_record_limit(self, count: int) -> bool:
        """Check if record count exceeds limit."""
        return count > self.maximum_full_records
    
    def is_factual_allowed(self, factuality: str) -> bool:
        """Check if factuality class is allowed in this scope."""
        return factuality in self.factuality_constraints