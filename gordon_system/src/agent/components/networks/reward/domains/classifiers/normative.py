# Multi-Domain Reward Engine - Normative Classifier (Phase 4.10.5)
# ================================================================

"""
NormativeRewardClassifier for Phase 4.10.5.

This classifier identifies normative reward: rewards that evaluate consistency
with internal principles, constraints, policies, architectural rules, and
ethical frameworks.
"""

from __future__ import annotations

from typing import Tuple, Optional

from ..domain import DomainType
from .base import BaseRewardClassifier, ClassifierResult


class NormativeRewardClassifier(BaseRewardClassifier):
    """
    Classify rewards as normative (principle/policy aligned).
    
    CLASSIFICATION-LAW-001: This classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: No motivation is inferred.
    CLASSIFICATION-LAW-008: No executive priorities are inferred.
    
    NORMATIVE REWARD SOURCES:
        - Consistency with internal principles
        - Constraint adherence
        - Policy compliance
        - Architectural rules
        - Ethical frameworks
    
    NOT RESPONSIBLE FOR:
        - Reward estimation (handled by Phase 4.10.3/4)
        - Motivation generation
        - Executive decisions
    """
    
    @property
    def domain_type(self) -> DomainType:
        """Return the domain type this classifier handles."""
        return DomainType.NORMATIVE
    
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """
        Classify rewards as normative.
        
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
        
        normative_indicators = [
            "principle_consistency",
            "constraint_adherence",
            "policy_compliance",
            "architectural_rules",
            "ethical_frameworks",
            "internal_principles",
            "governance_aligned",
            "regulatory_compliant",
            "standard_conforming",
            "rule_adherent",
        ]
        
        supporting_estimates: list[str] = []
        confidence_factors: list[float] = []
        
        for estimate in reward_estimates:
            if not isinstance(estimate, dict):
                continue
            
            estimate_id = estimate.get("estimate_id", "")
            magnitude = float(estimate.get("magnitude", 0.0))
            
            text_context = str(estimate).lower()
            is_normative = any(indicator in text_context for indicator in normative_indicators)
            
            if is_normative:
                supporting_estimates.append(estimate_id)
                confidence_factors.append(min(1.0, abs(magnitude) / 2.0 + 0.5))
        
        trace += ("ESTIMATES_ANALYZED",)
        
        if not supporting_estimates:
            findings.append("NO_NORMATIVE_INDICATORS_FOUND")
            return ClassifierResult(
                domain_type=DomainType.NORMATIVE,
                confidence=0.5,
                uncertainty=0.5,
                findings=tuple(findings),
                trace=trace + ("CLASSIFICATION_COMPLETE",),
            )
        
        avg_confidence = (
            sum(confidence_factors) / len(confidence_factors)
            if confidence_factors else 0.5
        )
        
        findings.append(f"FOUND_{len(supporting_estimates)}_NORMATIVE_ESTIMATES")
        
        trace += ("CLASSIFICATION_COMPLETE",)
        
        return ClassifierResult(
            domain_type=DomainType.NORMATIVE,
            confidence=avg_confidence,
            uncertainty=1.0 - avg_confidence,
            supporting_estimates=tuple(supporting_estimates),
            findings=tuple(findings),
            trace=trace,
        )