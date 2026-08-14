# Gordon Core: Runtime Upgrade Architecture (Phase 3.33)
"""
Runtime Upgrade Architecture - Provides canonical upgrade strategies and
execution framework for runtime upgrades in the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# UPGRADE TYPE ENUMERATION
# ============================================================================

class UpgradeType(Enum):
    """
    Canonical upgrade types for runtime components.
    
    - ROLLING: Gradual upgrade with zero downtime
    - CANARY: Gradual rollout to subset of nodes
    - BLUE_GREEN: Complete environment switch after validation
    - IN_PLACE: Direct in-place upgrade (requires restart)
    - RESTART_FREE: Upgrade without service interruption
    """
    
    ROLLING = "rolling"           # Gradual with zero downtime
    CANARY = "canary"            # Gradual rollout to subset
    BLUE_GREEN = "blue-green"     # Complete environment switch
    IN_PLACE = "in-place"        # Direct in-place (restart required)
    RESTART_FREE = "restart-free"  # No restart needed


# ============================================================================
# UPGRADE POLICY MODEL
# ============================================================================

@dataclass(frozen=True)
class UpgradePolicy:
    """
    Immutable upgrade policy for a runtime component.
    
    Defines the rules and constraints for upgrading components including
    validation requirements, rollback strategies, and execution constraints.
    """
    
    # Policy identity
    id: str                        # Unique policy identifier
    
    # Component information
    component_id: str             # ID of component to upgrade
    
    # Upgrade configuration
    strategy: UpgradeType         # Upgrade strategy to use
    version_from: str             # Source version
    version_to: str               # Target version
    
    # Timeline
    scheduled_at: datetime        # When upgrade is scheduled
    max_duration_minutes: int     # Maximum allowed duration
    
    # Constraints
    min_instances: int = 1        # Minimum instances that must remain active
    requires_validation: bool = True  # Whether validation is required
    rollback_on_failure: bool = True   # Rollback on failure
    
    @property
    def can_rollback(self) -> bool:
        """Check if rollback is supported."""
        return self.rollback_on_failure and self.strategy not in (
            UpgradeType.IN_PLACE, UpgradeType.RESTART_FREE
        )
    
    @property
    def is_zero_downtime(self) -> bool:
        """Check if upgrade has zero downtime."""
        return self.strategy in (UpgradeType.ROLLING, UpgradeType.CANARY)


# ============================================================================
# UPGRADE EXECUTION MODEL
# ============================================================================

@dataclass(frozen=True)
class UpgradeExecution:
    """
    Immutable execution record for an upgrade.
    
    Represents a single run of an upgrade policy with its actual execution
    results and progress tracking.
    """
    
    # Execution identity
    id: str                        # Unique execution identifier
    
    # Policy reference
    policy_id: str                # ID of the executed policy
    
    # Component information
    component_id: str             # ID of component being upgraded
    version_from: str             # Source version (captured at start)
    version_to: str               # Target version (from policy)
    
    # Execution state
    status: "UpgradeStatus"       # Current execution status
    progress: float = 0.0         # Progress as fraction (0.0 to 1.0)
    
    # Timing
    scheduled_at: datetime        # Original schedule time
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    rollback_on_failure: bool = True
    rolled_back: bool = False     # Whether rollback was executed
    
    @property
    def is_complete(self) -> bool:
        """Check if execution has reached a terminal state."""
        return self.status in (UpgradeStatus.COMPLETED, UpgradeStatus.FAILED)
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Get the actual duration in minutes if completed."""
        if not self.started_at or not self.completed_at:
            return None
        
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() / 60)


# ============================================================================
# UPGRADE STATUS ENUMERATION
# ============================================================================

class UpgradeStatus(Enum):
    """
    Canonical upgrade execution statuses.
    """
    
    SCHEDULED = "scheduled"       # Waiting for scheduled time
    PENDING = "pending"           # Ready to start
    RUNNING = "running"          # Currently executing
    VALIDATING = "validating"     # Post-execution validation phase
    COMPLETED = "completed"      # Successfully completed
    FAILED = "failed"            # Execution failed (not rolled back)
    ROLLED_BACK = "rolled-back"  # Rolled back after failure


# ============================================================================
# UPGRADE EXECUTOR
# ============================================================================

