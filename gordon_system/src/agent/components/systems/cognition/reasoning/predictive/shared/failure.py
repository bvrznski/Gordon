# Predictive Failure Model - Phase 7.40
# ======================================

"""
Predictive failure models various types of forecasting failures and their diagnostics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class FailureKind(Enum):
    """Types of predictive failures."""
    
    INVALID_ASSUMPTIONS = "invalid_assumptions"
    FORECAST_DIVERSION = "forecast_divergence"
    MISSING_OBSERVATIONS = "missing_observations"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONTRADICTORY_FORECASTS = "contradictory_forecasts"
    UNCALIBRATED_UNCERTAINTY = "uncalibrated_uncertainty"
    DETERMINISTIC_VIOLATION = "deterministic_violation"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FailureIdentity:
    """Unique identity for a failure record."""
    
    failure_id: str
    semantic_identity: str
    
    @classmethod
    def create(cls) -> FailureIdentity:
        """Create a new failure identity."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            semantic_identity="failure-identity",
        )


@dataclass(frozen=True)
class PredictiveFailure:
    """
    Records a predictive failure with its diagnostics and recovery options.
    
    Failures include:
        - Invalid assumptions
        - Forecast divergence
        - Missing observations
        - Insufficient evidence
        - Contradictory forecasts
        - Uncalibrated uncertainty
    
    Failures remain explicit for inspection and debugging.
    """
    
    # Identity
    failure_identity: str
    
    # Failure kind
    failure_kind: FailureKind
    
    # Diagnostics
    diagnostics: Dict[str, Any]
    
    # Recovery options
    recovery_options: List[str] = field(default_factory=list)
    
    # Provenance
    occurred_at_utc: float = field(default_factory=time.time)
    associated_session_id: Optional[str] = None  # Predictive session ID if known
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        diagnostics: Dict[str, Any],
        recovery_options: List[str] = None,
        associated_session_id: Optional[str] = None,
    ) -> PredictiveFailure:
        """Create a new predictive failure record."""
        return cls(
            failure_identity=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            diagnostics=diagnostics,
            recovery_options=recovery_options or [],
            occurred_at_utc=time.time(),
            associated_session_id=associated_session_id,
        )


__all__ = [
    "PredictiveFailure",
    "FailureIdentity",
    "FailureKind",
]