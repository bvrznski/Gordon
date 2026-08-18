# Predictive Evolution Model - Phase 7.40
# ========================================

"""
Predictive evolution model tracks changes to forecasts over time.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class EvolutionIdentity:
    """Unique identity for an evolution record."""
    
    evolution_id: str
    semantic_identity: str
    
    @classmethod
    def create(cls) -> EvolutionIdentity:
        """Create a new evolution identity."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            semantic_identity="evolution-identity",
        )


@dataclass(frozen=True)
class ForecastRevision:
    """A revision to a forecast."""
    
    revision_id: str
    original_forecast: Dict[str, Any]
    revised_forecast: Dict[str, Any]
    revision_reason: str
    timestamp_utc: float
    
    @classmethod
    def create(
        cls,
        original_forecast: Dict[str, Any],
        revised_forecast: Dict[str, Any],
        reason: str,
    ) -> ForecastRevision:
        """Create a forecast revision."""
        return cls(
            revision_id=f"rev:{uuid.uuid4().hex[:16]}",
            original_forecast=original_forecast,
            revised_forecast=revised_forecast,
            revision_reason=reason,
            timestamp_utc=time.time(),
        )


@dataclass(frozen=True)
class RevisionHistory:
    """Complete history of forecast revisions."""
    
    revision_count: int
    revision_timeline: List[ForecastRevision]
    latest_revision: Optional[ForecastRevision] = None
    
    @classmethod
    def create(cls, revisions: List[ForecastRevision] = None) -> RevisionHistory:
        """Create a revision history."""
        revisions = revisions or []
        return cls(
            revision_count=len(revisions),
            revision_timeline=revisions,
            latest_revision=revisions[-1] if revisions else None,
        )


@dataclass(frozen=True)
class PredictiveEvolution:
    """
    Tracks the evolution of predictive reasoning over time.
    
    An evolution record contains:
        - Evolution identity
        - History of changes to forecasts
        - Triggering events for each change
        - Updated forecast state
    """
    
    # Identity
    evolution_identity: str
    
    # Evolution history
    revision_history: RevisionHistory
    
    # Triggering events
    triggering_events: List[str] = field(default_factory=list)
    
    # Updated forecasts after all revisions
    updated_forecasts: Dict[str, Any]
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    original_forecast_ids: List[str] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        revision_history: RevisionHistory,
        triggering_events: List[str] = None,
        updated_forecasts: Dict[str, Any] = None,
        original_forecast_ids: List[str] = None,
    ) -> PredictiveEvolution:
        """Create a new predictive evolution record."""
        return cls(
            evolution_identity=f"evolution:{uuid.uuid4().hex[:16]}",
            revision_history=revision_history,
            triggering_events=triggering_events or [],
            updated_forecasts=updated_forecasts or {},
            original_forecast_ids=original_forecast_ids or [],
            created_at_utc=time.time(),
        )


__all__ = [
    "PredictiveEvolution",
    "EvolutionIdentity",
    "ForecastRevision",
    "RevisionHistory",
]