# Semantic Consistency - Phase 7.10
# ==================================

"""
Canonical Semantic Consistency contracts.

Semantic consistency evaluates:
    - Ontology correctness
    - Relation consistency
    - Inheritance correctness
    - Constraint preservation
    - Concept integrity

Consistency remains observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SemanticConsistency:
    """
    Semantic consistency evaluation result.
    
    A SemanticConsistency contains:
        - Consistency identity
        - Evaluated concepts
        - Findings
        - Violations
        - Provenance tracking
    """
    
    # Identity
    consistency_id: str                     # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was evaluated?
    
    # Evaluated concepts
    evaluated_concepts: Tuple[str, ...] = ()
    
    # Findings
    findings: Dict[str, bool] = field(default_factory=dict)
    
    # Violations
    violations: Tuple[ConsistencyViolation, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    state: str = "created"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def concept_count(self) -> int:
        """Count of evaluated concepts."""
        return len(self.evaluated_concepts)
    
    @property
    def violation_count(self) -> int:
        """Count of violations found."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        concepts: Optional[List[str]] = None,
    ) -> SemanticConsistency:
        """Create a new consistency evaluation record."""
        return cls(
            consistency_id=f"consistency:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            evaluated_concepts=tuple(concepts or []),
        )
    
    def add_findings(self, findings: Dict[str, bool]) -> SemanticConsistency:
        """Add consistency findings."""
        new_findings = dict(self.findings)
        new_findings.update(findings)
        return dataclass_replace(
            self,
            findings=new_findings,
        )
    
    def add_violations(self, violations: List[ConsistencyViolation]) -> SemanticConsistency:
        """Add consistency violations."""
        new_violations = tuple(self.violations) + tuple(violations)
        return dataclass_replace(
            self,
            violations=new_violations,
        )


@dataclass(frozen=True)
class ConsistencyViolation:
    """
    A consistency violation found during semantic evaluation.
    
    Violations include:
        - Ontology inconsistency
        - Relation conflict
        - Inheritance error
        - Constraint violation
    """
    
    violation_id: str                       # Unique identifier
    violation_type: str                     # e.g., "ontology_conflict", "relation_cycle"
    message: str                            # Description of the violation
    affected_concepts: Tuple[str, ...] = ()  # Concepts involved
    
    @classmethod
    def create_ontology_conflict(cls, concepts: List[str], details: str) -> ConsistencyViolation:
        """Create an ontology conflict violation."""
        return cls(
            violation_id=f"violation:{uuid.uuid4().hex[:16]}",
            violation_type="ontology_conflict",
            message=f"Ontology conflict: {details}",
            affected_concepts=tuple(concepts),
        )
    
    @classmethod
    def create_cycle(cls, concepts: List[str]) -> ConsistencyViolation:
        """Create a cycle in the hierarchy."""
        return cls(
            violation_id=f"violation:{uuid.uuid4().hex[:16]}",
            violation_type="hierarchy_cycle",
            message=f"Circular inheritance detected: {' -> '.join(concepts)}",
            affected_concepts=tuple(concepts),
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from consistency evaluation.
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
    
    @classmethod
    def warning(cls, message: str) -> DiagnosticsRecord:
        """Create a warning diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="warning",
            message=message,
            severity="warning",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SemanticConsistency",
    "ConsistencyViolation",
    "DiagnosticsRecord",
]