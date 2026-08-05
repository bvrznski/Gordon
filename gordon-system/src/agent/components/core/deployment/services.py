# Service Management Framework
# ============================

"""
Phase 3.8.10 - Service Management, Monitoring & Diagnostics

This module provides:
    - Service lifecycle management and supervision
    - Health monitoring with state transitions
    - Runtime diagnostics and health checks
    - Operational utilities and maintenance tools

ARCHITECTURAL PRINCIPLES:
    - Every managed service has a lifecycle
    - Health is continuously observable
    - Diagnostics are deterministic
    - Monitoring is centralized
    - Incidents are traceable
    - Recovery actions are documented
    - Operational utilities use canonical interfaces
    - Logs are structured
    - Monitoring overhead is bounded
    - Duplicate operational logic is prohibited
"""

from typing import (
    Optional, List, Dict, Any, Callable, Awaitable, Protocol
)
from dataclasses import dataclass, field
from enum import Enum, auto
import time
import uuid

from .core import (
    ServiceState,
    HealthStatus,
    ServiceDependency,
    ServiceHealthCheck,
    ServiceDefinition,
    LifecycleState,
    LifecycleTransitionRequest,
)


# =============================================================================
# SERVICE STATE MACHINE MODEL
# =============================================================================


@dataclass(frozen=True)
class ServiceStateTransition:
    """Record of a service state transition."""
    
    from_state: ServiceState
    to_state: ServiceState
    
    timestamp_utc: float = field(default_factory=time.time)
    
    service_id: str = ""
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ServiceLifecycleEvent:
    """Event in a service's lifecycle."""
    
    event_type: str  # e.g., "started", "stopped", "health_changed"
    service_id: str
    
    timestamp_utc: float = field(default_factory=time.time)
    
    state_before: Optional[str] = None
    state_after: Optional[str] = None
    
    payload: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# HEALTH MONITORING
# =============================================================================


@dataclass(frozen=True)
class HealthProbeResult:
    """Result of a health probe check."""
    
    probe_name: str
    healthy: bool
    
    timestamp_utc: float = field(default_factory=time.time)
    
    details: Optional[str] = None
    error_message: Optional[str] = None


@dataclass(frozen=True)
class HealthCheckReport:
    """Complete health check report for a service."""
    
    service_id: str
    overall_status: HealthStatus
    
    probes: List[HealthProbeResult]
    
    timestamp_utc: float = field(default_factory=time.time)
    duration_seconds: float = 0.0


# =============================================================================
# SERVICE REGISTRATION
# =============================================================================


@dataclass(frozen=True)
class ServiceRegistration:
    """Registered service information."""
    
    service_id: str
    definition: ServiceDefinition
    
    registered_at_utc: float = field(default_factory=time.time)
    last_heartbeat_at_utc: Optional[float] = None
    
    health_status: HealthStatus = HealthStatus.UNKNOWN
    
    # Runtime info
    host: Optional[str] = None
    port: Optional[int] = None
    pid: Optional[int] = None


# =============================================================================
# DEPENDENCY TRACKING
# =============================================================================


@dataclass(frozen=True)
class DependencyGraph:
    """Service dependency graph with topological information."""
    
    service_id: str
    dependencies: Dict[str, ServiceDependency]
    
    # Topological properties
    depth: int = 0
    depends_on_ids: List[str] = field(default_factory=list)
    dependents_ids: List[str] = field(default_factory=list)


# =============================================================================
# LIVENESS PROTOCOLS
# =============================================================================


class StartResult(Enum):
    """Result of a start operation."""
    
    SUCCESS = "success"
    ALREADY_STARTED = "already_started"
    PENDING_STARTUP = "pending_startup"
    FAILED = "failed"


@dataclass(frozen=True)
class ServiceStartRequest:
    """Request to start a service."""
    
    service_id: str
    force: bool = False  # Force start even if dependencies unavailable
    
    requested_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ServiceStopRequest:
    """Request to stop a service."""
    
    service_id: str
    grace_period_seconds: Optional[float] = None
    
    requested_at_utc: float = field(default_factory=time.time)


# =============================================================================
# SERVICE MANAGER INTERFACES
# =============================================================================