class UpgradeExecutor:
    """
    Executor for running upgrades.
    
    Manages the execution of upgrade policies, tracks progress, handles
    validation, and executes rollbacks when needed.
    """
    
    def __init__(self):
        self._executions: Dict[str, UpgradeExecution] = {}
        self._policies: Dict[str, UpgradePolicy] = {}
    
    def register_policy(self, policy: UpgradePolicy) -> None:
        """Register an upgrade policy."""
        self._policies[policy.id] = policy
    
    def create_execution(
        self,
        execution_id: str,
        policy_id: str,
        component_id: str
    ) -> UpgradeExecution:
        """Create a new upgrade execution."""
        policy = self._policies.get(policy_id)
        
        if not policy:
            raise ValueError(f"Policy '{policy_id}' not found")
        
        execution = UpgradeExecution(
            id=execution_id,
            policy_id=policy_id,
            component_id=component_id,
            version_from=policy.version_from,
            version_to=policy.version_to,
            status=UpgradeStatus.PENDING,
            scheduled_at=policy.scheduled_at,
            rollback_on_failure=policy.rollback_on_failure
        )
        
        self._executions[execution_id] = execution
        return execution
    
    def start_execution(self, execution_id: str) -> UpgradeExecution:
        """Start an upgrade execution."""
        execution = self._executions.get(execution_id)
        
        if not execution:
            raise ValueError(f"Execution '{execution_id}' not found")
        
        # Mark as running
        execution = UpgradeExecution(
            id=execution.id,
            policy_id=execution.policy_id,
            component_id=execution.component_id,
            version_from=execution.version_from,
            version_to=execution.version_to,
            status=UpgradeStatus.RUNNING,
            progress=0.1,
            scheduled_at=execution.scheduled_at,
            started_at=datetime.now(),
            rollback_on_failure=execution.rollback_on_failure
        )
        
        self._executions[execution_id] = execution
        return execution
    
    def validate_execution(self, execution_id: str) -> bool:
        """Validate an upgrade execution."""
        execution = self._executions.get(execution_id)
        
        if not execution:
            raise ValueError(f"Execution '{execution_id}' not found")
        
        # Mark as validating
        execution = UpgradeExecution(
            id=execution.id,
            policy_id=execution.policy_id,
            component_id=execution.component_id,
            version_from=execution.version_from,
            version_to=execution.version_to,
            status=UpgradeStatus.VALIDATING,
            progress=min(1.0, execution.progress + 0.1),
            scheduled_at=execution.scheduled_at,
            started_at=execution.started_at,
            rollback_on_failure=execution.rollback_on_failure
        )
        
        self._executions[execution_id] = execution
        return True
    
    def complete_execution(self, execution_id: str) -> UpgradeExecution:
        """Complete an upgrade execution successfully."""
        execution = self._executions.get(execution_id)
        
        if not execution:
            raise ValueError(f"Execution '{execution_id}' not found")
        
        # Mark as completed
        execution = UpgradeExecution(
            id=execution.id,
            policy_id=execution.policy_id,
            component_id=execution.component_id,
            version_from=execution.version_from,
            version_to=execution.version_to,
            status=UpgradeStatus.COMPLETED,
            progress=1.0,
            scheduled_at=execution.scheduled_at,
            started_at=execution.started_at,
            completed_at=datetime.now(),
            rollback_on_failure=execution.rollback_on_failure
        )
        
        self._executions[execution_id] = execution
        return execution
    
    def fail_execution(self, execution_id: str) -> UpgradeExecution:
        """Fail an upgrade execution."""
        execution = self._executions.get(execution_id)
        
        if not execution:
            raise ValueError(f"Execution '{execution_id}' not found")
        
        # Mark as failed
        execution = UpgradeExecution(
            id=execution.id,
            policy_id=execution.policy_id,
            component_id=execution.component_id,
            version_from=execution.version_from,
            version_to=execution.version_to,
            status=UpgradeStatus.FAILED,
            progress=execution.progress,
            scheduled_at=execution.scheduled_at,
            started_at=execution.started_at,
            rollback_on_failure=execution.rollback_on_failure
        )
        
        self._executions[execution_id] = execution
        
        # If rollback is enabled, also mark as rolled back
        if execution.rollback_on_failure:
            execution = UpgradeExecution(
                id=execution.id,
                policy_id=execution.policy_id,
                component_id=execution.component_id,
                version_from=execution.version_from,
                version_to=execution.version_to,
                status=UpgradeStatus.ROLLED_BACK,
                progress=1.0,
                scheduled_at=execution.scheduled_at,
                started_at=execution.started_at,
                completed_at=datetime.now(),
                rolled_back=True
            )
            self._executions[execution_id] = execution
        
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[UpgradeExecution]:
        """Get an upgrade execution by ID."""
        return self._executions.get(execution_id)
    
    def list_executions_for_policy(self, policy_id: str) -> List[UpgradeExecution]:
        """List all executions for a policy."""
        return [
            e for e in self._executions.values()
            if e.policy_id == policy_id
        ]
    
    def get_active_executions(self) -> List[UpgradeExecution]:
        """Get all currently active (non-terminal) executions."""
        return [
            e for e in self._executions.values()
            if not e.is_complete
        ]


# ============================================================================
# UPGRADE POLICY BUILDER
# ============================================================================

