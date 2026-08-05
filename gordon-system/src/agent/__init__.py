"""Gordon Agent Core Package.

Phase 3.7: Third-stage runtime expansion with production-grade capabilities.
"""
from __future__ import annotations

# Phase 3.7.29-I - Process Entrypoint
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agent.entrypoint.main import main as _main
    from agent.entrypoint.init import (
        AgentInitializationRequest,
        AgentInitializationContext,
        AgentInitializationPhase,
        AgentInitializationResult,
        AgentInitializationFailure,
        AgentInitializer,
        initialize_agent,
        get_canonical_initializer,
    )
    from agent.entrypoint.types import (
        AgentInvocationSurface,
        AgentRunMode,
        AgentBridgePolicy,
        AgentLaunchMode,
        AgentProcessIdentity,
        AgentLaunchIdentity,
        AgentRuntimeIdentity,
        AgentSystemIdentity,
        AgentConfigurationRequest,
        AgentLaunchRequest,
    )

__all__ = [
    # Legacy compatibility - these are delegated to canonical modules
]

# Expose main for backward compatibility (process entrypoint)
# The actual implementation is in agent.entrypoint.main


def __getattr__(name: str) -> Any:
    """Defer imports to canonical modules for backward compatibility.
    
    This enables legacy code that does `from agent import initialize_agent`
    to continue working by delegating to the canonical location.
    """
    if name == "main":
        from agent.entrypoint.main import main as _main
        return _main
    
    if name in (
        "AgentInitializationRequest",
        "AgentInitializationContext",
        "AgentInitializationPhase",
        "AgentInitializationResult",
        "AgentInitializationFailure",
    ):
        from agent.entrypoint.init.types import (
            AgentInitializationRequest,
            AgentInitializationContext,
            AgentInitializationPhase,
            AgentInitializationResult,
            AgentInitializationFailure,
        )
        
        if name == "AgentInitializationRequest":
            return AgentInitializationRequest
        elif name == "AgentInitializationContext":
            return AgentInitializationContext
        elif name == "AgentInitializationPhase":
            return AgentInitializationPhase
        elif name == "AgentInitializationResult":
            return AgentInitializationResult
        elif name == "AgentInitializationFailure":
            return AgentInitializationFailure
    
    if name == "AgentInitializer":
        from agent.entrypoint.init.initializer import AgentInitializer
        return AgentInitializer
    
    if name == "initialize_agent":
        from agent.entrypoint.init import initialize_agent
        return initialize_agent
    
    if name == "get_canonical_initializer":
        from agent.entrypoint.init import get_canonical_initializer
        return get_canonical_initializer
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
