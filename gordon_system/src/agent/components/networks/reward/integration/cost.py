# Cost Integrators for Reward Evaluation & Value Integration Engine (Phase 4.10.3)
# ==================================================================================================

"""
Cost integrators compute semantic contributions to reward estimation.

Each cost integrator handles one domain of cost contribution, preserving
decomposition and traceability as required by Phase 4.10.3.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

from .base import BaseCostIntegrator, IntegrationResult


# =============================================================================
# TIME COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class TimeCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from time expenditure.
    
    Computes how much time spent contributes to overall reward cost.
    
    COST-LAW-001: Time cost remains independent
    """
    
    weight: float = 1.0
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate time-based cost contributions."""
        trace: Tuple[str, ...] = ("TIME_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_time_evidence = "time" in kind.lower() or "duration" in kind.lower()
                
                # Costs are from negative relationships (contradicting reward)
                if is_time_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("TIME_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from time evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# ENERGY COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class EnergyCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from energy expenditure.
    
    Computes how much energy used contributes to overall reward cost.
    
    COST-LAW-002: Energy cost remains independent
    """
    
    weight: float = 0.9
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate energy-based cost contributions."""
        trace: Tuple[str, ...] = ("ENERGY_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_energy_evidence = "energy" in kind.lower() or "power" in kind.lower()
                
                if is_energy_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("ENERGY_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from energy evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# COMPUTE COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class ComputeCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from compute resource expenditure.
    
    Computes how much computational resources used contributes to overall reward cost.
    
    COST-LAW-003: Compute cost remains independent
    """
    
    weight: float = 0.8
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate compute-based cost contributions."""
        trace: Tuple[str, ...] = ("COMPUTE_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_compute_evidence = "compute" in kind.lower() or "cpu" in kind.lower()
                
                if is_compute_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("COMPUTE_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from compute evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# MEMORY COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class MemoryCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from memory usage.
    
    Computes how much memory used contributes to overall reward cost.
    
    COST-LAW-004: Memory cost remains independent
    """
    
    weight: float = 0.7
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate memory-based cost contributions."""
        trace: Tuple[str, ...] = ("MEMORY_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_memory_evidence = "memory" in kind.lower() or "storage" in kind.lower()
                
                if is_memory_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("MEMORY_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from memory evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# ATTENTION COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class AttentionCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from attention allocation.
    
    Computes how much attention allocated contributes to overall reward cost.
    
    COST-LAW-005: Attention cost remains independent
    """
    
    weight: float = 1.0
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate attention-based cost contributions."""
        trace: Tuple[str, ...] = ("ATTENTION_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_attention_evidence = "attention" in kind.lower() or "focus" in kind.lower()
                
                if is_attention_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("ATTENTION_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from attention evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# OPPORTUNITY COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class OpportunityCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from missed opportunities.
    
    Computes how much opportunity loss contributes to overall reward cost.
    
    COST-LAW-006: Opportunity cost remains independent
    """
    
    weight: float = 1.2
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate opportunity-based cost contributions."""
        trace: Tuple[str, ...] = ("OPPORTUNITY_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_opportunity_evidence = "opportunity" in kind.lower() or "missed" in kind.lower()
                
                if is_opportunity_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("OPPORTUNITY_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from opportunity evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# RISK COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class RiskCostIntegrator(BaseCostIntegrator):
    """
    Integrates cost from risk increase.
    
    Computes how much risk incurred contributes to overall reward cost.
    
    COST-LAW-007: Risk cost remains independent
    """
    
    weight: float = 1.5
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate risk-based cost contributions."""
        trace: Tuple[str, ...] = ("RISK_COST_INTEGRATION_START",)
        
        evidences = evidence_state.get("evidences", ())
        
        total_cost = 0.0
        confidence_sum = 0.0
        count = 0
        
        for evidence in evidences:
            if isinstance(evidence, dict):
                kind = evidence.get("evidence_kind", "")
                
                is_risk_evidence = "risk" in kind.lower() or "danger" in kind.lower()
                
                if is_risk_evidence and evidence.get("relationship") == "supports_punishment":
                    cost_value = self._compute_cost(evidence)
                    total_cost += cost_value * self.weight
                    
                    confidence_sum += evidence.get("confidence", 0.5)
                    count += 1
        
        trace += ("RISK_COST_INTEGRATED",)
        
        avg_confidence = confidence_sum / count if count > 0 else 0.5
        uncertainty = max(0.0, 1.0 - avg_confidence)
        
        return IntegrationResult(
            value=total_cost,
            confidence=avg_confidence,
            uncertainty=uncertainty,
            evidence=tuple(str(e.get("evidence_id", "")) for e in evidences if isinstance(e, dict)),
            trace=trace,
        )
    
    def _compute_cost(self, evidence: dict) -> float:
        """Compute cost value from risk evidence."""
        relationship = evidence.get("relationship", "unknown")
        
        if relationship == "supports_punishment":
            return 1.0
        elif relationship == "contradicts_punishment":
            return -0.5
        else:
            return 0.0


