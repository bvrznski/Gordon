# Perception Integration Session - Phase 5.2.3
# =============================================

"""
Integration Session: Groups related evidence-processing activity.

A PerceptionIntegrationSession tracks the state of an ongoing integration operation,
maintaining references to participating streams and modalities.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict as dataclass_asdict
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import time
import uuid


# =============================================================================
# INTEGRATION SESSION HEALTH - What is the session's operational status?
# =============================================================================


class IntegrationHealth(Enum):
    """
    Health status of an integration session.
    
    States:
        HEALTHY:       Session operating normally
        DEGRADED:      Some capabilities reduced
        PARTIAL:       Only partial results achievable
        AMBIGUOUS:     Multiple interpretations possible
        CONFLICTED:    Conflicting evidence detected
        FAILED:        Session failed
    """
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    PARTIAL = "partial"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    FAILED = "failed"


# =============================================================================
# PERCEPTION INTEGRATION SESSION - Track ongoing integration
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationSession:
    """
    Session tracking for a set of related integration activity.
    
    Fields:
        session_identity:     Unique session identifier
        participating_streams: Which data streams participate?
        participating_modalities: Which modalities are involved?
        integration_window:   Temporal window covered by this session
        active_correspondences: Current correspondence candidates
        active_bindings:      Current binding structures
        active_conflicts:     Conflicts under evaluation
        produced_artifacts:   Integrated artifacts from this session
        health:               Operational health status
        statistics:           Session metrics and counts
        provenance:           Origin tracking
    """
    
    session_identity: str                  # Unique ID
    
    participating_streams: Tuple[str, ...]  # Stream IDs involved
    
    participating_modalities: Tuple[str, ...]  # e.g., ("console", "vision")
    
    integration_window: Dict[str, Any] = field(default_factory=dict)  # time range, bounds
    
    active_correspondences: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    active_bindings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    active_conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    produced_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Artifact IDs
    
    health: IntegrationHealth = IntegrationHealth.HEALTHY
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def add_correspondence(
        self,
        correspondence_id: str,
        artifacts: List[str],
        kind: str,
    ) -> "PerceptionIntegrationSession":
        """Add a correspondence candidate to this session."""
        return dataclass_replace_frozen(self, active_correspondences=self.active_correspondences + ({"id": correspondence_id, "artifacts": tuple(artifacts), "kind": kind},))
    
    def add_binding(
        self,
        binding_id: str,
        bound_artifact_ids: List[str],
        window: Dict[str, Any],
    ) -> "PerceptionIntegrationSession":
        """Add a binding structure to this session."""
        return dataclass_replace_frozen(self, active_bindings=self.active_bindings + ({"id": binding_id, "bound_artifacts": tuple(bound_artifact_ids), "window": dict(window)},))
    
    def add_conflict(
        self,
        conflict_id: str,
        participating_artifact_ids: List[str],
        conflicting_fields: List[str],
    ) -> "PerceptionIntegrationSession":
        """Add a conflict to this session."""
        return dataclass_replace_frozen(self, active_conflicts=self.active_conflicts + ({"id": conflict_id, "artifacts": tuple(participating_artifact_ids), "fields": tuple(conflicting_fields)},))
    
    def add_produced_artifact(self, artifact_id: str) -> "PerceptionIntegrationSession":
        """Add an integrated artifact to the session results."""
        return dataclass_replace_frozen(self, produced_artifacts=self.produced_artifacts + (artifact_id,))
    
    def update_health(self, new_health: IntegrationHealth) -> "PerceptionIntegrationSession":
        """Update the session health status."""
        return dataclass_replace_frozen(self, health=new_health)
    
    def increment_statistic(self, key: str, value: int = 1) -> "PerceptionIntegrationSession":
        """Increment a statistics counter."""
        current = self.statistics.get(key, 0)
        new_stats = dict(self.statistics)
        new_stats[key] = current + value
        return dataclass_replace_frozen(self, statistics=new_stats)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_identity": self.session_identity,
            "participating_streams": list(self.participating_streams),
            "participating_modalities": list(self.participating_modalities),
            "integration_window": dict(self.integration_window),
            "active_correspondences_count": len(self.active_correspondences),
            "active_bindings_count": len(self.active_bindings),
            "active_conflicts_count": len(self.active_conflicts),
            "produced_artifacts": list(self.produced_artifacts),
            "health": self.health.value if hasattr(self.health, 'value') else str(self.health),
            "statistics": dict(self.statistics),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionIntegrationSession":
        """Create session from dictionary."""
        return cls(
            session_identity=data.get("session_identity", str(uuid.uuid4())),
            participating_streams=tuple(data.get("participating_streams", [])),
            participating_modalities=tuple(data.get("participating_modalities", [])),
            integration_window=dict(data.get("integration_window", {})),
            active_correspondences=tuple(),
            active_bindings=tuple(),
            active_conflicts=tuple(),
            produced_artifacts=tuple(data.get("produced_artifacts", [])),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_frozen(instance, **kwargs):
    """Replace fields in a frozen dataclass."""
    return type(instance)(**{**dataclass_asdict(instance), **kwargs})


def create_integration_session(
    participating_modalities: List[str],
    participating_streams: Optional[List[str]] = None,
) -> PerceptionIntegrationSession:
    """
    Create a new integration session.
    
    Args:
        participating_modalities: Modalities involved in this session
        participating_streams: Data streams involved (optional)
        
    Returns:
        New PerceptionIntegrationSession
    """
    return PerceptionIntegrationSession(
        session_identity=f"integration_session:{uuid.uuid4().hex[:16]}",
        participating_streams=tuple(participating_streams or []),
        participating_modalities=tuple(participating_modalities),
        integration_window={},
        statistics={"started_at_utc": time.time()},
        provenance={
            "origin": "system",
            "created_at_utc": time.time(),
        },
    )