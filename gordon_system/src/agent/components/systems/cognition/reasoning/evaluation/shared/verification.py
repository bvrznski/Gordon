# Objective Verification - Phase 7.23
# ====================================

"""
Objective Verification for Gordon's Evaluation Reasoning subsystem.

Verification evaluates:
- Expected outcomes vs observed outcomes
- Acceptance thresholds
- Constraint satisfaction
- Termination validity
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class VerificationResultKind(Enum):
    """Kinds of verification results."""
    
    SATISFIED = "satisfied"     # All objectives met
    PARTIAL = "partial"         # Some objectives met
    FAILED = "failed"           # No objectives met
    INVALID = "invalid"         # Cannot verify (missing information)


@dataclass(frozen=True)
class VerificationEvidence:
    """
    Evidence supporting or contradicting an objective.
    
    Each piece of evidence contains:
        - Evidence type and description
        - Supporting or refuting nature
        - Strength estimate
        - Timestamps
    
    Evidence remains explicit and inspectable.
    """
    
    evidence_id: str                  # Unique evidence identifier
    evidence_type: str                # Type of evidence (observation, measurement, etc.)
    description: str                  # Human-readable description
    supports_objective: bool          # Does this support the objective?
    strength: float = 1.0             # Confidence in this evidence (0.0-1.0)
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ObjectiveVerification:
    """
    An objective verification result.
    
    A verification contains:
        - Verification identity
        - Evaluated objectives
        - Supporting evidence
        - Verification result
        - Provenance tracking
    
    Verifications remain explicit and independently inspectable.
    """
    
    # Identity
    verification_id: str              # Unique verification identifier
    semantic_identity: str            # Semantic identity for traceability
    
    # Evaluated objective
    evaluated_objective: Dict[str, Any] = field(default_factory=dict)  # Objective info
    
    # Evidence
    supporting_evidence: List[VerificationEvidence] = field(default_factory=list)
    
    # Verification result
    verification_result: Optional[VerificationResultKind] = None
    acceptance_status: Optional[str] = None  # "accepted", "rejected", "pending"
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_verification_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def evidence_count(self) -> int:
        """Return number of evidence items."""
        return len(self.supporting_evidence)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_objective: Dict[str, Any],
        evidence: List[VerificationEvidence],
        origin_context: str = "unknown",
        source_verification_id: Optional[str] = None,
    ) -> ObjectiveVerification:
        """Create a new objective verification."""
        # Count supporting vs refuting evidence
        supporting_count = sum(1 for e in evidence if e.supports_objective)
        total_count = len(evidence)
        
        if total_count == 0:
            result = VerificationResultKind.INVALID
            status = "pending"
        elif supporting_count > total_count * 0.8:  # >80% support
            result = VerificationResultKind.SATISFIED
            status = "accepted"
        elif supporting_count > total_count * 0.2:  # >20% support
            result = VerificationResultKind.PARTIAL
            status = "pending"
        else:
            result = VerificationResultKind.FAILED
            status = "rejected"
        
        return cls(
            verification_id=f"verify:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_objective=dict(evaluated_objective),
            supporting_evidence=list(evidence),
            verification_result=result,
            acceptance_status=status,
            origin_context=origin_context,
            source_verification_id=source_verification_id,
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "VerificationResultKind",
    "VerificationEvidence",
    "ObjectiveVerification",
]