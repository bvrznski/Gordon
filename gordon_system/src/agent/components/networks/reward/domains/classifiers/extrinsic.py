# Multi-Domain Reward Engine - Extrinsic Classifier (Phase 4.10.5)
# ================================================================

"""
ExtrinsicRewardClassifier for Phase 4.10.5.

This classifier identifies extrinsic reward: rewards that originate from
task completion, resource acquisition, objective achievement, and external
evaluation.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..domain import DomainType
from .base import BaseRewardClassifier, ClassifierResult


class ExtrinsicRewardClassifier(BaseRewardClassifier):
    """
    Classify rewards as extrinsic (external outcomes).
    
    CLASSIFICATION-LAW-001: This classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: No motivation is inferred.
    CLASSIFICATION-LAW-008: No executive priorities are inferred.
    
    EXTRINSIC REWARD SOURCES:
        - Task completion
        - Resource acquisition
        - Objective achievement
        - Environmental success
        - External evaluation
    
    NOT RESPONSIBLE FOR:
        - Reward estimation (handled by Phase 4.10.3/4)
        - Motivation generation
        - Executive decisions
    """
    
    @property
    def domain_type(self) -> DomainType:
        """Return the domain type this classifier handles."""
        return DomainType.EXTRINSIC
    
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """
        Classify rewards as extrinsic.
        
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
        
        # Extrinsic reward indicators
        extrinsic_indicators = [
            "task_completion",
            "resource_acquisition",
            "objective_achievement",
            "environmental_success",
            "external_evaluation",
            "goal_achieved",
            "target_met",
            "outcome_positive",
            "result_satisfactory",
            "performance_high",
        ]
        
        supporting_estimates: list[str] = []
        confidence_factors: list[float] = []
        
        for estimate in reward_estimates:
            if not isinstance(estimate, dict):
                continue
            
            estimate_id = estimate.get("estimate_id", "")
            magnitude = float(estimate.get("magnitude", 0.0))
            source = estimate.get("source", "")
            
            # Check for extrinsic indicators
            text_context = str(estimate).lower()
            is_extrinsic = any(indicator in text_context for indicator in extrinsic_indicators)
            
            # External sources indicate extrinsic reward
            is_external_source = (
                "environment" in source.lower() or 
                "external" in source.lower() or
                "task" in source.lower()
            )
            
            if is_extrinsic or is_external_source:
                supporting_estimates.append(estimate_id)
                confidence_factors.append(min(1.0, abs(magnitude) / 2.0 + 0.5))
        
        trace += ("ESTIMATES_ANALYZED",)
        
        if not supporting_estimates:
            findings.append("NO_EXTRINSIC_INDICATORS_FOUND")
            return ClassifierResult(
                domain_type=DomainType.EXTRINSIC,
                confidence=0.5,
                uncertainty=0.5,
                findings=tuple(findings),
                trace=trace + ("CLASSIFICATION_COMPLETE",),
            )
        
        avg_confidence = (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors else 0.5
        )
        
        findings.append(f"FOUND_{len(supporting_estimates)}_EXTRINSIC_ESTIMATES")
        
        trace += ("CLASSIFICATION_COMPLETE",)
        
        return ClassifierResult(
            domain_type=DomainType.EXTRINSIC,
            confidence=avg_confidence,
            uncertainty=1.0 - avg_confidence,
            supporting_estimates=tuple(supporting_estimates),
            findings=tuple(findings),
            trace=trace,
        )