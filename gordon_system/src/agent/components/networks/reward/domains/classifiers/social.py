# Multi-Domain Reward Engine - Social Classifier (Phase 4.10.5)
# =============================================================

"""
SocialRewardClassifier for Phase 4.10.5.

This classifier identifies social reward: rewards that originate from
cooperation, trust, communication, approval, and shared goals.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..domain import DomainType
from .base import BaseRewardClassifier, ClassifierResult


class SocialRewardClassifier(BaseRewardClassifier):
    """
    Classify rewards as social (interpersonal interactions).
    
    CLASSIFICATION-LAW-001: This classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: No motivation is inferred.
    CLASSIFICATION-LAW-008: No executive priorities are inferred.
    
    SOCIAL REWARD SOURCES:
        - Cooperation
        - Trust
        - Communication
        - Approval
        - Shared goals
        - Relationship maintenance
    
    NOT RESPONSIBLE FOR:
        - Reward estimation (handled by Phase 4.10.3/4)
        - Motivation generation
        - Executive decisions
    """
    
    @property
    def domain_type(self) -> DomainType:
        """Return the domain type this classifier handles."""
        return DomainType.SOCIAL
    
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """
        Classify rewards as social.
        
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
        
        social_indicators = [
            "cooperation",
            "trust",
            "communication",
            "approval",
            "shared_goal",
            "relationship_maintenance",
            "social_interact",
            "group_align",
            "mutual_benefit",
            "collaboration",
            "partnership",
            "harmony",
        ]
        
        supporting_estimates: list[str] = []
        confidence_factors: list[float] = []
        
        for estimate in reward_estimates:
            if not isinstance(estimate, dict):
                continue
            
            estimate_id = estimate.get("estimate_id", "")
            magnitude = float(estimate.get("magnitude", 0.0))
            
            text_context = str(estimate).lower()
            is_social = any(indicator in text_context for indicator in social_indicators)
            
            if is_social:
                supporting_estimates.append(estimate_id)
                confidence_factors.append(min(1.0, abs(magnitude) / 2.0 + 0.5))
        
        trace += ("ESTIMATES_ANALYZED",)
        
        if not supporting_estimates:
            findings.append("NO_SOCIAL_INDICATORS_FOUND")
            return ClassifierResult(
                domain_type=DomainType.SOCIAL,
                confidence=0.5,
                uncertainty=0.5,
                findings=tuple(findings),
                trace=trace + ("CLASSIFICATION_COMPLETE",),
            )
        
        avg_confidence = (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors else 0.5
        )
        
        findings.append(f"FOUND_{len(supporting_estimates)}_SOCIAL_ESTIMATES")
        
        trace += ("CLASSIFICATION_COMPLETE",)
        
        return ClassifierResult(
            domain_type=DomainType.SOCIAL,
            confidence=avg_confidence,
            uncertainty=1.0 - avg_confidence,
            supporting_estimates=tuple(supporting_estimates),
            findings=tuple(findings),
            trace=trace,
        )