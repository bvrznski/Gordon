# Runtime Constraints
# ===================

"""
Runtime constraints - declarative specifications of what must NOT happen.

Constraint violations trigger governance interventions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BASE CONSTRAINT
# =============================================================================

@dataclass(frozen=True)
class RuntimeConstraint:
    """Base class for runtime constraints."""
    
    constraint_id: str
    name: str
    description: str
    severity: str  # critical, warning, info
    
    @staticmethod
    def generate_id() -> str:
        return f"constraint_{uuid.uuid4().hex[:12]}"
    
    @property
    def constraint_type(self) -> str:
        return self.__class__.__name__


# =============================================================================
# RESOURCE LIMIT CONSTRAINTS
# =============================================================================

@dataclass(frozen=True)
class ResourceLimitConstraint(RuntimeConstraint):
    """Resource utilization limit constraint."""
    
    max_value: float
    resource_type: str = "cpu"  # cpu, memory, io, network
    
    def __init__(self, resource_name: str = "unknown"):
        super().__init__(
            constraint_id=f"resource_limit_{uuid.uuid4().hex[:8]}",
            name=f"{resource_name} Limit Constraint",
            description=f"{resource_name} must not exceed limit",
            severity="warning"
        )
        self.max_value = 100.0
        self.resource_type = "cpu"


@dataclass(frozen=True)
class ExecutionLimitConstraint(RuntimeConstraint):
    """Execution time limit constraint."""
    
    max_duration_seconds: float
    
    def __init__(self):
        super().__init__(
            constraint_id=f"exec_limit_{uuid.uuid4().hex[:8]}",
            name="Execution Duration Constraint",
            description="Execution must complete within time limit",
            severity="warning"
        )
        self.max_duration_seconds = 60.0


@dataclass(frozen=True)
class SchedulingLimitConstraint(RuntimeConstraint):
    """Scheduling latency constraint."""
    
    max_delay_seconds: float
    
    def __init__(self):
        super().__init__(
            constraint_id=f"schedule_limit_{uuid.uuid4().hex[:8]}",
            name="Scheduling Delay Constraint",
            description="Task scheduling delay must stay within limits",
            severity="warning"
        )
        self.max_delay_seconds = 5.0


@dataclass(frozen=True)
class ConcurrencyLimitConstraint(RuntimeConstraint):
    """Concurrency limit constraint."""
    
    max_concurrent: int
    
    def __init__(self):
        super().__init__(
            constraint_id=f"concurrency_limit_{uuid.uuid4().hex[:8]}",
            name="Concurrency Limit Constraint",
            description="Concurrent operations must stay within limits",
            severity="warning"
        )
        self.max_concurrent = 100


@dataclass(frozen=True)
class CommunicationLimitConstraint(RuntimeConstraint):
    """Communication rate limit constraint."""
    
    max_rate_per_second: float
    
    def __init__(self):
        super().__init__(
            constraint_id=f"comm_limit_{uuid.uuid4().hex[:8]}",
            name="Communication Rate Constraint",
            description="Communication rate must stay within limits",
            severity="warning"
        )
        self.max_rate_per_second = 1000.0


@dataclass(frozen=True)
class PersistenceLimitConstraint(RuntimeConstraint):
    """Persistence operation limit constraint."""
    
    max_duration_seconds: float
    
    def __init__(self):
        super().__init__(
            constraint_id=f"persistence_limit_{uuid.uuid4().hex[:8]}",
            name="Persistence Duration Constraint",
            description="Persistence operations must complete within time limit",
            severity="warning"
        )
        self.max_duration_seconds = 30.0


@dataclass(frozen=True)
class LifecycleLimitConstraint(RuntimeConstraint):
    """Lifecycle transition time constraint."""
    
    max_transition_seconds: float
    
    def __init__(self):
        super().__init__(
            constraint_id=f"lifecycle_limit_{uuid.uuid4().hex[:8]}",
            name="Lifecycle Transition Constraint",
            description="Lifecycle transitions must complete within time limit",
            severity="warning"
        )
        self.max_transition_seconds = 120.0


@dataclass(frozen=True)
class DeploymentLimitConstraint(RuntimeConstraint):
    """Deployment rate limit constraint."""
    
    max_deployments_per_hour: int
    
    def __init__(self):
        super().__init__(
            constraint_id=f"deploy_limit_{uuid.uuid4().hex[:8]}",
            name="Deployment Rate Constraint",
            description="Deployment rate must stay within limits",
            severity="critical"
        )
        self.max_deployments_per_hour = 24


@dataclass(frozen=True)
class PolicyLimitConstraint(RuntimeConstraint):
    """Policy evaluation limit constraint."""
    
    max_evaluation_seconds: float
    
    def __init__(self):
        super().__init__(
            constraint_id=f"policy_limit_{uuid.uuid4().hex[:8]}",
            name="Policy Evaluation Constraint",
            description="Policy evaluations must complete within time limit",
            severity="warning"
        )
        self.max_evaluation_seconds = 1.0


# =============================================================================
# CONSTRAINT VIOLATION
# =============================================================================

@dataclass(frozen=True)
class ConstraintViolation:
    """Represents a constraint violation."""
    
    violation_id: str
    constraint_id: str
    constraint_name: str
    timestamp_utc: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "warning"
    observed_value: Optional[Any] = None
    limit_value: Optional[Any] = None
    
    @staticmethod
    def generate_id() -> str:
        return f"violation_{uuid.uuid4().hex[:12]}"
    
    @property
    def is_critical(self) -> bool:
        return self.severity == "critical"


# =============================================================================
# CONSTRAINT EVALUATOR
# =============================================================================

class ConstraintEvaluator:
    """Evaluates constraints against runtime state."""
    
    def __init__(self):
        self._constraints: Dict[str, RuntimeConstraint] = {}
        self._violations: List[ConstraintViolation] = []
    
    def register_constraint(self, constraint: RuntimeConstraint) -> None:
        """Register a constraint for evaluation."""
        self._constraints[constraint.constraint_id] = constraint
    
    def unregister_constraint(self, constraint_id: str) -> None:
        """Unregister a constraint."""
        self._constraints.pop(constraint_id, None)
    
    def evaluate_all(
        self,
        state: Dict[str, Any]
    ) -> List[ConstraintViolation]:
        """Evaluate all constraints against runtime state."""
        violations = []
        
        for constraint_id, constraint in self._constraints.items():
            violation = self._evaluate_constraint(state, constraint)
            if violation:
                violations.append(violation)
                self._violations.append(violation)
        
        return violations
    
    def _evaluate_constraint(
        self,
        state: Dict[str, Any],
        constraint: RuntimeConstraint
    ) -> Optional[ConstraintViolation]:
        """Evaluate a single constraint."""
        # Simplified evaluation - actual implementation would check specific metrics
        if isinstance(constraint, ResourceLimitConstraint):
            resource_value = state.get(f"{constraint.resource_type}_usage_percent", 0)
            if resource_value > constraint.max_value:
                return ConstraintViolation(
                    violation_id=ConstraintViolation.generate_id(),
                    constraint_id=constraint.constraint_id,
                    constraint_name=constraint.name,
                    severity=constraint.severity,
                    observed_value=resource_value,
                    limit_value=constraint.max_value
                )
        elif isinstance(constraint, ExecutionLimitConstraint):
            exec_duration = state.get("execution_duration_seconds", 0)
            if exec_duration > constraint.max_duration_seconds:
                return ConstraintViolation(
                    violation_id=ConstraintViolation.generate_id(),
                    constraint_id=constraint.constraint_id,
                    constraint_name=constraint.name,
                    severity=constraint.severity,
                    observed_value=exec_duration,
                    limit_value=constraint.max_duration_seconds
                )
        
        return None
    
    def get_violations(self, limit: int = 100) -> List[ConstraintViolation]:
        """Get recent violations."""
        return self._violations[-limit:]
    
    def clear_violations(self) -> None:
        """Clear violation history."""
        self._violations.clear()


__all__ = [
    "RuntimeConstraint",
    "ResourceLimitConstraint",
    "ExecutionLimitConstraint",
    "SchedulingLimitConstraint",
    "ConcurrencyLimitConstraint",
    "CommunicationLimitConstraint",
    "PersistenceLimitConstraint",
    "LifecycleLimitConstraint",
    "DeploymentLimitConstraint",
    "PolicyLimitConstraint",
    "ConstraintViolation",
    "ConstraintEvaluator",
]