# World-Model Reasoning Consistency - Phase 7.44
# =================================

"""
Canonical World Consistency Management.

Consistency evaluates physical, causal, and structural coherence of the world model.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ConsistencyKind(Enum):
    """Types of consistency evaluation."""
    
    PHYSICAL = "physical"               # Physical laws and constraints
    TEMPORAL = "temporal"               # Temporal ordering and causality
    IDENTITY = "identity"               # Entity identity stability
    CAUSAL = "causal"                   # Causal coherence
    STRUCTURAL = "structural"           # Structural integrity
    SEMANTIC = "semantic"               # Semantic consistency


class ConsistencyState(Enum):
    """Consistency evaluation states."""
    
    PENDING = "pending"
    ANALYZING = "analyzing"
    VERIFIED = "verified"
    VIOLATIONS_FOUND = "violations_found"


@dataclass(frozen=True)
class ConsistencyViolation:
    """
    A detected consistency violation.
    """
    
    violation_id: str                   # Unique identifier
    timestamp_utc: float                # When detected
    
    # Violation details
    kind: ConsistencyKind               # What type of violation?
    description: str                    # Human-readable description
    
    # Affected elements
    affected_entity_ids: List[str]      # Entities involved
    affected_state_hash: Optional[str] = None  # World state hash at violation time
    
    # Severity and confidence
    severity: float = 1.0               # Impact severity (0.0 to 1.0)
    confidence: float = 1.0             # Confidence in the detection
    
    @classmethod
    def create(
        cls,
        kind: ConsistencyKind,
        description: str,
        affected_entity_ids: Optional[List[str]] = None,
    ) -> ConsistencyViolation:
        """Create a new consistency violation."""
        return cls(
            violation_id=f"violation:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            kind=kind,
            description=description,
            affected_entity_ids=affected_entity_ids or [],
            severity=1.0,
            confidence=1.0,
        )


@dataclass(frozen=True)
class ConsistencyMetric:
    """
    A metric measuring a specific aspect of consistency.
    """
    
    metric_id: str                      # Unique identifier
    timestamp_utc: float                # When measured
    
    # Metric details
    kind: ConsistencyKind               # What does this measure?
    value: float                        # Numeric value (0.0 to 1.0, where 1.0 = fully consistent)
    
    @classmethod
    def create(
        cls,
        kind: ConsistencyKind,
        value: float,
        timestamp_utc: Optional[float] = None,
    ) -> ConsistencyMetric:
        """Create a new consistency metric."""
        return cls(
            metric_id=f"metric:{uuid.uuid4().hex[:16]}",
            timestamp_utc=timestamp_utc or time.time(),
            kind=kind,
            value=value,
        )


@dataclass(frozen=True)
class WorldConsistency:
    """
    World consistency analysis result.
    
    A WorldConsistency contains:
        - Consistency identity
        - Consistency metrics (measured values)
        - Detected violations
        - Confidence estimates
        - Provenance tracking
    """
    
    # Identity
    consistency_id: str                 # Unique consistency identifier
    
    # Metrics
    physical_consistency: float = 1.0   # Physical laws satisfied?
    temporal_consistency: float = 1.0   # Temporal ordering correct?
    identity_consistency: float = 1.0   # Entity identities stable?
    causal_consistency: float = 1.0     # Causal coherence maintained?
    structural_consistency: float = 1.0 # Structural integrity OK?
    
    # Violations
    detected_violations: List[ConsistencyViolation] = field(default_factory=list)
    
    # Metadata
    world_revision: int = 1
    
    # Confidence and provenance
    confidence: float = 1.0
    provenance: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
        world_revision: int = 1,
    ) -> WorldConsistency:
        """Create a new world consistency analysis."""
        return cls(
            consistency_id=f"consistency:{uuid.uuid4().hex[:16]}",
            physical_consistency=1.0,
            temporal_consistency=1.0,
            identity_consistency=1.0,
            causal_consistency=1.0,
            structural_consistency=1.0,
            detected_violations=[],
            confidence=1.0,
            provenance=provenance,
            world_revision=world_revision,
        )
    
    def with_violation(self, violation: ConsistencyViolation) -> WorldConsistency:
        """Add a detected violation."""
        new_violations = self.detected_violations + [violation]
        
        # Update metrics based on violation
        new_physical = self.physical_consistency * (1.0 - 0.2 * (1 if violation.kind == ConsistencyKind.PHYSICAL else 0))
        new_temporal = self.temporal_consistency * (1.0 - 0.2 * (1 if violation.kind == ConsistencyKind.TEMPORAL else 0))
        new_identity = self.identity_consistency * (1.0 - 0.2 * (1 if violation.kind == ConsistencyKind.IDENTITY else 0))
        new_causal = self.causal_consistency * (1.0 - 0.2 * (1 if violation.kind == ConsistencyKind.CAUSAL else 0))
        new_structural = self.structural_consistency * (1.0 - 0.2 * (1 if violation.kind == ConsistencyKind.STRUCTURAL else 0))
        
        return dataclass_replace(
            self,
            physical_consistency=max(0.0, new_physical),
            temporal_consistency=max(0.0, new_temporal),
            identity_consistency=max(0.0, new_identity),
            causal_consistency=max(0.0, new_causal),
            structural_consistency=max(0.0, new_structural),
            detected_violations=new_violations,
        )


@dataclass(frozen=True)
class WorldConsistencyManagement:
    """
    World consistency management contract.
    
    A world consistency management result contains:
        - Consistency identity
        - Consistency model (complete representation)
        - Detected violations
        - Confidence estimates
        - Provenance tracking
    """
    
    # Identity
    management_id: str                  # Unique management identifier
    
    # Model
    consistency_model: Dict[str, Any]   # Complete consistency model
    
    # Violations and metrics
    detected_violations: List[ConsistencyViolation]
    consistency_metrics: List[ConsistencyMetric] = field(default_factory=list)
    
    # Metadata
    confidence: float = 1.0
    provenance: Optional[str] = None
    world_revision: int = 1
    
    @classmethod
    def create(
        cls,
        provenance: Optional[str] = None,
        world_revision: int = 1,
    ) -> WorldConsistencyManagement:
        """Create a new world consistency management."""
        return cls(
            management_id=f"consistency_management:{uuid.uuid4().hex[:16]}",
            consistency_model={},
            detected_violations=[],
            consistency_metrics=[],
            confidence=1.0,
            provenance=provenance,
            world_revision=world_revision,
        )
    
    def with_consistency_model(self, model: Dict[str, Any]) -> WorldConsistencyManagement:
        """Update management result with full consistency model."""
        return dataclass_replace(
            self,
            consistency_model=model,
        )


# Helper function for dataclass replacement
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConsistencyKind",
    "ConsistencyState",
    "ConsistencyViolation",
    "ConsistencyMetric",
    "WorldConsistency",
    "WorldConsistencyManagement",
]