# Fault Model - Phase 7.39
# =======================

"""
Fault management models.

Defines:
    - FaultModel: A model of a localized fault
    - FaultSeverity: Impact level of the fault
    - FaultKind: Category of the fault
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class FaultKind(Enum):
    """Kinds of faults."""
    
    COMPONENT = "component"       # Component-level failure
    CONNECTION = "connection"     # Connection/link failure
    CONFIGURATION = "configuration"  # Configuration error
    STATE = "state"               # State corruption or inconsistency
    RESOURCE = "resource"         # Resource exhaustion or misallocation


class FaultSeverity(Enum):
    """Severity levels for faults."""
    
    MINOR = "minor"           # Non-critical, graceful degradation possible
    MODERATE = "moderate"     # Significant impact, requires attention
    SEVERE = "severe"         # Critical impact, immediate action required
    CRITICAL = "critical"     # System failure, urgent recovery needed


@dataclass(frozen=True)
class FaultModel:
    """
    Model of a localized fault.
    
    Each fault includes:
        - Identity and localization
        - Affected components
        - Probability and priority estimates
        - Provenance tracking
    """
    
    fault_id: str
    semantic_identity: str
    
    # Localization
    fault_kind: FaultKind
    localized_at: List[str]  # Component IDs where fault is localized
    
    # Probability and impact
    fault_probability: float = 1.0  # 0.0 to 1.0 (diagnostic confidence)
    fault_priority: int = 5         # 1-10, 10 = highest priority
    
    # Dependencies and isolation
    depends_on: List[str] = field(default_factory=list)  # Faults this depends on
    isolates_from: List[str] = field(default_factory=list)  # Components isolated
    
    # Context
    timestamp_utc: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_critical(self) -> bool:
        """Check if fault is critical."""
        return self.fault_priority >= 8 or \
               self.fault_kind == FaultKind.COMPONENT
    
    @classmethod
    def create(
        cls,
        localized_at: List[str],
        fault_kind: FaultKind = FaultKind.COMPONENT,
        fault_probability: float = 1.0,
        fault_priority: int = 5,
        depends_on: Optional[List[str]] = None,
        isolates_from: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> FaultModel:
        """Create a new fault model."""
        return cls(
            fault_id=f"fault:{uuid.uuid4().hex[:16]}",
            semantic_identity=f"{fault_kind.value}:{uuid.uuid4().hex[:8]}",
            fault_kind=fault_kind,
            localized_at=localized_at,
            fault_probability=fault_probability,
            fault_priority=fault_priority,
            depends_on=depends_on or [],
            isolates_from=isolates_from or [],
            context=context or {},
        )
    
    def update_confidence(self, new_confidence: float) -> FaultModel:
        """Return updated fault with new probability estimate."""
        return dataclass_replace(
            self,
            fault_probability=new_confidence,
        )


@dataclass(frozen=True)
class FaultSetIdentity:
    """
    Identity for a set of faults.
    
    Allows grouping and comparison of fault sets.
    """
    
    set_id: str
    semantic_identity: str
    created_at_utc: float
    
    @classmethod
    def create(cls, semantic_identity: str) -> FaultSetIdentity:
        """Create a fault set identity."""
        return cls(
            set_id=f"fault_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "FaultKind",
    "FaultSeverity",
    "FaultModel",
    "FaultSetIdentity",
]