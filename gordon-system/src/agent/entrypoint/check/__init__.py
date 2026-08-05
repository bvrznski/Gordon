"""Gordon Agent Entrypoint Preflight and Compilation Authority.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

This package provides the canonical Agent startup preflight and compilation
authority for Gordon autonomous cognitive agents.

Preflight Responsibilities
--------------------------
The preflight subsystem determines whether initialization may safely be attempted.
It does NOT:
- Initialize the Agent
- Load Agent components  
- Prove runtime integrity or readiness
- Open admission or start cognition

Preflight DOES:
- Verify source and artifact validity
- Compile approved Python targets
- Validate startup structure
- Inspect package metadata
- Evaluate static environment prerequisites
- Detect blocking startup conditions
- Produce immutable provenance-preserving preflight results

Architecture Boundaries
-----------------------
This module owns:
- Canonical Agent startup preflight orchestration
- Compilation-policy execution
- Static source validation
- Package-layout validation  
- Startup-contract validation
- Environment prerequisite validation
- Preflight diagnostics and result publication

This module does NOT own:
- Process entrypoint logic (main.py)
- Component discovery or loading (entrypoint/load/)
- Agent Core construction authority (components/core/)
- Runtime assembly, activation, or cognition

Public API
----------
- AgentPreflightChecker: Canonical preflight checker class
- check_agent(request): Top-level preflight invocation function
- AgentPreflightRequest: Immutable preflight request model
- AgentPreflightResult: Immutable preflight result model  
- AgentPreflightPolicy: Preflight policy configuration
- AgentCompilationPolicy: Compilation policy configuration

Import-time behavior:
- No active preflight checks at import time
- No source scanning at import time
- No environment probing at import time
- No subprocess creation at import time
- No resource allocation at import time

Canonical Startup Path:
    Immutable Agent launch request
        ↓
    agent.entrypoint.check.AgentPreflightChecker
        ↓
    Immutable Agent preflight result (PASS/PASS_WITH_WARNINGS/BLOCKED/FAILED)
        ↓
    Eligibility decision
        ↓
    agent.entrypoint.init initialization chain
"""

from __future__ import annotations

# Core types and models
from .types import (
    AgentPreflightOutcome,
    AgentPreflightPhase,
    AgentPreflightCheckKind,
    AgentPreflightSeverity,
    AgentCompilationPolicy,
    # Identity classes
    AgentLaunchIdentity,
    AgentProcessIdentity,
    AgentRuntimeIdentity,
)

# Request/Result contracts
from .request import AgentPreflightRequest
from .result import AgentPreflightResult

# Policy models  
from .policy import AgentPreflightPolicy, AgentCompilationPolicy

# Check system
from .checks import (
    AgentPreflightCheck,
    AgentPreflightCheckResult,
    PreflightCheckRegistry,
    get_default_check_registry,
)

# Context for check execution
from .context import AgentPreflightContext

# Exception types
from .exceptions import (
    AgentPreflightError,
    PreflightRequestError,
    PreflightPolicyError,
    PreflightCompilationError,
    PreflightTimeoutError,
    PreflightCancellationError,
    PreflightInternalError,
)

# Main checker
from .checker import AgentPreflightChecker, check_agent

__all__ = [
    # Core types
    "AgentPreflightOutcome",
    
    # Registry
    "get_default_check_registry",
    "AgentPreflightPhase", 
    "AgentPreflightCheckKind",
    "AgentPreflightSeverity",
    "AgentCompilationPolicy",
    # Identity classes
    "AgentLaunchIdentity",
    "AgentProcessIdentity",
    "AgentRuntimeIdentity",
    
    # Contracts
    "AgentPreflightRequest",
    "AgentPreflightResult",
    
    # Policy
    "AgentPreflightPolicy",
    "AgentCompilationPolicy",
    
    # Check system
    "AgentPreflightCheck",
    "AgentPreflightCheckResult",
    "PreflightCheckRegistry",
    
    # Context
    "AgentPreflightContext",
    
    # Exceptions
    "AgentPreflightError",
    "PreflightRequestError",
    "PreflightPolicyError",
    "PreflightCompilationError",
    "PreflightTimeoutError",
    "PreflightCancellationError",
    "PreflightInternalError",
    
    # Checker
    "AgentPreflightChecker",
    "check_agent",
]