# Introspection Shared Contracts - Phase 7.29
# ============================================

"""
Shared contracts for introspection reasoning.

This package contains the canonical contracts governing:
    - Self model construction
    - Cognitive awareness
    - Internal consistency
    - Self diagnostics
    - Validation
    - Governance
"""

from __future__ import annotations

from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.descriptor import IntrospectionDescriptor
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.introspection_set import (
    IntrospectionSet,
    ObservationBoundary,
    PublicationPolicy,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.pipeline import (
    IntrospectionPipeline,
    IntrospectionStage,
)
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.self_model import SelfModel, SelfModelManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.awareness import CognitiveAwareness, AwarenessManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.consistency import InternalConsistency, ConsistencyManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.diagnostics import SelfDiagnostics, DiagnosticManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.evolution import IntrospectionEvolution
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.failure import IntrospectionFailure, FAILURE_KINDS
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.governance import IntrospectionGovernance, GovernanceEvaluation
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.health import IntrospectionHealth
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.publication import SelfStatePublication
from gordon_system.src.agent.components.systems.cognition.reasoning.introspection.shared.validation import IntrospectionValidation

__all__ = [
    "IntrospectionDescriptor",
    "IntrospectionSet",
    "ObservationBoundary",
    "PublicationPolicy",
    "IntrospectionPipeline",
    "IntrospectionStage",
    "SelfModel",
    "SelfModelManagement",
    "CognitiveAwareness",
    "AwarenessManagement",
    "InternalConsistency",
    "ConsistencyManagement",
    "SelfDiagnostics",
    "DiagnosticManagement",
    "IntrospectionEvolution",
    "IntrospectionFailure",
    "FAILURE_KINDS",
    "IntrospectionGovernance",
    "GovernanceEvaluation",
    "IntrospectionHealth",
    "SelfStatePublication",
    "IntrospectionValidation",
]