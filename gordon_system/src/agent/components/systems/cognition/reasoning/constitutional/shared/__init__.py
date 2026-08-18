# Constitutional Reasoning Shared Contracts - Phase 7.36
# ===============================================================

"""
Shared contract types for the constitutional reasoning subsystem.

This module provides canonical implementations of all constitutional reasoning contracts:

    ConstitutionalDescriptor     - Metadata about constitutional sessions
    ConstitutionalSet            - Set of constitutional articles and principles
    ConstitutionalPipeline       - Pipeline state for constitutional reasoning
    ConstitutionalInterpretation - Interpretation of constitutional text
    ConstitutionalLegitimacy     - Legitimacy assessment of constitutional decisions
    ConstitutionalPrecedence     - Precedence hierarchy of constitutional elements
    ConstitutionalEvolution      - History of constitutional evolution
    AmendmentProposal            - Proposal for constitutional amendment
    ConstitutionalFailure        - Failure record for constitutional sessions
    ConstitutionalGovernance     - Governance evaluation of constitutional reasoning
    ConstitutionalHealth         - Health metrics for constitutional reasoning
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.shared import ReasoningKind

__all__ = [
    "ReasoningKind",
]