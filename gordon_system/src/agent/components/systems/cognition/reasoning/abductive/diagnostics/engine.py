# Abduction Diagnostic Engine - Phase 7.3
# ======================================

"""
Diagnostic reasoning engine for abductive explanation.

This provides:
    - Diagnostic session management
    - Failure mode identification
    - Root cause analysis
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DiagnosticMode(Enum):
    """Modes of diagnostic reasoning."""
    
    FAILURE_ANALYSIS = "failure_analysis"     # Identify failure causes
    PERFORMANCE_ISSUE = "performance_issue"   # Analyze performance problems
    BEHAVIORAL_INCONSISTENCY = "behavioral_inconsistency"  # Find behavioral mismatches
    CONFIGURATION_ERROR = "configuration_error"  # Diagnose config issues
    INTEGRATION_FAILURE = "integration_failure"  # Diagnose integration problems


class DiagnosticLifecycle(Enum):
    """Diagnostic session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVATION_COLLECTION = "observation_collection"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    CAUSAL_ANALYSIS = "causal_analysis"
    ROOT_CAUSE_IDENTIFICATION = "root_cause_identification"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DiagnosticSessionIdentity:
    """
    Immutable identity for a diagnostic session.
    
    Allows replay and verification of diagnostic results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> DiagnosticSessionIdentity:
        """Create a new diagnostic session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


@dataclass(frozen=True)
class CandidateCause:
    """
    A candidate cause in diagnostic reasoning.
    
    Each candidate represents a potential root cause of observed symptoms.
    """
    
    # Identity
    cause_id: str                             # Unique identifier
    
    # Description
    cause_description: str                    # What is the potential cause?
    effect_observed: str                      # What effect is being caused?
    
    # Assessment
    plausibility: float = 0.5                 # How plausible is this cause?
    frequency: float = 1.0                    # How often does this occur?
    detectability: float = 0.5                # How easy to detect?
    
    # Context
    context_tags: Tuple[str, ...] = ()        # Context for filtering
    
    @property
    def diagnostic_score(self) -> float:
        """Calculate diagnostic priority score."""
        return self.plausibility * self.frequency * self.detectability
    
    @classmethod
    def create(
        cls,
        cause_description: str,
        effect_observed: str,
        plausibility: float = 0.5,
        frequency: float = 1.0,
        detectability: float = 0.5,
        context_tags: Optional[List[str]] = None,
    ) -> CandidateCause:
        """Create a new candidate cause."""
        return cls(
            cause_id=f"cause:{uuid.uuid4().hex[:16]}",
            cause_description=cause_description,
            effect_observed=effect_observed,
            plausibility=plausibility,
            frequency=frequency,
            detectability=detectability,
            context_tags=tuple(context_tags or []),
        )


@dataclass(frozen=True)
class FailureMode:
    """
    A failure mode in diagnostic reasoning.
    
    Failure modes represent patterns of failure that can occur in a system.
    """
    
    # Identity
    failure_mode_id: str                      # Unique identifier
    
    # Description
    failure_name: str                         # Human-readable name
    failure_description: str                  # Detailed description
    
    # Trigger conditions
    trigger_conditions: Tuple[str, ...] = ()  # When does this fail?
    observable_symptoms: Tuple[str, ...] = () # What indicates this failure?
    
    # Impact assessment
    severity: float = 1.0                     # Severity when it occurs
    impact_scope: str = "single_component"    # How wide is the impact?
    
    @classmethod
    def create(
        cls,
        failure_name: str,
        failure_description: str,
        trigger_conditions: Optional[List[str]] = None,
        observable_symptoms: Optional[List[str]] = None,
        severity: float = 1.0,
        impact_scope: str = "single_component",
    ) -> FailureMode:
        """Create a new failure mode."""
        return cls(
            failure_mode_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_name=failure_name,
            failure_description=failure_description,
            trigger_conditions=tuple(trigger_conditions or []),
            observable_symptoms=tuple(observable_symptoms or []),
            severity=severity,
            impact_scope=impact_scope,
        )


