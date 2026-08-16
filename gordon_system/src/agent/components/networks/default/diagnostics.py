# Default Network Diagnostics
# ===========================

"""
Bounded diagnostic records for the DefaultNetwork.

Diagnostics expose semantic metrics about network operation without exposing
hidden chain-of-thought, raw latent states, or credentials.

PHASE 4.3.1: Bounded Diagnostic Records
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# DIAGNOSTIC EVENT (single operation record)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DiagnosticEvent:
    """
    A single diagnostic event during network operation.
    
    Records a specific operation or assessment for debugging and monitoring.
    """
    
    # Event timestamp
    timestamp_utc: datetime
    
    # Event source (which component generated it)
    event_source: str  # e.g., "network", "policy", "validation"
    
    # Event stage in processing pipeline
    event_stage: str  # e.g., "input_received", "assessment_started", "output_emitted"
    
    # Event type classification
    event_type: str  # e.g., "start", "end", "error", "warning"
    
    # Human-readable description
    description: str
    
    # Optional additional data (scalar values only)
    metadata: dict = field(default_factory=dict)


# =============================================================================
# DIAGNOSTICS SNAPSHOT (complete state at point in time)
# =============================================================================

@dataclass(frozen=True, slots=True)
class NetworkDiagnostics:
    """
    Complete diagnostics snapshot for the DefaultNetwork.
    
    This captures bounded diagnostic data without exposing raw computational
    details or private states.
    """
    
    # Timestamp of snapshot
    timestamp_utc: datetime
    
    # Activation metrics (bounded)
    activation_level: float = 0.0
    internal_orientation_score: float = 0.0
    
    # Proposal metrics (bounded counts)
    proposal_count: int = 0
    candidate_count: int = 0
    
    # Association metrics (bounded)
    association_count: int = 0
    memory_reactivation_count: int = 0
    
    # Reflection and simulation metrics
    reflection_candidate_count: int = 0
    simulation_candidate_count: int = 0
    prospection_candidate_count: int = 0
    
    # Goal-related metrics (bounded)
    unresolved_goal_count: int = 0
    
    # Input/output metrics (bounded counts)
    input_count: int = 0
    output_count: int = 0
    
    # Assessment confidence (normalized [0.0, 1.0])
    confidence: float = 0.5
    uncertainty: float = 0.0


# =============================================================================
# DIAGNOSTICS COLLECTOR (aggregates events during execution)
# =============================================================================

class DiagnosticsCollector:
    """
    Collector for diagnostic events during network operation.
    
    Used to aggregate events during assessment without modifying runtime state.
    """
    
    def __init__(self) -> None:
        """Initialize the diagnostics collector."""
        self._events: list[DiagnosticEvent] = []
    
    @property
    def event_count(self) -> int:
        """Return the number of collected events."""
        return len(self._events)
    
    def collect(self, event: DiagnosticEvent) -> None:
        """
        Collect a diagnostic event.
        
        Args:
            event: The diagnostic event to collect
        """
        self._events.append(event)
    
    def get_events(self) -> Tuple[DiagnosticEvent, ...]:
        """Return all collected events as an immutable tuple."""
        return tuple(self._events)
    
    def clear(self) -> None:
        """Clear all collected events."""
        self._events.clear()


# =============================================================================
# DIAGNOSTICS SINK (interface for emitting diagnostics)
# =============================================================================

class DiagnosticsSink:
    """
    Interface for emitting diagnostic data.
    
    This is a semantic interface only - it does NOT specify runtime transport
    mechanisms like network I/O or filesystem access.
    """
    
    def emit_diagnostics(self, diagnostics: NetworkDiagnostics) -> None:
        """
        Emit diagnostics snapshot.
        
        Args:
            diagnostics: The diagnostics to emit
        """
        pass  # Interface method - implementation is outside the network
    
    def emit_event(self, event: DiagnosticEvent) -> None:
        """
        Emit a single diagnostic event.
        
        Args:
            event: The event to emit
        """
        pass  # Interface method - implementation is outside the network


# =============================================================================
# DIAGNOSTIC METRICS (bounded)
# =============================================================================

class DiagnosticMetrics:
    """
    Semantic diagnostic metrics definitions.
    
    These define what can be measured about the DefaultNetwork's operation,
    without specifying how measurements are collected or stored.
    """
    
    # Activation metrics
    ACTIVATION_LEVEL = "activation_level"
    INTERNAL_ORIENTATION_SCORE = "internal_orientation_score"
    
    # Proposal metrics
    PROPOSAL_COUNT = "proposal_count"
    CANDIDATE_COUNT = "candidate_count"
    
    # Association metrics
    ASSOCIATION_COUNT = "association_count"
    MEMORY_REACTIVATION_COUNT = "memory_reactivation_count"
    
    # Reflection and simulation metrics
    REFLECTION_CANDIDATE_COUNT = "reflection_candidate_count"
    SIMULATION_CANDIDATE_COUNT = "simulation_candidate_count"
    PROSPECTION_CANDIDATE_COUNT = "prospection_candidate_count"
    
    # Goal-related metrics
    UNRESOLVED_GOAL_COUNT = "unresolved_goal_count"
    
    # Input/output metrics
    INPUT_COUNT = "input_count"
    OUTPUT_COUNT = "output_count"
    
    # Assessment metrics
    CONFIDENCE = "confidence"
    UNCERTAINTY = "uncertainty"


# =============================================================================
# DIAGNOSTIC CONSTANTS (bounded)
# =============================================================================

class DiagnosticBounds:
    """
    Bounds for diagnostic values.
    
    Ensures no diagnostic can exceed acceptable semantic bounds.
    """
    
    # Confidence must be in [0.0, 1.0]
    MIN_CONFIDENCE: float = 0.0
    MAX_CONFIDENCE: float = 1.0
    
    # Maximum event count (bounded)
    MAX_EVENT_COUNT: int = 1000


def validate_confidence(confidence: float) -> bool:
    """
    Validate that a confidence value is in valid range.
    
    Args:
        confidence: The confidence value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return DiagnosticBounds.MIN_CONFIDENCE <= confidence <= DiagnosticBounds.MAX_CONFIDENCE


def validate_event_count(count: int) -> bool:
    """
    Validate that event count is within bounds.
    
    Args:
        count: The event count to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= count <= DiagnosticBounds.MAX_EVENT_COUNT