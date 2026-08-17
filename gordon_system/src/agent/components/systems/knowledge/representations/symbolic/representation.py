# Knowledge Representation - Symbolic - Phase 6.2
# ==============================================

"""
Symbolic Representation: Explicit semantic structure for reasoning.

This module implements the canonical symbolic representation contract:
    * Entities - Named objects with unique identity
    * Relations - Semantic connections between entities
    * Attributes - Properties of entities
    * Constraints - Rules governing valid configurations
    * Provenance - Generation history tracking

Symbolic representations are preferred for:
    * Reasoning operations
    * Planning tasks
    * Verification and validation
    * Governance and audit
    * Human-readable explanations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# SYMBOLIC REPRESENTATION - Canonical contract
# =============================================================================


@dataclass(frozen=True)
class SymbolicRepresentation:
    """
    Symbolic representation of a semantic artifact.
    
    Provides explicit, inspectable structure for reasoning operations.
    
    Fields:
        representation_identity: Unique identifier for this representation
        semantic_identity:       Identity of the represented artifact
        semantic_revision:       Revision number of the artifact
        symbolic_structure:      The actual symbolic content (entities, relations)
        ontology_revision:       Revision of ontology used for structure
        constraints:             Validity constraints on the structure
        provenance:              Generation and evolution history
    """
    
    # Identity (required)
    representation_identity: str            # Unique representation ID
    
    semantic_identity: str                  # Artifact being represented
    semantic_revision: int = 1              # Artifact revision
    
    # Symbolic content (required)
    symbolic_structure: Dict[str, Any]      # Entities, relations, attributes
    
    # Metadata (optional, with defaults)
    ontology_revision: int = 1              # Ontology version used
    constraints: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Constraints
    provenance_identity: str = field(default_factory=lambda: f"sym:{uuid.uuid4().hex[:16]}")
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if representation has valid data."""
        return (
            len(self.representation_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.symbolic_structure is not None
        )
    
    @property
    def entity_count(self) -> int:
        """Get number of entities in symbolic structure."""
        entities = self.symbolic_structure.get("entities", [])
        return len(entities) if isinstance(entities, (list, tuple)) else 0
    
    @property
    def relation_count(self) -> int:
        """Get number of relations in symbolic structure."""
        relations = self.symbolic_structure.get("relations", [])
        return len(relations) if isinstance(relations, (list, tuple)) else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert representation to dictionary for serialization."""
        return {
            "representation_identity": self.representation_identity,
            "semantic_identity": self.semantic_identity,
            "semantic_revision": self.semantic_revision,
            "symbolic_structure": self.symbolic_structure,
            "ontology_revision": self.ontology_revision,
            "constraints": [c for c in self.constraints],
            "provenance_identity": self.provenance_identity,
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolicRepresentation":
        """Create representation from dictionary."""
        return cls(
            representation_identity=data.get("representation_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            semantic_revision=int(data.get("semantic_revision", 1)),
            symbolic_structure=data.get("symbolic_structure", {}),
            ontology_revision=int(data.get("ontology_revision", 1)),
            constraints=tuple(data.get("constraints", [])),
            provenance_identity=data.get("provenance_identity", f"sym:{uuid.uuid4().hex[:16]}"),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )
    
    @classmethod
    def create_initial(
        cls,
        semantic_identity: str,
        structure: Dict[str, Any],
        ontology_revision: int = 1,
    ) -> "SymbolicRepresentation":
        """Create initial symbolic representation."""
        return cls(
            representation_identity=f"symbolic:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            semantic_revision=1,
            symbolic_structure=structure,
            ontology_revision=ontology_revision,
        )
    
    def with_revision(self, new_revision: int) -> "SymbolicRepresentation":
        """Create new representation with updated revision."""
        return SymbolicRepresentation(
            representation_identity=f"symbolic:{uuid.uuid4().hex[:16]}",
            semantic_identity=self.semantic_identity,
            semantic_revision=new_revision,
            symbolic_structure=self.symbolic_structure,
            ontology_revision=self.ontology_revision,
            constraints=self.constraints,
            provenance_identity=f"sym:{uuid.uuid4().hex[:16]}",
            created_at_utc=time.time(),
        )


__all__ = [
    "SymbolicRepresentation",
]