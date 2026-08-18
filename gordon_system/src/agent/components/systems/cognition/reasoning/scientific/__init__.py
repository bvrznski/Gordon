# Scientific Reasoning Subsystem - Phase 7.34
# =====================================================

"""
The Scientific Reasoning subsystem is Gordon's knowledge discovery engine.

Scientific Reasoning transforms observations into validated, reproducible,
evidence-based knowledge through explicit hypothesis generation, evidence
integration, experimentation and model revision.

Architecture Position:
    Observations → Scientific Reasoning → Validated Models → Learning → Knowledge

Canonical Components:
    - shared/      : Contract definitions
    - hypotheses/  : Hypothesis management
    - evidence/    : Evidence integration
    - experiments/ : Experimental design
    - models/      : Model revision
    - predictions/ : Prediction generation
    - validation/  : Scientific validation
    - governance/  : Governance evaluation

Scientific Laws:
    SCIENTIFIC-LAW-001: Every session has one immutable semantic identity
    SCIENTIFIC-LAW-002: Scientific reasoning executes over explicit scientific sets
    SCIENTIFIC-LAW-003: Every model references explicit observational evidence
    SCIENTIFIC-LAW-004: Provenance is always preserved
    SCIENTIFIC-LAW-005: Evidential lineage is preserved
    SCIENTIFIC-LAW-006: Reasoning remains independently inspectable
    SCIENTIFIC-LAW-007: Reasoning remains deterministic given identical evidence
    SCIENTIFIC-LAW-008: Completed sessions remain immutable

Hypothesis Laws:
    HYPOTHESIS-LAW-001: Every hypothesis has one explicit identity
    HYPOTHESIS-LAW-002: Supporting evidence remains explicit
    HYPOTHESIS-LAW-003: Contradictory evidence remains explicit
    HYPOTHESIS-LAW-004: Hypothesis provenance remains complete

Evidence Laws:
    EVIDENCE-LAW-001: Every Evidence Model has one explicit identity
    EVIDENCE-LAW-002: Evidence sources remain explicit
    EVIDENCE-LAW-003: Evidence quality remains explicit
    EVIDENCE-LAW-004: Evidence provenance remains complete

Anti-Patterns to Avoid:
    - Accepting hypotheses without evidence
    - Suppressing contradictory observations
    - Discarding failed experiments
    - Overwriting previous scientific models
    - Merging scientific reasoning with learning directly
    - Fabricating confidence estimates
    - Bypassing validation or governance
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.scientific.shared import (
    ScientificDescriptor,
    ScientificMode,
    ScientificState,
)

__all__ = [
    # Shared contracts (exported directly)
    "ScientificDescriptor",
    "ScientificMode",
    "ScientificState",
]