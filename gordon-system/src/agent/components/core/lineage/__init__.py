# Core Lineage System
# ===================
"""
Core runtime entity lineage tracking.

Provides:
- Entity evolution tracking across state transitions
- Ancestry relationships between entity versions
- Branching and merging of entity lineages

Phase 3.7: Runtime third-stage expansion - Lineage subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import time


# =============================================================================
# Lineage Types
# =============================================================================

class LineageType(Enum):
    """
    Types of lineage relationships between entities.
    
    - EVOLUTION: Entity evolved through state changes
    - SIBLING: Entities created from same parent at same time
    - FORK: One entity forked into multiple
    - MERGE: Multiple entities merged into one
    - DERIVATION: Entity derived from another via transformation
    """
    
    EVOLUTION = "evolution"
    SIBLING = "sibling"
    FORK = "fork"
    MERGE = "merge"
    DERIVATION = "derivation"


# =============================================================================
# Lineage Node
# =============================================================================

@dataclass(frozen=True)
class LineageNode:
    """
    A node in an entity's lineage graph.
    
    Represents an entity at a specific point in its lifecycle.
    
    Usage:
        node = LineageNode(
            entity_id=entity_id,
            version=version_num,
            timestamp=time.time(),
            parent_ids=[parent_entity_id]
        )
    """
    
    node_id: str  # Unique identifier for this lineage node
    
    entity_id: str  # The entity being tracked
    version: int  # Version number in the lineage
    
    timestamp: float = field(default_factory=time.time)
    
    # Relationship to parents
    parent_ids: List[str] = field(default_factory=list)  # Parent node IDs
    lineage_type: LineageType = LineageType.EVOLUTION
    
    # State at this point
    state_hash: Optional[str] = None  # Hash of entity state
    
    @property
    def is_root(self) -> bool:
        """Check if this is the first (root) node in a lineage."""
        return len(self.parent_ids) == 0
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        # This would need reverse reference to check properly
        return False  # Placeholder - depends on graph structure
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "node_id": self.node_id,
            "entity_id": self.entity_id,
            "version": self.version,
            "timestamp": self.timestamp,
            "parent_count": len(self.parent_ids),
            "lineage_type": self.lineage_type.value if hasattr(self.lineage_type, 'value') else str(self.lineage_type)
        }


# =============================================================================
# Entity Lineage
# =============================================================================

class EntityLineage:
    """
    Tracks the complete lineage of an entity.
    
    Supports:
        - Evolution tracking through versions
        - Fork/merge operations
        - Branch management
    
    Usage:
        lineage = EntityLineage(entity_id="entity_123")
        
        # Record state change
        node = lineage.record_state_change(
            version=version_num,
            parent_ids=[prev_node_id]
        )
        
        # Get full history
        history = lineage.get_history()
    """
    
    def __init__(self, entity_id: str) -> None:
        self.entity_id = entity_id
        self._nodes: Dict[str, LineageNode] = {}
        self._children: Dict[str, List[str]] = {}  # parent -> children
        self._current_version: int = 0
        self._lock = __import__("threading").Lock()
    
    def record_state_change(
        self,
        version: int,
        parent_ids: Optional[List[str]] = None,
        state_hash: Optional[str] = None
    ) -> LineageNode:
        """
        Record a state change and create a new lineage node.
        
        Args:
            version: New version number
            parent_ids: Parent node IDs (default: latest version)
            state_hash: Hash of the new state
            
        Returns:
            The created LineageNode
        """
        import uuid
        
        with self._lock:
            actual_parents = parent_ids or []
            
            # If no parents specified, use current latest
            if not actual_parents and self._current_version > 0:
                # Find latest node for this entity
                latest = max(
                    (n for n in self._nodes.values() 
                     if n.entity_id == self.entity_id),
                    key=lambda n: n.version,
                    default=None
                )
                if latest:
                    actual_parents = [latest.node_id]
            
            node = LineageNode(
                node_id=f"lineage_{uuid.uuid4().hex[:8]}",
                entity_id=self.entity_id,
                version=version,
                timestamp=time.time(),
                parent_ids=actual_parents,
                state_hash=state_hash
            )
            
            self._nodes[node.node_id] = node
            self._current_version = max(self._current_version, version)
            
            # Record child relationships
            for parent_id in actual_parents:
                if parent_id not in self._children:
                    self._children[parent_id] = []
                self._children[parent_id].append(node.node_id)
            
            return node
    
    def fork(
        self,
        source_version: int,
        new_entity_id: Optional[str] = None
    ) -> LineageNode:
        """
        Fork the lineage from a specific version.
        
        Args:
            source_version: Version to fork from
            new_entity_id: New entity ID (auto-generated if not provided)
            
        Returns:
            The new root node of the forked lineage
        """
        import uuid
        
        with self._lock:
            # Find latest node for this entity
            latest = max(
                (n for n in self._nodes.values() 
                 if n.entity_id == self.entity_id and n.version <= source_version),
                key=lambda n: n.version,
                default=None
            )
            
            parent_ids = [latest.node_id] if latest else []
            
            node = LineageNode(
                node_id=f"lineage_{uuid.uuid4().hex[:8]}",
                entity_id=new_entity_id or f"{self.entity_id}_fork_{time.monotonic_ns()}",
                version=source_version + 1,
                timestamp=time.time(),
                parent_ids=parent_ids,
                lineage_type=LineageType.FORK
            )
            
            self._nodes[node.node_id] = node
            
            if latest:
                if latest.node_id not in self._children:
                    self._children[latest.node_id] = []
                self._children[latest.node_id].append(node.node_id)
            
            return node
    
    def get_history(self, max_versions: Optional[int] = None) -> List[LineageNode]:
        """
        Get the entity's lineage history.
        
        Returns nodes from root to latest (oldest to newest).
        """
        with self._lock:
            nodes_for_entity = [
                n for n in self._nodes.values() if n.entity_id == self.entity_id
            ]
            
            # Sort by version
            nodes_for_entity.sort(key=lambda n: n.version)
            
            if max_versions is not None:
                nodes_for_entity = nodes_for_entity[-max_versions:]
            
            return nodes_for_entity
    
    def get_latest_node(self) -> Optional[LineageNode]:
        """Get the most recent lineage node."""
        history = self.get_history()
        return history[-1] if history else None
    
    @property
    def version_count(self) -> int:
        """Return number of recorded versions."""
        with self._lock:
            return len([n for n in self._nodes.values() 
                       if n.entity_id == self.entity_id])
    
    @property
    def is_forked(self) -> bool:
        """Check if this entity has multiple lineage branches."""
        with self._lock:
            # Count how many children the root node has
            roots = [n for n in self._nodes.values() 
                    if n.entity_id == self.entity_id and n.is_root]
            
            for root in roots:
                children = self._children.get(root.node_id, [])
                if len(children) > 1:
                    return True
            
            return False


# =============================================================================
# Lineage Graph
# =============================================================================

class LineageGraph:
    """
    A graph of all entity lineages in the runtime.
    
    Provides:
        - Global lineage tracking across entities
        - Cross-entity lineage queries
        - Branch analysis
    
    Usage:
        graph = LineageGraph()
        
        # Add lineage for an entity
        graph.add_lineage(lineage)
        
        # Query cross-entity relationships
        siblings = graph.find_siblings(entity_id)
        common_ancestor = graph.find_common_ancestor(entity_a, entity_b)
    """
    
    def __init__(self) -> None:
        self._lineages: Dict[str, EntityLineage] = {}
        self._node_index: Dict[str, LineageNode] = {}  # node_id -> node
        self._lock = __import__("threading").Lock()
    
    def add_lineage(self, lineage: EntityLineage) -> None:
        """Add an entity's lineage to the graph."""
        with self._lock:
            self._lineages[lineage.entity_id] = lineage
            
            for node in lineage.get_history():
                self._node_index[node.node_id] = node
    
    def get_lineage(self, entity_id: str) -> Optional[EntityLineage]:
        """Get the lineage for an entity."""
        return self._lineages.get(entity_id)
    
    def find_siblings(self, entity_id: str) -> List[str]:
        """
        Find sibling entities (share a common parent).
        
        Returns list of entity IDs that share lineage parents.
        """
        with self._lock:
            lineage = self._lineages.get(entity_id)
            if not lineage:
                return []
            
            latest = lineage.get_latest_node()
            if not latest or not latest.parent_ids:
                return []
            
            # Find other entities with the same parent(s)
            siblings = set()
            for other_lineage in self._lineages.values():
                if other_lineage.entity_id == entity_id:
                    continue
                
                other_latest = other_lineage.get_latest_node()
                if other_latest and any(
                    p in latest.parent_ids 
                    for p in other_latest.parent_ids
                ):
                    siblings.add(other_lineage.entity_id)
            
            return list(siblings)
    
    def find_common_ancestor(
        self,
        entity_a: str,
        entity_b: str
    ) -> Optional[LineageNode]:
        """
        Find the most recent common ancestor of two entities.
        
        Returns:
            The common ancestor node, or None if none exists
        """
        lineage_a = self._lineages.get(entity_a)
        lineage_b = self._lineages.get(entity_b)
        
        if not lineage_a or not lineage_b:
            return None
        
        ancestors_a = {n.version for n in lineage_a.get_history()}
        
        for node in reversed(lineage_b.get_history()):
            if node.version in ancestors_a:
                # Return the matching node from lineage A
                for a_node in lineage_a.get_history():
                    if a_node.version == node.version:
                        return a_node
        
        return None
    
    @property
    def entity_count(self) -> int:
        """Return number of tracked entities."""
        with self._lock:
            return len(self._lineages)
    
    @property
    def total_nodes(self) -> int:
        """Return total number of lineage nodes."""
        with self._lock:
            return len(self._node_index)


__all__ = [
    # Lineage types
    "LineageType",
    
    # Nodes and graphs
    "LineageNode",
    "EntityLineage",
    "LineageGraph",
]