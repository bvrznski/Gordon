# Identity Integration Plan Model
# ===============================

"""
Immutable identity integration plan model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True, slots=True)
class IdentityIntegrationPlan:
    """
    Immutable declarative bounded identity integration plan.
    
    PROPERTIES:
        • plan_id: Unique identifier for this plan
        • purpose: Purpose being planned (IdentityIntegrationPurposeKind.*)
        • subject: Subject being planned (IdentitySubjectKind.*)
        • scope_constraints: Scope constraints to apply
        • coordination_steps: Steps in the coordination workflow
        • dependencies: Step dependencies
        • expected_products: Product types expected from this plan
        • recursion_limit: Maximum recursive review depth allowed
    """
    
    plan_id: str = ""
    """Unique identifier for this identity integration plan."""
    
    purpose: str = "general_identity_integration"
    """Purpose being planned (IdentityIntegrationPurposeKind.*)."""
    
    subject: str = "whole_agent"
    """Subject being planned (IdentitySubjectKind.*)."""
    
    scope_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Scope constraints to apply."""
    
    coordination_steps: Tuple[str, ...] = field(default_factory=tuple)
    """Steps in the coordination workflow (CoordinationStepKind.*)."""
    
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Step dependencies."""
    
    expected_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product types expected from this plan (IdentityProductKind.*)."""
    
    recursion_limit: int = 3
    """Maximum recursive review depth allowed."""