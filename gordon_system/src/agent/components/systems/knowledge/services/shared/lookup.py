"""Semantic Lookup - Phase 6.9 Part 2 Section 5.

This module implements the canonical contract for semantic identity resolution
in Knowledge Services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LOOKUP STRATEGY - Phase 6.9 Part 2 Section 5
# =============================================================================


class LookupStrategy(Enum):
    """
    Strategies for semantic lookup.
    
    Direct Resolution:
        EXACT       -> Exact identity match (no ambiguity possible)
        CANONICAL   -> Resolve to canonical form
    
    Similarity-Based:
        SEMANTIC    -> Semantic similarity matching
        STRUCTURAL  -> Structural pattern matching
    
    Complex Resolution:
        ALIAS       -> Alias expansion and resolution
        DUPLICATE   -> Duplicate detection and resolution
        
    Mixed:
        HYBRID      -> Combined strategies for complex lookups
    """
    
    EXACT = "exact"
    CANONICAL = "canonical"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    ALIAS = "alias"
    DUPLICATE = "duplicate"
    HYBRID = "hybrid"


# =============================================================================
# AMBIGUITY KIND - Phase 6.9 Part 2 Section 5 (LOOKUP-LAW-003)
# =============================================================================


class AmbiguityKind(Enum):
    """
    Kinds of lookup ambiguity.
    
    Per LOOKUP-LAW-003: Lookup ambiguity shall remain explicit.
    """
    
    NO_AMBIGUITY = "no_ambiguity"  # Single, unambiguous result
    ALIAS = "alias"              # Multiple aliases for same concept
    DUPLICATE = "duplicate"      # Multiple representations of same artifact
    SEMANTIC_SIMILARITY = "semantic_similarity"  # Similar but distinct concepts
    UNKNOWN = "unknown"


# =============================================================================
# RESOLVED ARTIFACT - Phase 6.9 Part 2 Section 5
# =============================================================================


@dataclass(frozen=True)
class ResolvedArtifact:
    """
    Result of semantic lookup.
    
    Per LOOKUP-LAW-001: Lookup shall resolve canonical semantic identities.
    Per LOOKUP-LAW-002: Aliases shall remain distinguishable from canonical artifacts.
    
    Fields:
        resolved_identity: The resolved canonical identity
        is_canonical: Whether this is the canonical form (not an alias)
        confidence: Confidence score for this resolution (0.0 - 1.0)
        original_references: Original references that led to this resolution
    """
    
    resolved_identity: str
    is_canonical: bool
    confidence: float = 1.0
    original_references: Tuple[str, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resolved artifact to dictionary."""
        return {
            "resolved_identity": self.resolved_identity,
            "is_canonical": self.is_canonical,
            "confidence": self.confidence,
            "original_references": list(self.original_references),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResolvedArtifact:
        """Create resolved artifact from dictionary."""
        return cls(
            resolved_identity=data.get("resolved_identity", ""),
            is_canonical=bool(data.get("is_canonical", True)),
            confidence=float(data.get("confidence", 1.0)),
            original_references=tuple(data.get("original_references", [])),
        )


# =============================================================================
# SEMANTIC LOOKUP - Phase 6.9 Part 2 Section 5
# =============================================================================


@dataclass(frozen=True)
class SemanticLookup:
    """
    Semantic lookup operation result.
    
    Per LOOKUP-LAW-004: Lookup provenance shall remain complete.
    Per LOOKUP-LAW-007: Lookup shall remain independently inspectable.
    
    Fields:
        lookup_identity: Unique identifier for this lookup operation
        lookup_strategy: Strategy used for the lookup
        lookup_targets: Original targets that were looked up
        resolved_artifacts: Resolved canonical artifacts
        ambiguity: Kind of ambiguity encountered (if any)
        
    Invariants:
        * Lookup preserves semantic identity (LOOKUP-LAW-001)
        * Aliases remain distinguishable (LOOKUP-LAW-002)
        * Ambiguity is explicit (LOOKUP-LAW-003)
    """
    
    lookup_identity: str  # Unique identifier
    
    # Lookup strategy (required)
    lookup_strategy: LookupStrategy
    
    # Original targets
    lookup_targets: Tuple[str, ...]
    
    # Resolved artifacts
    resolved_artifacts: Tuple[ResolvedArtifact, ...]
    
    # Ambiguity kind (Per LOOKUP-LAW-003)
    ambiguity: AmbiguityKind = AmbiguityKind.NO_AMBIGUITY
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    def __post_init__(self) -> None:
        """Validate lookup result after creation."""
        if not self.lookup_identity:
            raise ValueError("lookup_identity cannot be empty")
    
    @property
    def is_ambiguous(self) -> bool:
        """Check if this lookup encountered ambiguity."""
        return self.ambiguity != AmbiguityKind.NO_AMBIGUITY
    
    @property
    def has_canonical(self) -> bool:
        """Check if at least one canonical artifact was resolved."""
        return any(a.is_canonical for a in self.resolved_artifacts)
    
    @classmethod
    def create_initial(
        cls,
        lookup_strategy: LookupStrategy,
        targets: List[str],
    ) -> "SemanticLookup":
        """
        Create a new initial semantic lookup.
        
        Args:
            lookup_strategy: Strategy to use for lookup
            targets: Artifact identifiers to look up
            
        Returns:
            New SemanticLookup with empty results
        """
        return cls(
            lookup_identity=f"lookup:{uuid.uuid4().hex[:16]}",
            lookup_strategy=lookup_strategy,
            lookup_targets=tuple(targets),
            resolved_artifacts=tuple(),
            provenance=(
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": "Semantic lookup initialization",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ),
        )
    
    def add_resolved(
        self,
        artifact: ResolvedArtifact,
    ) -> "SemanticLookup":
        """Add a resolved artifact and return new lookup result."""
        return SemanticLookup(
            lookup_identity=self.lookup_identity,
            lookup_strategy=self.lookup_strategy,
            lookup_targets=self.lookup_targets,
            resolved_artifacts=tuple(list(self.resolved_artifacts) + [artifact]),
            ambiguity=self.ambiguity,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Added resolved artifact: {artifact.resolved_identity}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def set_ambiguity(self, kind: AmbiguityKind) -> "SemanticLookup":
        """Record ambiguity encountered during lookup."""
        return SemanticLookup(
            lookup_identity=self.lookup_identity,
            lookup_strategy=self.lookup_strategy,
            lookup_targets=self.lookup_targets,
            resolved_artifacts=self.resolved_artifacts,
            ambiguity=kind,
            provenance=tuple(list(self.provenance) + [
                {
                    "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                    "originating_request": f"Ambiguity recorded: {kind.value}",
                    "originating_system": "knowledge-services-system",
                    "timestamp_utc": time.time(),
                },
            ]),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lookup result to dictionary for serialization."""
        return {
            "lookup_identity": self.lookup_identity,
            "lookup_strategy": self.lookup_strategy.value,
            "lookup_targets": list(self.lookup_targets),
            "resolved_artifacts": [a.to_dict() for a in self.resolved_artifacts],
            "ambiguity": self.ambiguity.value,
            "provenance": list(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SemanticLookup":
        """Create lookup result from dictionary."""
        artifacts = []
        for a_data in data.get("resolved_artifacts", []):
            if isinstance(a_data, dict):
                artifacts.append(ResolvedArtifact.from_dict(a_data))
        
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            lookup_identity=data.get("lookup_identity", str(uuid.uuid4())),
            lookup_strategy=LookupStrategy(data.get("lookup_strategy", "exact")),
            lookup_targets=tuple(data.get("lookup_targets", [])),
            resolved_artifacts=tuple(artifacts),
            ambiguity=AmbiguityKind(data.get("ambiguity", "no_ambiguity")),
            provenance=tuple(provenance),
        )


__all__ = [
    # Lookup strategies (Part 2 Section 5)
    "LookupStrategy",
    # Ambiguity kinds
    "AmbiguityKind",
    # Resolved artifact
    "ResolvedArtifact",
    # Semantic lookup
    "SemanticLookup",
]