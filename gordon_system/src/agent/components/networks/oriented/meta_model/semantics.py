# Oriented Network Semantic Foundations
# ======================================

"""
Semantic foundations of the Canonical Orientation Meta-Model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class OrientationSemantics:
    """
    Semantic foundations of the Oriented Network.
    
    Defines the root concepts, semantic laws, and global invariants that
    govern the entire semantic architecture.
    
    ROOT CONCEPTS (Primary):
        - Orientation: The fundamental semantic relationship
        - Intent: Deliberate cognitive commitment
        - Purpose: The highest-level orientation aim
        
    SEMANTIC LAWS:
        ORIENTED-META-LAW-001 through ORIENTED-META-LAW-008
        
    GLOBAL INVARIANTS:
        INV-001 through INV-030
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