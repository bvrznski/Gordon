# Multi-Domain Reward Engine - Engine (Phase 4.10.5)
# ===================================================

"""
RewardDomainEngine for Phase 4.10.5.

This engine orchestrates all domain classification, producing immutable
MultiDomainRewardState without modifying any reward estimates from Phase 4.10.3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict

from .domain import DomainType, RewardDomain
from .taxonomy import RewardTaxonomy, DomainClassificationRules
from .classifiers.base import (
    BaseRewardClassifier,
    ClassifierResult,
)
from .classifiers.intrinsic import IntrinsicRewardClassifier
from .classifiers.extrinsic import ExtrinsicRewardClassifier
from .classifiers.social import SocialRewardClassifier
from .classifiers.epistemic import EpistemicRewardClassifier
from .classifiers.competence import CompetenceRewardClassifier
from .classifiers.autonomy import AutonomyRewardClassifier
from .classifiers.curiosity import CuriosityRewardClassifier
from .classifiers.mission import MissionRewardClassifier
from .classifiers.normative import NormativeRewardClassifier
from .profile import RewardProfile, DomainProfile
from .relationships import DomainRelationshipGraph, DomainRelationship
from .state import MultiDomainRewardState


@dataclass(frozen=True)
class RewardDomainEngine:
    """
    Orchestrates domain classification for a set of reward estimates.
    
    DOMAIN-LAW-001: Exactly one canonical RewardDomainEngine shall exist.
    
    PROCESSING PIPELINE (Part 2, Section 5):
        validate request
            ↓
        validate Reward Landscape
            ↓
        classify intrinsic reward
            ↓
        classify extrinsic reward
            ↓
        classify social reward
            ↓
        classify epistemic reward
            ↓
        classify competence reward
            ↓
        classify autonomy reward
            ↓
        classify curiosity reward
            ↓
        classify mission reward
            ↓
        classify normative reward
            ↓
        construct Reward Profiles
            ↓
        construct Domain Graph
            ↓
        construct Multi-Domain Reward State
            ↓
        validation
            ↓
        MultiDomainRewardResult
    
    PROPERTIES:
        • deterministic: Same inputs produce same outputs
        • immutable: No state modifications during evaluation
        • traceable: Full provenance preserved
    
    NOT RESPONSIBLE FOR:
        • Learning (reinforcement, policy updates)
        • Executive decisions
        • Action selection
        • State modification
    """
    
    taxonomy: RewardTaxonomy = field(default_factory=RewardTaxonomy.create_canonical)
    """The reward taxonomy for domain classification."""
    
    rules: DomainClassificationRules = field(
        default_factory=DomainClassificationRules.create_canonical
    )
    """Classification rules for domain assignment."""
    
    def classify_domains(
        self,
        reward_estimates: Tuple[dict, ...],
        evidence_state: Optional[dict] = None,
    ) -> Tuple[Tuple[str, ...], MultiDomainRewardState]:
        """
        Classify all reward domains for a set of estimates.
        
        This is the main entry point for Phase 4.10.5 classification.
        
        Args:
            reward_estimates: Reward estimates to classify into domains
            evidence_state: Optional additional evidence state
            
        Returns:
            Tuple of (trace, MultiDomainRewardState)
        """
        trace: Tuple[str, ...] = ("REQUEST_RECEIVED",)
        
        # Validate estimates
        is_valid, validation_issues = self._validate_estimates(reward_estimates)
        if not is_valid:
            trace += ("VALIDATION_FAILED",)
            return (
                trace,
                MultiDomainRewardState.create_empty("invalid-estimates"),
            )
        
        trace += ("ESTIMATES_VALIDATED",)
        
        # Initialize classifiers (one per domain)
        classifiers: Dict[DomainType, BaseRewardClassifier] = {
            DomainType.INTRINSIC: IntrinsicRewardClassifier(),
            DomainType.EXTRINSIC: ExtrinsicRewardClassifier(),
            DomainType.SOCIAL: SocialRewardClassifier(),
            DomainType.EPISTEMIC: EpistemicRewardClassifier(),
            DomainType.COMPETENCE: CompetenceRewardClassifier(),
            DomainType.AUTONOMY: AutonomyRewardClassifier(),
            DomainType.CURIOSITY: CuriosityRewardClassifier(),
            DomainType.MISSION: MissionRewardClassifier(),
            DomainType.NORMATIVE: NormativeRewardClassifier(),
        }
        
        # Classify each domain
        classified_domains: list[RewardDomain] = []
        for domain_type, classifier in classifiers.items():
            result = self._classify_with_classifier(classifier, reward_estimates)
            
            if result.is_valid:
                trace += (f"{domain_type.value.upper()}_CLASSIFIED",)
                domain = result.to_domain()
                classified_domains.append(domain)
        
        trace += ("DOMAINS_CLASSIFIED",)
        
        # Construct profile
        domain_profiles = tuple(DomainProfile.from_domain(d) for d in classified_domains)
        profile = RewardProfile(
            profile_id="reward_profile",
            revision=0,
            domain_profiles=domain_profiles,
            findings=("PROFILE_CREATED",),
            trace=("DOMAIN_PROFILES_AGGREGATED",),
        )
        
        # Build empty relationship graph (relationships are not automatically computed)
        domain_graph = DomainRelationshipGraph.create_empty()
        
        # Construct final state
        state = MultiDomainRewardState.from_components(
            profile=profile,
            domain_graph=domain_graph,
            state_id=f"reward_state_{len(reward_estimates)}_estimates",
        )
        
        trace += ("STATE_CONSTRUCTED", "VALIDATION_COMPLETED")
        
        return (trace, state)
    
    def _validate_estimates(self, estimates: Tuple[dict, ...]) -> Tuple[bool, Tuple[str, ...]]:
        """Validate reward estimates before classification."""
        issues = []
        
        if not isinstance(estimates, tuple):
            issues.append("ESTIMATES_NOT_TUPLE")
            return False, tuple(issues)
        
        for i, est in enumerate(estimates):
            if not isinstance(est, dict):
                issues.append(f"ESTIMATE_{i}_NOT_DICT")
        
        return len(issues) == 0, tuple(issues)
    
    def _classify_with_classifier(
        self,
        classifier: BaseRewardClassifier,
        reward_estimates: Tuple[dict, ...],
    ) -> ClassifierResult:
        """Classify estimates using a specific classifier."""
        return classifier.classify(reward_estimates)


# =============================================================================
# ALTERNATE ENTRY POINT: Classify single estimate
# =============================================================================

def classify_single_estimate(
    estimate: dict,
    taxonomy: Optional[RewardTaxonomy] = None,
) -> Tuple[DomainType, float]:
    """
    Classify a single estimate and return (domain_type, confidence).
    
    This is a convenience function for simple use cases.
    
    Args:
        estimate: Single reward estimate to classify
        taxonomy: Taxonomy instance (optional)
        
    Returns:
        Tuple of (most likely domain type, confidence score)
    """
    engine = RewardDomainEngine()
    result = engine.classify_domains((estimate,))
    
    state = result[1]
    if not state.has_domains:
        return (DomainType.UNKNOWN, 0.5)
    
    # Get the domain with highest confidence
    profiles = sorted(
        state.reward_profile.domain_profiles,
        key=lambda p: p.confidence,
        reverse=True
    )
    
    if profiles:
        top = profiles[0]
        return (top.domain_type, top.confidence)
    
    return (DomainType.UNKNOWN, 0.5)


__all__ = [
    "RewardDomainEngine",
    "classify_single_estimate",
]