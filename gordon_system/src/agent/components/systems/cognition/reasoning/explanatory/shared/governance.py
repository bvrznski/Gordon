# Explanation Governance - Phase 7.14
# ====================================

"""
Explanation governance for explanatory reasoning.

Governance evaluates:
    - Explanation correctness
    - Evidence quality
    - Justification completeness
    - Narrative coherence
    - Interpretability
    - Diagnostics

Governance remains observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class GovernanceIdentity:
    """
    Immutable identity for an explanation governance evaluation.
    """
    
    semantic_identity: str                    # Stable identity across runs
    governance_number: int = 1                # For repeated evaluations
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, governance_number: int = 1) -> GovernanceIdentity:
        """Create a new governance identity."""
        return cls(
            semantic_identity=semantic_identity,
            governance_number=governance_number,
        )


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A finding from explanation governance evaluation.
    
    Findings include:
        - Interpretability issues
        - Justification gaps
        - Evidence quality problems
        - Narrative incoherence
    """
    
    # Identity
    finding_id: str                           # Unique identifier
    
    # Content
    finding_type: str                         # What kind of finding?
    severity: float = 0.5                     # How severe? (0.0-1.0)
    
    # Details
    description: str = ""                     # What's the issue?
    recommendation: str = ""                  # How to fix it?


@dataclass(frozen=True)
class ExplanationGovernance:
    """
    Governance evaluation for an explanation.
    
    Evaluates:
        - Explanation correctness
        - Evidence quality
        - Justification completeness
        - Narrative coherence
        - Interpretability
        - Diagnostics
    
    Governance remains observational - it evaluates but does not mutate.
    """
    
    # Identity
    governance_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...]       # Which explanations were checked?
    
    # Findings
    findings: Tuple[GovernanceFinding, ...]
    
    # Summary metrics
    violation_count: int = 0                  # Number of issues found
    interpretability_score: float = 0.5       # How interpretable?
    
    @property
    def is_compliant(self) -> bool:
        """Check if explanation meets governance standards."""
        return self.violation_count == 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_sessions: List[str],
        findings: Optional[List[GovernanceFinding]] = None,
    ) -> "ExplanationGovernance":
        """Create a new governance evaluation."""
        finding_tuple = tuple(findings or [])
        
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_sessions=tuple(evaluated_sessions),
            findings=finding_tuple,
            violation_count=sum(1 for f in finding_tuple if f.severity >= 0.5),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GovernanceIdentity",
    "GovernanceFinding",
    "ExplanationGovernance",
]