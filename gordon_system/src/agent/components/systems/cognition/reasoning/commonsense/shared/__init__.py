# Commonsense Reasoning Shared Contracts - Phase 7.45
# ====================================================

"""
Shared contracts for Commonsense Reasoning.

This module provides the foundational data structures and contracts
for Gordon's implicit understanding architecture.
"""

from __future__ import annotations

# Commonsense Descriptor and Set are defined in their respective modules
# CommonsenseDescriptor and CommonsenseSet are imported from shared modules below

from gordon_system.src.agent.components.systems.cognition.reasoning.commonsense.shared.assumptions import (
    AssumptionIdentity,
    SupportingObservation,
    AssumptionModel,
    ApplicabilityConditions,
    AssumptionManagement,
    AssumptionTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.commonsense.shared.physical import (
    PhysicalIntuitionIdentity,
    PhysicalConstraint,
    PhysicalIntuitionModel,
    PhysicalCommonsense,
    PhysicalIntuitionType,
    PhysicalTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.commonsense.shared.social import (
    SocialIntuitionIdentity,
    SocialExpectation,
    SocialIntuitionModel,
    SocialCommonsense,
    SocialIntuitionType,
    SocialTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.commonsense.shared.affordances import (
    AffordanceIdentity,
    PossibleAction,
    AffordanceModel,
    AffordanceManagement,
    AffordanceType,
    AffordanceTrace,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.commonsense.shared.plausibility import (
    PlausibilityIdentity,
    PlausibilityScore,
    PlausibilityModel,
    PlausibilityManagement,
    PlausibilityType,
    PlausibilityTrace,
)


__all__ = [
    # Assumption Contracts
    "AssumptionIdentity",
    "SupportingObservation",
    "AssumptionModel",
    "ApplicabilityConditions",
    "AssumptionManagement",
    "AssumptionTrace",
    
    # Physical Intuition Contracts
    "PhysicalIntuitionIdentity",
    "PhysicalConstraint",
    "PhysicalIntuitionModel",
    "PhysicalCommonsense",
    "PhysicalIntuitionType",
    "PhysicalTrace",
    
    # Social Intuition Contracts
    "SocialIntuitionIdentity",
    "SocialExpectation",
    "SocialIntuitionModel",
    "SocialCommonsense",
    "SocialIntuitionType",
    "SocialTrace",
    
    # Affordance Contracts
    "AffordanceIdentity",
    "PossibleAction",
    "AffordanceModel",
    "AffordanceManagement",
    "AffordanceType",
    "AffordanceTrace",
    
    # Plausibility Contracts
    "PlausibilityIdentity",
    "PlausibilityScore",
    "PlausibilityModel",
    "PlausibilityManagement",
    "PlausibilityType",
    "PlausibilityTrace",
]