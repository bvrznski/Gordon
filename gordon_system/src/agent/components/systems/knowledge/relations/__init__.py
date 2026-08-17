# Gordon Cognitive Architecture - Phase 6.5 Relations
# ===================================================

"""
Knowledge Relations: Semantic connective structures for Gordon's knowledge system.

Relations define how semantic artifacts (Concepts, Assertions, Beliefs) are connected.
They form the structure of the knowledge graph and enable reasoning over semantic networks.

PHASE 6.5 PARTS:
    Part 1:  Relation Philosophy & Architectural Position
    Part 2:  Canonical Contracts & Algebra
    Part 3:  Normative Specification & Certification

This module implements:
    - Relation descriptors with lifecycle management
    - Property system for relation metrics
    - Algebra operations (composition, inversion, closure)
    - Inverse relations and direction handling
    - Governance for quality assurance
    - Shared contracts and validation rules

RELATION KINDS:
    STRUCTURAL  -> part_of, contains, member_of, component_of
    SEMANTIC    -> is_a, instance_of, specialization_of, generalization_of
    CAUSAL      -> causes, prevents, enables, disables, requires, depends_on
    TEMPORAL    -> before, after, during, overlaps, starts, ends
    SPATIAL     -> inside, outside, left_of, right_of, above, below, near
    FUNCTIONAL  -> uses, implements, produces, consumes, transforms, executes
    SOCIAL      -> owns, reports_to, cooperates_with, trusts, communicates_with
    LOGICAL     -> implies, equivalent, negates, contradicts
    STATISTICAL -> correlates_with, causes_with (with confidence)

ARCHITECTURE:
    Concepts
        ↓
    Assertions  
        ↓
    Relations         ← This module
        ↓
    Beliefs
        ↓
    Knowledge Graph
        ↓
    Models
        ↓
    Reasoning

LICENSE: Gordon Cognitive Architecture Project
"""

from __future__ import annotations

# Shared modules - core contracts
from .shared.descriptor import (
    RelationDescriptor,
    RelationLifecycleState,
    RelationPublicationStatus,
    RelationCompatibilityKind,
    RelationCertificationLevel,
)

from .shared.property import (
    RelationProperty,
    RelationPropertyKind,
    RelationPropertyValueKind,
)

from .shared.algebra import (
    RelationAlgebra,
    RelationAlgebraOperation,
    CompositionRule,
    compose_relations,
    invert_relation,
    compute_closure,
)

from .shared.closure import (
    RelationClosure,
    ClosureKind,
    compute_transitive_closure,
    compute_reflexive_closure,
)

from .shared.inverse import (
    InverseRelation,
    INVERSE_RELATIONS,
)

from .shared.governance import (
    RelationGovernance,
    GovernanceKind,
    detect_duplicates,
    detect_cycles,
)

# Phase 6.5 Part 3 - Certification Status
PHASE_65_VERSION = "1.0.0"
PHASE_65_STATUS = "PARTIAL"
PHASE_65_CERTIFIED_PARTS = [
    "Part 1: Relation Philosophy & Architecture",
    "Part 2: Canonical Contracts (descriptor, property, algebra)",
]

__all__ = [
    # Descriptor
    "RelationDescriptor",
    "RelationLifecycleState",
    "RelationPublicationStatus", 
    "RelationCompatibilityKind",
    "RelationCertificationLevel",
    # Property
    "RelationProperty",
    "RelationPropertyKind",
    "RelationPropertyValueKind",
    # Algebra
    "RelationAlgebra",
    "RelationAlgebraOperation",
    "CompositionRule",
    "compose_relations",
    "invert_relation", 
    "compute_closure",
    # Closure
    "RelationClosure",
    "ClosureKind",
    "compute_transitive_closure",
    "compute_reflexive_closure",
    # Inverse
    "InverseRelation",
    "INVERSE_RELATIONS",
    # Governance
    "RelationGovernance",
    "GovernanceKind",
    "detect_duplicates",
    "detect_cycles",
    # Phase info
    "PHASE_65_VERSION",
    "PHASE_65_STATUS",
    "PHASE_65_CERTIFIED_PARTS",
]


# =============================================================================
# PHASE 6.5 CERTIFICATION CHECKLIST
# =============================================================================

"""
Part 1 - Relation Philosophy ✓
[✓] Relations as semantic connective structures
[✓] Direction, cardinality, constraints support
[✓] Transitivity and symmetry handling
[✓] Inverse relations
[✓] Composition rules

Part 2 - Canonical Contracts (Partial)  
[✓] Descriptor contract (RelationDescriptor)
[✓] Property contract (RelationProperty)
[✓] Algebra contract (RelationAlgebra)
[✓] Closure contract (RelationClosure)
[✓] Inverse relation contract (InverseRelation)
[ ] Governance contract (partial implementation)
[ ] Discovery contract (pending)
[ ] Refinement contract (pending)
[ ] Composition contract (pending)
[ ] Constraint contract (pending)

Part 3 - Normative Laws (In Progress)
[ ] Relation laws
[ ] Structural relation laws  
[ ] Causal relation laws
[ ] Temporal relation laws
[ ] Spatial relation laws
[ ] Functional relation laws
[ ] Direction laws
[ ] Composition laws
[ ] Transitivity laws
[ ] Constraint laws
[ ] Discovery laws
[ ] Governance laws
[ ] Global invariants
[ ] Anti-patterns
[ ] Test requirements

IMPLEMENTATION STATUS:
    Shared contracts:      ✓ Implemented (descriptor, property, algebra, closure)
    Inverse relations:     ✓ Implemented  
    Governance:            ✓ Partially implemented (detection functions)
    Direction module:      ⚠️ Pending
    Composition module:    ⚠️ Pending
    Constraints module:    ⚠️ Pending
    Validation module:     ⚠️ Pending
    Structural relations:  ⚠️ Pending
    Semantic relations:    ⚠️ Pending
    Causal relations:      ⚠️ Pending
    Temporal relations:    ⚠️ Pending
    Spatial relations:     ⚠️ Pending
    Functional relations:  ⚠️ Pending

NEXT STEPS:
1. Complete remaining shared modules (inheritance, discovery, refinement, etc.)
2. Implement specific relation kinds per Part 3 laws
3. Add validation and constraint checking
4. Create test suite for certification

PHASE 6.5 STATUS: IN PROGRESS - Core infrastructure implemented,
                   specific relation kinds and full certification pending.
"""