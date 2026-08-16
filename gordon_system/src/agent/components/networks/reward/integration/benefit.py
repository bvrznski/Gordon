# Benefit Integrators for Reward Evaluation & Value Integration Engine (Phase 4.10.3)
# ==================================================================================================

"""
Benefit integrators compute semantic contributions to reward estimation.

Each benefit integrator handles one domain of benefit contribution, preserving
decomposition and traceability as required by Phase 4.10.3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .base import BaseBenefitIntegrator, IntegrationResult


# =============================================================================
# GOAL BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class GoalBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates benefit from goal progress.
    
    Computes how much advancement toward strategic objectives contributes
    to overall reward estimation.
    
    BENEFIT-LAW-002: Goal benefit remains independent
    BENEFIT-LAW-003: Every contributor remains individually represented
    """
    
    weight: float = 1.0
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate goal-based benefit contributions."""
        trace: Tuple[str, ...] = ("GOAL_BENEFIT_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_benefit = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                # Check for goal-related evidence
                context = evidence.get("context", [])
                
                is_goal_evidence = any(
                    "goal" in str(c).lower() 
                    for c in context
                )
                
                if is_goal_evidence and evidence.get("relationship") == "supports_reward":
                    benefit_value = self._compute_benefit(evidence)
                    total_benefit += benefit_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("GOAL_BENEFIT_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_benefit,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_benefit(self, evidence: dict) -> float:
        """Compute benefit value from a single piece of goal evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_reward":
            return 1.0
        elif relationship == "contradicts_reward":
            return -0.5
        else:
            return 0.0


