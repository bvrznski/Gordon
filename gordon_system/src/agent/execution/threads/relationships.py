# Thread Relationships Model
# ===========================

"""
Thread relationship model for parent-child delegation.

A Thread may have relationships with other Threads, most commonly:
    - Parent-child: Thread delegates work to a child and awaits its completion
    - Sibling: Related threads working on parts of the same objective

Relationships must:
    - Be explicit (no implicit dependencies)
    - Prevent cycles (parent cannot be ancestor of child)
    - Support provenance tracking
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum


class RelationshipKind(Enum):
    """
    Kinds of thread relationships.
    
    - DELEGATION: Parent delegates work to child, awaits completion
    - COLLABORATION: Siblings working together on shared objective
    - MONITORING: Thread monitors another thread's progress
    - REFERENCE: Non-authoritative reference to another thread
    """
    
    DELEGATION = "delegation"       # Parent → Child (awaiting result)
    COLLABORATION = "collaboration"  # Sibling collaboration
    MONITORING = "monitoring"        # Watch another thread's state
    REFERENCE = "reference"          # Non-binding reference


@dataclass(frozen=True)
class ThreadRelationship:
    """
    A relationship between two Threads.
    
    This is an immutable artifact that describes the relationship at a point
    in time. Actual runtime behavior follows from this semantic contract.
    """
    
    # Identifiers
    source_thread_id: str  # Who initiated/owns the relationship?
    target_thread_id: str  # Who is the other party?
    
    # Relationship type
    kind: RelationshipKind
    
    # Metadata
    created_at_utc: float = field(default_factory=lambda: 0.0)
    status: str = "active"  # active, completed, terminated, expired
    
    # Contract details (for delegation specifically)
    expected_outcome: Optional[str] = None  # What outcome is expected?
    
    def __hash__(self) -> int:
        return hash((self.source_thread_id, self.target_thread_id, self.kind))


@dataclass(frozen=True)
class ParentChildRelationship:
    """
    A parent-child delegation relationship between threads.
    
    This represents the canonical case where a Thread delegates work to
    another Thread and awaits its completion.
    
    Invariants:
        PC-001: Child cannot be ancestor of parent (no cycles)
        PC-002: Parent must be in DELEGATED state while child is active
        PC-003: Child completion triggers parent completion or transition
    """
    
    # Identifiers
    parent_thread_id: str
    child_thread_id: str
    
    # Creation metadata
    created_at_utc: float = field(default_factory=lambda: 0.0)
    delegated_by: Optional[str] = None
    
    # Expected outcome contract
    expected_outcome_description: Optional[str] = None
    
    # Status tracking
    child_status: str = "pending"  # pending, active, completed, failed, terminated
    parent_awaiting_child: bool = True
    
    # Completion info
    child_completed_at_utc: Optional[float] = None
    child_completion_reason: Optional[str] = None
    
    def is_active(self) -> bool:
        """Check if the relationship is still active (child not finished)."""
        return self.child_status in ("pending", "active")
    
    def to_child_terminated(self, reason: str) -> "ParentChildRelationship":
        """Return a new relationship with child marked as terminated."""
        return dataclass_replace(
            self,
            child_status="terminated",
            child_completed_at_utc=0.0,
            child_completion_reason=reason,
        )
    
    def to_child_completed(self, result: Optional[str] = None) -> "ParentChildRelationship":
        """Return a new relationship with child marked as completed."""
        return dataclass_replace(
            self,
            child_status="completed",
            child_completed_at_utc=0.0,
            child_completion_reason=result or "purpose_fulfilled",
        )


@dataclass(frozen=True)
class ThreadRelationshipGraph:
    """
    Graph of relationships between Threads.
    
    Provides methods to query and validate relationship sets.
    """
    
    # Relationships: (source_id, target_id) -> Relationship
    _relationships: Dict[tuple, ThreadRelationship] = field(
        default_factory=dict,
        init=False,
    )
    
    def __init__(self) -> None:
        """Initialize empty relationship graph."""
        object.__setattr__(self, "_relationships", {})
    
    def add_relationship(self, rel: ThreadRelationship) -> bool:
        """
        Add a relationship to the graph.
        
        Returns True if added, False if duplicate or invalid.
        """
        key = (rel.source_thread_id, rel.target_thread_id)
        if key in self._relationships:
            return False
        
        # Check for cycles (PC-001: no cycles)
        if self._would_create_cycle(rel):
            return False
        
        relationships = dict(self._relationships)
        relationships[key] = rel
        object.__setattr__(self, "_relationships", relationships)
        return True
    
    def get_relationships_for_thread(
        self, thread_id: str, kind: Optional[RelationshipKind] = None
    ) -> List[ThreadRelationship]:
        """Get all relationships for a thread (as source)."""
        results = []
        for key, rel in self._relationships.items():
            if key[0] == thread_id and (kind is None or rel.kind == kind):
                results.append(rel)
        return results
    
    def get_child_threads(self, parent_thread_id: str) -> List[str]:
        """Get all child threads of a parent."""
        children = []
        for key, rel in self._relationships.items():
            if key[0] == parent_thread_id and rel.kind == RelationshipKind.DELEGATION:
                children.append(key[1])
        return children
    
    def get_parent_threads(self, child_thread_id: str) -> List[str]:
        """Get all parent threads of a child."""
        parents = []
        for key, rel in self._relationships.items():
            if key[1] == child_thread_id and rel.kind == RelationshipKind.DELEGATION:
                parents.append(key[0])
        return parents
    
    def _would_create_cycle(self, new_rel: ThreadRelationship) -> bool:
        """Check if adding this relationship would create a cycle."""
        # BFS from target back to source
        visited: Set[str] = set()
        queue = [new_rel.source_thread_id]
        
        while queue:
            current = queue.pop(0)
            if current == new_rel.target_thread_id:
                return True  # Cycle found!
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Find outgoing delegation relationships
            for key, rel in self._relationships.items():
                if (
                    key[0] == current
                    and rel.kind == RelationshipKind.DELEGATION
                    and key[1] not in visited
                ):
                    queue.append(key[1])
        
        return False
    
    def has_cycle(self) -> bool:
        """Check if the entire graph contains any cycles."""
        # Check each relationship for cycle potential
        for rel in self._relationships.values():
            if self._would_create_cycle(rel):
                return True
        return False


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


@dataclass(frozen=True)
class ThreadRelationshipSnapshot:
    """
    Immutable snapshot of thread relationships at a point in time.
    
    Used for persistence and recovery of relationship state.
    """
    
    parent_child_relationships: Tuple[ParentChildRelationship, ...] = ()
    other_relationships: Tuple[ThreadRelationship, ...] = ()
    
    @classmethod
    def empty(cls) -> "ThreadRelationshipSnapshot":
        """Create an empty snapshot."""
        return cls()
    
    @classmethod
    def with_parent_child(
        cls, relationships: List[ParentChildRelationship]
    ) -> "ThreadRelationshipSnapshot":
        """Create a snapshot with parent-child relationships."""
        return cls(parent_child_relationships=tuple(relationships))


__all__ = [
    "RelationshipKind",
    "ThreadRelationship",
    "ParentChildRelationship",
    "ThreadRelationshipGraph",
    "ThreadRelationshipSnapshot",
]