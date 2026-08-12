# Runtime State Package Metadata
# ===============================

"""
Package metadata for Core runtime state infrastructure.

This module is declarative only - it describes the package, not implements it.
"""

# Canonical package identification
CANONICAL_NAME = "gordon.system.src.agent.components.core.runtime_state"

# Semantic owner - who owns this package?
SEMANTIC_OWNER = "core"

# Package purpose and scope
PURPOSE = (
    "Phase 3.2 infrastructure for domain-neutral runtime structures:\n"
    "- Entity registries with explicit registration semantics\n"
    "- Runtime context transport (immutable, versioned)\n"
    "- Runtime state management (single authoritative owner)\n"
    "- Shutdown and cancellation signaling\n"
    "- Runtime-scoped resource management"
)

# Package maturity
MATURITY = "alpha"  # alpha, beta, stable

# Stability level
STABILITY = "unstable"  # unstable, developing, stable

# Dependencies (packages this one depends on)
DEPENDENCIES = [
    "gordon.system.src.agent.types",  # Core types
]

# Documentation references
DOCUMENTATION = {
    "architecture": "docs/agent/architecture/runtime-state.md",
    "phase": "docs/agent/architecture/phase-3.2-report.md",
}

# Package status
STATUS = "in_development"

# Release information
RELEASE_VERSION = "0.1.0"