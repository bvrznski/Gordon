# Governance Policies
# ===================

"""
Governance policies - declarative rules defining acceptable behavior patterns,
constraints, and operational boundaries.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum, auto
import uuid
import time


# =============================================================================
# BASE POLICY
# =============================================================================

@dataclass(frozen=True)
class GovernancePolicy:
    """Base class for governance policies."""
    
    policy_id: str
    name: str
    description: str
    enabled: bool = True
    
    @staticmethod
    def generate_id() -> str:
        return f"policy_{uuid.uuid4().hex[:12]}"
    
    @property
    def policy_type(self) -> str:
        return self.__class__.__name__


# =============================================================================
# OPERATIONAL POLICIES
# =============================================================================

@dataclass(frozen=True)
class OperationalPolicy(GovernancePolicy):
    """Operational behavior policy."""
    
    min_uptime_percent: float = 95.0
    max_error_rate_percent: float = 1.0
    
    def __init__(self):
        super().__init__(
            policy_id="operational_policy",
            name="Operational Policy",
            description="Defines operational behavior expectations",
            enabled=True,
        )


# =============================================================================
# ADMISSION POLICIES
# =============================================================================

@dataclass(frozen=True)
class AdmissionPolicy(GovernancePolicy):
    """Policy for admitting work to the system."""
    
    max_admission_rate_per_second: float = 100.0
    priority_threshold: int = 0
    
    def __init__(self):
        super().__init__(
            policy_id="admission_policy",
            name="Admission Policy",
            description="Controls what work is admitted to the system",
            enabled=True,
        )


# =============================================================================
# EXECUTION POLICIES
# =============================================================================

@dataclass(frozen=True)
class ExecutionPolicy(GovernancePolicy):
    """Policy for execution behavior."""
    
    max_execution_duration_seconds: float = 60.0
    max_concurrent_executions: int = 100
    
    def __init__(self):
        super().__init__(
            policy_id="execution_policy",
            name="Execution Policy",
            description="Controls execution behavior and limits",
            enabled=True,
        )


# =============================================================================
# RECOVERY POLICIES
# =============================================================================

@dataclass(frozen=True)
class RecoveryPolicy(GovernancePolicy):
    """Policy for recovery operations."""
    
    auto_recovery_enabled: bool = True
    max_recovery_attempts: int = 3
    
    def __init__(self):
        super().__init__(
            policy_id="recovery_policy",
            name="Recovery Policy",
            description="Controls automatic recovery behavior",
            enabled=True,
        )


# =============================================================================
# DEGRADATION POLICIES
# =============================================================================

@dataclass(frozen=True)
class DegradationPolicy(GovernancePolicy):
    """Policy for graceful degradation."""
    
    degradation_enabled: bool = True
    min_acceptable_performance_percent: float = 50.0
    
    def __init__(self):
        super().__init__(
            policy_id="degradation_policy",
            name="Degradation Policy",
            description="Controls graceful degradation behavior",
            enabled=True,
        )


# =============================================================================
# INTERVENTION POLICIES
# =============================================================================

@dataclass(frozen=True)
class InterventionPolicy(GovernancePolicy):
    """Policy for intervention actions."""
    
    auto_intervention_enabled: bool = True
    escalation_timeout_seconds: float = 30.0
    
    def __init__(self):
        super().__init__(
            policy_id="intervention_policy",
            name="Intervention Policy",
            description="Controls when and how interventions occur",
            enabled=True,
        )


# =============================================================================
# ESCALATION POLICIES
# =============================================================================

@dataclass(frozen=True)
class EscalationPolicy(GovernancePolicy):
    """Policy for escalation procedures."""
    
    max_escalation_level: int = 3
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    
    def __init__(self):
        super().__init__(
            policy_id="escalation_policy",
            name="Escalation Policy",
            description="Controls escalation procedures and notifications",
            enabled=True,
        )


# =============================================================================
# OPTIMIZATION POLICIES
# =============================================================================

@dataclass(frozen=True)
class OptimizationPolicy(GovernancePolicy):
    """Policy for optimization opportunities."""
    
    auto_optimization_enabled: bool = True
    min_utilization_percent: float = 30.0
    
    def __init__(self):
        super().__init__(
            policy_id="optimization_policy",
            name="Optimization Policy",
            description="Controls when optimization actions are triggered",
            enabled=True,
        )


# =============================================================================
# MAINTENANCE POLICIES
# =============================================================================

@dataclass(frozen=True)
class MaintenancePolicy(GovernancePolicy):
    """Policy for maintenance operations."""
    
    maintenance_window_enabled: bool = True
    max_maintenance_duration_hours: int = 4
    
    def __init__(self):
        super().__init__(
            policy_id="maintenance_policy",
            name="Maintenance Policy",
            description="Controls maintenance operation windows and limits",
            enabled=True,
        )


# =============================================================================
# POLICY ENFORCEMENT RESULT
# =============================================================================

class EnforcementResult(Enum):
    """Result of policy enforcement."""
    
    COMPLIANT = "compliant"
    VIOLATION_WARNING = "violation_warning"
    VIOLATION_CRITICAL = "violation_critical"


@dataclass(frozen=True)
class PolicyEnforcementResult:
    """Result of enforcing a policy against runtime state."""
    
    result_id: str
    policy_id: str
    policy_name: str
    enforcement_result: EnforcementResult
    timestamp_utc: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def generate_id() -> str:
        return f"enforcement_{uuid.uuid4().hex[:12]}"
    
    @property
    def is_violation(self) -> bool:
        return self.enforcement_result in (
            EnforcementResult.VIOLATION_WARNING,
            EnforcementResult.VIOLATION_CRITICAL,
        )
    
    @property
    def is_critical(self) -> bool:
        return self.enforcement_result == EnforcementResult.VIOLATION_CRITICAL


# =============================================================================
# POLICY EVALUATION CONTEXT
# =============================================================================

@dataclass
class PolicyEvaluationContext:
    """Context for policy evaluation."""
    
    context_id: str
    timestamp_utc: float = field(default_factory=time.time)
    runtime_state: Dict[str, Any] = field(default_factory=dict)
    event_type: Optional[str] = None
    source_component: Optional[str] = None
    
    @staticmethod
    def generate_id() -> str:
        return f"context_{uuid.uuid4().hex[:12]}"
    
    @property
    def is_emergency(self) -> bool:
        """Check if this is an emergency context."""
        return self.runtime_state.get("emergency_mode", False)


# =============================================================================
# POLICY REGISTRY
# =============================================================================

class GovernancePoliciesRegistry:
    """Registry of all governance policies."""
    
    _policies: Dict[str, GovernancePolicy] = {}
    
    def __init__(self):
        self._register_default_policies()
    
    def _register_default_policies(self) -> None:
        """Register default policy instances."""
        policies = [
            OperationalPolicy(),
            AdmissionPolicy(),
            ExecutionPolicy(),
            RecoveryPolicy(),
            DegradationPolicy(),
            InterventionPolicy(),
            EscalationPolicy(),
            OptimizationPolicy(),
            MaintenancePolicy(),
        ]
        
        for policy in policies:
            self._policies[policy.policy_id] = policy
    
    def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        """Get a policy by its ID."""
        return self._policies.get(policy_id)
    
    def get_all_policies(self) -> List[GovernancePolicy]:
        """Get all registered policies."""
        return list(self._policies.values())
    
    def get_enabled_policies(self) -> List[GovernancePolicy]:
        """Get only enabled policies."""
        return [p for p in self._policies.values() if p.enabled]
    
    def evaluate_policy(
        self,
        policy: GovernancePolicy,
        context: PolicyEvaluationContext
    ) -> PolicyEnforcementResult:
        """Evaluate a policy against runtime state."""
        # Simplified evaluation - actual implementation would check specific metrics
        if isinstance(policy, OperationalPolicy):
            error_rate = context.runtime_state.get("error_rate_percent", 0)
            if error_rate > policy.max_error_rate_percent:
                return PolicyEnforcementResult(
                    result_id=PolicyEnforcementResult.generate_id(),
                    policy_id=policy.policy_id,
                    policy_name=policy.name,
                    enforcement_result=EnforcementResult.VIOLATION_CRITICAL
                )
        
        return PolicyEnforcementResult(
            result_id=PolicyEnforcementResult.generate_id(),
            policy_id=policy.policy_id,
            policy_name=policy.name,
            enforcement_result=EnforcementResult.COMPLIANT
        )


__all__ = [
    "GovernancePolicy",
    "OperationalPolicy",
    "AdmissionPolicy",
    "ExecutionPolicy",
    "RecoveryPolicy",
    "DegradationPolicy",
    "InterventionPolicy",
    "EscalationPolicy",
    "OptimizationPolicy",
    "MaintenancePolicy",
    "EnforcementResult",
    "PolicyEnforcementResult",
    "PolicyEvaluationContext",
    "GovernancePoliciesRegistry",
]