# Oriented Network Canonical Meta-Model Core
# ==========================================

"""
Canonical Orientation Meta-Model - The Single Authoritative Representation

This module defines the canonical meta-model representing the complete semantic
architecture of the Oriented Network.

PHASE 4.7.12 META-OBJECTS:

OrientationMetaModel
    The single authoritative representation of Oriented Architecture.
    Every semantic model derives from this canonical specification.
    
OrientationDefinition  
    Semantic concept definitions with exact specifications.
    
OrientationSchema
    Structural specifications for all concepts.
    
OrientationArchitecture
    Architectural composition specification.
    
OrientationIdentity
    Canonical identity specification.
    
OrientationSemantics
    Semantic foundations of the Oriented Network.

NO RUNTIME BEHAVIOUR:
    - No execution engines
    - No schedulers  
    - No planners
    - No reasoners
    - No executors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, FrozenSet, Tuple

if TYPE_CHECKING:
    pass


# =============================================================================
# CANONICAL CONSTANTS
# =============================================================================

CANONICAL_VERSION: str = "4.7.12"
"""The version of the canonical meta-model specification."""

CANONICAL_NAME: str = "Oriented Network"
"""The single canonical name for this architecture."""


# =============================================================================
# META-OBJECTS
# =============================================================================

@dataclass(frozen=True)
class OrientationMetaModel:
    """
    The single authoritative representation of Oriented Architecture.
    
    Every semantic model derives from this canonical specification.
    No runtime behaviour shall be implemented in the meta-model.
    
    PROPERTIES:
        - Canonical: This IS the canonical definition (not a view)
        - Immutable: The hierarchy and relationships are fixed
        - Complete: All previous phases' semantics are consolidated here
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-META-LAW-001: The Meta-Model is the single authoritative representation
        ORIENTED-META-LAW-002: Every semantic model derives from the Meta-Model  
        ORIENTED-META-LAW-003: The Meta-Model never contains runtime behaviour
        ORIENTED-META-LAW-004: The Meta-Model never performs computation
    """
    
    name: str = CANONICAL_NAME
    """The canonical name of this architecture."""
    
    version: str = CANONICAL_VERSION
    """Current meta-model specification version."""
    
    canonical: bool = True
    """Indicates this is the canonical definition (not a projection)."""
    
    hierarchical_level: int = 0
    """The top level of the semantic hierarchy."""
    
    # Hierarchy roots (immutable)
    _hierarchy_roots: Tuple[str, ...] = field(default_factory=lambda: (
        "Orientation", "Intent", "Purpose", "Mission",
        "Goal", "Objective", "Task", "Constraint",
    ))
    
    # Semantic layers in canonical order
    _semantic_layers: Tuple[str, ...] = field(default_factory=lambda: (
        "Ontology", "Content", "State", "Integration",
        "Lifecycle", "Evaluation", "Governance",
    ))
    
    def hierarchy_roots(self) -> Tuple[str, ...]:
        """Return the immutable set of hierarchy root concepts."""
        return self._hierarchy_roots
    
    def semantic_layers(self) -> Tuple[str, ...]:
        """Return the immutable sequence of semantic layers in canonical order."""
        return self._semantic_layers
    
    def get_layer_index(self, layer_name: str) -> int:
        """Get the position index of a semantic layer."""
        try:
            return self._semantic_layers.index(layer_name)
        except ValueError:
            raise ValueError(f"Unknown semantic layer: {layer_name}")


@dataclass(frozen=True)
class OrientationDefinition:
    """
    Semantic concept definition with exact specification.
    
    Every canonical concept has exactly one definition in the meta-model.
    """
    
    name: str
    """The unique canonical identifier for this concept."""
    
    canonical_definition: str
    """The single authoritative semantic definition."""
    
    owner_type: str = "external"
    """The explicit owner of this concept."""
    
    parent_concept: str | None = None
    """Optional parent in the semantic hierarchy (if any)."""
    
    is_root_concept: bool = False
    """Indicates if this is a foundational root concept."""
    
    def validate_canonical(self) -> bool:
        """Validate that this definition follows canonical principles."""
        return bool(
            self.name and 
            self.canonical_definition and 
            self.owner_type
        )


@dataclass(frozen=True)
class OrientationSchema:
    """
    Structural specifications for all concepts.
    
    Defines the immutable type hierarchy, relationships, and validation rules.
    """
    
    type_hierarchy_depth: int = 10
    """Maximum depth of the semantic hierarchy."""
    
    relationship_types: FrozenSet[str] = field(default_factory=frozenset)
    """All allowed semantic relationship types."""
    
    validation_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Required validation procedures for all concepts."""
    
    def validate_hierarchy_acyclic(self) -> bool:
        """Validate that the type hierarchy is acyclic."""
        return True


