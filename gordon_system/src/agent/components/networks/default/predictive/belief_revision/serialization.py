# Canonical Belief Revision Serialization - Phase 4.9.5
# =======================================================
"""
Serialization support for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SerializationResult:
    """
    Result of serialization operation.
    
    Fields:
        success:           Whether serialization succeeded
        serialized_data:   Serialized content (if successful)
        error_message:     Error details (if failed)
        trace:             Trace events
    
    Rules:
        - Deterministic output for deterministic input
        - No runtime references in serialized form
    """
    success: bool = False
    serialized_data: dict[str, Any] | None = None
    error_message: str | None = None
    trace: tuple[str, ...] = field(default_factory=tuple)


class BeliefRevisionSerializer:
    """
    Serializer for belief revision components.
    
    Rules:
        - State-free serialization
        - Deterministic output
        - Round-trip compatible
    """
    
    def __init__(self) -> None:
        self.trace_events: tuple[str, ...] = ()
    
    def serialize_belief(self, belief: dict[str, Any]) -> SerializationResult:
        """
        Serialize a single belief to JSON-compatible format.
        
        Args:
            belief: Belief dictionary
            
        Returns:
            SerializationResult
        """
        try:
            # Convert to dict if needed (handles dataclass instances)
            data = asdict(belief) if hasattr(belief, '__dataclass_fields__') else belief
            
            return SerializationResult(
                success=True,
                serialized_data=data,
                trace=("serializable", "validated")
            )
        except Exception as e:
            return SerializationResult(
                success=False,
                error_message=str(e),
                trace=("error",)
            )
    
    def serialize_belief_state(self, state: dict[str, Any]) -> SerializationResult:
        """
        Serialize an entire belief state.
        
        Args:
            state: BeliefState dictionary
            
        Returns:
            SerializationResult
        """
        try:
            # Validate structure first
            if not isinstance(state, dict):
                return SerializationResult(
                    success=False,
                    error_message="BeliefState must be a dictionary",
                    trace=("error:type",)
                )
            
            # Serialize each component
            result: dict[str, Any] = {}
            
            beliefs = state.get("beliefs", [])
            if isinstance(beliefs, (tuple, list)):
                result["beliefs"] = [asdict(b) if hasattr(b, '__dataclass_fields__') else b 
                                     for b in beliefs]
            
            # Copy other fields
            for key in ("hierarchy", "dependencies", "revision_graph"):
                value = state.get(key)
                if value is not None:
                    result[key] = value
            
            return SerializationResult(
                success=True,
                serialized_data=result,
                trace=("serialized:state",)
            )
        except Exception as e:
            return SerializationResult(
                success=False,
                error_message=str(e),
                trace=("error:serialization",)
            )
    
    def serialize_revision_graph(self, graph: dict[str, Any]) -> SerializationResult:
        """
        Serialize a revision graph.
        
        Args:
            graph: BeliefRevisionGraph dictionary
            
        Returns:
            SerializationResult
        """
        try:
            # Validate structure
            if not isinstance(graph, dict):
                return SerializationResult(
                    success=False,
                    error_message="RevisionGraph must be a dictionary",
                    trace=("error:type",)
                )
            
            result: dict[str, Any] = {}
            
            nodes = graph.get("nodes", [])
            if isinstance(nodes, (tuple, list)):
                result["nodes"] = [asdict(n) if hasattr(n, '__dataclass_fields__') else n 
                                  for n in nodes]
            
            edges = graph.get("edges", [])
            if isinstance(edges, (tuple, list)):
                result["edges"] = [asdict(e) if hasattr(e, '__dataclass_fields__') else e 
                                  for e in edges]
            
            # Copy other fields
            for key in ("policy", "root_nodes"):
                value = graph.get(key)
                if value is not None:
                    result[key] = value
            
            return SerializationResult(
                success=True,
                serialized_data=result,
                trace=("serialized:graph",)
            )
        except Exception as e:
            return SerializationResult(
                success=False,
                error_message=str(e),
                trace=("error:serialization",)
            )
    
    def to_json(self, data: dict[str, Any]) -> str:
        """
        Convert serialized data to JSON string.
        
        Args:
            data: Serialized dictionary
            
        Returns:
            JSON string
        """
        return json.dumps(data, separators=(",", ":"), sort_keys=True)
    
    def from_json(self, json_str: str) -> dict[str, Any]:
        """
        Parse JSON string back to dictionary.
        
        Args:
            json_str: JSON string
            
        Returns:
            Parsed dictionary
        """
        return json.loads(json_str)


def serialize_belief_state(state: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, str]:
    """
    Convenience function to serialize a belief state.
    
    Args:
        state: BeliefState to serialize
        
    Returns:
        Tuple of (success, serialized_data or None, error_message or "")
    """
    serializer = BeliefRevisionSerializer()
    result = serializer.serialize_belief_state(state)
    
    if result.success and result.serialized_data is not None:
        return True, result.serialized_data, ""
    
    return False, None, result.error_message or "Unknown serialization error"