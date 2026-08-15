# Executive State Summaries
# =========================

"""
Summary types for executive state.

These provide bounded summaries of executive conditions without implementing
the full detailed models (which belong to later phases).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# SUMMARY STATUS ENUMS
# =============================================================================


class ExecutiveSummaryStatus(Enum):
    """Status of an executive summary."""
    
    UNKNOWN = "unknown"
    """Unknown status."""
    
    NONE = "none"
    """No issues detected."""
    
    LOW = "low"
    """Minor issues or low demand."""
    
    MEDIUM = "medium"
    """Moderate issues or demand."""
    
    HIGH = "high"
    """Significant issues or high demand."""
    
    CRITICAL = "critical"
    """Critical issues requiring immediate attention."""


# =============================================================================
# CONTROL STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutiveControlStateSummary:
    """
    Summary of current control state.
    
    Provides a bounded view of control allocation without exposing full
    implementation details.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall control status."""
    
    allocated_capacity: float = 0.0
    """Currently allocated control capacity (0.0 to 1.0)."""
    
    available_capacity: float = 1.0
    """Remaining available control capacity (0.0 to 1.0)."""
    
    active_allocations: Tuple[str, ...] = field(default_factory=tuple)
    """Identifiers of active control allocations."""
    
    total_demands: int = 0
    """Total number of control demands being considered."""
    
    is_saturated: bool = False
    """Whether capacity is fully saturated."""
    
    confidence: float = 1.0
    """Confidence in the summary (0.0 to 1.0)."""
    
    @property
    def demand_level(self) -> str:
        """Get a human-readable demand level string."""
        if self.is_saturated:
            return "critical"
        elif self.available_capacity < 0.2:
            return "high"
        elif self.available_capacity < 0.5:
            return "medium"
        else:
            return "low"


# =============================================================================
# CONFLICT STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutiveConflictStateSummary:
    """
    Summary of conflict state.
    
    Provides a bounded view of conflicts without implementing full
    conflict resolution algorithms.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall conflict status."""
    
    unresolved_count: int = 0
    """Number of unresolved conflicts."""
    
    resolved_count: int = 0
    """Number of resolved conflicts (in this session)."""
    
    critical_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of critical unresolved conflicts."""
    
    high_priority_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of high-priority unresolved conflicts."""
    
    medium_priority_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of medium-priority unresolved conflicts."""
    
    low_priority_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of low-priority unresolved conflicts."""
    
    confidence: float = 1.0
    """Confidence in conflict assessment (0.0 to 1.0)."""
    
    @property
    def has_unresolved(self) -> bool:
        """Check if there are any unresolved conflicts."""
        return self.unresolved_count > 0
    
    @property
    def severity_class(self) -> str:
        """Get the highest severity class of unresolved conflicts."""
        if self.critical_conflicts:
            return "critical"
        elif self.high_priority_conflicts:
            return "high"
        elif self.medium_priority_conflicts:
            return "medium"
        elif self.low_priority_conflicts:
            return "low"
        return "none"


# =============================================================================
# PERFORMANCE STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutivePerformanceStateSummary:
    """
    Summary of performance state.
    
    Provides a bounded view of performance without implementing full
    monitoring algorithms.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall performance status."""
    
    evaluation_count: int = 0
    """Number of evaluations performed."""
    
    success_rate: float = 1.0
    """Historical success rate (0.0 to 1.0)."""
    
    average_duration_seconds: float = 0.0
    """Average evaluation duration in seconds."""
    
    error_count: int = 0
    """Number of errors encountered."""
    
    timeout_count: int = 0
    """Number of timeouts encountered."""
    
    confidence: float = 1.0
    """Confidence in performance assessment (0.0 to 1.0)."""
    
    @property
    def is_healthy(self) -> bool:
        """Check if performance appears healthy."""
        return (
            self.status == ExecutiveSummaryStatus.NONE
            and self.success_rate >= 0.95
            and self.error_count < 10
        )


# =============================================================================
# DECISION STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutiveDecisionStateSummary:
    """
    Summary of decision state.
    
    Provides a bounded view of decision readiness without implementing full
    decision algorithms.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall decision status."""
    
    requirements_met: bool = True
    """Whether all decision requirements are met."""
    
    missing_information: Tuple[str, ...] = field(default_factory=tuple)
    """Information needed but not available."""
    
    decision_count: int = 0
    """Number of decisions made in this session."""
    
    pending_decisions: int = 0
    """Number of decisions waiting for input."""
    
    confidence: float = 1.0
    """Confidence in decision assessment (0.0 to 1.0)."""
    
    @property
    def is_ready(self) -> bool:
        """Check if a decision can be made."""
        return self.status == ExecutiveSummaryStatus.NONE and self.requirements_met


# =============================================================================
# INHIBITION STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutiveInhibitionStateSummary:
    """
    Summary of inhibition state.
    
    Provides a bounded view of inhibition without implementing full
    inhibition algorithms.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall inhibition status."""
    
    active_inhibitions: int = 0
    """Number of currently active inhibitions."""
    
    total_targets: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of inhibited targets."""
    
    strength: float = 0.0
    """Overall inhibition strength (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in inhibition assessment (0.0 to 1.0)."""
    
    @property
    def is_over_inhibited(self) -> bool:
        """Check if inhibition may be excessive."""
        return self.strength > 0.8


# =============================================================================
# SWITCHING STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutiveSwitchingStateSummary:
    """
    Summary of switching state.
    
    Provides a bounded view of switching needs without implementing full
    switching algorithms.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall switching status."""
    
    switch_required: bool = False
    """Whether a switch is currently required."""
    
    current_switch_type: Optional[str] = None
    """Type of switch if one is required (e.g., 'task', 'strategy')."""
    
    recent_switches: int = 0
    """Number of switches in recent history."""
    
    optimal_strategy: bool = True
    """Whether the current strategy appears optimal."""
    
    confidence: float = 1.0
    """Confidence in switching assessment (0.0 to 1.0)."""
    
    @property
    def needs_attention(self) -> bool:
        """Check if switching attention is required."""
        return self.switch_required or not self.optimal_strategy


# =============================================================================
# RECOVERY STATE SUMMARY
# =============================================================================


@dataclass(frozen=True)
class ExecutiveRecoveryStateSummary:
    """
    Summary of recovery state.
    
    Provides a bounded view of recovery needs without implementing full
    recovery algorithms.
    """
    
    status: ExecutiveSummaryStatus = ExecutiveSummaryStatus.NONE
    """Overall recovery status."""
    
    in_recovery: bool = False
    """Whether currently in recovery mode."""
    
    recovery_steps_completed: int = 0
    """Number of recovery steps completed."""
    
    total_recovery_steps: int = 0
    """Total number of recovery steps needed."""
    
    error_type: Optional[str] = None
    """Type of error causing recovery (if known)."""
    
    confidence: float = 1.0
    """Confidence in recovery assessment (0.0 to 1.0)."""
    
    @property
    def is_recovering(self) -> bool:
        """Check if recovering from an error."""
        return self.in_recovery
    
    @property
    def completion_fraction(self) -> float:
        """Get the fraction of recovery completed."""
        if self.total_recovery_steps == 0:
            return 1.0
        return self.recovery_steps_completed / self.total_recovery_steps


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveSummaryStatus",
    "ExecutiveControlStateSummary",
    "ExecutiveConflictStateSummary",
    "ExecutivePerformanceStateSummary",
    "ExecutiveDecisionStateSummary",
    "ExecutiveInhibitionStateSummary",
    "ExecutiveSwitchingStateSummary",
    "ExecutiveRecoveryStateSummary",
)