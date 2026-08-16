# Multi-Domain Reward Engine - Autonomy Classifier (Phase 4.10.5)
# ===============================================================

"""
AutonomyRewardClassifier for Phase 4.10.5.

This classifier identifies autonomy reward: rewards that evaluate independent
problem solving, self-directed behavior, minimal external intervention,
and adaptive self-regulation.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..domain import DomainType
from .base import BaseRewardClassifier, ClassifierResult


class AutonomyRewardClassifier(BaseRewardClassifier):
    """
    Classify rewards as autonomy-related (self-direction).
    
    CLASSIFICATION-LAW-001: This classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: No motivation is inferred.
    CLASSIFICATION-LAW-008: No executive priorities are inferred.
    
    AUTONOMY REWARD SOURCES:
        - Independent problem solving
        - Self-directed behavior
        - Minimal external intervention
        - Adaptive self-regulation
    
    NOT RESPONSIBLE FOR:
        - Reward estimation (handled by Phase 4.10.3/4)
        - Motivation generation
        - Executive decisions
    """
    
    @property
    def domain_type(self) -> DomainType:
        """Return the domain type this classifier handles."""
        return DomainType.AUTONOMY
    
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """
        Classify rewards as autonomy-related.
        
        Args:
            reward_estimates: Reward estimates to classify
            evidence_state: Optional additional evidence state
            
        Returns:
            ClassifierResult with the classified domain
        """
        trace: Tuple[str, ...] = ("CLASSIFIER_START",)
        findings: list[str] = []
        
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
        
        autonomy_indicators = [
            "independent_problem_solving",
            "self_directed_behavior",
            "minimal_external_intervention",
            "adaptive_self_regulation",
            "autonomous_decision",
            "self_initiated_action",
            "independent_execution",
            "self_governance",
            "自主性",  # Japanese for autonomy
        ]
        
        supporting_estimates: list[str] = []
        confidence_factors: list[float] = []
        
        for estimate in reward_estimates:
            if not isinstance(estimate, dict):
                continue
            
            estimate_id = estimate.get("estimate_id", "")
            magnitude = float(estimate.get("magnitude", 0.0))
            
            text_context = str(estimate).lower()
            is_autonomy = any(indicator in text_context for indicator in autonomy_indicators)
            
            if is_autonomy:
                supporting_estimates.append(estimate_id)
                confidence_factors.append(min(1.0, abs(magnitude) / 2.0 + 0.5))
        
        trace += ("ESTIMATES_ANALYZED",)
        
        if not supporting_estimates:
            findings.append("NO_AUTONOMY_INDICATORS_FOUND")
            return ClassifierResult(
                domain_type=DomainType.AUTONOMY,
                confidence=0.5,
                uncertainty=0.5,
                findings=tuple(findings),
                trace=trace + ("CLASSIFICATION_COMPLETE",),
            )
        
        avg_confidence = (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors else 0.5
        )
        
        findings.append(f"FOUND_{len(supporting_estimates)}_AUTONOMY_ESTIMATES")
        
        trace += ("CLASSIFICATION_COMPLETE",)
        
        return ClassifierResult(
            domain_type=DomainType.AUTONOMY,
            confidence=avg_confidence,
            uncertainty=1.0 - avg_confidence,
            supporting_estimates=tuple(supporting_estimates),
            findings=tuple(findings),
            trace=trace,
        )