# Memory Proposal Models
# ======================

"""
Immutable proposal models for memory integration.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY CONSOLIDATION CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryConsolidationCandidate:
    """
    Immutable candidate for memory consolidation.
    
    A consolidation candidate represents an opportunity to transform multiple
    records into a more efficient representation without performing consolidation.
    
    PROPERTIES:
        • candidate_id: Unique identifier for this candidate
        • source_references: References to source records
        • consolidation_kind: Kind of consolidation (ConsolidationKind.*)
        • proposed_target_form: What the consolidated form would be
        • supporting_evidence: Evidence supporting consolidation
        • opposing_evidence: Evidence against consolidation
        • expected_benefit: Expected benefit score (0.0 to 1.0)
        • information_loss_risk: Risk of information loss (0.0 to 1.0)
        • confidence: Confidence in the candidate (0.0 to 1.0)
        • required_authority: What authority level is needed
        • provenance: Provenance reference
        
    IS NOT:
        - Authoritative consolidation (just a proposal)
        - A consolidated record yet
    """
    
    # Identity
    candidate_id: str
    """Unique identifier for this consolidation candidate."""
    
    # Source records
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to source records for consolidation."""
    
    # Consolidation details
    consolidation_kind: str  # ConsolidationKind.*
    """Kind of consolidation proposed."""
    
    proposed_target_form: str = ""
    """Description of the consolidated target form."""
    
    # Evidence
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this consolidation."""
    
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence against this consolidation."""
    
    # Quality assessments
    expected_benefit: float = 0.5
    """Expected benefit score (0.0 to 1.0)."""
    
    information_loss_risk: float = 0.0
    """Risk of information loss (0.0 to 1.0)."""
    
    confidence: float = 0.5
    """Confidence in the candidate (0.0 to 1.0)."""
    
    required_authority: str = "memory_authority"
    """Required authority level for consolidation."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        source_references: Tuple[str, ...],
        consolidation_kind: str,
        expected_benefit: float = 0.5,
        information_loss_risk: float = 0.1,
    ) -> MemoryConsolidationCandidate:
        """Create a new consolidation candidate."""
        return cls(
            candidate_id=f"consolidation_{id(cls)}",
            source_references=source_references,
            consolidation_kind=consolidation_kind,
            expected_benefit=expected_benefit,
            information_loss_risk=information_loss_risk,
        )
    
    def is_low_risk(self) -> bool:
        """Check if this consolidation has low information loss risk."""
        return self.information_loss_risk <= 0.2
    
    def is_high_confidence(self) -> bool:
        """Check if this candidate has high confidence."""
        return self.confidence >= 0.7


# =============================================================================
# MEMORY ABSTRACTION CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryAbstractionCandidate:
    """
    Immutable candidate for memory abstraction.
    
    An abstraction proposes a generalized semantic representation derived from
    multiple memory records without actually creating the abstraction.
    
    PROPERTIES:
        • candidate_id: Unique identifier for this candidate
        • source_references: References to source records
        • proposed_concept: The abstracted concept
        • generalized_relation: Generalized relationship
        • examples: Example instances supporting the abstraction
        • counterexamples: Counterexamples that may limit the abstraction
        • confidence: Confidence in the abstraction (0.0 to 1.0)
        • coverage: How much of the domain is covered (0.0 to 1.0)
        • information_loss_risk: Risk of information loss (0.0 to 1.0)
        • novelty: Novelty of the abstraction (0.0 to 1.0)
        • provenance: Provenance reference
        
    IS NOT:
        - An accepted semantic concept
        - A permanently stored abstraction
    """
    
    # Identity
    candidate_id: str
    """Unique identifier for this abstraction candidate."""
    
    # Source records
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to source records."""
    
    # Abstraction details
    proposed_concept: str = ""
    """The abstracted concept being proposed."""
    
    generalized_relation: str = ""
    """Generalized relationship between concepts."""
    
    # Evidence
    examples: Tuple[str, ...] = field(default_factory=tuple)
    """Example instances supporting the abstraction."""
    
    counterexamples: Tuple[str, ...] = field(default_factory=tuple)
    """Counterexamples that may limit the abstraction."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence in the abstraction (0.0 to 1.0)."""
    
    coverage: float = 0.0
    """Coverage of the domain (0.0 to 1.0)."""
    
    information_loss_risk: float = 0.0
    """Risk of information loss (0.0 to 1.0)."""
    
    novelty: float = 0.0
    """Novelty of the abstraction (0.0 to 1.0)."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        source_references: Tuple[str, ...],
        proposed_concept: str,
        examples: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> MemoryAbstractionCandidate:
        """Create a new abstraction candidate."""
        return cls(
            candidate_id=f"abstraction_{id(cls)}",
            source_references=source_references,
            proposed_concept=proposed_concept,
            examples=examples,
            confidence=confidence,
        )
    
    def is_well_supported(self) -> bool:
        """Check if this abstraction has sufficient supporting evidence."""
        return self.confidence >= 0.7 and len(self.examples) >= 2
    
    def has_known_limitations(self) -> bool:
        """Check if counterexamples have been identified."""
        return len(self.counterexamples) > 0


# =============================================================================
# MEMORY RETRIEVAL CUE PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryRetrievalCueProposal:
    """
    Immutable proposal for a retrieval cue.
    
    A retrieval cue proposal suggests indexing improvements without actually
    updating any indexes.
    
    PROPERTIES:
        • candidate_id: Unique identifier for this candidate
        • cue_type: Type of cue (concept, entity, temporal, etc.)
        • cue_representation: The cue itself
        • target_memories: Memory references the cue should help retrieve
        • rationale: Why this cue is proposed
        • expected_utility: Expected utility score (0.0 to 1.0)
        • specificity: How specific the cue is (0.0 to 1.0)
        • collision_risk: Risk of over-retrieval (0.0 to 1.0)
        • privacy: Privacy classification
        • provenance: Provenance reference
        
    IS NOT:
        - An actual index update
        - A commitment to change retrieval behavior
    """
    
    # Identity
    candidate_id: str
    """Unique identifier for this retrieval cue proposal."""
    
    # Cue details
    cue_type: str  # Concept, Entity, Temporal, etc.
    """Type of cue."""
    
    cue_representation: str = ""
    """The cue itself (text or structure)."""
    
    target_memories: Tuple[str, ...] = field(default_factory=tuple)
    """Memory references this cue should help retrieve."""
    
    # Rationale and assessment
    rationale: str = ""
    """Why this cue is proposed."""
    
    expected_utility: float = 0.5
    """Expected utility score (0.0 to 1.0)."""
    
    specificity: float = 0.5
    """How specific the cue is (0.0 to 1.0)."""
    
    collision_risk: float = 0.0
    """Risk of over-retrieval (0.0 to 1.0)."""
    
    privacy: str = "internal"
    """Privacy classification."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        cue_type: str,
        cue_representation: str,
        target_memories: Tuple[str, ...],
        expected_utility: float = 0.5,
    ) -> MemoryRetrievalCueProposal:
        """Create a new retrieval cue proposal."""
        return cls(
            candidate_id=f"cue_{id(cls)}",
            cue_type=cue_type,
            cue_representation=cue_representation,
            target_memories=target_memories,
            expected_utility=expected_utility,
        )
    
    def is_specific(self) -> bool:
        """Check if this cue has high specificity."""
        return self.specificity >= 0.7
    
    def has_low_collision_risk(self) -> bool:
        """Check if this cue has low collision risk."""
        return self.collision_risk <= 0.3


