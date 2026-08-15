# Focusing Network Output Contracts
# ==================================

"""
Output contracts for the FocusingNetwork Phase 4.2.8.

These define stable interfaces for consuming focus assessments and other outputs
without exposing implementation details of how they were computed.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional
from datetime import datetime


# =============================================================================
# FOCUS ASSESSMENT CONSUMER - Primary assessment output
# =============================================================================

@dataclass(frozen=True)
class FocusAssessmentConsumer:
    """
    Consumer of focus assessment outputs.
    
    Receives completed focus assessments from the FocusingNetwork. The Network
    computes and delivers assessments, but the consumer decides what to do with them.
    
    PROPERTIES:
        • Observational - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of assessment processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"focus_assessment_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Assessment processing
    assessments_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received assessment dictionaries (results only)."""
    
    last_assessment_utc: Optional[datetime] = None
    """When the last assessment was received."""
    
    process_count: int = 0
    """Total number of assessments processed."""
    
    def receive_assessment(self, assessment: Dict[str, Any]) -> None:
        """
        Receive a focus assessment.
        
        Args:
            assessment: Assessment dictionary with all computed values
        """
        object.__setattr__(
            self,
            "assessments_received",
            self.assessments_received + (assessment,)
        )
        now = datetime.utcnow()
        if self.last_assessment_utc is None:
            object.__setattr__(self, "last_assessment_utc", now)
    
    def get_confirmed_targets(self, assessment_id: str) -> Tuple[str, ...]:
        """
        Get confirmed focus targets from an assessment.
        
        Args:
            assessment_id: The assessment to query
            
        Returns:
            Tuple of target IDs confirmed by the consumer
        """
        for assessment in self.assessments_received:
            if assessment.get("assessment_id") == assessment_id:
                return tuple(assessment.get("confirmed_targets", ()))
        return tuple()
    
    def get_rejected_targets(self, assessment_id: str) -> Tuple[str, ...]:
        """
        Get rejected focus targets from an assessment.
        
        Args:
            assessment_id: The assessment to query
            
        Returns:
            Tuple of target IDs rejected by the consumer
        """
        for assessment in self.assessments_received:
            if assessment.get("assessment_id") == assessment_id:
                return tuple(assessment.get("rejected_targets", ()))
        return tuple()


# =============================================================================
# PRIORITY ASSESSMENT CONSUMER - Priority assessment output
# =============================================================================

@dataclass(frozen=True)
class PriorityAssessmentConsumer:
    """
    Consumer of priority assessment outputs.
    
    Receives priority assessments from the FocusingNetwork. Only observes results,
    never how priorities were computed.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of assessment processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"priority_assessment_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Assessment data
    assessments_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received priority assessment dictionaries."""
    
    def receive_priority_assessment(self, assessment: Dict[str, Any]) -> None:
        """
        Receive a priority assessment.
        
        Args:
            assessment: Priority assessment dictionary
        """
        object.__setattr__(
            self,
            "assessments_received",
            self.assessments_received + (assessment,)
        )


# =============================================================================
# COMPETITION ASSESSMENT CONSUMER - Competition assessment output
# =============================================================================

@dataclass(frozen=True)
class CompetitionAssessmentConsumer:
    """
    Consumer of competition assessment outputs.
    
    Receives competition assessments from the FocusingNetwork. Only observes results,
    never how competitions were analyzed.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of assessment processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"competition_assessment_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Assessment data
    assessments_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received competition assessment dictionaries."""
    
    def receive_competition_assessment(self, assessment: Dict[str, Any]) -> None:
        """
        Receive a competition assessment.
        
        Args:
            assessment: Competition assessment dictionary
        """
        object.__setattr__(
            self,
            "assessments_received",
            self.assessments_received + (assessment,)
        )


# =============================================================================
# PRECISION ASSESSMENT CONSUMER - Precision assessment output
# =============================================================================

@dataclass(frozen=True)
class PrecisionAssessmentConsumer:
    """
    Consumer of precision assessment outputs.
    
    Receives precision assessments from the FocusingNetwork. Only observes results,
    never how precisions were estimated.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of assessment processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"precision_assessment_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Assessment data
    assessments_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received precision assessment dictionaries."""
    
    def receive_precision_assessment(self, assessment: Dict[str, Any]) -> None:
        """
        Receive a precision assessment.
        
        Args:
            assessment: Precision assessment dictionary
        """
        object.__setattr__(
            self,
            "assessments_received",
            self.assessments_received + (assessment,)
        )


# =============================================================================
# PERSISTENCE ASSESSMENT CONSUMER - Persistence assessment output
# =============================================================================

@dataclass(frozen=True)
class PersistenceAssessmentConsumer:
    """
    Consumer of persistence assessment outputs.
    
    Receives persistence assessments from the FocusingNetwork. Only observes results,
    never how persistence was computed.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of assessment processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"persistence_assessment_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Assessment data
    assessments_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received persistence assessment dictionaries."""
    
    def receive_persistence_assessment(self, assessment: Dict[str, Any]) -> None:
        """
        Receive a persistence assessment.
        
        Args:
            assessment: Persistence assessment dictionary
        """
        object.__setattr__(
            self,
            "assessments_received",
            self.assessments_received + (assessment,)
        )


# =============================================================================
# ALLOCATION RECOMMENDATION CONSUMER - Allocation recommendation output
# =============================================================================

@dataclass(frozen=True)
class AllocationRecommendationConsumer:
    """
    Consumer of resource allocation recommendations.
    
    Receives allocation recommendations from the FocusingNetwork. Only observes
    results, never how allocations were computed.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of recommendation processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"allocation_recommendation_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Recommendation data
    recommendations_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received allocation recommendation dictionaries."""
    
    def receive_allocation_recommendation(self, recommendation: Dict[str, Any]) -> None:
        """
        Receive an allocation recommendation.
        
        Args:
            recommendation: Allocation recommendation dictionary
        """
        object.__setattr__(
            self,
            "recommendations_received",
            self.recommendations_received + (recommendation,)
        )


# =============================================================================
# BIAS ASSESSMENT CONSUMER - Bias assessment output
# =============================================================================

@dataclass(frozen=True)
class BiasAssessmentConsumer:
    """
    Consumer of bias assessment outputs.
    
    Receives bias assessments from the FocusingNetwork. Only observes results,
    never how biases were generated.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of assessment processing
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"bias_assessment_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Assessment data
    assessments_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received bias assessment dictionaries."""
    
    def receive_bias_assessment(self, assessment: Dict[str, Any]) -> None:
        """
        Receive a bias assessment.
        
        Args:
            assessment: Bias assessment dictionary
        """
        object.__setattr__(
            self,
            "assessments_received",
            self.assessments_received + (assessment,)
        )


# =============================================================================
# DIAGNOSTICS CONSUMER - Diagnostics output consumer
# =============================================================================

@dataclass(frozen=True)
class DiagnosticsConsumer:
    """
    Consumer of diagnostics outputs from the FocusingNetwork.
    
    Receives all diagnostic information without exposing implementation details
    of how diagnostics are generated.
    
    PROPERTIES:
        • Observational only - no computation responsibility
        • Versioned for compatibility tracking
        • External ownership of diagnostics storage
    """
    
    # Consumer identity
    consumer_id: str = field(default_factory=lambda: f"diagnostics_{id(datetime.utcnow()):x}")
    """Unique identifier for this consumer."""
    
    # Diagnostic data types
    trace_events_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received trace event dictionaries."""
    
    metric_events_received: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Received metric event dictionaries."""
    
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    """Performance metrics (duration_ms, event_count, etc.)."""
    
    def receive_trace_event(self, trace: Dict[str, Any]) -> None:
        """
        Receive a trace event.
        
        Args:
            trace: Trace event dictionary
        """
        object.__setattr__(
            self,
            "trace_events_received",
            self.trace_events_received + (trace,)
        )
    
    def receive_metric_event(self, metric: Dict[str, Any]) -> None:
        """
        Receive a metric event.
        
        Args:
            metric: Metric event dictionary
        """
        object.__setattr__(
            self,
            "metric_events_received",
            self.metric_events_received + (metric,)
        )


# =============================================================================
# EXTERNAL INTERFACES - Protocol definitions for external systems
# =============================================================================

try:
    from typing import Protocol, runtime_checkable
except ImportError:
    from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FocusOutputConsumer(Protocol):
    """
    Protocol for consuming FocusingNetwork outputs.
    
    Allows external systems to receive assessments without coupling to the
    FocusingNetwork implementation. The Network delivers outputs but never
    decides what happens next.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new assessment types via enum)
    
    OWNERSHIP:
        - Network owns computation only
        - Consumer owns received outputs
        - No shared state or references after delivery
    
    USE BY:
        - FocusingNetwork calls this contract after each assessment
        - Consumer handles routing, logging, and action decisions
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @abstractmethod
    def receive_assessment(
        self,
        assessment: Dict[str, Any],
    ) -> None:
        """
        Receive a focus assessment.
        
        Args:
            assessment: Complete focus assessment dictionary with all computed values
        """
        ...


__all__ = [
    # Primary output consumer
    "FocusAssessmentConsumer",
    # Assessment consumers (observational only)
    "PriorityAssessmentConsumer",
    "CompetitionAssessmentConsumer",
    "PrecisionAssessmentConsumer",
    "PersistenceAssessmentConsumer",
    "AllocationRecommendationConsumer",
    "BiasAssessmentConsumer",
    # Diagnostics consumer
    "DiagnosticsConsumer",
    # External interface protocol
    "FocusOutputConsumer",
]