@dataclass(frozen=True)
class ServiceLifecycleResult:
    """Result of a lifecycle operation on a service."""
    
    success: bool
    service_id: str
    
    from_state: Optional[ServiceState] = None
    to_state: Optional[ServiceState] = None
    
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass(frozen=True)
class HealthCheckResult:
    """Complete health check result."""
    
    overall_status: str  # "healthy", "degraded", "unhealthy"
    
    services: Dict[str, str]  # service_id -> status
    
    probes_executed: int = 0
    probes_passed: int = 0
    probes_failed: int = 0
    
    duration_seconds: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ServiceSnapshot:
    """Immutable snapshot of service state."""
    
    services: Dict[str, ServiceDefinition]
    
    health_status: str
    dependencies_resolved: bool
    
    total_services: int = 0
    running_services: int = 0


# =============================================================================
# SERVICE MANAGEMENT FRAMEWORK - ABSTRACT INTERFACE
# =============================================================================


class ServiceLifecycleManager:
    """
    Canonical authority for service lifecycle management.
    
    Architecture Boundary:
        - One canonical manager per runtime instance
        - All service operations flow through this manager
        - No direct service manipulation elsewhere in the codebase
    
    Contract:
        - State transitions are deterministic and auditable
        - Dependencies are respected
        - Lifecycle events are emitted
        - State is persisted and observable
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._transitions: List[ServiceStateTransition] = []
        self._event_handlers: Dict[str, Callable[[ServiceLifecycleEvent], Awaitable[None]]] = {}
    
    async def start_service(
        self, request: ServiceStartRequest
    ) -> ServiceLifecycleResult:
        """
        Start a registered service.
        
        Args:
            request: Start request with service_id
            
        Returns:
            Result with success status and duration
        """
        if request.service_id not in self._services:
            return ServiceLifecycleResult(
                success=False,
                service_id=request.service_id,
                error_message="Service not registered"
            )
        
        start_time = time.time()
        
        # Check dependencies (unless force)
        if not request.force:
            deps_ok, missing_deps = await self._check_dependencies(request.service_id)
            if not deps_ok:
                return ServiceLifecycleResult(
                    success=False,
                    service_id=request.service_id,
                    error_message=f"Missing dependencies: {missing_deps}"
                )
        
        # Transition state
        service = self._services[request.service_id]
        result = await self._transition_state(
            request.service_id, service.state, ServiceState.STARTING, "start_requested"
        )
        
        duration = time.time() - start_time
        
        return ServiceLifecycleResult(
            success=True,
            service_id=request.service_id,
            from_state=service.state,
            to_state=ServiceState.STARTING,
            duration_seconds=duration
        )
    
    async def stop_service(
        self, request: ServiceStopRequest
    ) -> ServiceLifecycleResult:
        """
        Stop a running service.
        
        Args:
            request: Stop request with service_id
            
        Returns:
            Result with success status and duration
        """
        if request.service_id not in self._services:
            return ServiceLifecycleResult(
                success=False,
                service_id=request.service_id,
                error_message="Service not registered"
            )
        
        start_time = time.time()
        
        service = self._services[request.service_id]
        result = await self._transition_state(
            request.service_id, service.state, ServiceState.STOPPING, "stop_requested"
        )
        
        duration = time.time() - start_time
        
        return ServiceLifecycleResult(
            success=True,
            service_id=request.service_id,
            from_state=service.state,
            to_state=ServiceState.STOPPING,
            duration_seconds=duration
        )
    
    async def register_service(self, definition: ServiceDefinition) -> bool:
        """Register a new service."""
        if definition.service_id in self._services:
            return False
        
        self._services[definition.service_id] = definition
        return True
    
    async def unregister_service(self, service_id: str) -> bool:
        """Unregister a service."""
        if service_id not in self._services:
            return False
        
        del self._services[service_id]
        return True
    
    async def _check_dependencies(
        self, service_id: str
    ) -> tuple[bool, List[str]]:
        """
        Check if all dependencies are satisfied.
        
        Returns:
            Tuple of (success, missing_dependency_ids)
        """
        if service_id not in self._services:
            return False, []
        
        service = self._services[service_id]
        missing = []
        
        for dep in service.dependencies:
            if dep.required:
                if dep.service_id not in self._services:
                    missing.append(dep.service_id)
                elif self._services[dep.service_id].state != ServiceState.RUNNING:
                    missing.append(dep.service_id)
        
        return len(missing) == 0, missing
    
    async def _transition_state(
        self,
        service_id: str,
        from_state: ServiceState,
        to_state: ServiceState,
        reason: str
    ) -> ServiceLifecycleResult:
        """Perform a state transition."""
        if service_id not in self._services:
            return ServiceLifecycleResult(
                success=False, service_id=service_id,
                error_message="Service not registered"
            )
        
        # Record transition
        transition = ServiceStateTransition(
            from_state=from_state,
            to_state=to_state,
            timestamp_utc=time.time(),
            service_id=service_id,
            reason=reason
        )
        self._transitions.append(transition)
        
        # Update state
        service = self._services[service_id]
        self._services[service_id] = dataclass_replace(service, state=to_state)
        
        return ServiceLifecycleResult(
            success=True,
            service_id=service_id,
            from_state=from_state,
            to_state=to_state,
            duration_seconds=0.0
        )
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of service state."""
        return {
            "total_services": len(self._services),
            "running_services": sum(
                1 for s in self._services.values()
                if s.state == ServiceState.RUNNING
            ),
            "transition_count": len(self._transitions),
        }


