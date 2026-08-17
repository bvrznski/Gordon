# Knowledge-Perception Grounding - Correspondence Contract
# ==========================================================

"""
Correspondence: Semantic associations between Percepts and Knowledge Concepts.

Correspondence proposes semantic links without determining truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# CORRESPONDENCE KINDS - What kind of correspondence is this?
# =============================================================================


class CorrespondenceKind(Enum):
    """
    Kinds of semantic correspondences.
    
    DIRECT: Direct match between percept and concept
    PARTIAL: Partial match, some features align
    MULTIPLE: Multiple plausible matches exist
    HIERARCHICAL: Match through hierarchy (is-a relationship)
    ANALOGICAL: Analogy-based correspondence
    UNKNOWN: Undetermined correspondence type
    """
    
    DIRECT = "direct"
    PARTIAL = "partial"
    MULTIPLE = "multiple"
    HIERARCHICAL = "hierarchical"
    ANALOGICAL = "analogical"
    UNKNOWN = "unknown"


# =============================================================================
# SEMANTIC CORRESPONDENCE - Percept to concept mapping
# =============================================================================


@dataclass(frozen=True)
class SemanticCorrespondence:
    """
    Proposed semantic correspondence between a percept and concepts.
    
    Correspondence answers: "What might this percept mean?"
    It does not answer: "Is this meaning true?"
    
    Fields:
        correspondence_identity: Unique identifier
        
        percept:                 Reference to the percept being mapped
        candidate_concepts:      References to potentially corresponding concepts
        
        correspondence_kind:     What kind of correspondence is this?
        
        similarity:              Similarity score (0.0-1.0)
        
        supporting_features:     Features supporting this match
        contradicting_features:  Features contradicting this match
        
        confidence:              Confidence in this correspondence (0.0-1.0)
        uncertainty:             Uncertainty about this correspondence
        
        provenance:              Origin tracking
    """
    
    # Identity (required)
    correspondence_identity: str
    
    # Percept reference (required)
    percept: str                   # Reference to the percept
    
    # Concept candidates (required)
    candidate_concepts: Tuple[str, ...]  # References to concept IDs
    
    # Correspondence description (required)
    correspondence_kind: str       # e.g., "direct", "partial"
    
    # Quality metrics
    similarity: float = 0.5        # Similarity score (0.0-1.0)
    
    supporting_features: Tuple[str, ...] = field(default_factory=tuple)   # Supporting evidence
    contradicting_features: Tuple[str, ...] = field(default_factory=tuple)  # Contradicting evidence
    
    confidence: float = 1.0        # Correspondence confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about correspondence
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate correspondence."""
        if not self.correspondence_identity:
            raise ValueError("correspondence_identity is required")
        if not self.percept:
            raise ValueError("percept reference is required")
    
    @property
    def is_exact_match(self) -> bool:
        """Check if this is an exact match (single concept, high confidence)."""
        return (
            len(self.candidate_concepts) == 1 and
            self.confidence >= 0.9 and
            self.correspondence_kind in ("direct", "hierarchical")
        )
    
    @property
    def is_ambiguous(self) -> bool:
        """Check if there are multiple plausible matches."""
        return (
            len(self.candidate_concepts) > 1 or
            self.confidence < 0.7 or
            self.correspondence_kind in ("multiple", "unknown")
        )
    
    @classmethod
    def create(
        cls,
        percept_id: str,
        candidate_concept_ids: List[str],
        correspondence_kind: CorrespondenceKind = CorrespondenceKind.UNKNOWN,
        similarity: float = 0.5,
        supporting_features: Optional[List[str]] = None,
        contradicting_features: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "SemanticCorrespondence":
        """Create a new semantic correspondence."""
        return cls(
            correspondence_identity=f"correspondence:{uuid.uuid4().hex[:24]}",
            percept=percept_id,
            candidate_concepts=tuple(candidate_concept_ids),
            correspondence_kind=correspondence_kind.value if isinstance(correspondence_kind, Enum) else correspondence_kind,
            similarity=max(0.0, min(1.0, float(similarity))),
            supporting_features=tuple(supporting_features or []),
            contradicting_features=tuple(contradicting_features or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert correspondence to dictionary."""
        return {
            "correspondence_identity": self.correspondence_identity,
            "percept": self.percept,
            "candidate_concepts": list(self.candidate_concepts),
            "correspondence_kind": self.correspondence_kind,
            "similarity": self.similarity,
            "supporting_features": list(self.supporting_features),
            "contradicting_features": list(self.contradicting_features),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# VECTOR CORRESPONDENCE - Vector-based correspondence matching
# =============================================================================


@dataclass(frozen=True)
class VectorCorrespondence:
    """
    Correspondence based on vector similarity.
    
    Fields:
        correspondence_identity: Unique identifier
        
        percept_embedding:       Embedding of the percept
        candidate_embeddings:    Embeddings of candidate concepts
        
        similarity_metric:       Metric used (e.g., "cosine", "euclidean")
        neighborhood:            K-nearest neighbors in embedding space
        
        similarity_scores:       Score for each candidate
        confidence:              Confidence in vector matching (0.0-1.0)
        uncertainty:             Uncertainty about embeddings
        
        provenance:              Origin tracking
    """
    
    # Identity (required)
    correspondence_identity: str
    
    # Percept embedding reference
    percept_embedding: str         # Reference to percept's embedding
    
    # Candidate embeddings
    candidate_embeddings: Tuple[str, ...]  # References to concept embeddings
    
    # Matching details
    similarity_metric: str         # e.g., "cosine", "euclidean"
    
    neighborhood: int = 5          # K-nearest neighbors considered
    similarity_scores: Dict[str, float] = field(default_factory=dict)  # candidate_id -> score
    
    confidence: float = 1.0        # Vector matching confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about embeddings
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate vector correspondence."""
        if not self.correspondence_identity:
            raise ValueError("correspondence_identity is required")
    
    @property
    def top_candidate(self) -> Optional[Tuple[str, float]]:
        """Get the highest scoring candidate and its score."""
        if not self.similarity_scores:
            return None
        max_score = max(self.similarity_scores.values())
        for cid, score in self.similarity_scores.items():
            if score == max_score:
                return (cid, max_score)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "correspondence_identity": self.correspondence_identity,
            "percept_embedding": self.percept_embedding,
            "candidate_embeddings": list(self.candidate_embeddings),
            "similarity_metric": self.similarity_metric,
            "neighborhood": self.neighborhood,
            "similarity_scores": dict(self.similarity_scores),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# STRUCTURAL CORRESPONDENCE - Structural pattern matching
# =============================================================================


@dataclass(frozen=True)
class StructuralCorrespondence:
    """
    Correspondence based on structural pattern analysis.
    
    Fields:
        correspondence_identity: Unique identifier
        
        percept_structure:       Structural description of the percept
        candidate_concepts:      Candidate concepts with their structures
        
        matched_components:      Components that match
        unmatched_components:    Components that don't match
        
        structural_score:        Overall structural similarity (0.0-1.0)
        
        confidence:              Confidence in structural match (0.0-1.0)
        uncertainty:             Uncertainty about structure
        
        provenance:              Origin tracking
    """
    
    # Identity (required)
    correspondence_identity: str
    
    # Structure references
    percept_structure: str         # Reference to percept's structure
    candidate_concepts: Tuple[str, ...]  # Candidate concept IDs
    
    # Structural analysis
    matched_components: Tuple[str, ...] = field(default_factory=tuple)   # Matched parts
    unmatched_components: Tuple[str, ...] = field(default_factory=tuple)  # Unmatched parts
    
    structural_score: float = 0.5  # Overall similarity (0.0-1.0)
    
    confidence: float = 1.0        # Structural match confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about structure
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate structural correspondence."""
        if not self.correspondence_identity:
            raise ValueError("correspondence_identity is required")
    
    @classmethod
    def create(
        cls,
        percept_structure: str,
        candidate_concept_ids: List[str],
        matched_components: Optional[List[str]] = None,
        unmatched_components: Optional[List[str]] = None,
        structural_score: float = 0.5,
        confidence: float = 1.0,
    ) -> "StructuralCorrespondence":
        """Create a new structural correspondence."""
        return cls(
            correspondence_identity=f"structural_correspondence:{uuid.uuid4().hex[:24]}",
            percept_structure=percept_structure,
            candidate_concepts=tuple(candidate_concept_ids),
            matched_components=tuple(matched_components or []),
            unmatched_components=tuple(unmatched_components or []),
            structural_score=max(0.0, min(1.0, float(structural_score))),
            confidence=max(0.0, min(1.0, float(confidence))),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "correspondence_identity": self.correspondence_identity,
            "percept_structure": self.percept_structure,
            "candidate_concepts": list(self.candidate_concepts),
            "matched_components": list(self.matched_components),
            "unmatched_components": list(self.unmatched_components),
            "structural_score": self.structural_score,
            "confidence": self.confidence,
        }


# =============================================================================
# HYBRID CORRESPONDENCE - Combined correspondence strategies
# =============================================================================


@dataclass(frozen=True)
class HybridCorrespondence:
    """
    Combined correspondence using multiple strategies.
    
    Fields:
        correspondence_identity: Unique identifier
        
        vector_results:          Vector-based correspondence results
        structural_results:      Structural correspondence results
        symbolic_results:        Symbolic matching results
        
        combined_candidates:     Merged candidate list with scores
        fusion_method:           How were the results combined? (e.g., "weighted_average")
        
        confidence:              Overall confidence in the hybrid result (0.0-1.0)
        uncertainty:             Uncertainty about fusion
        
        provenance:              Origin tracking
    """
    
    # Identity (required)
    correspondence_identity: str
    
    # Results from each strategy
    vector_results: Tuple[VectorCorrespondence, ...] = field(default_factory=tuple)
    structural_results: Tuple[StructuralCorrespondence, ...] = field(default_factory=tuple)
    symbolic_results: Tuple[str, ...] = field(default_factory=tuple)  # Symbolic match IDs
    
    # Combined results
    combined_candidates: Dict[str, float] = field(default_factory=dict)  # concept_id -> score
    fusion_method: str = "weighted_average"  # How were scores combined?
    
    confidence: float = 1.0        # Hybrid result confidence (0.0-1.0)
    uncertainty: float = 0.0       # Uncertainty about fusion
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    def __post_init__(self):
        """Validate hybrid correspondence."""
        if not self.correspondence_identity:
            raise ValueError("correspondence_identity is required")
    
    @property
    def top_candidate(self) -> Optional[Tuple[str, float]]:
        """Get the highest scoring candidate from combined results."""
        if not self.combined_candidates:
            return None
        max_score = max(self.combined_candidates.values())
        for cid, score in self.combined_candidates.items():
            if score == max_score:
                return (cid, max_score)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "correspondence_identity": self.correspondence_identity,
            "vector_results_count": len(self.vector_results),
            "structural_results_count": len(self.structural_results),
            "symbolic_results_count": len(self.symbolic_results),
            "combined_candidates": dict(self.combined_candidates),
            "fusion_method": self.fusion_method,
            "confidence": self.confidence,
        }


__all__ = [
    "CorrespondenceKind",
    "SemanticCorrespondence",
    "VectorCorrespondence",
    "StructuralCorrespondence",
    "HybridCorrespondence",
]