# Modality Diagnostics - Phase 5.2 Runtime Diagnostics
# =====================================================

"""
ModalityDiagnostics: Detailed diagnostic information for a modality.

Diagnostics include observation counts, dropped events, quality metrics,
permission scope, sandbox status, and calibration state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# DIAGNOSTICS METRICS - Runtime diagnostic measurements
# =============================================================================


@dataclass(frozen=True)
class DiagnosticsMetrics:
    """
    Runtime metrics for diagnostics.
    
    Fields:
        observations_produced:   Total observations generated
        
        signals_processed:       Total signals processed
        
        features_extracted:      Total features computed
        
        percepts_generated:      Total percepts created
        
        dropped_events_count:    Events that could not be processed
    """
    
    # Core metrics
    observations_produced: int = 0
    
    signals_processed: int = 0
    
    features_extracted: int = 0
    
    percepts_generated: int = 0
    
    dropped_events_count: int = 0


# =============================================================================
# MODALITY DIAGNOSTICS - Complete diagnostic report
# =============================================================================


@dataclass(frozen=True)
class ModalityDiagnostics:
    """
    Detailed diagnostic information for a modality.
    
    Fields:
        observation_count:       Total observations produced
        
        dropped_event_count:     Events that could not be processed
        
        signal_quality_mean:     Mean quality score of signals
        
        confidence_distribution: Confidence value distribution
        uncertainty_distribution: Uncertainty value distribution
        
        effective_permission_scope: Current permission scope
        
        sandbox_status:          Sandbox enforcement status
        
        calibration_status:      Calibration state string
    """
    
    # Core identity (required)
    observation_count: int = 0
    
    dropped_event_count: int = 0
    
    signal_quality_mean: float = 1.0
    
    confidence_distribution: Dict[str, float] = field(default_factory=dict)  # value -> count
    
    uncertainty_distribution: Dict[str, float] = field(default_factory=dict)
    
    effective_permission_scope: Tuple[str, ...] = field(default_factory=tuple)
    
    sandbox_status: str = "none"
    
    calibration_status: str = "unknown"
    
    @property
    def is_operational(self) -> bool:
        """Check if modality appears operational based on diagnostics."""
        return self.observation_count > 0 or self.signal_quality_mean >= 0.5
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the diagnostic report.
        
        Returns:
            Dictionary with summary information
        """
        total_events = self.observation_count + self.dropped_event_count
        
        return {
            "observation_count": self.observation_count,
            "dropped_event_count": self.dropped_event_count,
            "total_events": total_events,
            "drop_rate_percent": (self.dropped_event_count / max(total_events, 1) * 100),
            "signal_quality_mean": self.signal_quality_mean,
            "effective_permissions": len(self.effective_permission_scope),
            "sandbox_status": self.sandbox_status,
            "calibration_status": self.calibration_status,
        }


# =============================================================================
# DIAGNOSTIC LOGGER - Interface for diagnostic logging
# =============================================================================


class DiagnosticLogger:
    """
    Interface for diagnostic logging and reporting.
    
    Implementations track:
        - Event counts and drop rates
        - Quality trends
        - Confidence/uncertainty distributions
        - Permission and sandbox enforcement events
        - Calibration status changes
    """
    
    def log_observation(
        self,
        modality_identity: str,
        quality: float = 1.0,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> None:
        """
        Log an observation event for diagnostics.
        
        Args:
            modality_identity: Modality that produced the observation
            quality: Observation quality 0.0-1.0
            confidence: Confidence in the observation
            uncertainty: Known limitations
        """
        raise NotImplementedError
    
    def log_dropped_event(
        self,
        modality_identity: str,
        reason: str = "unknown",
    ) -> None:
        """
        Log a dropped event for diagnostics.
        
        Args:
            modality_identity: Modality where event was dropped
            reason: Reason for the drop
        """
        raise NotImplementedError
    
    def get_diagnostics(
        self,
        modality_identity: str,
    ) -> ModalityDiagnostics:
        """
        Get current diagnostic state for a modality.
        
        Args:
            modality_identity: Modality to check
            
        Returns:
            Current diagnostics report
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Dataclasses
    "DiagnosticsMetrics",
    "ModalityDiagnostics",
    
    # Classes
    "DiagnosticLogger",
]