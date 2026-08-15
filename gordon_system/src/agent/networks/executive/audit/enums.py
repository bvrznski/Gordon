# Audit Enums - Gordon Executive Network Audit Subsystem
# =========================================================

"""
Enumeration types for the Executive Audit subsystem.
"""

from enum import Enum, auto
from typing import Tuple


class AuditStatus(Enum):
    """
    Status of an audit session.
    
    Values:
        PENDING: Session created but not yet started
        RUNNING: Session is currently executing
        COMPLETED: Session finished successfully
        FAILED: Session encountered a critical error
        DEGRADED: Session completed with degraded functionality
    """
    
    PENDING = "pending"
    """Audit session created but not yet started."""
    
    RUNNING = "running"
    """Audit session is currently executing."""
    
    COMPLETED = "completed"
    """Audit session finished successfully."""
    
    FAILED = "failed"
    """Audit session encountered a critical error."""
    
    DEGRADED = "degraded"
    """Audit session completed with degraded functionality."""
    
    @classmethod
    def terminal_values(cls) -> Tuple[str, ...]:
        """
        Get all terminal status values.
        
        Returns:
            Tuple of terminal status string values
        """
        return (cls.COMPLETED.value, cls.FAILED.value, cls.DEGRADED.value)
    
    @property
    def is_terminal(self) -> bool:
        """Check if this status is terminal (no further state changes)."""
        return self.value in self.terminal_values()


class AuditType(Enum):
    """
    Type of audit being performed.
    
    Values:
        ON_DEMAND: Requested by external caller
        SCHEDULED: Performed on regular schedule
        CONTINUOUS: Performed continuously with minimal delay
        INTEGRITY_CHECK: Special integrity verification audit
        POST_MORTEM: Performed after an incident
    """
    
    ON_DEMAND = "on_demand"
    """Requested by external caller."""
    
    SCHEDULED = "scheduled"
    """Performed on regular schedule."""
    
    CONTINUOUS = "continuous"
    """Performed continuously with minimal delay."""
    
    INTEGRITY_CHECK = "integrity_check"
    """Special integrity verification audit."""
    
    POST_MORTEM = "post_mortem"
    """Performed after an incident."""
    
    @property
    def is_automatic(self) -> bool:
        """Check if this audit type runs automatically."""
        return self in (self.SCHEDULED, self.CONTINUOUS)
    
    @property
    def is_reactive(self) -> bool:
        """Check if this audit type responds to events."""
        return self in (self.POST_MORTEM, self.INTEGRITY_CHECK)


