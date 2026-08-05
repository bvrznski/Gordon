"""Gordon Agent Entrypoint Shutdown Coordinator.

Phase 3.7.34-I: Agent Entrypoint Shutdown Coordination
======================================================

Canonical Agent entrypoint shutdown coordination authority positioned between
the outer process boundary and detailed Core shutdown subsystems.
"""
from .types import (
    AgentShutdownIntent,
    AgentShutdownRequest,
    AgentShutdownReason,
    AgentShutdownUrgency,
    AgentShutdownMode,
)
from .policy import (
    AgentShutdownPolicy,
    DefaultShutdownPolicy,
)
from .context import (
    AgentShutdownContext,
    AgentShutdownPhase,
)
from .outcomes import (
    AgentShutdownOutcome,
    AgentShutdownOwnershipState,
)
from .exceptions import (
    AgentShutdownError,
    AgentShutdownRequestError,
    AgentShutdownTimeoutError,
    AgentShutdownDuplicateError,
    AgentShutdownIdentityError,
    AgentShutdownOwnershipError,
)
from .result import AgentShutdownResult
from .coordinator import AgentShutdownCoordinator, shutdown_agent
from .duplicate_fence import DuplicateShutdownFence, FenceState, get_fence_state

__all__ = [
    # Types
    "AgentShutdownIntent",
    "AgentShutdownRequest",
    "AgentShutdownReason",
    "AgentShutdownUrgency",
    "AgentShutdownMode",
    # Policy
    "AgentShutdownPolicy",
    "DefaultShutdownPolicy",
    # Context
    "AgentShutdownContext",
    "AgentShutdownPhase",
    # Outcomes
    "AgentShutdownOutcome",
    "AgentShutdownOwnershipState",
    # Exceptions
    "AgentShutdownError",
    "AgentShutdownRequestError",
    "AgentShutdownTimeoutError",
    "AgentShutdownDuplicateError",
    "AgentShutdownIdentityError",
    "AgentShutdownOwnershipError",
    # Result
    "AgentShutdownResult",
    # Coordinator
    "AgentShutdownCoordinator",
    "shutdown_agent",
    # Duplicate Fence
    "DuplicateShutdownFence",
    "FenceState",
    "get_fence_state",
]
