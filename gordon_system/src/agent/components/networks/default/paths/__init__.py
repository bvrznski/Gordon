# Paths Package
# =============

"""
Path abstraction layer for Default Network coordination.

This package defines:
    • Path Handler Protocol: Runtime-neutral interface for specialized paths
    • Path Context: Immutable inputs to path handlers
    • Path Result: Immutable outputs from path handlers
    • Path Registry: Mapping of path kinds to handler implementations
    • Path Selector: Deterministic path selection logic

ARCHITECTURAL PRINCIPLES:
    1. Paths are semantic coordination approaches, NOT runtime routes
    2. Handlers are stateless or explicitly state-projected
    3. All contracts are deeply immutable
    4. No runtime references in domain models
    5. Bounded local progression per invocation

PHASE 4.3.12: Path Abstraction Layer
"""

from __future__ import annotations

# Main protocol and types
from .base import (
    DefaultNetworkPathHandler,
    DefaultNetworkPathContext,
    DefaultNetworkPathResult,
)

# Registry
from .registry import (
    DefaultNetworkPathRegistry,
    create_default_path_registry,
)

# Selector
from .selector import (
    DefaultNetworkPathSelector,
    DefaultNetworkPathSelection,
    create_default_path_selector,
)


__all__ = [
    # Protocols
    "DefaultNetworkPathHandler",
    
    # Context and result types
    "DefaultNetworkPathContext",
    "DefaultNetworkPathResult",
    
    # Registry
    "DefaultNetworkPathRegistry",
    "create_default_path_registry",
    
    # Selector
    "DefaultNetworkPathSelector",
    "DefaultNetworkPathSelection",
    "create_default_path_selector",
]