# Chronology - Phase 7.8
# ======================

"""
Canonical Chronology Construction.

Chronology construction converts events into temporal orderings and builds
chronology graphs for reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto

# Import for type references (circular dependency is acceptable at runtime)
try:
    from .event_set import EventSet
except ImportError:
    pass


class TemporalRelationType(Enum):
    """Types of temporal relations between events."""
    
    BEFORE = "before"                       # Event A occurs before event B
    AFTER = "after"                         # Event A occurs after event B
    DURING = "during"                       # Event A is during event B
    OVERLAPS = "overlaps"                   # Event A overlaps with event B
    STARTS = "starts"                       # Event A starts at the same time as event B
    FINISHES = "finishes"                   # Event A finishes at the same time as event B
    MEETS = "meets"                         # Event A ends when event B starts
    CONTAINS = "contains"                   # Event A contains event B
    EQUALS = "equals"                       # Events are temporally equal
    DISJOINT = "disjoint"                   # Events do not overlap in any way


class ChronologyState(Enum):
    """Chronology construction states."""
    
    BUILDING = "building"
    ORDERING = "ordering"
    VALIDATING = "validating"
    COMPLETE = "complete"


@dataclass(frozen=True)
class TemporalRelation:
    """
    Temporal relation between two events.
    
    Every temporal relation references explicit participating events and
    preserves provenance of the inference.
    """
    
    # Identity
    relation_id: str                        # Unique relation identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Participating events
    source_event_id: str                    # First event in relation
    target_event_id: str                    # Second event in relation
    
    # Relation type
    relation_type: TemporalRelationType     # What kind of temporal relation?
    
    # Confidence and provenance
    confidence: float = 1.0                 # Certainty (0.0 to 1.0)
    inference_rule: Optional[str] = None    # Rule used for this inference
    
    # Provenance
    source_relation_id: Optional[str] = None   # If derived from another relation
    origin_system: str = "unknown"              # Where did the relation originate?
    
    @property
    def is_confirmed(self) -> bool:
        """Check if relation has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def is_inferred(self) -> bool:
        """Check if this relation was inferred (not directly observed)."""
        return self.inference_rule is not None
    
    def invert(self) -> TemporalRelation:
        """Return the inverse of this relation."""
        inverse_map = {
            TemporalRelationType.BEFORE: TemporalRelationType.AFTER,
            TemporalRelationType.AFTER: TemporalRelationType.BEFORE,
            TemporalRelationType.DURING: TemporalRelationType.CONTAINS,
            TemporalRelationType.OVERLAPS: TemporalRelationType.OVERLAPS,
            TemporalRelationType.STARTS: TemporalRelationType.FINISHES,
            TemporalRelationType.FINISHES: TemporalRelationType.STARTS,
            TemporalRelationType.MEETS: TemporalRelationType.MEETS,
            TemporalRelationType.CONTAINS: TemporalRelationType.DURING,
            TemporalRelationType.EQUALS: TemporalRelationType.EQUALS,
            TemporalRelationType.DISJOINT: TemporalRelationType.DISJOINT,
        }
        return dataclass_replace(
            self,
            relation_type=inverse_map.get(self.relation_type, TemporalRelationType.EQUALS),
            source_event_id=self.target_event_id,
            target_event_id=self.source_event_id,
        )
    
    def conflicts_with(self, other: TemporalRelation) -> bool:
        """Check if this relation conflicts with another."""
        if self.source_event_id != other.source_event_id or self.target_event_id != other.target_event_id:
            return False
        
        conflict_pairs = {
            (TemporalRelationType.BEFORE, TemporalRelationType.AFTER),
            (TemporalRelationType.AFTER, TemporalRelationType.BEFORE),
            (TemporalRelationType.DURING, TemporalRelationType.CONTAINS),
            (TemporalRelationType.STARTS, TemporalRelationType.FINISHES),
        }
        
        pair = (self.relation_type, other.relation_type)
        return pair in conflict_pairs or pair[::-1] in conflict_pairs


