# Creative Trace - Phase 7.33
# ==========================

"""
Canonical Creative Trace.

Every Creative Session produces a trace containing:
- Concept synthesis history
- Exploration history
- Invented concepts
- Search branches
- Validation results
- Diagnostics

Trace remains inspectable for transparency and debugging.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CreativeTrace:
    """
    Represents the trace of a creative session.
    
    A trace includes:
        - Complete creative history
        - Creativity graph (relationships between concepts)
        - Diagnostic information
    
    Traces remain inspectable for transparency and debugging.
    """
    
    # Identity
    trace_id: str                           # Unique trace identifier
    semantic_identity: str                  # Semantic identity
    
    # Creative history (ordered sequence of events)
    creative_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Creativity graph (concept relationships)
    creativity_graph: Dict[str, List[str]] = field(default_factory=dict)  # node -> neighbors
    
    # Diagnostics
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def history_length(self) -> int:
        """Return number of events in creative history."""
        return len(self.creative_history)
    
    @property
    def is_completed(self) -> bool:
        """Check if trace is complete."""
        return self.completed_at_utc is not None
    
    def add_event(self, event_type: str, payload: Dict[str, Any]) -> CreativeTrace:
        """Add an event to the creative history."""
        event = {
            "event_id": f"event:{uuid.uuid4().hex[:8]}",
            "event_type": event_type,
            "timestamp_utc": time.time(),
            **payload,
        }
        return dataclass_replace(
            self,
            creative_history=list(self.creative_history) + [event],
        )
    
    def add_graph_edge(self, from_node: str, to_node: str) -> CreativeTrace:
        """Add an edge to the creativity graph."""
        new_graph = dict(self.creativity_graph)
        if from_node not in new_graph:
            new_graph[from_node] = []
        if to_node not in new_graph.get(from_node, []):
            new_graph[from_node].append(to_node)
        return dataclass_replace(
            self,
            creativity_graph=new_graph,
        )
    
    def add_diagnostic(self, diagnostic_type: str, details: Dict[str, Any]) -> CreativeTrace:
        """Add a diagnostic entry."""
        diag = {
            "diagnostic_id": f"diag:{uuid.uuid4().hex[:8]}",
            "diagnostic_type": diagnostic_type,
            "timestamp_utc": time.time(),
            **details,
        }
        return dataclass_replace(
            self,
            diagnostics=list(self.diagnostics) + [diag],
        )
    
    def complete(self) -> CreativeTrace:
        """Mark trace as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeTrace",
]