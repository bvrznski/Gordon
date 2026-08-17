# Abduction Failure Modes - Phase 7.3
# ===================================

"""
Failure mode identification for diagnostic reasoning.

This module provides:
    - Failure mode definitions
    - Failure analysis utilities
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class FailureMode:
    """
    A failure mode - a pattern of how a system component can fail.
    
    Each failure mode has:
        - Distinctive symptoms (what we observe when it fails)
        - Trigger conditions (when it typically occurs)
        - Impact assessment (how bad is it?)
    """
    
    # Identity
    failure_mode_id: str                      # Unique identifier
    
    # Description
    name: str                                 # Human-readable name
    description: str                          # Detailed description
    
    # Characteristics
    trigger_conditions: Tuple[str, ...] = ()  # When does this fail?
    observable_symptoms: Tuple[str, ...] = () # What indicates failure?
    
    # Assessment
    severity: float = 1.0                     # Severity when it occurs (0-1)
    likelihood: float = 0.5                   # How likely is this failure?
    detectability: float = 0.5                # How easy to detect?
    
    @property
    def risk_priority(self) -> float:
        """Calculate RPN (Risk Priority Number)."""
        return self.severity * self.likelihood * self.detectability
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        trigger_conditions: Optional[List[str]] = None,
        observable_symptoms: Optional[List[str]] = None,
        severity: float = 1.0,
        likelihood: float = 0.5,
        detectability: float = 0.5,
    ) -> FailureMode:
        """Create a new failure mode."""
        return cls(
            failure_mode_id=f"failure:{uuid.uuid4().hex[:16]}",
            name=name,
            description=description,
            trigger_conditions=tuple(trigger_conditions or []),
            observable_symptoms=tuple(observable_symptoms or []),
            severity=severity,
            likelihood=likelihood,
            detectability=detectability,
        )


@dataclass(frozen=True)
class CandidateCause:
    """
    A candidate cause - a potential root cause of observed symptoms.
    
    Each candidate represents a specific instance of a failure mode
    being applied to the current situation.
    """
    
    # Identity
    cause_id: str                             # Unique identifier
    
    # Description
    cause_description: str                    # What is the potential cause?
    effect_observed: str                      # What effect are we seeing?
    
    # Assessment
    plausibility: float = 0.5                 # How plausible is this cause?
    frequency: float = 1.0                    # How often does this occur?
    detectability: float = 0.5                # How easy to detect?
    
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
    ) -> CandidateCause:
        """Create a new candidate cause."""
        return cls(
            cause_id=f"cause:{uuid.uuid4().hex[:16]}",
            cause_description=cause_description,
            effect_observed=effect_observed,
            plausibility=plausibility,
            frequency=frequency,
            detectability=detectability,
        )


@dataclass(frozen=True)
class FailureModeAnalysis:
    """
    Analysis of which failure modes apply to current observations.
    
    This provides:
        - Matched failure modes with confidence
        - Missing diagnostics needed
        - Recommended investigations
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
    
    @property
    def has_confident_match(self) -> bool:
        """Check if any failure mode has high confidence."""
        return any(c >= 0.8 for c in self.confidence_per_mode.values())
    
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
    diagnostic_mode: str                      # What kind of diagnosis?
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
    lifecycle_state: str = "completed"        # Session state
    
    @property
    def candidate_count(self) -> int:
        """Number of candidate causes."""
        return len(self.candidate_causes)
    
    @classmethod
    def create(
        cls,
        observations: List[Dict[str, Any]],
        reasoning_goal: str,
        diagnostic_mode: str = "failure_analysis",
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
            lifecycle_state="completed",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "FailureMode",
    "CandidateCause",
    "FailureModeAnalysis",
    "DiagnosticReasoning",
]