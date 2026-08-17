# Gordon Phase 5.7.7: Situated World - Model Exports
# ====================================================

"""
Model exports for the Situated World capability.
"""

from gordon_system.src.agent.capabilities.consciousness.situated_world.models.entity import (
    Entity,
    EntityAttributes,
)
from gordon_system.src.agent.capabilities.consciousness.situated_world.models.relation import (
    Relation,
    RelationKind,
)
from gordon_system.src.agent.capabilities.consciousness.situated_world.models.affordance import (
    Affordance,
    AffordancePrecondition,
)
from gordon_system.src.agent.capabilities.consciousness.situated_world.models.constraint import (
    Constraint,
    ConstraintCategory,
)

__all__: tuple[str, ...] = (
    # Entity
    "Entity",
    "EntityAttributes",
    # Relation  
    "Relation",
    "RelationKind",
    # Affordance
    "Affordance",
    "AffordancePrecondition",
    # Constraint
    "Constraint",
    "ConstraintCategory",
)