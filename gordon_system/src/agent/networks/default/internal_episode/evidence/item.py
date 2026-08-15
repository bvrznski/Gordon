# Internal Episode Evidence Item
# ==============================

"""
Evidence item model for internal episode coordination.

Evidence represents information produced or accepted during episode coordination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


InternalEpisodeEvidenceId = str
"""Unique identifier for an evidence item."""


@dataclass(frozen=True, slots=True)
class InternalEpisodeEvidence:
    """
    Immutable evidence item produced during episode coordination.
    
    Evidence represents information used in internal cognition. It is NOT
    automatic truth - it must be evaluated for confidence and relevance.
    
    EVIDENCE CATEGORIES:
        • memory: Memory projection or retrieval result
        • identity: Identity projection or self-model result
        • narrative: Narrative projection or story structure result
        • prediction: Predictive model or scenario result
        • simulation: Simulation or counterfactual exploration result
        • reflection: Reflection or self-analysis result
        • concern: Unresolved concern or pending issue
        • contradiction: Detected contradiction or inconsistency
        • insight: New insight or understanding produced
        • workspace_feedback: Feedback from conscious workspace processing
        • evaluation: Evaluation or assessment result
        • policy: Policy constraint or rule applied
        • resource: Resource state or capacity information
        
    PROPERTIES:
        • evidence_id: Unique identifier for this item
        • category: What type of information
        • source: Where it came from (capability, projection, etc.)
        • source_reference: Reference to the source
        • confidence: Quality assessment
        • relevance: How relevant to the episode purpose
        
    BOUNDEDNESS:
        • timestamp_utc: When produced (for freshness evaluation)
        • content_summary: Short summary instead of full payload
        
    NOT RESPONSIBLE FOR:
        • Evaluating truth or validity (that's done separately)
        • Storing unlimited payloads
        • Creating live runtime references
    """
    
    # Identity
    evidence_id: InternalEpisodeEvidenceId
    """Unique identifier for this evidence item."""
    
    # Category and source
    category: str  # InternalEvidenceCategory.*
    """What type of information this is."""
    
    source: str
    """Where the information came from (capability name or projection type)."""
    
    source_reference: Optional[str] = None
    """Reference to the specific source item (e.g., memory ID, result ID)."""
    
    # Quality assessment
    confidence: float = 0.5
    """Quality of this evidence (0.0 to 1.0)."""
    
    relevance: float = 1.0
    """How relevant this is to the episode purpose (0.0 to 1.0)."""
    
    # Timestamp
    timestamp_utc: str = ""
    """When this evidence was produced."""
    
    # Content reference (not full payload)
    content_summary: Optional[str] = None
    """Brief summary of content (for diagnostics, not full data)."""
    
    # Relationship to other evidence
    contradicts_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evidence items this contradicts."""
    
    supports_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evidence items this supports."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference (where this evidence type is documented)."""
    
    @classmethod
    def create(
        cls,
        evidence_id: str,
        category: str,
        source: str,
        confidence: float = 0.5,
        relevance: float = 1.0,
    ) -> InternalEpisodeEvidence:
        """
        Create a new evidence item.
        
        Args:
            evidence_id: Unique identifier for this item
            category: What type of information
            source: Where it came from
            confidence: Quality assessment (0.0 to 1.0)
            relevance: Relevance to episode purpose (0.0 to 1.0)
            
        Returns:
            New InternalEpisodeEvidence instance
        """
        return cls(
            evidence_id=evidence_id,
            category=category,
            source=source,
            confidence=confidence,
            relevance=relevance,
        )