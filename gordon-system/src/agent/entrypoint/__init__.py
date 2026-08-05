"""Gordon Agent Process Entrypoint Package.

Phase 3.7.29-I + 3.7.30-I + 3.7.32-I + 3.7.33-I: Agent Process Entrypoint
==========================================================================

This package provides the canonical Agent process entry architecture.

Canonical Entrypoint Chain:
    python -m agent
        -> agent.__main__
        -> agent.entrypoint.main.main()
        -> agent.entrypoint.startup.start_agent() (Phase 3.7.33-I)
        -> agent.entrypoint.check.check_agent() (Phase 3.7.32-I)
        -> agent.entrypoint.init.initialize_agent() (Phase 3.7.30)
        -> agent.components.core

Architecture Boundaries:
- Process entry: This package (entrypoint/)
- Startup coordination: agent.entrypoint/startup/ (Phase 3.7.33-I)
- Preflight checks: agent.entrypoint/check/ (Phase 3.7.32-I)
- Initialization: agent.entrypoint/init/ (Phase 3.7.30)
- Loading: agent.entrypoint/load/ (Phase 3.7.31)
- Runtime: agent/components/core/

Responsibilities:
- Process-level entry point normalization
- CLI argument parsing (Agent-specific surface only)
- Launch request construction (immutable)
- Signal routing to shutdown intent
- Exit-status mapping

NOT responsible for:
- Configuration-file parsing internals
- Component discovery or loading
- Agent Core construction
- Runtime assembly or activation
- Cognition, planning, or operation
- Preflight check implementations (entrypoint/check.py)
- Startup coordination (entrypoint/startup.py)

Public API (Phase 3.7.29):
    - main(argv: Sequence[str] | None = None) -> int
    - AgentInvocationSurface
    - AgentRunMode
    - AgentBridgePolicy
    - AgentLaunchMode
    - AgentProcessIdentity
    - AgentLaunchIdentity
    - AgentRuntimeIdentity
    - AgentSystemIdentity
    - AgentConfigurationRequest
    - AgentLaunchRequest
    - AgentExitStatus

Public API (Phase 3.7.30):
    - initialize_agent(request) -> Result
    - AgentInitializer
    - AgentInitializationRequest
    - AgentInitializationContext
    - AgentInitializationPhase
    - AgentInitializationResult
    - AgentInitializationFailure
    - AgentInitializationError

Public API (Phase 3.7.32):
    - check_agent(request) -> PreflightResult
    - AgentPreflightChecker
    - AgentPreflightRequest
    - AgentPreflightResult
    - AgentPreflightOutcome
    - AgentPreflightPhase

Public API (Phase 3.7.33-I):
    - start_agent(launch_request) -> StartupResult
    - AgentStartupCoordinator
    - AgentStartupResult
    - AgentStartupPolicy
    - AgentStartupContext
    - AgentStartupPhase
    - AgentStartupOutcome
    - AgentStartupFailure

Import-time behavior:
- No CLI parsing at import time
- No logging configuration at import time
- No signal handlers installed at import time
- No event loop created at import time
- No Agent runtime constructed at import time
- No startup performed at import time
- No preflight checks executed at import time

Files in Phase 3.7.29:
- __init__.py: Package initialization and exports
- main.py: Canonical process entrypoint
- types.py: Type definitions (immutable dataclasses/enums)
- exits.py: Exit status codes

Files in Phase 3.7.30:
- init/__init__.py: Initialization package exports
- init/types.py: Initialization type definitions
- init/exceptions.py: Initialization exception types
- init/initializer.py: Canonical initializer implementation

Files in Phase 3.7.32:
- check/__init__.py: Preflight package exports
- check/types.py: Preflight type definitions
- check/request.py: Preflight request models
- check/result.py: Preflight result models
- check/policy.py: Preflight policy models
- check/checker.py: Preflight checker implementation
- check/checks.py: Individual preflight checks

Files in Phase 3.7.33-I:
- startup/__init__.py: Startup package exports
- startup/startup.py: Canonical startup coordinator
- startup/context.py: Startup context definitions
- startup/policy.py: Startup policy definitions
- startup/outcomes.py: Startup outcome definitions
- startup/result.py: Startup result definitions
- startup/exceptions.py: Startup exception types
"""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .main import main
    from .types import (
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
    from .exits import AgentExitStatus, format_exit_status
    # Phase 3.7.30 imports (deferred until accessed)
    from .init.types import (
        AgentInitializationRequest,
        AgentInitializationContext,
        AgentInitializationPhase,
        AgentInitializationResult,
        AgentInitializationFailure,
    )
    from .init.initializer import AgentInitializer, initialize_agent
    # Phase 3.7.32 imports (deferred until accessed)
    from .check import (
        AgentPreflightRequest,
        AgentPreflightResult,
        AgentPreflightOutcome,
        AgentPreflightPhase,
    )
    from .check.checker import AgentPreflightChecker, check_agent
    # Phase 3.7.33-I imports (deferred until accessed)
    from .startup import (
        start_agent,
        AgentStartupCoordinator,
        AgentStartupResult,
        AgentStartupPolicy,
        AgentStartupContext,
        AgentStartupPhase,
        AgentStartupOutcome,
        AgentStartupFailure,
    )

from .types import (
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
from .exits import AgentExitStatus, format_exit_status
from .main import main

# Phase 3.7.30 exports (deferred for lazy loading in __init__.py)
# These are available via the init/ subpackage and through delegation

# Phase 3.7.32 exports (deferred for lazy loading in __init__.py)
# These are available via the check/ subpackage and through delegation

# Phase 3.7.33-I exports
from .startup import start_agent, AgentStartupCoordinator


def __getattr__(name: str) -> Any:
    """Defer imports to canonical modules for backward compatibility."""
    if name == "initialize_agent":
        from .init import initialize_agent
        return initialize_agent
    
    if name == "AgentInitializer":
        from .init.initializer import AgentInitializer
        return AgentInitializer
    
    if name in (
        "AgentInitializationRequest",
        "AgentInitializationContext",
        "AgentInitializationPhase",
        "AgentInitializationResult",
        "AgentInitializationFailure",
    ):
        from .init.types import (
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
    
    if name == "check_agent":
        from . import check
        return check.check_agent
    
    if name == "AgentPreflightChecker":
        from .check.checker import AgentPreflightChecker
        return AgentPreflightChecker
    
    if name in (
        "AgentPreflightRequest",
        "AgentPreflightResult",
        "AgentPreflightOutcome",
        "AgentPreflightPhase",
    ):
        from .check import (
            AgentPreflightRequest,
            AgentPreflightResult,
            AgentPreflightOutcome,
            AgentPreflightPhase,
        )
        
        if name == "AgentPreflightRequest":
            return AgentPreflightRequest
        elif name == "AgentPreflightResult":
            return AgentPreflightResult
        elif name == "AgentPreflightOutcome":
            return AgentPreflightOutcome
        elif name == "AgentPreflightPhase":
            return AgentPreflightPhase
    
    if name in (
        "start_agent",
        "AgentStartupCoordinator",
        "AgentStartupResult",
        "AgentStartupPolicy",
        "AgentStartupContext",
        "AgentStartupPhase",
        "AgentStartupOutcome",
    ):
        from .startup import (
            start_agent,
            AgentStartupCoordinator,
            AgentStartupResult,
            AgentStartupPolicy,
            AgentStartupContext,
            AgentStartupPhase,
            AgentStartupOutcome,
        )
        
        if name == "start_agent":
            return start_agent
        elif name == "AgentStartupCoordinator":
            return AgentStartupCoordinator
        elif name == "AgentStartupResult":
            return AgentStartupResult
        elif name == "AgentStartupPolicy":
            return AgentStartupPolicy
        elif name == "AgentStartupContext":
            return AgentStartupContext
        elif name == "AgentStartupPhase":
            return AgentStartupPhase
        elif name == "AgentStartupOutcome":
            return AgentStartupOutcome
    
    if name == "AgentStartupFailure":
        from .startup.exceptions import AgentStartupFailure
        return AgentStartupFailure
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "main",
    "start_agent",
    "AgentStartupCoordinator",
    "AgentInvocationSurface",
    "AgentRunMode",
    "AgentBridgePolicy",
    "AgentLaunchMode",
    "AgentProcessIdentity",
    "AgentLaunchIdentity",
    "AgentRuntimeIdentity",
    "AgentSystemIdentity",
    "AgentConfigurationRequest",
    "AgentLaunchRequest",
    "AgentExitStatus",
    "format_exit_status",
]