# Oriented Network Semantic Vocabulary
# =====================================

"""
Terminology Vocabulary for the Oriented Network (Phase 4.7.2)

This module defines canonical meanings for all important concepts.

ARCHITECTURAL PRINCIPLES:
    - Every concept has exactly one canonical meaning
    - Avoid ambiguous terminology
    - Terminology must be internally consistent
    - No concept may have multiple overlapping meanings

SEMANTIC LAWS (See laws.py):
    ORIENTED-SEMANTIC-LAW-015: Terminology shall never be ambiguous
    ORIENTED-SEMANTIC-LAW-016: Equivalent concepts shall not coexist without explicit semantic distinction
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# CONCEPT DEFINITION
# =============================================================================

@dataclass(frozen=True)
class ConceptDefinition:
    """
    A canonical concept definition with precise semantics.
    
    Each concept has exactly one canonical meaning in the Oriented Network.
    No ambiguity or overlapping meanings are permitted.
    """
    name: str
    """The canonical name of the concept"""
    
    definition: str
    """Precise semantic definition"""
    
    domain: str = "general"
    """Domain category for organizational purposes"""
    
    hierarchy_level: int = 0
    """Position in the conceptual hierarchy (0 = highest)"""
    
    synonyms: tuple[str, ...] = field(default_factory=tuple)
    """Synonyms that are semantically equivalent (for reference only)"""
    
    related_concepts: tuple[str, ...] = field(default_factory=tuple)
    """Other concepts this one relates to"""


# =============================================================================
# SEMANTIC RELATIONSHIP TYPES
# =============================================================================

class SemanticRelationshipType(Enum):
    """
    Types of semantic relationships between concepts.
    
    These relationship types are used in the relationship graph to define
    how concepts connect and interact with each other.
    """
    # Ownership Relationships
    OWNERSHIP = "ownership"
    """Concept owns or controls another concept"""
    
    REFERENCE = "reference"
    """Concept points to another (without ownership)"""
    
    # Hierarchical Relationships
    INHERITANCE = "inheritance"
    """Subtype relationship in semantic hierarchy"""
    
    COMPOSITION = "composition"
    """Whole-part relationship"""
    
    # Dependency Relationships
    DEPENDENCY = "dependency"
    """One concept requires another for completion"""
    
    REQUIREMENT = "requirement"
    """Condition that must be satisfied"""
    
    # Influence Relationships
    INFLUENCE = "influence"
    """Affects but does not determine"""
    
    CONSTRAINT = "constraint"
    """Limitation or condition affecting another"""
    
    # State Lifecycle Relationships
    TRANSITION = "transition"
    """State change between lifecycle states"""
    
    CONTINUATION = "continuation"
    """Persistence across episodes"""
    
    INTERRUPTION = "interruption"
    """Temporary cessation of orientation"""
    
    RESTORATION = "restoration"
    """Resumption after interruption"""
    
    # Evaluation Relationships
    EVALUATES = "evaluates"
    """Assesses or evaluates another concept"""
    
    ACHIEVES = "achieves"
    """Fulfills or completes another concept"""
    
    CONTRIBUTES_TO = "contributes_to"
    """Helps toward achieving a higher-level goal"""
    
    # Context Relationships
    CONTEXTUALIZES = "contextualizes"
    """Provides context for understanding"""
    
    BOUNDS = "bounds"
    """Defines boundaries for scope"""


@dataclass(frozen=True)
class SemanticRelationship:
    """
    A typed semantic relationship between two concepts.
    
    Every relationship is explicitly typed and documented.
    Relationships never imply ownership unless specified by the ownership model.
    """
    source: str
    """The source concept in the relationship"""
    
    target: str
    """The target concept in the relationship"""
    
    relationship_type: SemanticRelationshipType
    """The type of relationship"""
    
    description: str = ""
    """Human-readable description of the relationship"""
    
    cardinality: str = "one-to-one"
    """Cardinality: one-to-one, one-to-many, many-to-one"""


# =============================================================================
# CANONICAL VOCABULARY
# =============================================================================

@dataclass(frozen=True)
class Vocabulary:
    """
    The complete canonical vocabulary of the Oriented Network.
    
    This vocabulary defines precise meanings for all important concepts.
    Every concept has exactly one canonical meaning. No ambiguity is permitted.
    """
    
    # =============================================================================
    # HIERARCHY DEFINITIONS
    # =============================================================================
    
    def get_hierarchy_levels(self) -> dict[str, int]:
        """Return the hierarchy level for each concept."""
        return {
            # Top-level purpose concepts
            "Purpose": 0,
            "Intent": 0,
            
            # Mission level
            "Mission": 1,
            
            # Goal system level
            "Goal": 2,
            
            # Objective/Task level
            "Objective": 3,
            "Task": 4,
            
            # Orientation state concepts
            "Orientation": 2,
            "Constraint": 2,
            "Context": 2,
            
            # Lifecycle and state concepts
            "Commitment": 1,
            "Continuation": 1,
            "Interruption": 1,
            "Suspension": 1,
            "Restoration": 1,
            
            # Boundary concepts
            "Scope": 2,
            "Horizon": 2,
            "Dependency": 2,
            "Requirement": 2,
            "Expectation": 2,
            
            # Evaluation concepts
            "Priority": 3,
            "Progress": 3,
            "Completion": 3,
            "Alignment": 3,
            "Confidence": 3,
            "Risk": 3,
            "Recovery": 3,
            "Failure": 3,
        }
    
    # =============================================================================
    # CANONICAL DEFINITIONS
    # =============================================================================
    
    def get_concept_definitions(self) -> tuple[ConceptDefinition, ...]:
        """Return all canonical concept definitions."""
        return (
            # Purpose and Intent (Top Level)
            ConceptDefinition(
                name="Purpose",
                definition=(
                    "The highest-level semantic orientation toward a final aim or "
                    "ultimate cognitive objective that provides ultimate justification."
                ),
                domain="orientation_root",
                hierarchy_level=0,
                synonyms=("Ultimate Aim", "Final Objective"),
                related_concepts=("Mission", "Goal", "Orientation")
            ),
            
            ConceptDefinition(
                name="Intent",
                definition=(
                    "Intentional orientation established through deliberate cognitive "
                    "commitment rather than passive perception."
                ),
                domain="orientation_root",
                hierarchy_level=0,
                synonyms=None,  # No synonyms - intent has unique meaning
                related_concepts=("Orientation", "Goal", "Mission")
            ),
            
            # Mission Level
            ConceptDefinition(
                name="Mission",
                definition=(
                    "A major orientation toward achieving a significant cognitive objective "
                    "that contributes to Purpose and organizes related Goals."
                ),
                domain="orientation_target",
                hierarchy_level=1,
                synonyms=None,  # Mission is unique - not synonymous with goal
                related_concepts=("Purpose", "Goal", "Orientation")
            ),
            
            # Goal Level
            ConceptDefinition(
                name="Goal",
                definition=(
                    "An actively oriented cognitive target that requires specific cognitive work "
                    "to achieve. Remains externally authoritative and externally owned."
                ),
                domain="orientation_target",
                hierarchy_level=2,
                synonyms=None,  # Goal is not Objective, Task, Mission, or Purpose
                related_concepts=("Objective", "Task", "Mission", "Orientation")
            ),
            
            # Objective Level
            ConceptDefinition(
                name="Objective",
                definition=(
                    "An intermediate cognitive target that contributes to Goal achievement. "
                    "Remains externally authoritative and is decomposed from Goals."
                ),
                domain="orientation_target",
                hierarchy_level=3,
                synonyms=None,  # Objective is distinct from Goal and Task
                related_concepts=("Goal", "Task", "Orientation")
            ),
            
            # Task Level
            ConceptDefinition(
                name="Task",
                definition=(
                    "An executable cognitive unit derived from Objectives. "
                    "Remains externally owned and is the basis for runtime execution."
                ),
                domain="orientation_target",
                hierarchy_level=4,
                synonyms=None,  # Task is not an Objective or Goal
                related_concepts=("Objective", "Goal", "Orientation")
            ),
            
            # Orientation Root Concept
            ConceptDefinition(
                name="Orientation",
                definition=(
                    "The semantic relationship between the cognitive agent and "
                    "the entities currently regarded as intentionally relevant."
                ),
                domain="orientation_root",
                hierarchy_level=2,
                synonyms=None,  # Unique - not planning, reasoning, or execution
                related_concepts=("Intent", "Goal", "Context", "Constraint")
            ),
            
            # Context Concept
            ConceptDefinition(
                name="Context",
                definition=(
                    "The surrounding cognitive environment that shapes current orientation. "
                    "Influences but does not determine orientation semantics."
                ),
                domain="boundary",
                hierarchy_level=2,
                synonyms=None,  # Context is not ownership or runtime
                related_concepts=("Orientation", "Constraint", "Scope")
            ),
            
            # Constraint Concept
            ConceptDefinition(
                name="Constraint",
                definition=(
                    "A limitation or condition that affects current orientation. "
                    "Remains externally authoritative and influences orientation semantics."
                ),
                domain="boundary",
                hierarchy_level=2,
                synonyms=None,  # Unique meaning - not goal or objective
                related_concepts=("Orientation", "Goal", "Progress")
            ),
            
            # State and Lifecycle Concepts
            ConceptDefinition(
                name="Commitment",
                definition=(
                    "A semantic strengthening of orientation toward a target. "
                    "Enables persistence across reasoning episodes without runtime execution."
                ),
                domain="lifecycle",
                hierarchy_level=1,
                synonyms=None,  # Unique semantic strengthening
                related_concepts=("Continuation", "Orientation", "Interruption")
            ),
            
            ConceptDefinition(
                name="Continuation",
                definition=(
                    "The maintenance of orientation across multiple reasoning episodes "
                    "or decision boundaries. Preserves semantic identity over time."
                ),
                domain="lifecycle",
                hierarchy_level=1,
                synonyms=None,  # Unique persistence mechanism
                related_concepts=("Commitment", "Suspension", "Restoration")
            ),
            
            ConceptDefinition(
                name="Interruption",
                definition=(
                    "The temporary cessation of active orientation toward a target, "
                    "without termination. May be followed by restoration."
                ),
                domain="lifecycle",
                hierarchy_level=1,
                synonyms=None,  # Unique temporary state
                related_concepts=("Suspension", "Restoration", "Continuation")
            ),
            
            ConceptDefinition(
                name="Suspension",
                definition=(
                    "The preservation of semantic identity during interruption, "
                    "enabling potential future restoration."
                ),
                domain="lifecycle",
                hierarchy_level=1,
                synonyms=None,  # Unique intermediate state
                related_concepts=("Interruption", "Restoration")
            ),
            
            ConceptDefinition(
                name="Restoration",
                definition=(
                    "The resumption of orientation toward a previously interrupted or "
                    "suspended target. May continue from where orientation was suspended."
                ),
                domain="lifecycle",
                hierarchy_level=1,
                synonyms=None,  # Unique recovery mechanism
                related_concepts=("Interruption", "Suspension")
            ),
            
            # Boundary Concepts
            ConceptDefinition(
                name="Scope",
                definition=(
                    "The boundaries of current orientation - what is included and "
                    "what is excluded from intentional focus."
                ),
                domain="boundary",
                hierarchy_level=2,
                synonyms=None,  # Unique boundary concept
                related_concepts=("Orientation", "Context")
            ),
            
            ConceptDefinition(
                name="Horizon",
                definition=(
                    "The temporal and conceptual reach of current orientation. "
                    "Determines how far ahead orientation considers possibilities."
                ),
                domain="boundary",
                hierarchy_level=2,
                synonyms=None,  # Unique temporal extent concept
                related_concepts=("Orientation", "Progress")
            ),
            
            # Evaluation Concepts
            ConceptDefinition(
                name="Priority",
                definition=(
                    "The relative importance or urgency of one orientation target "
                    "compared to others. Affects cognitive resource allocation."
                ),
                domain="evaluation",
                hierarchy_level=3,
                synonyms=None,  # Unique ordering concept
                related_concepts=("Goal", "Objective", "Task")
            ),
            
            ConceptDefinition(
                name="Progress",
                definition=(
                    "Semantic advancement toward orientation targets. "
                    "Not execution percentage but semantic movement toward completion."
                ),
                domain="evaluation",
                hierarchy_level=3,
                synonyms=None,  # Semantic not runtime progress
                related_concepts=("Completion", "Goal")
            ),
            
            ConceptDefinition(
                name="Completion",
                definition=(
                    "Semantic satisfaction of an orientation target. "
                    "Not runtime termination but semantic fulfillment."
                ),
                domain="evaluation",
                hierarchy_level=3,
                synonyms=None,  # Semantic satisfaction
                related_concepts=("Progress", "Goal")
            ),
            
            ConceptDefinition(
                name="Alignment",
                definition=(
                    "Semantic consistency between orientation targets and other cognitive elements. "
                    "Evaluates whether targets are mutually supportive or conflicting."
                ),
                domain="evaluation",
                hierarchy_level=3,
                synonyms=None,  # Unique consistency evaluation
                related_concepts=("Goal", "Objective", "Constraint")
            ),
            
            ConceptDefinition(
                name="Confidence",
                definition=(
                    "Semantic belief in the achievement of orientation targets. "
                    "Not probabilistic inference but semantic conviction based on information."
                ),
                domain="evaluation",
                hierarchy_level=3,
                synonyms=None,  # Semantic belief
                related_concepts=("Goal", "Risk")
            ),
            
            ConceptDefinition(
                name="Risk",
                definition=(
                    "The potential for orientation failure or incomplete achievement. "
                    "Assesses what may prevent successful orientation toward targets."
                ),
                domain="evaluation",
                hierarchy_level=3,
                synonyms=None,  # Unique threat assessment
                related_concepts=("Failure", "Recovery")
            ),
            
            ConceptDefinition(
                name="Recovery",
                definition=(
                    "The restoration of semantic continuity after interruption or failure. "
                    "Preserves orientation identity where possible."
                ),
                domain="lifecycle",
                hierarchy_level=3,
                synonyms=None,  # Unique continuity preservation
                related_concepts=("Interruption", "Failure")
            ),
            
            ConceptDefinition(
                name="Failure",
                definition=(
                    "Semantic inability to satisfy orientation toward a target. "
                    "Not runtime error but semantic termination when achievement is impossible."
                ),
                domain="lifecycle",
                hierarchy_level=3,
                synonyms=None,  # Semantic termination
                related_concepts=("Recovery", "Orientation")
            ),
            
            # Relationship Concepts
            ConceptDefinition(
                name="Dependency",
                definition=(
                    "A semantic relationship where one concept requires another to achieve "
                    "its purpose. Represents requirement without runtime implementation."
                ),
                domain="relationship",
                hierarchy_level=2,
                synonyms=None,  # Semantic not runtime dependency
                related_concepts=("Requirement", "Constraint")
            ),
            
            ConceptDefinition(
                name="Requirement",
                definition=(
                    "A condition or capability that must be satisfied for orientation "
                    "to proceed successfully."
                ),
                domain="relationship",
                hierarchy_level=2,
                synonyms=None,  # Unique necessary condition
                related_concepts=("Dependency", "Constraint")
            ),
            
            ConceptDefinition(
                name="Expectation",
                definition=(
                    "The anticipated outcome or state that orientation targets. "
                    "Semantic anticipation, not probabilistic prediction."
                ),
                domain="relationship",
                hierarchy_level=2,
                synonyms=None,  # Semantic anticipation
                related_concepts=("Progress", "Completion")
            ),
        )
    
    # =============================================================================
    # RELATIONSHIP GRAPH
    # =============================================================================

    def get_relationship_graph(self) -> tuple[SemanticRelationship, ...]:
        """Return the complete semantic relationship graph."""
        return (
            # Orientation relationships
            SemanticRelationship(
                source="Orientation",
                target="Goal",
                relationship_type=SemanticRelationshipType.REFERENCE,
                description="Orientation references Goals as intentional targets"
            ),
            SemanticRelationship(
                source="Orientation",
                target="Objective",
                relationship_type=SemanticRelationshipType.REFERENCE,
                description="Orientation references Objectives as operational targets"
            ),
            SemanticRelationship(
                source="Orientation",
                target="Task",
                relationship_type=SemanticRelationshipType.REFERENCE,
                description="Orientation references Tasks as executable units"
            ),
            SemanticRelationship(
                source="Orientation",
                target="Constraint",
                relationship_type=SemanticRelationshipType.CONSTRAINT,
                description="Constraints influence current orientation"
            ),
            SemanticRelationship(
                source="Orientation",
                target="Context",
                relationship_type=SemanticRelationshipType.CONTEXTUALIZES,
                description="Context surrounds and shapes orientation"
            ),
            
            # Hierarchy relationships (Purpose → Mission → Goal → Objective → Task)
            SemanticRelationship(
                source="Mission",
                target="Goal",
                relationship_type=SemanticRelationshipType.COMPOSITION,
                description="Missions organize Goals around common aims"
            ),
            SemanticRelationship(
                source="Goal",
                target="Objective",
                relationship_type=SemanticRelationshipType.COMPOSITION,
                description="Goals organize Objectives as intermediate targets"
            ),
            SemanticRelationship(
                source="Objective",
                target="Task",
                relationship_type=SemanticRelationshipType.COMPOSITION,
                description="Objectives decompose into executable Tasks"
            ),
            
            # Goal contribution relationships
            SemanticRelationship(
                source="Goal",
                target="Mission",
                relationship_type=SemanticRelationshipType.CONTRIBUTES_TO,
                description="Goals contribute toward Missions"
            ),
            SemanticRelationship(
                source="Objective",
                target="Goal",
                relationship_type=SemanticRelationshipType.CONTRIBUTES_TO,
                description="Objectives contribute toward Goals"
            ),
            SemanticRelationship(
                source="Task",
                target="Objective",
                relationship_type=SemanticRelationshipType.CONTRIBUTES_TO,
                description="Tasks contribute toward Objectives"
            ),
            
            # Lifecycle relationships
            SemanticRelationship(
                source="Intent",
                target="Orientation",
                relationship_type=SemanticRelationshipType.INFLUENCE,
                description="Intent establishes orientation through commitment"
            ),
            SemanticRelationship(
                source="Commitment",
                target="Continuation",
                relationship_type=SemanticRelationshipType.CONTINUATION,
                description="Commitment enables continuation across episodes"
            ),
            SemanticRelationship(
                source="Interruption",
                target="Suspension",
                relationship_type=SemanticRelationshipType.TRANSITION,
                description="Interruption creates suspended state for potential restoration"
            ),
            SemanticRelationship(
                source="Restoration",
                target="Continuation",
                relationship_type=SemanticRelationshipType.CONTINUATION,
                description="Restoration enables continuation after interruption"
            ),
            
            # Constraint relationships
            SemanticRelationship(
                source="Constraint",
                target="Orientation",
                relationship_type=SemanticRelationshipType.CONSTRAINT,
                description="Constraints influence what orientation can achieve"
            ),
            SemanticRelationship(
                source="Dependency",
                target="Task",
                relationship_type=SemanticRelationshipType.REQUIREMENT,
                description="Tasks may depend on other tasks or objectives"
            ),
            
            # Evaluation relationships
            SemanticRelationship(
                source="Priority",
                target="Goal",
                relationship_type=SemanticRelationshipType.EVALUATES,
                description="Priority determines goal selection order"
            ),
            SemanticRelationship(
                source="Progress",
                target="Goal",
                relationship_type=SemanticRelationshipType.ACHIEVES,
                description="Progress measures advancement toward goal achievement"
            ),
            SemanticRelationship(
                source="Completion",
                target="Goal",
                relationship_type=SemanticRelationshipType.ACHIEVES,
                description="Completion indicates semantic satisfaction of goal"
            ),
            SemanticRelationship(
                source="Alignment",
                target="Goal",
                relationship_type=SemanticRelationshipType.EVALUATES,
                description="Alignment evaluates consistency with other goals"
            ),
            SemanticRelationship(
                source="Confidence",
                target="Goal",
                relationship_type=SemanticRelationshipType.EVALUATES,
                description="Confidence expresses belief in goal achievement"
            ),
            SemanticRelationship(
                source="Risk",
                target="Goal",
                relationship_type=SemanticRelationshipType.CONSTRAINT,
                description="Risk assesses threats to goal achievement"
            ),
        )
    
    # =============================================================================
    # SEMANTIC DIMENSIONS
    # =============================================================================

    def get_orientation_dimensions(self) -> tuple[ConceptDefinition, ...]:
        """Return the orientation semantic dimensions."""
        return (
            ConceptDefinition(
                name="Goal Orientation",
                definition=(
                    "Orientation toward one or more active Goals. "
                    "Goals remain externally owned."
                ),
                domain="orientation_dimension",
                hierarchy_level=1
            ),
            ConceptDefinition(
                name="Objective Orientation",
                definition=(
                    "Orientation toward operational objectives contributing to active Goals. "
                    "Objectives remain externally authoritative."
                ),
                domain="orientation_dimension",
                hierarchy_level=2
            ),
            ConceptDefinition(
                name="Task Orientation",
                definition=(
                    "Orientation toward executable Tasks derived from objectives. "
                    "Tasks remain externally owned."
                ),
                domain="orientation_dimension",
                hierarchy_level=3
            ),
            ConceptDefinition(
                name="Mission Orientation",
                definition=(
                    "Orientation toward overarching Missions. "
                    "Missions provide semantic cohesion across Goal systems."
                ),
                domain="orientation_dimension",
                hierarchy_level=1
            ),
            ConceptDefinition(
                name="Context Orientation",
                definition=(
                    "The semantic relationship between orientation and its surrounding cognitive context. "
                    "Context influences but does not own orientation."
                ),
                domain="orientation_dimension",
                hierarchy_level=0
            ),
            ConceptDefinition(
                name="Constraint Orientation",
                definition=(
                    "Awareness of limitations affecting current orientation. "
                    "Constraints remain externally authoritative."
                ),
                domain="orientation_dimension",
                hierarchy_level=1
            ),
            ConceptDefinition(
                name="Temporal Orientation",
                definition=(
                    "Orientation with respect to time. Includes horizon, urgency, and timing."
                ),
                domain="orientation_dimension",
                hierarchy_level=0
            ),
            ConceptDefinition(
                name="Environmental Orientation",
                definition=(
                    "Orientation toward external entities and conditions in the environment."
                ),
                domain="orientation_dimension",
                hierarchy_level=1
            ),
            ConceptDefinition(
                name="Strategic Orientation",
                definition=(
                    "Orientation toward long-term strategy and high-level goals."
                ),
                domain="orientation_dimension",
                hierarchy_level=0
            ),
            ConceptDefinition(
                name="Operational Orientation",
                definition=(
                    "Orientation toward immediate tasks and operational objectives."
                ),
                domain="orientation_dimension",
                hierarchy_level=1
            ),
            ConceptDefinition(
                name="Social Orientation",
                definition=(
                    "Orientation toward other agents, collaborators, or stakeholders."
                ),
                domain="orientation_dimension",
                hierarchy_level=0
            ),
        )


# Singleton instance of the vocabulary
CANONICAL_VOCABULARY = Vocabulary()

__all__ = [
    # Concept definitions
    "ConceptDefinition",
    
    # Relationship types
    "SemanticRelationshipType",
    
    # Relationships
    "SemanticRelationship",
    
    # Vocabulary
    "Vocabulary",
    "CANONICAL_VOCABULARY",
]