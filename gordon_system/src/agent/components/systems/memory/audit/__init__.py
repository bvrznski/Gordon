# Memory Audit System - Phase 5.1.9
# ====================================

"""
Memory Audit: Independent assurance layer for memory integrity.

This module provides the canonical Memory Audit subsystem that validates,
certifies, and reports on the health of Gordon's memory systems without ever
owning or modifying memories.

Audit Principles:

    AUDIT-PRINCIPLE-001: Audit is read-only - never modifies memories
    AUDIT-PRINCIPLE-002: Audit preserves ownership boundaries
    AUDIT-PRINCIPLE-003: Audit preserves provenance and lineage
    AUDIT-PRINCIPLE-004: Audit remains deterministic and replayable
    AUDIT-PRINCIPLE-005: Audit exposes all findings explicitly

Audit Responsibilities:

    - Structural validation (schema, identifiers, contracts)
    - Reference integrity (broken references, orphan nodes, dangling refs)
    - Lineage verification (origin, source, revision history)
    - Provenance verification (completeness, continuity, ownership)
    - Integrity validation (corruption, truncation, checksums)
    - Duplication analysis (exact, semantic, embedding duplicates)
    - Consistency validation (cross-references, contradictions)
    - Retrieval validation (can memories be retrieved?)
    - Health assessment and certification

Audit Does NOT Do:

    - Never repairs memory
    - Never deletes memory
    - Never consolidates memory
    - Never forgets memory
    - Never fabricates missing lineage
    - Never hides corruption or contradictions

Audit Flow:

    Audit Request → Planner → Adapter Selection → Memory Snapshot
        ↓
    Validation → Analysis → Lineage Verification → Provenance Verification
        ↓
    Consistency Verification → Integrity Verification
        ↓
    Health Aggregation → Report → Certification

The subsystem operates independently of memory implementations and never
owns memories. It only observes, validates, and reports.

Exports:
    - AuditTypes: Canonical audit type identifiers
    - AuditCertificationStatus: Possible certification outcomes
    - MemoryAuditRequest: Request to perform an audit
    - MemoryAuditSession: Session managing a single audit run
    - MemoryAuditReport: Immutable audit findings report
    - MemoryAuditEngine: Main engine coordinating audits
    - HealthAssessment: Aggregated health metrics
    - AuditFinding: Individual finding from an audit

Anti-Patterns Rejected:
    - Mutable audit records
    - Hidden audit results
    - Non-deterministic evaluation
    - Silently ignoring failures
    - Fabricating missing information
"""

from __future__ import annotations

# Core exports - use relative imports for module-local dependencies
try:
    from .enums import (
        AuditTypes,
        AuditCertificationStatus,
    )
except ImportError:
    pass

try:
    from .models import (
        MemoryAuditRequest,
        MemoryAuditSession,
        MemoryAuditReport,
        AuditFinding,
        HealthAssessment,
    )
except ImportError:
    pass

try:
    from .engine import (
        MemoryAuditEngine,
    )
except ImportError:
    pass

__all__ = [
    # Enums
    "AuditTypes",
    "AuditCertificationStatus",
    # Models
    "MemoryAuditRequest",
    "MemoryAuditSession",
    "MemoryAuditReport",
    "AuditFinding",
    "HealthAssessment",
    # Engine
    "MemoryAuditEngine",
]
