# Gordon Executive Decision Architectural Laws - Phase 4.4.10A
# =============================================================

"""
Executive Decision Architectural Laws.

This module defines the immutable architectural laws that govern
all Executive Decisions in Gordon.


EXECUTIVE DECISION ARCHITECTURAL LAWS (E-XXX)
=============================================

Identity Laws
-------------
E-007: Identity survives revisions.
E-008: Revisions never overwrite history.

Authority and Ownership Laws
----------------------------
E-009: Authority shall never imply ownership.
E-010: Ownership shall never imply authority.

Provenance and Traceability Laws
--------------------------------
E-011: Every decision shall possess complete provenance.
E-012: Every decision shall possess immutable lineage.
E-014: No anonymous Executive Decisions shall exist.

Semantic Integrity Laws
-----------------------
E-015: Every Executive Decision shall be completely reconstructable from serialized semantic artifacts.
E-016: Every Executive Decision shall possess exactly one semantic context.
E-017: Every Executive Decision shall declare explicit scope.
E-018: Every Executive Decision shall identify its governed subject.
E-019: Every Executive Decision shall expose explicit purpose.

Composition Laws
----------------
E-020: Every Executive Decision shall define assumptions and constraints independently.
E-023: Dependencies shall form an acyclic semantic graph.

Evidence and Justification Laws
-------------------------------
E-021: Evidence shall be referenced, never embedded as mutable runtime state.
E-022: Justification shall describe semantic rationale, never implementation details.

Runtime and Execution Laws
--------------------------
E-025: Every Executive Decision is immutable.
E-026: Identity survives every revision.
E-027: Revisions preserve semantic continuity.
E-028: Replacement creates a new Decision Identity.
E-029: Recommendations never possess authority.
E-030: Commitments never execute behavior.
E-031: Execution never mutates Decision semantics.
E-032: Evidence is referenced, not embedded as runtime state.

Explicitness Laws
-----------------
E-033: Every dependency shall be explicit.
E-034: Every assumption shall be explicit.
E-035: Every constraint shall be explicit.
E-036: Authority shall always be verifiable.
E-037: Ownership shall always be explicit.

Serialization Laws
------------------
E-038: Every Decision shall possess complete provenance.
E-039: Semantic artifacts shall never contain executable behavior.
E-040: Executive Decision semantics are runtime-independent.

SEMANTIC OBJECT HIERARCHY
=========================

ExecutiveSemanticObject
        │
        ▼
ExecutiveArtifact
        │
        ▼
DecisionArtifact
        │
 ┌──────┼──────────────┐
 ▼      ▼              ▼
Decision Recommendation Commitment
        │
        ▼
DecisionRevision


SEMANTIC FLOW
=============

Observation → Evidence → Reasoning → Recommendation → Executive Decision → Commitment

Note: This flow terminates at ActionSelectionRequest. Execution belongs to another subsystem.
"""

# Architectural Law Categories
class ArchitecturalLawCategory:
    """Categories of architectural laws."""
    
    IDENTITY = "identity"
    AUTHORITY_OWNERSHIP = "authority_ownership"
    PROVENANCE_TRACEABILITY = "provenance_traceability"
    SEMANTIC_INTEGRITY = "semantic_integrity"
    COMPOSITION = "composition"
    EVIDENCE_JUSTIFICATION = "evidence_justification"
    RUNTIME_EXECUTION = "runtime_execution"
    EXPLICITNESS = "explicitness"
    SERIALIZATION = "serialization"


