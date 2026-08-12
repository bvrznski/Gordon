# Core Ownership Model
# ====================
"""
Immutable ownership records with transfer protocol.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time


@dataclass(frozen=True)
class OwnershipKind(Enum):
    """Kinds of ownership."""
    EXCLUSIVE = "exclusive"         # Single owner
    SHARED = "shared"               # Multiple owners can use simultaneously
    DELEGATED = "delegated"         # Owner delegates to another
    TEMPORARY = "temporary"         # Temporary ownership until transfer


@dataclass(frozen=True)
class ResourceOwnership:
    """
    Immutable record of resource ownership.
    
    Every allocated resource has exactly one authoritative owner.
    Ownership is distinct from usage rights (leases).
    """
    allocation_id: str
    owner_id: str
    
    kind: OwnershipKind = OwnershipKind.EXCLUSIVE
    
    created_at_utc: float = field(default_factory=time.time)
    
    # Transfer tracking
    transfer_epoch: int = 1          # Increments on each transfer
    
    # Source
    source_transaction_id: str = ""


@dataclass(frozen=True)
class OwnershipTransfer:
    """
    Record of an ownership transfer.
    
    Controls the transfer pipeline to ensure no split-brain.
    """
    transfer_id: str
    allocation_id: str
    
    from_owner_id: str
    to_owner_id: str
    
    source_epoch: int               # Epoch at time of transfer request
    target_epoch: int               # New epoch after transfer
    
    requested_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    status: str = "pending"         # pending, verified, failed


@dataclass(frozen=True)
class OwnershipConflict:
    """
    Record of an ownership conflict (split-brain detected).
    """
    conflict_id: str
    allocation_id: str
    conflicting_owners: Tuple[str, ...]
    
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "OwnershipKind",
    "ResourceOwnership",
    "OwnershipTransfer",
    "OwnershipConflict",
]


class OwnerId(str):
    """Unique identifier for an owner (task, service, etc.)."""
    pass


class GenerationEpoch(int):
    """
    Epoch counter for split-brain fencing.
    
    Each time a new authority is activated, the epoch increments.
    Old attempts with lower epochs are rejected.
    """
    
    def next(self) -> "GenerationEpoch":
        return GenerationEpoch(self + 1)