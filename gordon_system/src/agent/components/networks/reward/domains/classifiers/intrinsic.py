# Multi-Domain Reward Engine - Intrinsic Classifier (Phase 4.10.5)
# ================================================================

"""
IntrinsicRewardClassifier for Phase 4.10.5.

This classifier identifies intrinsic reward: rewards that originate from
problem solving, understanding, mastery, curiosity satisfaction, and internal
coherence without external reinforcement.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..domain import DomainType, RewardDomain
from .base import BaseRewardClassifier, ClassifierResult


class IntrinsicRewardClassifier(BaseRewardClassifier):
    """
    Classify rewards as intrinsic (internal to the agent).
    
    CLASSIFICATION-LAW-001: This classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: No motivation is inferred.
    CLASSIFICATION-LAW-008: No executive priorities are inferred.
    
    INTRINSIC REWARD SOURCES:
        - Problem solving
        - Understanding / comprehension
        - Mastery of skills
        - Curiosity satisfaction  
        - Internal coherence
        - Creative generation
    
    NOT RESPONSIBLE FOR:
        - Reward estimation (handled by Phase 4.10.3/4)
        - Motivation generation
        - Executive decisions
    """
    
    @property
    def domain_type(self) -> DomainType:
        """Return the domain type this classifier handles."""
        return DomainType.INTRINSIC
    
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """
        Classify rewards as intrinsic.
        
        Args:
            reward_estimates: Reward estimates to classify
            evidence_state: Optional additional evidence state
            
        Returns:
            ClassifierResult with the classified domain
        """
        trace: Tuple[str, ...] = ("CLASSIFIER_START",)
        findings: list[str] = []
        
        # Validate input
        is_valid, issues = self.validate_estimates(reward_estimates)
        if not is_valid:
            trace += ("VALIDATION_FAILED",)
            return ClassifierResult(
                domain_type=None,
                confidence=0.0,
                uncertainty=1.0,
                findings=tuple(issues),
                trace=trace,
            )
        
        trace += ("INPUT_VALIDATED",)
        
        # Intrinsic reward indicators
        intrinsic_indicators = [
            "problem_solving",
            "understanding",
            "mastery",
            "comprehension",
            "internal_coherence",
            "creative_generation",
            "self_directed_learning",
            "curiosity_satisfaction",
            "concept_formation",
        ]
        
        supporting_estimates: list[str] = []
        confidence_factors: list[float] = []
        
        for estimate in reward_estimates:
            if not isinstance(estimate, dict):
                continue
            
            estimate_id = estimate.get("estimate_id", "")
            magnitude = float(estimate.get("magnitude", 0.0))
            valence = estimate.get("valence", "unknown")
            source = estimate.get("source", "")
            
            # Check for intrinsic indicators in various fields
            text_context = str(estimate).lower()
            is_intrinsic = any(indicator in text_context for indicator in intrinsic_indicators)
            
            # Also consider positive valence and self-referenced sources
            is_positive_valence = valence in ("positive", "rewarding")
            is_self_referenced = "self" in source.lower() or "internal" in source.lower()
            
            if is_intrinsic or (is_positive_valence and is_self_referenced):
                supporting_estimates.append(estimate_id)
                # Higher magnitude = higher confidence
                confidence_factors.append(min(1.0, abs(magnitude) / 2.0 + 0.5))
        
        trace += ("ESTIMATES_ANALYZED",)
        
        if not supporting_estimates:
            findings.append("NO_INTRINSIC_INDICATORS_FOUND")
            return ClassifierResult(
                domain_type=DomainType.INTRINSIC,
                confidence=0.5,  # Default uncertainty
                uncertainty=0.5,
                findings=tuple(findings),
                trace=trace + ("CLASSIFICATION_COMPLETE",),
            )
        
        # Calculate average confidence from supporting estimates
        avg_confidence = (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors else 0.5
        )
        
        findings.append(f"FOUND_{len(supporting_estimates)}_INTRINSIC_ESTIMATES")
        
        trace += ("CLASSIFICATION_COMPLETE",)
        
        return ClassifierResult(
            domain_type=DomainType.INTRINSIC,
            confidence=avg_confidence,
            uncertainty=1.0 - avg_confidence,
            supporting_estimates=tuple(supporting_estimates),
            findings=tuple(findings),
            trace=trace,
        )