# Oriented Network Architectural Composition
# ===========================================

"""
Architectural composition specification for the Canonical Orientation Meta-Model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet


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
    
    layers: tuple[str, ...] = field(default_factory=lambda: (
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