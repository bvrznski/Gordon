# Core Causality System
# ======================
"""
Core runtime causality tracking.

Provides:
- Causal event ordering beyond correlation
- Event dependency chains
- Temporal constraints for causality
- Causality verification

Phase 3.7: Runtime third-stage expansion - Causality subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import time


# =============================================================================
# Causal Event
# =============================================================================

class CausalEventType(Enum):
    """
    Types of causally-related events in the runtime.
    
    - ENTITY_CREATED: Entity instance creation
    - STATE_CHANGED: Entity state transition
    - TASK_SUBMITTED: Task submission to scheduler
    - TASK_STARTED: Task execution started
    - TASK_COMPLETED: Task execution completed
    - TASK_FAILED: Task execution failed
    - DEPENDENCY_RESOLVED: Dependency satisfied
    - RESOURCE_ACQUIRED: Resource allocated
    - RESOURCE_RELEASED: Resource freed
    """
    
    ENTITY_CREATED = "entity_created"
    STATE_CHANGED = "state_changed"
    TASK_SUBMITTED = "task_submitted"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DEPENDENCY_RESOLVED = "dependency_resolved"
    RESOURCE_ACQUIRED = "resource_acquired"
    RESOURCE_RELEASED = "resource_released"


@dataclass(frozen=True)
class CausalEvent:
    """
    An event with causal relationships to other events.
    
    Events can have multiple causes and effects, forming a DAG.
    
    Usage:
        event = CausalEvent(
            event_id=event_id,
            event_type=CausalEventType.TASK_COMPLETED,
            timestamp=time.time(),
            cause_ids=[task_started_id],
            effect_ids=[]
        )
    """
    
    event_id: str
    
    # Event information
    event_type: CausalEventType
    timestamp: float  # Monotonic time
    
    # Causality links
    cause_ids: List[str] = field(default_factory=list)  # Events this depends on
    effect_ids: List[str] = field(default_factory=list)  # Events that depend on this
    
    # Context
    entity_id: Optional[str] = None
    task_id: Optional[str] = None
    source_component: str = ""
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_root(self) -> bool:
        """Check if this event has no causes (root of a causal chain)."""
        return len(self.cause_ids) == 0
    
    def add_cause(self, cause_id: str) -> "CausalEvent":
        """Return copy with added cause."""
        new_causes = list(self.cause_ids)
        if cause_id not in new_causes:
            new_causes.append(cause_id)
        
        return CausalEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            timestamp=self.timestamp,
            cause_ids=new_causes,
            effect_ids=list(self.effect_ids),
            entity_id=self.entity_id,
            task_id=self.task_id,
            source_component=self.source_component,
            payload=dict(self.payload)
        )
    
    def add_effect(self, effect_id: str) -> "CausalEvent":
        """Return copy with added effect."""
        new_effects = list(self.effect_ids)
        if effect_id not in new_effects:
            new_effects.append(effect_id)
        
        return CausalEvent(
            event_id=self.event_id,
            event_type=self.event_type,
            timestamp=self.timestamp,
            cause_ids=list(self.cause_ids),
            effect_ids=new_effects,
            entity_id=self.entity_id,
            task_id=self.task_id,
            source_component=self.source_component,
            payload=dict(self.payload)
        )


# =============================================================================
# Causal DAG (Directed Acyclic Graph)
# =============================================================================

class CausalDAG:
    """
    Directed acyclic graph of causal events.
    
    Provides:
        - Event insertion with causal links
        - Topological ordering for causal analysis
        - Cycle detection in the causality graph
    
    Usage:
        dag = CausalDAG()
        
        # Add event with dependencies
        dag.add_event(
            event_id="event_2",
            cause_ids=["event_1"]
        )
        
        # Get events in causal order
        ordered = dag.topological_order()
    """
    
    def __init__(self) -> None:
        self._events: Dict[str, CausalEvent] = {}
        self._dependencies: Dict[str, Set[str]] = {}  # event -> causes
        self._dependents: Dict[str, Set[str]] = {}  # event -> effects
        self._lock = __import__("threading").Lock()
    
    def add_event(self, event: CausalEvent) -> bool:
        """
        Add an event to the DAG.
        
        Args:
            event: The causal event to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            # Validate no cycle would be created
            for cause_id in event.cause_ids:
                if self._would_create_cycle(event.event_id, cause_id):
                    raise ValueError(
                        f"Adding {event.event_id} would create a causal cycle"
                    )
            
            self._events[event.event_id] = event
            
            # Record dependencies
            self._dependencies[event.event_id] = set(event.cause_ids)
            for cause_id in event.cause_ids:
                if cause_id not in self._dependents:
                    self._dependents[cause_id] = set()
                self._dependents[cause_id].add(event.event_id)
            
            return True
    
    def _would_create_cycle(self, new_event: str, potential_cause: str) -> bool:
        """Check if adding a dependency would create a cycle."""
        # DFS from cause to see if we can reach the new event
        visited = set()
        
        def dfs(node: str) -> bool:
            if node == new_event:
                return True
            if node in visited:
                return False
            visited.add(node)
            
            for dependent in self._dependents.get(node, set()):
                if dfs(dependent):
                    return True
            return False
        
        return dfs(potential_cause)
    
    def topological_order(self) -> List[str]:
        """
        Get events in topological order (causes before effects).
        
        Returns:
            List of event IDs in causal order
            
        Raises:
            ValueError: If DAG contains a cycle
        """
        with self._lock:
            # Build in-degree count
            in_degree: Dict[str, int] = {}
            
            for event_id in self._events:
                in_degree[event_id] = len(self._dependencies.get(event_id, set()))
            
            # Start with events that have no dependencies
            queue = [eid for eid, deg in in_degree.items() if deg == 0]
            result = []
            
            while queue:
                node = queue.pop(0)
                result.append(node)
                
                # Reduce in-degree of dependents
                for dependent in self._dependents.get(node, set()):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
            
            if len(result) != len(self._events):
                raise ValueError("DAG contains a cycle")
            
            return result
    
    def get_causes(self, event_id: str) -> List[str]:
        """Get direct causes of an event."""
        with self._lock:
            return list(self._dependencies.get(event_id, []))
    
    def get_effects(self, event_id: str) -> List[str]:
        """Get direct effects (dependents) of an event."""
        with self._lock:
            return list(self._dependents.get(event_id, []))
    
    @property
    def event_count(self) -> int:
        """Return number of events in DAG."""
        with self._lock:
            return len(self._events)
    
    @property
    def is_cyclic(self) -> bool:
        """Check if DAG contains a cycle."""
        try:
            self.topological_order()
            return False
        except ValueError:
            return True