# =============================================================================
# HEALTH MONITORING FRAMEWORK - ABSTRACT INTERFACE
# =============================================================================


class HealthMonitor:
    """
    Canonical authority for health monitoring.
    
    Architecture Boundary:
        - One canonical monitor per runtime instance
        - All health checks flow through this monitor
        - No direct health manipulation elsewhere in the codebase
    
    Contract:
        - Health is continuously evaluated
        - State transitions are observable
        - Probes are executed regularly
        - Reports are structured and actionable
    """
    
    def __init__(self):
        self._service_health: Dict[str, HealthStatus] = {}
        self._probes: Dict[str, Callable[[], Awaitable[HealthProbeResult]]] = {}
        self._results_history: List[HealthCheckReport] = []
    
    async def register_probe(
        self,
        probe_name: str,
        probe_func: Callable[[], Awaitable[HealthProbeResult]]
    ) -> None:
        """Register a health probe."""
        self._probes[probe_name] = probe_func
    
    async def unregister_probe(self, probe_name: str) -> bool:
        """Unregister a health probe."""
        if probe_name not in self._probes:
            return False
        del self._probes[probe_name]
        return True
    
    async def run_health_check(
        self, service_id: Optional[str] = None
    ) -> HealthCheckResult:
        """
        Run health checks.
        
        Args:
            service_id: Specific service (None = all services)
            
        Returns:
            Complete health check report
        """
        start_time = time.time()
        
        if service_id:
            probes_result = await self._run_service_probes(service_id)
        else:
            probes_result = await self._run_all_probes()
        
        overall_status = self._determine_overall_status(probes_result)
        
        duration = time.time() - start_time
        
        report = HealthCheckResult(
            overall_status=overall_status,
            services={service_id or "all": overall_status},
            probes_executed=len(probes_result),
            probes_passed=sum(1 for p in probes_result if p.healthy),
            probes_failed=sum(1 for p in probes_result if not p.healthy),
            duration_seconds=duration
        )
        
        self._results_history.append(report)
        
        return report
    
    async def _run_service_probes(
        self, service_id: str
    ) -> List[HealthProbeResult]:
        """Run all registered probes for a service."""
        results = []
        
        for probe_name, probe_func in self._probes.items():
            try:
                result = await probe_func()
                results.append(result)
            except Exception as e:
                results.append(HealthProbeResult(
                    probe_name=probe_name,
                    healthy=False,
                    error_message=str(e)
                ))
        
        return results
    
    async def _run_all_probes(self) -> List[HealthProbeResult]:
        """Run all registered probes."""
        return await self._run_service_probes("all")
    
    def _determine_overall_status(
        self, probe_results: List[HealthProbeResult]
    ) -> str:
        """Determine overall health status from probe results."""
        if not probe_results:
            return "healthy"
        
        healthy_count = sum(1 for p in probe_results if p.healthy)
        total = len(probe_results)
        
        if healthy_count == total:
            return "healthy"
        elif healthy_count > total * 0.5:
            return "degraded"
        else:
            return "unhealthy"


# =============================================================================
# DIAGNOSTICS FRAMEWORK - ABSTRACT INTERFACE
# =============================================================================


