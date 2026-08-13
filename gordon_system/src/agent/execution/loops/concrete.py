# Concrete Execution Loop Implementations
# ======================================
#
# PHASE 3.10.9 - First production-quality execution taxonomy implementation.
#
# This module implements the canonical loop policies for each thread type:
#     - ConversationLoop: Maintains productive semantic conversation
#     - TaskLoop: Progresses one semantic objective from definition to completion
#     - PlanningLoop: Produces or refines executable semantic plans
#     - MonitoringLoop: Observes semantic state over time
#     - RecoveryLoop: Performs semantic recovery after failure
#     - IdleLoop: Governs internal semantic behavior during idle periods

"""
Concrete Execution Loop Implementations for Gordon.

Each loop implements the behavioral policy for its associated Thread type.
Loops own continuation policy and cycle selection but do NOT:
    - Execute reasoning or planning algorithms (Capabilities do this)
    - Own Thread continuity (Threads own this)
    - Mutate Thread state directly (Thread accepts deltas)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import uuid

# Import base loop types
from . import (
    ExecutionLoop,
    LoopPolicy,
    LoopContext,
    CycleOutcome,
    LoopState,
    BehavioralMode as LoopBehavioralMode,
    DecisionType,
    ExecutionLoopDecision,
    ContinueDecision,
    CompleteDecision,
    SuspendDecision,
    TerminateDecision,
    dataclass_replace,
)

# Import concrete thread types for type annotations
from ..threads.concrete import (
    ConversationThread,
    TaskThread,
    MonitoringThread,
    InternalThread,
)


# =============================================================================
# ConversationLoop Implementation
# =============================================================================

class ConversationBehavior(Enum):
    """
    Behavioral modes specific to ConversationLoop.
    
    These define how the loop responds to conversational inputs:
        - INTERPRETING: Processing incoming input and building understanding
        - RESPONDING: Generating a response to the participant
        - CLARIFYING: Requesting missing or ambiguous information
        - WAITING: Waiting for external participant input
        - DELEGATING: Delegating work to child TaskThread
        - COMPLETING: Finalizing conversation and transitioning to completed state
    """
    INTERPRETING = "interpreting"
    RESPONDING = "responding"
    CLARIFYING = "clarifying"
    WAITING = "waiting"
    DELEGATING = "delegating"
    COMPLETING = "completing"


@dataclass(frozen=True)
class ConversationPolicyState:
    """
    Policy-local state for ConversationLoop.
    
    This tracks conversation-specific state not owned by the Thread:
        - Current behavioral mode
        - Last interpretation result
        - Clarification requests pending
        - Completion confidence
    """
    current_mode: LoopBehavioralMode = LoopBehavioralMode.ACTIVE
    last_interpretation_result: Optional[str] = None
    clarification_pending: bool = False
    completion_confidence: float = 0.0
    iteration_count: int = 0


class ConversationPolicy(LoopPolicy):
    """
    Behavioral policy for ConversationThread.
    
    This policy maintains productive semantic conversation until:
        - The conversation objective is completed
        - The conversation is suspended for external input
        - Work is delegated to child TaskThreads
    """
    
    def __init__(self, state: Optional[ConversationPolicyState] = None):
        self._policy_id = "conversation-1.0"
        self._state = state or ConversationPolicyState()
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopBehavioralMode:
        # Map from conversation-specific mode to general behavioral mode
        mode_map = {
            ConversationBehavior.INTERPRETING: LoopBehavioralMode.ACTIVE,
            ConversationBehavior.RESPONDING: LoopBehavioralMode.ACTIVE,
            ConversationBehavior.CLARIFYING: LoopBehavioralMode.AWAITING_INPUT,
            ConversationBehavior.WAITING: LoopBehavioralMode.AWAITING_INPUT,
            ConversationBehavior.DELEGATING: LoopBehavioralMode.ACTIVE,
            ConversationBehavior.COMPLETING: LoopBehavioralMode.ACTIVE,
        }
        return mode_map.get(self._state.current_mode, LoopBehavioralMode.ACTIVE)
    
    def decide(self, context: LoopContext) -> ExecutionLoopDecision:
        """
        Evaluate current state and produce a decision for ConversationThread.
        
        Logic:
            1. If there's pending clarification → AWAIT_INPUT
            2. If no cycle outcome (first iteration) → INTERPRETING
            3. Based on previous outcome, decide next action
            4. Default: continue with appropriate cycle
        """
        self._state = dataclass_replace(
            self._state,
            iteration_count=self._state.iteration_count + 1
        )
        
        # Check for pending clarifications
        if context.pending_interruptions:
            return SuspendDecision(
                decision_type=DecisionType.SUSPEND,
                thread_revision=context.thread_revision,
                rationale=f"Pending interruptions: {', '.join(context.pending_interruptions)}",
                is_valid=True
            )
        
        # First iteration - start with interpretation
        if not context.previous_cycle_outcome:
            self._state = dataclass_replace(self._state, current_mode=ConversationBehavior.INTERPRETING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="InterpretationCycle",
                rationale="Starting conversation with input interpretation",
                is_valid=True
            )
        
        # Process previous outcome
        outcome = context.previous_cycle_outcome
        
        if outcome.status == "completed":
            return self._handle_completed(outcome, context)
        elif outcome.status == "failed":
            return TerminateDecision(
                decision_type=DecisionType.TERMINATE,
                thread_revision=context.thread_revision,
                termination_reason=f"Conversation cycle failed: {outcome.failure_reason or 'unknown'}",
                is_valid=True
            )
        
        # Default continuation
        self._state = dataclass_replace(self._state, current_mode=ConversationBehavior.INTERPRETING)
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="InterpretationCycle",
            rationale="Continuing conversation processing",
            is_valid=True
        )
    
    def _handle_completed(self, outcome: CycleOutcome, context: LoopContext) -> ExecutionLoopDecision:
        """Handle a completed cycle outcome."""
        
        # Update completion confidence based on semantic delta
        if outcome.semantic_delta:
            self._state = dataclass_replace(
                self._state,
                completion_confidence=min(1.0, self._state.completion_confidence + 0.2)
            )
        
        # Check for child task delegation
        if isinstance(outcome.semantic_delta, dict) and 'delegated_task' in outcome.semantic_delta:
            self._state = dataclass_replace(self._state, current_mode=ConversationBehavior.DELEGATING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="DelegationCycle",
                rationale="Child task needs to be executed",
                is_valid=True
            )
        
        # Check for clarification requests
        if outcome.new_facts and any('clarify' in f.lower() for f in outcome.new_facts):
            self._state = dataclass_replace(self._state, current_mode=ConversationBehavior.CLARIFYING)
            return SuspendDecision(
                decision_type=DecisionType.SUSPEND,
                thread_revision=context.thread_revision,
                rationale="Waiting for participant clarification",
                resumption_trigger="participant provides clarification",
                is_valid=True
            )
        
        # Check if conversation is complete
        if self._state.completion_confidence >= 0.9:
            self._state = dataclass_replace(self._state, current_mode=ConversationBehavior.COMPLETING)
            return CompleteDecision(
                decision_type=DecisionType.COMPLETE,
                thread_revision=context.thread_revision,
                completion_reason="Conversation objective completed with high confidence",
                semantic_summary=outcome.semantic_result or "conversation completed",
                is_valid=True
            )
        
        # Continue processing
        self._state = dataclass_replace(self._state, current_mode=ConversationBehavior.RESPONDING)
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="ResponseCycle",
            rationale="Processing conversation and preparing response",
            is_valid=True
        )
    
    def transition_mode(self, target_mode: LoopBehavioralMode) -> "ConversationPolicy":
        """Return new policy with specified mode."""
        # Map general behavioral modes to conversation-specific modes
        mode_map = {
            LoopBehavioralMode.ACTIVE: ConversationBehavior.INTERPRETING,
            LoopBehavioralMode.AWAITING_INPUT: ConversationBehavior.WAITING,
        }
        
        conv_mode = mode_map.get(target_mode, ConversationBehavior.INTERPRETING)
        new_state = dataclass_replace(self._state, current_mode=conv_mode)
        return ConversationPolicy(state=new_state)
    
    def get_state(self) -> LoopState:
        """Get policy-local state."""
        return LoopState(
            current_mode=self.current_mode,
            iteration_count=self._state.iteration_count,
            completion_confidence=self._state.completion_confidence
        )
    
    def update_state(self, state: LoopState) -> None:
        """Update policy state from external source."""
        self._state = dataclass_replace(
            self._state,
            current_mode=ConversationBehavior.INTERPRETING  # Default for conversation
        )


def create_conversation_policy() -> ConversationPolicy:
    """Create a new ConversationLoop policy."""
    return ConversationPolicy()


# =============================================================================
# TaskLoop Implementation
# =============================================================================

class TaskBehavior(Enum):
    """
    Behavioral modes specific to TaskLoop.
    
    These define how the loop progresses task objectives:
        - PLANNING: Creating or refining task plan
        - EXECUTING: Executing steps from accepted plan
        - EVALUATING: Assessing execution results against criteria
        - RECOVERING: Recovering from failed execution
        - REPORTING: Producing final output
    """
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    RECOVERING = "recovering"
    REPORTING = "reporting"


@dataclass(frozen=True)
class TaskPolicyState:
    """Policy-local state for TaskLoop."""
    current_mode: LoopBehavioralMode = LoopBehavioralMode.ACTIVE
    task_status: str = TaskBehavior.PLANNING.value
    plan_confidence: float = 0.0
    completion_confidence: float = 0.0
    consecutive_failures: int = 0
    iteration_count: int = 0


class TaskPolicy(LoopPolicy):
    """
    Behavioral policy for TaskThread.
    
    This policy progresses one semantic objective from definition to completion.
    """
    
    def __init__(self, state: Optional[TaskPolicyState] = None):
        self._policy_id = "task-1.0"
        self._state = state or TaskPolicyState()
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopBehavioralMode:
        mode_map = {
            TaskBehavior.PLANNING: LoopBehavioralMode.ACTIVE,
            TaskBehavior.EXECUTING: LoopBehavioralMode.ACTIVE,
            TaskBehavior.EVALUATING: LoopBehavioralMode.ACTIVE,
            TaskBehavior.RECOVERING: LoopBehavioralMode.RECOVERY,
            TaskBehavior.REPORTING: LoopBehavioralMode.ACTIVE,
        }
        return mode_map.get(self._state.current_mode, LoopBehavioralMode.ACTIVE)
    
    def decide(self, context: LoopContext) -> ExecutionLoopDecision:
        """Evaluate current state and produce a decision for TaskThread."""
        
        self._state = dataclass_replace(
            self._state,
            iteration_count=self._state.iteration_count + 1
        )
        
        # Check for pending interruptions
        if context.pending_interruptions:
            return SuspendDecision(
                decision_type=DecisionType.SUSPEND,
                thread_revision=context.thread_revision,
                rationale=f"Task interrupted: {', '.join(context.pending_interruptions)}",
                is_valid=True
            )
        
        # First iteration - determine initial behavior
        if not context.previous_cycle_outcome:
            return self._initial_decision(context)
        
        # Process previous outcome
        outcome = context.previous_cycle_outcome
        
        if outcome.status == "failed":
            return self._handle_failure(outcome, context)
        elif outcome.status == "completed":
            return self._handle_completed(outcome, context)
        
        # Default: continue with same cycle type
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="ExecutionCycle",
            rationale="Continuing task execution",
            is_valid=True
        )
    
    def _initial_decision(self, context: LoopContext) -> ExecutionLoopDecision:
        """Make initial decision for a new TaskThread."""
        
        # If Thread has accepted plan, go to EXECUTING; otherwise PLANNING
        if context.active_objectives:
            self._state = dataclass_replace(self._state, current_mode=TaskBehavior.EXECUTING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="ExecutionCycle",
                rationale="Starting task execution with accepted plan",
                is_valid=True
            )
        else:
            self._state = dataclass_replace(self._state, current_mode=TaskBehavior.PLANNING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="PlanningCycle",
                rationale="Creating task plan before execution",
                is_valid=True
            )
    
    def _handle_failure(self, outcome: CycleOutcome, context: LoopContext) -> ExecutionLoopDecision:
        """Handle a failed cycle outcome."""
        
        self._state = dataclass_replace(
            self._state,
            consecutive_failures=self._state.consecutive_failures + 1
        )
        
        # After multiple failures, request recovery
        if self._state.consecutive_failures >= 3:
            self._state = dataclass_replace(self._state, current_mode=TaskBehavior.RECOVERING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="RecoveryCycle",
                rationale="Requesting semantic recovery after repeated failures",
                is_valid=True
            )
        
        # Otherwise, try same cycle again
        self._state = dataclass_replace(self._state, current_mode=TaskBehavior.EXECUTING)
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="ExecutionCycle",
            rationale=f"Retrying after failure: {outcome.failure_reason or 'unknown'}",
            is_valid=True
        )
    
    def _handle_completed(self, outcome: CycleOutcome, context: LoopContext) -> ExecutionLoopDecision:
        """Handle a completed cycle outcome."""
        
        # Update completion confidence based on semantic delta
        if outcome.semantic_delta and isinstance(outcome.semantic_result, dict):
            result = outcome.semantic_result
            if 'confidence' in result:
                self._state = dataclass_replace(
                    self._state,
                    completion_confidence=min(1.0, result['confidence'])
                )
        
        # Check for reporting need
        if self._state.completion_confidence >= 0.95:
            self._state = dataclass_replace(self._state, current_mode=TaskBehavior.REPORTING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="ReportingCycle",
                rationale="Generating final task report",
                is_valid=True
            )
        
        # Check for completion criteria met in semantic delta
        if outcome.semantic_delta and isinstance(outcome.semantic_delta, dict):
            delta = outcome.semantic_delta
            if delta.get('completion_criteria_met'):
                self._state = dataclass_replace(self._state, current_mode=TaskBehavior.REPORTING)
                return CompleteDecision(
                    decision_type=DecisionType.COMPLETE,
                    thread_revision=context.thread_revision,
                    completion_reason="Task objective completed successfully",
                    semantic_summary=outcome.semantic_result or "task completed",
                    is_valid=True
                )
        
        # Continue with next cycle type based on current mode
        if self._state.current_mode == TaskBehavior.EXECUTING:
            self._state = dataclass_replace(self._state, current_mode=TaskBehavior.EVALUATING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="EvaluationCycle",
                rationale="Evaluating execution result against criteria",
                is_valid=True
            )
        
        # Default: continue execution
        self._state = dataclass_replace(self._state, current_mode=TaskBehavior.EXECUTING)
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="ExecutionCycle",
            rationale="Continuing task execution",
            is_valid=True
        )
    
    def transition_mode(self, target_mode: LoopBehavioralMode) -> "TaskPolicy":
        """Return new policy with specified mode."""
        mode_map = {
            LoopBehavioralMode.ACTIVE: TaskBehavior.EXECUTING,
            LoopBehavioralMode.RECOVERY: TaskBehavior.RECOVERING,
        }
        
        task_mode = mode_map.get(target_mode, TaskBehavior.EXECUTING)
        new_state = dataclass_replace(self._state, current_mode=task_mode)
        return TaskPolicy(state=new_state)
    
    def get_state(self) -> LoopState:
        """Get policy-local state."""
        return LoopState(
            current_mode=self.current_mode,
            iteration_count=self._state.iteration_count,
            completion_confidence=self._state.completion_confidence
        )
    
    def update_state(self, state: LoopState) -> None:
        """Update policy state from external source."""
        self._state = dataclass_replace(
            self._state,
            current_mode=TaskBehavior.EXECUTING  # Default for task
        )


def create_task_policy() -> TaskPolicy:
    """Create a new TaskLoop policy."""
    return TaskPolicy()


# =============================================================================
# PlanningLoop Implementation
# =============================================================================

@dataclass(frozen=True)
class PlanningPolicyState:
    """Policy-local state for PlanningLoop."""
    current_mode: LoopBehavioralMode = LoopBehavioralMode.ACTIVE
    planning_iterations: int = 0
    plan_quality_score: float = 0.0
    alternatives_generated: List[str] = field(default_factory=list)
    best_alternative_id: Optional[str] = None


class PlanningPolicy(LoopPolicy):
    """
    Behavioral policy for producing or refining executable semantic plans.
    
    This policy is used temporarily when TaskThread needs planning work done.
    """
    
    def __init__(self, state: Optional[PlanningPolicyState] = None):
        self._policy_id = "planning-1.0"
        self._state = state or PlanningPolicyState()
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopBehavioralMode:
        return LoopBehavioralMode.DELIBERATIVE  # Planning requires careful reasoning
    
    def decide(self, context: LoopContext) -> ExecutionLoopDecision:
        """Evaluate current state and produce a planning decision."""
        
        self._state = dataclass_replace(
            self._state,
            planning_iterations=self._state.planning_iterations + 1
        )
        
        # Check for pending interruptions
        if context.pending_interruptions:
            return SuspendDecision(
                decision_type=DecisionType.SUSPEND,
                thread_revision=context.thread_revision,
                rationale=f"Planning interrupted: {', '.join(context.pending_interruptions)}",
                is_valid=True
            )
        
        # First iteration - start planning
        if not context.previous_cycle_outcome:
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="PlanningCycle",
                rationale="Starting plan production",
                is_valid=True
            )
        
        outcome = context.previous_cycle_outcome
        
        if outcome.status == "completed":
            # Update plan quality score from semantic delta
            if outcome.semantic_delta and isinstance(outcome.semantic_delta, dict):
                result = outcome.semantic_delta.get('plan_result', {})
                quality = result.get('quality_score', 0.5)
                self._state = dataclass_replace(
                    self._state,
                    plan_quality_score=quality
                )
            
            # Check if we have a good enough plan
            if self._state.plan_quality_score >= 0.8:
                return ContinueDecision(
                    decision_type=DecisionType.CONTINUE,
                    thread_revision=context.thread_revision,
                    cycle_definition="PlanCommitmentCycle",
                    rationale=f"Accepting plan with quality score {self._state.plan_quality_score}",
                    is_valid=True
                )
            
            # Refine the plan
            self._state = dataclass_replace(
                self._state,
                alternatives_generated=self._state.alternatives_generated + [f"alt-{self._state.planning_iterations}"]
            )
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="PlanningCycle",
                rationale=f"Refining plan (quality: {self._state.plan_quality_score})",
                is_valid=True
            )
        
        # Handle failure - request more planning
        self._state = dataclass_replace(
            self._state,
            alternatives_generated=self._state.alternatives_generated + ["retry"]
        )
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="PlanningCycle",
            rationale=f"Retrying planning after failure: {outcome.failure_reason or 'unknown'}",
            is_valid=True
        )
    
    def transition_mode(self, target_mode: LoopBehavioralMode) -> "PlanningPolicy":
        """Return new policy with specified mode."""
        # Planning always uses DELIBERATIVE mode
        return PlanningPolicy(state=self._state)
    
    def get_state(self) -> LoopState:
        """Get policy-local state."""
        return LoopState(
            current_mode=self.current_mode,
            iteration_count=self._state.planning_iterations,
            completion_confidence=self._state.plan_quality_score
        )
    
    def update_state(self, state: LoopState) -> None:
        """Update policy state from external source."""
        self._state = dataclass_replace(self._state)


def create_planning_policy() -> PlanningPolicy:
    """Create a new PlanningLoop policy."""
    return PlanningPolicy()


# =============================================================================
# MonitoringLoop Implementation
# =============================================================================

@dataclass(frozen=True)
class MonitoringPolicyState:
    """Policy-local state for MonitoringLoop."""
    current_mode: LoopBehavioralMode = LoopBehavioralMode.MONITORING
    observation_count: int = 0
    escalation_level: int = 0
    last_baseline_update_at: float = 0.0


class MonitoringPolicy(LoopPolicy):
    """
    Behavioral policy for MonitoringThread.
    
    This policy observes semantic state over time and determines when action is needed.
    """
    
    def __init__(self, state: Optional[MonitoringPolicyState] = None):
        self._policy_id = "monitoring-1.0"
        self._state = state or MonitoringPolicyState()
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopBehavioralMode:
        if self._state.escalation_level > 0:
            return LoopBehavioralMode.REACTIVE
        return LoopBehavioralMode.MONITORING
    
    def decide(self, context: LoopContext) -> ExecutionLoopDecision:
        """Evaluate current state and produce a monitoring decision."""
        
        self._state = dataclass_replace(
            self._state,
            observation_count=self._state.observation_count + 1
        )
        
        # Check for pending interruptions (e.g., system shutdown)
        if context.pending_interruptions:
            return CompleteDecision(
                decision_type=DecisionType.COMPLETE,
                thread_revision=context.thread_revision,
                completion_reason="Monitoring thread interrupted",
                is_valid=True
            )
        
        # First iteration - start monitoring
        if not context.previous_cycle_outcome:
            self._state = dataclass_replace(self._state, current_mode=LoopBehavioralMode.MONITORING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="ObservationCycle",
                rationale="Starting observation cycle",
                is_valid=True
            )
        
        outcome = context.previous_cycle_outcome
        
        if outcome.status == "completed":
            # Process the observation result
            if outcome.semantic_delta and isinstance(outcome.semantic_delta, dict):
                delta = outcome.semantic_delta
                
                # Check for escalation triggers
                if delta.get('escalation_required'):
                    self._state = dataclass_replace(
                        self._state,
                        escalation_level=self._state.escalation_level + 1
                    )
                    return ContinueDecision(
                        decision_type=DecisionType.CONTINUE,
                        thread_revision=context.thread_revision,
                        cycle_definition="EscalationCycle",
                        rationale=f"Escalating (level {self._state.escalation_level})",
                        is_valid=True
                    )
            
            # Continue monitoring
            self._state = dataclass_replace(self._state, current_mode=LoopBehavioralMode.MONITORING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="ObservationCycle",
                rationale="Continuing observation",
                is_valid=True
            )
        
        # Handle failure - retry observation
        self._state = dataclass_replace(self._state, current_mode=LoopBehavioralMode.MONITORING)
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="ObservationCycle",
            rationale=f"Retrying observation after failure: {outcome.failure_reason or 'unknown'}",
            is_valid=True
        )
    
    def transition_mode(self, target_mode: LoopBehavioralMode) -> "MonitoringPolicy":
        """Return new policy with specified mode."""
        # Map to monitoring behavior
        new_mode = LoopBehavioralMode.MONITORING  # Default
        return MonitoringPolicy(state=dataclass_replace(
            self._state,
            current_mode=new_mode
        ))
    
    def get_state(self) -> LoopState:
        """Get policy-local state."""
        return LoopState(
            current_mode=self.current_mode,
            iteration_count=self._state.observation_count,
            completion_confidence=0.5  # Monitoring doesn't have traditional completion
        )
    
    def update_state(self, state: LoopState) -> None:
        """Update policy state from external source."""
        pass


def create_monitoring_policy() -> MonitoringPolicy:
    """Create a new MonitoringLoop policy."""
    return MonitoringPolicy()


# =============================================================================
# RecoveryLoop Implementation
# =============================================================================

@dataclass(frozen=True)
class RecoveryPolicyState:
    """Policy-local state for RecoveryLoop."""
    current_mode: LoopBehavioralMode = LoopBehavioralMode.RECOVERY
    recovery_attempts: int = 0
    failure_classification: Optional[str] = None
    selected_strategy: Optional[str] = None


class RecoveryPolicy(LoopPolicy):
    """
    Behavioral policy for performing semantic recovery after failed execution.
    
    This policy is used temporarily when TaskThread needs to recover from failure.
    """
    
    def __init__(self, state: Optional[RecoveryPolicyState] = None):
        self._policy_id = "recovery-1.0"
        self._state = state or RecoveryPolicyState()
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopBehavioralMode:
        return LoopBehavioralMode.RECOVERY
    
    def decide(self, context: LoopContext) -> ExecutionLoopDecision:
        """Evaluate current state and produce a recovery decision."""
        
        self._state = dataclass_replace(
            self._state,
            recovery_attempts=self._state.recovery_attempts + 1
        )
        
        # Check for pending interruptions
        if context.pending_interruptions:
            return TerminateDecision(
                decision_type=DecisionType.TERMINATE,
                thread_revision=context.thread_revision,
                termination_reason="Recovery interrupted",
                is_valid=True
            )
        
        # First iteration - analyze failure and select strategy
        if not context.previous_cycle_outcome:
            self._state = dataclass_replace(
                self._state,
                failure_classification="initial_analysis"
            )
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="FailureAnalysisCycle",
                rationale="Analyzing failure for recovery strategy",
                is_valid=True
            )
        
        outcome = context.previous_cycle_outcome
        
        if outcome.status == "completed":
            # Recovery cycle completed - evaluate result
            if self._state.recovery_attempts >= 3:
                # Too many recovery attempts - return to original loop with failure
                return TerminateDecision(
                    decision_type=DecisionType.TERMINATE,
                    thread_revision=context.thread_revision,
                    termination_reason="Recovery failed after multiple attempts",
                    is_valid=True
                )
            
            self._state = dataclass_replace(self._state, selected_strategy=None)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="RecoveryCycle",
                rationale=f"Attempting recovery again (attempt {self._state.recovery_attempts})",
                is_valid=True
            )
        
        # Recovery failed - try different strategy or terminate
        if self._state.recovery_attempts >= 3:
            return TerminateDecision(
                decision_type=DecisionType.TERMINATE,
                thread_revision=context.thread_revision,
                termination_reason=f"Recovery exhausted after {self._state.recovery_attempts} attempts",
                is_valid=True
            )
        
        # Try again with different strategy
        self._state = dataclass_replace(self._state, selected_strategy="retry_alternative")
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="RecoveryCycle",
            rationale=f"Trying alternative recovery strategy (attempt {self._state.recovery_attempts})",
            is_valid=True
        )
    
    def transition_mode(self, target_mode: LoopBehavioralMode) -> "RecoveryPolicy":
        """Return new policy with specified mode."""
        return RecoveryPolicy(state=self._state)
    
    def get_state(self) -> LoopState:
        """Get policy-local state."""
        return LoopState(
            current_mode=self.current_mode,
            iteration_count=self._state.recovery_attempts,
            completion_confidence=0.0  # Recovery doesn't complete until success
        )
    
    def update_state(self, state: LoopState) -> None:
        """Update policy state from external source."""
        pass


def create_recovery_policy() -> RecoveryPolicy:
    """Create a new RecoveryLoop policy."""
    return RecoveryPolicy()


# =============================================================================
# IdleLoop Implementation
# =============================================================================

class IdleBehavior(Enum):
    """
    Behavioral modes for IdleLoop.
    
    These define internal activities during idle periods:
        - REFLECTING: Thinking about past execution and learning
        - CONSOLIDATING: Consolidating fragmented semantic state
        - MAINTAINING: Performing internal maintenance tasks
    """
    REFLECTING = "reflecting"
    CONSOLIDATING = "consolidating"
    MAINTAINING = "maintaining"


@dataclass(frozen=True)
class IdlePolicyState:
    """Policy-local state for IdleLoop."""
    current_mode: LoopBehavioralMode = LoopBehavioralMode.IDLE
    idle_behavior: IdleBehavior = IdleBehavior.REFLECTING
    reflection_count: int = 0
    consolidation_count: int = 0


class IdlePolicy(LoopPolicy):
    """
    Behavioral policy for internal semantic work during idle periods.
    
    This policy governs autonomous internally initiated work when no urgent
    external execution is required.
    """
    
    def __init__(self, state: Optional[IdlePolicyState] = None):
        self._policy_id = "idle-1.0"
        self._state = state or IdlePolicyState()
    
    @property
    def policy_id(self) -> str:
        return self._policy_id
    
    @property
    def current_mode(self) -> LoopBehavioralMode:
        if self._state.current_behavior == IdleBehavior.REFLECTING:
            return LoopBehavioralMode.REFLECTIVE
        elif self._state.current_behavior == IdleBehavior.CONSOLIDATING:
            return LoopBehavioralMode.ACTIVE
        else:
            return LoopBehavioralMode.IDLE
    
    @property
    def current_behavior(self) -> IdleBehavior:
        """Get current idle behavior (alias for compatibility)."""
        return self._state.idle_behavior
    
    def decide(self, context: LoopContext) -> ExecutionLoopDecision:
        """Evaluate current state and produce an idle decision."""
        
        # Check for pending interruptions (e.g., external request)
        if context.pending_interruptions:
            # Yield to more important work
            return SuspendDecision(
                decision_type=DecisionType.SUSPEND,
                thread_revision=context.thread_revision,
                rationale="Yielding to external interruption",
                is_valid=True
            )
        
        # First iteration - start with reflection
        if not context.previous_cycle_outcome:
            self._state = dataclass_replace(self._state, idle_behavior=IdleBehavior.REFLECTING)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition="ReflectionCycle",
                rationale="Starting internal reflection",
                is_valid=True
            )
        
        outcome = context.previous_cycle_outcome
        
        if outcome.status == "completed":
            # Process the internal work result
            self._state = dataclass_replace(
                self._state,
                reflection_count=self._state.reflection_count + 1
                    if self._state.idle_behavior == IdleBehavior.REFLECTING else self._state.reflection_count,
                consolidation_count=self._state.consolidation_count + 1
                    if self._state.idle_behavior == IdleBehavior.CONSOLIDATING else self._state.consolidation_count,
            )
            
            # Cycle through different internal activities
            behavior_cycle = [IdleBehavior.REFLECTING, IdleBehavior.CONSOLIDATING, IdleBehavior.MAINTAINING]
            current_idx = behavior_cycle.index(self._state.idle_behavior)
            next_behavior = behavior_cycle[(current_idx + 1) % len(behavior_cycle)]
            
            self._state = dataclass_replace(self._state, idle_behavior=next_behavior)
            return ContinueDecision(
                decision_type=DecisionType.CONTINUE,
                thread_revision=context.thread_revision,
                cycle_definition=f"{next_behavior.value.capitalize()}Cycle",
                rationale=f"Moving to {next_behavior.value} activity",
                is_valid=True
            )
        
        # Failure - try same behavior again
        self._state = dataclass_replace(self._state, idle_behavior=IdleBehavior.REFLECTING)
        return ContinueDecision(
            decision_type=DecisionType.CONTINUE,
            thread_revision=context.thread_revision,
            cycle_definition="ReflectionCycle",
            rationale=f"Retrying reflection after failure: {outcome.failure_reason or 'unknown'}",
            is_valid=True
        )
    
    def transition_mode(self, target_mode: LoopBehavioralMode) -> "IdlePolicy":
        """Return new policy with specified mode."""
        # Map to idle behaviors
        if target_mode == LoopBehavioralMode.REFLECTIVE:
            behavior = IdleBehavior.REFLECTING
        elif target_mode == LoopBehavioralMode.IDLE:
            behavior = IdleBehavior.MAINTAINING
        else:
            behavior = IdleBehavior.REFLECTING  # Default
        
        return IdlePolicy(state=dataclass_replace(
            self._state,
            current_behavior=behavior
        ))
    
    def get_state(self) -> LoopState:
        """Get policy-local state."""
        return LoopState(
            current_mode=self.current_mode,
            iteration_count=self._state.reflection_count + self._state.consolidation_count,
            completion_confidence=0.5  # Idle work doesn't have traditional completion
        )
    
    def update_state(self, state: LoopState) -> None:
        """Update policy state from external source."""
        pass


def create_idle_policy() -> IdlePolicy:
    """Create a new IdleLoop policy."""
    return IdlePolicy()


# =============================================================================
# Export all public symbols
# =============================================================================

__all__ = [
    # Conversation loop
    "ConversationBehavior",
    "ConversationPolicyState",
    "ConversationPolicy",
    "create_conversation_policy",
    
    # Task loop
    "TaskBehavior",
    "TaskPolicyState",
    "TaskPolicy",
    "create_task_policy",
    
    # Planning loop
    "PlanningPolicyState",
    "PlanningPolicy",
    "create_planning_policy",
    
    # Monitoring loop
    "MonitoringPolicyState",
    "MonitoringPolicy",
    "create_monitoring_policy",
    
    # Recovery loop
    "RecoveryPolicyState",
    "RecoveryPolicy",
    "create_recovery_policy",
    
    # Idle loop
    "IdleBehavior",
    "IdlePolicyState",
    "IdlePolicy",
    "create_idle_policy",
]