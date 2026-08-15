# Executive Program Validation
# ============================

"""
Executive Program Validation - Immutable dataclasses for program validation results.

Validation checks program integrity without implementing algorithms to fix issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ExecutiveProgramValidation:
    """
    Validation result for an ExecutiveProgram.
    
    Validation checks:
        - Goal alignment
        - Commitment alignment
        - Constraint alignment
        - Strategy alignment
        - Policy alignment
        - Task set validity
        - Ownership validity
    
    Validation does NOT implement algorithms to fix problems.
    It only reports issues found.
    """
    
    # Identity and revisioning
    validation_id: str = "exec_validation_initial"
    """Unique identifier for this validation result."""
    
    program_id: str = "exec_program_initial"
    """ID of the program being validated."""
    
    schema_version: str = "1.0.0"
    """Schema version at time of validation."""
    
    checked_at_utc: float = 0.0
    """When validation was performed (seconds since epoch)."""
    
    # Validation kind
    validation_kind: str = "full"
    """
    Kind of validation:
        'full' - Complete validation of all aspects
        'structural' - Structural validity only
        'semantic' - Semantic consistency only
        'lifecycle' - Lifecycle state validity only
    """
    
    # Check results
    goal_alignment_valid: bool = True
    """Whether all goals align with program objectives."""
    
    commitment_alignment_valid: bool = True
    """Whether all commitments align with program goals."""
    
    constraint_alignment_valid: bool = True
    """Whether constraints are satisfied by program actions."""
    
    strategy_alignment_valid: bool = True
    """Whether the strategy aligns with program objectives."""
    
    policy_alignment_valid: bool = True
    """Whether the control policy is consistent."""
    
    task_set_valid: bool = True
    """Whether the task set is valid and complete."""
    
    ownership_valid: bool = True
    """Whether ownership hierarchy is correct."""
    
    # Validation metrics
    total_checks: int = 10
    """Total number of validation checks performed."""
    
    passed_checks: int = 10
    """Number of checks that passed."""
    
    failed_checks: int = 0
    """Number of checks that failed."""
    
    # Issue tracking (only IDs, not full content)
    issue_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of validation issues found."""
    
    max_issues: int = 100
    """Maximum issues to track."""
    
    # Severity classification
    severity_class: str = "none"
    """
    Severity classification:
        'none' - No issues
        'warning' - Issues that should be reviewed
        'error' - Issues that prevent valid operation
        'critical' - Critical issues requiring immediate attention
    """
    
    @classmethod
    def initial(cls) -> ExecutiveProgramValidation:
        """
        Create an initial validation result.
        
        Returns:
            New validation with all checks passing
        """
        return cls(
            validation_id="exec_validation_initial",
            total_checks=10,
            passed_checks=10,
            severity_class="none",
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the program is fully valid."""
        return (
            self.goal_alignment_valid
            and self.commitment_alignment_valid
            and self.constraint_alignment_valid
            and self.strategy_alignment_valid
            and self.policy_alignment_valid
            and self.task_set_valid
            and self.ownership_valid
            and self.severity_class in ("none", "warning")
        )
    
    @property
    def validation_score(self) -> float:
        """Get a numerical validation score (0.0 to 1.0)."""
        if self.total_checks == 0:
            return 0.0
        return self.passed_checks / self.total_checks
    
    def add_issue(self, issue_id: str) -> ExecutiveProgramValidation:
        """
        Add an issue ID to the validation result.
        
        Args:
            issue_id: ID of the validation issue
            
        Returns:
            New validation with the issue added (if capacity allows)
        """
        if len(self.issue_ids) >= self.max_issues:
            return self  # At capacity
        
        new_failed = self.failed_checks + 1
        severity = "error" if new_failed > 5 else "warning"
        
        return dataclass_replace(
            self,
            issue_ids=self.issue_ids + (issue_id,),
            failed_checks=new_failed,
            passed_checks=self.passed_checks - 1,
            severity_class=severity,
            checked_at_utc=0.0,  # Would need actual timestamp
        )


@dataclass(frozen=True)
class ExecutiveProgramConsistency:
    """
    Consistency assessment for an ExecutiveProgram.
    
    Consistency evaluates how well the program's components align with each other.
    This is about organizational quality, not correctness of execution.
    """
    
    # Identity and revisioning
    consistency_id: str = "exec_consistency_initial"
    """Unique identifier for this consistency assessment."""
    
    program_id: str = "exec_program_initial"
    """ID of the program being assessed."""
    
    schema_version: str = "1.0.0"
    """Schema version at time of assessment."""
    
    assessed_at_utc: float = 0.0
    """When assessment was performed (seconds since epoch)."""
    
    # Consistency metrics (0.0 to 1.0)
    goal_consistency: float = 1.0
    """How well goals align with each other and program objectives."""
    
    commitment_consistency: float = 1.0
    """How well commitments align with program goals."""
    
    constraint_consistency: float = 1.0
    """How well constraints are satisfied by program actions."""
    
    strategy_consistency: float = 1.0
    """How well the strategy matches program objectives."""
    
    policy_consistency: float = 1.0
    """How consistent the control policies are."""
    
    # Overall assessment
    overall_consistency: float = 1.0
    """Overall consistency score (weighted average)."""
    
    consistency_class: str = "consistent"
    """
    Consistency classification:
        'consistent' - All components align well
        'partially_consistent' - Some misalignments present
        'inconsistent' - Significant misalignments detected
        'contradictory' - Direct contradictions found
    """
    
    @classmethod
    def initial(cls) -> ExecutiveProgramConsistency:
        """
        Create an initial consistency assessment.
        
        Returns:
            New assessment with all components consistent
        """
        return cls(
            consistency_id="exec_consistency_initial",
            overall_consistency=1.0,
            consistency_class="consistent",
        )
    
    def update_overall(self) -> ExecutiveProgramConsistency:
        """Update the overall consistency score based on component scores."""
        overall = (
            self.goal_consistency * 0.25
            + self.commitment_consistency * 0.25
            + self.constraint_consistency * 0.20
            + self.strategy_consistency * 0.15
            + self.policy_consistency * 0.15
        )
        
        if overall >= 0.9:
            consistency_class = "consistent"
        elif overall >= 0.7:
            consistency_class = "partially_consistent"
        elif overall >= 0.5:
            consistency_class = "inconsistent"
        else:
            consistency_class = "contradictory"
        
        return dataclass_replace(
            self,
            overall_consistency=overall,
            consistency_class=consistency_class,
            assessed_at_utc=0.0,  # Would need actual timestamp
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def dataclass_replace(instance: object, **kwargs) -> object:
    """
    Helper to replace fields in an immutable dataclass instance.
    
    Args:
        instance: The dataclass instance to copy
        kwargs: Field names and new values
        
    Returns:
        New instance with specified fields replaced
    """
    import dataclasses
    
    if not hasattr(instance, "__dataclass_fields__"):
        raise TypeError(f"{type(instance).__name__} is not a dataclass")
    
    # Get current field values
    field_dict = {f.name: getattr(instance, f.name) for f in dataclasses.fields(instance)}
    
    # Update with new values
    field_dict.update(kwargs)
    
    # Create new instance
    return type(instance)(**field_dict)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveProgramValidation",
    "ExecutiveProgramConsistency",
)