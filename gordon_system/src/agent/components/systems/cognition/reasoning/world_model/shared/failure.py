# World-Model Reasoning Failure - Phase 7.44
# =================================

"""
Canonical World Model Failures.

Failures include identity ambiguity, scene inconsistency, physical contradictions,
causal contradictions, missing observations, and environment uncertainty.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class FailureKind(Enum):
    """Types of world-model failures."""
    
    IDENTITY_AMBIGUITY = "identity_ambiguity"
    SCENE_INCONSISTENCY = "scene_inconsistency"
    PHYSICAL_CONTRADICTION = "physical_contradiction"
    CAUSAL_CONTRADICTION = "causal_contradiction"
    MISSING_OBSERVATION = "missing_observation"
    ENVIRONMENT_UNCERTAINTY = "environment_uncertainty"


@dataclass(frozen=True)
class WorldFailure:
    """
    A world-model failure.
    """
    
    failure_id: str
    failure_kind: FailureKind
    description: str
    
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    
    recovery_options: List[str] = field(default_factory=list)
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        failure_kind: FailureKind,
        description: str,
        provenance: Optional[str] = None,
    ) -> WorldFailure:
        """Create a new world failure."""
        return cls(
            failure_id=f"failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            description=description,
            diagnostics={},
            confidence=1.0,
            recovery_options=[],
            provenance=provenance,
        )


__all__ = [
    "FailureKind",
    "WorldFailure",
]