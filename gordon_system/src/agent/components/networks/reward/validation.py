# Reward Network - Validation Module (Phase 4.10.4)
# ==================================================

"""
Validation module for temporal reward analysis results.

Implements validation for all Phase 4.10.4 components ensuring semantic
consistency, type safety, and immutability without modifying any state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class ValidationTrace:
    """Trace of validation events for provenance."""
    
    events: Tuple[str, ...] = field(default_factory=tuple)
    
    def add(self, event: str) -> ValidationTrace:
        """Add an event to the trace and return new instance."""
        return ValidationTrace(events=self.events + (event,))
    
    @classmethod
    def start(cls) -> ValidationTrace:
        """Start a new validation trace."""
        return cls(events=("VALIDATION_STARTED",))
    
    @property
    def is_complete(self) -> bool:
        """Check if validation completed successfully."""
        return "VALIDATION_COMPLETED" in self.events


@dataclass(frozen=True)
class ValidationError:
    """
    Record of a validation error or warning.
    
    Errors are typed and descriptive, enabling downstream systems to
    understand why validation failed without modifying the input data.
    """
    
    error_type: str  # e.g., "INVALID_TRAJECTORY_TYPE", "MISSING_ESTIMATE"
    """Type classification of the validation error."""
    
    message: str
    """Human-readable description of the error."""
    
    context: Tuple[str, ...] = field(default_factory=tuple)
    """Additional context about where the error occurred."""
    
    severity: str = "error"  # error/warning
    """Severity level (errors block processing, warnings allow continuation)."""
    
    @property
    def is_error(self) -> bool:
        """Check if this is an error (not a warning)."""
        return self.severity == "error"
    
    @classmethod
    def invalid_type(cls, field_name: str, expected_type: str) -> ValidationError:
        """Create an invalid type validation error."""
        return cls(
            error_type="INVALID_TYPE",
            message=f"Invalid type for {field_name}, expected {expected_type}",
            context=(f"field={field_name}", f"expected={expected_type}"),
        )
    
    @classmethod
    def missing_field(cls, field_name: str) -> ValidationError:
        """Create a missing field validation error."""
        return cls(
            error_type="MISSING_FIELD",
            message=f"Required field missing: {field_name}",
            context=(f"field={field_name}",),
        )
    
    @classmethod
    def invalid_value(cls, field_name: str, value: str) -> ValidationError:
        """Create an invalid value validation error."""
        return cls(
            error_type="INVALID_VALUE",
            message=f"Invalid value for {field_name}: {value}",
            context=(f"field={field_name}", f"value={value}"),
        )
    
    @classmethod
    def immutable_violation(cls, object_id: str) -> ValidationError:
        """Create an immutable modification violation error."""
        return cls(
            error_type="IMMUTABLE_VIOLATION",
            message=f"Attempt to modify immutable object: {object_id}",
            context=(f"object={object_id}",),
            severity="warning",
        )


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating a temporal reward analysis component.
    
    Contains validation status, any errors found, and trace for provenance.
    Does not modify any input data - purely diagnostic.
    """
    
    is_valid: bool
    """Whether all required validations passed."""
    
    errors: Tuple[ValidationError, ...] = field(default_factory=tuple)
    """List of validation errors and warnings."""
    
    trace: ValidationTrace = field(default_factory=ValidationTrace)
    """Sequence of validation events for provenance."""
    
    @classmethod
    def valid(cls) -> ValidationResult:
        """Create a successful validation result."""
        return cls(
            is_valid=True,
            errors=tuple(),
            trace=ValidationTrace(events=("VALIDATION_PASSED",)),
        )
    
    @classmethod
    def with_error(cls, error: ValidationError) -> ValidationResult:
        """Create a failed validation result with a single error."""
        return cls(
            is_valid=False,
            errors=(error,),
            trace=ValidationTrace(events=("VALIDATION_FAILED", error.error_type)),
        )
    
    @classmethod
    def from_errors(cls, errors: Tuple[ValidationError, ...]) -> ValidationResult:
        """Create a failed validation result with multiple errors."""
        return cls(
            is_valid=len(errors) == 0,
            errors=errors,
            trace=ValidationTrace(
                events=("VALIDATION_FAILED",) if errors else ("VALIDATION_PASSED",)
            ),
        )
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
    
    @property
    def error_count(self) -> int:
        """Get count of validation errors."""
        return len(self.errors)


