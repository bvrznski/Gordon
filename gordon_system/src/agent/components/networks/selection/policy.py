# Gordon Cognitive Architecture - Phase 4.5.7
# ===========================================
#
"""
Selection policy types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ID TYPES
# =============================================================================

ActionSelectionPolicyKind = str
"""Canonical selection policy category."""

ActionSelectionPolicyReference = str
"""Reference to a specific selection policy."""


# =============================================================================
# ACTION SELECTION POLICY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ActionSelectionPolicy:
    """
    A selection policy that governs how candidates are selected from a frontier.
    
    PROPERTIES:
        • kind: Canonical policy category
        • reference: Policy identity and version
        • authority_scope: Which authorities this policy applies to
        • parameters: Additional policy-specific configuration
    
    POLICY KINDS:
        • SOLE_FRONTIER_MEMBER: Select sole member if exactly one eligible candidate
        • EXPLICIT_AUTHORITY_CHOICE: Apply explicit authority choice
        • EXPLICIT_USER_CHOICE: Apply explicit user choice
        • EXECUTIVE_DIRECTED: Apply executive network directive
        • LEXICOGRAPHIC: Use canonical ordering when all else equal
        • PARETO_WITH_DECLARED_TIE_BREAKER: Pareto with specified tie-breaker
        • SAFETY_FIRST: Prefer safest option (lowest risk, most reversible)
        • REVERSIBILITY_FIRST: Prefer most reversible options
        • INFORMATION_GAIN_FIRST: Prefer highest information gain
        • LOWEST_RISK: Minimize expected negative outcomes
        • LOWEST_COST: Minimize resource cost
        • MINIMUM_SIDE_EFFECT: Minimize side effects
        • MAXIMUM_ADEQUACY: Maximize minimum adequacy across dimensions
        • MAXIMUM_GOAL_ALIGNMENT: Best align with goals/commitments
        • PLAN_DIRECTED: Follow plan where possible
        • CONDITIONAL_SELECTION: Select conditional action when conditions hold
        • FALLBACK_SELECTION: Use fallback when primary unavailable
        • REPLAYED_PRIOR_SELECTION: Replay prior selection from record
        • NO_SELECTION_WHEN_UNRESOLVED: Explicitly produce no-selection for ties
        • UNKNOWN: Unspecified or unknown policy
    
    IMPORTANT:
        • Policy must be explicit, versioned, authority-scoped, and replayable
        • Policy never overrides hard constraints or vetoes
        • Policy never infers missing authorization
        • Policy selection is deterministic when inputs are identical
    """
    
    kind: ActionSelectionPolicyKind = "SOLE_FRONTIER_MEMBER"
    """Canonical policy category."""
    
    reference: str = ""
    """Policy identity and version (e.g., 'policy:v1.0')."""
    
    authority_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Authority IDs to which this policy applies."""
    
    parameters: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    """Additional key-value configuration for policy-specific behavior."""


# =============================================================================
# TIE BREAKER POLICY
# =============================================================================

@dataclass(frozen=True, slots=True)
class TieBreakerPolicy:
    """
    Policy for resolving ties between candidates.
    
    PROPERTIES:
        • method: How to break the tie
        • context: Additional context for the tie-break method
    
    TIE BREAKER METHODS:
        • NONE: Do not automatically resolve (produce no-selection or deferral)
        • CANONICAL_IDENTITY_ORDER: Use semantic identity ordering (only when all equal)
        • USER_PREFERENCE: Rely on user choice
        • EXECUTIVE_DIRECTIVE: Rely on executive directive
        • AUTHORITY_CHOICE: Rely on authority decision
        • LEXICOGRAPHIC: Use lexicographic ordering of candidate IDs
        • HIGHEST_CONFIDENCE: Select with highest confidence level
        • LOWEST_RISK: Prefer lowest risk option
        • MOST_REVERSIBLE: Prefer most reversible option
    """
    
    method: str = "NONE"
    """How to break the tie."""
    
    context: Tuple[str, ...] = field(default_factory=tuple)
    """Additional context for the tie-break method."""


# =============================================================================
# POLICY PRECEDENCE RULES
# =============================================================================

@dataclass(frozen=True, slots=True)
class PolicyPrecedenceRules:
    """
    Rules for when multiple policies or constraints apply.
    
    PRECEDENCE ORDER (higher before lower):
        1. Authoritative prohibitions (policy/security vetoes)
        2. Authority requirements
        3. Mandatory constraints (from decisions/commitments)
        4. Selection policy
        5. Soft preferences (ranking guidance)
        6. Stable canonical ordering (semantic neutrality only)
    """
    
    prohibit_policy_override: bool = True
    """Policy prohibitions cannot be overridden by selection policy."""
    
    prohibit_security_override: bool = True
    """Security prohibitions cannot be overridden by selection policy."""
    
    require_explicit_veto_resolution: bool = True
    """Vetoes must be explicitly resolved before selection proceeds."""
    
    prefer_canonical_ordering_only_for_semantic_neutral_ties: bool = True
    """Canonical ordering only for semantically equivalent candidates."""