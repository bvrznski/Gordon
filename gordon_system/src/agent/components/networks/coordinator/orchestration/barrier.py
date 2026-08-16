# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Synchronization Barrier Model
=============================

The SynchronizationBarrier coordinates semantic readiness across stages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from .enums import SynchronizationPolicy


@dataclass(frozen=True, slots=True)
class SynchronizationBarrier:
    """
    Immutable synchronization barrier model.
    
    BARRIER-LAW-001: Every synchronization barrier possesses one stable identity
    BARRIER-LAW-002: Barrier participants shall remain explicit
    BARRIER-LAW-003: Barrier release conditions shall remain explicit
    BARRIER-LAW-004: Barrier completion shall require all mandatory participants
    
    BARRIER-INV-001: Barrier is immutable (deeply frozen)
    BARRIER-INV-002: Barrier has no runtime references
    """
    
    identity: str = ""
    """Unique identity for this barrier."""
    
    participating_stages: tuple[str, ...] = ()
    """Stage identities that must reach this barrier."""
    
    required_participants: int = 0
    """Minimum number of participants required to release the barrier."""
    
    release_conditions: tuple[str, ...] = ()
    """Conditions that must be satisfied for release."""
    
    timeout_policy: str = ""
    """Policy for handling timeouts."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    status: str = "pending"
    """Current status of the barrier."""
    
    @classmethod
    def create(
        cls,
        identity: str,
        participating_stages: tuple[str, ...],
        required_participants: int = 0,
        release_conditions: tuple[str, ...] = (),
        timeout_policy: str = "",
    ) -> SynchronizationBarrier:
        """
        Create a new synchronization barrier.
        
        Args:
            identity: Unique barrier identity
            participating_stages: Stages that must reach the barrier
            required_participants: Minimum participants to release (0 = all)
            release_conditions: Conditions for releasing the barrier
            timeout_policy: Policy for handling timeouts
            
        Returns:
            A new SynchronizationBarrier instance
        """
        if required_participants == 0:
            required_participants = len(participating_stages)
        
        return cls(
            identity=identity,
            participating_stages=tuple(participating_stages),
            required_participants=required_participants,
            release_conditions=tuple(release_conditions),
            timeout_policy=timeout_policy,
            provenance_ref="",
            status="pending",
        )
    
    def __str__(self) -> str:
        return f"SynchronizationBarrier({self.identity}, stages={len(self.participating_stages)}, status={self.status})"