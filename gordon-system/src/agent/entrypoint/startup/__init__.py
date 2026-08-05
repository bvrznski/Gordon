"""Gordon Agent Startup Package.

Phase 3.7.33-I: Agent Startup Coordination
==========================================

Canonical startup coordination module exports.
"""
from .coordinator import (
    AgentStartupCoordinator,
    start_agent,
)
from .context import AgentStartupContext, AgentStartupPhase
from .policy import (
    AgentStartupPolicy,
    AgentStartupMode,
    AgentBridgePolicy,
)
from .outcomes import (
    AgentStartupOutcome,
    AgentStartupOwnershipState,
    AgentStartupHandoffStatus,
)
from .result import AgentStartupResult
from .exceptions import AgentStartupFailure

__all__ = [
    "AgentStartupCoordinator",
    "start_agent",
    "AgentStartupContext",
    "AgentStartupPhase",
    "AgentStartupPolicy",
    "AgentStartupMode",
    "AgentBridgePolicy",
    "AgentStartupOutcome",
    "AgentStartupOwnershipState",
    "AgentStartupHandoffStatus",
    "AgentStartupResult",
    "AgentStartupFailure",
]