# Knowledge Representation Provenance - Phase 6.2
# ================================================

"""
Provenance tracking for knowledge representations.

This module tracks the generation history of representations, including:
    * Generation model and revision
    * Parameters used during generation
    * Mapping chains (transformations applied)
    * Alignment chains (space alignments performed)
    * Regeneration history
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# REPRESENTATION PROVENANCE - Generation tracking
# =============================================================================


@dataclass(frozen=True)
class RepresentationProvenance:
    """
    Provenance record for a representation.
    
    Tracks the complete generation history including models, parameters,
    and transformation chains that produced this representation.
    
    Fields:
        provenance_identity:   Unique identifier for this provenance record
        semantic_identity:     Identity of the represented artifact
        generation_model:      Model used to generate (e.g., "gpt-4", "text-embedding-v3")
        generation_revision:   Revision number of the generation model
        generation_parameters: Parameters used during generation
        mapping_chain:         All mappings applied during generation
        alignment_chain:       All alignments performed during generation
        regeneration_chain:    All regeneration events that affected this representation
    """
    
    # Identity (required)
    provenance_identity: str               # Unique provenance ID
    
    semantic_identity: str                 # Artifact being represented
    
    # Generation info (required)
    generation_model: str                  # e.g., "gpt-4", "text-embedding-v3"
    generation_revision: int = 1
    
    # Parameters (optional, with defaults)
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Chains
    mapping_chain: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)     # Mappings applied
    alignment_chain: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)   # Alignments performed
    regeneration_chain: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Regenerations
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_complete(self) -> bool:
        """Check if provenance has essential information."""
        return (
            len(self.provenance_identity) > 0 and
            len(self.semantic_identity) > 0 and
            len(self.generation_model) > 0
        )
    
    @property
    def mapping_count(self) -> int:
        """Get total number of mappings in chain."""
        return len(self.mapping_chain)
    
    @property
    def alignment_count(self) -> int:
        """Get total number of alignments in chain."""
        return len(self.alignment_chain)
    
    @property
    def regeneration_count(self) -> int:
        """Get total number of regenerations."""
        return len(self.regeneration_chain)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provenance to dictionary for serialization."""
        return {
            "provenance_identity": self.provenance_identity,
            "semantic_identity": self.semantic_identity,
            "generation_model": self.generation_model,
            "generation_revision": self.generation_revision,
            "generation_parameters": self.generation_parameters,
            "mapping_chain": [m for m in self.mapping_chain],
            "alignment_chain": [a for a in self.alignment_chain],
            "regeneration_chain": [r for r in self.regeneration_chain],
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepresentationProvenance":
        """Create provenance from dictionary."""
        return cls(
            provenance_identity=data.get("provenance_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            generation_model=data.get("generation_model", ""),
            generation_revision=int(data.get("generation_revision", 1)),
            generation_parameters=data.get("generation_parameters", {}),
            mapping_chain=tuple(data.get("mapping_chain", [])),
            alignment_chain=tuple(data.get("alignment_chain", [])),
            regeneration_chain=tuple(data.get("regeneration_chain", [])),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )
    
    def with_mapping(self, mapping: Dict[str, Any]) -> "RepresentationProvenance":
        """Add a mapping to the provenance chain."""
        return RepresentationProvenance(
            provenance_identity=self.provenance_identity,
            semantic_identity=self.semantic_identity,
            generation_model=self.generation_model,
            generation_revision=self.generation_revision,
            generation_parameters=self.generation_parameters,
            mapping_chain=self.mapping_chain + (mapping,),
            alignment_chain=self.alignment_chain,
            regeneration_chain=self.regeneration_chain,
            created_at_utc=self.created_at_utc,
        )
    
    def with_alignment(self, alignment: Dict[str, Any]) -> "RepresentationProvenance":
        """Add an alignment to the provenance chain."""
        return RepresentationProvenance(
            provenance_identity=self.provenance_identity,
            semantic_identity=self.semantic_identity,
            generation_model=self.generation_model,
            generation_revision=self.generation_revision,
            generation_parameters=self.generation_parameters,
            mapping_chain=self.mapping_chain,
            alignment_chain=self.alignment_chain + (alignment,),
            regeneration_chain=self.regeneration_chain,
            created_at_utc=self.created_at_utc,
        )
    
    def with_regeneration(self, regeneration: Dict[str, Any]) -> "RepresentationProvenance":
        """Add a regeneration event to the provenance chain."""
        return RepresentationProvenance(
            provenance_identity=f"prov:{uuid.uuid4().hex[:16]}",
            semantic_identity=self.semantic_identity,
            generation_model=regeneration.get("generation_model", self.generation_model),
            generation_revision=int(regeneration.get("generation_revision", self.generation_revision + 1)),
            generation_parameters=self.generation_parameters,
            mapping_chain=tuple(),  # Reset on regeneration
            alignment_chain=tuple(),  # Reset on regeneration
            regeneration_chain=self.regeneration_chain + (regeneration,),
            created_at_utc=time.time(),
        )


# =============================================================================
# PROVENANCE VERIFICATION - Integrity checking
# =============================================================================


@dataclass(frozen=True)
class ProvenanceVerification:
    """
    Verification record for provenance integrity.
    
    Tracks when and how provenance was verified.
    
    Fields:
        verification_identity: Unique identifier for this verification
        provenance_id:         ID of the provenance being verified
        verification_timestamp: When verification occurred
        verification_method:   Method used (e.g., "hash", "signature")
        result:                Whether verification succeeded
        notes:                 Additional verification notes
    """
    
    # Identity and metadata
    verification_identity: str             # Unique verification ID
    
    provenance_id: str                     # Provenance being verified
    
    verification_timestamp: float = field(default_factory=time.time)
    verification_method: str = "hash"      # e.g., "hash", "signature"
    
    result: bool = True                    # Whether verification succeeded
    notes: Optional[str] = None            # Additional notes
    
    @classmethod
    def create_initial(
        cls,
        provenance_id: str,
        method: str = "hash",
    ) -> "ProvenanceVerification":
        """Create initial verification record."""
        return cls(
            verification_identity=f"verify:{uuid.uuid4().hex[:16]}",
            provenance_id=provenance_id,
            verification_method=method,
        )
    
    def mark_failed(self, reason: str) -> "ProvenanceVerification":
        """Mark verification as failed."""
        return ProvenanceVerification(
            verification_identity=self.verification_identity,
            provenance_id=self.provenance_id,
            verification_timestamp=time.time(),
            verification_method=self.verification_method,
            result=False,
            notes=reason,
        )


__all__ = [
    # Provenance record
    "RepresentationProvenance",
    
    # Verification records
    "ProvenanceVerification",
]