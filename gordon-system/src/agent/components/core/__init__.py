# Core Runtime Infrastructure
# ============================

"""
Core runtime infrastructure for Gordon agent.

This package provides the foundational runtime substrate including:
- Lifecycle management
- Registry and dependency resolution
- Configuration handling
- Context management
- State management
- Synchronization primitives
- Execution and scheduling
- Observability and integrity validation
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import submodules for type checking
    from core import contracts, types, exceptions, lifecycle
    from core import registry, dependency, configuration, context
    from core import state, synchronization, execution, scheduling
    from core import observability, integrity, kernel, runtime
    from core import testing

__all__ = [
    "contracts",
    "types", 
    "exceptions",
    "lifecycle",
    "registry",
    "dependency",
    "configuration",
    "context",
    "state",
    "synchronization",
    "execution",
    "scheduling",
    "observability",
    "integrity",
    "kernel",
    "runtime",
    "testing",
]