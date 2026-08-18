# Social Reasoning - Phase 7.32
# =============================

"""
Social Reasoning provides Gordon's Theory-of-Mind engine.

Social reasoning transforms observations of external agents into explicit
models of their internal cognitive state. Unlike introspection, which models
Gordon itself, social reasoning constructs models of OTHER autonomous minds.
"""

from __future__ import annotations

# Import shared contracts (Part 2)
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.descriptor import SocialDescriptor
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.social_set import SocialSet
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.pipeline import SocialPipeline
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.theory_of_mind import TheoryOfMindManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.beliefs import BeliefManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.intentions import IntentionManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.relationships import RelationshipManagement
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.evolution import SocialEvolution
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.validation import SocialValidation, ValidationFinding
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.failure import SocialFailure, AgentModelPartial
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.governance import SocialGovernance, GovernanceFinding
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.health import SocialHealth
from gordon_system.src.agent.components.systems.cognition.reasoning.social.shared.diagnostics import SocialDiagnostics, DiagnosticLogEntry

__all__ = [
    # Shared Contracts
    "SocialDescriptor",
    "SocialSet", 
    "SocialPipeline",
    "TheoryOfMindManagement",
    "BeliefManagement",
    "IntentionManagement",
    "RelationshipManagement",
    "SocialEvolution",
    "SocialValidation",
    "ValidationFinding",
    "SocialFailure",
    "AgentModelPartial",
    "SocialGovernance",
    "GovernanceFinding",
    "SocialHealth",
    "SocialDiagnostics",
    "DiagnosticLogEntry",
]