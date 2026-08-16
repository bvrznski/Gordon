# Oriented Network Configuration
# ==============================

"""
Configuration types for the OrientedNetwork.

Phase 4.7.1: Minimal Configuration Scaffold

The configuration establishes immutable parameters that control the
canonical Oriented Network instance.

NOTE: This is a scaffold. Behavioral configuration belongs to later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# PHASE 4.7.1: Configuration SCAFFOLD
# =============================================================================

@dataclass(frozen=True)
class OrientedNetworkConfiguration:
    """
    Immutable configuration for the Oriented Network scaffold.

    This configuration contains only structural parameters required for
    canonical operation. Behavioral configuration belongs to future phases.
    """

    schema_version: int = 1
    """Schema version for configuration serialization compatibility."""

    enabled: bool = True
    """Whether this network is active and should participate in coordination."""

    strict_validation: bool = False
    """Whether to enforce strict validation of all inputs and states."""

    bounded_diagnostic: bool = True
    """Whether to emit diagnostic information for canonical operations."""

    def __post_init__(self) -> None:
        """Validate configuration constraints."""
        if self.schema_version < 1:
            raise ValueError("Schema version must be >= 1")

    @classmethod
    def default(cls) -> "OrientedNetworkConfiguration":
        """Return the default configuration for the Oriented Network scaffold."""
        return cls()

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "OrientedNetworkConfiguration":
        """
        Construct a configuration from a dictionary.

        Args:
            data: Dictionary containing configuration parameters.

        Returns:
            A new OrientedNetworkConfiguration instance.

        Raises:
            TypeError: If required keys are missing or have wrong types.
            ValueError: If configuration constraints are violated.
        """
        if not isinstance(data, dict):
            raise TypeError("Configuration must be a dictionary")

        # Extract known keys with type checking
        kwargs: dict[str, object] = {}

        if "schema_version" in data:
            value = data["schema_version"]
            if not isinstance(value, int):
                raise TypeError("schema_version must be an integer")
            kwargs["schema_version"] = value

        if "enabled" in data:
            value = data["enabled"]
            if not isinstance(value, bool):
                raise TypeError("enabled must be a boolean")
            kwargs["enabled"] = value

        if "strict_validation" in data:
            value = data["strict_validation"]
            if not isinstance(value, bool):
                raise TypeError("strict_validation must be a boolean")
            kwargs["strict_validation"] = value

        if "bounded_diagnostic" in data:
            value = data["bounded_diagnostic"]
            if not isinstance(value, bool):
                raise TypeError("bounded_diagnostic must be a boolean")
            kwargs["bounded_diagnostic"] = value

        return cls(**kwargs)

    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation of the configuration."""
        return {
            "schema_version": self.schema_version,
            "enabled": self.enabled,
            "strict_validation": self.strict_validation,
            "bounded_diagnostic": self.bounded_diagnostic,
        }