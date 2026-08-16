# Oriented Network Semantic Relationships
# ======================================

"""
Semantic Relationship Graph for the Oriented Network (Phase 4.7.2)

This module defines the complete semantic relationship graph that connects
all concepts in the Oriented Network's ontology.

SEMANTIC RELATIONSHIP TYPES:
    - ownership: Concept A owns or controls concept B
    - reference: Concept A points to concept B (without ownership)
    - inheritance: Subtype relationship in semantic hierarchy
    - composition: Whole-part relationship
    - dependency: One concept requires another for completion
    - influence: A affects but does not determine B
    - constraint: B is limited or conditioned by A
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# RELATIONSHIP ROLE TYPES
# =============================================================================

@dataclass(frozen=True)
class SemanticRelationshipRole:
    """A role in a semantic relationship."""
    name: str
    """The canonical name of the role"""
    
    description: str
    """Description of what this role entails"""
    
    direction: str = "source-to-target"
    """Directionality of the role (source-to-target, target-to-source, bidirectional)"""


# =============================================================================
# COMPOSITE RELATIONSHIP DEFINITION
# =============================================================================

@dataclass(frozen=True)
class SemanticRelationshipGraph:
    """
    The complete semantic relationship graph for the Oriented Network.
    
    This graph defines all relationships between concepts in the ontology.
    Every relationship has an explicit type and direction.
    """
    
    # =============================================================================
    # ORIENTATION RELATIONSHIPS
    # =============================================================================
    
    def get_orientation_relationships(self) -> tuple[dict, ...]:
        """Return orientation's relationships with other concepts."""
        return (
            {
                "source": "Orientation",
                "target": "Goal",
                "relationship_type": "references",
                "role": "intentional_target",
                "cardinality": "one-to-many"
            },
            {
                "source": "Orientation",
                "target": "Objective",
                "relationship_type": "references",
                "role": "operational_target",
                "cardinality": "one-to-many"
            },
            {
                "source": "Orientation",
                "target": "Task",
                "relationship_type": "references",
                "role": "executable_unit",
                "cardinality": "one-to-many"
            },
            {
                "source": "Orientation",
                "target": "Constraint",
                "relationship_type": "influences",
                "role": "boundary_condition",
                "cardinality": "many-to-one"
            },
            {
                "source": "Orientation",
                "target": "Context",
                "relationship_type": "contextualizes",
                "role": "semantic_environment",
                "cardinality": "one-to-many"
            },
        )
    
    # =============================================================================
    # HIERARCHY RELATIONSHIPS
    # =============================================================================
    
    def get_hierarchy_relationships(self) -> tuple[dict, ...]:
        """Return semantic hierarchy relationships."""
        return (
            {
                "source": "Purpose",
                "target": "Mission",
                "relationship_type": "organizes",
                "role": "higher_level_aim",
                "cardinality": "one-to-many"
            },
            {
                "source": "Mission",
                "target": "Goal",
                "relationship_type": "organizes",
                "role": "goal_container",
                "cardinality": "one-to-many"
            },
            {
                "source": "Goal",
                "target": "Objective",
                "relationship_type": "decomposes_to",
                "role": "parent_goal",
                "cardinality": "one-to-many"
            },
            {
                "source": "Objective",
                "target": "Task",
                "relationship_type": "derives_into",
                "role": "parent_objective",
                "cardinality": "one-to-many"
            },
        )
    
    # =============================================================================
    # CONTRIBUTION RELATIONSHIPS
    # =============================================================================
    
    def get_contribution_relationships(self) -> tuple[dict, ...]:
        """Return contribution relationships ( Goals → Missions, etc.)"""
        return (
            {
                "source": "Goal",
                "target": "Mission",
                "relationship_type": "contributes_to",
                "role": "contributing_goal",
                "cardinality": "many-to-one"
            },
            {
                "source": "Objective",
                "target": "Goal",
                "relationship_type": "contributes_to",
                "role": "contributing_objective",
                "cardinality": "many-to-one"
            },
            {
                "source": "Task",
                "target": "Objective",
                "relationship_type": "contributes_to",
                "role": "contributing_task",
                "cardinality": "many-to-one"
            },
        )
    
    # =============================================================================
    # LIFECYCLE RELATIONSHIPS
    # =============================================================================
    
    def get_lifecycle_relationships(self) -> tuple[dict, ...]:
        """Return lifecycle-related relationships."""
        return (
            {
                "source": "Intent",
                "target": "Orientation",
                "relationship_type": "establishes",
                "role": "originator",
                "cardinality": "one-to-one"
            },
            {
                "source": "Commitment",
                "target": "Continuation",
                "relationship_type": "enables",
                "role": "semantic_strengthening",
                "cardinality": "one-to-many"
            },
            {
                "source": "Interruption",
                "target": "Suspension",
                "relationship_type": "creates",
                "role": "introducing_state",
                "cardinality": "one-to-one"
            },
            {
                "source": "Restoration",
                "target": "Continuation",
                "relationship_type": "resumes",
                "role": "continuation_recovery",
                "cardinality": "one-to-many"
            },
        )
    
    # =============================================================================
    # EVALUATION RELATIONSHIPS
    # =============================================================================
    
    def get_evaluation_relationships(self) -> tuple[dict, ...]:
        """Return evaluation-related relationships."""
        return (
            {
                "source": "Priority",
                "target": "Goal",
                "relationship_type": "evaluates",
                "role": "importance_assessment",
                "cardinality": "many-to-one"
            },
            {
                "source": "Progress",
                "target": "Goal",
                "relationship_type": "measures",
                "role": "semantic_advancement",
                "cardinality": "one-to-many"
            },
            {
                "source": "Completion",
                "target": "Goal",
                "relationship_type": "satisfies",
                "role": "fulfillment_indicator",
                "cardinality": "many-to-one"
            },
            {
                "source": "Alignment",
                "target": "Goal",
                "relationship_type": "evaluates",
                "role": "consistency_check",
                "cardinality": "many-to-one"
            },
            {
                "source": "Confidence",
                "target": "Goal",
                "relationship_type": "expresses",
                "role": "belief_assessment",
                "cardinality": "one-to-many"
            },
            {
                "source": "Risk",
                "target": "Goal",
                "relationship_type": "assesses",
                "role": "threat_analysis",
                "cardinality": "many-to-one"
            },
        )
    
    # =============================================================================
    # ALL RELATIONSHIPS
    # =============================================================================
    
    def get_all_relationships(self) -> tuple[dict, ...]:
        """Return all relationships in the graph."""
        return (
            self.get_orientation_relationships() +
            self.get_hierarchy_relationships() +
            self.get_contribution_relationships() +
            self.get_lifecycle_relationships() +
            self.get_evaluation_relationships()
        )


# Singleton instance of the relationship graph
RELATIONSHIP_GRAPH = SemanticRelationshipGraph()

__all__ = [
    "SemanticRelationshipRole",
    "SemanticRelationshipGraph",
    "RELATIONSHIP_GRAPH",
]