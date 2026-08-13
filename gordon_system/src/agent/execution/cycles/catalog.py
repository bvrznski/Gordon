# Canonical Cycle Catalog
# =======================
#
# PHASE 3.10.6 - Cycle catalog for resolving cycle kinds to definitions.
#
# This module implements a registry-like semantic catalog contract for cycle kind
# resolution. It does NOT use runtime registries but provides semantic mapping.

"""
Canonical Cycle Catalog for Gordon's execution layer.

A CycleCatalog is NOT:
    - A runtime registry with dynamic registration
    - A database of all cycles ever created
    - A factory that instantiates concrete cycle classes

A CycleCatalog IS:
    - A protocol-based contract for kind-to-definition resolution
    - A semantic mapping from CycleKind to CycleDefinition
    - A validation layer for cycle selection decisions

Architecture:
    src/agent/execution/cycles/
        ├── catalog/
        │   ├── __init__.py       # Package exports (this file)
        │   └── registry.py       # Protocol + initial implementation

Usage:
    from gordon_system.src.agent.execution.cycles import (
        CycleCatalog,
        CycleKind,
        get_default_catalog
    )
    
    catalog = get_default_catalog()
    definition = catalog.resolve(CycleKind.INTERPRETATION)
    assert catalog.supports(CycleKind.INTERPRETATION)

Invariants:
    CAT-001: Catalog is immutable (no runtime registration)
    CAT-002: Resolution is deterministic based on kind
    CAT-003: Unsupported kinds raise KeyError or return None
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, Dict, Any
from enum import Enum


class CycleKind(Enum):
    """
    Semantic kinds of cycles.
    
    These classify cycles by their semantic purpose within a Thread's lifecycle.
    """

    # Conversation cycles (Section 8)
    INTERPRETATION = "interpretation"
    CLARIFICATION = "clarification"
    RESPONSE = "response"

    # Planning cycles (Section 8)
    PROBLEM_FRAMING = "problem_framing"
    DECOMPOSITION = "decomposition"
    ALTERNATIVE_GENERATION = "alternative_generation"
    PLAN_EVALUATION = "plan_evaluation"
    PLAN_COMMITMENT = "plan_commitment"

    # Task cycles (Section 8)
    EXECUTION = "execution"
    EVALUATION = "evaluation"
    REVISION = "revision"
    REPORTING = "reporting"

    # Monitoring cycles (Section 8)
    OBSERVATION = "observation"
    BASELINE_ESTABLISHMENT = "baseline_establishment"
    COMPARISON = "comparison"
    ESCALATION = "escalation"

    # Recovery cycles (Section 8)
    FAILURE_ANALYSIS = "failure_analysis"
    RECOVERY_PLANNING = "recovery_planning"
    RECOVERY_EXECUTION = "recovery_execution"
    RECOVERY_EVALUATION = "recovery_evaluation"

    # Internal cycles (Section 8)
    SALIENCE_ASSESSMENT = "salience_assessment"
    REFLECTION_SUBJECT_SELECTION = "reflection_subject_selection"
    CONTEXT_RECONSTRUCTION = "context_reconstruction"
    REFLECTION = "reflection"
    INSIGHT_EVALUATION = "insight_evaluation"
    CONSOLIDATION = "consolidation"
    MAINTENANCE = "maintenance"

    # Delegation (Section 8)
    DELEGATION = "delegation"


@dataclass(frozen=True)
class CycleCatalogEntry:
    """
    A catalog entry mapping a kind to its definition.
    
    This is the semantic contract for how cycles are resolved.
    """

    kind: CycleKind
    name: str
    description: str
    definition_id: str


# =============================================================================
# Protocol Definition
# =============================================================================


class _CycleDefinition:
    """Internal cycle definition class - simple data holder."""
    def __init__(self, definition_id: str, name: str, description: str):
        self.definition_id = definition_id
        self.name = name
        self.description = description


class CycleCatalog(Protocol):
    """
    Protocol for cycle catalog implementations.
    
    A catalog provides resolution of CycleKind to _CycleDefinition through
    semantic mapping, not runtime registration.
    """

    def resolve(self, kind: CycleKind) -> Optional[_CycleDefinition]:
        """Resolve a CycleKind to its definition."""

    def supports(self, kind: CycleKind) -> bool:
        """Check if the catalog supports a given cycle kind."""

    def list_kinds(self) -> tuple[CycleKind, ...]:
        """Get all cycle kinds supported by this catalog."""


# =============================================================================
# Initial Catalog Implementation
# =============================================================================


@dataclass(frozen=True)
class SimpleCycleCatalog:
    """
    Simple immutable cycle catalog with predefined entries.
    
    This implements the CycleCatalog protocol with static mapping.
    No runtime registration is supported - this is by design per Section 10.
    """

    _entries: Dict[CycleKind, _CycleDefinition] = field(default_factory=dict)

    def resolve(self, kind: CycleKind) -> Optional[_CycleDefinition]:
        """
        Resolve a CycleKind to its definition.
        
        Args:
            kind: The semantic cycle kind to resolve
            
        Returns:
            A _CycleDefinition if supported, None otherwise
        """
        return self._entries.get(kind)

    def supports(self, kind: CycleKind) -> bool:
        """
        Check if the catalog supports a given cycle kind.
        
        Args:
            kind: The cycle kind to check
            
        Returns:
            True if this kind can be resolved, False otherwise
        """
        return kind in self._entries

    def list_kinds(self) -> tuple[CycleKind, ...]:
        """
        Get all cycle kinds supported by this catalog.
        
        Returns:
            Tuple of all CycleKind values in the catalog
        """
        return tuple(self._entries.keys())


def create_initial_catalog() -> SimpleCycleCatalog:
    """
    Create the initial catalog with all defined cycle kinds.
    
    This implements the initial catalog entries from Section 10 of the design.
    All cycles are initially created as generic definitions - specific
    implementations will be added later.
    
    Returns:
        A SimpleCycleCatalog pre-populated with all basic cycle definitions
    """
    entries: Dict[CycleKind, _CycleDefinition] = {}

    def make_def(kind: CycleKind, name: str, description: str) -> None:
        entries[kind] = _CycleDefinition(
            definition_id=f"cycle.{kind.value}",
            name=name,
            description=description,
        )

    # Conversation Cycles (Section 8)
    make_def(CycleKind.INTERPRETATION, "InterpretationCycle",
             "Convert new input into validated semantic interpretation")
    make_def(CycleKind.CLARIFICATION, "ClarificationCycle",
             "Produce precise request for missing or ambiguous information")
    make_def(CycleKind.RESPONSE, "ResponseCycle",
             "Produce validated outward response")

    # Planning Cycles (Section 8)
    make_def(CycleKind.PROBLEM_FRAMING, "ProblemFramingCycle",
             "Convert objective into bounded problem representation")
    make_def(CycleKind.DECOMPOSITION, "DecompositionCycle",
             "Decompose framed objective into subobjectives")
    make_def(CycleKind.ALTERNATIVE_GENERATION, "AlternativeGenerationCycle",
             "Generate multiple viable plans or approaches")
    make_def(CycleKind.PLAN_EVALUATION, "PlanEvaluationCycle",
             "Compare candidate plans against objectives and constraints")
    make_def(CycleKind.PLAN_COMMITMENT, "PlanCommitmentCycle",
             "Convert selected plan into accepted Task Thread state")

    # Task Cycles (Section 8)
    make_def(CycleKind.EXECUTION, "ExecutionCycle",
             "Execute one bounded step of an accepted plan")
    make_def(CycleKind.EVALUATION, "EvaluationCycle",
             "Evaluate semantic result against explicit criteria")
    make_def(CycleKind.REVISION, "RevisionCycle",
             "Correct plan, result, response, or artifact after failed evaluation")
    make_def(CycleKind.REPORTING, "ReportingCycle",
             "Produce final or interim semantic report")

    # Monitoring Cycles (Section 8)
    make_def(CycleKind.OBSERVATION, "ObservationCycle",
             "Acquire one bounded observation of a monitoring target")
    make_def(CycleKind.BASELINE_ESTABLISHMENT, "BaselineEstablishmentCycle",
             "Convert an observation into accepted monitoring baseline")
    make_def(CycleKind.COMPARISON, "ComparisonCycle",
             "Compare new observation against accepted baseline")
    make_def(CycleKind.ESCALATION, "EscalationCycle",
             "Convert meaningful condition into bounded escalation action")

    # Recovery Cycles (Section 8)
    make_def(CycleKind.FAILURE_ANALYSIS, "FailureAnalysisCycle",
             "Classify failed outcome and identify its semantic cause")
    make_def(CycleKind.RECOVERY_PLANNING, "RecoveryPlanningCycle",
             "Select bounded semantic recovery strategy")
    make_def(CycleKind.RECOVERY_EXECUTION, "RecoveryExecutionCycle",
             "Execute one bounded recovery strategy")
    make_def(CycleKind.RECOVERY_EVALUATION, "RecoveryEvaluationCycle",
             "Determine whether semantic recovery succeeded")

    # Internal Cycles (Section 8)
    make_def(CycleKind.SALIENCE_ASSESSMENT, "SalienceAssessmentCycle",
             "Determine which available semantic activity deserves attention")
    make_def(CycleKind.REFLECTION_SUBJECT_SELECTION, "ReflectionSubjectSelectionCycle",
             "Select one bounded subject for reflection")
    make_def(CycleKind.CONTEXT_RECONSTRUCTION, "ContextReconstructionCycle",
             "Reconstruct sufficient semantic context for reflection")
    make_def(CycleKind.REFLECTION, "ReflectionCycle",
             "Derive one bounded insight, correction, or explicit no-result outcome")
    make_def(CycleKind.INSIGHT_EVALUATION, "InsightEvaluationCycle",
             "Determine whether reflective result should alter accepted state")
    make_def(CycleKind.CONSOLIDATION, "ConsolidationCycle",
             "Consolidate redundant or fragmented semantic state")
    make_def(CycleKind.MAINTENANCE, "MaintenanceCycle",
             "Perform one bounded internal maintenance action")

    # Delegation
    make_def(CycleKind.DELEGATION, "DelegationCycle",
             "Create well-defined child Thread delegation")

    catalog = SimpleCycleCatalog()
    object.__setattr__(catalog, '_entries', entries)
    return catalog


# =============================================================================
# Convenience Accessors
# =============================================================================


_DEFAULT_CATALOG: Optional[SimpleCycleCatalog] = None


def get_default_catalog() -> CycleCatalog:
    """
    Get the default cycle catalog instance.
    
    This provides access to the initial catalog without requiring explicit
    instantiation. The returned catalog is immutable and thread-safe.
    
    Returns:
        The default CycleCatalog implementation
    """
    global _DEFAULT_CATALOG
    
    if _DEFAULT_CATALOG is None:
        _DEFAULT_CATALOG = create_initial_catalog()
    
    return _DEFAULT_CATALOG


# =============================================================================
# Export all public symbols
# =============================================================================


__all__ = [
    # Protocol
    "CycleCatalog",
    
    # Implementation
    "SimpleCycleCatalog",
    "create_initial_catalog",
    "get_default_catalog",
    
    # Types
    "CycleKind",
    "CycleCatalogEntry",
]