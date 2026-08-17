# Gordon Phase 5.7.9-R: Consciousness System Interfaces (Destination Scaffolding)

"""
Public protocol definitions for the Consciousness system.

This module establishes stable, path-independent contracts that will
be used by both the source implementation and destination implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Protocol


# =============================================================================
# CANONICAL SYSTEM IDENTITIES (Path-Independent)
# =============================================================================

SYSTEM_ID = "system.consciousness"
"""Stable semantic system identity for the Consciousness system."""

CAPABILITY_ID = "capability.consciousness"
"""Stable semantic capability identity for Consciousness."""


# =============================================================================
# PUBLIC FACADE PROTOCOL
# =============================================================================

class ConsciousnessFacadeProtocol(Protocol):
    """
    Protocol for the Consciousness facade that must be satisfied by both
    source and destination implementations.
    
    This protocol ensures interface compatibility during migration while
    allowing different internal implementations.
    """

    def initialize(self) -> Tuple[bool, Optional[str]]:
        """Initialize the consciousness system."""
        ...

    def start(self) -> Tuple[bool, Optional[str]]:
        """Start the consciousness system."""
        ...

    def stop(self) -> Tuple[bool, Optional[str]]:
        """Stop the consciousness system."""
        ...


# =============================================================================
# SYSTEM DESCRIPTOR (Destination-Ready)
# =============================================================================

@dataclass(frozen=True)
class ConsciousnessSystemDescriptor:
    """
    Immutable descriptor for the Consciousness system.
    
    This descriptor is compatible with the canonical system registry and
    is prepared for Phase 5.7.9-T registration.
    """

    # Identity
    system_id: str = SYSTEM_ID
    """Canonical system ID (path-independent)."""
    
    system_kind: str = "system"
    """System kind identifier."""
    
    provider_path: Optional[str] = None
    """Implementation provider path (set during Phase 5.7.9-T migration)."""
    
    # Classification
    capability_id: str = CAPABILITY_ID
    """Associated capability ID."""
    
    emergent_capability: bool = True
    """Whether this system provides an emergent composite capability."""
    
    # Lifecycle
    lifecycle_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Requirements before system is considered ready."""
    
    execution_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Execution context requirements."""
    
    # Dependencies
    required_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Other systems that must be running."""
    
    optional_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Optional peer systems."""
    
    # Integration
    health_participation: bool = True
    diagnostic_participation: bool = True
    integrity_participation: bool = True
    continuity_participation: bool = True
    
    # Metadata
    contract_version: str = "5.7.9-R"
    """Contract version for this descriptor."""
    
    generation: int = 1
    """Descriptor generation (incremented on breaking changes)."""
    
    # Status
    active: bool = False
    """Whether system is currently active (False during remediation)."""
    
    provider_active: bool = False
    """ Whether provider implementation is active."""

    # Constants
    _DEFAULT_SYSTEM_ID = SYSTEM_ID
    
    @classmethod
    def destination_ready(cls, provider_path: str) -> "ConsciousnessSystemDescriptor":
        """
        Create a descriptor ready for Phase 5.7.9-T registration.
        
        Args:
            provider_path: Python path to the implementation provider class
        """
        return cls(
            system_id=cls._DEFAULT_SYSTEM_ID,
            provider_path=provider_path,
            active=False,  # Inactive until Phase 5.7.9-T activation
            provider_active=False,
        )

    @classmethod
    def inactive(cls) -> "ConsciousnessSystemDescriptor":
        """Create an inactive descriptor for remediation-phase scaffolding."""
        return cls(
            system_id=cls._DEFAULT_SYSTEM_ID,
            active=False,
            provider_active=False,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "SYSTEM_ID",
    "CAPABILITY_ID",
    "ConsciousnessFacadeProtocol",
    "ConsciousnessSystemDescriptor",
)