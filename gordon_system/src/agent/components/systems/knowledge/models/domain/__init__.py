# Domain Models - Phase 6.7
# =========================

"""
Domain Models: Specialized knowledge representations for specific domains.

Domain Models organize domain-specific knowledge including:
- Domain ontologies and terminology
- Domain rules and constraints
- Domain-specific inference patterns
- Domain validation criteria
- Cross-domain integration points
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# DOMAIN MODEL - Canonical domain representation
# =============================================================================


@dataclass(frozen=True)
class DomainModel:
    """
    Canonical representation of a domain model in Gordon's knowledge system.
    
    Domain Models organize specialized knowledge while maintaining modularity.
    
    Fields:
        model_identity:         Unique identifier for this domain model
        semantic_identity:      Stable semantic identity across revisions
        domain_name:            Name of the domain being modeled
        ontology:               Domain concepts and their relationships
        rules:                  Domain rules and constraints
        validation_criteria:    Criteria for validating domain knowledge
        assumptions:            Domain-specific assumptions
        provenance:             Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    model_identity: str                 # Unique ID for this instance
    
    semantic_identity: str              # Stable identifier across revisions
    
    # Domain identification
    domain_name: str = ""               # Name of the domain
    
    # Ontology representation
    ontology: Dict[str, Any] = field(default_factory=dict)  # Concepts and relations
    
    # Rules (optional but recommended)
    rules: Tuple[str, ...] = field(default_factory=tuple)  # Domain rules
    
    # Validation criteria
    validation_criteria: Tuple[str, ...] = field(default_factory=tuple)  # Validation rules
    
    # Assumptions (required for domain models)
    assumptions: Tuple[str, ...] = field(default_factory=tuple)  # Domain assumptions
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if model has minimal required data."""
        return (
            len(self.model_identity) > 0 and
            len(self.domain_name) > 0
        )
    
    @property
    def rule_count(self) -> int:
        """Get the number of domain rules."""
        return len(self.rules)
    
    @property
    def concept_count(self) -> int:
        """Get the number of concepts in ontology."""
        return len(self.ontology.get("concepts", []))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert domain model to dictionary for serialization."""
        return {
            "model_identity": self.model_identity,
            "semantic_identity": self.semantic_identity,
            "domain_name": self.domain_name,
            "ontology": dict(self.ontology),
            "rules": list(self.rules),
            "validation_criteria": list(self.validation_criteria),
            "assumptions": list(self.assumptions),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainModel":
        """Create domain model from dictionary."""
        return cls(
            model_identity=data.get("model_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            domain_name=data.get("domain_name", ""),
            ontology=dict(data.get("ontology", {})),
            rules=tuple(data.get("rules", [])),
            validation_criteria=tuple(data.get("validation_criteria", [])),
            assumptions=tuple(data.get("assumptions", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        domain_name: str,
        semantic_identity: Optional[str] = None,
        ontology: Optional[Dict[str, Any]] = None,
        rules: Optional[List[str]] = None,
        validation_criteria: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None,
    ) -> "DomainModel":
        """
        Create a new domain model.
        
        Args:
            domain_name: Name of the domain being modeled
            semantic_identity: Stable identifier across revisions (optional)
            ontology: Domain concepts and relations (optional)
            rules: Domain rules (optional)
            validation_criteria: Validation criteria (optional)
            assumptions: Domain assumptions (required)
            
        Returns:
            A new domain model
        """
        if semantic_identity is None:
            semantic_identity = f"domain:{uuid.uuid4().hex[:16]}"
        
        return cls(
            model_identity=f"domain_model:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            domain_name=domain_name,
            ontology=dict(ontology or {}),
            rules=tuple(rules or []),
            validation_criteria=tuple(validation_criteria or []),
            assumptions=tuple(assumptions or []),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


# =============================================================================
# DOMAIN ONTOLOGY - Domain concept organization
# =============================================================================


@dataclass(frozen=True)
class DomainOntology:
    """
    Organization of domain concepts and relationships.
    
    Fields:
        ontology_id:            Unique identifier for the ontology
        concepts:               Domain concepts with their properties
        relations:              Relationships between concepts
        axioms:                 Self-evident truths in the domain
        inference_rules:        Rules for deriving new knowledge
    """
    
    ontology_id: str                    # Unique ID
    
    concepts: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # Concept properties
    
    relations: Dict[Tuple[str, str], str] = field(default_factory=dict)  # Concept relations
    
    axioms: Tuple[str, ...] = field(default_factory=tuple)  # Domain axioms
    
    inference_rules: Tuple[str, ...] = field(default_factory=tuple)  # Inference patterns


__all__ = [
    "DomainModel",
    "DomainOntology",
]