# Law definitions
ARCHITECTURAL_LAWS = {
    "E-007": {
        "id": "E-007",
        "title": "Identity survives revisions.",
        "category": ArchitecturalLawCategory.IDENTITY,
    },
    "E-008": {
        "id": "E-008",
        "title": "Revisions never overwrite history.",
        "category": ArchitecturalLawCategory.IDENTITY,
    },
    "E-009": {
        "id": "E-009",
        "title": "Authority shall never imply ownership.",
        "category": ArchitecturalLawCategory.AUTHORITY_OWNERSHIP,
    },
    "E-010": {
        "id": "E-010",
        "title": "Ownership shall never imply authority.",
        "category": ArchitecturalLawCategory.AUTHORITY_OWNERSHIP,
    },
    "E-011": {
        "id": "E-011",
        "title": "Every decision shall possess complete provenance.",
        "category": ArchitecturalLawCategory.PROVENANCE_TRACEABILITY,
    },
    "E-012": {
        "id": "E-012",
        "title": "Every decision shall possess immutable lineage.",
        "category": ArchitecturalLawCategory.PROVENANCE_TRACEABILITY,
    },
    "E-014": {
        "id": "E-014",
        "title": "No anonymous Executive Decisions shall exist.",
        "category": ArchitecturalLawCategory.PROVENANCE_TRACEABILITY,
    },
    "E-015": {
        "id": "E-015",
        "title": "Every Executive Decision shall be completely reconstructable from serialized semantic artifacts.",
        "category": ArchitecturalLawCategory.SEMANTIC_INTEGRITY,
    },
    "E-016": {
        "id": "E-016",
        "title": "Every Executive Decision shall possess exactly one semantic context.",
        "category": ArchitecturalLawCategory.COMPOSITION,
    },
    "E-017": {
        "id": "E-017",
        "title": "Every Executive Decision shall declare explicit scope.",
        "category": ArchitecturalLawCategory.COMPOSITION,
    },
    "E-018": {
        "id": "E-018",
        "title": "Every Executive Decision shall identify its governed subject.",
        "category": ArchitecturalLawCategory.COMPOSITION,
    },
    "E-019": {
        "id": "E-019",
        "title": "Every Executive Decision shall expose explicit purpose.",
        "category": ArchitecturalLawCategory.COMPOSITION,
    },
    "E-020": {
        "id": "E-020",
        "title": "Every Executive Decision shall define assumptions and constraints independently.",
        "category": ArchitecturalLawCategory.COMPOSITION,
    },
    "E-023": {
        "id": "E-023",
        "title": "Dependencies shall form an acyclic semantic graph.",
        "category": ArchitecturalLawCategory.COMPOSITION,
    },
    "E-021": {
        "id": "E-021",
        "title": "Evidence shall be referenced, never embedded as mutable runtime state.",
        "category": ArchitecturalLawCategory.EVIDENCE_JUSTIFICATION,
    },
    "E-022": {
        "id": "E-022",
        "title": "Justification shall describe semantic rationale, never implementation details.",
        "category": ArchitecturalLawCategory.EVIDENCE_JUSTIFICATION,
    },
    "E-025": {
        "id": "E-025",
        "title": "Every Executive Decision is immutable.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-026": {
        "id": "E-026",
        "title": "Identity survives every revision.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-027": {
        "id": "E-027",
        "title": "Revisions preserve semantic continuity.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-028": {
        "id": "E-028",
        "title": "Replacement creates a new Decision Identity.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-029": {
        "id": "E-029",
        "title": "Recommendations never possess authority.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-030": {
        "id": "E-030",
        "title": "Commitments never execute behavior.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-031": {
        "id": "E-031",
        "title": "Execution never mutates Decision semantics.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
    "E-032": {
        "id": "E-032",
        "title": "Evidence is referenced, never embedded as runtime state.",
        "category": ArchitecturalLawCategory.EVIDENCE_JUSTIFICATION,
    },
    "E-033": {
        "id": "E-033",
        "title": "Every dependency shall be explicit.",
        "category": ArchitecturalLawCategory.EXPLICITNESS,
    },
    "E-034": {
        "id": "E-034",
        "title": "Every assumption shall be explicit.",
        "category": ArchitecturalLawCategory.EXPLICITNESS,
    },
    "E-035": {
        "id": "E-035",
        "title": "Every constraint shall be explicit.",
        "category": ArchitecturalLawCategory.EXPLICITNESS,
    },
    "E-036": {
        "id": "E-036",
        "title": "Authority shall always be verifiable.",
        "category": ArchitecturalLawCategory.EXPLICITNESS,
    },
    "E-037": {
        "id": "E-037",
        "title": "Ownership shall always be explicit.",
        "category": ArchitecturalLawCategory.EXPLICITNESS,
    },
    "E-038": {
        "id": "E-038",
        "title": "Every Decision shall possess complete provenance.",
        "category": ArchitecturalLawCategory.PROVENANCE_TRACEABILITY,
    },
    "E-039": {
        "id": "E-039",
        "title": "Semantic artifacts shall never contain executable behavior.",
        "category": ArchitecturalLawCategory.SERIALIZATION,
    },
    "E-040": {
        "id": "E-040",
        "title": "Executive Decision semantics are runtime-independent.",
        "category": ArchitecturalLawCategory.RUNTIME_EXECUTION,
    },
}