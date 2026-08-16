# Multi-Domain Reward Engine - Base Classifier (Phase 4.10.5)
# ============================================================

"""
Base classifier for Phase 4.10.5 domain-specific reward classification.

This module defines the abstract base class that all domain classifiers must
implement. Each classifier owns exactly one semantic domain.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Optional

from ..domain import RewardDomain, DomainType


@dataclass(frozen=True)
class ClassifierResult:
    """
    Result of a classification operation.
    
    PROPERTIES:
        • domain: The classified reward domain (if classification succeeded)
        • confidence: Confidence in the classification (0.0-1.0)
        • uncertainty: Uncertainty in the classification (0.0-1.0)
        • findings: List of key findings from classification
        • trace: Trace of operations for provenance
    
    CLASSIFICATION-LAW-002: Classification preserves Reward Estimates.
    CLASSIFICATION-LAW-003: Classification preserves provenance.
    CLASSIFICATION-LAW-004: Classification preserves confidence.
    CLASSIFICATION-LAW-005: Classification preserves uncertainty.
    """
    
    domain_type: Optional[DomainType] = None
    """The classified domain type (None if classification failed)."""
    
    confidence: float = 0.0
    """Confidence in the classification (0.0-1.0)."""
    
    uncertainty: float = 1.0 - confidence
    """Uncertainty in the classification (0.0-1.0)."""
    
    supporting_estimates: Tuple[str, ...] = field(default_factory=tuple)
    """Reference IDs for supporting reward estimates."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from classification process."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Trace of operations for provenance."""
    
    @property
    def is_valid(self) -> bool:
        """Check if classification result is valid."""
        return self.domain_type is not None and 0.0 <= self.confidence <= 1.0
    
    def to_domain(self) -> RewardDomain:
        """
        Convert this result to a RewardDomain.
        
        Returns:
            New RewardDomain instance
            
        Raises:
            ValueError: If classification result is invalid
        """
        if self.domain_type is None:
            raise ValueError("Cannot convert invalid classifier result to domain")
        
        return RewardDomain(
            domain_type=self.domain_type,
            supporting_estimates=self.supporting_estimates,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance="classifier_result",
        )
    
    def update_confidence(self, new_confidence: float) -> ClassifierResult:
        """Return a copy with updated confidence."""
        if not (0.0 <= new_confidence <= 1.0):
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {new_confidence}")
        
        return ClassifierResult(
            domain_type=self.domain_type,
            confidence=new_confidence,
            uncertainty=1.0 - new_confidence,
            supporting_estimates=self.supporting_estimates,
            findings=self.findings,
            trace=self.trace,
        )


class BaseRewardClassifier(ABC):
    """
    Abstract base class for all reward domain classifiers.
    
    CLASSIFICATION-LAW-001: Each classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: Classification shall never infer motivation.
    CLASSIFICATION-LAW-008: Classification shall never infer executive priorities.
    
    PROPERTIES:
        • domain_type: The single semantic domain this classifier handles
        • classification_rules: Rules for how to classify rewards into this domain
    
    NOT RESPONSIBLE FOR:
        • Motivation generation
        • Executive decisions
        • State modification
    """
    
    @property
    @abstractmethod
    def domain_type(self) -> DomainType:
        """Get the domain type that this classifier handles."""
        pass
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.__class__.__name__}→{self.domain_type.value}"
    
    @abstractmethod
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """
        Classify a set of reward estimates into this domain.
        
        Args:
            reward_estimates: Reward estimates to classify
            evidence_state: Optional additional evidence state
            
        Returns:
            ClassifierResult with the classified domain or failure indication
            
        CLASSIFICATION-LAW-002: Classification preserves Reward Estimates.
        CLASSIFICATION-LAW-003: Classification preserves provenance.
        """
        pass
    
    def validate_estimates(self, estimates: Tuple[dict, ...]) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate a set of reward estimates before classification.
        
        Args:
            estimates: Reward estimates to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not isinstance(estimates, tuple):
            issues.append("ESTIMATES_NOT_TUPLE")
            return False, tuple(issues)
        
        for i, est in enumerate(estimates):
            if not isinstance(est, dict):
                issues.append(f"ESTIMATE_{i}_NOT_DICT")
        
        return len(issues) == 0, tuple(issues)


# =============================================================================
# PRE-BUILT CLASSIFIERS (for common use cases)
# =============================================================================

class NullClassifier(BaseRewardClassifier):
    """
    A classifier that always returns None (no classification).
    
    Used when a domain classifier is not configured or needed.
    """
    
    @property
    def domain_type(self) -> DomainType:
        return DomainType.UNKNOWN
    
    def classify(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> ClassifierResult:
        """Return no classification."""
        return ClassifierResult(
            findings=("NULL_CLASSIFIER",),
            trace=("CLASSIFICATION_SKIPPED",),
        )