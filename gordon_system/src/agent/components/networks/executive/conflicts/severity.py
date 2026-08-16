# Executive Conflict Severity Model
# ==================================

"""
Types for assessing the severity of executive conflicts.

Severity measures the potential impact of a conflict on executive
coherence, not its priority or urgency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictSeverityClass:
    """
    Severity classes for executive conflicts.
    """
    
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"
    CRITICAL = "critical"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ExecutiveConflictSeverity:
    """
    Structured assessment of executive conflict severity.
    """
    
    severity_class: str
    objective_impact_class: str = "unknown"
    commitment_impact_class: str = "unknown"
    policy_impact_class: str = "unknown"
    security_impact_class: str = "unknown"
    decision_impact_class: str = "unknown"
    action_impact_class: str = "unknown"
    recovery_impact_class: str = "unknown"
    scope_expansion_risk_class: str = "low"
    reversibility_class: str = "reversible"
    consequence_magnitude_class: str = "unknown"

    @property
    def is_high_severity(self) -> bool:
        return self.severity_class in (
            ExecutiveConflictSeverityClass.MAJOR,
            ExecutiveConflictSeverityClass.SEVERE,
            ExecutiveConflictSeverityClass.CRITICAL,
            ExecutiveConflictSeverityClass.BLOCKING,
        )

    @classmethod
    def blocking(cls) -> "ExecutiveConflictSeverity":
        return cls(
            severity_class=ExecutiveConflictSeverityClass.BLOCKING,
            objective_impact_class="critical",
            commitment_impact_class="critical",
            policy_impact_class="high",
            decision_impact_class="critical",
            action_impact_class="critical",
            recovery_impact_class="high",
            scope_expansion_risk_class="high",
            reversibility_class="irreversible",
        )


__all__: Tuple[str, ...] = (
    "ExecutiveConflictSeverityClass",
    "ExecutiveConflictSeverity",
)