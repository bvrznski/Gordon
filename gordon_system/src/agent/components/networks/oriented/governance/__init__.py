# Oriented Network Governance Package - Phase 4.7.11
# ===================================================

"""
Governance Framework for the Oriented Network (Phase 4.7.11)

This package provides the canonical semantic governance framework that defines:

    - admissibility rules
    - governance policies
    - constitutional constraints
    - compliance requirements
    - semantic permissions
    - semantic prohibitions  
    - semantic obligations
    - exception handling

ARCHITECTURAL PHILOSOPHY:

    Governance defines what is semantically valid, permitted, and required.
    Governance never performs runtime enforcement.

    The Oriented Network maintains strict separation between:
        - Governance (declarative rules)
        - Runtime behavior (executed by other subsystems)

PACKAGE STRUCTURE:

    base/           - Base abstractions for all governance models
    constitutions/  - Constitutional models (highest authority)
    policies/       - Policy hierarchy models
    admissibility/  - Orientation admissibility determinations
    compliance/     - Compliance evaluation models
    models/         - Constraint, Permission, Obligation, Exception models
    serialization/  - Deterministic serialization framework
    validation/     - Validation framework

NO RUNTIME CODE:
    - No execution logic
    - No authorization systems
    - No monitoring systems
    - No scheduling
"""

from __future__ import annotations


# =============================================================================
# CANONICAL METADATA
# =============================================================================

__version__: str = "4.7.11"
"""Phase version number"""


# =============================================================================
# PUBLIC API
# =============================================================================

# Base abstractions
from gordon_system.src.agent.components.networks.oriented.governance.base import (
    BasePolicyModel,
    BaseGovernanceModel,
    BaseComplianceModel,
    BaseConstraintModel,
    BasePermissionModel,
    BaseObligationModel,
    BaseExceptionModel,
)

# Constitutional models
from gordon_system.src.agent.components.networks.oriented.governance.constitutions import (
    ArchitectureConstitution,
    SemanticConstitution,
    OrientationConstitution,
    GovernanceConstitution,
    RepositoryConstitution,
    ConstitutionalHierarchy,
)

# Policy models  
from gordon_system.src.agent.components.networks.oriented.governance.policies import (
    OrientationPolicy,
    SemanticPolicy,
    LifecyclePolicy,
    IntegrationPolicy,
    EvaluationPolicy,
    CompliancePolicy,
    GovernancePolicy,
    PolicyHierarchy,
)

# Admissibility models
from gordon_system.src.agent.components.networks.oriented.governance.admissibility import (
    OrientationAdmissibility,
    AdmissibleOrientation,
    ConditionallyAdmissibleOrientation,
    RejectedOrientation,
    ForbiddenOrientation,
    UndefinedOrientation,
    AdmissibilityAssessment,
)

# Compliance models
from gordon_system.src.agent.components.networks.oriented.governance.compliance import (
    OrientationCompliance,
    CompliantOrientation,
    NonCompliantOrientation,
    ConditionallyCompliantOrientation,
    ComplianceViolation,
    ComplianceException,
    ComplianceEvaluation,
)

# Governance models (constraints, permissions, prohibitions, obligations, exceptions)
from gordon_system.src.agent.components.networks.oriented.governance.models import (
    # Constraints
    ArchitecturalConstraint,
    SemanticConstraint,
    LifecycleConstraint,
    EvaluationConstraint,
    IntegrationConstraint,
    GovernanceConstraint,
    
    # Permissions  
    AllowedOperation,
    ConditionallyAllowedOperation,
    ForbiddenOperation,
    RequiredOperation,
    OptionalOperation,
    
    # Prohibitions
    ForbiddenRelationship,
    ForbiddenOwnership,
    ForbiddenDependency,
    ForbiddenTransition,
    ForbiddenIntegration,
    
    # Obligations
    RequiredRelationship,
    RequiredOwnership,
    RequiredValidation,
    RequiredDocumentation,
    RequiredSerialization,
    
    # Exceptions
    PolicyException,
    TemporaryException,
    ArchitecturalException,
    CompatibilityException,
    LegacyException,
    
    # Contexts
    GovernanceContext,
    PolicyContext,
    ComplianceContext,
    ValidationContext,
    LifecycleContext,
    IntegrationContext,
)