@dataclass(frozen=True)
class FailureModeAnalysis:
    """
    Analysis of which failure modes apply to current observations.
    
    This provides:
        - Matched failure modes
        - Confidence in each match
        - Missing diagnostics needed
    """
    
    # Identity
    analysis_id: str                          # Unique identifier
    
    # Results
    matched_failure_modes: Tuple[Dict[str, Any], ...]  # Modes that fit observations
    confidence_per_mode: Dict[str, float] = field(default_factory=dict)  # mode_id -> confidence
    
    # Diagnostic gaps
    missing_diagnostics: Tuple[str, ...] = ()  # What else should we check?
    
    @property
    def best_matched_failure_mode(self) -> Optional[Dict[str, Any]]:
        """Get the failure mode with highest confidence."""
        if not self.confidence_per_mode:
            return None
        
        best_id = max(self.confidence_per_mode.keys(), key=lambda k: self.confidence_per_mode[k])
        for fm in self.matched_failure_modes:
            if fm.get("failure_mode_id") == best_id:
                return fm
        return None
    
    @classmethod
    def create(
        cls,
        matched_failure_modes: List[Dict[str, Any]],
        confidence_mapping: Dict[str, float],
        missing_diagnostics: Optional[List[str]] = None,
    ) -> FailureModeAnalysis:
        """Create a new failure mode analysis."""
        return cls(
            analysis_id=f"analysis:{uuid.uuid4().hex[:16]}",
            matched_failure_modes=tuple(matched_failure_modes),
            confidence_per_mode=confidence_mapping,
            missing_diagnostics=tuple(missing_diagnostics or []),
        )


@dataclass(frozen=True)
class DiagnosticReasoning:
    """
    Complete diagnostic reasoning session.
    
    This record contains:
        - Session identity and metadata
        - All observations (symptoms)
        - Candidate causes with scores
        - Preferred explanation
        - Validation status
    
    Diagnostic results remain revisable as new evidence arrives.
    """
    
    # Identity
    diagnostic_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Session info
    diagnostic_mode: DiagnosticMode           # What kind of diagnosis?
    reasoning_goal: str                       # What are we diagnosing?
    
    # Results
    observations: Tuple[Dict[str, Any], ...]  # All observed symptoms
    candidate_causes: Tuple[CandidateCause, ...] = ()  # Potential causes
    preferred_cause_id: Optional[str] = None           # Best explanation
    
    # Assessment
    diagnostic_confidence: float = 0.5        # Overall confidence in diagnosis
    diagnostic_completeness: float = 0.5      # How complete is the analysis?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    lifecycle_state: DiagnosticLifecycle = DiagnosticLifecycle.CREATED
    
    @property
    def candidate_count(self) -> int:
        """Number of candidate causes."""
        return len(self.candidate_causes)
    
    @classmethod
    def create(
        cls,
        observations: List[Dict[str, Any]],
        reasoning_goal: str,
        diagnostic_mode: DiagnosticMode = DiagnosticMode.FAILURE_ANALYSIS,
        candidate_causes: Optional[List[CandidateCause]] = None,
    ) -> DiagnosticReasoning:
        """Create a new diagnostic reasoning record."""
        causes = tuple(candidate_causes or [])
        
        # Calculate preferred cause (highest diagnostic score)
        preferred_id = None
        if causes:
            best_cause = max(causes, key=lambda c: c.diagnostic_score)
            preferred_id = best_cause.cause_id
        
        return cls(
            diagnostic_id=f"diagnostic:{uuid.uuid4().hex[:16]}",
            semantic_identity=reasoning_goal,
            diagnostic_mode=diagnostic_mode,
            reasoning_goal=reasoning_goal,
            observations=tuple(observations),
            candidate_causes=causes,
            preferred_cause_id=preferred_id,
            lifecycle_state=DiagnosticLifecycle.COMPLETED,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticReasoning",
    "DiagnosticSessionIdentity",
    "DiagnosticMode",
    "DiagnosticLifecycle",
    "CandidateCause",
    "FailureMode",
    "FailureModeAnalysis",
]