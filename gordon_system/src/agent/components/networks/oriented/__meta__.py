# Oriented Network Package Metadata
# ==================================

"""
Package metadata for OrientedNetwork - Gordon's intentional orientation
coordination network.
"""

__version__: str = "0.1.0-alpha"
"""Package version string following semantic versioning."""

PACKAGE_NAME: str = "oriented"
"""Canonical package identifier."""

DISPLAY_NAME: str = "Oriented Network"
"""Human-readable display name for the package."""

ARCHITECTURAL_LAYER: str = "cognitive_network"
"""Architectural layer to which this package belongs."""

PACKAGE_STATUS: str = "scaffold"
"""Current implementation status of the package."""

IMPLEMENTATION_PHASE: str = "4.7.1"
"""Phase during which this package was scaffolded."""

CANONICAL: bool = True
"""Indicates whether this is a canonical implementation."""

LEGACY_NAMES: tuple[str, ...] = (
    "directed",
    "Directed Network",
    "Task Positive Network",
    "TPN",
)
"""Historical names that have been retired in favor of this package."""

RESPONSIBILITIES: tuple[str, ...] = (
    "intentional orientation coordination",
    "Goal-oriented context coordination",
    "externally directed cognition coordination",
)
"""Primary responsibilities of the Oriented Network."""

FORBIDDEN_RESPONSIBILITIES: tuple[str, ...] = (
    "capability implementation",
    "persistent knowledge ownership",
    "Memory ownership",
    "Planning implementation",
    "Reasoning implementation",
    "Decision implementation",
    "Action execution",
    "runtime scheduling",
    "transport implementation",
)
"""Responsibilities explicitly forbidden to this package."""

ARCHITECTURAL_OWNERSHIP: str = "Oriented Network"
"""Canonical owner of the semantic orientation contract."""