# =============================================================================
# KNOWLEDGE BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class KnowledgeBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates benefit from knowledge acquisition.
    
    Computes how much learning and understanding contributes to reward.
    
    BENEFIT-LAW-002: Knowledge benefit remains independent
    """
    
    weight: float = 0.8
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate knowledge-based benefit contributions."""
        trace: Tuple[str, ...] = ("KNOWLEDGE_BENEFIT_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_benefit = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_knowledge_evidence = "knowledge" in kind.lower() or "learning" in kind.lower()
                
                if is_knowledge_evidence and evidence.get("relationship") == "supports_reward":
                    benefit_value = self._compute_benefit(evidence)
                    total_benefit += benefit_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("KNOWLEDGE_BENEFIT_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_benefit,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_benefit(self, evidence: dict) -> float:
        """Compute benefit value from knowledge evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_reward":
            return 1.0
        elif relationship == "contradicts_reward":
            return -0.5
        else:
            return 0.0


# =============================================================================
# EFFICIENCY BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class EfficiencyBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates benefit from resource efficiency.
    
    Computes how much reduced resource expenditure contributes to reward.
    
    BENEFIT-LAW-002: Efficiency benefit remains independent
    """
    
    weight: float = 0.6
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate efficiency-based benefit contributions."""
        trace: Tuple[str, ...] = ("EFFICIENCY_BENEFIT_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_benefit = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_efficiency_evidence = "efficiency" in kind.lower() or "resource" in kind.lower()
                
                if is_efficiency_evidence and evidence.get("relationship") == "supports_reward":
                    benefit_value = self._compute_benefit(evidence)
                    total_benefit += benefit_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("EFFICIENCY_BENEFIT_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_benefit,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_benefit(self, evidence: dict) -> float:
        """Compute benefit value from efficiency evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_reward":
            return 1.0
        elif relationship == "contradicts_reward":
            return -0.5
        else:
            return 0.0


# =============================================================================
# RESOURCE BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class ResourceBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates benefit from resource acquisition.
    
    Computes how much gaining new resources contributes to reward.
    
    BENEFIT-LAW-002: Resource benefit remains independent
    """
    
    weight: float = 0.7
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate resource-based benefit contributions."""
        trace: Tuple[str, ...] = ("RESOURCE_BENEFIT_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_benefit = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_resource_evidence = "resource" in kind.lower() and "gain" in kind.lower()
                
                if is_resource_evidence and evidence.get("relationship") == "supports_reward":
                    benefit_value = self._compute_benefit(evidence)
                    total_benefit += benefit_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("RESOURCE_BENEFIT_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_benefit,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_benefit(self, evidence: dict) -> float:
        """Compute benefit value from resource evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_reward":
            return 1.0
        elif relationship == "contradicts_reward":
            return -0.5
        else:
            return 0.0


# =============================================================================
# STABILITY BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class StabilityBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates benefit from system stability.
    
    Computes how much maintaining or improving system stability contributes to reward.
    
    BENEFIT-LAW-002: Stability benefit remains independent
    """
    
    weight: float = 0.5
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate stability-based benefit contributions."""
        trace: Tuple[str, ...] = ("STABILITY_BENEFIT_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_benefit = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_stability_evidence = "stability" in kind.lower() or "predict" in kind.lower()
                
                if is_stability_evidence and evidence.get("relationship") == "supports_reward":
                    benefit_value = self._compute_benefit(evidence)
                    total_benefit += benefit_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("STABILITY_BENEFIT_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_benefit,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_benefit(self, evidence: dict) -> float:
        """Compute benefit value from stability evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_reward":
            return 1.0
        elif relationship == "contradicts_reward":
            return -0.5
        else:
            return 0.0


# =============================================================================
# SOCIAL BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class SocialBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates benefit from social interactions.
    
    Computes how much positive social feedback contributes to reward.
    
    BENEFIT-LAW-002: Social benefit remains independent
    """
    
    weight: float = 0.6
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate social-based benefit contributions."""
        trace: Tuple[str, ...] = ("SOCIAL_BENEFIT_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_benefit = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_social_evidence = "social" in kind.lower() or "approve" in kind.lower()
                
                if is_social_evidence and evidence.get("relationship") == "supports_reward":
                    benefit_value = self._compute_benefit(evidence)
                    total_benefit += benefit_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("SOCIAL_BENEFIT_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_benefit,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_benefit(self, evidence: dict) -> float:
        """Compute benefit value from social evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_reward":
            return 1.0
        elif relationship == "contradicts_reward":
            return -0.5
        else:
            return 0.0


# =============================================================================
# COMPOSITE BENEFIT INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class CompositeBenefitIntegrator(BaseBenefitIntegrator):
    """
    Integrates all benefit sources into a composite estimate.
    
    Preserves decomposition of individual benefits while providing aggregate value.
    
    PROPERTIES:
        • goal_integrator: Goal benefit integrator
        • knowledge_integrator: Knowledge benefit integrator
        • efficiency_integrator: Efficiency benefit integrator
        • resource_integrator: Resource benefit integrator
        • stability_integrator: Stability benefit integrator
        • social_integrator: Social benefit integrator
    
    NOT RESPONSIBLE FOR:
        • Modifying individual integrators
        • Changing integration weights after construction
    """
    
    goal_integrator: GoalBenefitIntegrator = field(default_factory=GoalBenefitIntegrator)
    knowledge_integrator: KnowledgeBenefitIntegrator = field(default_factory=KnowledgeBenefitIntegrator)
    efficiency_integrator: EfficiencyBenefitIntegrator = field(default_factory=EfficiencyBenefitIntegrator)
    resource_integrator: ResourceBenefitIntegrator = field(default_factory=ResourceBenefitIntegrator)
    stability_integrator: StabilityBenefitIntegrator = field(default_factory=StabilityBenefitIntegrator)
    social_integrator: SocialBenefitIntegrator = field(default_factory=SocialBenefitIntegrator)
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate all benefit sources into composite estimate."""
        trace: Tuple[str, ...] = ("COMPOSITE_BENEFIT_INTEGRATION_START",)
        
        # Integrate each contributor
        goal_result = self.goal_integrator.integrate(evidence_state, world_model, goal_projection)
        knowledge_result = self.knowledge_integrator.integrate(evidence_state, world_model, goal_projection)
        efficiency_result = self.efficiency_integrator.integrate(evidence_state, world_model, goal_projection)
        resource_result = self.resource_integrator.integrate(evidence_state, world_model, goal_projection)
        stability_result = self.stability_integrator.integrate(evidence_state, world_model, goal_projection)
        social_result = self.social_integrator.integrate(evidence_state, world_model, goal_projection)
        
        trace += (
            "GOAL_BENEFIT_INTEGRATED",
            "KNOWLEDGE_BENEFIT_INTEGRATED",
            "EFFICIENCY_BENEFIT_INTEGRATED",
            "RESOURCE_BENEFIT_INTEGRATED",
            "STABILITY_BENEFIT_INTEGRATED",
            "SOCIAL_BENEFIT_INTEGRATED",
        )
        
        # Aggregate values
        total_value = (
            goal_result.value +
            knowledge_result.value +
            efficiency_result.value +
            resource_result.value +
            stability_result.value +
            social_result.value
        )
        
        # Aggregate confidence and uncertainty (simplified averaging)
        confidence_values = [
            goal_result.confidence,
            knowledge_result.confidence,
            efficiency_result.confidence,
            resource_result.confidence,
            stability_result.confidence,
            social_result.confidence,
        ]
        avg_confidence = sum(confidence_values) / len(confidence_values)
        
        uncertainty_values = [
            goal_result.uncertainty,
            knowledge_result.uncertainty,
            efficiency_result.uncertainty,
            resource_result.uncertainty,
            stability_result.uncertainty,
            social_result.uncertainty,
        ]
        avg_uncertainty = sum(uncertainty_values) / len(uncertainty_values)
        
        trace += ("COMPOSITE_BENEFIT_INTEGRATION_COMPLETE",)
        
        return IntegrationResult(
            value=total_value,
            confidence=avg_confidence,
            uncertainty=avg_uncertainty,
            evidence=(
                goal_result.evidence +
                knowledge_result.evidence +
                efficiency_result.evidence +
                resource_result.evidence +
                stability_result.evidence +
                social_result.evidence
            ),
            trace=trace,
        )