class DiagnosticsRunner:
    """
    Canonical authority for diagnostics execution.
    
    Architecture Boundary:
        - One canonical runner per runtime instance
        - All diagnostics flow through this runner
        - No direct diagnostics manipulation elsewhere in the codebase
    
    Contract:
        - Diagnostics are deterministic (same inputs = same outputs)
        - Reports include full context
        - Issues are actionable
        - Performance is bounded
    """
    
    def __init__(self):
        self._diagnostic_procedures: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {}
        self._results_history: List[Dict[str, Any]] = []
    
    async def register_diagnostic(
        self,
        diagnostic_name: str,
        procedure_func: Callable[[], Awaitable[Dict[str, Any]]]
    ) -> None:
        """Register a diagnostic procedure."""
        self._diagnostic_procedures[diagnostic_name] = procedure_func
    
    async def unregister_diagnostic(self, name: str) -> bool:
        """Unregister a diagnostic procedure."""
        if name not in self._diagnostic_procedures:
            return False
        del self._diagnostic_procedures[name]
        return True
    
    async def run_diagnostics(
        self, names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run diagnostics.
        
        Args:
            names: Specific diagnostics (None = all)
            
        Returns:
            Dictionary of diagnostic results
        """
        start_time = time.time()
        
        if names is None:
            names = list(self._diagnostic_procedures.keys())
        
        results = {}
        
        for name in names:
            if name in self._diagnostic_procedures:
                try:
                    result = await self._diagnostic_procedures[name]()
                    results[name] = {
                        "success": True,
                        "result": result
                    }
                except Exception as e:
                    results[name] = {
                        "success": False,
                        "error": str(e)
                    }
        
        duration = time.time() - start_time
        
        summary = {
            "timestamp_utc": time.time(),
            "duration_seconds": duration,
            "diagnostics_executed": len(names),
            "successful": sum(1 for r in results.values() if r["success"]),
            "failed": sum(1 for r in results.values() not in r["success"])
        }
        
        return {"summary": summary, "results": results}
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of diagnostics state."""
        return {
            "registered_diagnostics": len(self._diagnostic_procedures),
            "total_runs": len(self._results_history)
        }


# =============================================================================
# MAINTENANCE UTILITIES
# =============================================================================


@dataclass(frozen=True)
class MaintenanceTask:
    """A maintenance task to be executed."""
    
    task_id: str
    name: str
    description: str
    
    scheduled_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    status: str = "pending"  # pending, running, completed, failed


@dataclass(frozen=True)
class MaintenanceReport:
    """Maintenance activity report."""
    
    maintenance_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_duration_seconds: float = 0.0
    
    issues_identified: List[Dict[str, Any]] = field(default_factory=list)
    fixes_applied: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# SERVICE OPERATIONS UTILITIES
# =============================================================================


class ServiceOperations:
    """
    Canonical authority for service operational utilities.
    
    Architecture Boundary:
        - One canonical operator per runtime instance
        - All operational commands flow through this operator
        - No direct operational manipulation elsewhere in the codebase
    
    Contract:
        - Operations are auditable
        - Results are deterministic
        - Error reporting is comprehensive
        - Performance metrics are collected
    """
    
    def __init__(self):
        self._operation_history: List[Dict[str, Any]] = []
    
    async def restart_service(self, service_id: str) -> bool:
        """Restart a service."""
        return await self._execute_operation("restart", service_id)
    
    async def drain_service(self, service_id: str) -> bool:
        """Drain traffic from a service before shutdown."""
        return await self._execute_operation("drain", service_id)
    
    async def health_check(self, service_id: str) -> HealthStatus:
        """Check health of a specific service."""
        result = await self._execute_operation("health_check", service_id)
        return HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
    
    async def _execute_operation(
        self, operation_type: str, target_id: str
    ) -> bool:
        """Execute an operational command."""
        start_time = time.time()
        
        try:
            # Would execute the actual operation
            result = True  # Placeholder
            
            duration = time.time() - start_time
            
            self._operation_history.append({
                "operation_type": operation_type,
                "target_id": target_id,
                "success": result,
                "duration_seconds": duration,
                "timestamp_utc": time.time()
            })
            
            return result
            
        except Exception:
            return False
    
    def get_operation_history(
        self, since_utc: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get operation history with optional filtering."""
        if since_utc is None:
            return list(self._operation_history)
        
        return [
            op for op in self._operation_history
            if op["timestamp_utc"] >= since_utc
        ]


# =============================================================================
# DATACLASS HELPERS
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """Replace fields in a frozen dataclass."""
    import dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        return dataclasses.replace(obj, **kwargs)
    raise TypeError(f"Cannot replace fields in {type(obj)}")


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # State machine model
    "ServiceStateTransition",
    "ServiceLifecycleEvent",
    
    # Health monitoring
    "HealthProbeResult",
    "HealthCheckReport",
    
    # Service registration
    "ServiceRegistration",
    
    # Dependency tracking
    "DependencyGraph",
    
    # Liveness protocols
    "StartResult",
    "ServiceStartRequest",
    "ServiceStopRequest",
    
    # Result types
    "ServiceLifecycleResult",
    "HealthCheckResult",
    "ServiceSnapshot",
    
    # Manager interfaces
    "ServiceLifecycleManager",
    "HealthMonitor",
    "DiagnosticsRunner",
    "ServiceOperations",
]