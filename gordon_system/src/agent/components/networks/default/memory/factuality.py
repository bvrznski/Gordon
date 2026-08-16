# Factuality and Reconstruction Models
# =====================================

"""
Factuality classification and reconstruction handling for memory records.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Clear distinction between original and reconstructed content
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# RECONSTRUCTION CLASSIFICATION
# =============================================================================

class ReconstructionClassification:
    """
    Canonical classifications for how memory content was derived.
    
    These distinguish between direct records and reconstructed representations.
    """
    
    DIRECT_RECORD = "direct_record"
    """Original record as stored."""
    
    SUMMARIZED_RECORD = "summarized_record"
    """Condensed version of original record."""
    
    RECONSTRUCTED_RECORD = "reconstructed_record"
    """Rebuilt from partial evidence (not original)."""
    
    INFERRED_RECONSTRUCTION = "inferred_reconstruction"
    """Reconstruction based on inference and pattern matching."""
    
    HYPOTHETICAL_RECONSTRUCTION = "hypothetical_reconstruction"
    """Reconstruction based on hypothetical scenarios."""
    
    @classmethod
    def all_classifications(cls) -> Tuple[str, ...]:
        """Return all valid reconstruction classifications."""
        return (
            cls.DIRECT_RECORD,
            cls.SUMMARIZED_RECORD,
            cls.RECONSTRUCTED_RECORD,
            cls.INFERRED_RECONSTRUCTION,
            cls.HYPOTHETICAL_RECONSTRUCTION,
        )
    
    @classmethod
    def is_original(cls, classification: str) -> bool:
        """Check if reconstruction classification represents original content."""
        return classification in {
            cls.DIRECT_RECORD,
            cls.SUMMARIZED_RECORD,
        }
    
    @classmethod
    def is_reconstructed(cls, classification: str) -> bool:
        """Check if reconstruction classification represents reconstructed content."""
        return classification in {
            cls.RECONSTRUCTED_RECORD,
            cls.INFERRED_RECONSTRUCTION,
            cls.HYPOTHETICAL_RECONSTRUCTION,
        }


# =============================================================================
# MEMORY CONFLICT
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryConflict:
    """
    Immutable record of a conflict between memory records.
    
    A conflict represents incompatible claims that cannot both be true.
    
    PROPERTIES:
        • conflict_id: Unique identifier for this conflict
        • involved_records: References to conflicting records
        • source_owners: Owners of conflicting sources
        • revisions: Record revisions at time of conflict
        • factuality: Factuality classifications of conflicting claims
        • supporting_evidence: Evidence for each claim
        • severity: Conflict severity (low/medium/high/critical)
        • confidence: Confidence in the conflict assessment
        • blocking_status: Is this blocking further processing?
        • provenance: Provenance reference
        
    DOES NOT:
        - Choose one memory over another
        - Silently resolve conflicts
        - Mutate source records
    """
    
    # Identity
    conflict_id: str
    """Unique identifier for this conflict."""
    
    # Involved records
    involved_records: Tuple[str, ...] = field(default_factory=tuple)
    """References to conflicting memory records."""
    
    source_owners: Tuple[str, ...] = field(default_factory=tuple)
    """Owners of the conflicting sources."""
    
    revisions: Tuple[int, ...] = field(default_factory=tuple)
    """Record revisions at time of conflict detection."""
    
    # Conflict details
    kind: str  # ConflictKind.*
    """Type of conflict."""
    
    factuality: Tuple[str, ...] = field(default_factory=tuple)
    """Factuality classifications of conflicting claims."""
    
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting each claim in the conflict."""
    
    # Quality assessments
    severity: str = "medium"
    """Severity level: low, medium, high, critical"""
    
    confidence: float = 0.5
    """Confidence in the conflict assessment (0.0 to 1.0)."""
    
    blocking_status: str = "non_blocking"
    """Blocking status: blocking or non_blocking"""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        involved_records: Tuple[str, ...],
        kind: str,
        severity: str = "medium",
        confidence: float = 0.5,
    ) -> MemoryConflict:
        """Create a new memory conflict."""
        return cls(
            conflict_id=f"conflict_{id(cls)}",
            involved_records=involved_records,
            kind=kind,
            severity=severity,
            confidence=confidence,
        )
    
    def is_blocking(self) -> bool:
        """Check if this conflict blocks further processing."""
        return self.blocking_status == "blocking"
    
    def has_high_severity(self) -> bool:
        """Check if this conflict has high or critical severity."""
        return self.severity in {"high", "critical"}


