# Memory Link Models
# ==================

"""
Immutable link-related models for memory records.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY LINK
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryLink:
    """
    Immutable proposed or accepted link between memory records.
    
    A link is a structural relationship that may be:
        - Proposed (awaiting validation)
        - Accepted (validated and in use)
        - Rejected (declined by authority)
        
    PROPERTIES:
        • link_id: Unique identifier for this link
        • source_memory: Source memory reference
        • target_memory: Target memory reference
        • kind: Link kind (same as AssociationKind)
        • status: Proposed, accepted, or rejected
        • evidence: Supporting evidence
        • confidence: Confidence level (0.0 to 1.0)
        • factuality: Factuality of the link claim
        • provenance: Provenance reference
        
    DOES NOT:
        - Create the link (authority does that)
        - Store full record payloads
    """
    
    # Identity
    link_id: str
    """Unique identifier for this link."""
    
    # References
    source_memory: str
    """Reference to the source memory record."""
    
    target_memory: str
    """Reference to the target memory record."""
    
    # Link details
    kind: str  # Same as AssociationKind values
    """Type of structural relationship."""
    
    status: str = "proposed"
    """Status: proposed, accepted, rejected"""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this link."""
    
    confidence: float = 0.5
    """Confidence in the link (0.0 to 1.0)."""
    
    factuality: str = "unknown"
    """Factuality of the link claim."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def proposed(
        cls,
        source_memory: str,
        target_memory: str,
        kind: str,
        confidence: float = 0.5,
    ) -> MemoryLink:
        """Create a new proposed link."""
        return cls(
            link_id=f"link_proposed_{id(cls)}",
            source_memory=source_memory,
            target_memory=target_memory,
            kind=kind,
            status="proposed",
            confidence=confidence,
        )
    
    @classmethod
    def accepted(
        cls,
        link: MemoryLink,
        acceptance_evidence: Tuple[str, ...],
        authority_confirmed_at_utc: str = "",
    ) -> MemoryLink:
        """Convert a proposed link to accepted."""
        return cls(
            link_id=link.link_id,
            source_memory=link.source_memory,
            target_memory=link.target_memory,
            kind=link.kind,
            status="accepted",
            evidence=(*link.evidence, *acceptance_evidence),
            confidence=max(link.confidence, 0.7),
            factuality=link.factuality,
        )
    
    def is_proposed(self) -> bool:
        """Check if this link is proposed (awaiting validation)."""
        return self.status == "proposed"
    
    def is_accepted(self) -> bool:
        """Check if this link has been accepted."""
        return self.status == "accepted"


# =============================================================================
# MEMORY CLUSTER CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryClusterCandidate:
    """
    Immutable candidate cluster of related memory records.
    
    A cluster represents a grouping based on:
        - Temporal proximity
        - Semantic similarity
        - Shared subjects or objectives
        - Recurring patterns
        
    PROPERTIES:
        • cluster_id: Unique identifier for this cluster candidate
        • member_references: References to clustered memories
        • clustering_rationale: Why these memories belong together
        • shared_concepts: Concepts shared across members
        • shared_subjects: Subjects shared across members
        • temporal_start_utc: Start of cluster's time range
        • temporal_end_utc: End of cluster's time range
        • internal_cohesion: How tightly clustered (0.0 to 1.0)
        • outliers: References that don't fit well
        • confidence: Confidence in the clustering (0.0 to 1.0)
        • provenance: Provenance reference
        
    IS NOT:
        - A stored memory structure (just a candidate)
        - An authoritative grouping
    """
    
    # Identity
    cluster_id: str
    """Unique identifier for this cluster candidate."""
    
    # Members
    member_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to memories in this cluster."""
    
    # Clustering details
    clustering_rationale: str = ""
    """Explanation of why these memories were clustered together."""
    
    shared_concepts: Tuple[str, ...] = field(default_factory=tuple)
    """Concepts shared across members."""
    
    shared_subjects: Tuple[str, ...] = field(default_factory=tuple)
    """Subjects shared across members."""
    
    # Temporal bounds
    temporal_start_utc: Optional[str] = None
    """Start of cluster's time range (ISO format)."""
    
    temporal_end_utc: Optional[str] = None
    """End of cluster's time range (ISO format)."""
    
    # Quality assessments
    internal_cohesion: float = 0.5
    """How tightly clustered (0.0 to 1.0)."""
    
    outliers: Tuple[str, ...] = field(default_factory=tuple)
    """References that don't fit well in this cluster."""
    
    confidence: float = 0.5
    """Confidence in the clustering (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        member_references: Tuple[str, ...],
        shared_concepts: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> MemoryClusterCandidate:
        """Create a new cluster candidate."""
        return cls(
            cluster_id=f"cluster_{id(cls)}",
            member_references=member_references,
            shared_concepts=shared_concepts,
            confidence=confidence,
        )
    
    def is_valid(self) -> bool:
        """Check if this cluster has at least two members."""
        return len(self.member_references) >= 2
    
    def has_outliers(self) -> bool:
        """Check if any outliers were identified."""
        return len(self.outliers) > 0