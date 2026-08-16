# Processing Configuration - Phase 5.2.2
# ======================================

"""
Configuration: Processing parameter definitions and proposals.

Configuration defines the parameters that control processing behavior,
and proposals suggest changes based on adaptation assessments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PROCESSING CONFIGURATION - Processing parameter set
# =============================================================================


@dataclass(frozen=True)
class ProcessingConfiguration:
    """
    Configuration for processing stages.
    
    Fields:
        config_id:           Unique configuration identifier
        revision:            Configuration version number
        parameters:          Stage-specific parameters
        thresholds:          Threshold values for various metrics
        capabilities:        Enabled/disabled capabilities
        resource_limits:     Resource usage constraints
        created_at_utc:      When this configuration was created
    """
    
    config_id: str                      # Unique ID
    
    revision: int = 1                  # Version number
    
    parameters: Dict[str, Any] = field(default_factory=dict)  # stage_id -> params
    thresholds: Dict[str, float] = field(default_factory=dict)  # metric -> threshold
    
    capabilities: Tuple[str, ...] = field(default_factory=tuple)
    
    resource_limits: Dict[str, Any] = field(default_factory=dict)  # limits
    
    created_at_utc: float = field(default_factory=time.time)
    
    def get_stage_params(self, stage_id: str) -> Dict[str, Any]:
        """Get parameters for a specific stage."""
        return dict(self.parameters.get(stage_id, {}))
    
    def with_stage_params(
        self,
        stage_id: str,
        params: Dict[str, Any],
    ) -> "ProcessingConfiguration":
        """Create new config with updated stage parameters."""
        new_params = dict(self.parameters)
        new_params[stage_id] = params
        return dataclass_replace_config(
            self,
            parameters=new_params,
            revision=self.revision + 1,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "config_id": self.config_id,
            "revision": self.revision,
            "parameters": dict(self.parameters),
            "thresholds": dict(self.thresholds),
            "capabilities": list(self.capabilities),
            "resource_limits": dict(self.resource_limits),
            "created_at_utc": self.created_at_utc,
        }
    
    @classmethod
    def create(
        cls,
        config_id: Optional[str] = None,
        revision: int = 1,
        parameters: Optional[Dict[str, Any]] = None,
        thresholds: Optional[Dict[str, float]] = None,
        capabilities: Optional[List[str]] = None,
        resource_limits: Optional[Dict[str, Any]] = None,
    ) -> "ProcessingConfiguration":
        """Create a new configuration."""
        return cls(
            config_id=config_id or f"config:{uuid.uuid4().hex[:16]}",
            revision=revision,
            parameters=parameters or {},
            thresholds=thresholds or {},
            capabilities=tuple(capabilities or []),
            resource_limits=resource_limits or {},
            created_at_utc=time.time(),
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingConfiguration":
        """Create configuration from dictionary."""
        return cls(
            config_id=data.get("config_id", str(uuid.uuid4())),
            revision=data.get("revision", 1),
            parameters=dict(data.get("parameters", {})),
            thresholds=dict(data.get("thresholds", {})),
            capabilities=tuple(data.get("capabilities", [])),
            resource_limits=dict(data.get("resource_limits", {})),
            created_at_utc=float(data.get("created_at_utc", time.time())),
        )


# =============================================================================
# CONFIGURATION PROPOSAL - Proposed configuration change
# =============================================================================


@dataclass(frozen=True)
class ConfigurationProposal:
    """
    Proposed configuration change.
    
    Fields:
        proposal_id:         Unique proposal identifier
        target_stage:        Which stage's configuration changes?
        current_params:      Current parameter values
        proposed_params:     Proposed parameter values
        triggering_condition: What triggered this proposal?
        expected_benefit:    Expected improvement from the change
        confidence:          Confidence in the proposal's benefit
        uncertainty:         Known limitations of the proposal
        policy_requirements: Required policy checks before deployment
    """
    
    proposal_id: str                    # Unique ID
    
    target_stage: str                  # Stage to modify
    
    current_params: Dict[str, Any]     # Current values
    proposed_params: Dict[str, Any]    # Proposed values
    
    triggering_condition: Optional[str] = None  # What triggered this?
    
    expected_benefit: str = ""         # What improvement is expected?
    
    confidence: float = 0.5           # Confidence in benefit (0.0-1.0)
    uncertainty: float = 0.3         # Uncertainty about the change
    
    policy_requirements: Tuple[str, ...] = field(default_factory=tuple)  # Required checks
    
    @property
    def is_significant(self) -> bool:
        """Check if this proposal represents significant change."""
        changed_keys = set(self.current_params.keys()) ^ set(self.proposed_params.keys())
        return len(changed_keys) > 0 or any(
            self.current_params.get(k) != self.proposed_params.get(k)
            for k in self.current_params
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary."""
        return {
            "proposal_id": self.proposal_id,
            "target_stage": self.target_stage,
            "current_params": dict(self.current_params),
            "proposed_params": dict(self.proposed_params),
            "triggering_condition": self.triggering_condition,
            "expected_benefit": self.expected_benefit,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "policy_requirements": list(self.policy_requirements),
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_config(instance: ProcessingConfiguration, **kwargs) -> ProcessingConfiguration:
    """Replace fields in a frozen config dataclass."""
    return ProcessingConfiguration(
        config_id=instance.config_id,
        revision=kwargs.get("revision", instance.revision),
        parameters=kwargs.get("parameters", instance.parameters),
        thresholds=kwargs.get("thresholds", instance.thresholds),
        capabilities=kwargs.get("capabilities", instance.capabilities),
        resource_limits=kwargs.get("resource_limits", instance.resource_limits),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
    )