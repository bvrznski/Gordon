# Gordon Core: Architectural Drift Detection (Phase 3.33)
"""
Architectural Drift Detection - Detects and reports on architectural drift
and evolution in the Gordon Core repository.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


# ============================================================================
# DRIFT DETECTION MODEL
# ============================================================================

@dataclass(frozen=True)
class DriftDetection:
    """
    Immutable drift detection result.
    
    Represents a single drift detection operation with its results and
    the artifacts affected by architectural changes.
    """
    
    # Detection identity
    id: str                        # Unique detection identifier
    
    # Artifact information
    artifact_id: str              # ID of detected artifact
    expected_state: Dict[str, Any]  # Expected state from architecture
    actual_state: Dict[str, Any]   # Current state in repository
    
    # Drift analysis
    drift_type: "DriftType"       # Type of drift detected
    severity: "DriftSeverity"     # Severity level
    
    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0       # Confidence in detection (0.0 to 1.0)
    
    @property
    def is_active(self) -> bool:
        """Check if drift is still active."""
        return self.drift_type != DriftType.RESOLVED
    
    @property
    def can_remediate(self) -> bool:
        """Check if drift can be automatically remediated."""
        return self.severity in (DriftSeverity.LOW, DriftSeverity.MEDIUM)


# ============================================================================
# DRIFT TYPE ENUMERATION
# ============================================================================

class DriftType(Enum):
    """
    Canonical types of architectural drift.
    
    - DEPENDENCY: Dependency graph has changed unexpectedly
    - LAYERING: Layering boundaries have been violated
    - INTERFACE: Public interfaces have diverged from specification
    - OWNERSHIP: Ownership assignments have changed without approval
    - ARCHITECTURAL: General architectural erosion detected
    - RESOLVED: Drift has been remediated
    """
    
    DEPENDENCY = "dependency"      # Dependency drift
    LAYERING = "layering"         # Layering violation
    INTERFACE = "interface"       # Interface divergence
    OWNERSHIP = "ownership"       # Ownership change without approval
    ARCHITECTURAL = "architectural"  # General architecture erosion
    RESOLVED = "resolved"         # Drift has been fixed


# ============================================================================
# DRIFT SEVERITY ENUMERATION
# ============================================================================

class DriftSeverity(Enum):
    """
    Canonical severity levels for drift detection.
    
    - LOW: Minor deviation, can be auto-remediated
    - MEDIUM: Noticeable deviation, requires review
    - HIGH: Significant violation, blocks deployment
    """
    
    LOW = "low"                   # Auto-remediable
    MEDIUM = "medium"             # Requires review
    HIGH = "high"                 # Blocks deployment


# ============================================================================
# DRIFT REPORT MODEL
# ============================================================================

@dataclass(frozen=True)
class DriftReport:
    """
    Immutable report of all drift detections at a point in time.
    """
    
    # Report identity
    id: str                        # Unique report identifier
    
    # Detection results
    detections: List[DriftDetection] = field(default_factory=list)
    
    # Summary metrics
    total_detections: int = 0
    by_severity: Dict[str, int] = field(default_factory=dict)
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.now)
    reference_time: datetime = field(default_factory=datetime.now)
    
    def add_detection(self, detection: DriftDetection) -> "DriftReport":
        """Add a detection to the report."""
        new_detections = list(self.detections)
        new_detections.append(detection)
        
        return DriftReport(
            id=self.id,
            detections=new_detections,
            total_detections=len(new_detections),
            by_severity=self._calculate_by_severity(new_detections),
            generated_at=datetime.now(),
            reference_time=self.reference_time
        )
    
    def _calculate_by_severity(self, detections: List[DriftDetection]) -> Dict[str, int]:
        """Calculate detection count by severity."""
        result = {"low": 0, "medium": 0, "high": 0}
        
        for detection in detections:
            key = detection.severity.value
            if key in result:
                result[key] += 1
        
        return result
    
    def get_severity_counts(self) -> Dict[str, int]:
        """Get counts of drift by severity."""
        return self.by_severity.copy()
    
    @property
    def has_high_severity(self) -> bool:
        """Check if any high-severity drift exists."""
        return self.by_severity.get("high", 0) > 0
    
    @property
    def can_deploy(self) -> bool:
        """Check if repository is ready to deploy."""
        return not self.has_high_severity


# ============================================================================
# DRIFT REMEDIATION MODEL
# ============================================================================

@dataclass(frozen=True)
class DriftRemediation:
    """
    Immutable remediation plan for a drift detection.
    
    Represents the steps needed to fix architectural drift and restore
    architectural integrity.
    """
    
    # Remediation identity
    id: str                        # Unique remediation identifier
    
    # Original detection reference
    detection_id: str             # ID of original detection
    
    # Artifact information
    artifact_id: str              # ID of artifact with drift
    current_state: Dict[str, Any]  # Current (incorrect) state
    target_state: Dict[str, Any]   # Correct state per architecture
    
    # Remediation details
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    is_executed: bool = False
    
    def add_step(
        self,
        action: str,
        description: str,
        target_state: Dict[str, Any]
    ) -> "DriftRemediation":
        """Add a remediation step."""
        new_steps = list(self.steps)
        new_steps.append({
            "action": action,
            "description": description,
            "target_state": dict(target_state)
        })
        
        return DriftRemediation(
            id=self.id,
            detection_id=self.detection_id,
            artifact_id=self.artifact_id,
            current_state=dict(self.current_state),
            target_state=dict(target_state),
            steps=new_steps,
            created_at=self.created_at
        )
    
    def execute(self) -> "DriftRemediation":
        """Mark remediation as executed."""
        return DriftRemediation(
            id=self.id,
            detection_id=self.detection_id,
            artifact_id=self.artifact_id,
            current_state=dict(self.current_state),
            target_state=dict(self.target_state),
            steps=list(self.steps),
            created_at=self.created_at,
            executed_at=datetime.now(),
            is_executed=True
        )


# ============================================================================
# DRIFT DETECTOR CLASS
# ============================================================================

class DriftDetector:
    """
    Detector for architectural drift.
    
    Scans the repository for architectural deviations and generates
    drift reports with severity classifications.
    """
    
    def __init__(self):
        self._detections: Dict[str, List[DriftDetection]] = {}
    
    def detect_drift(
        self,
        artifact_id: str,
        expected_state: Dict[str, Any],
        actual_state: Dict[str, Any]
    ) -> List[DriftDetection]:
        """Detect drift between expected and actual states."""
        detections = []
        
        # Check for missing required components
        for key in expected_state:
            if key not in actual_state:
                detections.append(DriftDetection(
                    id=f"drift-{artifact_id}-{key}",
                    artifact_id=artifact_id,
                    expected_state=expected_state,
                    actual_state=actual_state,
                    drift_type=DriftType.ARCHITECTURAL,
                    severity=DriftSeverity.HIGH
                ))
        
        # Check for unexpected components
        for key in actual_state:
            if key not in expected_state and key != "metadata":
                detections.append(DriftDetection(
                    id=f"drift-{artifact_id}-{key}-unexpected",
                    artifact_id=artifact_id,
                    expected_state=expected_state,
                    actual_state=actual_state,
                    drift_type=DriftType.ARCHITECTURAL,
                    severity=DriftSeverity.LOW
                ))
        
        self._detections[artifact_id] = detections
        return detections
    
    def generate_report(
        self,
        artifact_ids: List[str] = None
    ) -> DriftReport:
        """Generate a drift report."""
        all_detections = []
        
        for aid, detections in self._detections.items():
            if artifact_ids is None or aid in artifact_ids:
                all_detections.extend(detections)
        
        return DriftReport(
            id=f"drift-report-{datetime.now().isoformat()}",
            detections=all_detections,
            total_detections=len(all_detections),
            by_severity=self._calculate_by_severity(all_detections)
        )
    
    def _calculate_by_severity(self, detections: List[DriftDetection]) -> Dict[str, int]:
        """Calculate detection count by severity."""
        result = {"low": 0, "medium": 0, "high": 0}
        
        for detection in detections:
            key = detection.severity.value
            if key in result:
                result[key] += 1
        
        return result
    
    def get_detections_for_artifact(
        self,
        artifact_id: str
    ) -> List[DriftDetection]:
        """Get all drift detections for a specific artifact."""
        return self._detections.get(artifact_id, [])
    
    def get_active_detections(self) -> List[DriftDetection]:
        """Get all active (non-resolved) drift detections."""
        all_detections = []
        
        for detections in self._detections.values():
            all_detections.extend(detections)
        
        return [d for d in all_detections if d.is_active]
    
    def get_high_severity_detections(self) -> List[DriftDetection]:
        """Get all high-severity drift detections."""
        return [
            d for d in self.get_active_detections()
            if d.severity == DriftSeverity.HIGH
        ]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_drift_severity_from_type(drift_type: DriftType) -> DriftSeverity:
    """Get the severity level from drift type."""
    high_severity_types = {
        DriftType.DEPENDENCY,
        DriftType.LAYERING,
    }
    
    if drift_type in high_severity_types:
        return DriftSeverity.HIGH
    
    return DriftSeverity.MEDIUM


def calculate_drift_score(detections: List[DriftDetection]) -> float:
    """Calculate overall drift score (0.0 to 1.0, where 1.0 is worse)."""
    if not detections:
        return 0.0
    
    total_weight = 0.0
    severity_weights = {
        DriftSeverity.LOW: 0.1,
        DriftSeverity.MEDIUM: 0.5,
        DriftSeverity.HIGH: 1.0
    }
    
    for detection in detections:
        total_weight += severity_weights.get(detection.severity, 0.5)
    
    # Normalize to 0-1 range (cap at 1.0)
    return min(total_weight / max(len(detections), 1), 1.0)


def get_drift_summary(detections: List[DriftDetection]) -> Dict[str, Any]:
    """Get a summary of drift detections."""
    if not detections:
        return {
            "total": 0,
            "low_severity": 0,
            "medium_severity": 0,
            "high_severity": 0,
            "can_deploy": True
        }
    
    by_type = {}
    for detection in detections:
        type_name = detection.drift_type.value
        by_type[type_name] = by_type.get(type_name, 0) + 1
    
    return {
        "total": len(detections),
        "low_severity": sum(1 for d in detections if d.severity == DriftSeverity.LOW),
        "medium_severity": sum(1 for d in detections if d.severity == DriftSeverity.MEDIUM),
        "high_severity": sum(1 for d in detections if d.severity == DriftSeverity.HIGH),
        "by_type": by_type,
        "can_deploy": not any(d.severity == DriftSeverity.HIGH for d in detections)
    }