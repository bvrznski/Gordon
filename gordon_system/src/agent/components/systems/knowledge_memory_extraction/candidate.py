# Knowledge Semantic Candidate
# =============================

"""
Semantic Candidate: Proposed semantic structure from memory extraction.

This module defines the SemanticCandidate model that represents potential
semantic structures (concepts, propositions, relations, etc.) extracted
from retained memory evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


@dataclass(frozen=True)
class KnowledgeSemanticCandidate:
    """
    A proposed semantic structure from extraction operations.
    
    A Semantic Candidate is not yet a Knowledge Artifact - it requires
    validation and acceptance by the Knowledge system before becoming
    an active semantic commitment.
    
    Fields:
        candidate_identity:       Unique ID for this candidate
        
        # Semantic kind
        candidate_kind:           What type of semantic structure? (concept, proposition, etc.)
        
        # Proposed content
        proposed_semantic_content: The proposed semantic structure
        candidate_scope:          Scope/conditions where this applies
        
        # Evidence support
        supporting_memory_artifacts: Artifacts supporting this candidate
        contradicting_memory_artifacts: Artifacts contradicting this candidate
        unresolved_memory_artifacts: Artifacts requiring further analysis
        
        # Extraction metadata
        extraction_references:    References to extraction operations
        source_roles:             Source roles of evidence artifacts
        ontology_context:         Ontology context for interpretation
        
        # Quality metrics
        confidence:               Confidence in this candidate (0.0-1.0)
        uncertainty:              Uncertainty about correctness
        alternatives:             Alternative interpretations considered
        
        # Limitations and revision info
        limitations:              Known issues with this candidate
        revision:                 Revision number of this candidate
        provenance:               How was this candidate generated?
    """
    
    # Identity (required)
    candidate_identity: str                  # Unique ID for this candidate
    
    # Semantic kind (required)
    candidate_kind: str                      # "concept", "proposition", "relation", etc.
    
    # Proposed semantic content
    proposed_semantic_content: Dict[str, Any]  # The actual structure being proposed
    
    # Scope (optional)
    candidate_scope: Optional[Dict[str, Any]] = None
    
    # Evidence support (required for grounding)
    supporting_memory_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Artifact IDs
    contradicting_memory_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    unresolved_memory_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    # Extraction metadata
    extraction_references: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    source_roles: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # SourceRoleMetadata dicts
    ontology_context: str = ""               # Ontology context for interpretation
    
    # Quality metrics (required)
    confidence: float = 0.5                  # Confidence in candidate (0.0-1.0)
    uncertainty: float = 0.5                 # Uncertainty about correctness
    
    # Alternatives and limitations
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Alternative interpretations
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known issues
    
    # Revision tracking
    revision: int = 1                        # Candidate revision number
    
    # Provenance (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate candidate."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {self.uncertainty}")
    
    @classmethod
    def create_concept_candidate(
        cls,
        concept_name: str,
        definition: Dict[str, Any],
        supporting_artifacts: List[str],
        confidence: float = 0.7,
    ) -> "KnowledgeSemanticCandidate":
        """Create a concept candidate."""
        return cls(
            candidate_identity=f"candidate:concept:{uuid.uuid4().hex[:16]}",
            candidate_kind="concept",
            proposed_semantic_content={
                "name": concept_name,
                "definition": definition,
                "type": "concept",
            },
            supporting_memory_artifacts=tuple(supporting_artifacts),
            confidence=confidence,
            uncertainty=1.0 - confidence,
            provenance={
                "origin": "semantic_extraction",
                "method": "pattern_recognition",
                "created_at_utc": uuid.uuid4().time if hasattr(uuid.uuid4(), 'time') else 0,
            },
        )
    
    @classmethod
    def create_proposition_candidate(
        cls,
        proposition_text: str,
        supporting_artifacts: List[str],
        confidence: float = 0.7,
    ) -> "KnowledgeSemanticCandidate":
        """Create a proposition candidate."""
        return cls(
            candidate_identity=f"candidate:proposition:{uuid.uuid4().hex[:16]}",
            candidate_kind="proposition",
            proposed_semantic_content={
                "text": proposition_text,
                "type": "assertion",
            },
            supporting_memory_artifacts=tuple(supporting_artifacts),
            confidence=confidence,
            uncertainty=1.0 - confidence,
            provenance={
                "origin": "semantic_extraction",
                "method": "pattern_recognition",
                "created_at_utc": uuid.uuid4().time if hasattr(uuid.uuid4(), 'time') else 0,
            },
        )
    
    @property
    def is_valid_candidate(self) -> bool:
        """Check if this candidate has minimal required data."""
        return (
            len(self.candidate_identity) > 0 and
            len(self.candidate_kind) > 0 and
            len(self.supporting_memory_artifacts) > 0 and
            0.0 <= self.confidence <= 1.0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary for serialization."""
        return {
            "candidate_identity": self.candidate_identity,
            "candidate_kind": self.candidate_kind,
            "proposed_semantic_content": dict(self.proposed_semantic_content),
            "candidate_scope": dict(self.candidate_scope) if self.candidate_scope else None,
            "supporting_memory_artifacts": list(self.supporting_memory_artifacts),
            "contradicting_memory_artifacts": list(self.contradicting_memory_artifacts),
            "unresolved_memory_artifacts": list(self.unresolved_memory_artifacts),
            "extraction_references": [ref if isinstance(ref, dict) else ref.to_dict() if hasattr(ref, 'to_dict') else {} for ref in self.extraction_references],
            "source_roles": [sr if isinstance(sr, dict) else sr.to_dict() if hasattr(sr, 'to_dict') else {} for sr in self.source_roles],
            "ontology_context": self.ontology_context,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "alternatives": list(self.alternatives),
            "limitations": list(self.limitations),
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeSemanticCandidate":
        """Create candidate from dictionary."""
        return cls(
            candidate_identity=data.get("candidate_identity", str(uuid.uuid4())),
            candidate_kind=data.get("candidate_kind", ""),
            proposed_semantic_content=dict(data.get("proposed_semantic_content", {})),
            candidate_scope=data.get("candidate_scope"),
            supporting_memory_artifacts=tuple(data.get("supporting_memory_artifacts", [])),
            contradicting_memory_artifacts=tuple(data.get("contradicting_memory_artifacts", [])),
            unresolved_memory_artifacts=tuple(data.get("unresolved_memory_artifacts", [])),
            extraction_references=tuple(data.get("extraction_references", [])),
            source_roles=tuple(data.get("source_roles", [])),
            ontology_context=data.get("ontology_context", ""),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            alternatives=tuple(data.get("alternatives", [])),
            limitations=tuple(data.get("limitations", [])),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = ["KnowledgeSemanticCandidate"]