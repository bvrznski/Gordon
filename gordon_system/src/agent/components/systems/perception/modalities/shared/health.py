# Modality Health - Phase 5.2 Operational Status
# ===============================================

"""
ModalityHealth: The operational health status of a modality.

Health covers availability, latency, sensor quality, confidence estimation,
and pipeline component health.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import time


# =============================================================================
# COMPONENT HEALTH - Health status of individual components
# =============================================================================


@dataclass(frozen=True)
class ComponentHealth:
    """
    Health status of a single component within the modality pipeline.
    
    Fields:
        component_name:      Name/ID of the component
        
        is_healthy:          True if component is functioning normally
        
        error_count:         Number of errors encountered
        
        last_error_utc:      When last error occurred
        
        recovery_time_ms:    Time to recover from failure
    """
    
    # Core identity (required)
    component_name: str                 # Component identifier
    
    is_healthy: bool = True             # Current health state
    
    error_count: int = 0                # Error count since operation start
    
    last_error_utc: Optional[float] = None  # Most recent error timestamp
    
    recovery_time_ms: float = 0.0       # Time to recover in ms


# =============================================================================
# MODALITY HEALTH - Complete operational health
# =============================================================================


@dataclass(frozen=True)
class ModalityHealth:
    """
    Operational health status of a modality.
    
    Fields:
        is_available:        True if modality can produce observations
        
        latency_ms:          Typical acquisition latency in milliseconds
        
        sensor_quality:      Quality score 0.0-1.0 for the sensor hardware
        
        confidence_quality:  Quality of confidence estimation 0.0-1.0
        
        pipeline_health:     Health of processing pipeline components
        
        diagnostics:         Tuple of diagnostic messages
    """
    
    # Core identity (required)
    is_available: bool = True           # Can produce observations?
    
    latency_ms: float = 0.0             # Acquisition latency
    
    sensor_quality: float = 1.0         # Sensor quality 0.0-1.0
    
    confidence_quality: float = 1.0     # Confidence estimation quality
    
    pipeline_health: Dict[str, bool] = field(default_factory=dict)  # Component health map
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)    # Diagnostics
    
    @property
    def is_operational(self) -> bool:
        """Check if modality can produce observations."""
        return self.is_available and all(self.pipeline_health.values())
    
    def get_component_health(self, component_name: str) -> bool:
        """
        Get health status of a specific component.
        
        Args:
            component_name: Component to check
            
        Returns:
            True if component is healthy
        """
        return self.pipeline_health.get(component_name, False)
    
    @classmethod
    def create(
        cls,
        is_available: bool = True,
        latency_ms: float = 0.0,
        sensor_quality: float = 1.0,
        confidence_quality: float = 1.0,
        pipeline_health: Optional[Dict[str, bool]] = None,
        diagnostics: Tuple[str, ...] = (),
    ) -> "ModalityHealth":
        """
        Create a new modality health instance.
        
        Args:
            is_available: Can produce observations?
            latency_ms: Acquisition latency
            sensor_quality: Sensor quality 0.0-1.0
            confidence_quality: Confidence estimation quality
            pipeline_health: Component health map
            diagnostics: Diagnostic messages
            
        Returns:
            New ModalityHealth instance
        """
        return cls(
            is_available=is_available,
            latency_ms=latency_ms,
            sensor_quality=sensor_quality,
            confidence_quality=confidence_quality,
            pipeline_health=pipeline_health or {},
            diagnostics=diagnostics,
        )


# =============================================================================
# HEALTH REPORTER - Interface for health reporting
# =============================================================================


class HealthReporter:
    """
    Interface for health monitoring and reporting.
    
    Implementations track:
        - Component health metrics
        - Error rates and patterns
        - Latency trends
        - Quality degradation signals
    """
    
    def report_health(
        self,
        modality_identity: str,
    ) -> ModalityHealth:
        """
        Report current health status for a modality.
        
        Args:
            modality_identity: Modality to check
            
        Returns:
            Current health status
        """
        raise NotImplementedError
    
    def record_error(
        self,
        modality_identity: str,
        component_name: Optional[str] = None,
    ) -> None:
        """
        Record an error event for health tracking.
        
        Args:
            modality_identity: Modality where error occurred
            component_name: Component that failed (optional)
        """
        raise NotImplementedError
    
    def get_health_history(
        self,
        modality_identity: str,
        window_seconds: float = 3600.0,  # Default 1 hour
    ) -> Tuple[ModalityHealth, ...]:
        """
        Get health history for a time window.
        
        Args:
            modality_identity: Modality to check
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of historical health states
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Dataclasses
    "ComponentHealth",
    "ModalityHealth",
    
    # Classes
    "HealthReporter",
]