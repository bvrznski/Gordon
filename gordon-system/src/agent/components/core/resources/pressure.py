# Core Resource Pressure Monitoring
# ==================================
"""
Resource pressure detection and handling.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time


@dataclass(frozen=True)
class PressureLevel(Enum):
    """Pressure levels for resource domains."""
    NORMAL = "normal"               # Healthy, plenty of capacity
    ELEVATED = "elevated"           # Some pressure, may slow down
    HIGH = "high"                   # Significant pressure
    CRITICAL = "critical"           # Near exhaustion
    EXHAUSTED = "exhausted"         # No capacity available


@dataclass(frozen=True)
class ResourcePressure:
    """
    Current pressure state for a resource domain.
    
    Tracks utilization and derived pressure level.
    """
    domain: str
    total_capacity: float
    used_capacity: float
    
    free_capacity: float = 0.0      # Derived: total - used
    headroom: float = 0.0           # Free capacity after headroom buffer
    
    pressure_level: PressureLevel = PressureLevel.NORMAL
    
    utilization_percent: float = 0.0  # 0-100


@dataclass(frozen=True)
class ResourcePressureObservation:
    """
    Observation of resource pressure at a point in time.
    
    Used for logging, debugging, and historical analysis.
    """
    runtime_id: str
    timestamp_utc: float
    
    domain_pressure: Dict[str, ResourcePressure]


@dataclass(frozen=True)
class ResourcePressureDecisionType(Enum):
    """Types of pressure-related decisions."""
    NO_ACTION = "no_action"              # Current pressure acceptable
    REDUCE_CONCURRENCY = "reduce_concurrency"  # Reduce parallelism
    INCREASE_HEADROOM = "increase_headroom"   # Request more headroom
    ENFORCE_STRICTER = "enforce_stricter"     # Enforce stricter limits
    REJECT_NEW_WORK = "reject_new_work"       # Reject new requests
    PREEMPT_LOW_PRIORITY = "preempt_low_priority"  # Preempt to free capacity


@dataclass(frozen=True)
class ResourcePressureDecision:
    """
    Decision on how to respond to resource pressure.
    """
    decision_type: ResourcePressureDecisionType
    
    # Details
    domain: str
    current_pressure: float     # Current utilization (0-1)
    
    action_description: Optional[str] = None


class PressureManager:
    """
    Manager for resource pressure detection and response.
    
    Monitors capacity utilization and reports when pressure levels change.
    Also suggests appropriate responses to various pressure levels.
    """
    
    # Thresholds for pressure levels
    ELEVATED_THRESHOLD: float = 0.6   # 60% utilization
    HIGH_THRESHOLD: float = 0.8       # 80% utilization
    CRITICAL_THRESHOLD: float = 0.95  # 95% utilization
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Current pressure state per domain
        self._pressure_state: Dict[str, ResourcePressure] = {}
    
    def update_pressure(
        self,
        domain: str,
        total_capacity: float,
        used_capacity: float
    ) -> Optional[ResourcePressure]:
        """
        Update pressure state for a domain.
        
        Returns the new pressure state if it changed.
        """
        with self._lock:
            # Calculate derived values
            free = max(0.0, total_capacity - used_capacity)
            
            if total_capacity > 0:
                utilization = (used_capacity / total_capacity) * 100
            else:
                utilization = 0.0
            
            # Determine pressure level
            if utilization >= self.CRITICAL_THRESHOLD * 100:
                level = PressureLevel.EXHAUSTED
            elif utilization >= self.HIGH_THRESHOLD * 100:
                level = PressureLevel.CRITICAL
            elif utilization >= self.ELEVATED_THRESHOLD * 100:
                level = PressureLevel.HIGH
            elif utilization > 0:
                level = PressureLevel.ELEVATED
            else:
                level = PressureLevel.NORMAL
            
            pressure = ResourcePressure(
                domain=domain,
                total_capacity=total_capacity,
                used_capacity=used_capacity,
                free_capacity=free,
                headroom=max(0.0, free - (used_capacity * 0.1)),  # 10% buffer
                pressure_level=level,
                utilization_percent=utilization,
            )
            
            old_pressure = self._pressure_state.get(domain)
            self._pressure_state[domain] = pressure
            
            if old_pressure is None or old_pressure.pressure_level != level:
                return pressure
            
            return None
    
    def get_domain_pressure(self, domain: str) -> Optional[ResourcePressure]:
        """Get current pressure state for a domain."""
        with self._lock:
            return self._pressure_state.get(domain)
    
    def get_all_pressure(self) -> Dict[str, ResourcePressure]:
        """Get current pressure for all domains."""
        with self._lock:
            return dict(self._pressure_state)
    
    def observe_pressure(
        self,
        total_capacity: float,
        used_capacity: float
    ) -> Tuple[ResourcePressure, List[ResourcePressureDecision]]:
        """
        Observe pressure and suggest responses.
        
        Returns the pressure state and suggested decisions.
        """
        with self._lock:
            # Update internal state
            pressure = self._pressure_state.get("global")
            
            if not pressure or pressure.total_capacity != total_capacity:
                pressure = ResourcePressure(
                    domain="global",
                    total_capacity=total_capacity,
                    used_capacity=used_capacity,
                    free_capacity=max(0.0, total_capacity - used_capacity),
                    headroom=max(0.0, (total_capacity - used_capacity) * 0.9),  # 10% buffer
                    pressure_level=PressureLevel.NORMAL,
                    utilization_percent=(
                        (used_capacity / total_capacity * 100) if total_capacity > 0 else 0
                    ),
                )
            
            decisions: List[ResourcePressureDecision] = []
            
            if pressure.pressure_level == PressureLevel.EXHAUSTED:
                decisions.append(ResourcePressureDecision(
                    decision_type=ResourcePressureDecisionType.REJECT_NEW_WORK,
                    domain="global",
                    current_pressure=pressure.utilization_percent / 100,
                    action_description="Reject all new work - resources exhausted",
                ))
            elif pressure.pressure_level == PressureLevel.CRITICAL:
                decisions.append(ResourcePressureDecision(
                    decision_type=ResourcePressureDecisionType.PREEMPT_LOW_PRIORITY,
                    domain="global",
                    current_pressure=pressure.utilization_percent / 100,
                    action_description="Consider preemption to free resources",
                ))
            elif pressure.pressure_level == PressureLevel.HIGH:
                decisions.append(ResourcePressureDecision(
                    decision_type=ResourcePressureDecisionType.REDUCE_CONCURRENCY,
                    domain="global",
                    current_pressure=pressure.utilization_percent / 100,
                    action_description="Reduce concurrency and queue work",
                ))
            elif pressure.pressure_level == PressureLevel.ELEVATED:
                decisions.append(ResourcePressureDecision(
                    decision_type=ResourcePressureDecisionType.NO_ACTION,
                    domain="global",
                    current_pressure=pressure.utilization_percent / 100,
                    action_description="Monitor closely, no immediate action needed",
                ))
            
            return pressure, decisions
    
    def get_snapshot(self) -> ResourcePressureObservation:
        """Get an immutable snapshot of pressure state."""
        with self._lock:
            return ResourcePressureObservation(
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                domain_pressure=dict(self._pressure_state),
            )


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "PressureLevel",
    "ResourcePressure",
    "ResourcePressureObservation",
    "ResourcePressureDecisionType",
    "ResourcePressureDecision",
    "PressureManager",
]