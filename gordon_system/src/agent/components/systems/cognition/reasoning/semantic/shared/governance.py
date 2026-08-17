# Semantic Governance - Phase 7.10
# =================================

"""
Canonical Semantic Governance contracts.

Semantic governance evaluates:
    - Ontology consistency
    - Concept integrity
    - Relation correctness
    - Inheritance validity
    - Semantic coherence
    - Diagnostics

Governance remains observational - it does NOT modify semantic artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SemanticGovernance:
    """
    Semantic governance evaluation result.
    
    A SemanticGovernance contains:
        - Governance identity
        - Evaluated sessions
        - Findings
        - Violations
        - Recommendations
        - Provenance tracking
    
    Governance remains observational - it never modifies artifacts directly.
    """
    
    # Identity
    governance_id: str                      # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was governed?
    
    # Evaluated semantic sessions
    evaluated_sessions: Tuple[str, ...] = ()
    
    # Findings
    findings: Dict[str, Any] = field(default_factory=dict)
    
    # Violations
    violations: Tuple[GovernanceViolation, ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    state: str = "evaluating"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def session_count(self) -> int:
        """Count of evaluated sessions."""
        return len(self.evaluated_sessions)
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        sessions: Optional[List[str]] = None,
    ) -> SemanticGovernance:
        """Create a new semantic governance record."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            evaluated_sessions=tuple(sessions or []),
        )
    
    def add_findings(self, findings: Dict[str, Any]) -> SemanticGovernance:
        """Add governance findings."""
        new_findings = dict(self.findings)
        new_findings.update(findings)
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def add_violations(self, violations: List[GovernanceViolation]) -> SemanticGovernance:
        """Add governance violations."""
        new_violations = tuple(self.violations) + tuple(violations)
        return dataclass_replace(
            self,
            violations=new_violations,
        )
    
    def complete(self) -> SemanticGovernance:
        """Mark governance as completed."""
        return dataclass_replace(
            self,
            state="completed",
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class GovernanceViolation:
    """
    A governance violation found during semantic evaluation.
    """
    
    violation_id: str                       # Unique identifier
    violation_type: str                     # e.g., "inconsistent", "undeterministic"
    message: str                            # Violation description
    
    @classmethod
    def create_ontology_inconsistency(cls, details: str) -> GovernanceViolation:
        """Create an ontology inconsistency violation."""
        return cls(
            violation_id=f"violation:{uuid.uuid4().hex[:16]}",
            violation_type="ontology_inconsistent",
            message=f"Ontology inconsistency: {details}",
        )
    
    @classmethod
    def create_undeterministic(cls, details: str) -> GovernanceViolation:
        """Create an undeterminism violation."""
        return cls(
            violation_id=f"violation:{uuid.uuid4().hex[:16]}",
            violation_type="undeterministic",
            message=f"Nondeterministic inference: {details}",
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from governance evaluation.
    """
    
    diagnostic_id: str                      # Unique identifier
    diagnostic_type: str                    # e.g., "checked", "skipped"
    message: str                            # Diagnostic message
    severity: str = "info"                  # info, warning, error
    
    @classmethod
    def info(cls, message: str) -> DiagnosticsRecord:
        """Create an info diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="info",
            message=message,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SemanticGovernance",
    "GovernanceViolation",
    "DiagnosticsRecord",
]