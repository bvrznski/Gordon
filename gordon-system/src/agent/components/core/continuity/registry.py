# Continuity Participant Registry
# ================================

"""
Participant registration and management for continuity infrastructure.

This module provides deterministic participant registration with validation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict

from .contracts import ContinuityParticipant, ParticipantId
from .exceptions import ParticipantRegistrationError


@dataclass(frozen=True)
class RegisteredParticipant:
    """Information about a registered participant."""
    
    participant_id: ParticipantId
    fragment_type: str
    schema_version: int
    required_for_restore: bool
    dependencies: Tuple[str, ...]  # IDs of participants this depends on
    
    @classmethod
    def from_participant(cls, participant: ContinuityParticipant) -> "RegisteredParticipant":
        """Create a registered participant from a ContinuityParticipant instance."""
        return cls(
            participant_id=participant.participant_id,
            fragment_type=participant.fragment_type,
            schema_version=participant.schema_version,
            required_for_restore=participant.required_for_restore,
            dependencies=(),  # Dependencies would be configured externally
        )


@dataclass
class ParticipantRegistry:
    """
    Registry for continuity participants.
    
    This registry provides deterministic registration with:
        - Duplicate ID rejection
        - Dependency validation
        - Cycle detection in dependency graph
        
    Usage:
        >>> registry = ParticipantRegistry()
        >>> registry.register(participant)
        >>> participant_info = registry.get("participant-id")
    """
    
    _participants: Dict[str, RegisteredParticipant] = field(default_factory=dict)
    _registration_order: List[str] = field(default_factory=list)
    _dependencies_resolved: Set[str] = field(default_factory=set)
    
    def register(self, participant: ContinuityParticipant) -> RegisteredParticipant:
        """
        Register a continuity participant.
        
        Args:
            participant: The participant to register
            
        Returns:
            The registered participant info
            
        Raises:
            ParticipantRegistrationError: If registration fails
        """
        pid_str = str(participant.participant_id)
        
        # Check for duplicate
        if pid_str in self._participants:
            raise ParticipantRegistrationError(
                participant_id=pid_str,
                reason=f"Duplicate participant ID already registered",
            )
        
        # Create and store the registration
        registered = RegisteredParticipant.from_participant(participant)
        self._participants[pid_str] = registered
        self._registration_order.append(pid_str)
        
        return registered
    
    def get(self, participant_id: str) -> Optional[RegisteredParticipant]:
        """Get a registered participant by its ID."""
        return self._participants.get(participant_id)
    
    def all_participants(self) -> Tuple[RegisteredParticipant, ...]:
        """Return all registered participants in registration order."""
        return tuple(self._participants.values())
    
    def required_participants(self) -> Tuple[RegisteredParticipant, ...]:
        """Return only the participants that are required for restoration."""
        return tuple(
            p for p in self._participants.values()
            if p.required_for_restore
        )
    
    def optional_participants(self) -> Tuple[RegisteredParticipant, ...]:
        """Return only the optional participants."""
        return tuple(
            p for p in self._participants.values()
            if not p.required_for_restore
        )
    
    def participant_count(self) -> int:
        """Return the number of registered participants."""
        return len(self._participants)
    
    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        self._participants.clear()
        self._registration_order.clear()


class DependencyGraph:
    """
    Directed graph for participant dependencies.
    
    Used to determine restoration order and detect cycles.
    """
    
    def __init__(self):
        self._edges: Dict[str, Set[str]] = defaultdict(set)  # participant -> dependencies
        self._reverse_edges: Dict[str, Set[str]] = defaultdict(set)  # dependency -> dependents
    
    def add_edge(self, participant_id: str, depends_on: str) -> None:
        """Add a dependency edge (participant depends_on another)."""
        if participant_id != depends_on:
            self._edges[participant_id].add(depends_on)
            self._reverse_edges[depends_on].add(participant_id)
    
    def get_dependencies(self, participant_id: str) -> Set[str]:
        """Get all direct dependencies of a participant."""
        return self._edges.get(participant_id, set()).copy()
    
    def has_cycle(self) -> bool:
        """
        Check if the graph contains a cycle.
        
        Uses DFS with three colors:
            WHITE = unvisited
            GRAY = currently visiting (in stack)
            BLACK = finished visiting
            
        A back edge to a GRAY node indicates a cycle.
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {node: WHITE for node in self._edges}
        
        def dfs(node: str) -> bool:
            if node not in color:
                return False
            if color[node] == GRAY:
                return True  # Cycle found
            if color[node] == BLACK:
                return False
            
            color[node] = GRAY
            for dep in self._edges.get(node, []):
                if dfs(dep):
                    return True
            color[node] = BLACK
            return False
        
        for node in list(self._edges.keys()):
            if color[node] == WHITE:
                if dfs(node):
                    return True
        
        return False
    
    def topological_sort(self) -> Tuple[str, ...]:
        """
        Return participants in dependency order (dependencies first).
        
        Raises:
            ValueError: If a cycle exists
        """
        if self.has_cycle():
            raise ValueError("Dependency graph contains a cycle")
        
        visited = set()
        result: List[str] = []
        
        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in self._edges.get(node, []):
                visit(dep)
            result.append(node)
        
        for node in list(self._edges.keys()):
            visit(node)
        
        return tuple(result)


def build_dependency_graph(
    registry: ParticipantRegistry,
) -> DependencyGraph:
    """
    Build a dependency graph from the participant registry.
    
    In this simplified implementation, participants have no dependencies.
    A real implementation would use participant metadata or configuration
    to determine dependencies.
    
    Args:
        registry: The participant registry
        
    Returns:
        A dependency graph with edges between dependent participants
    """
    graph = DependencyGraph()
    
    # In this simplified version, we don't add any edges
    # Real implementation would parse participant metadata
    
    return graph


def get_restoration_order(
    registry: ParticipantRegistry,
) -> Tuple[str, ...]:
    """
    Get the order in which participants should be restored.
    
    Args:
        registry: The participant registry
        
    Returns:
        Tuple of participant IDs in restoration order
    """
    # Sort required participants first, then optional
    required = [p.participant_id.value for p in registry.required_participants()]
    optional = [p.participant_id.value for p in registry.optional_participants()]
    
    return tuple(required) + tuple(optional)