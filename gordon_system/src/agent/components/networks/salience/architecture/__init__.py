# Salience Network Architecture Module

"""
Architecture layer for the Salience Network.

This module provides the canonical architectural definitions that govern
the Salience Network's role in the Gordon cognitive architecture.
"""

from __future__ import annotations

# Base Architectural Abstractions (Phase 4.8.1)
from ._base import (
    BaseSalienceArchitecture,
    BaseSalienceDefinition,
    BaseSalienceIdentity,
    BaseSalienceOwnership,
    BaseSalienceRelationship,
    BaseSalienceContext,
)

# Architectural Identity
from ._identity import (
    SalienceArchitecture,
    SalienceIdentity,
    SalienceDefinition,
    SalienceOwnership,
    SalienceResponsibility,
    SalienceScope,
)

# Ownership Model (Phase 4.8.1)
from ._ownership import (
    SalienceArchitectureReference,
    SalienceArchitectureRelationship,
    SalienceArchitectureRequirement,
    SalienceArchitectureAuthority,
    SalienceArchitectureOwner,
    SalienceArchitectureProjection,
)

# Responsibility Model (Phase 4.8.1)
from ._responsibility import (
    SalienceResponsibilityReference,
    SalienceResponsibilityRelationship,
    SalienceResponsibilityRequirement,
    SalienceResponsibilityAuthority,
    SalienceResponsibilityOwner,
    SalienceResponsibilityProjection,
)

# Context Model (Phase 4.8.1)
from ._context import (
    SalienceContextReference,
    SalienceContextRelationship,
    SalienceContextRequirement,
    SalienceContextAuthority,
    SalienceContextOwner,
    SalienceContextProjection,
)

__all__ = [
    # Base Archetypes
    "BaseSalienceArchitecture",
    "BaseSalienceDefinition",
    "BaseSalienceIdentity",
    "BaseSalienceOwnership",
    "BaseSalienceRelationship",
    "BaseSalienceContext",
    
    # Architectural Identity
    "SalienceArchitecture",
    "SalienceIdentity",
    "SalienceDefinition",
    "SalienceOwnership",
    "SalienceResponsibility",
    "SalienceScope",
    
    # Ownership Model
    "SalienceArchitectureReference",
    "SalienceArchitectureRelationship",
    "SalienceArchitectureRequirement",
    "SalienceArchitectureAuthority",
    "SalienceArchitectureOwner",
    "SalienceArchitectureProjection",
    
    # Responsibility Model
    "SalienceResponsibilityReference",
    "SalienceResponsibilityRelationship",
    "SalienceResponsibilityRequirement",
    "SalienceResponsibilityAuthority",
    "SalienceResponsibilityOwner",
    "SalienceResponsibilityProjection",
    
    # Context Model
    "SalienceContextReference",
    "SalienceContextRelationship",
    "SalienceContextRequirement",
    "SalienceContextAuthority",
    "SalienceContextOwner",
    "SalienceContextProjection",
]
