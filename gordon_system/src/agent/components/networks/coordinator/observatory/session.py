# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Observation Sessions
====================

Models for grouping related observations into sessions.

SESSION LAWS (from spec)
------------------------
SESSION-LAW-001: Observation Sessions shall group related observations.
SESSION-LAW-002: Session boundaries shall remain explicit.
SESSION-LAW-003: Observation membership shall remain explicit.
SESSION-LAW-004: Session aggregation shall preserve provenance.
SESSION-LAW-005: Historical sessions shall remain inspectable.
SESSION-LAW-006: Sessions shall remain immutable.
SESSION-LAW-007: Session revisions shall preserve lineage.
SESSION-LAW-008: Session construction shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class ObservationSession:
    """
    Immutable session grouping related observations.
    
    SESSION-LAW-001: Sessions group related observations.
    SESSION-LAW-002: Session boundaries remain explicit.
    """
    
    session_identity: str
    """Unique identifier for this session."""
    
    observation_window: tuple[int, int] = field(default_factory=lambda: (0, 1))
    """Temporal window of the session (start_epoch, end_epoch)."""
    
    participating_observations: tuple[str, ...] = ()
    """Observation identities in this session."""
    
    aggregated_reports: tuple[str, ...] = ()
    """Report identities generated from observations."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this session."""
    
    def __post_init__(self):
        """Validate session components."""
        if not self.session_identity:
            raise ValueError("Session identity cannot be empty")
        
        start, end = self.observation_window
        if start > end:
            raise ValueError(f"Invalid window: {start} > {end}")
    
    @classmethod
    def create(
        cls,
        observation_window: tuple[int, int] = (0, 1),
        participating_observations: tuple[str, ...] = (),
        aggregated_reports: tuple[str, ...] = (),
        provenance: Optional[dict[str, str]] = None,
    ) -> ObservationSession:
        """
        Create a new observation session.
        
        Args:
            observation_window: Temporal window of the session
            participating_observations: Observation identities in this session
            aggregated_reports: Report identities generated from observations
            provenance: Optional provenance dictionary
            
        Returns:
            New ObservationSession instance with deterministic identity
        """
        import hashlib
        
        # Create deterministic identity based on content
        identity_content = f"session:{observation_window[0]}:{observation_window[1]}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            session_identity=f"session:{identity_hash}",
            observation_window=observation_window,
            participating_observations=participating_observations,
            aggregated_reports=aggregated_reports,
            provenance=provenance or {},
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_identity": self.session_identity,
            "observation_window": list(self.observation_window),
            "participating_observations": list(self.participating_observations),
            "aggregated_reports": list(self.aggregated_reports),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObservationSession:
        """Create session from dictionary."""
        return cls(
            session_identity=data["session_identity"],
            observation_window=tuple(data.get("observation_window", [0, 1])),
            participating_observations=tuple(data.get("participating_observations", [])),
            aggregated_reports=tuple(data.get("aggregated_reports", [])),
            provenance=dict(data.get("provenance", {})),
        )