# Oriented Network State
# =======================

"""
State types for the OrientedNetwork.

Phase 4.7.1: Minimal State Scaffold

The state represents the canonical orientation of the network at a point
in time. This is a scaffold - full semantic content belongs to later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# PHASE 4.7.1: State LIFECYCLE ENUM
# =============================================================================

class OrientedNetworkLifecycle(Enum):
    """
    Lifecycle states for the Oriented Network.

    The network transitions through these states during its lifetime.
    """

    UNINITIALIZED = "uninitialized"
    """Initial state before initialization."""

    INITIALIZED = "initialized"
    """Configuration applied, ready for activation."""

    ACTIVE = "active"
    """Network is actively coordinating orientation."""

    INACTIVE = "inactive"
    """Network has been deactivated but not shutdown."""

    SUSPENDED = "suspended"
    """Network temporarily suspended (for future phases)."""

    TERMINATED = "terminated"
    """Network has been permanently terminated."""


# =============================================================================
# PHASE 4.7.1: STATE IMPLEMENTATION STATUS
# =============================================================================

class OrientedNetworkImplementationStatus(Enum):
    """
    Implementation completeness status for the network.
    """

    SCAFFOLD = "scaffold"
    """Phase 4.7.1 scaffold - no behavior implemented."""

    SEMANTICS_DEFERRED = "semantics_deferred"
    """State structure exists, semantics deferred to later phases."""

    BEHAVIOR_IMPLEMENTED = "behavior_implemented"
    """Behavioral implementation complete (future phase)."""


# =============================================================================
# PHASE 4.7.1: STATE SCAFFOLD
# =============================================================================

@dataclass(frozen=True)
class OrientedNetworkState:
    """
    Immutable state container for the Oriented Network scaffold.

    This is a minimal scaffold. Future phases extend this with semantic content.
    """

    lifecycle_status: OrientedNetworkLifecycle = OrientedNetworkLifecycle.UNINITIALIZED
    """Current lifecycle status of the network."""

    implementation_status: OrientedNetworkImplementationStatus = (
        OrientedNetworkImplementationStatus.SCAFFOLD
    )
    """Implementation completeness status."""

    is_valid: bool = True
    """Whether this state is considered valid."""

    revision: int = 0
    """State revision for change tracking."""

    provenance: str = "canonical_scaffold_4.7.1"
    """Provenance identifier for the state implementation."""

    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this phase's implementation."""

    def __post_init__(self) -> None:
        """Validate state constraints."""
        if self.revision < 0:
            raise ValueError("Revision must be >= 0")

    @classmethod
    def initial(cls) -> "OrientedNetworkState":
        """
        Return the initial state for a new network instance.
        """
        return cls(
            lifecycle_status=OrientedNetworkLifecycle.UNINITIALIZED,
            implementation_status=OrientedNetworkImplementationStatus.SCAFFOLD,
            is_valid=True,
            revision=0,
            provenance="canonical_scaffold_4.7.1",
        )

    @classmethod
    def active(cls) -> "OrientedNetworkState":
        """
        Return the state representing an active network.
        """
        return cls(
            lifecycle_status=OrientedNetworkLifecycle.ACTIVE,
            implementation_status=OrientedNetworkImplementationStatus.SCAFFOLD,
            is_valid=True,
            revision=0,
            provenance="canonical_scaffold_4.7.1",
        )

    def with_lifecycle(self, new_status: OrientedNetworkLifecycle) -> "OrientedNetworkState":
        """
        Return a new state with the specified lifecycle status.

        Args:
            new_status: The desired lifecycle status.

        Returns:
            A new OrientedNetworkState instance.
        """
        return self._replace(lifecycle_status=new_status)

    def _replace(self, **kwargs) -> "OrientedNetworkState":
        """
        Return a copy of this state with the specified fields replaced.

        This is a minimal replace implementation for frozen dataclass compatibility.
        """
        return type(self)(
            lifecycle_status=kwargs.get("lifecycle_status", self.lifecycle_status),
            implementation_status=kwargs.get("implementation_status", self.implementation_status),
            is_valid=kwargs.get("is_valid", self.is_valid),
            revision=kwargs.get("revision", self.revision),
            provenance=kwargs.get("provenance", self.provenance),
            limitations=kwargs.get("limitations", self.limitations),
        )

    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation of the state."""
        return {
            "lifecycle_status": self.lifecycle_status.value,
            "implementation_status": self.implementation_status.value,
            "is_valid": self.is_valid,
            "revision": self.revision,
            "provenance": self.provenance,
            "limitations": list(self.limitations),
        }