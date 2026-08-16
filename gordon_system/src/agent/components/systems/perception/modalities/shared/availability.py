# Modality Availability - Phase 5.2 State of Readiness
# =====================================================

"""
ModalityAvailability: The current state of readiness of a modality to produce
observations.

A modality may be unavailable due to missing dependencies, sandbox restrictions,
or other constraints. Unavailable modalities must report explicit status rather
than producing substitute observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# AVAILABILITY STATE - Readiness to produce observations
# =============================================================================


class AvailabilityState(Enum):
    """
    States of modality availability.
    
    AVAILABLE: Modality is ready and can produce observations
    DEGRADED: Some capabilities are unavailable but others work
    RESTRICTED: Observation scope limited by permission or sandbox
    SANDBOXED: Running within sandbox constraints
    DISABLED: User/admin disabled the modality
    UNSUPPORTED: Platform doesn't support this modality
    FAILED: Modality failed during initialization or operation
    UNKNOWN: State cannot be determined
    """
    
    AVAILABLE = "available"         # Fully operational
    DEGRADED = "degraded"           # Partially operational
    RESTRICTED = "restricted"       # Limited by constraints
    SANDBOXED = "sandboxed"         # Sandbox limited
    DISABLED = "disabled"           # Explicitly disabled
    UNSUPPORTED = "unsupported"     # Platform incompatible
    FAILED = "failed"               # Failed during operation
    UNKNOWN = "unknown"             # Cannot determine state


# =============================================================================
# AVAILABILITY REASON - Why a modality is in its current state
# =============================================================================


class AvailabilityReason(Enum):
    """
    Reasons for availability states.
    
    These provide detailed context about why a modality is available, degraded,
    or unavailable.
    """
    
    # Available reasons
    NORMAL = "normal"               # Operating normally
    
    # Degraded reasons
    PARTIAL_SENSOR = "partial_sensor"
    CALIBRATION_DEGRADED = "calibration_degraded"
    RESOURCE_LIMITED = "resource_limited"
    BUFFER_OVERFLOW = "buffer_overflow"
    
    # Unavailable reasons
    MISSING_DEPENDENCY = "missing_dependency"
    PERMISSION_DENIED = "permission_denied"
    SANDBOX_RESTRICTED = "sandbox_restricted"
    UNSUPPORTED_PLATFORM = "unsupported_platform"
    CONFIGURATION_ERROR = "configuration_error"
    SENSOR_UNAVAILABLE = "sensor_unavailable"
    INITIALIZATION_FAILED = "initialization_failed"


# =============================================================================
# AVAILABILITY REPORT - Detailed availability information
# =============================================================================


@dataclass(frozen=True)
class AvailabilityReport:
    """
    Detailed report of modality availability.
    
    Fields:
        state:              Current availability state
        
        reason:             Why in this state?
        
        unavailable_since_utc: When state changed (if known)
        
        affected_capabilities: Tuple of capability IDs that are unavailable
        available_capabilities: Tuple of capability IDs that work
        
        estimated_recovery_time_sec: Expected time until recovery (or None)
        
        diagnostic_messages: Tuple of diagnostic messages
        
        provenance: Availability tracking
    """
    
    # Core identity (required)
    state: str                          # AvailabilityState value
    
    reason: str = "unknown"             # AvailabilityReason value
    
    # Timing
    unavailable_since_utc: Optional[float] = None  # When became unavailable
    
    # Capabilities
    affected_capabilities: Tuple[str, ...] = field(default_factory=tuple)
    available_capabilities: Tuple[str, ...] = field(default_factory=tuple)
    
    # Recovery info
    estimated_recovery_time_sec: Optional[float] = None
    
    # Diagnostics
    diagnostic_messages: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_available(self) -> bool:
        """Check if the modality is available."""
        return self.state == "available"
    
    @property
    def is_unavailable(self) -> bool:
        """Check if the modality is unavailable."""
        return self.state in ("unavailable", "failed", "disabled", "unsupported")
    
    @property
    def is_degraded(self) -> bool:
        """Check if the modality is degraded but partially available."""
        return self.state == "degraded"
    
    @classmethod
    def create(
        cls,
        state: str = "available",
        reason: str = "normal",
        affected_capabilities: Tuple[str, ...] = (),
        available_capabilities: Tuple[str, ...] = (),
        estimated_recovery_time_sec: Optional[float] = None,
    ) -> "AvailabilityReport":
        """
        Create a new availability report.
        
        Args:
            state: Current availability state
            reason: Why in this state
            affected_capabilities: What's unavailable
            available_capabilities: What still works
            estimated_recovery_time_sec: Expected recovery time
            
        Returns:
            New AvailabilityReport instance
        """
        return cls(
            state=state,
            reason=reason,
            affected_capabilities=affected_capabilities,
            available_capabilities=available_capabilities,
            estimated_recovery_time_sec=estimated_recovery_time_sec,
        )


# =============================================================================
# AVAILABILITY CHECKER - Interface for availability checking
# =============================================================================


class AvailabilityChecker:
    """
    Interface for checking modality availability.
    
    Implementations may check:
        - Hardware presence
        - Dependencies installed
        - Permissions granted
        - Sandbox constraints
        - Platform compatibility
    """
    
    def check_availability(
        self,
        modality_identity: str,
        capabilities: Tuple[str, ...],
    ) -> AvailabilityReport:
        """
        Check availability of a modality.
        
        Args:
            modality_identity: Modality to check
            capabilities: Capabilities to verify
            
        Returns:
            Availability report with current state
        """
        raise NotImplementedError
    
    def get_unavailability_reasons(
        self,
        modality_identity: str,
    ) -> Tuple[str, ...]:
        """
        Get all known reasons why a modality might be unavailable.
        
        Args:
            modality_identity: Modality to check
            
        Returns:
            Tuple of reason strings
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "AvailabilityState",
    "AvailabilityReason",
    
    # Dataclasses
    "AvailabilityReport",
    
    # Classes
    "AvailabilityChecker",
]