class FindingKind(Enum):
    """
    Categories of findings that can be discovered during auditing.
    
    Values:
        POLICY_VIOLATION: Executive violated a policy
        UNAUTHORIZED_DECISION: Decision made without proper authorization
        CONSTRAINT_VIOLATION: Constraint was not satisfied
        SCHEDULING_CONFLICT: Conflict in scheduling or timing
        PRIORITY_OSCILLATION: Priority values are unstable
        RESOURCE_STARVATION: Resource allocation insufficient
        DEADLOCK_RISK: Potential for deadlock or blocking
        GOAL_CONFLICT: Goals that conflict with each other
        DECISION_CONFLICT: Decisions that contradict each other
        EXECUTION_FAILURE: Task execution did not complete
        RECOVERY_FAILURE: Recovery action did not succeed
        CONFIGURATION_MISMATCH: Configuration inconsistency detected
        DEPENDENCY_FAILURE: Subsystem dependency failed
        HEALTH_DEGRADATION: Executive health metrics indicate issues
        STATE_CORRUPTION_RISK: Evidence of potential state corruption
        DUPLICATE_EXECUTION: Same task executed multiple times
        SKIPPED_AUTHORIZATION: Authorization was not performed
        UNEXPECTED_TRANSITION: State transition was unexpected
        UNEXPECTED_TERMINATION: Unexpected shutdown or termination
    """
    
    POLICY_VIOLATION = "policy_violation"
    """Executive violated a policy."""
    
    UNAUTHORIZED_DECISION = "unauthorized_decision"
    """Decision made without proper authorization."""
    
    CONSTRAINT_VIOLATION = "constraint_violation"
    """Constraint was not satisfied."""
    
    SCHEDULING_CONFLICT = "scheduling_conflict"
    """Conflict in scheduling or timing."""
    
    PRIORITY_OSCILLATION = "priority_oscillation"
    """Priority values are unstable."""
    
    RESOURCE_STARVATION = "resource_starvation"
    """Resource allocation insufficient."""
    
    DEADLOCK_RISK = "deadlock_risk"
    """Potential for deadlock or blocking."""
    
    GOAL_CONFLICT = "goal_conflict"
    """Goals that conflict with each other."""
    
    DECISION_CONFLICT = "decision_conflict"
    """Decisions that contradict each other."""
    
    EXECUTION_FAILURE = "execution_failure"
    """Task execution did not complete."""
    
    RECOVERY_FAILURE = "recovery_failure"
    """Recovery action did not succeed."""
    
    CONFIGURATION_MISMATCH = "configuration_mismatch"
    """Configuration inconsistency detected."""
    
    DEPENDENCY_FAILURE = "dependency_failure"
    """Subsystem dependency failed."""
    
    HEALTH_DEGRADATION = "health_degradation"
    """Executive health metrics indicate issues."""
    
    STATE_CORRUPTION_RISK = "state_corruption_risk"
    """Evidence of potential state corruption."""
    
    DUPLICATE_EXECUTION = "duplicate_execution"
    """Same task executed multiple times."""
    
    SKIPPED_AUTHORIZATION = "skipped_authorization"
    """Authorization was not performed."""
    
    UNEXPECTED_TRANSITION = "unexpected_transition"
    """State transition was unexpected."""
    
    UNEXPECTED_TERMINATION = "unexpected_termination"
    """Unexpected shutdown or termination."""
    
    @property
    def is_critical(self) -> bool:
        """Check if this finding kind indicates critical issues."""
        return self in (
            self.UNAUTHORIZED_DECISION,
            self.STATE_CORRUPTION_RISK,
            self.SKIPPED_AUTHORIZATION,
        )
    
    @property
    def is_degradation_indicator(self) -> bool:
        """Check if this finding kind indicates degraded operation."""
        return self in (
            self.HEALTH_DEGRADATION,
            self.DEPENDENCY_FAILURE,
            self.RECOVERY_FAILURE,
        )


class RecommendationKind(Enum):
    """
    Categories of recommendations that can be generated.
    
    Values:
        REVIEW_DECISION: Review a decision for correctness
        REPLAN: Generate new plans
        RESCHEDULE: Reschedule tasks or events
        INCREASE_PRIORITY: Increase priority of certain items
        REDUCE_PRIORITY: Decrease priority of certain items
        RETRY_EXECUTION: Retry failed execution
        REQUEST_HUMAN_REVIEW: Request human review
        PAUSE_EXECUTION: Pause current execution
        INVESTIGATE_DEPENDENCY: Investigate a dependency
        REINITIALIZE_SUBSYSTEM: Reinitialize a subsystem
        PERFORM_RECOVERY: Perform recovery actions
        RUN_INTEGRITY_CHECK: Run integrity verification
    """
    
    REVIEW_DECISION = "review_decision"
    """Review a decision for correctness."""
    
    REPLAN = "replan"
    """Generate new plans."""
    
    RESCHEDULE = "reschedule"
    """Reschedule tasks or events."""
    
    INCREASE_PRIORITY = "increase_priority"
    """Increase priority of certain items."""
    
    REDUCE_PRIORITY = "reduce_priority"
    """Decrease priority of certain items."""
    
    RETRY_EXECUTION = "retry_execution"
    """Retry failed execution."""
    
    REQUEST_HUMAN_REVIEW = "request_human_review"
    """Request human review."""
    
    PAUSE_EXECUTION = "pause_execution"
    """Pause current execution."""
    
    INVESTIGATE_DEPENDENCY = "investigate_dependency"
    """Investigate a dependency."""
    
    REINITIALIZE_SUBSYSTEM = "reinitialize_subsystem"
    """Reinitialize a subsystem."""
    
    PERFORM_RECOVERY = "perform_recovery"
    """Perform recovery actions."""
    
    RUN_INTEGRITY_CHECK = "run_integrity_check"
    """Run integrity verification."""
    
    @property
    def requires_authority(self) -> bool:
        """
        Check if this recommendation requires authority approval.
        
        Returns:
            True if the recommendation involves direct system changes
        """
        return self in (
            self.PAUSE_EXECUTION,
            self.REINITIALIZE_SUBSYSTEM,
            self.PERFORM_RECOVERY,
            self.RUN_INTEGRITY_CHECK,
        )
    
    @property
    def is_urgent(self) -> bool:
        """Check if this recommendation requires immediate attention."""
        return self in (
            self.REQUEST_HUMAN_REVIEW,
            self.PAUSE_EXECUTION,
        )


