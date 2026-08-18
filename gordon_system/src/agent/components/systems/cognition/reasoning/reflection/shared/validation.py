# Validation - Phase 7.28
# ======================

"""
Validation observes reflection quality and correctness.

Validation evaluates:
    - Reflection quality (is it good?)
    - Causal validity (are explanations valid?)
    - Lesson quality (are lessons justified?)
    - Consolidation consistency (do proposals make sense?)

Validation remains observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ReflectionValidation:
    """
    Validation result for reflection analysis.
    
    A validation contains:
        - Explicit identity
        - Evaluated sessions and results
        - Findings (issues found)
        - Violations (law violations)
        - Recommendations
        - Provenance tracking
    
    Validations remain independently inspectable.
    """
    
    # Identity
    validation_id: str                        # Unique validation identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Evaluated items
    evaluated_reflections: List[str]          # Reflection IDs validated
    
    # Findings
    findings: Dict[str, Any]                  # What was found?
    
    # Violations (for governance)
    violations: List[Dict[str, Any]] = field(default_factory=list)  # Rule violations
    
    # Quality metrics
    quality_score: float = 0.0                # Overall quality score
    causal_validity_score: float = 0.0        # Causal validity score
    lesson_quality_score: float = 0.0         # Lesson quality score
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    validation_method: str = "observational"   # How was it validated?
    source_context: str = "unknown"            # Where validation originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_reflections: List[str],
        findings: Dict[str, Any],
        validation_method: str = "observational",
        source_context: str = "unknown",
    ) -> ReflectionValidation:
        """Create a new reflection validation."""
        return cls(
            validation_id=f"validation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_reflections=evaluated_reflections,
            findings=findings,
            validation_method=validation_method,
            source_context=source_context,
        )


@dataclass(frozen=True)
class ReflectionFailure:
    """
    Failure information for reflection sessions.
    
    A failure contains:
        - Explicit identity
        - Failure kind (insufficient evidence, conflict, ambiguity)
        - Diagnostics
        - Recovery options
        - Provenance tracking
    
    Failures remain explicit and inspectable.
    """
    
    # Identity
    failure_id: str                           # Unique failure identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Failure classification
    failure_kind: str = ""                    # kind of failure
    failure_location: str = ""                # Where did it occur?
    
    # Diagnostics
    diagnostics: Dict[str, Any]               # Detailed diagnostics
    root_cause: str = ""                      # Root cause analysis
    
    # Recovery options
    recovery_options: List[Dict[str, Any]] = field(default_factory=list)  # How to recover?
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_context: str = "unknown"           # Where failure occurred
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        failure_kind: str,
        diagnostics: Dict[str, Any],
        recovery_options: Optional[List[Dict[str, Any]]] = None,
        source_context: str = "unknown",
    ) -> ReflectionFailure:
        """Create a new reflection failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            failure_kind=failure_kind,
            diagnostics=diagnostics,
            recovery_options=recovery_options or [],
            source_context=source_context,
        )


@dataclass(frozen=True)
class ReflectionGovernance:
    """
    Governance evaluation of reflection analysis.
    
    A governance object contains:
        - Evaluated sessions
        - Findings (quality, validity issues)
        - Violations (law violations detected)
        - Recommendations
        - Provenance tracking
    
    Governance remains observational (does not modify reflections).
    """
    
    # Identity
    governance_id: str                        # Unique governance identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Evaluated items
    evaluated_sessions: List[str]             # Session IDs evaluated
    
    # Findings
    findings: Dict[str, Any]                  # What was found?
    
    # Violations detected
    violations: List[Dict[str, Any]] = field(default_factory=list)  # Law violations
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = field(default_factory=list)  # How to improve?
    
    # Quality metrics
    governance_score: float = 0.0             # Governance quality score
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    evaluation_method: str = "observational"   # How was it evaluated?
    source_context: str = "unknown"            # Where governance originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_sessions: List[str],
        findings: Dict[str, Any],
        evaluation_method: str = "observational",
        source_context: str = "unknown",
    ) -> ReflectionGovernance:
        """Create a new reflection governance evaluation."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_sessions=evaluated_sessions,
            findings=findings,
            evaluation_method=evaluation_method,
            source_context=source_context,
        )


__all__ = [
    "ReflectionValidation",
    "ReflectionFailure",
    "ReflectionGovernance",
]