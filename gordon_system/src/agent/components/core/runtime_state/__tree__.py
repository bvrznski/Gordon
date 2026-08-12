# Runtime State Package Tree Contract
# =====================================

"""
Package structural contract for Core runtime state infrastructure.

This module declares the package structure, not implements it.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import types only for type checking
    from typing import List, Dict, Optional


# Canonical package identification
CANONICAL_PATH = "src/agent/components/core/runtime_state"
SEMANTIC_OWNER = "core"

# Package kind and purpose
PACKAGE_KIND = "infrastructure"
PURPOSE = (
    "Phase 3.2 runtime infrastructure for:\n"
    "- Entity registries with explicit semantics\n"
    "- Runtime context transport (immutable, versioned)\n"
    "- Runtime state management (single authority)\n"
    "- Shutdown/cancellation signaling\n"
    "- Runtime-scoped resources"
)

# Parent package
PARENT = "src/agent/components/core"

# Child packages and modules
CHILDREN = [
    # Core implementation modules
    "registry.py",      # Registry with explicit mutation phases
    "context.py",       # Runtime context transport
    "signals.py",       # Cancellation and shutdown signals
    "resources.py",     # Resource scope abstraction
]

# Required files
REQUIRED_FILES = [
    "__init__.py",
    "__meta__.py",
    "__tree__.py",
]

# Allowed modules (no implementation in these)
ALLOWED_MODULES = []

# Forbidden modules (must not exist)
FORBIDDEN_MODULES = [
    "load.py",          # No import-time execution
    "__main__.py",      # Not executable package
]

# Dependencies by prefix
PERMITTED_DEPENDENCIES = [
    "gordon.system.src.agent.types",
    "gordon.system.src.agent.contracts",
    "gordon.system.src.agent.exceptions",
]

FORBIDDEN_DEPENDENCIES = [
    # No dependency on capabilities layer (lower cannot depend on higher)
    # No runtime implementations in this infrastructure package
]

# Local invariants
LOCAL_INVARIANTS = [
    "One authoritative registry mechanism",
    "Runtime context is immutable and versioned",
    "Runtime state has one authoritative owner per instance",
    "Shutdown and cancellation remain distinct signals",
    "Resource scope provides explicit ownership with deterministic release",
    "No import-time registration or runtime construction",
]

# Exports (public API)
PUBLIC_API = [
    # From __init__.py
    "RegistrationDescriptor",
    "RegistrationResult",
    "RegistrationStatus",
    "RegistryRevision",
    "RuntimeState",
    "RuntimeStateSnapshot",
    "RuntimeStateTransition",
    "RuntimeStateStore",
    
    # From registry.py
    "RegistryPhase",
    "RegistrySnapshot",
    "DuplicateRegistrationError",
    "ConflictingRegistrationError",
    "RegistrySealedError",
    "UnknownEntityError",
    "RegistryWriter",
    "RegistryReader",
    "Registry",
    
    # From context.py
    "ContextScope",
    "ContextEntry",
    "ContextSnapshot",
    "RuntimeContext",
    "ContextBuilder",
    "ContextLocal",
    
    # From signals.py
    "SignalType",
    "SignalOrigin",
    "SignalState",
    "CancellationRequestedError",
    "ShutdownRequestedError",
    "CancellationSignal",
    "ShutdownSignal",
    "CombinedSignal",
    
    # From resources.py
    "ResourceState",
    "ResourceHandle",
    "ResourceAcquisition",
    "ResourceScope",
    "ScopedResourceOwner",
]