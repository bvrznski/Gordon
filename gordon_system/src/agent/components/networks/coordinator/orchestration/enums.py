# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Orchestration Enumerations
==========================

Immutable enumerations for orchestration components.
All enums are frozen to ensure deterministic behavior.
"""

from __future__ import annotations

from enum import Enum, auto


class CycleKind(Enum):
    """
    Type of cognitive cycle being orchestrated.
    
    CYCLE-LAW-001: Every orchestration belongs to exactly one Cognitive Cycle
    CYCLE-LAW-002: Every Cognitive Cycle possesses explicit scope
    
    Suggested kinds per spec:
        PERCEPTION
        REASONING
        ACTION
        PLANNING
        LEARNING
        REFLECTION
        MEMORY
        DIALOGUE
        RECOVERY
        SLEEP
    """
    
    PERCEPTION = "perception"
    """Cycle focused on sensory perception and world model update."""
    
    REASONING = "reasoning"
    """Cycle focused on logical inference and deduction."""
    
    ACTION = "action"
    """Cycle focused on action selection and execution."""
    
    PLANNING = "planning"
    """Cycle focused on long-term planning and strategy."""
    
    LEARNING = "learning"
    """Cycle focused on learning from experience."""
    
    REFLECTION = "reflection"
    """Cycle focused on metacognition and self-assessment."""
    
    MEMORY = "memory"
    """Cycle focused on memory retrieval, update, and consolidation."""
    
    DIALOGUE = "dialogue"
    """Cycle focused on interactive communication."""
    
    RECOVERY = "recovery"
    """Cycle focused on error recovery and degradation handling."""
    
    SLEEP = "sleep"
    """Cycle focused on maintenance and offline processing."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified cycle kind."""


class StageKind(Enum):
    """
    Kind of execution stage.
    
    STAGE-LAW-001: Every execution stage possesses stable identity
    STAGE-LAW-002: Every stage belongs to exactly one orchestration plan
    
    Suggested stages per spec:
        INITIALIZATION
        CONTEXT_PREPARATION
        PERCEPTION
        ORIENTATION
        SALIENCE
        WORKSPACE_UPDATE
        PREDICTION
        REWARD_ESTIMATION
        EXECUTIVE_EVALUATION
        ACTION_SELECTION
        ACTION_PREPARATION
        ACTION_COMPLETION
        MEMORY_UPDATE
        LEARNING
        REFLECTION
        VALIDATION
        TERMINATION
    """
    
    INITIALIZATION = "initialization"
    """Setup coordination infrastructure and load context."""
    
    CONTEXT_PREPARATION = "context_preparation"
    """Prepare workspace and gather relevant information."""
    
    PERCEPTION = "perception"
    """Process sensory input and update world model."""
    
    ORIENTATION = "orientation"
    """Identify targets and set focus."""
    
    SALIENCE = "salience"
    """Rank candidates and determine urgency."""
    
    WORKSPACE_UPDATE = "workspace_update"
    """Update working memory and establish context."""
    
    PREDICTION = "prediction"
    """Generate predictions and evaluate accuracy."""
    
    REWARD_ESTIMATION = "reward_estimation"
    """Estimate rewards and compute values."""
    
    EXECUTIVE_EVALUATION = "executive_evaluation"
    """Evaluate options and make selection."""
    
    ACTION_SELECTION = "action_selection"
    """Select actions and configure parameters."""
    
    ACTION_PREPARATION = "action_preparation"
    """Prepare motor commands and validate feasibility."""
    
    ACTION_COMPLETION = "action_completion"
    """Execute actions and monitor progress."""
    
    MEMORY_UPDATE = "memory_update"
    """Store experiences and update models."""
    
    LEARNING = "learning"
    """Extract patterns and adapt strategies."""
    
    REFLECTION = "reflection"
    """Evaluate process and plan improvements."""
    
    VALIDATION = "validation"
    """Verify outcomes and assess correctness."""
    
    TERMINATION = "termination"
    """Clean up resources and report results."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified stage kind."""


class ParticipantRole(Enum):
    """
    Role of a participant in a cycle.
    
    PARTICIPANT-LAW-001: Every participant represents exactly one cognitive network
    PARTICIPANT-LAW-002: Participation roles remain explicit
    
    Suggested roles per spec:
        PRIMARY - main contributor
        SUPPORTING - assist primary participants
        OPTIONAL - may join or leave without invalidating plan
        OBSERVER - watch but do not contribute
        RECOVERY - responsible for recovery operations
        VALIDATOR - verify correctness of results
        BACKGROUND - runs in background with low priority
    """
    
    PRIMARY = "primary"
    """Main contributor to the cycle."""
    
    SUPPORTING = "supporting"
    """Assists primary participants."""
    
    OPTIONAL = "optional"
    """May join or leave without invalidating orchestration plan."""
    
    OBSERVER = "observer"
    """Observes but does not actively participate."""
    
    RECOVERY = "recovery"
    """Responsible for recovery operations."""
    
    VALIDATOR = "validator"
    """Verifies correctness of results."""
    
    BACKGROUND = "background"
    """Runs in background with low priority."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified role."""