@dataclass(frozen=True)
class RewardDynamicsValidator:
    """
    Validator for Phase 4.10.4 reward dynamics components.
    
    Validates all temporal analysis results ensuring:
        • Semantic consistency
        • Type safety  
        • Immutability preservation
        • Provenance completeness
        
    Does NOT:
        • Modify any input data
        • Make decisions based on validation
        • Learn from validation patterns
    """
    
    @classmethod
    def validate_trajectory(cls, trajectory: RewardTrajectory) -> ValidationResult:
        """Validate a single reward trajectory."""
        trace = ValidationTrace.start().add("VALIDATE_TRAJECTORY")
        
        errors: list[ValidationError] = []
        
        # Validate required fields
        if not trajectory.trajectory_id:
            errors.append(ValidationError.missing_field("trajectory_id"))
        
        if not trajectory.estimate_ref:
            errors.append(ValidationError.missing_field("estimate_ref"))
        
        valid_trajectory_types = {
            "increasing", "decreasing", "stable", "oscillating",
            "plateau", "recovering", "collapsing", "unknown"
        }
        if trajectory.trajectory_type not in valid_trajectory_types:
            errors.append(ValidationError.invalid_value(
                "trajectory_type", trajectory.trajectory_type
            ))
        
        # Validate confidence/uncertainty balance
        total = trajectory.confidence + trajectory.uncertainty
        if abs(total - 1.0) > 0.01:
            errors.append(ValidationError(
                error_type="CONFIDENCE_BALANCE",
                message=f"Confidence ({trajectory.confidence}) + uncertainty ({trajectory.uncertainty}) != 1.0",
                context=("trajectory_id", trajectory.trajectory_id),
            ))
        
        # Validate stability range
        if not (0.0 <= trajectory.stability <= 1.0):
            errors.append(ValidationError(
                error_type="STABILITY_RANGE",
                message=f"Stability ({trajectory.stability}) out of [0, 1] range",
                context=("trajectory_id", trajectory.trajectory_id),
            ))
        
        # Validate volatility range
        if not (0.0 <= trajectory.volatility <= 1.0):
            errors.append(ValidationError(
                error_type="VOLATILITY_RANGE",
                message=f"Volatility ({trajectory.volatility}) out of [0, 1] range",
                context=("trajectory_id", trajectory.trajectory_id),
            ))
        
        trace = trace.add("TRAJECTORY_VALIDATED")
        
        return ValidationResult.from_errors(tuple(errors)).__class__.from_errors(
            errors
        ).__class__(is_valid=len(errors) == 0, errors=tuple(errors), trace=trace)
    
    @classmethod
    def validate_baseline(cls, baseline: AdaptiveRewardBaseline) -> ValidationResult:
        """Validate a single adaptive reward baseline."""
        trace = ValidationTrace.start().add("VALIDATE_BASELINE")
        
        errors: list[ValidationError] = []
        
        # Validate required fields
        if not baseline.baseline_id:
            errors.append(ValidationError.missing_field("baseline_id"))
        
        if not baseline.domain:
            errors.append(ValidationError.missing_field("domain"))
        
        valid_domains = {
            "reward", "effort", "quality", "latency",
            "complexity", "uncertainty"
        }
        if baseline.domain not in valid_domains:
            errors.append(ValidationError.invalid_value(
                "domain", baseline.domain
            ))
        
        # Validate confidence/uncertainty balance
        total = baseline.confidence + baseline.uncertainty
        if abs(total - 1.0) > 0.01:
            errors.append(ValidationError(
                error_type="CONFIDENCE_BALANCE",
                message=f"Confidence ({baseline.confidence}) + uncertainty ({baseline.uncertainty}) != 1.0",
                context=("baseline_id", baseline.baseline_id),
            ))
        
        # Validate adaptation rate range
        if not (0.0 <= baseline.adaptation_rate <= 1.0):
            errors.append(ValidationError(
                error_type="ADAPTATION_RATE_RANGE",
                message=f"Adaptation rate ({baseline.adaptation_rate}) out of [0, 1] range",
                context=("baseline_id", baseline.baseline_id),
            ))
        
        trace = trace.add("BASELINE_VALIDATED")
        
        return ValidationResult.from_errors(tuple(errors)).__class__.from_errors(
            errors
        ).__class__(is_valid=len(errors) == 0, errors=tuple(errors), trace=trace)
    
    @classmethod
    def validate_state(cls, state: TemporalRewardState) -> ValidationResult:
        """Validate a complete temporal reward state."""
        trace = ValidationTrace.start().add("VALIDATE_STATE")
        
        errors: list[ValidationError] = []
        
        # Validate required fields
        if not state.state_id:
            errors.append(ValidationError.missing_field("state_id"))
        
        # Validate trajectory collection consistency
        if state.trajectory_collection and state.trajectories:
            if len(state.trajectories) != state.trajectory_collection.trajectory_count:
                errors.append(ValidationError(
                    error_type="TRAJECTORY_COUNT_MISMATCH",
                    message=f"Trajectory count mismatch: {len(state.trajectories)} vs {state.trajectory_collection.trajectory_count}",
                    context=("state_id", state.state_id),
                ))
        
        # Validate aggregate stability is in valid range
        if not (0.0 <= state.aggregate_stability <= 1.0):
            errors.append(ValidationError(
                error_type="AGGREGATE_STABILITY_RANGE",
                message=f"Aggregate stability ({state.aggregate_stability}) out of [0, 1] range",
                context=("state_id", state.state_id),
            ))
        
        # Validate aggregate volatility is in valid range
        if not (0.0 <= state.aggregate_volatility <= 1.0):
            errors.append(ValidationError(
                error_type="AGGREGATE_VOLATILITY_RANGE",
                message=f"Aggregate volatility ({state.aggregate_volatility}) out of [0, 1] range",
                context=("state_id", state.state_id),
            ))
        
        trace = trace.add("STATE_VALIDATED")
        
        return ValidationResult.from_errors(tuple(errors)).__class__.from_errors(
            errors
        ).__class__(is_valid=len(errors) == 0, errors=tuple(errors), trace=trace)


# Import at end to avoid circular dependencies
from .trajectory import RewardTrajectory, RewardTrajectoryCollection
from .baseline import AdaptiveRewardBaseline
from .state import TemporalRewardState

__all__ = [
    "ValidationTrace",
    "ValidationError",
    "ValidationResult",
    "RewardDynamicsValidator",
]