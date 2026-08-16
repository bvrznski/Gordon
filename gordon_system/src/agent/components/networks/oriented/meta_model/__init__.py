# Oriented Network Meta-Model Package
# ====================================

"""
Package exports for the Canonical Orientation Meta-Model.

This package contains:
    - Core meta-model classes (OrientationMetaModel, OrientationDefinition, etc.)
    - Semantic views (projections only)
    - Architectural views (descriptions only)
    - Context specifications (immutable)
    - Base abstractions
    - Registries (declarative)
    - Cross-model relationships
    - Serialization support
    - Validation framework
"""

from .meta_model import OrientationMetaModel, OrientationDefinition, OrientationSchema
from .definition import OrientationDefinition as Definition
from .schema import OrientationSchema as Schema
from .architecture import OrientationArchitecture
from .identity import OrientationIdentity
from .semantics import OrientationSemantics
from .views import (
    OntologyView,
    ContentView,
    StateView,
    LifecycleView,
    PersistenceView,
    EvaluationView,
    GovernanceView,
    IntegrationView,
)
from .architectural_views import (
    StructuralView,
    BehavioralPreparationView,
    LifecycleArchitecturalView,
    EvaluationArchitecturalView,
    IntegrationArchitecturalView,
)
from .context import (
    ArchitectureContext,
    SemanticContext,
    LifecycleContext,
    GovernanceContext,
    EvaluationContext,
    PersistenceContext,
    IntegrationContext,
    RepositoryContext,
)
from .registries import (
    OntologyRegistry,
    StateRegistry,
    ContentRegistry,
    LifecycleRegistry,
    PersistenceRegistry,
    EvaluationRegistry,
    GovernanceRegistry,
    IntegrationRegistry,
)
from .base import (
    BaseMetaModel,
    BaseMetaView,
    BaseMetaContext,
    BaseMetaRelationship,
    BaseMetaValidation,
    BaseMetaArchitecture,
)
from .relationships import CrossModelRelationship, RelationshipType
from .serialization import serialize, to_json, SerializationMixin
from .validation import (
    MetaModelValidator,
    OwnershipValidator,
    AuthorityValidator,
    HierarchyValidator,
    DependencyValidator,
    SerializationValidator,
)

__all__ = [
    # Meta-Objects
    'OrientationMetaModel',
    'OrientationDefinition',
    'OrientationSchema',
    'OrientationArchitecture',
    'OrientationIdentity',
    'OrientationSemantics',
    # Semantic Views
    'OntologyView',
    'ContentView',
    'StateView',
    'LifecycleView',
    'PersistenceView',
    'EvaluationView',
    'GovernanceView',
    'IntegrationView',
    # Architectural Views
    'StructuralView',
    'BehavioralPreparationView',
    'LifecycleArchitecturalView',
    'EvaluationArchitecturalView',
    'IntegrationArchitecturalView',
    # Meta-Contexts
    'ArchitectureContext',
    'SemanticContext',
    'LifecycleContext',
    'GovernanceContext',
    'EvaluationContext',
    'PersistenceContext',
    'IntegrationContext',
    'RepositoryContext',
    # Registries
    'OntologyRegistry',
    'StateRegistry',
    'ContentRegistry',
    'LifecycleRegistry',
    'PersistenceRegistry',
    'EvaluationRegistry',
    'GovernanceRegistry',
    'IntegrationRegistry',
    # Base Abstractions
    'BaseMetaModel',
    'BaseMetaView',
    'BaseMetaContext',
    'BaseMetaRelationship',
    'BaseMetaValidation',
    'BaseMetaArchitecture',
    # Relationships
    'CrossModelRelationship',
    'RelationshipType',
    # Serialization
    'serialize',
    'to_json',
    'SerializationMixin',
    # Validation
    'MetaModelValidator',
    'OwnershipValidator',
    'AuthorityValidator',
    'HierarchyValidator',
    'DependencyValidator',
    'SerializationValidator',
]