# =============================================================================
# MEMORY UPDATE PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryUpdateProposal:
    """
    Immutable proposal for a memory update operation.
    
    A memory update proposal requests changes to authoritative Memory without
    actually performing them.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • base_revision: Revision being updated from
        • intended_owner: Owner of the target record
        • proposed_change: Description of the change
        • supporting_evidence: Evidence supporting the change
        • opposing_evidence: Evidence against the change
        • factuality: Factuality of the updated content
        • authority_required: Authority level required
        • confidence: Confidence in this proposal (0.0 to 1.0)
        • reversibility: Can the change be reversed?
        • information_loss_risk: Risk of information loss (0.0 to 1.0)
        • privacy: Privacy classification
        • provenance: Provenance reference
        
    IS NOT:
        - An executed update
        - A commitment to apply changes
    """
    
    # Identity
    proposal_id: str
    """Unique identifier for this update proposal."""
    
    # Base revision
    base_revision: int = 1
    """Revision being updated from."""
    
    intended_owner: str = ""
    """Owner of the target record."""
    
    # Change details
    operation: str  # ProposalOperation.*
    """Type of operation requested."""
    
    proposed_change: str = ""
    """Description of the change."""
    
    # Evidence
    supporting_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting this proposal."""
    
    opposing_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence against this proposal."""
    
    # Quality assessments
    factuality: str = "unknown"
    """Factuality of the updated content."""
    
    authority_required: str = "memory_authority"
    """Authority level required."""
    
    confidence: float = 0.5
    """Confidence in this proposal (0.0 to 1.0)."""
    
    reversibility: str = "unknown"
    """Can the change be reversed?"""
    
    information_loss_risk: float = 0.0
    """Risk of information loss (0.0 to 1.0)."""
    
    privacy: str = "internal"
    """Privacy classification."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        operation: str,
        proposed_change: str,
        base_revision: int = 1,
        confidence: float = 0.5,
    ) -> MemoryUpdateProposal:
        """Create a new memory update proposal."""
        return cls(
            proposal_id=f"update_{id(cls)}",
            base_revision=base_revision,
            operation=operation,
            proposed_change=proposed_change,
            confidence=confidence,
        )
    
    def has_sufficient_evidence(self) -> bool:
        """Check if this proposal has sufficient supporting evidence."""
        return len(self.supporting_evidence) > 0 and self.confidence >= 0.5
    
    def is_low_risk(self) -> bool:
        """Check if this proposal has low information loss risk."""
        return self.information_loss_risk <= 0.2


# =============================================================================
# MEMORY CORRECTION PROPOSAL
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryCorrectionProposal:
    """
    Immutable proposal for a memory correction.
    
    A correction proposal requests specific corrections to memory records without
    actually performing them.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • original_content: Original content being challenged
        • challenged_content: Content that needs correction
        • corrected_candidate: Proposed correct version
        • evidence: Supporting evidence
        • source_authority: Source authority of the correction
        • factuality: Factuality of the corrected content
        • confidence: Confidence in this proposal (0.0 to 1.0)
        • unresolved_uncertainty: What remains uncertain
        • base_revision: Revision being corrected from
        • provenance: Provenance reference
        
    IS NOT:
        - An executed correction
        - Overwriting the original record
    """
    
    # Identity
    proposal_id: str
    """Unique identifier for this correction proposal."""
    
    # Content details
    original_content: str = ""
    """Original content being challenged."""
    
    challenged_content: str = ""
    """Content that needs correction."""
    
    corrected_candidate: str = ""
    """Proposed correct version."""
    
    # Evidence
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Supporting evidence for the correction."""
    
    source_authority: str = "unknown"
    """Source authority of the correction."""
    
    factuality: str = "unknown"
    """Factuality of the corrected content."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence in this proposal (0.0 to 1.0)."""
    
    unresolved_uncertainty: str = ""
    """What remains uncertain after correction."""
    
    base_revision: int = 1
    """Revision being corrected from."""
    
    # Provenance
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        original_content: str,
        challenged_content: str,
        corrected_candidate: str,
        evidence: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> MemoryCorrectionProposal:
        """Create a new memory correction proposal."""
        return cls(
            proposal_id=f"correction_{id(cls)}",
            original_content=original_content,
            challenged_content=challenged_content,
            corrected_candidate=corrected_candidate,
            evidence=evidence,
            confidence=confidence,
        )
    
    def has_high_confidence(self) -> bool:
        """Check if this correction has high confidence."""
        return self.confidence >= 0.7
    
    def is_well_supported(self) -> bool:
        """Check if this correction has substantial evidence."""
        return len(self.evidence) >= 2 and self.confidence >= 0.5


