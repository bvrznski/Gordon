# Reasoning Conclusion - Phase 7.0
# ==================================

"""
Canonical Conclusion Contract.

Conclusions summarize reasoning results without becoming beliefs automatically.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class ReasoningConclusion:
    """
    A conclusion summarizing completed reasoning.
    
    A conclusion contains:
        - Identity and tracking
        - Supporting inferences that led to it
        - Resulting assertions (proposed knowledge updates)
        - Confidence and uncertainty measures
        - Provenance
    
    Conclusions never become beliefs automatically;
    they propose changes to be evaluated by belief revision.
    """
    
    # Identity
    conclusion_id: str                      # Unique identifier
    semantic_identity: str                  # Stable identity for comparison
    
    # Content
    summary: str                            # What was concluded?
    conclusion_type: str = "general"        # e.g., "diagnosis", "strategy", "prediction"
    
    # Supporting evidence
    supporting_inferences: Tuple[str, ...]  # Which inferences support this?
    intermediate_conclusions: Tuple[str, ...] = ()  # Intermediate steps
    
    # Resulting assertions (proposals)
    resulting_assertions: Tuple[str, ...] = ()  # What should be believed/acted on?
    
    # Assessment
    confidence: float = 0.5                 # Confidence in the conclusion
    uncertainty: float = 0.3                # Remaining uncertainty
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    generated_by_reasoning: str = "unknown"  # Which reasoning produced this?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_confident(self) -> bool:
        """Check if conclusion has high confidence."""
        return self.confidence >= 0.85
    
    @property
    def is_definitive(self) -> bool:
        """Check if conclusion is definitive (high confidence, low uncertainty)."""
        return self.confidence >= 0.9 and self.uncertainty <= 0.1
    
    @classmethod
    def create(
        cls,
        summary: str,
        semantic_identity: str,
        supporting_inferences: List[str],
        resulting_assertions: Optional[List[str]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.3,
        generated_by_reasoning: str = "unknown",
    ) -> ReasoningConclusion:
        """Create a new conclusion."""
        return cls(
            conclusion_id=f"conclusion:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            summary=summary,
            supporting_inferences=tuple(supporting_inferences),
            resulting_assertions=tuple(resulting_assertions or []),
            confidence=confidence,
            uncertainty=uncertainty,
            generated_by_reasoning=generated_by_reasoning,
        )


@dataclass(frozen=True)
class ConclusionTrace:
    """
    Trace of conclusion derivation steps.
    
    Each entry records a step in how the final conclusion was reached.
    """
    
    # Identity
    trace_id: str                           # Unique identifier
    
    # Step information
    step_number: int                        # Order in sequence
    step_kind: str                          # e.g., "premise", "intermediate", "final"
    
    # Content
    content_summary: str                    # Summary of what happened at this step
    
    # Context
    premises_used: Tuple[str, ...] = ()     # What was used as input?
    conclusions_reached: Tuple[str, ...] = ()  # What came out?
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_step(
        cls,
        trace_id: str,
        step_number: int,
        step_kind: str,
        premises: List[str],
        conclusions: List[str],
        content_summary: str = "",
    ) -> ConclusionTrace:
        """Create a new trace entry."""
        return cls(
            trace_id=trace_id,
            step_number=step_number,
            step_kind=step_kind,
            content_summary=content_summary or f"Step {step_number}",
            premises_used=tuple(premises),
            conclusions_reached=tuple(conclusions),
        )


@dataclass(frozen=True)
class ConclusionEvaluation:
    """
    Evaluation of a conclusion's quality and reliability.
    
    An evaluation considers:
        - Logical soundness
        - Evidence strength
        - Consistency with known knowledge
        - Completeness of reasoning trace
    """
    
    # Identity
    evaluation_id: str                      # Unique identifier
    
    # Target
    evaluated_conclusion: str               # Which conclusion was evaluated?
    
    # Quality metrics
    logical_soundness: float = 1.0          # Was the reasoning valid?
    evidence_strength: float = 0.5          # How strong is the evidence?
    consistency_with_known: float = 1.0     # Consistency with existing knowledge
    
    # Completeness
    trace_completeness: float = 1.0         # Is the reasoning complete?
    unsupported_count: int = 0              # Number of unsupported steps
    
    # Overall assessment
    is_reliable: bool = False               # Is this conclusion trustworthy?
    reliability_reasons: Tuple[str, ...] = ()  # Why/why not?
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def overall_score(self) -> float:
        """Combined reliability score."""
        return (
            self.logical_soundness * 0.2 +
            self.evidence_strength * 0.4 +
            self.consistency_with_known * 0.3 +
            self.trace_completeness * 0.1
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if conclusion passes all quality checks."""
        return (
            self.logical_soundness >= 0.8 and
            self.evidence_strength >= 0.5 and
            self.consistency_with_known >= 0.7 and
            self.unsupported_count == 0
        )
    
    @classmethod
    def create(
        cls,
        evaluated_conclusion_id: str,
    ) -> ConclusionEvaluation:
        """Create a new evaluation."""
        return cls(
            evaluation_id=f"evaluation:{uuid.uuid4().hex[:16]}",
            evaluated_conclusion=evaluated_conclusion_id,
        )


__all__ = [
    "ReasoningConclusion", 
    "ConclusionTrace", 
    "ConclusionEvaluation",
]