# Default Network Ports
# =====================

"""
Semantic ports for the DefaultNetwork.

Ports define explicit interfaces where interaction is required. They belong to
the semantic network boundary and do NOT expose Core implementations.

PHASE 4.3.1: Semantic Ports Only
"""

from __future__ import annotations

from typing import Optional, Tuple


# =============================================================================
# PORT INTERFACES (semantic contracts)
# =============================================================================

class MemoryProjectionPort:
    """
    Port for receiving memory projections.
    
    The DefaultNetwork may receive bounded projections from Memory systems,
    but does NOT own or mutate Memory state directly.
    
    Semantics:
        - Receive memory reactivation signals
        - Receive autobiographical context
        - Receive associative memory activation patterns
        - Do NOT store, modify, or control Memory
    """
    
    def __init__(self) -> None:
        """Initialize the MemoryProjectionPort."""
        self._enabled = True
    
    @property
    def is_enabled(self) -> bool:
        """Return whether this port is enabled."""
        return self._enabled
    
    def disable(self) -> None:
        """Temporarily disable this port."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable this port."""
        self._enabled = True


class ConsciousnessProjectionPort:
    """
    Port for receiving consciousness projections.
    
    The DefaultNetwork may receive bounded conscious-context projections,
    but does NOT own or mutate Consciousness state directly.
    
    Semantics:
        - Receive current conscious context
        - Receive attentional state projections  
        - Do NOT determine what becomes conscious
        - Do NOT mutate conscious state
    """
    
    def __init__(self) -> None:
        """Initialize the ConsciousnessProjectionPort."""
        self._enabled = True
    
    @property
    def is_enabled(self) -> bool:
        """Return whether this port is enabled."""
        return self._enabled
    
    def disable(self) -> None:
        """Temporarily disable this port."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable this port."""
        self._enabled = True


class CognitionRequestPort:
    """
    Port for requesting cognition capabilities.
    
    The DefaultNetwork may coordinate requests to specialized Cognition systems,
    but does NOT implement all cognitive capabilities itself.
    
    Semantics:
        - Request reasoning when needed
        - Request prediction support  
        - Request simulation assistance
        - Do NOT replace specialized cognitive capabilities
    """
    
    def __init__(self) -> None:
        """Initialize the CognitionRequestPort."""
        self._enabled = True
    
    @property
    def is_enabled(self) -> bool:
        """Return whether this port is enabled."""
        return self._enabled
    
    def disable(self) -> None:
        """Temporarily disable this port."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable this port."""
        self._enabled = True


class KnowledgeProjectionPort:
    """
    Port for receiving knowledge projections.
    
    The DefaultNetwork may receive semantic knowledge from Knowledge systems,
    but does NOT own or modify knowledge state directly.
    
    Semantics:
        - Receive conceptual knowledge
        - Receive semantic schema activations
        - Do NOT store, modify, or control Knowledge
    """
    
    def __init__(self) -> None:
        """Initialize the KnowledgeProjectionPort."""
        self._enabled = True
    
    @property
    def is_enabled(self) -> bool:
        """Return whether this port is enabled."""
        return self._enabled
    
    def disable(self) -> None:
        """Temporarily disable this port."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable this port."""
        self._enabled = True


class GoalProjectionPort:
    """
    Port for receiving goal projections.
    
    The DefaultNetwork may receive projections about goals, including
    unresolved goals that should be resurfaced or incubated.
    
    Semantics:
        - Receive goal state projections
        - Receive priority adjustments for goals
        - Do NOT own or modify Goal state directly
    """
    
    def __init__(self) -> None:
        """Initialize the GoalProjectionPort."""
        self._enabled = True
    
    @property
    def is_enabled(self) -> bool:
        """Return whether this port is enabled."""
        return self._enabled
    
    def disable(self) -> None:
        """Temporarily disable this port."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable this port."""
        self._enabled = True


class DefaultNetworkOutputPort:
    """
    Port for emitting Default Network outputs.
    
    The network emits proposals and assessments through this port. These are
    semantic proposals that other systems may consider - they do NOT command
    execution directly.
    
    Semantics:
        - Emit proposals for internal processing coordination
        - Emit assessments of internally oriented demand
        - Do NOT command execution or authorize action
    """
    
    def __init__(self) -> None:
        """Initialize the DefaultNetworkOutputPort."""
        self._enabled = True
    
    @property
    def is_enabled(self) -> bool:
        """Return whether this port is enabled."""
        return self._enabled
    
    def disable(self) -> None:
        """Temporarily disable this port."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable this port."""
        self._enabled = True


# =============================================================================
# PORT COLLECTION
# =============================================================================

class DefaultNetworkPorts:
    """
    Collection of all ports for the DefaultNetwork.
    
    This provides a unified interface to all semantic ports, ensuring that
    port management remains separate from runtime mechanics.
    """
    
    def __init__(self) -> None:
        """Initialize all network ports."""
        self.memory_projection = MemoryProjectionPort()
        self.consciousness_projection = ConsciousnessProjectionPort()
        self.cognition_request = CognitionRequestPort()
        self.knowledge_projection = KnowledgeProjectionPort()
        self.goal_projection = GoalProjectionPort()
        self.output = DefaultNetworkOutputPort()
    
    def disable_all(self) -> None:
        """Disable all ports."""
        self.memory_projection.disable()
        self.consciousness_projection.disable()
        self.cognition_request.disable()
        self.knowledge_projection.disable()
        self.goal_projection.disable()
        self.output.disable()
    
    def enable_all(self) -> None:
        """Enable all ports."""
        self.memory_projection.enable()
        self.consciousness_projection.enable()
        self.cognition_request.enable()
        self.knowledge_projection.enable()
        self.goal_projection.enable()
        self.output.enable()


# =============================================================================
# PORT VALIDATION
# =============================================================================

class PortValidation:
    """
    Validation utilities for port states.
    
    These ensure ports maintain their semantic semantics without leaking
    runtime implementation details.
    """
    
    @staticmethod
    def validate_port_name(name: str) -> bool:
        """
        Validate that a port name is recognized.
        
        Args:
            name: The port name to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_names = {
            "memory_projection",
            "consciousness_projection", 
            "cognition_request",
            "knowledge_projection",
            "goal_projection",
            "output",
        }
        return name in valid_names


def get_port_names() -> Tuple[str, ...]:
    """Return the names of all recognized ports."""
    return (
        "memory_projection",
        "consciousness_projection",
        "cognition_request", 
        "knowledge_projection",
        "goal_projection",
        "output",
    )