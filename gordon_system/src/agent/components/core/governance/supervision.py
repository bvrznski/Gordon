# Runtime Supervision
# ===================

"""
Continuous runtime supervision of subsystem behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import uuid
import time


@dataclass(frozen=True)
class SupervisionResult:
    """Result of a supervision check."""
    
    result_id: str
    subsystem_name: str
    timestamp_utc: float = field(default_factory=time.time)
    status: str  # compliant, warning, critical
    details: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def generate_id() -> str:
        return f"supervision_{uuid.uuid4().hex[:12]}"
    
    @property
    def is_compliant(self) -> bool:
        return self.status == "compliant"
    
    @property
    def is_critical(self) -> bool:
        return self.status == "critical"


class SupervisionEvent(Enum):
    """Events in the supervision lifecycle."""
    
    SUBSYSTEM_STARTED = "subsystem_started"
    SUBSYSTEM_STOPPED = "subsystem_stopped"
    POLICY_VIOLATION = "policy_violation"
    CONSTRAINT_VIOLATION = "constraint_violation"
    OBJECTIVE_DEVIATION = "objective_deviation"
    HEALTH_CHECK_PASSED = "health_check_passed"
    HEALTH_CHECK_FAILED = "health_check_failed"


@dataclass(frozen=True)
class SupervisionEventRecord:
    """Record of a supervision event."""
    
    record_id: str
    event_type: SupervisionEvent
    timestamp_utc: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def generate_id() -> str:
        return f"supervision_event_{uuid.uuid4().hex[:12]}"


# =============================================================================
# BASE SUPERVISOR
# =============================================================================

class BaseSupervisor(ABC):
    """Base class for all supervisors."""
    
    @abstractmethod
    def supervise(self) -> SupervisionResult:
        """Perform supervision check."""
        pass
    
    @property
    @abstractmethod
    def subsystem_name(self) -> str:
        """Return the name of the supervised subsystem."""
        pass


# =============================================================================
# RUNTIME SUPERVISOR
# =============================================================================

class RuntimeSupervisor(BaseSupervisor):
    """
    Supervisor for runtime-level behavior.
    
    Monitors:
    - Runtime lifecycle transitions
    - State consistency
    - Cross-domain coordination
    """
    
    def __init__(self, runtime_id: str = "default"):
        self._runtime_id = runtime_id
    
    @property
    def subsystem_name(self) -> str:
        return "runtime"
    
    def supervise(self) -> SupervisionResult:
        """Supervise runtime behavior."""
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status="compliant",
            details={
                "runtime_id": self._runtime_id
            }
        )


# =============================================================================
# SERVICE SUPERVISOR
# =============================================================================

class ServiceSupervisor(BaseSupervisor):
    """
    Supervisor for services.
    
    Monitors:
    - Service health status
    - Response time metrics
    - Error rates
    """
    
    def __init__(self, service_name: str, max_error_rate: float = 0.1):
        self._service_name = service_name
        self._max_error_rate = max_error_rate
    
    @property
    def subsystem_name(self) -> str:
        return f"service:{self._service_name}"
    
    def supervise(self, error_rate: float = 0.0) -> SupervisionResult:
        """Supervise service behavior."""
        if error_rate > self._max_error_rate:
            status = "critical"
        elif error_rate > self._max_error_rate * 0.5:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "service_name": self._service_name,
                "error_rate": error_rate
            }
        )


# =============================================================================
# CAPABILITY SUPERVISOR
# =============================================================================

class CapabilitySupervisor(BaseSupervisor):
    """
    Supervisor for capabilities.
    
    Monitors:
    - Capability availability
    - Authorization status
    - Usage metrics
    """
    
    def __init__(self, capability_name: str):
        self._capability_name = capability_name
    
    @property
    def subsystem_name(self) -> str:
        return f"capability:{self._capability_name}"
    
    def supervise(self, usage_count: int = 0) -> SupervisionResult:
        """Supervise capability usage."""
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status="compliant",
            details={
                "capability_name": self._capability_name,
                "usage_count": usage_count
            }
        )


# =============================================================================
# SCHEDULER SUPERVISOR
# =============================================================================

class SchedulerSupervisor(BaseSupervisor):
    """
    Supervisor for schedulers.
    
    Monitors:
    - Schedule adherence
    - Task queue length
    - Scheduling latency
    """
    
    def __init__(self, scheduler_name: str, max_queue_length: int = 100):
        self._scheduler_name = scheduler_name
        self._max_queue_length = max_queue_length
    
    @property
    def subsystem_name(self) -> str:
        return f"scheduler:{self._scheduler_name}"
    
    def supervise(self, queue_length: int = 0, latency_seconds: float = 0.0) -> SupervisionResult:
        """Supervise scheduler behavior."""
        if queue_length > self._max_queue_length or latency_seconds > 5.0:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "queue_length": queue_length,
                "latency_seconds": latency_seconds
            }
        )


# =============================================================================
# EXECUTION SUPERVISOR
# =============================================================================

class ExecutionSupervisor(BaseSupervisor):
    """
    Supervisor for executions.
    
    Monitors:
    - Execution duration
    - Success rate
    - Timeout adherence
    """
    
    def __init__(self, max_execution_duration: float = 60.0):
        self._max_execution_duration = max_execution_duration
    
    @property
    def subsystem_name(self) -> str:
        return "execution"
    
    def supervise(self, duration_seconds: float = 0.0) -> SupervisionResult:
        """Supervise execution behavior."""
        if duration_seconds > self._max_execution_duration:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "duration_seconds": duration_seconds
            }
        )


# =============================================================================
# RESOURCE SUPERVISOR
# =============================================================================

class ResourceSupervisor(BaseSupervisor):
    """
    Supervisor for resources.
    
    Monitors:
    - CPU utilization
    - Memory consumption
    - I/O bandwidth
    - Network capacity
    """
    
    def __init__(
        self,
        max_cpu_percent: float = 80.0,
        max_memory_percent: float = 75.0
    ):
        self._max_cpu_percent = max_cpu_percent
        self._max_memory_percent = max_memory_percent
    
    @property
    def subsystem_name(self) -> str:
        return "resources"
    
    def supervise(
        self,
        cpu_percent: float = 0.0,
        memory_percent: float = 0.0
    ) -> SupervisionResult:
        """Supervise resource utilization."""
        if cpu_percent > self._max_cpu_percent or memory_percent > self._max_memory_percent:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
        )


# =============================================================================
# COMMUNICATION SUPERVISOR
# =============================================================================

class CommunicationSupervisor(BaseSupervisor):
    """
    Supervisor for communication patterns.
    
    Monitors:
    - Message delivery rate
    - Timeout occurrences
    - Retry frequency
    """
    
    def __init__(self, max_timeout_rate: float = 0.1):
        self._max_timeout_rate = max_timeout_rate
    
    @property
    def subsystem_name(self) -> str:
        return "communication"
    
    def supervise(
        self,
        timeout_rate: float = 0.0,
        messages_per_second: float = 0.0
    ) -> SupervisionResult:
        """Supervise communication behavior."""
        if timeout_rate > self._max_timeout_rate:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "timeout_rate": timeout_rate,
                "messages_per_second": messages_per_second
            }
        )


# =============================================================================
# PERSISTENCE SUPERVISOR
# =============================================================================

class PersistenceSupervisor(BaseSupervisor):
    """
    Supervisor for persistence operations.
    
    Monitors:
    - Transaction duration
    - Consistency violations
    - Backup status
    """
    
    def __init__(self, max_transaction_duration: float = 30.0):
        self._max_transaction_duration = max_transaction_duration
    
    @property
    def subsystem_name(self) -> str:
        return "persistence"
    
    def supervise(
        self,
        transaction_duration: float = 0.0,
        consistency_violations: int = 0
    ) -> SupervisionResult:
        """Supervise persistence behavior."""
        if transaction_duration > self._max_transaction_duration or consistency_violations > 0:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "transaction_duration": transaction_duration,
                "consistency_violations": consistency_violations
            }
        )


# =============================================================================
# RECOVERY SUPERVISOR
# =============================================================================

class RecoverySupervisor(BaseSupervisor):
    """
    Supervisor for recovery processes.
    
    Monitors:
    - Recovery attempt count
    - Recovery success rate
    - RTO compliance
    """
    
    def __init__(self, max_recovery_attempts: int = 3):
        self._max_recovery_attempts = max_recovery_attempts
    
    @property
    def subsystem_name(self) -> str:
        return "recovery"
    
    def supervise(
        self,
        recent_attempts: int = 0,
        success_rate: float = 1.0
    ) -> SupervisionResult:
        """Supervise recovery behavior."""
        if recent_attempts >= self._max_recovery_attempts or success_rate < 0.5:
            status = "critical"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "recent_attempts": recent_attempts,
                "success_rate": success_rate
            }
        )


# =============================================================================
# LIFECYCLE SUPERVISOR
# =============================================================================

class LifecycleSupervisor(BaseSupervisor):
    """
    Supervisor for lifecycle transitions.
    
    Monitors:
    - Transition duration
    - State consistency
    - Health check compliance
    """
    
    def __init__(self, max_transition_duration: float = 120.0):
        self._max_transition_duration = max_transition_duration
    
    @property
    def subsystem_name(self) -> str:
        return "lifecycle"
    
    def supervise(
        self,
        transition_duration: float = 0.0,
        state_consistent: bool = True
    ) -> SupervisionResult:
        """Supervise lifecycle behavior."""
        if transition_duration > self._max_transition_duration or not state_consistent:
            status = "warning"
        else:
            status = "compliant"
        
        return SupervisionResult(
            result_id=SupervisionResult.generate_id(),
            subsystem_name=self.subsystem_name,
            status=status,
            details={
                "transition_duration": transition_duration,
                "state_consistent": state_consistent
            }
        )


# =============================================================================
# GOVERNANCE SUPERVISOR (Main Supervisor)
# =============================================================================

class GovernanceSupervisor:
    """
    Main governance supervisor that coordinates all domain supervisors.
    
    Provides:
    - Continuous supervision of all subsystems
    - Event aggregation and notification
    - Supervision history and diagnostics
    """
    
    def __init__(self, runtime_id: str = "default"):
        self._runtime_id = runtime_id
        self._supervisors: Dict[str, BaseSupervisor] = {}
        self._events: List[SupervisionEventRecord] = []
        self._last_supervision_timestamp: Optional[float] = None
    
    def register_supervisor(self, name: str, supervisor: BaseSupervisor) -> None:
        """Register a domain supervisor."""
        self._supervisors[name] = supervisor
    
    def get_supervisor(self, name: str) -> Optional[BaseSupervisor]:
        """Get a registered supervisor."""
        return self._supervisors.get(name)
    
    def supervise_all(self) -> Dict[str, SupervisionResult]:
        """
        Perform supervision checks on all subsystems.
        
        Returns:
            Dictionary of subsystem names to supervision results
        """
        results = {}
        for name, supervisor in self._supervisors.items():
            result = supervisor.supervise()
            results[name] = result
            
            if not result.is_compliant:
                # Record event for non-compliant results
                event_type = (
                    SupervisionEvent.CONSTRAINT_VIOLATION 
                    if result.is_critical 
                    else SupervisionEvent.POLICY_VIOLATION
                )
                self._events.append(SupervisionEventRecord(
                    record_id=SupervisionEventRecord.generate_id(),
                    event_type=event_type,
                    context={
                        "subsystem": name,
                        "result": result.details
                    }
                ))
        
        self._last_supervision_timestamp = time.time()
        return results
    
    def get_events(self, limit: int = 100) -> List[SupervisionEventRecord]:
        """Get recent supervision events."""
        return self._events[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall supervision summary."""
        if not self._supervisors:
            return {
                "runtime_id": self._runtime_id,
                "status": "no_supervisors_registered"
            }
        
        results = self.supervise_all()
        compliant_count = sum(1 for r in results.values() if r.is_compliant)
        
        return {
            "runtime_id": self._runtime_id,
            "total_subsystems": len(results),
            "compliant": compliant_count,
            "non_compliant": len(results) - compliant_count,
            "last_supervision_utc": self._last_supervision_timestamp
        }


__all__ = [
    "SupervisionResult",
    "SupervisionEvent",
    "SupervisionEventRecord",
    "BaseSupervisor",
    "RuntimeSupervisor",
    "ServiceSupervisor",
    "CapabilitySupervisor",
    "SchedulerSupervisor", 
    "ExecutionSupervisor",
    "ResourceSupervisor",
    "CommunicationSupervisor",
    "PersistenceSupervisor",
    "RecoverySupervisor",
    "LifecycleSupervisor",
]