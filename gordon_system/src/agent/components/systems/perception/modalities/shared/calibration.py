# Modality Calibration - Phase 5.2 Sensor Alignment
# ==================================================

"""
ModalityCalibration: The calibration state and metadata for a modality.

Each modality owns its own calibration. Calibration includes sensor alignment,
noise estimation, quality estimation, and time synchronization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# CALIBRATION STATE - Current calibration status
# =============================================================================


class CalibrationState(Enum):
    """
    States of modality calibration.
    
    UNCALIBRATED: Not yet calibrated
    CALIBRATING: Currently calibrating
    CALIBRATED: Calibrated and ready
    DEGRADED: Calibrated but degraded accuracy
    INVALID: Calibration data is invalid or expired
    """
    
    UNCALIBRATED = "uncalibrated"
    CALIBRATING = "calibrating"
    CALIBRATED = "calibrated"
    DEGRADED = "degraded"
    INVALID = "invalid"


# =============================================================================
# CALIBRATION METHOD - How calibration was performed
# =============================================================================


class CalibrationMethod(Enum):
    """
    Methods of calibration used by a modality.
    
    Factory: Default calibration from manufacturer
    Auto: Automatic calibration based on environment
    Manual: User-performed calibration
    External: Performed by external system or service
    Estimation: Calibrated using statistical estimation
    """
    
    FACTORY = "factory"                 # Default factory calibration
    AUTO = "auto"                       # Self-calibration
    MANUAL = "manual"                   # User-initiated
    EXTERNAL = "external"               # External calibration
    ESTIMATION = "estimation"           # Statistical estimation


# =============================================================================
# CALIBRATION METADATA - Calibration information
# =============================================================================


@dataclass(frozen=True)
class CalibrationMetadata:
    """
    Metadata about a calibration operation.
    
    Fields:
        method:              Calibration method used
        
        timestamp_utc:       When calibration was performed
        
        revision:            Calibration revision number
        
        sensor_alignment:    Alignment parameters (e.g., rotation, translation)
        
        noise_estimate:      Estimated noise characteristics
        quality_estimate:    Quality assessment after calibration
        
        time_sync_offset_ms: Time synchronization offset in milliseconds
        
        inputs_used:         References to input data used for calibration
        validation_result:   Result of calibration validation
        
        provenance:          Calibration tracking
    """
    
    # Core identity (required)
    method: str                         # CalibrationMethod value
    
    timestamp_utc: float = field(default_factory=time.time)
    
    revision: int = 1                   # Calibration version
    
    # Sensor-specific parameters
    sensor_alignment: Dict[str, Any] = field(default_factory=dict)  # e.g., rotation matrix
    
    # Quality metrics
    noise_estimate: float = 0.0         # Estimated noise level
    quality_estimate: float = 1.0       # Post-calibration quality 0.0-1.0
    
    # Time synchronization
    time_sync_offset_ms: float = 0.0    # Offset in milliseconds
    
    # References and validation
    inputs_used: Tuple[str, ...] = field(default_factory=tuple)
    validation_result: str = "pending"  # pending, passed, failed
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    @property
    def is_calibrated(self) -> bool:
        """Check if this calibration represents a valid state."""
        return self.validation_result == "passed"
    
    @classmethod
    def create(
        cls,
        method: str = "factory",
        sensor_alignment: Optional[Dict[str, Any]] = None,
        noise_estimate: float = 0.0,
        quality_estimate: float = 1.0,
        time_sync_offset_ms: float = 0.0,
        validation_result: str = "pending",
    ) -> "CalibrationMetadata":
        """
        Create a new calibration metadata instance.
        
        Args:
            method: Calibration method used
            sensor_alignment: Alignment parameters
            noise_estimate: Estimated noise level
            quality_estimate: Quality after calibration
            time_sync_offset_ms: Time sync offset in ms
            validation_result: Result of validation
            
        Returns:
            New CalibrationMetadata instance
        """
        return cls(
            method=method,
            revision=1,
            sensor_alignment=sensor_alignment or {},
            noise_estimate=noise_estimate,
            quality_estimate=quality_estimate,
            time_sync_offset_ms=time_sync_offset_ms,
            validation_result=validation_result,
        )


# =============================================================================
# CALIBRATION STATE - Complete calibration state
# =============================================================================


@dataclass(frozen=True)
class CalibrationStateData:
    """
    Complete calibration state for a modality.
    
    Fields:
        current_state:       Current calibration state
        
        metadata:            Current calibration metadata
        
        history:             Tuple of previous calibration events
        
        next_calibration_utc: When the next calibration is due
        
        revision:            State version number
    """
    
    # Core identity (required)
    current_state: str                  # CalibrationState value
    
    metadata: CalibrationMetadata = field(default_factory=CalibrationMetadata)
    
    history: Tuple[CalibrationMetadata, ...] = field(default_factory=tuple)
    
    next_calibration_utc: Optional[float] = None  # Due date
    
    revision: int = 1
    
    @property
    def is_ready(self) -> bool:
        """Check if modality is ready for observation."""
        return self.current_state in ("calibrated", "degraded")
    
    @property
    def needs_calibration(self) -> bool:
        """Check if calibration is needed or overdue."""
        if self.current_state == "uncalibrated":
            return True
        
        if self.current_state == "invalid":
            return True
        
        # Check if next calibration has passed
        if (self.next_calibration_utc and 
            time.time() > self.next_calibration_utc):
            return True
        
        return False
    
    def get_history_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of the calibration history.
        
        Returns:
            Dictionary with summary information
        """
        return {
            "current_state": self.current_state,
            "is_ready": self.is_ready,
            "needs_calibration": self.needs_calibration,
            "calibration_count": len(self.history) + 1,
            "last_calibration_utc": self.metadata.timestamp_utc,
            "next_calibration_utc": self.next_calibration_utc,
            "quality_estimate": self.metadata.quality_estimate,
        }


# =============================================================================
# CALIBRATOR - Interface for calibration operations
# =============================================================================


class Calibrator:
    """
    Interface for performing calibration operations.
    
    Implementations handle:
        - Sensor alignment
        - Noise estimation
        - Quality assessment
        - Time synchronization
        - Calibration validation
    """
    
    def calibrate(
        self,
        modality_identity: str,
        current_state: str,
    ) -> Tuple[bool, CalibrationMetadata]:
        """
        Perform calibration for a modality.
        
        Args:
            modality_identity: Modality to calibrate
            current_state: Current calibration state
            
        Returns:
            Tuple of (success, calibration metadata if successful)
        """
        raise NotImplementedError
    
    def validate_calibration(
        self,
        calibration_metadata: CalibrationMetadata,
    ) -> bool:
        """
        Validate a calibration result.
        
        Args:
            calibration_metadata: Calibration to validate
            
        Returns:
            True if validation passes
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "CalibrationState",
    "CalibrationMethod",
    
    # Dataclasses
    "CalibrationMetadata",
    "CalibrationStateData",
    
    # Classes
    "Calibrator",
]