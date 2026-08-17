# Semantic Health - Phase 7.10
# ============================

"""
Canonical Semantic Health metrics.

Health metrics include:
    - Concepts analyzed
    - Relations inferred
    - Inheritance depth
    - Ontology consistency
    - Composition success
    - Validation success
    - Diagnostics

Health remains descriptive.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SemanticHealth:
    """
    Semantic health metrics record.
    
    A SemanticHealth contains:
        - Health identity
        - Metrics (descriptive only)
        - Diagnostics
        - Timestamps
    
    Health remains descriptive - it does not modify artifacts.
    """
    
    # Identity
    health_id: str                          # Unique identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was assessed?
    
    # Metrics
    concepts_analyzed: int = 0
    relations_inferred: int = 0
    max_inheritance_depth: int = 0
    ontology_consistency_count: int = 0
    composition_success_count: int = 0
    validation_success_count: int = 0
    validation_failure_count: int = 0
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    state: str = "assessing"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def validation_rate(self) -> float:
        """Calculate validation success rate."""
        total = self.validation_success_count + self.validation_failure_count
        if total == 0:
            return 1.0
        return self.validation_success_count / total
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
    ) -> SemanticHealth:
        """Create a new semantic health record."""
        return cls(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
        )
    
    def increment_concepts(self, count: int = 1) -> SemanticHealth:
        """Increment concepts analyzed."""
        return dataclass_replace(
            self,
            concepts_analyzed=self.concepts_analyzed + count,
        )
    
    def increment_relations(self, count: int = 1) -> SemanticHealth:
        """Increment relations inferred."""
        return dataclass_replace(
            self,
            relations_inferred=self.relations_inferred + count,
        )
    
    def record_inheritance_depth(self, depth: int) -> SemanticHealth:
        """Record a new inheritance depth."""
        new_max = max(self.max_inheritance_depth, depth)
        return dataclass_replace(
            self,
            max_inheritance_depth=new_max,
        )
    
    def record_validation(self, passed: bool) -> SemanticHealth:
        """Record validation result."""
        if passed:
            return dataclass_replace(
                self,
                validation_success_count=self.validation_success_count + 1,
            )
        else:
            return dataclass_replace(
                self,
                validation_failure_count=self.validation_failure_count + 1,
            )
    
    def complete(self) -> SemanticHealth:
        """Mark health as completed."""
        return dataclass_replace(
            self,
            state="completed",
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from health assessment.
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
    "SemanticHealth",
    "DiagnosticsRecord",
]