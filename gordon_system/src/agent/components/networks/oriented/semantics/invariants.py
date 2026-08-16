# Oriented Network Semantic Invariants
# ====================================

"""
Semantic Invariants for the Oriented Network (Phase 4.7.2)

These are the invariants that always hold true in the semantic model.
They form the invariant principles of the Oriented Network's semantics.

SEMANTIC INVARIANTS:
    INV-001 through INV-030

Every implementation must maintain these invariants.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SemanticInvariant:
    """
    A semantic invariant that must always hold.
    
    Every implementation must maintain these invariants.
    """
    code: str
    """The invariant code (e.g., INV-001)"""
    
    title: str
    """Short description of the invariant"""
    
    content: str
    """Full text of the invariant"""
    
    category: str = "general"
    """Category: identity, ownership, hierarchy, relationship"""


# =============================================================================
# SEMANTIC INVARIANTS (INV-XXX)
# =============================================================================

SEMANTIC_INVARIANTS: tuple[SemanticInvariant, ...] = (
    SemanticInvariant(
        code="INV-001",
        title="Orientation Has Identity",
        content=(
            "Every Orientation possesses semantic identity."
        ),
        category="identity"
    ),
    
    SemanticInvariant(
        code="INV-002",
        title="Orientation Has Targets",
        content=(
            "Every Orientation possesses intentional targets."
        ),
        category="identity"
    ),
    
    SemanticInvariant(
        code="INV-003",
        title="Goal Has Unique Definition",
        content=(
            "Every Goal possesses exactly one semantic definition."
        ),
        category="definition"
    ),
    
    SemanticInvariant(
        code="INV-004",
        title="Objective Has Unique Definition",
        content=(
            "Every Objective possesses exactly one semantic definition."
        ),
        category="definition"
    ),
    
    SemanticInvariant(
        code="INV-005",
        title="Task Has Unique Definition",
        content=(
            "Every Task possesses exactly one semantic definition."
        ),
        category="definition"
    ),
    
    SemanticInvariant(
        code="INV-006",
        title="Constraint Has Unique Definition",
        content=(
            "Every Constraint possesses exactly one semantic definition."
        ),
        category="definition"
    ),
    
    SemanticInvariant(
        code="INV-007",
        title="Context Has Unique Definition",
        content=(
            "Every Context possesses exactly one semantic definition."
        ),
        category="definition"
    ),
    
    SemanticInvariant(
        code="INV-008",
        title="Concept Has Single Owner",
        content=(
            "Every semantic concept has exactly one owner."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-009",
        title="Ownership Never Changes Implicitly",
        content=(
            "Semantic ownership never changes implicitly."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-010",
        title="Authority Is Externally Defined",
        content=(
            "Semantic authority remains externally defined."
        ),
        category="authority"
    ),
    
    SemanticInvariant(
        code="INV-011",
        title="Orientation Never Owns Goals",
        content=(
            "Orientation never owns Goals."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-012",
        title="Orientation Never Owns Objectives",
        content=(
            "Orientation never owns Objectives."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-013",
        title="Orientation Never Owns Tasks",
        content=(
            "Orientation never owns Tasks."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-014",
        title="Orientation Never Owns Plans",
        content=(
            "Orientation never owns Plans."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-015",
        title="Orientation Never Owns Decisions",
        content=(
            "Orientation never owns Decisions."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-016",
        title="Orientation Never Owns Workspace",
        content=(
            "Orientation never owns Workspace."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-017",
        title="Orientation Never Owns Working Memory",
        content=(
            "Orientation never owns Working Memory."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-018",
        title="Orientation Never Owns Scheduler",
        content=(
            "Orientation never owns Scheduler behaviour."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-019",
        title="Hierarchy is Acyclic",
        content=(
            "Semantic hierarchy remains acyclic."
        ),
        category="hierarchy"
    ),
    
    SemanticInvariant(
        code="INV-020",
        title="Relationships are Typed",
        content=(
            "Every semantic relationship is typed."
        ),
        category="relationship"
    ),
    
    SemanticInvariant(
        code="INV-021",
        title="Dependencies are Explicit",
        content=(
            "Every semantic dependency is explicit."
        ),
        category="relationship"
    ),
    
    SemanticInvariant(
        code="INV-022",
        title="Influences are Explicit",
        content=(
            "Every semantic influence is explicit."
        ),
        category="relationship"
    ),
    
    SemanticInvariant(
        code="INV-023",
        title="Lineage Preserved",
        content=(
            "Semantic lineage is preserved across replacement."
        ),
        category="lifecycle"
    ),
    
    SemanticInvariant(
        code="INV-024",
        title="Continuity Survives Interruption",
        content=(
            "Semantic continuity survives interruption when justified."
        ),
        category="lifecycle"
    ),
    
    SemanticInvariant(
        code="INV-025",
        title="Continuity Survives Suspension",
        content=(
            "Semantic continuity survives suspension."
        ),
        category="lifecycle"
    ),
    
    SemanticInvariant(
        code="INV-026",
        title="Context Never Owns Orientation",
        content=(
            "Context never owns Orientation."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-027",
        title="Constraints Never Own Orientation",
        content=(
            "Constraints never own Orientation."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-028",
        title="Dependencies Never Own Orientation",
        content=(
            "Dependencies never own Orientation."
        ),
        category="ownership"
    ),
    
    SemanticInvariant(
        code="INV-029",
        title="Vocabulary is Canonical",
        content=(
            "Semantic vocabulary remains canonical."
        ),
        category="vocabulary"
    ),
    
    SemanticInvariant(
        code="INV-030",
        title="Terminology Consistent",
        content=(
            "Terminology remains internally consistent."
        ),
        category="vocabulary"
    ),
)

__all__ = [
    "SemanticInvariant",
    "SEMANTIC_INVARIANTS",
]