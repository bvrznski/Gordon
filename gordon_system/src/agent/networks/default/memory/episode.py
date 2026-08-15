# Memory Integration Episode
# ==========================

"""
Immutable episode model for memory integration.

ARCHITECTURAL PRINCIPLES:
    - Reuses InternalEpisode machinery
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY INTEGRATION EPISODE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationEpisode:
    """
    Immutable episode for one memory integration cycle.
    
    This reuses the canonical InternalEpisode machinery while adding
    memory-specific properties. It is bounded in scope and lifetime.
    
    PROPERTIES:
        • episode_id: Unique identifier for this episode
        • purpose: Memory integration purpose (purpose.MemoryIntegrationPurpose)
        • subject: Integration subject (subject.MemoryIntegrationSubject)
        • scope: Scope constraints (scope.MemoryIntegrationScope)
        • context_id: Bound context reference
        • context_revision: Context version at start
        
        • memory_projection_references: References to required projections
        • selected_memory_records: Selected memory records
        • associations: Identified associations
        • links: Established links
        • clusters: Formed clusters
        • conflicts: Identified conflicts
        • gaps: Identified gaps
        • duplicates: Detected duplicates
        • inconsistencies: Identified inconsistencies
        
        • consolidation_candidates: Proposed consolidations
        • abstraction_candidates: Proposed abstractions
        • retrieval_cues: Proposed retrieval cues
        • update_proposals: Proposed updates
        • correction_proposals: Proposed corrections
        
        • products: Generated memory integration products
        • outcome: Episode outcome (outcome.MemoryIntegrationOutcome)
        • continuation: Next steps (continuation.MemoryIntegrationContinuation)
        
    REUSES:
        - InternalEpisode lifecycle machinery
        - InternalEpisode evidence collection
        - InternalThought product format
    
    DOES NOT OWN:
        - Memory storage or retrieval
        - Persistence operations
        - Authority to modify records
    """
    
    # Episode identity and binding
    episode_id: str
    """Unique identifier for this episode."""
    
    purpose: str  # Serialized MemoryIntegrationPurpose
    """Memory integration purpose (serialized)."""
    
    subject: str  # Serialized MemoryIntegrationSubject
    """Integration subject (serialized)."""
    
    scope: str  # Serialized MemoryIntegrationScope
    """Scope constraints (serialized)."""
    
    context_id: str
    """Bound context reference."""
    
    context_revision: int = 1
    """Context version at start."""
    
    # Memory references and selections
    memory_projection_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to required projections."""
    
    selected_memory_records: Tuple[str, ...] = field(default_factory=tuple)
    """Selected memory records (serialized)."""
    
    # Relationship models
    associations: Tuple[str, ...] = field(default_factory=tuple)
    """Identified associations (serialized MemoryAssociation)."""
    
    links: Tuple[str, ...] = field(default_factory=tuple)
    """Established links (serialized MemoryLink)."""
    
    clusters: Tuple[str, ...] = field(default_factory=tuple)
    """Formed clusters (serialized MemoryClusterCandidate)."""
    
    # Defect analysis
    conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Identified conflicts (serialized MemoryConflict)."""
    
    gaps: Tuple[str, ...] = field(default_factory=tuple)
    """Identified gaps (serialized MemoryGap)."""
    
    duplicates: Tuple[str, ...] = field(default_factory=tuple)
    """Detected duplicates (serialized MemoryDuplicateCandidate)."""
    
    inconsistencies: Tuple[str, ...] = field(default_factory=tuple)
    """Identified inconsistencies (serialized MemoryInconsistency)."""
    
    # Proposal models
    consolidation_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Proposed consolidations (serialized MemoryConsolidationCandidate)."""
    
    abstraction_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Proposed abstractions (serialized MemoryAbstractionCandidate)."""
    
    retrieval_cues: Tuple[str, ...] = field(default_factory=tuple)
    """Proposed retrieval cues (serialized MemoryRetrievalCueProposal)."""
    
    update_proposals: Tuple[str, ...] = field(default_factory=tuple)
    """Proposed updates (serialized MemoryUpdateProposal)."""
    
    correction_proposals: Tuple[str, ...] = field(default_factory=tuple)
    """Proposed corrections (serialized MemoryCorrectionProposal)."""
    
    # Results
    products: Tuple[str, ...] = field(default_factory=tuple)
    """Generated memory integration products."""
    
    outcome: str = ""  # Serialized MemoryIntegrationOutcome
    """Episode outcome."""
    
    continuation: str = ""  # Serialized MemoryIntegrationContinuation
    """Next steps recommendation."""
    
    # Status tracking
    status: str = "pending"
    """Episode status (pending, in_progress, completed, failed, cancelled)."""
    
    started_at_utc: Optional[str] = None
    """When the episode started (ISO format)."""
    
    completed_at_utc: Optional[str] = None
    """When the episode completed (ISO format)."""
    
    @classmethod
    def new(
        cls,
        purpose: str,
        subject: str,
        scope: str,
        context_id: str,
        episode_id: Optional[str] = None,
    ) -> MemoryIntegrationEpisode:
        """Create a new memory integration episode."""
        return cls(
            episode_id=episode_id or f"memory_integration_{id(cls)}",
            purpose=purpose,
            subject=subject,
            scope=scope,
            context_id=context_id,
            status="pending",
        )
    
    def can_proceed(self) -> bool:
        """Check if this episode is ready to proceed."""
        return self.status in {"pending", "in_progress"}
    
    def has_completed(self) -> bool:
        """Check if this episode has reached a terminal state."""
        return self.status in {"completed", "failed", "cancelled"}