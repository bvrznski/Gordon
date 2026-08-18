# Cognitive Appraisal - Phase 7.23
# ===============================

"""
Cognitive Appraisal for Gordon's Evaluation Reasoning subsystem.

Appraisal evaluates:
- Overall success (full, partial, none)
- Unexpected outcomes
- System significance
- Future implications
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AppraisalResultKind(Enum):
    """Kinds of appraisal results."""
    
    SUCCESS = "success"                   # Overall success
    PARTIAL_SUCCESS = "partial_success"   # Some objectives met
    FAILURE = "failure"                   # No success
    UNEXPECTED = "unexpected"             # Unexpected outcome


@dataclass(frozen=True)
class AppraisalFinding:
    """
    A single finding in the cognitive appraisal.
    
    Each finding contains:
        - Finding type and description
        - Support strength
        - Relevance to objectives
        - Timestamps
    
    Findings remain explicit and inspectable.
    """
    
    finding_id: str                   # Unique finding identifier
    finding_type: str                 # Type of finding (objective_met, constraint_violated, etc.)
    description: str                  # Human-readable description
    support_strength: float = 1.0     # Strength of this finding (0.0-1.0)
    relevance_to_objectives: str = "high"  # high/medium/low
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class CognitiveAppraisal:
    """
    A cognitive appraisal result.
    
    An appraisal contains:
        - Appraisal identity
        - Evaluation summary (what was evaluated)
        - Overall assessment
        - Supporting findings
        - Provenance tracking
    
    Appraisals remain explicit and independently inspectable.
    """
    
    # Identity
    appraisal_id: str                 # Unique appraisal identifier
    semantic_identity: str            # Semantic identity for traceability
    
    # Evaluation summary
    evaluation_summary: Dict[str, Any] = field(default_factory=dict)  # What was evaluated
    
    # Appraisal result
    overall_assessment: Optional[AppraisalResultKind] = None
    assessment_description: str = ""  # Human-readable explanation
    
    # Findings
    supporting_findings: List[AppraisalFinding] = field(default_factory=list)
    
    # Significance estimates
    success_significance: float = 0.0       # How significant was this outcome?
    failure_significance: float = 0.0       # How problematic was any failure?
    unexpected_significance: float = 0.0    # How surprising were the outcomes?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_appraisal_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def finding_count(self) -> int:
        """Return number of findings."""
        return len(self.supporting_findings)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluation_summary: Dict[str, Any],
        findings: List[AppraisalFinding],
        origin_context: str = "unknown",
        source_appraisal_id: Optional[str] = None,
    ) -> CognitiveAppraisal:
        """Create a new cognitive appraisal."""
        # Determine overall assessment based on findings
        success_count = sum(1 for f in findings if "success" in f.finding_type.lower())
        failure_count = sum(1 for f in findings if "failure" in f.finding_type.lower() or "error" in f.finding_type.lower())
        
        total_found = len(findings)
        if total_found == 0:
            assessment = AppraisalResultKind.UNEXPECTED
            description = "No findings available"
        elif success_count > failure_count * 2:  # Significantly more successes
            assessment = AppraisalResultKind.SUCCESS
            description = f"{success_count} successes, {failure_count} failures"
        elif success_count > 0:
            assessment = AppraisalResultKind.PARTIAL_SUCCESS
            description = f"Partial: {success_count} successes with some issues"
        else:
            assessment = AppraisalResultKind.FAILURE
            description = f"{failure_count} failures detected"
        
        return cls(
            appraisal_id=f"appraisal:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluation_summary=dict(evaluation_summary),
            overall_assessment=assessment,
            assessment_description=description,
            supporting_findings=list(findings),
            success_significance=min(success_count / max(total_found, 1), 1.0),
            failure_significance=min(failure_count / max(total_found, 1), 1.0),
            unexpected_significance=0.0 if total_found > 0 else 1.0,
            origin_context=origin_context,
            source_appraisal_id=source_appraisal_id,
            created_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AppraisalResultKind",
    "AppraisalFinding",
    "CognitiveAppraisal",
]