# =============================================================================
# MEMORY RETENTION AND DE-EMPHASIS PROPOSALS
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryRetentionProposal:
    """
    Immutable proposal for retention classification.
    
    A retention proposal suggests retention-related decisions without actually
    applying them.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • memory_references: References to affected memories
        • retention_classification: Proposed classification
        • reasons: Why this classification is proposed
        • confidence: Confidence in this proposal (0.0 to 1.0)
        • provenance: Provenance reference
        
    IS NOT:
        - An executed retention change
        - A commitment to modify retention policy
    """
    
    # Identity
    proposal_id: str
    """Unique identifier for this retention proposal."""
    
    memory_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to affected memories."""
    
    retention_classification: str = "standard"
    """Proposed retention classification."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Why this classification is proposed."""
    
    confidence: float = 0.5
    """Confidence in this proposal (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        memory_references: Tuple[str, ...],
        retention_classification: str,
        reasons: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> MemoryRetentionProposal:
        """Create a new retention proposal."""
        return cls(
            proposal_id=f"retention_{id(cls)}",
            memory_references=memory_references,
            retention_classification=retention_classification,
            reasons=reasons,
            confidence=confidence,
        )


@dataclass(frozen=True, slots=True)
class MemoryDeemphasisProposal:
    """
    Immutable proposal for de-emphasizing memories.
    
    A de-emphasis proposal suggests reducing retrieval priority without
    actually modifying indexes or storage.
    
    PROPERTIES:
        • proposal_id: Unique identifier for this proposal
        • memory_references: References to affected memories
        • reasons: Why de-emphasis is proposed
        • confidence: Confidence in this proposal (0.0 to 1.0)
        • provenance: Provenance reference
        
    IS NOT:
        - An actual index modification
        - A deletion or archival action
    """
    
    # Identity
    proposal_id: str
    """Unique identifier for this de-emphasis proposal."""
    
    memory_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to affected memories."""
    
    reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Why de-emphasis is proposed."""
    
    confidence: float = 0.5
    """Confidence in this proposal (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        memory_references: Tuple[str, ...],
        reasons: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> MemoryDeemphasisProposal:
        """Create a new de-emphasis proposal."""
        return cls(
            proposal_id=f"deemphasize_{id(cls)}",
            memory_references=memory_references,
            reasons=reasons,
            confidence=confidence,
        )