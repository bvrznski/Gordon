# Integration Base Classes for Reward Evaluation & Value Integration Engine (Phase 4.10.3)
# ==================================================================================================

"""
Base classes for benefit and cost integrators.

Each integrator is responsible for computing a semantic contribution to reward
estimation, preserving decomposition and traceability.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# INTEGRATION RESULT
# =============================================================================

@dataclass(frozen=True)
class IntegrationResult:
    """
    Result of an integration operation.
    
    PROPERTIES:
        • value: Computed integration value
        • confidence: Confidence in this integration
        • uncertainty: Uncertainty about this integration
        • evidence: Supporting evidence references
        • trace: Processing trace for provenance
    
    INVARIANTS:
        • Integration results are immutable
        • Trace is always preserved
    """
    
    value: float
    """Computed integration value."""
    
    confidence: float = 1.0
    """Confidence in this integration (0.0 to 1.0)."""
    
    uncertainty: float = 0.0
    """Uncertainty about this integration (0.0 to 1.0)."""
    
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Processing trace for provenance."""
    
    @classmethod
    def zero(cls) -> IntegrationResult:
        """Create a zero-value integration result."""
        return cls(value=0.0)


# =============================================================================
# BASE BENEFIT INTEGRATOR
# =============================================================================

class BaseBenefitIntegrator(ABC):
    """
    Abstract base class for benefit integrators.
    
    Each benefit integrator is responsible for computing one semantic domain
    of benefits (e.g., goal progress, knowledge gain, efficiency).
    
    BENEFIT INTEGRATION LAWS:
        BENEFIT-LAW-001: Benefit integration preserves every contributing benefit
        BENEFIT-LAW-002: Every contributor remains individually represented
        BENEFIT-LAW-003: Integration remains deterministic
        BENEFIT-LAW-004: Evidence is always preserved
    
    INTEGRATION RESPONSIBILITIES:
        • Compute semantic benefit value
        • Track confidence and uncertainty
        • Preserve contributing evidence
        • Generate trace for provenance
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Making executive decisions
        • Learning or policy updates
    """
    
    @abstractmethod
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
        goal_projection: Optional[dict] = None,
    ) -> IntegrationResult:
        """
        Integrate benefit contributions from evidence state.
        
        Args:
            evidence_state: RewardEvidenceState as dictionary
            world_model: World model state (optional)
            goal_projection: Goal projection (optional)
            
        Returns:
            IntegrationResult with computed benefit value and metadata
        """


# =============================================================================
# BASE COST INTEGRATOR
# =============================================================================

class BaseCostIntegrator(ABC):
    """
    Abstract base class for cost integrators.
    
    Each cost integrator is responsible for computing one semantic domain
    of costs (e.g., time, energy, compute, opportunity).
    
    COST INTEGRATION LAWS:
        COST-LAW-001: Time cost remains independent
        COST-LAW-002: Compute cost remains independent
        COST-LAW-003: Energy cost remains independent
        COST-LAW-004: Integration remains deterministic
    
    INTEGRATION RESPONSIBILITIES:
        • Compute semantic cost value
        • Track confidence and uncertainty
        • Preserve contributing evidence
        • Generate trace for provenance
    
    NOT RESPONSIBLE FOR:
        • Modifying system state
        • Making executive decisions
        • Learning or policy updates
    """
    
    @abstractmethod
    def integrate(
        self,
        evidence_state: dict,
        world_model: Optional[dict] = None,
    ) -> IntegrationResult:
        """
        Integrate cost contributions from evidence state.
        
        Args:
            evidence_state: RewardEvidenceState as dictionary
            world_model: World model state (optional)
            
        Returns:
            IntegrationResult with computed cost value and metadata
        """


# =============================================================================
# INTEGRATION POLICY
# =============================================================================

@dataclass(frozen=True)
class IntegrationPolicy:
    """
    Policy for integration operations.
    
    Specifies weighting, normalization, and aggregation strategies for
    benefit and cost integration.
    
    PROPERTIES:
        • benefit_weight: Weight applied to benefits during integration
        • cost_weight: Weight applied to costs during integration
        • normalize: Whether to normalize values before integration
        • preserve_decomposition: Whether to keep individual contributors
    
    INVARIANTS:
        • Policy is immutable
        • Weights must be non-negative
    """
    
    benefit_weight: float = 1.0
    """Weight applied to benefits during integration (>= 0)."""
    
    cost_weight: float = 1.0
    """Weight applied to costs during integration (>= 0)."""
    
    normalize: bool = True
    """Whether to normalize values before integration."""
    
    preserve_decomposition: bool = True
    """Whether to keep individual contributors in result."""
    
    def __post_init__(self):
        if self.benefit_weight < 0:
            raise ValueError("benefit_weight must be non-negative")
        if self.cost_weight < 0:
            raise ValueError("cost_weight must be non-negative")