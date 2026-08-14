# Operational Modes
# =================

"""
Operational modes - Different states the runtime can operate in with varying capabilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import uuid
import time


class OperationalMode(Enum):
    """Operational modes for the runtime."""
    
    NORMAL = "normal"           # Standard operation - all services enabled
    SAFE = "safe"               # Reduced functionality with safety first
    RECOVERY = "recovery"       # Recovery operations only
    MAINTENANCE = "maintenance" # System maintenance mode
    DIAGNOSTIC = "diagnostic"   # Diagnostics only
    SIMULATION = "simulation"   # Test without real effects
    OFFLINE = "offline"         # No external connectivity
    EMERGENCY = "emergency"     # Critical state - safety first
    MINIMAL = "minimal"         # Bare minimum operation


@dataclass(frozen=True)
class OperationalModeConfig:
    """Configuration for an operational mode."""
    
    mode: OperationalMode
    enabled_services: List[str]
    disabled_services: List[str]
    enabled_policies: List[str]
    disabled_policies: List[str]
    restrictions: Dict[str, Any]
    priority: int  # Higher = more restrictive
    
    @staticmethod
    def generate_id() -> str:
        return f"mode_{uuid.uuid4().hex[:12]}"


# =============================================================================
# MODE CONFIGURATIONS
# =============================================================================

NORMAL_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.NORMAL,
    enabled_services=[
        "execution", "communication", "persistence", 
        "configuration", "monitoring"
    ],
    disabled_services=[],
    enabled_policies=["all"],
    disabled_policies=[],
    restrictions={},
    priority=0
)

SAFE_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.SAFE,
    enabled_services=[
        "safety_monitoring", "emergency_stop",
        "basic_execution"
    ],
    disabled_services=[
        "non_essential_features", "experimental_features"
    ],
    enabled_policies=["safety_only"],
    disabled_policies=["optimization"],
    restrictions={
        "max_cpu_percent": 50.0,
        "max_memory_percent": 60.0
    },
    priority=10
)

RECOVERY_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.RECOVERY,
    enabled_services=[
        "recovery", "health_check",
        "basic_execution"
    ],
    disabled_services=[
        "user_requests", "non_essential_features"
    ],
    enabled_policies=["recovery"],
    disabled_policies=["optimization", "normal_operations"],
    restrictions={
        "max_concurrent_executions": 10
    },
    priority=20
)

MAINTENANCE_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.MAINTENANCE,
    enabled_services=[
        "maintenance_tools", "backup",
        "configuration_update"
    ],
    disabled_services=[
        "user_requests", "execution", "external_communication"
    ],
    enabled_policies=["maintenance"],
    disabled_policies=["normal_operations", "optimization"],
    restrictions={
        "max_concurrent_executions": 0,
        "allow_user_requests": False
    },
    priority=30
)

DIAGNOSTIC_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.DIAGNOSTIC,
    enabled_services=[
        "diagnostics", "monitoring",
        "health_check"
    ],
    disabled_services=[
        "user_requests", "execution"
    ],
    enabled_policies=["diagnostic"],
    disabled_policies=["normal_operations"],
    restrictions={
        "max_concurrent_executions": 0
    },
    priority=40
)

SIMULATION_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.SIMULATION,
    enabled_services=[
        "execution", "communication",
        "monitoring"
    ],
    disabled_services=[
        "hardware_interfaces", "production_persistence"
    ],
    enabled_policies=["simulation"],
    disabled_policies=[],
    restrictions={
        "write_to_production": False
    },
    priority=50
)

OFFLINE_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.OFFLINE,
    enabled_services=[
        "local_storage", "diagnostics"
    ],
    disabled_services=[
        "external_communication", "execution", "user_requests"
    ],
    enabled_policies=["offline"],
    disabled_policies=["networked_operations"],
    restrictions={
        "allow_network_calls": False
    },
    priority=60
)

EMERGENCY_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.EMERGENCY,
    enabled_services=[
        "safety_monitoring", "emergency_stop",
        "basic_logging"
    ],
    disabled_services=[
        "all_non_essential"
    ],
    enabled_policies=["emergency"],
    disabled_policies=["normal_operations", "optimization"],
    restrictions={
        "max_concurrent_executions": 1,
        "shutdown_non_essential_after_seconds": 5
    },
    priority=70
)

MINIMAL_MODE_CONFIG = OperationalModeConfig(
    mode=OperationalMode.MINIMAL,
    enabled_services=[
        "core_health", "basic_logging"
    ],
    disabled_services=[
        "all_features"
    ],
    enabled_policies=["minimal"],
    disabled_policies=[],
    restrictions={
        "max_concurrent_executions": 0
    },
    priority=80
)


# =============================================================================
# MODE TRANSITION
# =============================================================================

class ModeTransition(Enum):
    """Mode transition types."""
    
    GRADUAL = "gradual"         # Step-by-step transition with validation
    IMMEDIATE = "immediate"     # Instant mode change
    ROLLBACK = "rollback"       # Rollback to previous mode
    FALLBACK = "fallback"       # Automatic fallback on error


@dataclass(frozen=True)
class ModeTransitionRequest:
    """Request to transition between operational modes."""
    
    request_id: str
    source_mode: OperationalMode
    target_mode: OperationalMode
    transition_type: ModeTransition
    timestamp_utc: float = field(default_factory=time.time)
    reason: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def generate_id() -> str:
        return f"transition_{uuid.uuid4().hex[:12]}"
    
    @property
    def is_safe_transition(self) -> bool:
        """Check if transition is safe."""
        # Safe transitions: normal <-> safe, any -> recovery
        if self.target_mode == OperationalMode.RECOVERY:
            return True
        if self.source_mode == OperationalMode.NORMAL and self.target_mode == OperationalMode.SAFE:
            return True
        if self.source_mode == OperationalMode.SAFE and self.target_mode == OperationalMode.NORMAL:
            return True
        return False


class ModeTransitionEngine:
    """Engine for managing operational mode transitions."""
    
    def __init__(self):
        self._current_mode: Optional[OperationalMode] = None
        self._mode_history: List[Dict[str, Any]] = []
    
    @property
    def current_mode(self) -> Optional[OperationalMode]:
        """Get current operational mode."""
        return self._current_mode
    
    def can_transition(self, from_mode: OperationalMode, to_mode: OperationalMode) -> bool:
        """Check if transition is allowed."""
        # Can always transition to recovery or emergency
        if to_mode in (OperationalMode.RECOVERY, OperationalMode.EMERGENCY):
            return True
        # Can always transition from emergency/recovery
        if from_mode in (OperationalMode.EMERGENCY, OperationalMode.RECOVERY):
            return True
        # Normal <-> Safe is allowed
        if from_mode == OperationalMode.NORMAL and to_mode == OperationalMode.SAFE:
            return True
        if from_mode == OperationalMode.SAFE and to_mode == OperationalMode.NORMAL:
            return True
        # Other transitions require validation
        return False
    
    def transition_to(
        self,
        target_mode: OperationalMode,
        reason: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ModeTransitionRequest:
        """Request a mode transition."""
        request = ModeTransitionRequest(
            request_id=ModeTransitionRequest.generate_id(),
            source_mode=self._current_mode or OperationalMode.NORMAL,
            target_mode=target_mode,
            transition_type=ModeTransition.GRADUAL,
            reason=reason,
            parameters=parameters or {}
        )
        
        if self.can_transition(request.source_mode, request.target_mode):
            old_mode = self._current_mode
            self._current_mode = target_mode
            self._mode_history.append({
                "old_mode": old_mode.value if old_mode else None,
                "new_mode": target_mode.value,
                "timestamp_utc": time.time(),
                "request_id": request.request_id,
                "reason": reason
            })
        
        return request
    
    def get_mode_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get mode transition history."""
        return self._mode_history[-limit:]
    
    def is_in_emergency_state(self) -> bool:
        """Check if runtime is in emergency state."""
        return self._current_mode == OperationalMode.EMERGENCY
    
    def get_config_for_mode(self, mode: OperationalMode) -> Optional[OperationalModeConfig]:
        """Get configuration for a mode."""
        configs = {
            OperationalMode.NORMAL: NORMAL_MODE_CONFIG,
            OperationalMode.SAFE: SAFE_MODE_CONFIG,
            OperationalMode.RECOVERY: RECOVERY_MODE_CONFIG,
            OperationalMode.MAINTENANCE: MAINTENANCE_MODE_CONFIG,
            OperationalMode.DIAGNOSTIC: DIAGNOSTIC_MODE_CONFIG,
            OperationalMode.SIMULATION: SIMULATION_MODE_CONFIG,
            OperationalMode.OFFLINE: OFFLINE_MODE_CONFIG,
            OperationalMode.EMERGENCY: EMERGENCY_MODE_CONFIG,
            OperationalMode.MINIMAL: MINIMAL_MODE_CONFIG,
        }
        return configs.get(mode)


__all__ = [
    "OperationalMode",
    "OperationalModeConfig",
    "NORMAL_MODE_CONFIG",
    "SAFE_MODE_CONFIG", 
    "RECOVERY_MODE_CONFIG",
    "MAINTENANCE_MODE_CONFIG",
    "DIAGNOSTIC_MODE_CONFIG",
    "SIMULATION_MODE_CONFIG",
    "OFFLINE_MODE_CONFIG",
    "EMERGENCY_MODE_CONFIG",
    "MINIMAL_MODE_CONFIG",
    "ModeTransition",
    "ModeTransitionRequest",
    "ModeTransitionEngine",
]