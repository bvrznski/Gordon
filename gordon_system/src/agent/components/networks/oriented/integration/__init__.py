# Oriented Network Integration Package
# =====================================

"""
OrientedNetwork Integration - Gordon's semantic integration layer for higher cognitive systems.

Canonical Definition:
    The OrientedNetwork Integration package provides canonical integration contracts between
    the Oriented Network and Gordon's higher cognitive subsystems:
    
    - Executive Network (executive control, arbitration, directives)
    - Strategy (strategic reasoning, long-term strategy, adaptation)
    - Planning (plan generation, evaluation, refinement)
    - Reasoning (inference, logical reasoning, causal reasoning)
    - Decision (decision formation, evaluation, commitment)

Architectural Role:
    Semantic coordination layer - Never replaces subsystems
    Consumes capabilities via integration contracts

Public API (Phase 4.7.6):
    Base Integration Abstractions:
        - BaseExecutiveIntegration: Executive integration contract base
        - BaseStrategyIntegration: Strategy integration contract base
        - BasePlanningIntegration: Planning integration contract base
        - BaseReasoningIntegration: Reasoning integration contract base
        - BaseDecisionIntegration: Decision integration contract base
    
    Executive Integration:
        - ExecutiveReference: Reference to executive state or directive
        - ExecutiveDirective: Semantic executive directive
        - ExecutiveContext: Executive context information
        - ExecutiveInfluence: Executive influence on orientation
        - ExecutiveRelationship: Oriented-Executive relationship
        
    Strategy Integration:
        - StrategyReference: Reference to strategic intent
        - StrategyContext: Strategic context information
        - StrategyInfluence: Strategy's influence on orientation
        - StrategyRelationship: Oriented-Strategy relationship
        - StrategyProjection: Semantic strategy projection
        
    Planning Integration:
        - PlanningReference: Reference to planning state
        - PlanningContext: Planning context information
        - PlanningRequest: Request for planning capabilities
        - PlanningProjection: Planning output projection
        - PlanningRelationship: Oriented-Planning relationship
        
    Reasoning Integration:
        - ReasoningReference: Reference to reasoning state
        - ReasoningContext: Reasoning context information
        - ReasoningProjection: Reasoning output projection
        - ReasoningRelationship: Oriented-Reasoning relationship
        - ReasoningInfluence: Reasoning influence on orientation
        
    Decision Integration:
        - DecisionReference: Reference to decision state
        - DecisionProjection: Decision output projection
        - DecisionContext: Decision context information
        - DecisionRelationship: Oriented-Decision relationship
        - DecisionInfluence: Decision influence on orientation

SEMANTIC INTEGRATION LAWS (Phase 4.7.6):
    INTEGRATION-LAW-001: The Oriented Network coordinates cognitive subsystems.
                         It never replaces them.
    INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
    INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
    INTEGRATION-LAW-004: Planning remains the sole owner of planning.
    INTEGRATION-LAW-005: Reasoning remains the sole owner of inference.
    INTEGRATION-LAW-006: Decision Network remains the sole owner of decision formation.
    INTEGRATION-LAW-007: Integration never transfers ownership.
    INTEGRATION-LAW-008: Every subsystem possesses exactly one architectural authority.
    INTEGRATION-LAW-009: Integration shall remain semantic.
    INTEGRATION-LAW-010: Integration shall remain deterministic.

VERSION: 4.7.6
COMPATIBILITY: forward (phased implementation)
"""

from __future__ import annotations

# =============================================================================
# BASE INTEGRATION ABSTRACTIONS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.integration.base import (
    BaseExecutiveIntegration,
    BaseStrategyIntegration,
    BasePlanningIntegration,
    BaseReasoningIntegration,
    BaseDecisionIntegration,
)

# =============================================================================
# EXECUTIVE INTEGRATION CONTRACTS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.integration.executive.types import (
    ExecutiveReference,
    ExecutiveDirective,
    ExecutiveContext,
    ExecutiveInfluence,
    ExecutiveRelationship,
)

from gordon_system.src.agent.components.networks.oriented.integration.executive.authority import (
    ExecutiveAuthority,
)

# =============================================================================
# STRATEGY INTEGRATION CONTRACTS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.integration.strategy.types import (
    StrategyReference,
    StrategyContext,
    StrategyInfluence,
    StrategyRelationship,
    StrategyProjection,
)

# =============================================================================
# PLANNING INTEGRATION CONTRACTS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.integration.planning.types import (
    PlanningReference,
    PlanningContext,
    PlanningRequest,
    PlanningProjection,
    PlanningRelationship,
)

# =============================================================================
# REASONING INTEGRATION CONTRACTS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.integration.reasoning.types import (
    ReasoningReference,
    ReasoningContext,
    ReasoningProjection,
    ReasoningRelationship,
    ReasoningInfluence,
)

# =============================================================================
# DECISION INTEGRATION CONTRACTS
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.integration.decision.types import (
    DecisionReference,
    DecisionProjection,
    DecisionContext,
    DecisionRelationship,
    DecisionInfluence,
)

__all__ = [
    # Base integration abstractions
    "BaseExecutiveIntegration",
    "BaseStrategyIntegration",
    "BasePlanningIntegration",
    "BaseReasoningIntegration",
    "BaseDecisionIntegration",
    
    # Executive integration contracts
    "ExecutiveReference",
    "ExecutiveDirective",
    "ExecutiveContext",
    "ExecutiveInfluence",
    "ExecutiveRelationship",
    "ExecutiveAuthority",
    
    # Strategy integration contracts
    "StrategyReference",
    "StrategyContext",
    "StrategyInfluence",
    "StrategyRelationship",
    "StrategyProjection",
    
    # Planning integration contracts
    "PlanningReference",
    "PlanningContext",
    "PlanningRequest",
    "PlanningProjection",
    "PlanningRelationship",
    
    # Reasoning integration contracts
    "ReasoningReference",
    "ReasoningContext",
    "ReasoningProjection",
    "ReasoningRelationship",
    "ReasoningInfluence",
    
    # Decision integration contracts
    "DecisionReference",
    "DecisionProjection",
    "DecisionContext",
    "DecisionRelationship",
    "DecisionInfluence",
]