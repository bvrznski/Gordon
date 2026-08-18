# Adaptation Governance - Phase 7.25
# =================================

"""
Canonical Adaptation Governance contract.

Governance evaluates adaptation correctness, configuration consistency,
policy compliance, rollback safety, behavior stability, and diagnostics.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class AdaptationGovernance:
    """
    Governance of adaptation sessions.
    
    Governance remains observational - it does not modify adaptations,
    only evaluates and reports on their correctness and safety.
    """
    
    # Identity
    governance_identity: str              # Unique governance identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = field(default_factory=tuple)
    
    # Findings
    findings: Dict[str, Any] = field(default_factory=dict)
    
    # Violations (if any)
    violations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Recommendations
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    evaluated_at_utc: Optional[float] = None
    
    @property
    def is_compliant(self) -> bool:
        """Check if all evaluated sessions are compliant."""
        return len(self.violations) == 0
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: List[str],
        findings: Optional[Dict[str, Any]] = None,
        violations: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationGovernance:
        """Create a new adaptation governance evaluation."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(evaluated_sessions),
            findings=findings or {},
            violations=tuple(violations or []),
            recommendations=tuple(recommendations or []),
            provenance=provenance or {},
            evaluated_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationGovernance",
]