# Obligation Analysis - Phase 7.47 Part 1
# ========================================

"""
Obligation Contract.

Obligation analysis evaluates:
    - mandatory duties
    - prohibited actions
    - conditional duties
    - reporting obligations
    - retention obligations
    - compliance deadlines

Obligations remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class Obligation:
    """
    A legal obligation requiring or prohibiting specific actions.
    
    An obligation includes:
        - Source of the obligation (statute, regulation, etc.)
        - Triggering conditions
        - Required/prohibited action
        - Compliance deadlines
    
    Obligations drive compliance behavior.
    """
    
    # Identity
    obligation_id: str                        # Unique identifier
    
    # Source
    legal_source_id: str                      # Which source creates this?
    source_type: str                          # e.g., "statute", "regulation"
    
    # Content
    description: str = ""                     # What does the obligation require/prohibit?
    action_required: Tuple[str, ...] = ()     # Required actions
    actions_prohibited: Tuple[str, ...] = ()  # Prohibited actions
    
    # Triggering conditions
    triggering_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    deadline_utc: Optional[float] = None      # When must compliance occur?
    grace_period_seconds: float = 0           # Grace period after deadline
    
    # Status
    is_active: bool = True                    # Is this obligation currently active?
    has_been_fulfilled: bool = False          # Has it been met?
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_due(self) -> bool:
        """Check if deadline has passed."""
        if self.deadline_utc is None:
            return False
        return time.time() > self.deadline_utc
    
    @classmethod
    def create(
        cls,
        legal_source_id: str,
        source_type: str,
        description: str,
        action_required: Optional[List[str]] = None,
        actions_prohibited: Optional[List[str]] = None,
    ) -> Obligation:
        """Create a new obligation."""
        return cls(
            obligation_id=f"obligation:{uuid.uuid4().hex[:16]}",
            legal_source_id=legal_source_id,
            source_type=source_type,
            description=description,
            action_required=tuple(action_required or []),
            actions_prohibited=tuple(actions_prohibited or []),
        )


@dataclass(frozen=True)
class ObligationAnalysis:
    """
    Analysis of applicable obligations for a legal question.
    
    Includes identification of all obligations and assessment
    of compliance status.
    """
    
    # Identity
    analysis_id: str                          # Unique identifier
    
    # Input
    legal_question: str                       # Question being analyzed
    factual_context: Dict[str, Any] = field(default_factory=dict)  # Facts
    
    # Analysis results
    applicable_obligations: Tuple[Obligation, ...] = ()
    
    # Compliance assessment
    compliance_status: Optional[str] = None   # e.g., "compliant", "partial", "non-compliant"
    violations_detected: Tuple[str, ...] = ()  # Which obligations violated?
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legal_question: str,
        factual_context: Optional[Dict[str, Any]] = None,
    ) -> ObligationAnalysis:
        """Create a new obligation analysis."""
        return cls(
            analysis_id=f"obligation_analysis:{uuid.uuid4().hex[:16]}",
            legal_question=legal_question,
            factual_context=factual_context or {},
        )
    
    def with_applicable_obligations(self, obligations: List[Obligation]) -> ObligationAnalysis:
        """Return a copy with updated applicable obligations."""
        return dataclass_replace(
            self,
            applicable_obligations=tuple(obligations),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Obligation",
    "ObligationAnalysis",
]