# Serialization
from gordon_system.src.agent.components.networks.oriented.governance.serialization import (
    SCHEMA_VERSION,
    serialize_governance_object,
    deserialize_governance_object,
    serialize_to_json,
    deserialize_from_json,
    validate_serialization_schema,
    get_deterministic_hash,
    SerializationContract,
)

# Validation
from gordon_system.src.agent.components.networks.oriented.governance.validation import (
    ValidationError,
    ValidationResult,
    ConstitutionalValidator,
    PolicyValidator,
    ComplianceValidator,
    ConstraintValidator,
    PermissionValidator,
    ObligationValidator,
    ExceptionValidator,
)


__all__ = [
    # Metadata
    "__version__",
    
    # Base abstractions
    "BasePolicyModel",
    "BaseGovernanceModel",
    "BaseComplianceModel",
    "BaseConstraintModel",
    "BasePermissionModel",
    "BaseObligationModel",
    "BaseExceptionModel",
    
    # Constitutional models
    "ArchitectureConstitution",
    "SemanticConstitution",
    "OrientationConstitution",
    "GovernanceConstitution",
    "RepositoryConstitution",
    "ConstitutionalHierarchy",
    
    # Policy models
    "OrientationPolicy",
    "SemanticPolicy",
    "LifecyclePolicy",
    "IntegrationPolicy",
    "EvaluationPolicy",
    "CompliancePolicy",
    "GovernancePolicy",
    "PolicyHierarchy",
    
    # Admissibility models
    "OrientationAdmissibility",
    "AdmissibleOrientation",
    "ConditionallyAdmissibleOrientation",
    "RejectedOrientation",
    "ForbiddenOrientation",
    "UndefinedOrientation",
    "AdmissibilityAssessment",
    
    # Compliance models
    "OrientationCompliance",
    "CompliantOrientation",
    "NonCompliantOrientation",
    "ConditionallyCompliantOrientation",
    "ComplianceViolation",
    "ComplianceException",
    "ComplianceEvaluation",
    
    # Governance models
    "ArchitecturalConstraint",
    "SemanticConstraint",
    "LifecycleConstraint",
    "EvaluationConstraint",
    "IntegrationConstraint",
    "GovernanceConstraint",
    "AllowedOperation",
    "ConditionallyAllowedOperation",
    "ForbiddenOperation",
    "RequiredOperation",
    "OptionalOperation",
    "ForbiddenRelationship",
    "ForbiddenOwnership",
    "ForbiddenDependency",
    "ForbiddenTransition",
    "ForbiddenIntegration",
    "RequiredRelationship",
    "RequiredOwnership",
    "RequiredValidation",
    "RequiredDocumentation",
    "RequiredSerialization",
    "PolicyException",
    "TemporaryException",
    "ArchitecturalException",
    "CompatibilityException",
    "LegacyException",
    "GovernanceContext",
    "PolicyContext",
    "ComplianceContext",
    "ValidationContext",
    "LifecycleContext",
    "IntegrationContext",
    
    # Serialization
    "SCHEMA_VERSION",
    "serialize_governance_object",
    "deserialize_governance_object",
    "serialize_to_json",
    "deserialize_from_json",
    "validate_serialization_schema",
    "get_deterministic_hash",
    "SerializationContract",
    
    # Validation
    "ValidationError",
    "ValidationResult",
    "ConstitutionalValidator",
    "PolicyValidator",
    "ComplianceValidator",
    "ConstraintValidator",
    "PermissionValidator",
    "ObligationValidator",
    "ExceptionValidator",
]