# Executive Network Package Metadata
# ====================================

"""
Package metadata for the Executive Network.

This file contains static metadata about the package itself,
including version, authors, dependencies, and architectural notes.
"""

# =============================================================================
# PACKAGE IDENTIFICATION
# =============================================================================

__title__: str = "executive"
"""Canonical package name (lowercase)."""

__package_name__: str = "Executive Network"
"""Human-readable package name."""

__version__: str = "0.1.0-alpha"
"""Package version following semantic versioning."""

__phase__: str = "4.4.1"
"""Architecture phase identifier."""

# =============================================================================
# ARCHITECTURAL INFORMATION
# =============================================================================

__architectural_role__: str = (
    "Gordon's primary semantic control Network - maintains and evaluates "
    "the currently active executive organization of cognition."
)

__canonical_name__: str = "ExecutiveNetwork"
"""Canonical implementation type name."""

__package_path__: str = "gordon_system.src.agent.networks.executive"
"""Fully qualified package import path."""

# =============================================================================
# VERSION AND RELEASE
# =============================================================================

__version_tuple__: tuple = (0, 1, 0, "alpha")
"""Version as tuple for programmatic access."""

__release_date__: str = "2026-08-15"
"""Release date placeholder."""

__status__: str = "planning"
"""Development status: planning | pre-alpha | alpha | beta | stable."""

# =============================================================================
# OWNERSHIP AND MAINTENANCE
# =============================================================================

__owner__: str = "Gordon Cognitive Architecture Team"
"""Package ownership declaration."""

__maintainer__: str = "Gordon Development Team"
"""Current maintainers."""

# =============================================================================
# DEPENDENCIES (runtime)
# =============================================================================

__dependencies__: tuple = (
    "gordon_system.src.agent.architecture",
)
"""Direct runtime dependencies."""

__optional_dependencies__: dict = {
    "testing": ("pytest",),
}
"""Optional development/test dependencies."""

# =============================================================================
# EXPORT POLICY
# =============================================================================

__public_api__: tuple = (
    "ExecutiveNetworkMetadata",
    "ExecutiveNetworkId",
    "ExecutiveStateReference",
    "ExecutiveContextReference",
    "ExecutiveTaskSetReference",
    "ExecutiveRequestReference",
    "ExecutiveResultReference",
    "ExecutiveProductReference",
    "ExecutiveProposalReference",
    "ExecutiveOutcomeReference",
    "ExecutiveContinuationReference",
    "ExecutiveAuthorityReference",
    "ExecutiveMode",
    "ExecutiveProductKind",
    "ExecutiveOutcomeKind",
    "ExecutiveContinuationKind",
    "ConflictKind",
    "ControlDemandAssessment",
    "DecisionReadinessAssessment",
    "ExecutiveNetworkConfig",
    "ExecutiveNetwork",
    "_PlaceholderExecutiveNetwork",
    "initialize_network",
)
"""Explicitly declared public API for external consumers."""

__internal__: tuple = (
    # Internal types and implementation details
)
"""Internal types not part of the public API."""

# =============================================================================
# ARCHITECTURAL INVARIANTS (Phase 4.4.1)
# =============================================================================

__invariants__: dict = {
    "EXEC-ARCH-INV-001": "Canonical subsystem name is Executive Network",
    "EXEC-ARCH-INV-002": "Executive control is a function, not the complete identity",
    "EXEC-ARCH-INV-003": "Semantic coordination only - no runtime orchestration",
    "EXEC-ARCH-INV-004": "No scheduling, workers, processes, timers, polling",
    "EXEC-ARCH-INV-005": "No ExecutionThread, Loop, or Cycle progression",
    "EXEC-ARCH-INV-006": "No direct invocation of concrete subsystems",
    "EXEC-ARCH-INV-007": "No direct action execution",
    "EXEC-ARCH-INV-008": "No capability or tool registry ownership",
    "EXEC-ARCH-INV-009": "No generic component lifecycle ownership",
    "EXEC-ARCH-INV-010": "Semantic activation distinct from runtime activation",
}

# =============================================================================
# IMPORT SAFETY GUARD
# =============================================================================

__import_behavior__: str = (
    "Import performs no runtime activation, scheduling, provider discovery, "
    "model loading, or subsystem invocation."
)

__no_side_effects__: bool = True
"""Import has zero side effects."""

__runtime_activation_required__: bool = False
"""Runtime behavior requires explicit initialization via initialize_network()."""

# =============================================================================
# PHASE ROADMAP
# =============================================================================

__upcoming_phases__: tuple = (
    "4.4.2  Executive State and Executive Context",
    "4.4.3  Executive Task Sets and Active Programs",
    "4.4.4  Goal, Commitment, and Priority Coordination",
    "4.4.5  Conflict Monitoring and Executive Demand",
    "4.4.6  Performance, Outcome, and Error Monitoring",
    "4.4.7  Executive Control Allocation and Modulation",
    "4.4.8  Cognitive Flexibility, Switching, and Inhibition",
    "4.4.9  Strategy and Policy Coordination",
    "4.4.10 Decision and Action-Selection Coordination",
    "4.4.11 Attention, Motivation, Workspace, and Working-Memory Coordination",
    "4.4.12 Executive Loop, Cycle, and Thread Integration",
    "4.4.13 Runtime-Neutral Executive Network Implementation",
    "4.4.14 Executive Network Integration Contracts",
    "4.4.15 Executive Network Behavioral Validation",
    "4.4.16 Executive Network Architectural Audit",
    "4.4.17 Executive Network Architectural Remediation",
    "4.4.18 Executive Network Final Certification",
)
"""Future phases in the Executive Network lifecycle."""