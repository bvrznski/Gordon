# Oriented Network Executive Integration Package
# ===============================================

"""
Executive Integration Contracts for Phase 4.7.6.

OWNERSHIP (Executive Network):
    - executive control
    - arbitration
    - executive supervision
    - executive directives
    
ORIENTED NETWORK ROLE:
    - consumes executive guidance
    - never performs executive control
    - maintains semantic reference to executive state

SEMANTIC INTEGRATION LAWS (Phase 4.7.6):
    INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
    INTEGRATION-LAW-007: Integration never transfers ownership.
"""

from __future__ import annotations

# =============================================================================
# EXECUTIVE INTEGRATION TYPES
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

__all__ = [
    "ExecutiveReference",
    "ExecutiveDirective",
    "ExecutiveContext",
    "ExecutiveInfluence",
    "ExecutiveRelationship",
    "ExecutiveAuthority",
]