# Economic Session Descriptor - Phase 7.48 Part 1
# ===============================================

"""
Economic Session Descriptor.

Every economic reasoning process occurs inside an Economic Session.
The session defines:
    - available resources
    - economic objectives
    - constraints
    - participants
    - allocation goals
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EconomicReasoningKind(Enum):
    """Categories of economic reasoning operations."""
    
    RESOURCE_ASSESSMENT = "resource_assessment"     # What resources are available?
    VALUE_ANALYSIS = "value_analysis"               # How are resources valued?
    ALLOCATION_ANALYSIS = "allocation_analysis"     # How should resources be allocated?
    INCENTIVE_ANALYSIS = "incentive_analysis"       # What incentives drive behavior?
    MARKET_ANALYSIS = "market_analysis"             # What market mechanisms apply?
    PRICING_ANALYSIS = "pricing_analysis"           # What are the prices?
    OPTIMIZATION = "optimization"                   # How to optimize allocation?
    
    # Combined reasoning modes
    COMPREHENSIVE_ECONOMIC = "comprehensive_economic"
    RESOURCE_ALLOCATION = "resource_allocation"


class EconomicLifecycleState(Enum):
    """Economic session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    MODELING = "modeling"
    VALUATING = "valuating"
    ALLOCATING = "allocating"
    OPTIMIZING = "optimizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class EconomicSessionDescriptor:
    """
    Descriptor exposing economic session metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning classification
    reasoning_kind: EconomicReasoningKind   # What kind of economic reasoning?
    reasoning_mode: Optional[str] = None    # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: EconomicLifecycleState = EconomicLifecycleState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if reasoning completed."""
        return self.lifecycle_state == EconomicLifecycleState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == EconomicLifecycleState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_kind: EconomicReasoningKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> EconomicSessionDescriptor:
        """Create a new economic session descriptor."""
        return cls(
            descriptor_id=f"descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_kind=reasoning_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: EconomicLifecycleState) -> EconomicSessionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == EconomicLifecycleState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EconomicSessionDescriptor",
    "EconomicReasoningKind",
    "EconomicLifecycleState",
]