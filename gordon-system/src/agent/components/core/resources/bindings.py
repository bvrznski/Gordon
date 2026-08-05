# Core Resource Binding
# =====================
"""
Resource binding connects allocations to consumers.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time


@dataclass(frozen=True)
class ResourceBindingRequest:
    """
    Request for a resource binding.
    
    This is the INPUT - everything needed to validate and create a binding.
    """
    runtime_id: str
    
    allocation_id: str         # Which allocation to bind
    consumer_id: str           # Who will consume this resource
    
    # Binding context
    binding_type: str = "direct"  # direct, indirect, proxy
    
    # Validation hints
    lease_required: bool = True   # Must have active lease?
    
    correlation_id: Optional[str] = None


@dataclass(frozen=True)
class ResourceBindingState(Enum):
    """States of a resource binding."""
    PENDING = "pending"           # Requested, not yet validated
    VALIDATED = "validated"       # All checks passed
    ACTIVE = "active"             # Binding is active
    EXPIRED = "expired"           # Lease or allocation expired
    REVOKED = "revoked"           # Explicitly revoked


@dataclass(frozen=True)
class ResourceBinding:
    """
    A binding between an allocation and a consumer.
    
    This enables the consumer to use the resource through the allocation.
    """
    binding_id: str
    
    runtime_id: str
    allocation_id: str          # The underlying allocation
    consumer_id: str            # Who can use this via the binding
    
    bound_at_utc: float
    expires_at_utc: Optional[float] = None  # When lease expires
    
    state: ResourceBindingState = ResourceBindingState.ACTIVE
    
    # Provenance
    source_transaction_id: str = ""


@dataclass(frozen=True)
class ResourceBindingResult(Enum):
    """Result of a binding operation."""
    SUCCESS = "success"
    ALLOCATION_NOT_FOUND = "allocation_not_found"
    LEASE_NOT_ACTIVE = "lease_not_active"
    CONSUMER_INVALID = "consumer_invalid"
    GENERATION_STALE = "generation_stale"
    STATE_MISMATCH = "state_mismatch"


@dataclass(frozen=True)
class ResourceBindingFailure:
    """
    Record of a binding failure.
    """
    failure_id: str
    failure_type: str           # See ResourceBindingResult enum values
    reason: str
    
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "ResourceBindingRequest",
    "ResourceBindingState",
    "ResourceBinding",
    "ResourceBindingResult",
    "ResourceBindingFailure",
]


class BindingId(str):
    """Unique identifier for a binding."""
    
    @classmethod
    def generate(cls) -> "BindingId":
        return cls(value=f"bind_{time.time():.0f}_{id(cls)}")