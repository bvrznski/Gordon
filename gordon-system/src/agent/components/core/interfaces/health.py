# Core Health Interface
# =====================

"""
Core health interface - defines contracts for health checking.

Health checks are a critical runtime capability that allows the system to
determine if components and services are operating correctly.

ARCHITECTURAL PRINCIPLES:
- Health checks are non-blocking by default
- Health status is observable without introspection
- Health check results are cached briefly (avoid frequent calls)
"""

from typing import Protocol, Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import time


class HealthStatus(Enum):
    """Health status values."""
    HEALTHY = "healthy"          # Component is operating normally
    DEGRADED = "degraded"        # Component has issues but is partially functional
    FAILED = "failed"            # Component is not operational
    UNKNOWN = "unknown"          # Health cannot be determined


@dataclass(frozen=True)
class HealthCheckResult:
    """
    Result of a health check.
    
    Args:
        status: The overall health status
        timestamp_utc: When the check was performed
        component_id: Which component was checked
        details: Additional context-specific information
        duration_ms: How long the check took in milliseconds
        error_message: Description if unhealthy (optional)
    """
    status: HealthStatus
    timestamp_utc: float = field(default_factory=time.time)  # type: ignore
    component_id: str = "unknown"
    details: Dict[str, Any] = None  # type: ignore
    duration_ms: float = 0.0
    error_message: Optional[str] = None


class IHealthChecker(Protocol):
    """
    Interface for health checkers.
    
    Health checkers perform component-specific health verification.
    They are responsible for checking internal state and external dependencies.
    """
    
    @property
    def checker_id(self) -> str:
        """Get the unique ID of this health checker."""
        ...
    
    async def check_health(
        self,
        component_id: Optional[str] = None,
    ) -> HealthCheckResult:
        """
        Perform a health check on a component.
        
        Args:
            component_id: The component to check (None = check all)
            
        Returns:
            Result with status, details, and timing information
            
        Note: This method should NOT block for long periods. Use timeouts
        for any external dependency checks.
        """
        ...
    
    async def get_all_health_checks(self) -> Dict[str, HealthCheckResult]:
        """Get health check results for all managed components."""
        ...


class IHealthRegistry(Protocol):
    """
    Interface for the health registry - maintains health state across components.
    
    The registry:
        - Stores health check results
        - Tracks health history (optional)
        - Provides aggregated views of system health
        - Maintains health status over time
    """
    
    async def record_health(
        self,
        component_id: str,
        result: HealthCheckResult,
    ) -> None:
        """Record a health check result."""
        ...
    
    async def get_health(self, component_id: str) -> Optional[HealthCheckResult]:
        """Get the most recent health check for a component."""
        ...
    
    async def get_all_health(self) -> Dict[str, HealthCheckResult]:
        """Get all stored health check results."""
        ...
    
    def get_system_status(self) -> HealthStatus:
        """
        Get overall system health status.
        
        Returns:
            - HEALTHY if all components are healthy
            - DEGRADED if any component is degraded
            - FAILED if any component has failed
            - UNKNOWN if no health data available
        """
        ...
    
    async def get_health_history(
        self,
        component_id: str,
        window_seconds: float = 300.0,  # Default 5 minutes
    ) -> List[HealthCheckResult]:
        """Get health check history for a component within a time window."""
        ...


class IHealthObserver(Protocol):
    """
    Interface for components that observe health changes.
    
    Health observers can react when component health status changes,
    enabling automatic remediation or alerting.
    """
    
    async def on_health_changed(
        self,
        component_id: str,
        previous_status: HealthStatus,
        new_status: HealthStatus,
        result: HealthCheckResult,
    ) -> None:
        """
        Called when a component's health status changes.
        
        Args:
            component_id: Which component changed
            previous_status: The previous health status
            new_status: The new health status
            result: Full health check result for the change
        """
        ...
    
    async def on_health_check_failed(
        self,
        component_id: str,
        error_message: str,
    ) -> None:
        """Called when a health check encounters an error."""
        ...


class HealthCheckError(Exception):
    """Raised when a health check cannot be performed."""
    pass


class ComponentUnhealthyError(HealthCheckError):
    """
    Raised when a component is found to be unhealthy during a check.
    
    This can be used to trigger remediation actions.
    """
    
    def __init__(self, component_id: str, status: HealthStatus, message: str = ""):
        super().__init__(f"Component {component_id} is {status.value}: {message}")
        self.component_id = component_id
        self.status = status


__all__ = [
    "HealthStatus",
    "HealthCheckResult",
    "IHealthChecker",
    "IHealthRegistry",
    "IHealthObserver",
    "HealthCheckError",
    "ComponentUnhealthyError",
]