class DependencyKind(Enum):
    """
    Kind of dependency between stages.
    
    DEPENDENCY-LAW-001: Execution dependencies remain explicit
    DEPENDENCY-LAW-002: Dependency graphs remain acyclic unless explicitly declared
    
    Suggested kinds per spec:
        DATA - data flow dependency
        CONTROL - control flow dependency
        RESOURCE - resource access dependency
        SYNCHRONIZATION - synchronization barrier requirement
        VALIDATION - validation result dependency
    """
    
    DATA = "data"
    """Stage requires output from prerequisite stage."""
    
    CONTROL = "control"
    """Stage requires prerequisite to complete before executing."""
    
    RESOURCE = "resource"
    """Stage requires access to resources managed by prerequisite."""
    
    SYNCHRONIZATION = "synchronization"
    """Stage must synchronize with prerequisite at barrier."""
    
    VALIDATION = "validation"
    """Stage requires validation result from prerequisite."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified dependency kind."""


class SynchronizationPolicy(Enum):
    """
    Policy for synchronization behavior.
    
    BARRIER-LAW-001: Every synchronization barrier possesses stable identity
    BARRIER-LAW-003: Barrier release conditions remain explicit
    
    Suggested policies:
        ALL_PARTICIPANTS - all participants must reach barrier
        MAJORITY - majority of participants sufficient
        FIRST_COMPLETE - first completion releases barrier
        TIMEOUT_REQUIRED - timeout-based with required participants
    """
    
    ALL_PARTICIPANTS = "all_participants"
    """All registered participants must reach barrier."""
    
    MAJORITY = "majority"
    """Majority of participants sufficient."""
    
    FIRST_COMPLETE = "first_complete"
    """First completion releases barrier."""
    
    TIMEOUT_REQUIRED = "timeout_required"
    """Timeout-based with required participant count."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified policy."""


class ResourceBudgetPolicy(Enum):
    """
    Policy for resource budget allocation.
    
    RESOURCE-LAW-001: Resource allocation remains semantic
    RESOURCE-LAW-004: Resource policies remain explicit
    
    Suggested policies per spec:
        CONSERVATIVE - minimize usage, prioritize safety
        BALANCED - mix of performance and efficiency
        PERFORMANCE - maximize throughput, use resources freely
        MINIMAL - minimal resource footprint
        EMERGENCY - burst allocation for critical scenarios
    """
    
    CONSERVATIVE = "conservative"
    """Minimize resource usage, prioritize safety."""
    
    BALANCED = "balanced"
    """Mix of performance and efficiency."""
    
    PERFORMANCE = "performance"
    """Maximize throughput, use resources freely."""
    
    MINIMAL = "minimal"
    """Minimal resource footprint."""
    
    EMERGENCY = "emergency"
    """Burst allocation for critical scenarios."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified policy."""


class CompletionPolicy(Enum):
    """
    Policy for determining cycle completion.
    
    COMPLETION-LAW-001: Completion policy remains explicit
    COMPLETION-LAW-002: Cycle completion shall satisfy completion policy requirements
    
    Suggested policies per spec:
        ALL_REQUIRED_COMPLETE - all mandatory participants must complete
        MAJORITY_COMPLETE - majority participation sufficient
        GOAL_SATISFIED - stop when goal is achieved
        FIRST_VALID_RESULT - accept first valid result
        TIME_LIMIT - terminate after time budget exhausted
        MANUAL_TERMINATION - external control required
    """
    
    ALL_REQUIRED_COMPLETE = "all_required_complete"
    """All mandatory participants must complete."""
    
    MAJORITY_COMPLETE = "majority_complete"
    """Majority participation sufficient."""
    
    GOAL_SATISFIED = "goal_satisfied"
    """Stop when goal is achieved."""
    
    FIRST_VALID_RESULT = "first_valid_result"
    """Accept first valid result."""
    
    TIME_LIMIT = "time_limit"
    """Terminate after time budget exhausted."""
    
    MANUAL_TERMINATION = "manual_termination"
    """External control required for termination."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified policy."""


