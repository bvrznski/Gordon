# Operational Objectives
# ======================

"""
Operational objectives - declarative specifications of what must be achieved.

Objectives are:
- Declarative: Described as desired states, not implementations
- Continuously evaluated: Governance checks alignment throughout execution
- Priority-weighted: Some objectives take precedence over others
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BASE OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class OperationalObjective:
    """
    Base class for operational objectives.
    
    Every objective must specify what should be achieved and how compliance
    is measured.
    """
    
    objective_id: str
    name: str
    description: str
    priority: int  # Higher = more important
    enabled: bool = True
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for an objective."""
        return f"objective_{uuid.uuid4().hex[:12]}"
    
    @property
    def objective_type(self) -> str:
        """Return the type of operational objective."""
        return self.__class__.__name__


# =============================================================================
# AVAILABILITY OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class AvailabilityObjective(OperationalObjective):
    """
    Objective: System availability must meet target percentage.
    
    Metrics:
    - Uptime percentage
    - Mean time between failures (MTBF)
    - Mean time to recovery (MTTR)
    """
    
    min_availability_percent: float = 99.0  # Target: 99% uptime
    
    def __init__(self):
        super().__init__(
            objective_id="availability_objective",
            name="Availability Objective",
            description="System must maintain minimum availability percentage",
            priority=1,  # Critical
        )


# =============================================================================
# PERFORMANCE OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class PerformanceObjective(OperationalObjective):
    """
    Objective: System performance must meet response time targets.
    
    Metrics:
    - Response time p50/p95/p99
    - Throughput (requests per second)
    - Latency percentiles
    """
    
    max_response_time_p99_ms: float = 100.0
    min_throughput_rps: float = 1000.0
    
    def __init__(self):
        super().__init__(
            objective_id="performance_objective",
            name="Performance Objective",
            description="System response time must meet latency targets",
            priority=2,
        )


# =============================================================================
# RELIABILITY OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class ReliabilityObjective(OperationalObjective):
    """
    Objective: System must maintain reliable operation.
    
    Metrics:
    - Error rate percentage
    - Failed request ratio
    - Consistency guarantees met
    """
    
    max_error_rate_percent: float = 0.1  # Max 0.1% errors
    
    def __init__(self):
        super().__init__(
            objective_id="reliability_objective",
            name="Reliability Objective",
            description="System error rate must stay below threshold",
            priority=2,
        )


# =============================================================================
# SAFETY OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class SafetyObjective(OperationalObjective):
    """
    Objective: System operation must be safe.
    
    Metrics:
    - No security breaches
    - No data corruption
    - No resource exhaustion
    """
    
    def __init__(self):
        super().__init__(
            objective_id="safety_objective",
            name="Safety Objective",
            description="System operation must not compromise safety",
            priority=3,  # Highest priority
        )


# =============================================================================
# RESOURCE OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class ResourceObjective(OperationalObjective):
    """
    Objective: Resource utilization must stay within budget.
    
    Metrics:
    - CPU usage percentage
    - Memory consumption
    - I/O bandwidth
    - Network capacity
    """
    
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 75.0
    
    def __init__(self):
        super().__init__(
            objective_id="resource_objective",
            name="Resource Objective",
            description="Resource usage must stay within budgeted limits",
            priority=1,
        )


# =============================================================================
# SCHEDULING OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class SchedulingObjective(OperationalObjective):
    """
    Objective: Tasks must be scheduled and executed on time.
    
    Metrics:
    - Task start time adherence
    - Task completion rate
    - Schedule compliance
    """
    
    max_task_delay_seconds: float = 5.0
    
    def __init__(self):
        super().__init__(
            objective_id="scheduling_objective",
            name="Scheduling Objective",
            description="Tasks must be scheduled and executed on time",
            priority=2,
        )


# =============================================================================
# EXECUTION OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class ExecutionObjective(OperationalObjective):
    """
    Objective: Executions must complete within constraints.
    
    Metrics:
    - Execution duration
    - Execution success rate
    - Timeout adherence
    """
    
    max_execution_duration_seconds: float = 30.0
    
    def __init__(self):
        super().__init__(
            objective_id="execution_objective",
            name="Execution Objective",
            description="Executions must complete within time limits",
            priority=2,
        )


# =============================================================================
# RECOVERY OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class RecoveryObjective(OperationalObjective):
    """
    Objective: System must recover from failures quickly.
    
    Metrics:
    - Recovery time objective (RTO)
    - Recovery point objective (RPO)
    - Automatic recovery success rate
    """
    
    rto_seconds: float = 60.0  # Recover within 60 seconds
    
    def __init__(self):
        super().__init__(
            objective_id="recovery_objective",
            name="Recovery Objective",
            description="System must recover from failures within time limit",
            priority=2,
        )


# =============================================================================
# DEPLOYMENT OBJECTIVE
# =============================================================================

@dataclass(frozen=True)
class DeploymentObjective(OperationalObjective):
    """
    Objective: Deployments must meet quality standards.
    
    Metrics:
    - Deployment success rate
    - Rollback rate
    - Validation pass rate
    """
    
    min_deployment_success_rate_percent: float = 95.0
    
    def __init__(self):
        super().__init__(
            objective_id="deployment_objective",
            name="Deployment Objective",
            description="Deployments must meet quality standards",
            priority=2,
        )


# =============================================================================
# OBJECTIVE REGISTRY
# =============================================================================

class OperationalObjectivesRegistry:
    """Registry of all operational objectives."""
    
    _objectives: Dict[str, OperationalObjective] = {}
    
    def __init__(self):
        self._register_default_objectives()
    
    def _register_default_objectives(self) -> None:
        """Register default objective instances."""
        objectives = [
            AvailabilityObjective(),
            PerformanceObjective(),
            ReliabilityObjective(),
            SafetyObjective(),
            ResourceObjective(),
            SchedulingObjective(),
            ExecutionObjective(),
            RecoveryObjective(),
            DeploymentObjective(),
        ]
        
        for obj in objectives:
            self._objectives[obj.objective_id] = obj
    
    def get_objective(self, objective_id: str) -> Optional[OperationalObjective]:
        """Get an objective by its ID."""
        return self._objectives.get(objective_id)
    
    def get_all_objectives(self) -> List[OperationalObjective]:
        """Get all registered objectives."""
        return list(self._objectives.values())
    
    def get_enabled_objectives(self) -> List[OperationalObjective]:
        """Get only enabled objectives."""
        return [o for o in self._objectives.values() if o.enabled]
    
    def sort_by_priority(self, objectives: List[OperationalObjective]) -> List[OperationalObjective]:
        """Sort objectives by priority (highest first)."""
        return sorted(objectives, key=lambda o: o.priority, reverse=True)


__all__ = [
    "OperationalObjective",
    "AvailabilityObjective",
    "PerformanceObjective",
    "ReliabilityObjective",
    "SafetyObjective",
    "ResourceObjective",
    "SchedulingObjective",
    "ExecutionObjective",
    "RecoveryObjective",
    "DeploymentObjective",
    "OperationalObjectivesRegistry",
]