# =============================================================================
# COMPOSITE COST INTEGRATOR
# =============================================================================

@dataclass(frozen=True)
class CompositeCostIntegrator(BaseCostIntegrator):
    """
    Integrates all cost sources into a composite estimate.
    
    Preserves decomposition of individual costs while providing aggregate value.
    
    PROPERTIES:
        • time_integrator: Time cost integrator
        • energy_integrator: Energy cost integrator
        • compute_integrator: Compute cost integrator
        • memory_integrator: Memory cost integrator
        • attention_integrator: Attention cost integrator
        • opportunity_integrator: Opportunity cost integrator
        • risk_integrator: Risk cost integrator
    
    NOT RESPONSIBLE FOR:
        • Modifying individual integrators
        • Changing integration weights after construction
    """
    
    time_integrator: TimeCostIntegrator = field(default_factory=TimeCostIntegrator)
    energy_integrator: EnergyCostIntegrator = field(default_factory=EnergyCostIntegrator)
    compute_integrator: ComputeCostIntegrator = field(default_factory=ComputeCostIntegrator)
    memory_integrator: MemoryCostIntegrator = field(default_factory=MemoryCostIntegrator)
    attention_integrator: AttentionCostIntegrator = field(default_factory=AttentionCostIntegrator)
    opportunity_integrator: OpportunityCostIntegrator = field(default_factory=OpportunityCostIntegrator)
    risk_integrator: RiskCostIntegrator = field(default_factory=RiskCostIntegrator)
    
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """Integrate all cost sources into composite estimate."""
        trace: Tuple[str, ...] = ("COMPOSITE_COST_INTEGRATION_START",)
        
        # Integrate each contributor
        time_result = self.time_integrator.integrate(evidence_state, world_model)
        energy_result = self.energy_integrator.integrate(evidence_state, world_model)
        compute_result = self.compute_integrator.integrate(evidence_state, world_model)
        memory_result = self.memory_integrator.integrate(evidence_state, world_model)
        attention_result = self.attention_integrator.integrate(evidence_state, world_model)
        opportunity_result = self.opportunity_integrator.integrate(evidence_state, world_model)
        risk_result = self.risk_integrator.integrate(evidence_state, world_model)
        
        trace += (
            "TIME_COST_INTEGRATED",
            "ENERGY_COST_INTEGRATED",
            "COMPUTE_COST_INTEGRATED",
            "MEMORY_COST_INTEGRATED",
            "ATTENTION_COST_INTEGRATED",
            "OPPORTUNITY_COST_INTEGRATED",
            "RISK_COST_INTEGRATED",
        )
        
        # Aggregate values
        total_value = (
            time_result.value +
            energy_result.value +
            compute_result.value +
            memory_result.value +
            attention_result.value +
            opportunity_result.value +
            risk_result.value
        )
        
        # Aggregate confidence and uncertainty (simplified averaging)
        confidence_values = [
            time_result.confidence,
            energy_result.confidence,
            compute_result.confidence,
            memory_result.confidence,
            attention_result.confidence,
            opportunity_result.confidence,
            risk_result.confidence,
        ]
        avg_confidence = sum(confidence_values) / len(confidence_values)
        
        uncertainty_values = [
            time_result.uncertainty,
            energy_result.uncertainty,
            compute_result.uncertainty,
            memory_result.uncertainty,
            attention_result.uncertainty,
            opportunity_result.uncertainty,
            risk_result.uncertainty,
        ]
        avg_uncertainty = sum(uncertainty_values) / len(uncertainty_values)
        
        trace += ("COMPOSITE_COST_INTEGRATION_COMPLETE",)
        
        return IntegrationResult(
            value=total_value,
            confidence=avg_confidence,
            uncertainty=avg_uncertainty,
            evidence=(
                time_result.evidence +
                energy_result.evidence +
                compute_result.evidence +
                memory_result.evidence +
                attention_result.evidence +
                opportunity_result.evidence +
                risk_result.evidence
            ),
            trace=trace,
        )