# Knowledge Assertions - Shared Contracts - Phase 6.4
# =====================================================

"""
Knowledge Assertions Shared Contracts for Gordon's Assertion Subsystem.

This module defines the canonical contracts that govern assertion identity,
propositions, predicates, subjects, objects, quantifiers, conditions, evidence,
justification, and their relationships.
"""

from __future__ import annotations

# Re-export all modules from shared package (using relative imports within package)
from .descriptor import (
    AssertionDescriptor,
    AssertionKind,
    AssertionLifecycleState,
)
from .logical_operator import (
    LogicalOperator,
    LogicalOperatorKind,
)
from .compound import (
    CompoundAssertion,
    LogicalStructureKind,
)
from .quantified import (
    QuantifiedAssertion,
    QuantifierKind,
)
from .conditional import (
    ConditionalAssertion,
    ConditionKind,
)
from .aggregation import (
    EvidenceAggregation,
    EvidenceSupportKind,
)
from .dependency import (
    AssertionDependency,
    AssertionDependencyKind,
)
from .contradiction import (
    AssertionContradiction,
    ContradictionKind,
)
from .refinement import (
    AssertionRefinement,
    RefinementKind,
)
from .governance import (
    AssertionGovernance,
    GovernanceFinding,
    GovernanceFindingKind,
)
from .health import (
    AssertionHealthMetrics,
    AssertionHealthSummary,
)
from .validation import (
    AssertionValidator,
    ValidationRule,
)

# Re-export core types
from . import (
    AssertionKind,
    AssertionLifecycleState,
    QuantifierKind,
    ConditionKind,
    EvidenceSupportKind,
    LogicalOperatorKind,
)
