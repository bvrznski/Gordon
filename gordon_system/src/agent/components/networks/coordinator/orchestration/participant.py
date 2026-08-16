# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Cycle Participant Model
=======================

The CycleParticipant represents a cognitive network participating in an orchestration cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from .identity import ParticipantIdentity
from .enums import ParticipantRole, Status


@dataclass(frozen=True, slots=True)
class CycleParticipant:
    """
    Immutable participant model for a cognitive cycle.
    
    PARTICIPANT-LAW-001: Every participant represents exactly one cognitive network
    PARTICIPANT-LAW-002: Participation roles remain explicit
    PARTICIPANT-LAW-003: Mandatory participants shall never be silently removed
    PARTICIPANT-LAW-004: Optional participants remain distinguishable
    PARTICIPANT-LAW-005: Participant capabilities remain explicit
    PARTICIPANT-LAW-006: Participant status shall preserve provenance
    
    PARTICIPANT-INV-001: Participant is immutable (deeply frozen)
    PARTICIPANT-INV-002: Participant has no runtime references
    """
    
    identity: ParticipantIdentity
    """Unique identity for this participant."""
    
    network_ref: str = ""
    """Reference to the cognitive network."""
    
    role: str = ""  # ParticipantRole.*
    """Participant's role in the cycle."""
    
    priority: int = 0
    """Priority level (higher = more important)."""
    
    is_mandatory: bool = True
    """Whether this participant is mandatory for completion."""
    
    dependencies: Tuple[str, ...] = ()
    """References to participants whose results this depends on."""
    
    capabilities: Tuple[str, ...] = ()
    """Capabilities this participant provides."""
    
    status: str = Status.CREATED.value
    """Current status of this participant (from Status enum)."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        network_ref: str,
        role: str,
        is_mandatory: bool = True,
        priority: int = 0,
        dependencies: tuple[str, ...] = (),
        capabilities: tuple[str, ...] = (),
    ) -> CycleParticipant:
        """
        Create a new cycle participant.
        
        Args:
            network_ref: Reference to cognitive network
            role: Role in the cycle
            is_mandatory: Whether mandatory
            priority: Priority level (0 = default)
            dependencies: References to dependent participants
            capabilities: Capabilities provided
            
        Returns:
            A new CycleParticipant instance
        """
        identity = ParticipantIdentity.create(
            network_ref=network_ref,
            role=role,
            is_mandatory=is_mandatory,
        )
        
        return cls(
            identity=identity,
            network_ref=network_ref,
            role=role,
            priority=priority,
            is_mandatory=is_mandatory,
            dependencies=tuple(dependencies),
            capabilities=tuple(capabilities),
            status=Status.CREATED.value,
            provenance_ref="",
        )
    
    def __str__(self) -> str:
        return f"CycleParticipant({self.identity}, role={self.role}, status={self.status})"


# Alias for type clarity
ParticipantStatus = Status