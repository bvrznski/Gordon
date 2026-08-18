# Legal Session Descriptor - Phase 7.47 Part 1
# ==============================================

"""
Legal Session Descriptor.

Every legal reasoning process occurs inside a Legal Session.
The session defines:
    - jurisdictions
    - applicable legal sources
    - facts
    - questions
    - requested determinations
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class LegalReasoningKind(Enum):
    """Categories of legal reasoning operations."""
    
    JURISDICTION_ANALYSIS = "jurisdiction_analysis"     # Which jurisdictions apply?
    STATUTORY_ANALYSIS = "statutory_analysis"           # What do statutes require?
    REGULATORY_ANALYSIS = "regulatory_analysis"         # What do regulations require?
    RIGHTS_ANALYSIS = "rights_analysis"                 # What rights are protected?
    OBLIGATION_ANALYSIS = "obligation_analysis"         # What obligations exist?
    COMPLIANCE_ASSESSMENT = "compliance_assessment"     # Is compliance achieved?
    PRECEDENT_ANALYSIS = "precedent_analysis"           # What precedents apply?
    
    # Combined reasoning modes
    LEGAL_INTERPRETATION = "legal_interpretation"
    REGULATORY_COMPLIANCE = "regulatory_compliance"


class LegalLifecycleState(Enum):
    """Legal session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    SOURCE_DISCOVERY = "source_discovery"
    JURISDICTION_IDENTIFICATION = "jurisdiction_identification"
    INTERPRETING = "interpreting"
    ANALYZING = "analyzing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class LegalSessionDescriptor:
    """
    Descriptor exposing legal session metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning kind and mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what legal reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning classification
    reasoning_kind: LegalReasoningKind        # What kind of legal reasoning?
    reasoning_mode: Optional[str] = None      # Mode-specific details
    
    # Lifecycle state
    lifecycle_state: LegalLifecycleState = LegalLifecycleState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Session configuration
    applicable_jurisdictions: Tuple[str, ...] = ()   # Jurisdictions to consider
    legal_question: Optional[str] = None             # The question being answered
    factual_context: Dict[str, Any] = field(default_factory=dict)  # Known facts
    
    # Resulting assessment (populated after completion)
    resulting_assessment: Optional[str] = None       # Final determination
    confidence_score: Optional[float] = None         # Confidence in result
    
    # Provenance
    source_descriptor_id: Optional[str] = None       # If this is a refinement
    origin_context: str = "unknown"                  # Where did reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if reasoning completed."""
        return self.lifecycle_state == LegalLifecycleState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == LegalLifecycleState.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_kind: LegalReasoningKind,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        applicable_jurisdictions: Optional[List[str]] = None,
        legal_question: Optional[str] = None,
    ) -> LegalSessionDescriptor:
        """Create a new legal session descriptor."""
        return cls(
            descriptor_id=f"legal_session:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_kind=reasoning_kind,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            applicable_jurisdictions=tuple(applicable_jurisdictions or []),
            legal_question=legal_question,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: LegalLifecycleState) -> LegalSessionDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == LegalLifecycleState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LegalSessionDescriptor",
    "LegalReasoningKind",
    "LegalLifecycleState",
]