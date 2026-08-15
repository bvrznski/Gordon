# Gordon Executive Decision Package - Phase 4.4.10A
# ================================================

"""
Executive Decisions - Immutable, runtime-neutral semantic commitments.

This package provides:
- Canonical immutable decision definitions
- Authority and ownership tracking
- Revision management
- Runtime-neutral execution semantics

ARCHITECTURAL PHASE: 4.4.10A
STATUS: PARTIAL - Contract system complete, laws defined

EXECUTIVE DECISION SEMANTIC OBJECTS
===================================

Core Contracts (from contracts/):
    ExecutiveDecision      - Main decision type
    DecisionIdentity       - Immutable identity for decisions
    DecisionRevision       - Revision tracking
    DecisionCommitment     - Commitment records
    DecisionRecommendation - Recommendation records

Authority & Ownership:
    DecisionAuthority      - Authority definitions
    DecisionOwnership      - Ownership tracking

Provenance & Context:
    DecisionProvenance     - Lineage tracking
    DecisionContext        - Operational context
    DecisionMetadata       - Metadata record

Composition:
    DecisionComposition    - Semantic composition
    DecisionAssumptions    - Explicit assumptions
    DecisionConstraints    - Semantic boundaries

Evidence & Reasoning:
    DecisionEvidence       - Evidence references
    DecisionJustification  - Why commitment was accepted

References:
    DecisionReference      - Reference types
    ReferenceKind          - Kind of reference

ARCHITECTURAL LAWS
==================

E-007 through E-040 are defined in laws.py.

Key principles:
    - Identity survives revisions (E-007, E-026)
    - Revisions never overwrite history (E-008)
    - Authority ≠ Ownership (E-009, E-010)
    - Decisions are immutable (E-025)
    - No runtime state in decisions (E-039, E-040)

SEMANTIC FLOW
=============

Observation → Evidence → Reasoning → Recommendation → Executive Decision → Commitment

Note: This flow terminates at ActionSelectionRequest. Execution belongs to another subsystem.
"""

from gordon_system.src.agent.networks.executive.decisions.laws import (
    ARCHITECTURAL_LAWS,
    ArchitecturalLawCategory,
)

__all__ = [
    # Laws
    "ARCHITECTURAL_LAWS",
    "ArchitecturalLawCategory",
]