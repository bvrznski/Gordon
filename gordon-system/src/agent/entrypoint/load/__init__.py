"""Gordon Agent Entrypoint Loading.

Phase 3.7.31-I: Agent Component Loading Architecture
====================================================

Canonical loading facade for Agent component loading operations.

This package provides exactly one canonical loading authority that:

- Discovers declarative __load__.py descriptors
- Validates descriptor contracts
- Builds deterministic dependency graphs
- Resolves capabilities deterministically
- Generates immutable load plans
- Imports implementations safely
- Constructs components through factories
- Tracks ownership and rollback evidence
- Returns immutable load results

Architecture Boundaries
-----------------------
This package owns:
- Canonical component loading coordinator
- Immutable load request model
- Deterministic dependency resolution
- Component construction orchestration
- Load result construction with provenance

This module does NOT own:
- Configuration parsing (delegated to configuration authority)
- Core construction authority (kernel/builder.py)
- Runtime assembly authority (runtime assembler)
- Component implementation discovery (external to loading)

Canonical Loading Chain:
    agent.entrypoint.init.initialize_agent()
        ↓
    AgentInitializer._step_load_components()
        ↓
    entrypoint/load/load_components(request)
        ↓
    LoadRequest validation
        ↓
    Descriptor discovery (__load__.py files)
        ↓
    Dependency graph construction
        ↓
    Capability resolution
        ↓
    Deterministic load plan generation
        ↓
    Implementation import
        ↓
    Factory resolution
        ↓
    Component construction
        ↓
    LoadResult with component summary

Import-time behavior:
- No configuration resolution at import time
- No component discovery at import time
- No runtime construction at import time

Public API:
    - load_components(request: AgentLoadRequest) -> AgentLoadResult
    - request_load_plan(launch_id: str, config_fingerprint: str) -> LoadPlan

Exports:
    from .request import AgentLoadRequest
    from .result import AgentLoadResult, AgentComponentLoadStatus
    from .types import (
        LoadDescriptor,
        LoadDescriptorSet,
        LoadPlan,
        LoadPhase,
        ComponentKind,
        DependencyType,
        CapabilityDeclaration,
        ConfigurationProjection,
    )
    from .manager import (
        AgentLoadManager,
        LoadOperationIdentity,
        DependencyEdge,
        DependencyGraph,
        CapabilityProviderSelection,
        ComponentConstructionResult,
    )
"""

from __future__ import annotations

import asyncio

# Import all public types and functions
from .request import AgentLoadRequest
from .result import (
    AgentLoadResult,
    AgentComponentLoadStatus,
)
from .types import (
    LoadDescriptor,
    LoadDescriptorSet,
    LoadPlan,
    LoadPhase,
    ComponentKind,
    DependencyType,
    CapabilityDeclaration,
    ConfigurationProjection,
)
from .manager import (
    AgentLoadManager,
    LoadOperationIdentity,
    DependencyEdge,
    DependencyGraph,
    CapabilityProviderSelection,
    ComponentConstructionResult,
)


# =============================================================================
# MODULE-LEVEL WRAPPER FUNCTIONS
# =============================================================================


def load_components(request: "AgentLoadRequest") -> "AgentLoadResult":
    """Synchronous wrapper for AgentLoadManager.load_components().
    
    This function provides a sync interface to the async load_components method.
    It creates an AgentLoadManager and runs the async method to completion.
    
    Args:
        request: The load request with configuration and plan information
        
    Returns:
        AgentLoadResult with component construction results
    """
    manager = AgentLoadManager()
    return asyncio.run(manager.load_components(request))


def request_load_plan(launch_id: str, config_fingerprint: str) -> "LoadPlan":
    """Synchronous wrapper for AgentLoadManager.request_load_plan().
    
    This function provides a sync interface to the async request_load_plan method.
    It creates an AgentLoadManager and runs the async method to completion.
    
    Args:
        launch_id: The launch session ID
        config_fingerprint: Fingerprint of the configuration
        
    Returns:
        LoadPlan with deterministic load ordering
    """
    manager = AgentLoadManager()
    return asyncio.run(manager.request_load_plan(launch_id, config_fingerprint))



__all__ = [
    # Request model
    "AgentLoadRequest",
    # Result models
    "AgentLoadResult",
    "AgentComponentLoadStatus",
    # Type definitions
    "LoadDescriptor",
    "LoadDescriptorSet",
    "LoadPlan",
    "LoadPhase",
    "ComponentKind",
    "DependencyType",
    "CapabilityDeclaration",
    "ConfigurationProjection",
    # Manager types
    "LoadOperationIdentity",
    "DependencyEdge",
    "DependencyGraph",
    "CapabilityProviderSelection",
    "ComponentConstructionResult",
    # Manager
    "AgentLoadManager",
    # Module-level functions
    "load_components",
    "request_load_plan",
]
