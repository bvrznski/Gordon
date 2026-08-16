# Memory Integration Purpose Models
# ==================================

"""
Immutable purpose models for memory integration requests.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# MEMORY INTEGRATION PURPOSE KINDS
# =============================================================================

class MemoryIntegrationPurposeKind:
    """
    Canonical purpose kinds for memory integration requests.
    
    Each purpose determines:
        - Required memory kinds
        - Required source confidence
        - Allowed factuality classes
        - Expected products
        - Scope limits
        - Completion rules
        - Proposal permissions
    """
    
    CONTEXT_ENRICHMENT = "context_enrichment"
    """Enrich context with relevant memories."""
    
    EPISODIC_INTEGRATION = "episodic_integration"
    """Integrate episodic memory records."""
    
    SEMANTIC_INTEGRATION = "semantic_integration"
    """Integrate semantic memory records."""
    
    AUTOBIOGRAPHICAL_INTEGRATION = "autobiographical_integration"
    """Integrate autobiographical memory records."""
    
    RECENT_EXPERIENCE_INTEGRATION = "recent_experience_integration"
    """Integrate recent experiences with prior knowledge."""
    
    MEMORY_ASSOCIATION = "memory_association"
    """Identify semantic associations between memories."""
    
    MEMORY_LINKAGE = "memory_linkage"
    """Establish structural links between memories."""
    
    MEMORY_CLUSTERING = "memory_clustering"
    """Form clusters of related memories."""
    
    MEMORY_CONFLICT_ANALYSIS = "memory_conflict_analysis"
    """Analyze conflicts between memory records."""
    
    MEMORY_GAP_ANALYSIS = "memory_gap_analysis"
    """Identify gaps in memory coverage."""
    
    MEMORY_DUPLICATION_ANALYSIS = "memory_duplication_analysis"
    """Detect potential duplicate memories."""
    
    MEMORY_INCONSISTENCY_ANALYSIS = "memory_inconsistency_analysis"
    """Identify inconsistencies within or across records."""
    
    RETRIEVAL_CUE_GENERATION = "retrieval_cue_generation"
    """Generate retrieval cues for future access."""
    
    CONSOLIDATION_CANDIDATE_GENERATION = "consolidation_candidate_generation"
    """Identify consolidation candidates."""
    
    ABSTRACTION_CANDIDATE_GENERATION = "abstraction_candidate_generation"
    """Identify abstraction candidates."""
    
    MEMORY_UPDATE_REVIEW = "memory_update_review"
    """Review memory update proposals."""
    
    MEMORY_CORRECTION_REVIEW = "memory_correction_review"
    """Review memory correction proposals."""
    
    IDENTITY_MEMORY_INTEGRATION = "identity_memory_integration"
    """Integrate memories relevant to identity."""
    
    NARRATIVE_MEMORY_INTEGRATION = "narrative_memory_integration"
    """Integrate memories for narrative coherence."""
    
    REFLECTION_MEMORY_SUPPORT = "reflection_memory_support"
    """Support reflection with memory evidence."""
    
    SIMULATION_MEMORY_SUPPORT = "simulation_memory_support"
    """Support simulation with memory evidence."""
    
    PREDICTION_MEMORY_SUPPORT = "prediction_memory_support"
    """Support prediction with memory evidence."""
    
    WORKSPACE_MEMORY_PREPARATION = "workspace_memory_preparation"
    """Prepare memories for workspace usage."""
    
    GENERAL_MEMORY_INTEGRATION = "general_memory_integration"
    """General purpose memory integration."""
    
    @classmethod
    def all_purposes(cls) -> Tuple[str, ...]:
        """Return all valid purpose kinds."""
        return (
            cls.CONTEXT_ENRICHMENT,
            cls.EPISODIC_INTEGRATION,
            cls.SEMANTIC_INTEGRATION,
            cls.AUTOBIOGRAPHICAL_INTEGRATION,
            cls.RECENT_EXPERIENCE_INTEGRATION,
            cls.MEMORY_ASSOCIATION,
            cls.MEMORY_LINKAGE,
            cls.MEMORY_CLUSTERING,
            cls.MEMORY_CONFLICT_ANALYSIS,
            cls.MEMORY_GAP_ANALYSIS,
            cls.MEMORY_DUPLICATION_ANALYSIS,
            cls.MEMORY_INCONSISTENCY_ANALYSIS,
            cls.RETRIEVAL_CUE_GENERATION,
            cls.CONSOLIDATION_CANDIDATE_GENERATION,
            cls.ABSTRACTION_CANDIDATE_GENERATION,
            cls.MEMORY_UPDATE_REVIEW,
            cls.MEMORY_CORRECTION_REVIEW,
            cls.IDENTITY_MEMORY_INTEGRATION,
            cls.NARRATIVE_MEMORY_INTEGRATION,
            cls.REFLECTION_MEMORY_SUPPORT,
            cls.SIMULATION_MEMORY_SUPPORT,
            cls.PREDICTION_MEMORY_SUPPORT,
            cls.WORKSPACE_MEMORY_PREPARATION,
            cls.GENERAL_MEMORY_INTEGRATION,
        )


# =============================================================================
# MEMORY INTEGRATION PURPOSE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationPurpose:
    """
    Immutable purpose descriptor for a memory integration episode.
    
    PROPERTIES:
        • kind: Purpose kind (MemoryIntegrationPurposeKind.*)
        • description: Human-readable description
        • required_memory_kinds: Required memory kinds for this purpose
        • minimum_confidence_threshold: Minimum confidence required
        • allowed_factuality_classes: Factuality classes permitted
        • expected_products: Product kinds expected from this integration
        • completion_criteria: Explicit conditions for success
        
    DETERMINES:
        - Memory kinds needed
        - Source confidence requirements
        - Factuality constraints
        - Expected products
        - Scope limits
        - Completion rules
    """
    
    # Purpose kind
    kind: str  # MemoryIntegrationPurposeKind.*
    """The purpose kind."""
    
    # Description
    description: str = ""
    """Human-readable description."""
    
    # Memory requirements
    required_memory_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Required memory kinds (MemoryKind.*)."""
    
    minimum_confidence_threshold: float = 0.3
    """Minimum confidence threshold for included memories."""
    
    allowed_factuality_classes: Tuple[str, ...] = field(
        default_factory=lambda: (
            "observed",
            "recorded",
            "reported",
            "inferred",
            "simulated",
            "counterfactual",
        )
    )
    """Factuality classes permitted for this purpose."""
    
    # Product expectations
    expected_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product kinds expected from integration."""
    
    # Completion criteria
    completion_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit conditions for successful completion."""
    
    @classmethod
    def context_enrichment(
        cls,
        minimum_confidence_threshold: float = 0.3,
    ) -> MemoryIntegrationPurpose:
        """Create a context enrichment purpose."""
        return cls(
            kind=MemoryIntegrationPurposeKind.CONTEXT_ENRICHMENT,
            description="Enrich current context with relevant memories",
            required_memory_kinds=("episodic", "semantic"),
            minimum_confidence_threshold=minimum_confidence_threshold,
            allowed_factuality_classes=("observed", "recorded", "reported", "inferred"),
            expected_products=(
                "memory_context",
                "associations",
                "links",
            ),
        )
    
    @classmethod
    def episodic_integration(
        cls,
        minimum_confidence_threshold: float = 0.5,
    ) -> MemoryIntegrationPurpose:
        """Create an episodic integration purpose."""
        return cls(
            kind=MemoryIntegrationPurposeKind.EPISODIC_INTEGRATION,
            description="Integrate episodic memory records",
            required_memory_kinds=("episodic",),
            minimum_confidence_threshold=minimum_confidence_threshold,
            allowed_factuality_classes=("observed", "recorded"),
            expected_products=(
                "episodic_integration",
                "links",
                "clusters",
            ),
        )
    
    @classmethod
    def semantic_integration(
        cls,
        minimum_confidence_threshold: float = 0.4,
    ) -> MemoryIntegrationPurpose:
        """Create a semantic integration purpose."""
        return cls(
            kind=MemoryIntegrationPurposeKind.SEMANTIC_INTEGRATION,
            description="Integrate semantic memory records",
            required_memory_kinds=("semantic",),
            minimum_confidence_threshold=minimum_confidence_threshold,
            allowed_factuality_classes=(
                "observed",
                "recorded",
                "reported",
                "inferred",
            ),
            expected_products=(
                "semantic_integration",
                "consolidation_candidates",
                "abstraction_candidates",
            ),
        )
    
    @classmethod
    def conflict_analysis(
        cls,
        minimum_confidence_threshold: float = 0.5,
    ) -> MemoryIntegrationPurpose:
        """Create a conflict analysis purpose."""
        return cls(
            kind=MemoryIntegrationPurposeKind.MEMORY_CONFLICT_ANALYSIS,
            description="Analyze conflicts between memory records",
            required_memory_kinds=("episodic", "semantic"),
            minimum_confidence_threshold=minimum_confidence_threshold,
            allowed_factuality_classes=(
                "observed",
                "recorded",
                "reported",
                "inferred",
            ),
            expected_products=("conflicts", "gaps", "proposals"),
        )
    
    @classmethod
    def consolidation_candidate_generation(
        cls,
        minimum_confidence_threshold: float = 0.6,
    ) -> MemoryIntegrationPurpose:
        """Create a consolidation candidate generation purpose."""
        return cls(
            kind=MemoryIntegrationPurposeKind.CONSOLIDATION_CANDIDATE_GENERATION,
            description="Identify consolidation candidates",
            required_memory_kinds=("episodic", "semantic"),
            minimum_confidence_threshold=minimum_confidence_threshold,
            allowed_factuality_classes=(
                "observed",
                "recorded",
                "reported",
                "inferred",
            ),
            expected_products=("consolidation_candidates",),
        )