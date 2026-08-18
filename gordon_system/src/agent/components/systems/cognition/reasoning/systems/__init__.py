# Systems Reasoning - Phase 7.38
# =================================

"""
Canonical Systems Reasoning Module.

Systems Reasoning is Gordon's complex systems intelligence engine.
It explains how large collections of interacting components collectively
produce stable or unstable global behavior through:
    - Component organization and topology
    - Interaction networks and dependencies
    - Emergent behaviors and collective dynamics
    - Feedback loops and stability analysis
    - Hierarchical system organization

Unlike Causal Reasoning (which explains individual mechanisms),
Systems Reasoning explains the emergent behavior of interacting systems.
"""

from __future__ import annotations

from .shared.descriptor import SystemDescriptor, SystemReasoningMode, SystemLifecycle
from .shared.system_set import SystemSet, ComponentModel, InteractionAssumption
from .shared.pipeline import SystemPipeline, PipelineStage
from .topology.manager import TopologyManager, TopologyAnalysis
from .interactions.manager import InteractionManager, InteractionNetwork
from .emergence.manager import EmergenceManager, EmergenceAnalysis
from .feedback.manager import FeedbackManager, FeedbackAnalysis
from .stability.manager import StabilityManager, StabilityAssessment
from .validation.manager import SystemsValidation, ValidationReport
from .governance.manager import SystemsGovernance, GovernanceFindings

__all__ = [
    # Core descriptors
    "SystemDescriptor",
    "SystemReasoningMode",
    "SystemLifecycle",
    # System sets and pipelines
    "SystemSet",
    "ComponentModel",
    "InteractionAssumption",
    "SystemPipeline",
    "PipelineStage",
    # Managers
    "TopologyManager",
    "TopologyAnalysis",
    "InteractionManager",
    "InteractionNetwork",
    "EmergenceManager",
    "EmergenceAnalysis",
    "FeedbackManager",
    "FeedbackAnalysis",
    "StabilityManager",
    "StabilityAssessment",
    "SystemsValidation",
    "ValidationReport",
    "SystemsGovernance",
    "GovernanceFindings",
]