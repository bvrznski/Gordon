# Oriented Network Conceptual Hierarchy
# =====================================

"""
Conceptual Hierarchy for the Oriented Network (Phase 4.7.2)

This module defines the semantic hierarchy of concepts, establishing
the acyclic ordering from highest-level purposes to executable tasks.

ARCHITECTURAL PRINCIPLES:
    - Semantic hierarchy is strictly acyclic
    - Higher levels provide context and meaning for lower levels
    - Lower levels realize the higher-level intentions
    - No concept may be both ancestor and descendant of another

SEMANTIC HIERARCHY (Top to Bottom):
    
    Purpose (0) - Highest semantic level, ultimate aim
    
        ↓
        
    Mission (1) - Organizes Goals around common aims
        
        ↓
        
    Goal (2) - Actively oriented cognitive target
        
        ↓
        
    Objective (3) - Intermediate target toward goal achievement
        
        ↓
        
    Task (4) - Executable cognitive unit derived from objectives

LIFECYCLE HIERARCHY:
    
    Intent → Orientation → Engagement → Continuation
    
    Interruption → Suspension → Restoration
    
    Commitment enables Continuation across episodes

SEMANTIC LAWS:
    ORIENTED-SEMANTIC-LAW-037: Semantic hierarchy shall remain acyclic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# HIERARCHY LEVELS
# =============================================================================

class HierarchyLevel(Enum):
    """Hierarchy levels from highest (abstract) to lowest (concrete)."""
    
    PURPOSE = 0
    """Ultimate aim, highest level semantic justification"""
    
    MISSION = 1
    """Major orientation organizing related Goals around a common aim"""
    
    GOAL = 2
    """Actively oriented cognitive target requiring specific cognitive work"""
    
    OBJECTIVE = 3
    """Intermediate target contributing to Goal achievement"""
    
    TASK = 4
    """Executable cognitive unit derived from Objectives"""
    
    ORIENTATION_ROOT = 5
    """Orientation and Intent - the root of intentional orientation"""
    
    LIFECYCLE = 6
    """State lifecycle concepts (Continuation, Interruption, etc.)"""
    
    BOUNDARY = 7
    """Boundary concepts (Context, Scope, Horizon)"""
    
    RELATIONSHIP = 8
    """Relationship concepts (Dependency, Requirement, Expectation)"""
    
    EVALUATION = 9
    """Evaluation concepts (Progress, Alignment, Confidence, etc.)"""


@dataclass(frozen=True)
class HierarchyEdge:
    """
    A directed edge in the semantic hierarchy graph.
    
    Represents a "is-a" or "part-of" relationship between concepts.
    """
    parent: str
    """The parent concept in the hierarchy"""
    
    child: str
    """The child concept that inherits from or is part of parent"""
    
    relationship_type: str = "specializes"
    """Type of relationship (specializes, composes, realizes)"""


# =============================================================================
# CANONICAL HIERARCHY
# =============================================================================

@dataclass(frozen=True)
class ConceptualHierarchy:
    """
    The complete conceptual hierarchy for the Oriented Network.
    
    This hierarchy defines all semantic relationships in terms of
    higher-to-lower ordering. The graph is guaranteed to be acyclic.
    """
    
    # =============================================================================
    # MAIN SEMANTIC HIERARCHY (Purpose → Mission → Goal → Objective → Task)
    # =============================================================================
    
    @property
    def main_hierarchy(self) -> tuple[HierarchyEdge, ...]:
        """Return the main semantic hierarchy edges."""
        return (
            HierarchyEdge(
                parent="Purpose",
                child="Mission",
                relationship_type="organizes"
            ),
            HierarchyEdge(
                parent="Mission",
                child="Goal",
                relationship_type="organizes"
            ),
            HierarchyEdge(
                parent="Goal",
                child="Objective",
                relationship_type="decomposes_to"
            ),
            HierarchyEdge(
                parent="Objective",
                child="Task",
                relationship_type="derives_into"
            ),
        )
    
    # =============================================================================
    # LIFECYCLE HIERARCHY
    # =============================================================================
    
    @property
    def lifecycle_hierarchy(self) -> tuple[HierarchyEdge, ...]:
        """Return the lifecycle hierarchy edges."""
        return (
            HierarchyEdge(
                parent="Intent",
                child="Orientation",
                relationship_type="establishes"
            ),
            HierarchyEdge(
                parent="Commitment",
                child="Continuation",
                relationship_type="enables"
            ),
            HierarchyEdge(
                parent="Interruption",
                child="Suspension",
                relationship_type="creates"
            ),
            HierarchyEdge(
                parent="Suspension",
                child="Restoration",
                relationship_type="prepares_for"
            ),
        )
    
    # =============================================================================
    # CONTRIBUTION RELATIONSHIPS (Goals → Missions, etc.)
    # =============================================================================
    
    @property
    def contribution_hierarchy(self) -> tuple[HierarchyEdge, ...]:
        """Return the contribution hierarchy edges."""
        return (
            HierarchyEdge(
                parent="Goal",
                child="Mission",
                relationship_type="contributes_to"
            ),
            HierarchyEdge(
                parent="Objective",
                child="Goal",
                relationship_type="contributes_to"
            ),
            HierarchyEdge(
                parent="Task",
                child="Objective",
                relationship_type="contributes_to"
            ),
        )
    
    # =============================================================================
    # ALL HIERARCHY EDGES
    # =============================================================================
    
    @property
    def all_edges(self) -> tuple[HierarchyEdge, ...]:
        """Return all hierarchy edges."""
        return (
            self.main_hierarchy +
            self.lifecycle_hierarchy +
            self.contribution_hierarchy
        )
    
    # =============================================================================
    # PARENT-CHILD MAPPINGS
    # =============================================================================
    
    def get_children(self, concept: str) -> list[str]:
        """Get all direct children of a concept."""
        children = []
        for edge in self.all_edges:
            if edge.parent == concept:
                children.append(edge.child)
        return children
    
    def get_parent(self, concept: str) -> str | None:
        """Get the parent of a concept, or None if root."""
        for edge in self.all_edges:
            if edge.child == concept:
                return edge.parent
        return None
    
    # =============================================================================
    # DESCENDANTS AND ANCESTORS
    # =============================================================================
    
    def get_descendants(self, concept: str) -> set[str]:
        """Get all descendants (children, grandchildren, etc.) of a concept."""
        descendants = set()
        direct_children = self.get_children(concept)
        
        for child in direct_children:
            descendants.add(child)
            descendants.update(self.get_descendants(child))
        
        return descendants
    
    def get_ancestors(self, concept: str) -> list[str]:
        """Get all ancestors (parent, grandparent, etc.) of a concept."""
        ancestors = []
        parent = self.get_parent(concept)
        
        while parent is not None:
            ancestors.append(parent)
            parent = self.get_parent(parent)
        
        return ancestors
    
    # =============================================================================
    # VALIDATION
    # =============================================================================
    
    def validate_acyclic(self) -> bool:
        """Validate that the hierarchy is acyclic."""
        # For each concept, check if it's an ancestor of itself
        for edge in self.all_edges:
            descendants = self.get_descendants(edge.child)
            if edge.parent in descendants:
                return False
        return True
    
    def get_highest_level(self, concept: str) -> int:
        """Get the highest hierarchy level (0 = Purpose, lowest = most specific)."""
        ancestors = self.get_ancestors(concept)
        
        # Map concepts to levels
        level_map = {
            "Purpose": 0,
            "Mission": 1,
            "Goal": 2,
            "Objective": 3,
            "Task": 4,
        }
        
        if concept in level_map:
            return level_map[concept]
        
        # Find the highest ancestor level
        highest = float('inf')
        for ancestor in ancestors:
            if ancestor in level_map and level_map[ancestor] < highest:
                highest = level_map[ancestor]
        
        return highest if highest != float('inf') else 99


# Singleton instance of the hierarchy
CANONICAL_HIERARCHY = ConceptualHierarchy()

__all__ = [
    # Hierarchy levels
    "HierarchyLevel",
    
    # Edge types
    "HierarchyEdge",
    
    # Hierarchy
    "ConceptualHierarchy",
    "CANONICAL_HIERARCHY",
]