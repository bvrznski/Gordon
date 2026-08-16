# Integration Health - Phase 5.2.3
# ================================

"""
Integration Health: Operational status of the integration system.

Health monitoring tracks availability, component health, and degradation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# INTEGRATION HEALTH - Overall system health state
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationHealth:
    """
    Health status of the integration system.
    
    Fields:
        availability: Is the system available?
        correspondence_health: Correspondence evaluation health
        temporal_binding_health: Temporal binding health
        spatial_binding_health: Spatial binding health
        fusion_health: Fusion execution health
        source_dependency_health: Source dependency analysis health
        conflict_preservation_health: Conflict preservation health
        confidence_integrity: Confidence aggregation integrity
        uncertainty_integrity: Uncertainty aggregation integrity
        provenance_integrity: Provenance tracking integrity
        degradation: Current level of degraded operation (0.0-1.0)
    """
    
    availability: bool = True               # Is the system available?
    
    correspondence_health: float = 1.0      # 0.0-1.0 (degraded if < 1.0)
    temporal_binding_health: float = 1.0
    spatial_binding_health: float = 1.0
    fusion_health: float = 1.0
    
    source_dependency_health: float = 1.0
    conflict_preservation_health: float = 1.0
    confidence_integrity: float = 1.0
    uncertainty_integrity: float = 1.0
    provenance_integrity: float = 1.0
    
    degradation: float = 0.0                # 0.0 = healthy, 1.0 = fully degraded
    
    health_status: Dict[str, Any] = field(default_factory=dict)
    
    last_check: float = field(default_factory=time.time)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def overall_health(self) -> float:
        """Calculate overall health as average of component health."""
        components = [
            self.correspondence_health,
            self.temporal_binding_health,
            self.spatial_binding_health,
            self.fusion_health,
            self.source_dependency_health,
            self.conflict_preservation_health,
            self.confidence_integrity,
            self.uncertainty_integrity,
            self.provenance_integrity,
        ]
        return sum(components) / len(components)
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is fully healthy."""
        return self.availability and self.overall_health >= 0.95
    
    @property
    def is_degraded(self) -> bool:
        """Check if system is operating in degraded mode."""
        return not self.is_healthy and self.availability
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health status to dictionary."""
        return {
            "availability": self.availability,
            "correspondence_health": self.correspondence_health,
            "temporal_binding_health": self.temporal_binding_health,
            "spatial_binding_health": self.spatial_binding_health,
            "fusion_health": self.fusion_health,
            "source_dependency_health": self.source_dependency_health,
            "conflict_preservation_health": self.conflict_preservation_health,
            "confidence_integrity": self.confidence_integrity,
            "uncertainty_integrity": self.uncertainty_integrity,
            "provenance_integrity": self.provenance_integrity,
            "degradation": self.degradation,
            "overall_health": self.overall_health,
            "is_healthy": self.is_healthy,
            "is_degraded": self.is_degraded,
            "last_check": self.last_check,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def healthy(cls) -> "PerceptionIntegrationHealth":
        """Create a healthy health status."""
        return cls(
            availability=True,
            confidence=1.0,
            uncertainty=0.0,
            last_check=time.time(),
            provenance={"origin": "system"},
        )
    
    @classmethod
    def degraded(cls, degradation: float = 0.5) -> "PerceptionIntegrationHealth":
        """Create a degraded health status."""
        return cls(
            availability=True,
            confidence=max(0.0, 1.0 - degradation),
            uncertainty=min(1.0, 0.5 + degradation * 0.3),
            degradation=degradation,
            last_check=time.time(),
            provenance={"origin": "system", "degraded_reason": "component_failure"},
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionIntegrationHealth":
        """Create health status from dictionary."""
        return cls(
            availability=bool(data.get("availability", True)),
            correspondence_health=float(data.get("correspondence_health", 1.0)),
            temporal_binding_health=float(data.get("temporal_binding_health", 1.0)),
            spatial_binding_health=float(data.get("spatial_binding_health", 1.0)),
            fusion_health=float(data.get("fusion_health", 1.0)),
            source_dependency_health=float(data.get("source_dependency_health", 1.0)),
            conflict_preservation_health=float(data.get("conflict_preservation_health", 1.0)),
            confidence_integrity=float(data.get("confidence_integrity", 1.0)),
            uncertainty_integrity=float(data.get("uncertainty_integrity", 1.0)),
            provenance_integrity=float(data.get("provenance_integrity", 1.0)),
            degradation=float(data.get("degradation", 0.0)),
        )


# =============================================================================
# DIAGNOSTICS - Integration diagnostic information
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationDiagnostics:
    """
    Diagnostic information for an integration operation.
    
    Fields:
        diagnostics_identity: Unique identifier for this diagnostics record
        request_reference: Reference to the integrated request
        timing: Timing information per stage
        resource_usage: Resource consumption metrics
        component_states: State of each integration component
        warnings: Any warnings encountered
        errors: Any errors encountered
        trace_ids: Related trace IDs for correlation
    """
    
    diagnostics_identity: str              # Unique ID
    
    request_reference: str                 # Reference to integrated request
    
    timing: Dict[str, float] = field(default_factory=dict)  # stage -> duration_seconds
    resource_usage: Dict[str, Any] = field(default_factory=dict)  # cpu, memory, etc.
    
    component_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # component -> state
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    errors: Tuple[str, ...] = field(default_factory=tuple)
    
    trace_ids: Tuple[str, ...] = field(default_factory=tuple)  # Correlation IDs
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def add_warning(self, warning: str) -> "PerceptionIntegrationDiagnostics":
        """Add a warning to diagnostics."""
        return dataclass_replace_frozen(self, warnings=self.warnings + (warning,))
    
    def add_error(self, error: str) -> "PerceptionIntegrationDiagnostics":
        """Add an error to diagnostics."""
        return dataclass_replace_frozen(self, errors=self.errors + (error,))
    
    def set_timing(self, stage: str, duration_seconds: float) -> "PerceptionIntegrationDiagnostics":
        """Set timing for a component."""
        new_timing = dict(self.timing)
        new_timing[stage] = duration_seconds
        return dataclass_replace_frozen(self, timing=new_timing)


try:
    from dataclasses import fields as dataclass_fields
    
    def dataclass_replace_frozen(instance, **kwargs):
        """Replace fields in a frozen dataclass."""
        return type(instance)(**{**dataclass_asdict(instance), **kwargs})
except ImportError:
    # Fallback for older Python versions
    import copy
    
    def dataclass_replace_frozen(instance, **kwargs):
        """Replace fields in a frozen dataclass."""
        new_data = {}
        for field_info in dataclass_fields(instance):
            key = field_info.name
            if key in kwargs:
                new_data[key] = kwargs[key]
            else:
                new_data[key] = getattr(instance, key)
        return type(instance)(**new_data)


def create_integration_diagnostics(
    request_reference: str,
) -> PerceptionIntegrationDiagnostics:
    """Create initial diagnostics for an integration."""
    return PerceptionIntegrationDiagnostics(
        diagnostics_identity=f"diag:{uuid.uuid4().hex[:16]}",
        request_reference=request_reference,
        provenance={
            "origin": "system",
            "created_at_utc": time.time(),
        },
    )