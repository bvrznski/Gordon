# Introspection Governance - Phase 7.29
# ======================================

"""
Introspection Governance evaluates introspection quality.

Governance is:
    Observational - It does not modify introspection artifacts directly
    Explicit - All findings are documented
    Independent - Results can be inspected separately
    
Governance ensures introspection follows architectural principles.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class IntrospectionGovernance:
    """
    Governance evaluation of introspection.
    
    A governance report contains:
        - Explicit identity
        - Evaluated sessions
        - Findings and violations
        - Recommendations
        - Provenance tracking
    
    Governance remains observational.
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Evaluated sessions
    evaluated_sessions: List[str] = field(default_factory=list)  # Session IDs evaluated
    
    # Findings
    findings: List[Dict[str, Any]] = field(default_factory=list)  # Governance findings
    violation_count: int = 0                  # Number of violations found
    
    # Violations (if any)
    violations: List[Dict[str, Any]] = field(default_factory=list)  # Policy violations
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)  # Improvement suggestions
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> IntrospectionGovernance:
        """Create a new introspection governance report."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionGovernance",
]