class ExecutionPolicy(Enum):
    """
    Policy for execution orchestration behavior.
    
    POLICY-LAW-001: Every orchestration shall reference exactly one execution policy
    POLICY-LAW-002: Policies influence orchestration without altering cognition
    
    Suggested policies per spec:
        LATENCY_OPTIMIZED - minimize response time
        THROUGHPUT_OPTIMIZED - maximize processing rate
        RESOURCE_EFFICIENT - minimize resource usage
        SAFETY_FIRST - prioritize safety over speed
        EXPLORATORY - encourage experimentation
        DETERMINISTIC - ensure reproducibility
    """
    
    LATENCY_OPTIMIZED = "latency_optimized"
    """Minimize response time."""
    
    THROUGHPUT_OPTIMIZED = "throughput_optimized"
    """Maximize processing rate."""
    
    RESOURCE_EFFICIENT = "resource_efficient"
    """Minimize resource usage."""
    
    SAFETY_FIRST = "safety_first"
    """Prioritize safety over speed."""
    
    EXPLORATORY = "exploratory"
    """Encourage experimentation."""
    
    DETERMINISTIC = "deterministic"
    """Ensure reproducibility."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified policy."""


class Status(Enum):
    """
    General status enumeration.
    
    Every orchestration artifact has a status that indicates its current state.
    
    Suggested statuses:
        CREATED - initialized but not yet validated
        VALIDATED - passed validation
        READY - ready for execution
        ACTIVE - currently executing
        DEGRADED - executing with degraded capabilities
        COMPLETED - successfully completed
        TERMINATED - terminated before completion
        FAILED - failed during execution
    """
    
    CREATED = "created"
    """Artifact created but not yet validated."""
    
    VALIDATED = "validated"
    """Artifact passed validation."""
    
    READY = "ready"
    """Ready for execution."""
    
    ACTIVE = "active"
    """Currently executing."""
    
    DEGRADED = "degraded"
    """Executing with degraded capabilities."""
    
    COMPLETED = "completed"
    """Successfully completed."""
    
    TERMINATED = "terminated"
    """Terminated before completion."""
    
    FAILED = "failed"
    """Failed during execution."""
    
    UNKNOWN = "unknown"
    """Unknown status."""


class ValidationErrorKind(Enum):
    """
    Kind of validation error.
    
    VALIDATION-LAW-001: Every orchestration request shall validate before planning
    VALIDATION-LAW-002: Every orchestration plan shall validate before publication
    
    Suggested validation kinds per spec:
        INVALID_DEPENDENCY - dependency is malformed or invalid
        MISSING_PARTICIPANT - required participant not specified
        UNSATISFIED_CONSTRAINT - constraint cannot be satisfied
        RESOURCE_CONFLICT - resources conflict with each other
        BARRIER_INCONSISTENT - barrier configuration inconsistent
        INVALID_COMPLETION_POLICY - completion policy invalid
        UNKNOWN - unspecified validation error
    """
    
    INVALID_DEPENDENCY = "invalid_dependency"
    """Dependency is malformed or invalid."""
    
    MISSING_PARTICIPANT = "missing_participant"
    """Required participant not specified."""
    
    UNSATISFIED_CONSTRAINT = "unsatisfied_constraint"
    """Constraint cannot be satisfied."""
    
    RESOURCE_CONFLICT = "resource_conflict"
    """Resources conflict with each other."""
    
    BARRIER_INCONSISTENT = "barrier_inconsistent"
    """Barrier configuration inconsistent."""
    
    INVALID_COMPLETION_POLICY = "invalid_completion_policy"
    """Completion policy invalid."""
    
    CYCLE_DETECTED = "cycle_detected"
    """Circular dependency detected in execution graph."""
    
    UNKNOWN = "unknown"
    """Unknown validation error."""


class QueryKind(Enum):
    """
    Kind of orchestration query.
    
    QUERY-LAW-001: All queries shall be read-only
    """
    
    ACTIVE_CYCLES = "active_cycles"
    """List active cycles."""
    
    PLAN_BY_ID = "plan_by_id"
    """Get plan by its identity."""
    
    STAGES_BY_CYCLE = "stages_by_cycle"
    """Get stages for a cycle."""
    
    PARTICIPANTS_BY_STAGE = "participants_by_stage"
    """Get participants for a stage."""
    
    RESOURCE_ALLOCATIONS = "resource_allocations"
    """List resource allocations."""
    
    ACTIVE_BARRIERS = "active_barriers"
    """List active synchronization barriers."""
    
    DEGRADED_CYCLES = "degraded_cycles"
    """List cycles in degraded mode."""
    
    UNKNOWN = "unknown"
    """Unknown query kind."""