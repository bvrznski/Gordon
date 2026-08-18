# Experimental Reasoning - Failure Handling
# =========================================

"""
Canonical Failure contracts.

Failures identify problems with experiment designs and recovery options.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class FailureKind(Enum):
    """Categories of experimental failures."""
    
    UNSAFE_INTERVENTION = "unsafe_intervention"          # Intervention poses safety risks
    UNOBSERVABLE_VARIABLES = "unobservable_variables"    # Variables cannot be measured
    RESOURCE_EXHAUSTION = "resource_exhaustion"          # Insufficient resources
    MEASUREMENT_AMBIGUITY = "measurement Ambiguity"      # Measurements unclear or ambiguous
    INVALID_CONTROLS = "invalid_controls"                # Controls not properly defined
    HYPOTHESIS_INCOHERENT = "hypothesis_incoherent"      # Hypotheses are inconsistent
    DESIGN_IMPOSSIBLE = "design_impossible"              # Design cannot be realized


@dataclass(frozen=True)
class RecoveryOption(Enum):
    """Recovery options for handling failures."""
    
    MODIFY_DESIGN = "modify_design"                      # Modify the experiment design
    SKIP_EXPERIMENT = "skip_experiment"                  # Skip this experiment
    USE_ALTERNATIVE = "use_alternative"                  # Use an alternative experiment
    ADDITIONAL_DATA = "additional_data"                  # Gather more data first
    MANUAL_REVIEW = "manual_review"                      # Require manual review


@dataclass(frozen=True)
class ExperimentalFailure:
    """
    A failure in experimental design.
    
    Failures include:
        - Type of failure
        - Diagnostics (what went wrong)
        - Recovery options
    
    Failures remain explicit and never silently discard experiment designs.
    """
    
    # Identity
    failure_id: str                             # Unique identifier
    
    # Failure details
    kind: FailureKind                           # What kind of failure?
    experiment_identity: str                    # Which experiment failed?
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()           # Detailed diagnostic information
    error_message: str = ""                     # Human-readable error message
    
    # Recovery options
    recovery_options: Tuple[RecoveryOption, ...] = field(
        default_factory=lambda: (RecoveryOption.MODIFY_DESIGN,)
    )
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    origin_context: str = "unknown"
    
    @property
    def is_recoverable(self) -> bool:
        """Check if this failure has recovery options."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        kind: FailureKind,
        experiment_identity: str,
        diagnostics: List[str] = None,
        error_message: str = "",
        recovery_options: List[RecoveryOption] = None,
        origin_context: str = "unknown",
    ) -> ExperimentalFailure:
        """Create a new experimental failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            kind=kind,
            experiment_identity=experiment_identity,
            diagnostics=tuple(diagnostics or []),
            error_message=error_message,
            recovery_options=tuple(recovery_options or [RecoveryOption.MODIFY_DESIGN]),
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class FailureReport:
    """
    Complete failure report for an experiment design.
    
    Includes all failures found and their diagnostics.
    """
    
    # Identity
    report_id: str                              # Unique identifier
    
    # Experiment info
    experiment_identity: str                    # Failed experiment
    failure_timestamp_utc: float = field(default_factory=time.time)
    
    # Failure details
    total_failures: int = 0                     # Total number of failures
    failures_by_kind: Dict[str, int] = field(default_factory=dict)  # Count by kind
    
    @classmethod
    def create(
        cls,
        experiment_identity: str,
        failures: List[ExperimentalFailure] = None,
    ) -> FailureReport:
        """Create a new failure report."""
        failures_by_kind = {}
        for f in (failures or []):
            kind_str = f.kind.value
            failures_by_kind[kind_str] = failures_by_kind.get(kind_str, 0) + 1
        
        return cls(
            report_id=f"failure_report:{uuid.uuid4().hex[:16]}",
            experiment_identity=experiment_identity,
            total_failures=len(failures or []),
            failures_by_kind=failures_by_kind,
        )


__all__ = [
    "FailureKind",
    "RecoveryOption",
    "ExperimentalFailure",
    "FailureReport",
]