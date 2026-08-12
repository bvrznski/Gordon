# Execution Registry
# =================

"""
Registry and discovery mechanisms for execution components.

This module provides:
    - Unit type registries (Thread, Loop, Cycle)
    - Discovery mechanisms for concrete implementations
    - Factory registration for Core integration
"""

from dataclasses import dataclass, field
from typing import Dict, Type, Optional, List
from enum import Enum


# =============================================================================
# Unit Types
# =============================================================================

class ExecutionUnitType(Enum):
    """Categories of execution units."""
    
    THREAD = "thread"
    LOOP = "loop"
    CYCLE = "cycle"


@dataclass(frozen=True)
class UnitDescriptor:
    """
    Descriptor for an execution unit type.
    
    Contains metadata about a unit without importing the concrete class.
    """
    
    # Identity (required - no defaults)
    unit_type: ExecutionUnitType
    name: str
    
    # Classification
    description: Optional[str] = None
    semantic_owner: Optional[str] = None  # e.g., "Thread", "Loop", "Cycle"
    
    # Implementation info (not for direct use)
    implementation_path: Optional[str] = None
    
    # Capabilities
    supports_checkpointing: bool = False
    supports_cancellation: bool = True
    max_repetitions: Optional[int] = None  # For loops, max iterations


# =============================================================================
# Registry
# =============================================================================

class ExecutionRegistry:
    """
    Canonical registry for execution unit types.
    
    This is the single source of truth for available execution components.
    Concrete implementations register here during import/bootstrap.
    
    Rules:
        - Only one canonical registry per execution category
        - Registry stores descriptors, not concrete classes (for Core)
        - Discovery happens through descriptors
    """
    
    def __init__(self) -> None:
        # unit_type.name -> UnitDescriptor mapping
        self._thread_descriptors: Dict[str, UnitDescriptor] = {}
        self._loop_descriptors: Dict[str, UnitDescriptor] = {}
        self._cycle_descriptors: Dict[str, UnitDescriptor] = {}
        
        # implementation_path -> descriptor reverse lookup
        self._implementation_to_descriptor: Dict[str, UnitDescriptor] = {}
    
    def register_thread(
        self,
        name: str,
        description: Optional[str] = None,
        semantic_owner: Optional[str] = "Thread",
        implementation_path: Optional[str] = None,
    ) -> UnitDescriptor:
        """
        Register a Thread type.
        
        Args:
            name: Unique identifier for this thread type
            description: Human-readable description
            semantic_owner: Component that semantically owns this thread
            implementation_path: Module path to concrete class (for factory)
        """
        descriptor = UnitDescriptor(
            unit_type=ExecutionUnitType.THREAD,
            name=name,
            description=description or "",
            semantic_owner=semantic_owner,
            implementation_path=implementation_path,
        )
        
        if name in self._thread_descriptors:
            raise ValueError(f"Thread type '{name}' already registered")
        
        self._thread_descriptors[name] = descriptor
        if implementation_path:
            self._implementation_to_descriptor[implementation_path] = descriptor
        
        return descriptor
    
    def register_loop(
        self,
        name: str,
        description: Optional[str] = None,
        semantic_owner: Optional[str] = "Loop",
        implementation_path: Optional[str] = None,
        supports_checkpointing: bool = False,
        max_repetitions: Optional[int] = None,
    ) -> UnitDescriptor:
        """
        Register a Loop type.
        
        Args:
            name: Unique identifier for this loop type
            description: Human-readable description
            semantic_owner: Component that semantically owns this loop
            implementation_path: Module path to concrete class (for factory)
            supports_checkpointing: Can this loop be checkpointed?
            max_repetitions: Maximum iterations before forced termination
        """
        descriptor = UnitDescriptor(
            unit_type=ExecutionUnitType.LOOP,
            name=name,
            description=description or "",
            semantic_owner=semantic_owner,
            implementation_path=implementation_path,
            supports_checkpointing=supports_checkpointing,
            max_repetitions=max_repetitions,
        )
        
        if name in self._loop_descriptors:
            raise ValueError(f"Loop type '{name}' already registered")
        
        self._loop_descriptors[name] = descriptor
        if implementation_path:
            self._implementation_to_descriptor[implementation_path] = descriptor
        
        return descriptor
    
    def register_cycle(
        self,
        name: str,
        description: Optional[str] = None,
        semantic_owner: Optional[str] = "Cycle",
        implementation_path: Optional[str] = None,
        supports_checkpointing: bool = False,
    ) -> UnitDescriptor:
        """
        Register a Cycle type.
        
        Args:
            name: Unique identifier for this cycle type
            description: Human-readable description
            semantic_owner: Component that semantically owns this cycle
            implementation_path: Module path to concrete class (for factory)
            supports_checkpointing: Can this cycle be checkpointed?
        """
        descriptor = UnitDescriptor(
            unit_type=ExecutionUnitType.CYCLE,
            name=name,
            description=description or "",
            semantic_owner=semantic_owner,
            implementation_path=implementation_path,
            supports_checkpointing=supports_checkpointing,
        )
        
        if name in self._cycle_descriptors:
            raise ValueError(f"Cycle type '{name}' already registered")
        
        self._cycle_descriptors[name] = descriptor
        if implementation_path:
            self._implementation_to_descriptor[implementation_path] = descriptor
        
        return descriptor
    
    def get_thread(self, name: str) -> Optional[UnitDescriptor]:
        """Get a registered thread descriptor by name."""
        return self._thread_descriptors.get(name)
    
    def get_loop(self, name: str) -> Optional[UnitDescriptor]:
        """Get a registered loop descriptor by name."""
        return self._loop_descriptors.get(name)
    
    def get_cycle(self, name: str) -> Optional[UnitDescriptor]:
        """Get a registered cycle descriptor by name."""
        return self._cycle_descriptors.get(name)
    
    def get_by_implementation_path(self, path: str) -> Optional[UnitDescriptor]:
        """Get a descriptor by its implementation path (reverse lookup)."""
        return self._implementation_to_descriptor.get(path)
    
    def list_threads(self) -> List[UnitDescriptor]:
        """List all registered thread types."""
        return list(self._thread_descriptors.values())
    
    def list_loops(self) -> List[UnitDescriptor]:
        """List all registered loop types."""
        return list(self._loop_descriptors.values())
    
    def list_cycles(self) -> List[UnitDescriptor]:
        """List all registered cycle types."""
        return list(self._cycle_descriptors.values())


# Global registry instance
_registry: Optional[ExecutionRegistry] = None


def get_registry() -> ExecutionRegistry:
    """
    Get the global execution registry.
    
    Creates a new registry if none exists.
    """
    global _registry
    if _registry is None:
        _registry = ExecutionRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _registry
    _registry = None


__all__ = [
    # Enums
    "ExecutionUnitType",
    
    # Descriptors
    "UnitDescriptor",
    
    # Registry classes
    "ExecutionRegistry",
    
    # Global accessors
    "get_registry",
    "reset_registry",
]