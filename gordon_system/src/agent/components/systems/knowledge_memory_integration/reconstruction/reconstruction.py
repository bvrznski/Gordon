# Knowledge Semantic Reconstruction
# ================================

"""
Reconstruction: Restore semantic candidates from persisted representations.

This module defines the reconstruction models that rebuild Knowledge candidates
from their persisted Memory representations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import uuid


# =============================================================================
# RECONSTRUCTION STATUSES
# =============================================================================


class ReconstructionStatus(Enum):
    """
    Status of semantic reconstruction from persistence.
    
    Indicates whether reconstruction completed successfully and what state
    the reconstructed candidate is in.
    """
    
    COMPLETE = "complete"           # Full reconstruction successful
    PARTIAL = "partial"             # Partial reconstruction, some data unavailable
    DEGRADED = "degraded"           # Reconstruction available but degraded
    SUPERSEDED = "superseded"       # Candidate has been superseded
    INCOMPATIBLE = "incompatible"   # Incompatible with current ontology
    MISSING_DEPENDENCIES = "missing_dependencies"  # Dependencies not found
    CORRUPTED = "corrupted"         # Representation corrupted
    RESTRICTED = "restricted"       # Limited by authorization
    REJECTED = "rejected"           # Reconstruction rejected
    FAILED = "failed"               # Reconstruction failed
    UNKNOWN = "unknown"             # Status unknown


# =============================================================================
# KNOWLEDGE SEMANTIC RECONSTRUCTION
# =============================================================================


@dataclass(frozen=True)
class KnowledgeSemanticReconstruction:
    """
    Reconstructed candidate from persisted Memory representation.
    
    The result is a candidate for Knowledge activation - it is not yet active
    knowledge until validated.
    
    Fields:
        reconstruction_identity:   Unique ID for this reconstruction
        
        # Source memory side
        memory_artifacts:          The memory artifacts used for reconstruction
        persistence_references:    References to persistence records
        
        # Stored semantics
        stored_semantic_identity:  Semantic identity in storage
        stored_semantic_revision:  Revision in storage
        stored_schema_revision:    Schema revision in storage
        stored_ontology_revision:  Ontology revision in storage
        
        # Target context
        target_knowledge_contract: Knowledge contract being targeted
        reconstructed_candidate:   The reconstructed candidate structure
        
        # Grounding and dependencies
        grounding_references:      References to grounding records
        missing_dependencies:      Dependencies not found
        
        # Compatibility check
        compatibility:             Is this compatible with current system?
        
        # Quality metrics (required)
        confidence:                Confidence in reconstruction quality
        uncertainty:               Uncertainty about correctness
        
        # Limitations and provenance
        limitations:               Known issues
        revision:                  Reconstruction revision number
        provenance:                How was this reconstructed?
    """
    
    # Identity (required)
    reconstruction_identity: str              # Unique ID
    
    # Source memory side
    memory_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Artifact IDs
    persistence_references: Tuple[str, ...] = field(default_factory=tuple)
    
    # Stored semantics
    stored_semantic_identity: str = ""
    stored_semantic_revision: int = 1
    stored_schema_revision: int = 1
    stored_ontology_revision: int = 1
    
    # Target context
    target_knowledge_contract: str = ""       # Contract being targeted
    reconstructed_candidate: Dict[str, Any] = field(default_factory=dict)
    
    # Grounding and dependencies
    grounding_references: Tuple[str, ...] = field(default_factory=tuple)
    missing_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    
    # Compatibility (required)
    compatibility: bool = False               # Is this compatible?
    
    # Quality metrics (required)
    confidence: float = 0.5                   # Confidence in reconstruction
    uncertainty: float = 0.5                  # Uncertainty about correctness
    
    # Limitations and diagnostics
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    # Revision tracking
    revision: int = 1                         # Reconstruction revision number
    
    # Provenance (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate reconstruction."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
    
    @property
    def is_compatible(self) -> bool:
        """Check if this reconstruction is compatible with current system."""
        return self.compatibility
    
    @property
    def can_be_activated(self) -> bool:
        """Check if this reconstructed candidate can be activated."""
        return self.is_compatible and len(self.reconstructed_candidate) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reconstruction to dictionary for serialization."""
        return {
            "reconstruction_identity": self.reconstruction_identity,
            "memory_artifacts": list(self.memory_artifacts),
            "persistence_references": list(self.persistence_references),
            "stored_semantic_identity": self.stored_semantic_identity,
            "stored_semantic_revision": self.stored_semantic_revision,
            "stored_schema_revision": self.stored_schema_revision,
            "stored_ontology_revision": self.stored_ontology_revision,
            "target_knowledge_contract": self.target_knowledge_contract,
            "reconstructed_candidate": dict(self.reconstructed_candidate),
            "grounding_references": list(self.grounding_references),
            "missing_dependencies": list(self.missing_dependencies),
            "compatibility": self.compatibility,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "diagnostics": list(self.diagnostics),
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeSemanticReconstruction":
        """Create reconstruction from dictionary."""
        return cls(
            reconstruction_identity=data.get("reconstruction_identity", str(id(data))),
            memory_artifacts=tuple(data.get("memory_artifacts", [])),
            persistence_references=tuple(data.get("persistence_references", [])),
            stored_semantic_identity=data.get("stored_semantic_identity", ""),
            stored_semantic_revision=int(data.get("stored_semantic_revision", 1)),
            stored_schema_revision=int(data.get("stored_schema_revision", 1)),
            stored_ontology_revision=int(data.get("stored_ontology_revision", 1)),
            target_knowledge_contract=data.get("target_knowledge_contract", ""),
            reconstructed_candidate=dict(data.get("reconstructed_candidate", {})),
            grounding_references=tuple(data.get("grounding_references", [])),
            missing_dependencies=tuple(data.get("missing_dependencies", [])),
            compatibility=bool(data.get("compatibility", False)),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            limitations=tuple(data.get("limitations", [])),
            diagnostics=tuple(data.get("diagnostics", [])),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = [
    "ReconstructionStatus",
    "KnowledgeSemanticReconstruction",
]