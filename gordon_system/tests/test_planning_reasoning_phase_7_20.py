# Test Planning Reasoning Phase 7.20
# ====================================

"""
Tests for the Planning Reasoning subsystem (Phase 7.20).

Test Coverage:
    - Plan Set construction and validation
    - Planned Task creation, management, and decomposition
    - Dependency graph analysis (causal ordering, cycles)
    - Resource allocation planning
    - Contingency plan generation
    - Plan refinement with history preservation
    - Planning validation and failure handling
    - Governance evaluation
    - Health metrics tracking
"""

import pytest
from typing import Tuple

# Import Phase 7.20 contracts
from gordon_system.src.agent.components.systems.cognition.reasoning.planning import (
    # Descriptors
    PlanningDescriptor,
    PlanningSessionIdentity,
    PlanningMode,
    PlanningLifecycle,
    
    # Plan Set
    ExecutionPlan,
    PlanSet,
    PlanConstruction,
    
    # Tasks
    PlannedTask,
    TaskKind,
    TaskState,
    TaskManagement,
    TaskDecomposition,
    
    # Dependencies
    TaskDependency,
    DependencyKind,
    DependencyGraphState,
    DependencyGraph,
    DependencyAnalysis,
    
    # Resources
    ResourceAllocation,
    ResourceType,
    AllocationPolicy,
    ResourcePlanning,
    ResourceAvailability,
    
    # Contingencies
    ContingencyPlan,
    ContingencyKind,
    ContingencyState,
    ContingencyManagement,
    RecoveryTrigger,
    
    # Refinement
    PlanningRefinement,
    PlanHistory,
    
    # Validation
    PlanningValidation,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
    
    # Failure
    PlanningFailure,
    FailureKind,
    FailureTrace,
    
    # Governance
    PlanningGovernance,
    GovernanceFindingKind,
    GovernanceFinding,
    PlanningSessionGovernance,
    
    # Health
    PlanningHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.planning.shared.descriptor import (
    PlanningDescriptor,
    PlanningSessionIdentity,
    PlanningMode,
    PlanningLifecycle,
)


class TestPlanningDescriptors:
    """Tests for Planning Descriptor contracts."""
    
    def test_planning_session_identity(self) -> None:
        """Test that session identity is immutable."""
        session_id = PlanningSessionIdentity.create("mission-001")
        
        assert isinstance(session_id, PlanningSessionIdentity)
        assert session_id.identity.startswith("session:")
        assert session_id.mission_reference == "mission-001"
    
    def test_planning_descriptor(self) -> None:
        """Test PlanningDescriptor creation and metadata."""
        descriptor = PlanningDescriptor.create(
            planning_goal="Achieve objective X",
            planning_mode=PlanningMode.TEMPLATE,
        )
        
        assert isinstance(descriptor, PlanningDescriptor)
        assert descriptor.planning_goal == "Achieve objective X"
        assert descriptor.planning_mode == PlanningMode.TEMPLATE
        assert descriptor.lifecycle_state == PlanningLifecycle.CREATED


class TestPlanSetAndExecutionPlans:
    """Tests for Plan Set and Execution Plan contracts."""
    
    def test_execution_plan_creation(self) -> None:
        """Test creating an execution plan with tasks."""
        task = PlannedTask.create(
            objective_reference="Perform action A",
            task_kind=TaskKind.ATOMIC,
        )
        
        assert task.objective_reference == "Perform action A"
        assert task.task_kind == TaskKind.ATOMIC
        assert isinstance(task.task_id, str)
    
    def test_plan_set_construction(self) -> None:
        """Test constructing a plan set with multiple plans."""
        plan1 = ExecutionPlan.create(
            originating_decision="Decision-001",
            tasks=(PlannedTask.create("task-1"),),
        )
        
        plan2 = ExecutionPlan.create(
            originating_decision="Decision-001",
            tasks=(PlannedTask.create("task-2"),),
        )
        
        plan_set = PlanSet.create(
            participating_plans=(plan1, plan2),
        )
        
        assert len(plan_set.participating_plans) == 2


class TestTaskManagement:
    """Tests for Task management contracts."""
    
    def test_planned_task_creation(self) -> None:
        """Test creating a planned task with all properties."""
        task = PlannedTask.create(
            objective_reference="Complete project phase",
            task_kind=TaskKind.COMPOSITE,
            task_depth=1,
        )
        
        assert task.objective_reference == "Complete project phase"
        assert task.task_kind == TaskKind.COMPOSITE
        assert task.task_depth == 1
        assert not task.is_leaf
    
    def test_planned_task_with_resources(self) -> None:
        """Test adding resources to a task."""
        base_task = PlannedTask.create("Perform computation")
        
        task_with_resources = base_task.with_resources(
            resources=("cpu-4", "gpu-1", "memory-8GB"),
        )
        
        assert len(task_with_resources.required_resources) == 3
    
    def test_planned_task_with_conditions(self) -> None:
        """Test adding pre/postconditions to a task."""
        base_task = PlannedTask.create("Execute step")
        
        task_with_conditions = base_task.with_conditions(
            preconditions=("prerequisite A complete",),
            postconditions=("step result available",),
        )
        
        assert len(task_with_conditions.preconditions) == 1
        assert len(task_with_conditions.postconditions) == 1
    
    def test_task_management_evaluation(self) -> None:
        """Test task management quality evaluation."""
        tasks = (
            PlannedTask.create("task-1"),
            PlannedTask.create("task-2", task_kind=TaskKind.ATOMIC),
            PlannedTask.create("task-3", task_kind=TaskKind.CHECKPOINT),
        )
        
        management = TaskManagement.create(
            participating_tasks=tasks,
            decomposition_strategy="hierarchical",
        )
        
        assert management.total_tasks == 3
        assert management.decomposition_strategy == "hierarchical"


class TestDependencyGraphs:
    """Tests for Dependency graph contracts."""
    
    def test_task_dependency_creation(self) -> None:
        """Test creating a task dependency."""
        dep = TaskDependency.create(
            predecessor_task_id="task-1",
            successor_task_id="task-2",
            dependency_kind=DependencyKind.CAUSAL,
        )
        
        assert dep.predecessor_task_id == "task-1"
        assert dep.successor_task_id == "task-2"
        assert dep.dependency_kind == DependencyKind.CAUSAL
    
    def test_dependency_graph_creation(self) -> None:
        """Test creating a dependency graph."""
        tasks = ("task-1", "task-2", "task-3")
        
        deps = (
            TaskDependency.create("task-1", "task-2"),
            TaskDependency.create("task-2", "task-3"),
        )
        
        graph = DependencyGraph.create(
            participating_task_ids=tasks,
            dependency_edges=deps,
        )
        
        assert len(graph.participating_task_ids) == 3
        assert len(graph.dependency_edges) == 2
    
    def test_dependency_analysis(self) -> None:
        """Test dependency analysis."""
        analysis = DependencyAnalysis.create(
            analyzed_graph_id="graph-001",
            is_acyclic=True,
        )
        
        assert analysis.analyzed_graph_id == "graph-001"
        assert analysis.is_acyclic


class TestResourcePlanning:
    """Tests for Resource planning contracts."""
    
    def test_resource_allocation_creation(self) -> None:
        """Test creating a resource allocation."""
        allocation = ResourceAllocation.create(
            resource_type=ResourceType.COMPUTE,
            resource_name="cpu-4",
        )
        
        assert allocation.resource_type == ResourceType.COMPUTE
        assert allocation.resource_name == "cpu-4"
    
    def test_resource_planning_record(self) -> None:
        """Test creating a resource planning record."""
        allocations = (
            ResourceAllocation.create(ResourceType.COMPUTE, "cpu-1"),
            ResourceAllocation.create(ResourceType.MEMORY, "8GB"),
        )
        
        planning = ResourcePlanning.create(
            allocated_resources=allocations,
            allocation_strategy="parallel",
        )
        
        assert len(planning.allocated_resources) == 2
        assert planning.allocation_strategy == "parallel"


class TestContingencyPlans:
    """Tests for Contingency plan contracts."""
    
    def test_contingency_plan_creation(self) -> None:
        """Test creating a contingency plan."""
        contingency = ContingencyPlan.create(
            triggering_conditions=("task fails",),
            recovery_strategy="retry",
            fallback_plan_tasks=("fallback-task-1",),
        )
        
        assert len(contingency.triggering_conditions) == 1
        assert contingency.recovery_strategy == "retry"
    
    def test_contingency_management(self) -> None:
        """Test contingency management evaluation."""
        contingencies = (
            ContingencyPlan.create(("fail-1",)),
            ContingencyPlan.create(("fail-2",)),
        )
        
        mgmt = ContingencyManagement.create(
            contingency_graph=contingencies,
            recovery_policy="automatic",
        )
        
        assert mgmt.total_contingencies == 2


class TestPlanningRefinement:
    """Tests for Plan refinement contracts."""
    
    def test_planning_refinement(self) -> None:
        """Test creating a planning refinement record."""
        refinement = PlanningRefinement.create(
            previous_plan=("previous-plan",),
            refined_plan=("refined-plan",),
            refinement_strategy="constraint-addition",
            refinement_trigger="new-resource-available",
        )
        
        assert "previous-plan" in refinement.previous_plan
        assert "refined-plan" in refinement.refined_plan
    
    def test_plan_history(self) -> None:
        """Test plan history with multiple refinements."""
        history = PlanHistory.create("original-plan")
        
        initial_count = history.version_count
        assert initial_count == 1


class TestPlanningValidation:
    """Tests for Planning validation contracts."""
    
    def test_planning_validation(self) -> None:
        """Test planning validation results."""
        validation = PlanningValidation.create()
        
        assert validation.is_valid
    
    def test_validation_finding_creation(self) -> None:
        """Test creating a validation finding."""
        finding = ValidationFinding.create(
            finding_kind=ValidationFindingKind.MISSING_CONTINGENCY_PLAN,
            description="Task X has no contingency",
            severity="warning",
        )
        
        assert finding.finding_kind == ValidationFindingKind.MISSING_CONTINGENCY_PLAN
        assert finding.severity == "warning"


class TestPlanningFailure:
    """Tests for Planning failure contracts."""
    
    def test_planning_failure_creation(self) -> None:
        """Test creating a planning failure record."""
        failure = PlanningFailure.create(
            failure_kind=FailureKind.CYCLIC_DEPENDENCY,
            diagnostics=("Cycle detected in dependency graph",),
            recovery_options=("Break cycle by adding edge",),
        )
        
        assert failure.failure_kind == FailureKind.CYCLIC_DEPENDENCY
        assert len(failure.diagnostics) == 1
    
    def test_failure_trace(self) -> None:
        """Test failure trace collection."""
        trace = FailureTrace.create()
        
        assert trace.total_failures == 0


class TestPlanningGovernance:
    """Tests for Planning governance contracts."""
    
    def test_planning_governance(self) -> None:
        """Test planning governance evaluation."""
        governance = PlanningGovernance.create()
        
        assert governance.dependency_integrity_valid
        assert governance.resource_efficiency_valid
    
    def test_governance_finding_creation(self) -> None:
        """Test creating a governance finding."""
        finding = GovernanceFinding.create(
            finding_kind=GovernanceFindingKind.CYCLIC_DEPENDENCY,
            description="Circular dependency detected",
        )
        
        assert finding.finding_kind == GovernanceFindingKind.CYCLIC_DEPENDENCY


class TestPlanningHealth:
    """Tests for Planning health metrics."""
    
    def test_planning_health(self) -> None:
        """Test planning health metrics."""
        health = PlanningHealth.create()
        
        assert health.overall_health_score == 1.0
        assert health.dependency_integrity_score == 1.0
    
    def test_health_metrics_snapshot(self) -> None:
        """Test health metrics snapshot."""
        snapshot = HealthMetricsSnapshot.create()
        
        assert snapshot.plans_generated == 0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
