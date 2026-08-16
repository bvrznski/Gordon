# Processing Adaptation Proposal - Phase 5.2.2
# =============================================

"""
Adaptation Proposal: Request to change processing configuration.

A proposal represents a recommended configuration change based on
environmental assessment, to be approved by configuration management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PROCESSING ADAPTATION PROPOSAL - Configuration change request
# =============================================================================


@dataclass(frozen=True)
class ProcessingAdaptationProposal:
    """
    Requested adaptation of processing configuration.
    
    Fields:
        proposal_identity:   Unique identifier for this proposal
        target_stage:        Which stage's configuration should change?
        current_parameters:  Current parameter values before change
        proposed_parameters: Parameter values after change
        triggering_conditions: What environmental changes triggered this?
        expected_benefit:    Expected improvement from the adaptation
        expected_cost:       Expected cost or downside of the change
        confidence:          Confidence in the benefit being realized
        uncertainty:         Known limitations of this proposal
        policy_requirements: Required policy checks before deployment
    """
    
    proposal_identity: str              # Unique ID
    
    target_stage: str                  # Stage to modify
    
    current_parameters: Dict[str, Any]  # Current values
    proposed_parameters: Dict[str, Any] # Proposed values
    
    triggering_conditions: Tuple[str, ...] = field(default_factory=tuple)  # Conditions that triggered this
    
    expected_benefit: str = ""         # What improvement is expected?
    expected_cost: str = ""            # What cost or downside is expected?
    
    confidence: float = 0.5           # Confidence in benefit (0.0-1.0)
    uncertainty: float = 0.3         # Uncertainty about the change
    
    policy_requirements: Tuple[str, ...] = field(default_factory=tuple)  # Required checks
    
    @property
    def is_significant_change(self) -> bool:
        """Check if this represents a significant configuration change."""
        current_keys = set(self.current_parameters.keys())
        proposed_keys = set(self.proposed_parameters.keys())
        
        # Check for different keys or changed values
        changed_keys = current_keys ^ proposed_keys
        has_key_changes = len(changed_keys) > 0
        
        has_value_changes = any(
            self.current_parameters.get(k) != self.proposed_parameters.get(k)
            for k in current_keys & proposed_keys
        )
        
        return has_key_changes or has_value_changes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary."""
        return {
            "proposal_identity": self.proposal_identity,
            "target_stage": self.target_stage,
            "current_parameters": dict(self.current_parameters),
            "proposed_parameters": dict(self.proposed_parameters),
            "triggering_conditions": list(self.triggering_conditions),
            "expected_benefit": self.expected_benefit,
            "expected_cost": self.expected_cost,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "policy_requirements": list(self.policy_requirements),
        }
    
    @classmethod
    def create(
        cls,
        target_stage: str,
        current_params: Dict[str, Any],
        proposed_params: Dict[str, Any],
        triggering_conditions: Optional[List[str]] = None,
        expected_benefit: str = "Improved processing quality",
        expected_cost: str = "",
        confidence: float = 0.5,
        uncertainty: float = 0.3,
    ) -> "ProcessingAdaptationProposal":
        """Create a new adaptation proposal."""
        return cls(
            proposal_identity=f"adapt_prop:{uuid.uuid4().hex[:16]}",
            target_stage=target_stage,
            current_parameters=current_params,
            proposed_parameters=proposed_params,
            triggering_conditions=tuple(triggering_conditions or []),
            expected_benefit=expected_benefit,
            expected_cost=expected_cost,
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingAdaptationProposal":
        """Create proposal from dictionary."""
        return cls(
            proposal_identity=data.get("proposal_identity", str(uuid.uuid4())),
            target_stage=data.get("target_stage", ""),
            current_parameters=dict(data.get("current_parameters", {})),
            proposed_parameters=dict(data.get("proposed_parameters", {})),
            triggering_conditions=tuple(data.get("triggering_conditions", [])),
            expected_benefit=data.get("expected_benefit", ""),
            expected_cost=data.get("expected_cost", ""),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
        )