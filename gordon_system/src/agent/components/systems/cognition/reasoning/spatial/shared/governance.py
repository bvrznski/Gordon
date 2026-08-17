# Spatial Governance - Phase 7.9
# =============================

"""
Canonical Spatial Governance.

Spatial governance evaluates:
    geometric correctness, topological consistency, transformation validity,
    navigation semantics, reference-frame integrity.
    
Governance remains observational (never modifies artifacts directly).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GovernanceFinding:
    """
    Individual finding from governance evaluation.
    
    Each finding documents what was evaluated and whether it passed.
    """
    
    # Identity
    finding_id: str                         # Unique identifier
    
    # Check type
    check_type: str                         # e.g., "frame_integrity", "topology_consistency"
    
    # Result
    is_valid: bool = True                   # Did the check pass?
    severity: str = "info"                  # info, warning, error
    
    # Details
    description: str = ""                   # Human-readable description
    affected_entity_ids: Tuple[str, ...] = ()  # Which entities are affected?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""


@dataclass(frozen=True)
class SpatialGovernance:
    """
    Result of spatial governance evaluation.
    
    Governance remains observational (never modifies artifacts directly).
    """
    
    # Identity
    governance_id: str                      # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()   # Session IDs evaluated
    
    # Findings from all checks
    findings: Tuple[GovernanceFinding, ...] = ()
    
    # Violations (if any)
    violations: Tuple[str, ...] = ()        # Detailed violation descriptions
    
    # Recommendations for improvement
    recommendations: Tuple[str, ...] = ()
    
    # Overall status
    is_compliant: bool = True               # Passed all checks?
    
    # Check summaries
    frame_integrity_valid: bool = True
    topology_consistency_valid: bool = True
    transformation_correctness_valid: bool = True
    navigation_semantics_valid: bool = True
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def session_count(self) -> int:
        """Return number of evaluated sessions."""
        return len(self.evaluated_sessions)
    
    @property
    def finding_count(self) -> int:
        """Return number of findings."""
        return len(self.findings)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        session_ids: List[str],
    ) -> SpatialGovernance:
        """Create a new governance evaluation result."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids),
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def add_finding(self, finding: GovernanceFinding) -> SpatialGovernance:
        """Return new governance with additional finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
            violations=self.violations + (() if finding.is_valid else (finding.description,)),
            is_compliant=self.is_compliant and finding.is_valid,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SpatialGovernance", 
    "GovernanceFinding",
]