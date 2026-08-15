# Memory Integration Plan Models
# ==============================

"""
Immutable plan models for memory integration episodes.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# COORDINATION STEP KINDS
# =============================================================================

class CoordinationStepKind:
    """
    Canonical coordination step kinds for memory integration.
    
    Each step describes one semantic coordination action without
    implementing infrastructure or storage operations.
    """
    
    VALIDATE_CONTEXT = "validate_context"
    """Validate the bound context."""
    
    VALIDATE_SUBJECT = "validate_subject"
    """Validate the subject reference."""
    
    VALIDATE_MEMORY_REFERENCES = "validate_memory_references"
    """Validate memory projection references."""
    
    REQUEST_EPISODIC_PROJECTION = "request_episodic_projection"
    """Request episodic memory projections."""
    
    REQUEST_SEMANTIC_PROJECTION = "request_semantic_projection"
    """Request semantic memory projections."""
    
    REQUEST_AUTOBIOGRAPHICAL_PROJECTION = "request_autobiographical_projection"
    """Request autobiographical memory projections."""
    
    REQUEST_PROCEDURAL_REFERENCE = "request_procedural_reference"
    """Request procedural memory references."""
    
    REQUEST_RECENT_EXPERIENCE_PROJECTION = "request_recent_experience_projection"
    """Request recent experience projections."""
    
    NORMALIZE_MEMORY_KIND = "normalize_memory_kind"
    """Normalize memory kind classification."""
    
    NORMALIZE_SOURCE_AUTHORITY = "normalize_source_authority"
    """Normalize source authority classification."""
    
    NORMALIZE_FACTUALITY = "normalize_factuality"
    """Normalize factuality classifications."""
    
    NORMALIZE_REVISIONS = "normalize_revisions"
    """Normalize record revisions."""
    
    ASSESS_RELEVANCE = "assess_relevance"
    """Assess memory relevance."""
    
    ASSESS_FRESHNESS = "assess_freshness"
    """Assess memory freshness."""
    
    IDENTIFY_ASSOCIATIONS = "identify_associations"
    """Identify semantic associations."""
    
    IDENTIFY_LINKS = "identify_links"
    """Identify structural links."""
    
    IDENTIFY_CLUSTERS = "identify_clusters"
    """Identify memory clusters."""
    
    IDENTIFY_CONFLICTS = "identify_conflicts"
    """Identify conflicts between records."""
    
    IDENTIFY_GAPS = "identify_gaps"
    """Identify gaps in coverage."""
    
    IDENTIFY_DUPLICATES = "identify_duplicates"
    """Identify duplicate candidates."""
    
    IDENTIFY_INCONSISTENCIES = "identify_inconsistencies"
    """Identify inconsistencies."""
    
    GENERATE_RETRIEVAL_CUES = "generate_retrieval_cues"
    """Generate retrieval cue proposals."""
    
    GENERATE_CONSOLIDATION_CANDIDATES = "generate_consolidation_candidates"
    """Generate consolidation candidates."""
    
    GENERATE_ABSTRACTION_CANDIDATES = "generate_abstraction_candidates"
    """Generate abstraction candidates."""
    
    GENERATE_PROPOSALS = "generate_proposals"
    """Generate proposals (consolidation, update, correction)."""
    
    VALIDATE_PRODUCTS = "validate_products"
    """Validate generated products."""
    
    COMPOSE_OUTCOME = "compose_outcome"
    """Compose final outcome."""
    
    PREPARE_PROPOSALS = "prepare_proposals"
    """Prepare proposals for Memory authority."""


# =============================================================================
# MEMORY INTEGRATION PLAN
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationPlan:
    """
    Immutable declarative plan for memory integration.
    
    A plan describes the sequence of coordination steps without implementing
    them. Each step has dependencies and conditions.
    
    PROPERTIES:
        • plan_id: Unique identifier for this plan
        • purpose: Purpose this plan serves
        • subject: Subject being integrated
        • scope: Scope constraints for execution
        
        • steps: Ordered sequence of coordination steps
        • step_dependencies: Dependencies between steps
        • step_conditions: Conditions for each step's execution
        
        • max_retrieval_rounds: Maximum retrieval rounds allowed
        • max_context_refreshes: Maximum context refreshes allowed
        • max_integration_depth: Maximum nested episode depth
        
    IS DECLARATIVE:
        - Describes WHAT should happen
        - Does not HOW it happens
        - No runtime resource allocation
    """
    
    # Plan identity and scope
    plan_id: str
    """Unique identifier for this plan."""
    
    purpose: str  # MemoryIntegrationPurpose.*
    """Purpose this plan serves."""
    
    subject: str  # MemoryIntegrationSubject.*
    """Subject being integrated."""
    
    scope: str  # Serialized MemoryIntegrationScope
    """Scope constraints (serialized)."""
    
    # Coordination steps
    steps: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered sequence of coordination steps."""
    
    step_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies between steps (format: 'step_b:step_a')."""
    
    step_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions for each step's execution."""
    
    # Recursion controls
    max_retrieval_rounds: int = 3
    """Maximum retrieval rounds allowed."""
    
    max_context_refreshes: int = 2
    """Maximum context refreshes allowed."""
    
    max_integration_depth: int = 5
    """Maximum integration depth (nested episodes)."""
    
    @classmethod
    def context_enrichment(cls) -> MemoryIntegrationPlan:
        """Create a plan for context enrichment."""
        return cls(
            plan_id="context_enrichment",
            purpose=CoordinationStepKind.VALIDATE_CONTEXT,
            subject=CoordinationStepKind.ASSESS_RELEVANCE,
            steps=(
                CoordinationStepKind.VALIDATE_CONTEXT,
                CoordinationStepKind.VALIDATE_SUBJECT,
                CoordinationStepKind.REQUEST_SEMANTIC_PROJECTION,
                CoordinationStepKind.ASSESS_RELEVANCE,
                CoordinationStepKind.COMPOSE_OUTCOME,
            ),
        )
    
    @classmethod
    def episodic_integration(cls) -> MemoryIntegrationPlan:
        """Create a plan for episodic integration."""
        return cls(
            plan_id="episodic_integration",
            purpose=CoordinationStepKind.REQUEST_EPISODIC_PROJECTION,
            subject=CoordinationStepKind.IDENTIFY_CLUSTERS,
            steps=(
                CoordinationStepKind.VALIDATE_CONTEXT,
                CoordinationStepKind.REQUEST_EPISODIC_PROJECTION,
                CoordinationStepKind.ASSESS_RELEVANCE,
                CoordinationStepKind.ASSESS_FRESHNESS,
                CoordinationStepKind.IDENTIFY_ASSOCIATIONS,
                CoordinationStepKind.IDENTIFY_LINKS,
                CoordinationStepKind.IDENTIFY_CLUSTERS,
                CoordinationStepKind.COMPOSE_OUTCOME,
            ),
        )
    
    @classmethod
    def conflict_analysis(cls) -> MemoryIntegrationPlan:
        """Create a plan for conflict analysis."""
        return cls(
            plan_id="conflict_analysis",
            purpose=CoordinationStepKind.VALIDATE_MEMORY_REFERENCES,
            subject=CoordinationStepKind.IDENTIFY_CONFLICTS,
            steps=(
                CoordinationStepKind.VALIDATE_CONTEXT,
                CoordinationStepKind.REQUEST_EPISODIC_PROJECTION,
                CoordinationStepKind.NORMALIZE_FACTUALITY,
                CoordinationStepKind.IDENTIFY_CONFLICTS,
                CoordinationStepKind.GENERATE_PROPOSALS,
                CoordinationStepKind.COMPOSE_OUTCOME,
            ),
        )