class RiskLevel(Enum):
    """
    Risk levels for audit findings.
    
    Values:
        NEGLECTIBLE: No meaningful risk
        LOW: Some risk but acceptable with monitoring
        MEDIUM: Significant risk requiring attention
        HIGH: Critical risk requiring immediate action
    """
    
    NEGLECTIBLE = "negligible"
    """No meaningful risk."""
    
    LOW = "low"
    """Some risk but acceptable with monitoring."""
    
    MEDIUM = "medium"
    """Significant risk requiring attention."""
    
    HIGH = "high"
    """Critical risk requiring immediate action."""
    
    @property
    def score_range(self) -> Tuple[int, int]:
        """
        Get the numeric score range for this risk level.
        
        Returns:
            Tuple of (min_score, max_score)
        """
        if self == self.NEGLECTIBLE:
            return (0, 25)
        elif self == self.LOW:
            return (26, 49)
        elif self == self.MEDIUM:
            return (50, 79)
        else:  # HIGH
            return (80, 100)


class DegradationMode(Enum):
    """
    Modes of degraded operation.
    
    Values:
        NONE: Full functionality available
        PARTIAL: Some features unavailable but core functionality works
        CRITICAL: Core functionality compromised
    """
    
    NONE = "none"
    """Full functionality available."""
    
    PARTIAL = "partial"
    """Some features unavailable but core functionality works."""
    
    CRITICAL = "critical"
    """Core functionality compromised."""
    
    @property
    def is_operational(self) -> bool:
        """Check if subsystem can still operate in this mode."""
        return self != self.CRITICAL
    
    @property
    def requires_attention(self) -> bool:
        """Check if this mode requires attention from operators."""
        return self != self.NONE


class EvidenceSource(Enum):
    """
    Categories of evidence sources.
    
    Values:
        STATE: Executive state information
        CONTEXT: Executive context projections
        PROGRAMS: Program definitions and history
        GOALS: Goal state and status
        COMMITMENTS: Commitment tracking
        CONFLICTS: Conflict detection results
        DEMAND: Demand assessment data
        PERFORMANCE: Performance metrics
        POLICY: Policy compliance evidence
        DECISIONS: Decision records
    """
    
    STATE = "state"
    """Executive state information."""
    
    CONTEXT = "context"
    """Executive context projections."""
    
    PROGRAMS = "programs"
    """Program definitions and history."""
    
    GOALS = "goals"
    """Goal state and status."""
    
    COMMITMENTS = "commitments"
    """Commitment tracking."""
    
    CONFLICTS = "conflicts"
    """Conflict detection results."""
    
    DEMAND = "demand"
    """Demand assessment data."""
    
    PERFORMANCE = "performance"
    """Performance metrics."""
    
    POLICY = "policy"
    """Policy compliance evidence."""
    
    DECISIONS = "decisions"
    """Decision records."""