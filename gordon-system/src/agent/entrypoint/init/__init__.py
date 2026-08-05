"""Gordon Agent Entrypoint Initialization.

Phase 3.7.30: Agent Initialization Chain
========================================

This package provides the canonical initialization interface for the Agent.
It coordinates:

1. Immutable initialization request validation
2. Runtime-scoped initialization context creation
3. Deterministic phase sequencing
4. Configuration consumption coordination
5. Loading-subsystem invocation
6. Core-builder invocation
7. Runtime-assembly invocation
8. Structural-verification invocation
9. Integrity-verification invocation
10. Activation invocation
11. Readiness evaluation
12. Admission opening
13. Initialization rollback coordination

Architecture Boundaries
-----------------------
This package owns:
- Canonical Agent initialization coordinator
- Immutable initialization request model
- Runtime-scoped initialization context
- Deterministic phase sequencing
- Failure classification and preservation
- Rollback coordination
- Diagnostics and event emission
- Result construction

This module does NOT own:
- Process entrypoint logic (main.py)
- CLI parsing (main.py)
- Component discovery or loading (entrypoint/load/)
- Agent Core construction authority (components/core/)
- Runtime-state mutation (kernel, scheduler, executor, etc.)
- Operational execution (Agent loop)
- Shutdown sequencing (shutdown authority)

Canonical Initialization Chain:
    Typed launch request
        ↓
    agent.entrypoint.init.initialize_agent()
        ↓
    Immutable initialization request
        ↓
    Validated effective configuration
        ↓
    agent.entrypoint.load() boundary
        ↓
    Constructed components result
        ↓
    Agent Core builder (components/core/)
        ↓
    Runtime assembler
        ↓
    Structural verification
        ↓
    Integrity verification
        ↓
    Activation
        ↓
    Readiness evaluation
        ↓
    Admission opening
        ↓
    Immutable initialized-Agent result

Import-time behavior:
- No configuration resolution at import time
- No component discovery at import time
- No Core construction at import time
- No event loop creation at import time
- No Agent runtime constructed at import time

Public API:
    - AgentInitializer: Canonical initializer class
    - AgentInitializationRequest: Immutable initialization request
    - AgentInitializationContext: Runtime-scoped context
    - AgentInitializationPhase: Phase enumeration
    - AgentInitializationResult: Successful result
    - AgentInitializationFailure: Failure result
    - initialize_agent(): Top-level initialization function

Exports:
    from .types import (
        AgentInitializationRequest,
        AgentInitializationContext,
        AgentInitializationPhase,
        AgentInitializationResult,
        AgentInitializationFailure,
    )
    from .initializer import AgentInitializer
    from .exceptions import *
    from .load import load_components, request_load_plan
"""

from __future__ import annotations

# Import all public types
from .types import (
    AgentInitializationRequest,
    AgentInitializationContext,
    AgentInitializationPhase,
    AgentInitializationResult,
    AgentInitializationFailure,
)

# Import initializer and entry point
from .initializer import AgentInitializer, initialize_agent, get_canonical_initializer

# Import rollback coordinator types
from .initializer import RollbackState, RollbackCoordinator

# Import exceptions for convenience
from .exceptions import *

# Import load subsystem functions (load is at agent.entrypoint.load)
from ..load import load_components, request_load_plan

__all__ = [
    # Types
    "AgentInitializationRequest",
    "AgentInitializationContext",
    "AgentInitializationPhase",
    "AgentInitializationResult",
    "AgentInitializationFailure",
    # Initializer
    "AgentInitializer",
    # Rollback coordinator
    "RollbackState",
    "RollbackCoordinator",
    # Top-level entry points
    "initialize_agent",
    "get_canonical_initializer",
    # Load subsystem
    "load_components",
    "request_load_plan",
    # Exceptions (all from exceptions module)
    "AgentInitializationError",
    "InitializationRequestError",
    "InitializationRequestMissingField",
    "InitializationRequestInvalidValue",
    "InitializationConfigurationError",
    "InitializationConfigurationMissing",
    "InitializationConfigurationInvalid",
    "InitializationContextError",
    "InitializationContextAlreadyCreated",
    "InitializationLoadError",
    "InitializationLoadDescriptorNotFound",
    "InitializationLoadImportError",
    "InitializationLoadDependencyError",
    "InitializationCoreConstructionError",
    "InitializationCoreAuthorityError",
    "InitializationAssemblyError",
    "InitializationAssemblyConnectionError",
    "InitializationVerificationError",
    "InitializationStructureError",
    "InitializationIntegrityError",
    "InitializationActivationError",
    "InitializationActivationTimeout",
    "InitializationReadinessError",
    "InitializationReadinessNotMet",
    "InitializationAdmissionError",
    "InitializationCancellationError",
    "InitializationTimeoutError",
    "InitializationRollbackError",
    "InitializationInternalError",
]