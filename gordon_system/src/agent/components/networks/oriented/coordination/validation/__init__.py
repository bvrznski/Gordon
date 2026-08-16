# Oriented Network Coordination Validation Package
# ================================================

"""
Validation Framework for Phase 4.7.5

PUBLIC API:
    - BaseValidator: Abstract base for validation logic
    - HierarchyValidator: Validates intentional hierarchy structure
    - OwnershipValidator: Validates ownership contracts
    - ReferenceValidator: Validates reference relationships
    - ConsistencyValidator: Validates semantic consistency
    - SerializationValidator: Validates serialization format

VALIDATION LAWS (Phase 4.7.5):
    ORIENTED-COORDINATION-LAW-028 through 030, 034 through 039:
        - Every coordination contract shall be serializable
        - Every coordination contract shall be validatable
        - Coordination interfaces shall remain stable
        - Coordination shall preserve subsystem isolation
        - Coordination shall never introduce implicit ownership
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.7.5: Validation Framework - Public API
# =============================================================================

from gordon_system.src.agent.components.networks.oriented.coordination.validation.base import (
    ValidationResult,
    BaseValidator,
    HierarchyValidator,
    OwnershipValidator,
    ReferenceValidator,
    SerializationValidator,
    ConsistencyValidator,
)

__all__ = [
    # Validation result types
    "ValidationResult",
    # Base interface
    "BaseValidator",
    # Specialized validators (Phase 4.7.5)
    "HierarchyValidator",
    "OwnershipValidator",
    "ReferenceValidator", 
    "SerializationValidator",
    "ConsistencyValidator",
]
