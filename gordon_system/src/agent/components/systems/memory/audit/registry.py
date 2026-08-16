# Memory Audit Registry - Phase 5.1.9
# =====================================

"""
Registry system for audit components.

This module manages the registration and lookup of:
    - Adapters: Memory access implementations
    - Validators: Validation checkers
    - Planners: Execution planners
    - Analyzers: Deep analysis modules
"""

from __future__ import annotations

import threading
from typing import Dict, Tuple, Type, Optional, Any
from dataclasses import dataclass

# Import base classes (runtime to avoid circular deps)
try:
    from .base import (
        MemoryAuditAdapter,
        MemoryAuditValidator,
        MemoryAuditPlanner,
        MemoryAuditAnalyzer,
    )
except ImportError:
    pass


# =============================================================================
# COMPONENT REGISTRY - Thread-safe component registry
# =============================================================================


class ComponentRegistry:
    """
    Thread-safe registry for audit components.
    
    Components are registered by name and can be looked up later.
    The registry is thread-safe and supports registration of:
        - Adapters
        - Validators
        - Planners
        - Analyzers
    
    Anti-Patterns Rejected:
        - Non-thread-safe registries (use locking)
        - Overwriting existing registrations (raise error instead)
    """
    
    def __init__(self):
        """Initialize the component registry."""
        self._adapters: Dict[str, Type[MemoryAuditAdapter]] = {}
        self._validators: Dict[str, Type[MemoryAuditValidator]] = {}
        self._planners: Dict[str, Type[MemoryAuditPlanner]] = {}
        self._analyzers: Dict[str, Type[MemoryAuditAnalyzer]] = {}
        self._lock = threading.RLock()
    
    def register_adapter(
        self,
        name: str,
        adapter_class: Type[MemoryAuditAdapter],
    ) -> None:
        """
        Register an adapter class.
        
        Args:
            name: Unique name for this adapter type
            adapter_class: The adapter class to register
            
        Raises:
            ValueError: If name is already registered
        """
        with self._lock:
            if name in self._adapters:
                raise ValueError(f"Adapter '{name}' is already registered")
            self._adapters[name] = adapter_class
    
    def unregister_adapter(self, name: str) -> None:
        """Unregister an adapter by name."""
        with self._lock:
            self._adapters.pop(name, None)
    
    def get_adapter(self, name: str) -> Optional[Type[MemoryAuditAdapter]]:
        """Get an adapter class by name."""
        with self._lock:
            return self._adapters.get(name)
    
    def list_adapters(self) -> Tuple[str, ...]:
        """List all registered adapter names."""
        with self._lock:
            return tuple(sorted(self._adapters.keys()))
    
    def register_validator(
        self,
        name: str,
        validator_class: Type[MemoryAuditValidator],
    ) -> None:
        """
        Register a validator class.
        
        Args:
            name: Unique name for this validator type
            validator_class: The validator class to register
            
        Raises:
            ValueError: If name is already registered
        """
        with self._lock:
            if name in self._validators:
                raise ValueError(f"Validator '{name}' is already registered")
            self._validators[name] = validator_class
    
    def unregister_validator(self, name: str) -> None:
        """Unregister a validator by name."""
        with self._lock:
            self._validators.pop(name, None)
    
    def get_validator(self, name: str) -> Optional[Type[MemoryAuditValidator]]:
        """Get a validator class by name."""
        with self._lock:
            return self._validators.get(name)
    
    def list_validators(self) -> Tuple[str, ...]:
        """List all registered validator names."""
        with self._lock:
            return tuple(sorted(self._validators.keys()))
    
    def register_planner(
        self,
        name: str,
        planner_class: Type[MemoryAuditPlanner],
    ) -> None:
        """
        Register a planner class.
        
        Args:
            name: Unique name for this planner type
            planner_class: The planner class to register
            
        Raises:
            ValueError: If name is already registered
        """
        with self._lock:
            if name in self._planners:
                raise ValueError(f"Planner '{name}' is already registered")
            self._planners[name] = planner_class
    
    def unregister_planner(self, name: str) -> None:
        """Unregister a planner by name."""
        with self._lock:
            self._planners.pop(name, None)
    
    def get_planner(self, name: str) -> Optional[Type[MemoryAuditPlanner]]:
        """Get a planner class by name."""
        with self._lock:
            return self._planners.get(name)
    
    def list_planners(self) -> Tuple[str, ...]:
        """List all registered planner names."""
        with self._lock:
            return tuple(sorted(self._planners.keys()))
    
    def register_analyzer(
        self,
        name: str,
        analyzer_class: Type[MemoryAuditAnalyzer],
    ) -> None:
        """
        Register an analyzer class.
        
        Args:
            name: Unique name for this analyzer type
            analyzer_class: The analyzer class to register
            
        Raises:
            ValueError: If name is already registered
        """
        with self._lock:
            if name in self._analyzers:
                raise ValueError(f"Analyzer '{name}' is already registered")
            self._analyzers[name] = analyzer_class
    
    def unregister_analyzer(self, name: str) -> None:
        """Unregister an analyzer by name."""
        with self._lock:
            self._analyzers.pop(name, None)
    
    def get_analyzer(self, name: str) -> Optional[Type[MemoryAuditAnalyzer]]:
        """Get an analyzer class by name."""
        with self._lock:
            return self._analyzers.get(name)
    
    def list_analyzers(self) -> Tuple[str, ...]:
        """List all registered analyzer names."""
        with self._lock:
            return tuple(sorted(self._analyzers.keys()))
    
    @property
    def adapter_count(self) -> int:
        """Get count of registered adapters."""
        with self._lock:
            return len(self._adapters)
    
    @property
    def validator_count(self) -> int:
        """Get count of registered validators."""
        with self._lock:
            return len(self._validators)
    
    @property
    def planner_count(self) -> int:
        """Get count of registered planners."""
        with self._lock:
            return len(self._planners)
    
    @property
    def analyzer_count(self) -> int:
        """Get count of registered analyzers."""
        with self._lock:
            return len(self._analyzers)


# =============================================================================
# GLOBAL REGISTRY - Singleton instance
# =============================================================================

# Create global registry (will be populated by other modules)
_global_registry = ComponentRegistry()


def get_registry() -> ComponentRegistry:
    """
    Get the global component registry.
    
    Returns:
        The singleton ComponentRegistry instance
    """
    return _global_registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _global_registry
    _global_registry = ComponentRegistry()


__all__ = [
    "ComponentRegistry",
    "get_registry",
    "reset_registry",
]