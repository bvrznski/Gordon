# =============================================================================
# GORDON COGNITIVE ARCHITECTURE
# TEST SUITE FOR EXECUTION REASONING - PHASE 7.21
# =============================================================================

"""
Test suite for Phase 7.21 Execution Reasoning implementation.

This module tests the canonical execution contracts, sequencing,
coordination, authorization, rollback, validation, and governance.
"""

import time
import pytest
from typing import Tuple

# Import execution reasoning modules
from gordon_system.src.agent.components.systems.cognition.reasoning.execution import (
    # Shared
    ExecutionDescriptor,
    ExecutionSessionIdentity,
    ExecutionCommand,
    ExecutionSet,
    # Orchestration
    ExecutionOrchestration,
    OrchestrationStrategy,
    ExecutionGraphState,
    ExecutionCommandGroup,
    OrchestrationTrace,
    OrchestrationStep,
    # Authorization
    ExecutionAuthorization,
    AuthorizationPolicy,
    AuthorizationState,
    AuthorizationTrace,
    AuthorizationStep,
    # Synchronization
    SynchronizationPoint,
    SynchronizationPolicy,
    SynchronizationState,
    OrderingConstraints,
    SynchronizationGraph,
    # Adaptation
    ExecutionAdaptationPipeline,
    AdaptationTrigger,
    AdaptationStrategy,
    AdaptedExecutionState,
    # Rollback
    RollbackManagement,
    RollbackScope,
    RecoveryCheckpoint,
    RollbackPlan,
    # Validation
    ExecutionValidation,
    ValidationFindingKind,
    ValidationFinding,
    ValidationTrace,
    ValidationStep,
    # Failure
    ExecutionFailure,
    FailureKind,
    FailureTrace,
    # Governance
    ExecutionGovernance,
    GovernanceFindingKind,
    GovernanceFinding,
    ExecutionSessionGovernance,
    # Health
    ExecutionHealth,
    HealthMetricsSnapshot,
    HealthAlert,
)


class TestExecutionDescriptor:
    """Test execution descriptor functionality."""
    
    def test_descriptor_creation(self):
        """Test basic descriptor creation."""
        descriptor = ExecutionDescriptor.create(
            semantic_identity="test-session-001",
            execution_goal="Test execution goal",
        )
        
        assert descriptor.descriptor_id is not None
        assert descriptor.semantic_identity == "test-session-001"
        assert descriptor.execution_goal == "Test execution goal"
        assert descriptor.lifecycle_state == ExecutionDescriptor.ExecutionLifecycle.CREATED
    
    def test_descriptor_to_state(self):
        """Test state transitions."""
        descriptor = ExecutionDescriptor.create(
            semantic_identity="test-session-002",
            execution_goal="Test goal",
        )
        
        completed = descriptor.to_state(ExecutionDescriptor.ExecutionLifecycle.COMPLETED)
        
        assert completed.lifecycle_state == ExecutionDescriptor.ExecutionLifecycle.COMPLETED
        assert descriptor.lifecycle_state == ExecutionDescriptor.ExecutionLifecycle.CREATED  # Original unchanged


class TestExecutionCommand:
    """Test execution command functionality."""
    
    def test_command_creation(self):
        """Test basic command creation."""
        command = ExecutionCommand.create(
            originating_plan_id="plan-001",
            command_type="action",
            command_payload={"action": "test"},
        )
        
        assert command.command_identity is not None
        assert command.originating_plan_id == "plan-001"
        assert command.command_type == "action"
    
    def test_command_with_constraints(self):
        """Test command with constraints."""
        command = ExecutionCommand.create(
            originating_plan_id="plan-002",
            command_type="resource_acquisition",
            resource_constraints=("mutex:shared_resource",),
        )
        
        assert len(command.resource_constraints) == 1
        assert "mutex:shared_resource" in command.resource_constraints


class TestExecutionSet:
    """Test execution set functionality."""
    
    def test_set_creation(self):
        """Test basic execution set creation."""
        commands = tuple([
            ExecutionCommand.create("plan-001", "action", {"data": i})
            for i in range(3)
        ])
        
        execution_set = ExecutionSet.create(
            execution_commands=commands,
            execution_constraints=("sequential_execution",),
        )
        
        assert len(execution_set.execution_commands) == 3
        assert len(execution_set.execution_constraints) >= 1


class TestExecutionOrchestration:
    """Test execution orchestration functionality."""
    
    def test_orchestration_creation(self):
        """Test basic orchestration creation."""
        command = ExecutionCommand.create("plan-001", "action", {"data": "test"})
        group = ExecutionCommandGroup.create((command,))
        
        orchestration = ExecutionOrchestration.create(
            orchestration_strategy=OrchestrationStrategy.SEQUENTIAL,
            execution_graph=(group,),
        )
        
        assert orchestration.orchestration_identity is not None
        assert orchestration.orchestration_strategy == OrchestrationStrategy.SEQUENTIAL
        assert len(orchestration.execution_graph) == 1
    
    def test_orchestration_duration(self):
        """Test duration calculation."""
        start_time = time.time()
        
        command = ExecutionCommand.create("plan-002", "action", {"data": "test"})
        group = ExecutionCommandGroup.create((command,))
        
        orchestration = ExecutionOrchestration.create(
            orchestration_strategy=OrchestrationStrategy.SEQUENTIAL,
            execution_graph=(group,),
        )
        
        # Duration should be calculated if started_at_utc is set
        assert orchestration.duration_seconds >= 0


