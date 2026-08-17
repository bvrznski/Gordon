# Reasoning Inference - Phase 7.0
# ================================

"""
Canonical Inference Contract.

Inference derives conclusions from available Knowledge.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class InferenceStrategy(Enum):
    """Strategies for performing inference."""
    
    MODUS_PONENS = "modus_ponens"               # If P→Q and P, then Q
    MODUS_TOLLENS = "modus_tollens"             # If P→Q and ¬Q, then ¬P
    HYPOTHETICAL_SYLLOGISM = "hypothetical_syllogism"  # If P→Q and Q→R, then P→R
    DISJUNCTIVE_SYLLOGISM = "disjunctive_syllogism"    # If P∨Q and ¬P, then Q
    ANALYTIC_HIERARCHY = "analytic_hierarchy"   # Hierarchical analysis
    CASE_BASED_REASONING = "case_based_reasoning"  # Past case matching
    PROBABILISTIC_INFERENCE = "probabilistic_inference"  # Bayesian reasoning
    DEDUCTIVE_CHAIN = "deductive_chain"         # Chain of deductive steps
    INDUCTIVE_GENERALIZATION = "inductive_generalization"  # Pattern generalization
    ABDUCTIVE_INFERENCE = "abductive_inference"  # Best explanation


@dataclass(frozen=True)
class Inference:
    """
    Inference derives conclusions from available Knowledge.
    
    An inference contains:
        - Identity and provenance tracking
        - Strategy used for the inference
        - Supporting artifacts (premises, knowledge references)
        - Working assumptions made during inference
        - Generated conclusions
        - Confidence and uncertainty measures
    
    Inference never modifies Knowledge directly;
    it produces inferences that can be reviewed.
    """
    
    # Identity
    inference_id: str                       # Unique inference identifier
    semantic_identity: str                  # Stable identity for replay
    
    # Classification
    inference_strategy: InferenceStrategy   # How was inference performed?
    
    # Supporting context
    supporting_artifacts: Tuple[str, ...]   # References to knowledge artifacts
    assumptions_made: Tuple[str, ...] = ()  # Working assumptions during inference
    
    # Results
    conclusions: Tuple[str, ...]            # What was inferred?
    conclusion_confidence: float = 1.0      # Confidence in each conclusion
    
    # Uncertainty
    epistemic_uncertainty: float = 0.0      # Lack of knowledge
    aleatoric_uncertainty: float = 0.0      # Inherent randomness
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)  # How was this derived?
    
    @property
    def total_uncertainty(self) -> float:
        """Total uncertainty (epistemic + aleatoric)."""
        return self.epistemic_uncertainty + self.aleatoric_uncertainty
    
    @property
    def effective_confidence(self) -> float:
        """Confidence adjusted for total uncertainty."""
        return max(0.0, min(1.0, self.conclusion_confidence * (1 - self.total_uncertainty)))
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        strategy: InferenceStrategy,
        supporting_artifacts: List[str],
        conclusions: List[str],
        assumptions: Optional[List[str]] = None,
        confidence: float = 1.0,
        epistemic_uncertainty: float = 0.0,
        aleatoric_uncertainty: float = 0.0,
    ) -> Inference:
        """Create a new inference."""
        return cls(
            inference_id=f"inference:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            inference_strategy=strategy,
            supporting_artifacts=tuple(supporting_artifacts),
            assumptions_made=tuple(assumptions or []),
            conclusions=tuple(conclusions),
            conclusion_confidence=confidence,
            epistemic_uncertainty=epistemic_uncertainty,
            aleatoric_uncertainty=aleatoric_uncertainty,
            created_at_utc=time.time(),
        )


@dataclass(frozen=True)
class InferenceTrace:
    """
    Trace of inference steps for auditability.
    
    Each trace entry records a single step in the inference chain.
    """
    
    # Identity
    trace_id: str                           # Unique trace identifier
    
    # Step information
    step_number: int                        # Order in inference sequence
    step_kind: str                          # e.g., "premise", "inference", "conclusion"
    
    # Context
    input_artifacts: Tuple[str, ...]        # What went in?
    output_artifacts: Tuple[str, ...]       # What came out?
    
    # Strategy used at this step
    strategy_used: Optional[InferenceStrategy] = None
    
    # Timing
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create_step(
        cls,
        trace_id: str,
        step_number: int,
        step_kind: str,
        inputs: List[str],
        outputs: List[str],
        strategy: Optional[InferenceStrategy] = None,
    ) -> InferenceTrace:
        """Create a new inference trace step."""
        return cls(
            trace_id=trace_id,
            step_number=step_number,
            step_kind=step_kind,
            input_artifacts=tuple(inputs),
            output_artifacts=tuple(outputs),
            strategy_used=strategy,
            timestamp_utc=time.time(),
        )


__all__ = [
    "Inference",
    "InferenceTrace",
    "InferenceStrategy",
]