@dataclass(frozen=True)
class ChronologyGraph:
    """
    Graph representation of temporal chronology.
    
    Nodes represent events. Edges represent temporal relations.
    """
    
    # Identity
    graph_id: str                           # Unique graph identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Graph structure
    event_nodes: Tuple[str, ...]            # Node IDs (event IDs)
    relation_edges: Tuple[TemporalRelation, ...]  # Edges representing relations
    
    # Temporal ordering derived from graph
    ordered_event_ids: Optional[Tuple[str, ...]] = None  # Topological sort order if acyclic
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def node_count(self) -> int:
        """Return the number of nodes in this graph."""
        return len(self.event_nodes)
    
    @property
    def edge_count(self) -> int:
        """Return the number of edges in this graph."""
        return len(self.relation_edges)
    
    def get_successors(self, event_id: str) -> Tuple[str, ...]:
        """Get events that occur after the given event."""
        successors = []
        for relation in self.relation_edges:
            if relation.source_event_id == event_id and relation.relation_type in (
                TemporalRelationType.BEFORE,
                TemporalRelationType.AFTER,
            ):
                target = relation.target_event_id
                if target != event_id and target not in successors:
                    successors.append(target)
        return tuple(successors)
    
    def get_predecessors(self, event_id: str) -> Tuple[str, ...]:
        """Get events that occur before the given event."""
        predecessors = []
        for relation in self.relation_edges:
            if relation.target_event_id == event_id and relation.relation_type in (
                TemporalRelationType.BEFORE,
                TemporalRelationType.AFTER,
            ):
                source = relation.source_event_id
                if source != event_id and source not in predecessors:
                    predecessors.append(source)
        return tuple(predecessors)
    
    def has_cycle(self) -> bool:
        """Check if the chronology graph contains a cycle."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for successor in self.get_successors(node):
                if successor not in visited:
                    if dfs(successor):
                        return True
                elif successor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.event_nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False
    
    def topological_sort(self) -> Optional[Tuple[str, ...]]:
        """Return a topological ordering of events, or None if cyclic."""
        if self.has_cycle():
            return None
        
        in_degree: Dict[str, int] = {node: 0 for node in self.event_nodes}
        for relation in self.relation_edges:
            if relation.relation_type == TemporalRelationType.BEFORE:
                target = relation.target_event_id
                if target in in_degree:
                    in_degree[target] += 1
        
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for successor in self.get_successors(node):
                if successor in in_degree:
                    in_degree[successor] -= 1
                    if in_degree[successor] == 0:
                        queue.append(successor)
        
        return tuple(result) if len(result) == len(self.event_nodes) else None


@dataclass(frozen=True)
class ChronologyConstruction:
    """
    Result of chronology construction from an event set.
    
    Canonical chronology construction flow:
        Events -> Temporal Ordering -> Dependency Analysis -> 
        Chronology Graph -> Consistency Validation -> Publication
    """
    
    # Identity
    construction_id: str                    # Unique construction identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Input
    input_event_set_id: Optional[str] = None   # Event set that was processed
    
    # Output
    chronology_graph: ChronologyGraph         # Resulting chronology graph
    
    # Ordering strategy used
    ordering_strategy: str = "timestamp_based"  # e.g., "timestamp_based", "constraint_propagation"
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()         # Notes about the construction process
    validation_errors: Tuple[str, ...] = ()    # Any validation errors encountered
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_construction_id: Optional[str] = None  # If derived from another construction
    origin_context: str = "unknown"               # Where did the construction originate?
    
    @property
    def is_consistent(self) -> bool:
        """Check if the constructed chronology is consistent (acyclic)."""
        return not self.chronology_graph.has_cycle()
    
    @property
    def ordered_events(self) -> Optional[Tuple[str, ...]]:
        """Return events in chronological order, or None if cyclic."""
        return self.chronology_graph.topological_sort()
    
    @classmethod
    def from_event_set(cls, event_set: EventSet) -> ChronologyConstruction:
        """
        Build a chronology construction from an event set.
        
        Uses timestamp-based ordering as the primary strategy.
        """
        # Build relation edges based on timestamps
        relations = []
        ordered_events = event_set.get_ordered_events()
        
        for i, event1 in enumerate(ordered_events):
            for event2 in ordered_events[i+1:]:
                if event1.strictly_before(event2):
                    relations.append(TemporalRelation(
                        relation_id=f"relation:{uuid.uuid4().hex[:8]}",
                        semantic_identity=f"{event1.event_id}:{event2.event_id}",
                        source_event_id=event1.event_id,
                        target_event_id=event2.event_id,
                        relation_type=TemporalRelationType.BEFORE,
                        confidence=0.95,
                        inference_rule="timestamp_ordering",
                    ))
                elif event2.strictly_before(event1):
                    relations.append(TemporalRelation(
                        relation_id=f"relation:{uuid.uuid4().hex[:8]}",
                        semantic_identity=f"{event2.event_id}:{event1.event_id}",
                        source_event_id=event2.event_id,
                        target_event_id=event1.event_id,
                        relation_type=TemporalRelationType.BEFORE,
                        confidence=0.95,
                        inference_rule="timestamp_ordering",
                    ))
        
        # Check for overlapping events
        for i, event1 in enumerate(ordered_events):
            for event2 in ordered_events[i+1:]:
                if event1.overlaps_with(event2) and not event1.strictly_before(event2) and not event2.strictly_before(event1):
                    relations.append(TemporalRelation(
                        relation_id=f"relation:{uuid.uuid4().hex[:8]}",
                        semantic_identity=f"{event1.event_id}:{event2.event_id}",
                        source_event_id=event1.event_id,
                        target_event_id=event2.event_id,
                        relation_type=TemporalRelationType.OVERLAPS,
                        confidence=0.9,
                        inference_rule="overlap_detection",
                    ))
        
        graph = ChronologyGraph(
            graph_id=f"chronology:{uuid.uuid4().hex[:16]}",
            semantic_identity=event_set.semantic_identity,
            event_nodes=tuple(event.event_id for event in ordered_events),
            relation_edges=tuple(relations),
        )
        
        return cls(
            construction_id=f"construction:{uuid.uuid4().hex[:16]}",
            semantic_identity=event_set.semantic_identity,
            input_event_set_id=event_set.event_set_id,
            chronology_graph=graph,
            ordering_strategy="timestamp_based",
        )


@dataclass(frozen=True)
class ChronologyIdentity:
    """
    Immutable identity for a chronology.
    
    Allows replay and verification of chronology construction results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Context
    chronology_number: int = 1                # For repeated constructions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, chronology_number: int = 1) -> ChronologyIdentity:
        """Create a new chronology identity."""
        return cls(
            semantic_identity=semantic_identity,
            chronology_number=chronology_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TemporalRelation",
    "ChronologyGraph",
    "ChronologyConstruction",
    "ChronologyIdentity",
    "TemporalRelationType",
    "ChronologyState",
]