# =============================================================================
# MEMORY GAP
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryGap:
    """
    Immutable record of a gap in memory coverage.
    
    A gap represents missing information that would improve understanding.
    
    PROPERTIES:
        • gap_id: Unique identifier for this gap
        • kind: Gap kind (GapKind.*)
        • expected_content: What was expected but missing
        • related_records: Records that reference the gap
        • temporal_bounds: Expected time range if applicable
        • confidence: Confidence in the gap assessment
        • completeness_impact: Impact on record completeness
        • provenance: Provenance reference
        
    DOES NOT:
        - Fabricate content to fill the gap
        - Assume the missing information
        - Modify source records
    """
    
    # Identity
    gap_id: str
    """Unique identifier for this gap."""
    
    # Gap details
    kind: str  # GapKind.*
    """Type of gap."""
    
    expected_content: str = ""
    """Description of what was expected but missing."""
    
    related_records: Tuple[str, ...] = field(default_factory=tuple)
    """Records that reference or are affected by the gap."""
    
    # Temporal bounds (if applicable)
    temporal_bounds_start_utc: Optional[str] = None
    """Expected start time (ISO format)."""
    
    temporal_bounds_end_utc: Optional[str] = None
    """Expected end time (ISO format)."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence in the gap assessment (0.0 to 1.0)."""
    
    completeness_impact: str = "unknown"
    """Impact on completeness: low, medium, high, critical"""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        kind: str,
        expected_content: str,
        related_records: Tuple[str, ...] = (),
        confidence: float = 0.5,
    ) -> MemoryGap:
        """Create a new memory gap."""
        return cls(
            gap_id=f"gap_{id(cls)}",
            kind=kind,
            expected_content=expected_content,
            related_records=related_records,
            confidence=confidence,
        )
    
    def indicates_severe_impact(self) -> bool:
        """Check if this gap has severe completeness impact."""
        return self.completeness_impact in {"high", "critical"}


# =============================================================================
# MEMORY DUPLICATE CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryDuplicateCandidate:
    """
    Immutable candidate record for potential duplicate detection.
    
    A duplicate candidate represents records that may be the same or very similar.
    
    PROPERTIES:
        • candidate_id: Unique identifier for this duplicate pair/group
        • record_refs_a: First set of record references
        • record_refs_b: Second set of record references
        • evidence: Evidence suggesting duplication
        • overlap_score: Similarity score (0.0 to 1.0)
        • is_definitive_duplicate: Is this definitely a duplicate?
        • potential_merge_target: Which record should be kept if merging
        • provenance: Provenance reference
        
    IS NOT:
        - Permission to delete or merge (authority decides)
        - A merged record (just a candidate for merging)
    """
    
    # Identity
    candidate_id: str
    """Unique identifier for this duplicate candidate."""
    
    # Record references
    record_refs_a: Tuple[str, ...] = field(default_factory=tuple)
    """First set of record references."""
    
    record_refs_b: Tuple[str, ...] = field(default_factory=tuple)
    """Second set of record references."""
    
    # Evidence for duplication
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting duplicate classification."""
    
    overlap_score: float = 0.5
    """Similarity score (0.0 to 1.0)."""
    
    # Classification
    is_definitive_duplicate: bool = False
    """Is this definitely a duplicate?"""
    
    potential_merge_target: Optional[str] = None
    """Which record should be kept if merging."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        record_refs_a: Tuple[str, ...],
        record_refs_b: Tuple[str, ...],
        overlap_score: float = 0.5,
    ) -> MemoryDuplicateCandidate:
        """Create a new duplicate candidate."""
        return cls(
            candidate_id=f"dup_{id(cls)}",
            record_refs_a=record_refs_a,
            record_refs_b=record_refs_b,
            overlap_score=overlap_score,
        )
    
    def is_high_confidence_duplicate(self) -> bool:
        """Check if this is a high-confidence duplicate."""
        return self.is_definitive_duplicate or self.overlap_score >= 0.8


# =============================================================================
# MEMORY INCONSISTENCY
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryInconsistency:
    """
    Immutable record of an inconsistency in memory records.
    
    An inconsistency may exist within one record or across a set without
    constituting a direct conflict.
    
    Examples:
        - Impossible temporal ordering
        - Mismatched participants
        - Missing source lineage
        - Contradictory factuality labels
        - Revision chain break
        - Claimed outcome without event
        
    PROPERTIES:
        • inconsistency_id: Unique identifier for this inconsistency
        • kind: Inconsistency kind
        • records_affected: References to affected records
        • specific_issue: Description of the issue
        • confidence: Confidence in the assessment
        • completeness_impact: Impact on record quality
        • provenance: Provenance reference
        
    DIFFERS FROM CONFLICT:
        - Conflict: Both claims cannot be true (mutually exclusive)
        - Inconsistency: Something seems wrong but not necessarily contradictory
    """
    
    # Identity
    inconsistency_id: str
    """Unique identifier for this inconsistency."""
    
    # Details
    kind: str  # Same as GapKind values for inspiration
    """Type of inconsistency."""
    
    records_affected: Tuple[str, ...] = field(default_factory=tuple)
    """References to affected records."""
    
    specific_issue: str = ""
    """Description of the specific issue."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence in the inconsistency assessment (0.0 to 1.0)."""
    
    completeness_impact: str = "unknown"
    """Impact on record quality."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        records_affected: Tuple[str, ...],
        specific_issue: str,
        confidence: float = 0.5,
    ) -> MemoryInconsistency:
        """Create a new memory inconsistency."""
        return cls(
            inconsistency_id=f"inconsistency_{id(cls)}",
            kind="temporal",  # Default example
            records_affected=records_affected,
            specific_issue=specific_issue,
            confidence=confidence,
        )
    
    def affects_high_quality(self) -> bool:
        """Check if this inconsistency significantly affects record quality."""
        return self.confidence >= 0.7 and len(self.records_affected) > 1