class TestAuthorization:
    """Test authorization functionality."""
    
    def test_authorization_creation(self):
        """Test basic authorization creation."""
        command = ExecutionCommand.create("plan-001", "action", {"data": "test"})
        
        auth = ExecutionAuthorization.create(
            authorized_commands=(command,),
            authorization_policy=AuthorizationPolicy.STRICT,
        )
        
        assert auth.authorization_identity is not None
        assert len(auth.authorized_commands) == 1
        assert auth.authorization_state == AuthorizationState.PENDING


class TestSynchronization:
    """Test synchronization functionality."""
    
    def test_sync_point_creation(self):
        """Test basic sync point creation."""
        sync = SynchronizationPoint.create(
            waiting_command_ids=("cmd-001", "cmd-002"),
            synchronization_policy=SynchronizationPolicy.STRICT_ORDERING,
        )
        
        assert sync.synchronization_identity is not None
        assert len(sync.waiting_command_ids) == 2
        assert sync.synchronization_state == SynchronizationState.PENDING


class TestAdaptation:
    """Test adaptation functionality."""
    
    def test_adaptation_pipeline_creation(self):
        """Test basic adaptation pipeline creation."""
        pipeline = ExecutionAdaptationPipeline.create(
            triggering_conditions=("resource_failure", "partial_completion"),
            adaptation_strategy=AdaptationStrategy.RERUN_FAILED,
        )
        
        assert pipeline.adaptation_identity is not None
        assert len(pipeline.triggering_conditions) == 2
        assert pipeline.adaptation_strategy == AdaptationStrategy.RERUN_FAILED


class TestRollback:
    """Test rollback functionality."""
    
    def test_rollback_plan_creation(self):
        """Test basic rollback plan creation."""
        plan = RollbackPlan.create(
            checkpoint_reference="checkpoint-001",
            rollback_scope=RollbackScope.GROUP_LEVEL,
        )
        
        assert plan.rollback_identity is not None
        assert plan.checkpoint_reference == "checkpoint-001"
        assert plan.rollback_scope == RollbackScope.GROUP_LEVEL
    
    def test_recovery_checkpoint_creation(self):
        """Test recovery checkpoint creation."""
        checkpoint = RecoveryCheckpoint.create(
            command_states={"cmd-001": "completed", "cmd-002": "pending"},
        )
        
        assert checkpoint.checkpoint_identity is not None
        assert len(checkpoint.command_states) == 2


class TestValidation:
    """Test validation functionality."""
    
    def test_validation_creation(self):
        """Test basic validation creation."""
        finding = ValidationFinding.create(
            finding_kind=ValidationFindingKind.AUTHORIZATION_INTEGRITY,
            description="Test finding",
        )
        
        validation = ExecutionValidation.create(
            evaluated_sessions=("session-001",),
            findings=(finding,),
        )
        
        assert validation.validation_identity is not None
        assert validation.total_findings == 1


class TestFailure:
    """Test failure functionality."""
    
    def test_failure_creation(self):
        """Test basic failure creation."""
        failure = ExecutionFailure.create(
            failure_kind=FailureKind.DEADLOCK,
            diagnostics=("circular_wait",),
            recovery_options=("abort_transaction", "timeout"),
        )
        
        assert failure.failure_identity is not None
        assert failure.failure_kind == FailureKind.DEADLOCK
        assert len(failure.diagnostics) == 1


class TestGovernance:
    """Test governance functionality."""
    
    def test_governance_creation(self):
        """Test basic governance creation."""
        finding = GovernanceFinding.create(
            finding_kind=GovernanceFindingKind.AUTHORIZATION_INTEGRITY,
            description="Test finding",
        )
        
        governance = ExecutionGovernance.create(
            evaluated_sessions=("session-001",),
            findings=(finding,),
        )
        
        assert governance.governance_identity is not None
        assert governance.total_findings == 1


class TestHealth:
    """Test health functionality."""
    
    def test_health_creation(self):
        """Test basic health creation."""
        health = ExecutionHealth.create()
        
        assert health.health_identity is not None
        assert health.commands_orchestrated == 0
    
    def test_health_record_command(self):
        """Test command recording in health."""
        health = ExecutionHealth.create()
        updated = health.record_command(is_parallel=True)
        
        assert updated.commands_orchestrated == 1
        assert updated.parallel_commands == 1


class TestExecutionReasoningLaws:
    """Test compliance with execution reasoning laws."""
    
    def test_law_001_unique_identity(self):
        """EXECUTION-LAW-001: Every Execution Session has one immutable Semantic Identity."""
        command = ExecutionCommand.create("plan-001", "action", {})
        
        # Command should have unique identity
        assert len(command.command_identity) > 0
        
        # Create two commands - they should have different identities
        command2 = ExecutionCommand.create("plan-001", "action", {})
        assert command.command_identity != command2.command_identity
    
    def test_law_004_provenance_preserved(self):
        """EXECUTION-LAW-004: Execution Reasoning shall preserve provenance."""
        command = ExecutionCommand.create(
            originating_plan_id="plan-001",
            command_type="test",
            origin_context="test-context",
        )
        
        assert command.origin_context == "test-context"
    
    def test_law_006_independently_inspectable(self):
        """EXECUTION-LAW-006: Execution Reasoning shall remain independently inspectable."""
        command = ExecutionCommand.create("plan-001", "action", {})
        
        # Should be able to inspect all attributes
        assert hasattr(command, 'command_identity')
        assert hasattr(command, 'originating_plan_id')
        assert hasattr(command, 'command_type')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])