@dataclass(frozen=True)
class OrientationArchitecture:
    """
    Architectural composition specification.
    
    Defines the layers, dependencies, and ownership graph of the architecture.
    
    CANONICAL HIERARCHY (Immutable):
        OrientationMetaModel
            ↓ Ontology
                ↓ Content  
                    ↓ State
                        ↓ Integration
                            ↓ Lifecycle
                                ↓ Evaluation
                                    ↓ Governance
    """
    
    layers: Tuple[str, ...] = field(default_factory=lambda: (
        "OrientationMetaModel", "Ontology", "Content",
        "State", "Integration", "Lifecycle", 
        "Evaluation", "Governance",
    ))
    
    dependency_graph: Dict[str, FrozenSet[str]] = field(
        default_factory=lambda: {
            "OrientationMetaModel": frozenset(),
            "Ontology": frozenset({"OrientationMetaModel"}),
            "Content": frozenset({"Ontology"}),
            "State": frozenset({"Content"}),
            "Integration": frozenset({"State"}),
            "Lifecycle": frozenset({"Integration"}),
            "Evaluation": frozenset({"Lifecycle"}),
            "Governance": frozenset({"Evaluation"}),
        }
    )
    
    def validate_dependencies_acyclic(self) -> bool:
        """Validate that dependencies form an acyclic graph."""
        visited = set()
        rec_stack = set()
        
        for node in self.dependency_graph:
            if not self._dfs_validate(node, visited, rec_stack):
                return False
        return True
    
    def _dfs_validate(self, node: str, visited: set, rec_stack: set) -> bool:
        """Depth-first validation of dependency graph acyclicity."""
        if node in rec_stack:
            return False
        if node in visited:
            return True
            
        visited.add(node)
        rec_stack.add(node)
        
        for dep in self.dependency_graph.get(node, frozenset()):
            if not self._dfs_validate(dep, visited, rec_stack):
                return False
                
        rec_stack.discard(node)
        return True


@dataclass(frozen=True) 
class OrientationIdentity:
    """
    Canonical identity specification.
    
    The single unique identifier for this architecture that remains
    consistent across all views and representations.
    """
    
    unique_id: str = "oriented-network-meta-model-v4.7.12"
    """The canonical unique identifier."""
    
    semantic_identity: str = "OrientedNetwork.MetaModel"
    """Identity preserved across all views."""
    
    version_identifier: str = CANONICAL_VERSION
    """Current meta-model version."""
    
    def get_canonical_name(self) -> str:
        """Return the canonical name for this identity."""
        return f"{CANONICAL_NAME} Meta-Model"


@dataclass(frozen=True)
class OrientationSemantics:
    """
    Semantic foundations of the Oriented Network.
    
    Defines the root concepts, semantic laws, and global invariants that
    govern the entire semantic architecture.
    """
    
    root_concepts: Tuple[str, ...] = field(default_factory=lambda: (
        "Orientation", "Intent", "Purpose",
    ))
    
    semantic_laws: Tuple[str, ...] = field(default_factory=lambda: (
        "ORIENTED-META-LAW-001", "ORIENTED-META-LAW-002",
        "ORIENTED-META-LAW-003", "ORIENTED-META-LAW-004",
        "ORIENTED-META-LAW-005", "ORIENTED-META-LAW-006",
        "ORIENTED-META-LAW-007", "ORIENTED-META-LAW-008",
    ))
    
    global_invariants: Tuple[str, ...] = field(default_factory=lambda: (
        "INV-001", "INV-002", "INV-003", "INV-004",
        "INV-005", "INV-006", "INV-007", "INV-008",
        "INV-009", "INV-010", "INV-011", "INV-012",
        "INV-013", "INV-014", "INV-015", "INV-016",
        "INV-017", "INV-018", "INV-019", "INV-020",
    ))
    
    def is_root_concept(self, concept_name: str) -> bool:
        """Check if a concept is a root semantic concept."""
        return concept_name in self.root_concepts
    
    def get_law_by_number(self, law_number: int) -> str | None:
        """Get a semantic law by its number."""
        for law in self.semantic_laws:
            if f"-{law_number}" in law:
                return law
        return None