# =============================================================================
# Causality Context
# =============================================================================

@dataclass(frozen=True)
class CausalityContext:
    """
    Context for causality tracking in operations.
    
    Usage:
        ctx = CausalityContext.create_from_parent(parent_event_id)
        
        # Run operation with this causal context
        result = await run_operation(causality_context=ctx)
        
        # Record the operation as having caused new events
        ctx.record_effect(new_event_ids)
    """
    
    trace_id: str  # Correlation ID for the causal chain
    
    parent_event_id: Optional[str] = None
    
    event_chain: List[str] = field(default_factory=list)  # Events in this context
    
    timestamp: float = field(default_factory=time.time)
    
    @classmethod
    def create_root(cls, event_id: str, trace_id: str) -> "CausalityContext":
        """Create a root causality context."""
        return cls(
            trace_id=trace_id,
            parent_event_id=None,
            event_chain=[event_id],
            timestamp=time.time()
        )
    
    @classmethod
    def create_from_parent(cls, parent_event_id: str, trace_id: str) -> "CausalityContext":
        """Create a child causality context."""
        return cls(
            trace_id=trace_id,
            parent_event_id=parent_event_id,
            event_chain=[parent_event_id],
            timestamp=time.time()
        )
    
    def with_child(self, child_event_id: str) -> "CausalityContext":
        """Create a child context from this one."""
        return CausalityContext(
            trace_id=self.trace_id,
            parent_event_id=self.event_chain[-1] if self.event_chain else None,
            event_chain=list(self.event_chain) + [child_event_id],
            timestamp=time.time()
        )
    
    @property
    def is_root_context(self) -> bool:
        """Check if this is a root (no parent) context."""
        return self.parent_event_id is None
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "trace_id": self.trace_id,
            "parent_event_id": self.parent_event_id,
            "event_chain_length": len(self.event_chain),
            "timestamp": self.timestamp
        }


__all__ = [
    # Event types
    "CausalEventType",
    
    # Events
    "CausalEvent",
    
    # DAG
    "CausalDAG",
    
    # Context
    "CausalityContext",
]