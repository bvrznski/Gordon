# Gordon Core: Repository Migration Framework (Phase 3.33)
"""
Repository Migration Framework - Provides canonical migration strategies and
framework for moving artifacts between contexts in the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# MIGRATION STRATEGY ENUMERATION
# ============================================================================

class MigrationStrategy(Enum):
    """
    Canonical migration strategies for artifacts.
    
    - ROLLING: Gradual migration with both old and new versions running simultaneously
    - BLUE_GREEN: Complete switch from old to new environment after validation
    - CANARY: Gradual rollout to subset of consumers, then full rollout
    - REVERSE_PROXY: Migration handled by proxy/adapter layer
    - BRIDGE: Temporary compatibility bridge during migration period
    """
    
    ROLLING = "rolling"           # Gradual migration with simultaneous versions
    BLUE_GREEN = "blue-green"     # Complete environment switch after validation
    CANARY = "canary"            # Gradual rollout to subset, then full
    REVERSE_PROXY = "reverse-proxy"  # Proxy/adapter handles translation
    BRIDGE = "bridge"            # Temporary compatibility bridge


# ============================================================================
# MIGRATION PLAN MODEL
# ============================================================================

@dataclass(frozen=True)
class MigrationPlan:
    """
    Immutable migration plan for an artifact.
    
    Defines the complete strategy and steps for migrating an artifact from
    its current state to a target state.
    """
    
    # Plan identity
    id: str                        # Unique plan identifier
    
    # Artifact information
    source_artifact: str          # Source artifact identifier
    target_artifact: str          # Target artifact identifier
    
    # Strategy
    strategy: MigrationStrategy   # Migration strategy to use
    
    # Timeline
    start_at: datetime            # When migration begins
    end_at: datetime              # When migration should complete
    
    # Steps (ordered sequence of migration actions)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Validation
    pre_migration_validation: bool = True   # Run validation before start
    post_migration_validation: bool = True  # Run validation after completion
    
    @property
    def duration_days(self) -> int:
        """Get the migration duration in days."""
        return (self.end_at - self.start_at).days
    
    @property
    def is_rolling(self) -> bool:
        """Check if using rolling strategy."""
        return self.strategy == MigrationStrategy.ROLLING
    
    @property
    def is_blue_green(self) -> bool:
        """Check if using blue-green strategy."""
        return self.strategy == MigrationStrategy.BLUE_GREEN
    
    def add_step(
        self,
        name: str,
        description: str,
        depends_on: Optional[List[str]] = None,
        rollback_on_failure: bool = True
    ) -> "MigrationPlan":
        """Add a step to the migration plan."""
        new_steps = list(self.steps)
        new_steps.append({
            "name": name,
            "description": description,
            "depends_on": depends_on or [],
            "rollback": rollback_on_failure
        })
        
        return MigrationPlan(
            id=self.id,
            source_artifact=self.source_artifact,
            target_artifact=self.target_artifact,
            strategy=self.strategy,
            start_at=self.start_at,
            end_at=self.end_at,
            steps=new_steps,
            pre_migration_validation=self.pre_migration_validation,
            post_migration_validation=self.post_migration_validation
        )
    
    def get_ready_steps(self, completed: List[str] = None) -> List[Dict[str, Any]]:
        """Get migration steps that are ready to execute."""
        completed_set = set(completed or [])
        
        return [
            step for step in self.steps
            if all(dep in completed_set for dep in step.get("depends_on", []))
            and step["name"] not in completed_set
        ]


# ============================================================================
# MIGRATION TASK MODEL
# ============================================================================

@dataclass(frozen=True)
class MigrationTask:
    """
    Immutable migration task representing a single execution unit.
    
    Tasks are the individual units of work within a migration plan that can be
    executed and tracked independently.
    """
    
    # Task identity
    id: str                        # Unique task identifier
    
    # Plan information
    plan_id: str                  # ID of parent migration plan
    plan_step_name: str           # Name of the step this task executes
    
    # Artifact information
    source_artifact: str          # Source artifact identifier
    target_artifact: str          # Target artifact identifier
    
    # Task state
    status: "MigrationStatus"     # Current execution status
    progress: float = 0.0         # Progress as fraction (0.0 to 1.0)
    
    # Execution context
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    error_message: Optional[str] = None
    validation_passed: bool = True
    
    def mark_started(self) -> "MigrationTask":
        """Mark task as started."""
        return MigrationTask(
            id=self.id,
            plan_id=self.plan_id,
            plan_step_name=self.plan_step_name,
            source_artifact=self.source_artifact,
            target_artifact=self.target_artifact,
            status=MigrationStatus.RUNNING,
            progress=0.1
        )
    
    def mark_completed(self) -> "MigrationTask":
        """Mark task as completed."""
        return MigrationTask(
            id=self.id,
            plan_id=self.plan_id,
            plan_step_name=self.plan_step_name,
            source_artifact=self.source_artifact,
            target_artifact=self.target_artifact,
            status=MigrationStatus.COMPLETED,
            progress=1.0,
            completed_at=datetime.now()
        )
    
    def mark_failed(self, error: str) -> "MigrationTask":
        """Mark task as failed."""
        return MigrationTask(
            id=self.id,
            plan_id=self.plan_id,
            plan_step_name=self.plan_step_name,
            source_artifact=self.source_artifact,
            target_artifact=self.target_artifact,
            status=MigrationStatus.FAILED,
            progress=self.progress,
            error_message=error
        )


# ============================================================================
# MIGRATION STATUS ENUMERATION
# ============================================================================

class MigrationStatus(Enum):
    """
    Canonical migration task statuses.
    """
    
    PENDING = "pending"           # Task is queued but not started
    RUNNING = "running"          # Task is currently executing
    COMPLETED = "completed"      # Task completed successfully
    FAILED = "failed"            # Task failed during execution
    ROLLED_BACK = "rolled-back"  # Task was rolled back after failure


# ============================================================================
# MIGRATION EXECUTOR
# ============================================================================

class MigrationExecutor:
    """
    Executor for running migrations.
    
    Manages the execution of migration plans, tracks progress, and handles
    rollback on failures.
    """
    
    def __init__(self):
        self._tasks: Dict[str, MigrationTask] = {}
        self._plans: Dict[str, MigrationPlan] = {}
        self._current_plans: List[str] = []
    
    def register_plan(self, plan: MigrationPlan) -> None:
        """Register a migration plan."""
        self._plans[plan.id] = plan
        if plan.pre_migration_validation:
            self._validate_plan(plan)
    
    def _validate_plan(self, plan: MigrationPlan) -> bool:
        """Validate migration plan before execution."""
        # Check for circular dependencies
        step_names = [s["name"] for s in plan.steps]
        for step in plan.steps:
            for dep in step.get("depends_on", []):
                if dep not in step_names:
                    raise ValueError(f"Step '{step['name']}' depends on unknown step '{dep}'")
        
        return True
    
    def create_task(self, task_id: str, plan_id: str, step_name: str) -> MigrationTask:
        """Create a new migration task."""
        task = MigrationTask(
            id=task_id,
            plan_id=plan_id,
            plan_step_name=step_name,
            source_artifact=self._plans[plan_id].source_artifact,
            target_artifact=self._plans[plan_id].target_artifact,
            status=MigrationStatus.PENDING
        )
        
        self._tasks[task_id] = task
        return task
    
    def execute_task(self, task_id: str) -> MigrationTask:
        """Execute a migration task."""
        task = self._tasks.get(task_id)
        
        if not task:
            raise ValueError(f"Task '{task_id}' not found")
        
        # Mark as running
        task = task.mark_started()
        self._tasks[task_id] = task
        
        # Simulate execution
        task = task.mark_completed()
        self._tasks[task_id] = task
        
        return task
    
    def get_task(self, task_id: str) -> Optional[MigrationTask]:
        """Get a migration task by ID."""
        return self._tasks.get(task_id)
    
    def list_tasks_for_plan(self, plan_id: str) -> List[MigrationTask]:
        """List all tasks for a migration plan."""
        return [
            t for t in self._tasks.values()
            if t.plan_id == plan_id
        ]
    
    def get_completed_tasks(self, plan_id: str) -> List[str]:
        """Get list of completed task names for a plan."""
        tasks = self.list_tasks_for_plan(plan_id)
        return [t.plan_step_name for t in tasks if t.status == MigrationStatus.COMPLETED]
    
    def get_migration_status(self, plan_id: str) -> Dict[str, Any]:
        """Get comprehensive status for a migration plan."""
        plan = self._plans.get(plan_id)
        
        if not plan:
            return {"error": "Plan not found"}
        
        tasks = self.list_tasks_for_plan(plan_id)
        completed = len([t for t in tasks if t.status == MigrationStatus.COMPLETED])
        total = len(tasks)
        
        overall_status = (
            MigrationStatus.COMPLETED if completed == total else
            MigrationStatus.RUNNING if total > 0 else MigrationStatus.PENDING
        )
        
        return {
            "plan_id": plan_id,
            "source_artifact": plan.source_artifact,
            "target_artifact": plan.target_artifact,
            "strategy": plan.strategy.value,
            "duration_days": plan.duration_days,
            "progress": completed / total if total > 0 else 0.0,
            "total_tasks": total,
            "completed_tasks": completed,
            "status": overall_status.value
        }


# ============================================================================
# MIGRATION PLAN BUILDER
# ============================================================================

class MigrationPlanBuilder:
    """
    Builder for constructing migration plans.
    
    Provides a fluent API for creating complex migration plans with multiple
    steps and dependencies.
    """
    
    def __init__(self):
        self._id: str = ""
        self._source_artifact: str = ""
        self._target_artifact: str = ""
        self._strategy: MigrationStrategy = MigrationStrategy.ROLLING
        self._start_at: datetime = None
        self._end_at: datetime = None
        self._steps: List[Dict[str, Any]] = []
    
    def with_id(self, plan_id: str) -> "MigrationPlanBuilder":
        """Set the migration plan ID."""
        self._id = plan_id
        return self
    
    def from_artifact(self, artifact_id: str) -> "MigrationPlanBuilder":
        """Set the source artifact."""
        self._source_artifact = artifact_id
        return self
    
    def to_artifact(self, artifact_id: str) -> "MigrationPlanBuilder":
        """Set the target artifact."""
        self._target_artifact = artifact_id
        return self
    
    def using_strategy(self, strategy: MigrationStrategy) -> "MigrationPlanBuilder":
        """Set the migration strategy."""
        self._strategy = strategy
        return self
    
    def starting_at(self, date: datetime) -> "MigrationPlanBuilder":
        """Set the migration start time."""
        self._start_at = date
        return self
    
    def ending_at(self, date: datetime) -> "MigrationPlanBuilder":
        """Set the migration completion time."""
        self._end_at = date
        return self
    
    def with_step(
        self,
        name: str,
        description: str,
        depends_on: Optional[List[str]] = None,
        rollback_on_failure: bool = True
    ) -> "MigrationPlanBuilder":
        """Add a step to the migration plan."""
        self._steps.append({
            "name": name,
            "description": description,
            "depends_on": depends_on or [],
            "rollback": rollback_on_failure
        })
        return self
    
    def build(self) -> MigrationPlan:
        """Build the migration plan."""
        if not all([
            self._id,
            self._source_artifact,
            self._target_artifact,
            self._start_at,
            self._end_at
        ]):
            raise ValueError("All required fields must be set")
        
        return MigrationPlan(
            id=self._id,
            source_artifact=self._source_artifact,
            target_artifact=self._target_artifact,
            strategy=self._strategy,
            start_at=self._start_at,
            end_at=self._end_at,
            steps=list(self._steps)
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def determine_migration_strategy(source_version: str, target_version: str) -> MigrationStrategy:
    """Determine the most appropriate migration strategy based on version difference."""
    # Parse versions
    source_parts = [int(x) for x in source_version.split(".")]
    target_parts = [int(x) for x in target_version.split(".")]
    
    # Major version change requires blue-green or bridge
    if source_parts[0] != target_parts[0]:
        return MigrationStrategy.BLUE_GREEN
    
    # Minor version change can use rolling
    if source_parts[1] != target_parts[1]:
        return MigrationStrategy.ROLLING
    
    # Patch version change can be direct
    return MigrationStrategy.REVERSE_PROXY


def calculate_migration_progress(plan: MigrationPlan, completed_tasks: List[str]) -> float:
    """Calculate migration progress as a percentage."""
    total_steps = len(plan.steps)
    
    if total_steps == 0:
        return 1.0
    
    completed_count = sum(1 for step in plan.steps if step["name"] in completed_tasks)
    
    return completed_count / total_steps


def get_next_migration_step(
    plan: MigrationPlan,
    completed: List[str]
) -> Optional[Dict[str, Any]]:
    """Get the next migration step that should be executed."""
    ready = plan.get_ready_steps(completed)
    
    if not ready:
        return None
    
    # Return first ready step
    return ready[0]


def check_migration_dependencies(
    plan: MigrationPlan,
    completed: List[str]
) -> Dict[str, bool]:
    """Check dependency satisfaction for all migration steps."""
    result = {}
    
    for step in plan.steps:
        deps = step.get("depends_on", [])
        satisfied = all(dep in completed for dep in deps)
        result[step["name"]] = satisfied
    
    return result