class UpgradePolicyBuilder:
    """
    Builder for constructing upgrade policies.
    
    Provides a fluent API for creating complex upgrade policies with
    multiple constraints and strategies.
    """
    
    def __init__(self):
        self._id: str = ""
        self._component_id: str = ""
        self._strategy: UpgradeType = UpgradeType.ROLLING
        self._version_from: str = "0.0.0"
        self._version_to: str = "1.0.0"
        self._scheduled_at: datetime = None
        self._max_duration_minutes: int = 60
        self._min_instances: int = 1
        self._requires_validation: bool = True
        self._rollback_on_failure: bool = True
    
    def with_id(self, policy_id: str) -> "UpgradePolicyBuilder":
        """Set the policy ID."""
        self._id = policy_id
        return self
    
    def for_component(self, component_id: str) -> "UpgradePolicyBuilder":
        """Set the component to upgrade."""
        self._component_id = component_id
        return self
    
    def using_strategy(self, strategy: UpgradeType) -> "UpgradePolicyBuilder":
        """Set the upgrade strategy."""
        self._strategy = strategy
        return self
    
    def from_version(self, version: str) -> "UpgradePolicyBuilder":
        """Set the source version."""
        self._version_from = version
        return self
    
    def to_version(self, version: str) -> "UpgradePolicyBuilder":
        """Set the target version."""
        self._version_to = version
        return self
    
    def schedule_at(self, date: datetime) -> "UpgradePolicyBuilder":
        """Set the upgrade schedule time."""
        self._scheduled_at = date
        return self
    
    def with_max_duration(self, minutes: int) -> "UpgradePolicyBuilder":
        """Set the maximum allowed duration in minutes."""
        self._max_duration_minutes = minutes
        return self
    
    def with_min_instances(self, count: int) -> "UpgradePolicyBuilder":
        """Set the minimum instances that must remain active."""
        self._min_instances = count
        return self
    
    def requiring_validation(self, required: bool = True) -> "UpgradePolicyBuilder":
        """Specify whether validation is required."""
        self._requires_validation = required
        return self
    
    def with_rollback_on_failure(self, rollback: bool = True) -> "UpgradePolicyBuilder":
        """Specify whether to rollback on failure."""
        self._rollback_on_failure = rollback
        return self
    
    def build(self) -> UpgradePolicy:
        """Build the upgrade policy."""
        if not all([
            self._id,
            self._component_id,
            self._scheduled_at
        ]):
            raise ValueError("All required fields must be set")
        
        return UpgradePolicy(
            id=self._id,
            component_id=self._component_id,
            strategy=self._strategy,
            version_from=self._version_from,
            version_to=self._version_to,
            scheduled_at=self._scheduled_at,
            max_duration_minutes=self._max_duration_minutes,
            min_instances=self._min_instances,
            requires_validation=self._requires_validation,
            rollback_on_failure=self._rollback_on_failure
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def determine_upgrade_type(
    version_from: str,
    version_to: str,
    supports_zero_downtime: bool = True
) -> UpgradeType:
    """Determine the most appropriate upgrade type based on version difference."""
    # Parse versions
    source_parts = [int(x) for x in version_from.split(".")]
    target_parts = [int(x) for x in version_to.split(".")]
    
    # Major version change typically requires full restart
    if source_parts[0] != target_parts[0]:
        return UpgradeType.BLUE_GREEN
    
    # Minor version change can often be zero-downtime
    if supports_zero_downtime:
        return UpgradeType.ROLLING
    
    # Without zero-downtime support, use in-place upgrade
    return UpgradeType.IN_PLACE


def calculate_upgrade_progress(execution: UpgradeExecution) -> float:
    """Calculate upgrade progress based on execution state."""
    if execution.status == UpgradeStatus.SCHEDULED:
        return 0.0
    elif execution.status == UpgradeStatus.PENDING:
        return 0.1
    elif execution.status == UpgradeStatus.RUNNING:
        return min(execution.progress, 0.9)
    elif execution.status == UpgradeStatus.VALIDATING:
        return min(execution.progress + 0.1, 1.0)
    elif execution.status == UpgradeStatus.COMPLETED:
        return 1.0
    else:  # FAILED or ROLLED_BACK
        return 0.0


def get_upgrade_status_summary(executions: List[UpgradeExecution]) -> Dict[str, Any]:
    """Get a summary of upgrade execution statuses."""
    if not executions:
        return {
            "total": 0,
            "scheduled": 0,
            "pending": 0,
            "running": 0,
            "validating": 0,
            "completed": 0,
            "failed": 0,
            "rolled_back": 0
        }
    
    summary = {
        "total": len(executions),
        "scheduled": sum(1 for e in executions if e.status == UpgradeStatus.SCHEDULED),
        "pending": sum(1 for e in executions if e.status == UpgradeStatus.PENDING),
        "running": sum(1 for e in executions if e.status == UpgradeStatus.RUNNING),
        "validating": sum(1 for e in executions if e.status == UpgradeStatus.VALIDATING),
        "completed": sum(1 for e in executions if e.status == UpgradeStatus.COMPLETED),
        "failed": sum(1 for e in executions if e.status == UpgradeStatus.FAILED),
        "rolled_back": sum(1 for e in executions if e.status == UpgradeStatus.ROLLED_BACK)
    }
    
    summary["success_rate"] = (
        summary["completed"] / summary["total"] * 100
        if summary["total"] > 0 else 0.0
    )
    
    return summary