# Containment Management - Phase 7.26
# ====================================

"""
Canonical Containment Management.

Containment determines fault isolation, dependency protection,
resource isolation, behavior freezing, failure propagation
boundaries, and escalation thresholds.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class ContainmentPolicy(Enum):
    """Containment policies for stability."""
    
    ISOLATE = "isolate"              # Completely isolate a failing component
    RATE_LIMIT = "rate_limit"        # Limit resource usage or request rate
    BEHAVIOR_FREEZE = "behavior_freeze"  # Stop behavioral changes temporarily
    RESOURCE_ISOLATION = "resource_isolation"  # Protect resources for critical components
    ESCALATE = "escalate"            # Escalate to higher-level handler


@dataclass(frozen=True)
class ProtectedComponent:
    """A component protected by containment."""
    
    component_id: str
    component_name: str
    protection_type: ContainmentPolicy
    threshold: Optional[float] = None  # When to apply protection (None = always active)


@dataclass(frozen=True)
class ContainmentScope:
    """The scope of a containment policy."""
    
    scope_id: str
    scope_name: str
    
    # Subsystems included in this scope
    subsystems: List[str]
    
    # Priority order for protection
    priority_order: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ContainmentManagement:
    """
    Containment management evaluates containment policies.
    
    Evaluates:
        - Fault isolation boundaries
        - Dependency protection requirements
        - Resource isolation needs
        - Behavior freezing triggers
        - Failure propagation paths
        - Escalation thresholds
    
    Containment remains explicit and inspectable.
    """
    
    containment_id: str
    containment_identity: str
    
    # Containment scope
    containment_scope: Optional[ContainmentScope] = None
    
    # Active containment policies
    containment_policy: Optional[ContainmentPolicy] = None
    
    # Protected components
    protected_components: List[ProtectedComponent] = field(default_factory=list)
    
    # Escalation thresholds
    escalation_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    applied_at_utc: float = field(default_factory=time.time)
    
    @property
    def protection_count(self) -> int:
        """Get the number of protected components."""
        return len(self.protected_components)
    
    def get_protection_for_subsystem(self, subsystem_id: str) -> Optional[ProtectedComponent]:
        """Get protection policy for a specific subsystem."""
        for component in self.protected_components:
            if component.component_id == subsystem_id:
                return component
        return None
    
    def should_escalate(self, subsystem_id: str, severity: float) -> bool:
        """Check if severity exceeds escalation threshold."""
        threshold = self.escalation_thresholds.get(subsystem_id, 1.0)
        return severity > threshold
    
    @classmethod
    def create(
        cls,
        containment_identity: str,
        containment_scope: Optional[ContainmentScope] = None,
        containment_policy: Optional[ContainmentPolicy] = None,
        protected_components: List[ProtectedComponent] = None,
        provenance: str = "unknown",
    ) -> ContainmentManagement:
        """Create a new containment management instance."""
        if protected_components is None:
            protected_components = []
        
        return cls(
            containment_id=f"cont:{uuid.uuid4().hex[:16]}",
            containment_identity=containment_identity,
            containment_scope=containment_scope,
            containment_policy=containment_policy,
            protected_components=protected_components,
            provenance=provenance,
        )


__all__ = [
    "ContainmentManagement",
    "ProtectedComponent",
    "ContainmentScope",
    "ContainmentPolicy",
]