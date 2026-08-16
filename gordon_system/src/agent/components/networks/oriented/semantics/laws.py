# Oriented Network Semantic Laws
# ==============================

"""
Semantic Laws for the Oriented Network (Phase 4.7.2)

These are the normative semantic laws that every implementation must obey.
They form the constitutional foundation of the Oriented Network's semantics.

SEMANTIC LAWS:
    ORIENTED-SEMANTIC-LAW-001 through ORIENTED-SEMANTIC-LAW-040

Every law is enforced as a principle in the semantic model.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SemanticLaw:
    """
    A semantic law that governs the Oriented Network.
    
    Every implementation must conform to these laws.
    """
    code: str
    """The law code (e.g., ORIENTED-SEMANTIC-LAW-001)"""
    
    title: str
    """Short description of the law"""
    
    content: str
    """Full text of the law"""
    
    category: str = "general"
    """Category: general, ownership, hierarchy, relationship"""


# =============================================================================
# ORIENTED NETWORK SEMANTIC LAWS (ORIENTED-SEMANTIC-LAW-XXX)
# =============================================================================

ORIENTED_SEMANTIC_LAWS: tuple[SemanticLaw, ...] = (
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-001",
        title="Orientation is Semantic",
        content=(
            "Orientation is a semantic relationship. It is not a runtime process."
        ),
        category="orientation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-002",
        title="No Execution Implied",
        content=(
            "Orientation never implies execution."
        ),
        category="orientation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-003",
        title="No Planning Implied",
        content=(
            "Orientation never implies planning."
        ),
        category="orientation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-004",
        title="No Reasoning Implied",
        content=(
            "Orientation never implies reasoning."
        ),
        category="orientation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-005",
        title="Independent Existence",
        content=(
            "Orientation may exist independently of execution."
        ),
        category="orientation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-006",
        title="Stable Identity",
        content=(
            "Orientation possesses stable semantic identity."
        ),
        category="identity"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-007",
        title="Goal External Authority",
        content=(
            "Goals remain externally authoritative."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-008",
        title="Objective External Authority",
        content=(
            "Objectives remain externally authoritative."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-009",
        title="Task External Authority",
        content=(
            "Tasks remain externally authoritative."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-010",
        title="Plan External Authority",
        content=(
            "Plans remain externally authoritative."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-011",
        title="Decision External Authority",
        content=(
            "Decisions remain externally authoritative."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-012",
        title="References Not Ownership",
        content=(
            "Orientation references cognitive artefacts. It never owns them."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-013",
        title="Unique Canonical Definition",
        content=(
            "Every semantic concept possesses exactly one canonical definition."
        ),
        category="definition"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-014",
        title="Unique Architectural Owner",
        content=(
            "Every semantic concept possesses exactly one architectural owner."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-015",
        title="No Ambiguous Terminology",
        content=(
            "Terminology shall never be ambiguous."
        ),
        category="vocabulary"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-016",
        title="Distinct Equivalent Concepts",
        content=(
            "Equivalent concepts shall not coexist without explicit semantic distinction."
        ),
        category="vocabulary"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-017",
        title="Purpose Higher Than Mission",
        content=(
            "Purpose exists at a higher semantic level than Mission."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-018",
        title="Mission Higher Than Goal",
        content=(
            "Mission exists at a higher semantic level than Goal."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-019",
        title="Goals Organize Objectives",
        content=(
            "Goals organize Objectives."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-020",
        title="Objectives Organize Tasks",
        content=(
            "Objectives organize Tasks."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-021",
        title="Tasks Contribute to Objectives",
        content=(
            "Tasks contribute toward Objectives."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-022",
        title="Objectives Contribute to Goals",
        content=(
            "Objectives contribute toward Goals."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-023",
        title="Goals Contribute to Missions",
        content=(
            "Goals contribute toward Missions."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-024",
        title="Missions Contribute to Purpose",
        content=(
            "Missions contribute toward Purpose."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-025",
        title="Context Influences Orientation",
        content=(
            "Context influences Orientation."
        ),
        category="relationship"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-026",
        title="Constraints Influence Orientation",
        content=(
            "Constraints influence Orientation."
        ),
        category="relationship"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-027",
        title="Dependencies Influence Orientation",
        content=(
            "Dependencies influence Orientation."
        ),
        category="relationship"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-028",
        title="Alignment Evaluates Consistency",
        content=(
            "Alignment evaluates semantic consistency."
        ),
        category="evaluation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-029",
        title="Confidence is Semantic Belief",
        content=(
            "Confidence expresses semantic belief. It is not probabilistic inference."
        ),
        category="evaluation"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-030",
        title="Progress is Semantic Advancement",
        content=(
            "Progress represents semantic advancement. It is not execution percentage."
        ),
        category="progress"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-031",
        title="Completion is Semantic Satisfaction",
        content=(
            "Completion represents semantic satisfaction."
        ),
        category="progress"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-032",
        title="Failure is Semantic Inability",
        content=(
            "Failure represents semantic inability to satisfy Orientation."
        ),
        category="failure"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-033",
        title="Recovery Preserves Continuity",
        content=(
            "Recovery preserves semantic continuity whenever possible."
        ),
        category="lifecycle"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-034",
        title="Interruption Does Not Terminate",
        content=(
            "Interruption does not necessarily terminate Orientation."
        ),
        category="lifecycle"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-035",
        title="Suspension Preserves Identity",
        content=(
            "Suspension preserves semantic identity."
        ),
        category="lifecycle"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-036",
        title="Replacement Preserves Lineage",
        content=(
            "Replacement preserves semantic lineage."
        ),
        category="lifecycle"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-037",
        title="Hierarchy is Acyclic",
        content=(
            "Semantic hierarchy shall remain acyclic."
        ),
        category="hierarchy"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-038",
        title="Ownership Never Overlaps",
        content=(
            "Semantic ownership shall never overlap."
        ),
        category="ownership"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-039",
        title="Explicit Relationships",
        content=(
            "Every semantic relationship shall possess explicit meaning."
        ),
        category="relationship"
    ),
    
    SemanticLaw(
        code="ORIENTED-SEMANTIC-LAW-040",
        title="Internal Consistency",
        content=(
            "The semantic ontology shall remain internally consistent."
        ),
        category="ontology"
    ),
)

__all__ = [
    "SemanticLaw",
    "ORIENTED_SEMANTIC_LAWS",
]