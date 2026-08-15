# Executive Evidence Gap Demand Types
# ====================================

"""
Types for assessing evidence gap demand.

An evidence gap must include the required evidence and recommended source.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveEvidenceGap:
    """
    A gap in required evidence for executive assessment.
    
    An evidence gap remains explicit - it does not fabricate certainty.
    """
    
    gap_kind: str = "unknown"
    required_evidence_description: str = ""
    requesting_purpose: str = ""
    affected_program_id: str = ""
    affected_task_set_id: str = ""
    blocking_status: bool = False
    confidence_impact_class: str = "unknown"
    completeness_impact_class: str = "unknown"
    recommended_source: str = ""
    authority_required: str = ""


@dataclass(frozen=True)
class ExecutiveEvidenceGapDemand:
    """
    Demand contributed by evidence gaps.
    
    Evidence-gap demand must remain distinct from conflict severity.
    """
    
    gap_count: int = 0
    overall_gap_class: str = "unknown"
    gap_kinds: Tuple[str, ...] = ()
    recommendations: Tuple[str, ...] = ()


__all__: Tuple[str, ...] = (
    "ExecutiveEvidenceGap",
    "ExecutiveEvidenceGapDemand",
)