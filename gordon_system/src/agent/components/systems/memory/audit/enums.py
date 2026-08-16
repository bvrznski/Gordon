# Memory Audit Enums - Phase 5.1.9
# ===================================

"""
Audit Types, Certification Statuses, and other enumerations.

All audit operations use these canonical identifiers to ensure consistency
across the memory audit subsystem.
"""

from __future__ import annotations

from enum import Enum, auto


# =============================================================================
# AUDIT TYPES - Canonical audit operation identifiers
# =============================================================================


class AuditTypes(Enum):
    """
    Canonical audit types supported by the Memory Audit subsystem.
    
    Each audit type validates a specific aspect of memory health:
        - STRUCTURAL: Schema, fields, identifiers, contracts
        - INTEGRITY: Corruption, truncation, checksums
        - CONSISTENCY: Cross-references, contradictions
        - LINEAGE: Origin, source, revision history
        - PROVENANCE: Completeness, ownership, compatibility
        - REFERENCE: Broken refs, dangling refs, orphan nodes
        - INDEX: Index validity, consistency, performance
        - RETRIEVAL: Can memories be retrieved?
        - DUPLICATION: Exact/semantic/embedding duplicates
        - CONSOLIDATION: Memory consolidation state
        - PERFORMANCE: Performance metrics and bottlenecks
        - SECURITY: Access control, permissions, vulnerabilities
        - FULL_SYSTEM: Complete system audit (all of above)
    """
    
    # Core validation types
    STRUCTURAL_AUDIT = "structural"              # Schema, fields, contracts
    INTEGRITY_AUDIT = "integrity"               # Corruption, truncation
    CONSISTENCY_AUDIT = "consistency"           # Cross-references, contradictions
    
    # Provenance and lineage
    LINEAGE_AUDIT = "lineage"                   # Origin, history
    PROVENANCE_AUDIT = "provenance"             # Completeness, ownership
    
    # Reference validation
    REFERENCE_AUDIT = "reference"               # Broken refs, orphans
    INDEX_AUDIT = "index"                       # Index validity
    RETRIEVAL_AUDIT = "retrieval"               # Retrieval behavior
    
    # Analysis types
    DUPLICATION_AUDIT = "duplication"           # Duplicate detection
    CORRUPTION_AUDIT = "corruption"             # Corruption analysis
    
    # System-level audits
    CONSOLIDATION_AUDIT = "consolidation"       # Consolidation state
    PERFORMANCE_AUDIT = "performance"           # Performance metrics
    SECURITY_AUDIT = "security"                 # Security validation
    
    # Composite types
    FULL_SYSTEM_AUDIT = "full_system"           # Complete audit
    HEALTH_CHECK = "health_check"               # Quick health assessment


# =============================================================================
# CERTIFICATION RESULTS - Audit outcome states
# =============================================================================


class AuditCertificationStatus(Enum):
    """
    Possible certification outcomes from a memory audit.
    
    Certification Status Rules:
        - CERTIFIED: Memory passed all validations with no issues
        - CERTIFIED_WITH_WARNINGS: Memory passed but has non-critical warnings
        - DEGRADED: Some validations failed, memory may have issues
        - FAILED: Critical failures detected, memory not trustworthy
        - NOT_AUDITED: Audit could not be completed (e.g., unavailable subsystem)
    """
    
    CERTIFIED = "certified"                           # All checks passed
    CERTIFIED_WITH_WARNINGS = "certified_with_warnings"  # Passed with warnings
    DEGRADED = "degraded"                             # Some failures, degraded
    FAILED = "failed"                                 # Critical failures
    NOT_AUDITED = "not_audited"                       # Could not audit


# =============================================================================
# FINDING SEVERITY - How critical is a finding?
# =============================================================================


class FindingSeverity(Enum):
    """
    Severity levels for audit findings.
    
    Severity determines how findings are aggregated and影响 certification:
        - CRITICAL: Memory is fundamentally compromised
        - ERROR: Significant issues affecting reliability
        - WARNING: Non-critical issues worth noting
        - INFO: Observational findings, not necessarily problematic
    """
    
    CRITICAL = "critical"      # Memory fundamentally compromised
    ERROR = "error"           # Significant reliability issues
    WARNING = "warning"       # Non-critical issues to note
    INFO = "info"             # Observational findings


# =============================================================================
# AUDIT PHASES - Audit execution stages
# =============================================================================


class AuditPhases(Enum):
    """
    Stages of audit execution.
    
    The audit pipeline flows through these phases:
        1. PLANNING: Decide what to audit and how
        2. SNAPSHOT: Capture memory state for auditing
        3. VALIDATION: Run structural/semantic validations
        4. ANALYSIS: Perform deep analysis (lineage, provenance)
        5. VERIFICATION: Cross-check findings
        6. HEALTH: Aggregate health metrics
        7. REPORTING: Generate final report and certification
    """
    
    PLANNING = "planning"          # Audit planning phase
    SNAPSHOT = "snapshot"          # Memory snapshot capture
    VALIDATION = "validation"      # Initial validation
    ANALYSIS = "analysis"          # Deep analysis phase
    VERIFICATION = "verification"  # Cross-verification
    HEALTH = "health"              # Health aggregation
    REPORTING = "reporting"        # Report generation


# =============================================================================
# MEMORY DOMAINS - Memory types that can be audited
# =============================================================================


class MemoryDomains(Enum):
    """
    Memory domain types supported for auditing.
    
    The audit subsystem can audit any memory type, but these are the canonical
    domains defined in Gordon's architecture:
        
        - WORKING_MEMORY: Active working memory contents
        - EPISODIC_MEMORY: Event-based memories with temporal context
        - SEMANTIC_MEMORY: Factual knowledge and concepts
        - PROCEDURAL_MEMORY: Skills and habits
        - AUTOBIOGRAPHICAL_MEMORY: Personal history and self-references
        - WORLD_MODEL_MEMORY: Model of external world
        - SELF_MODEL_MEMORY: Model of self and identity
        - EMOTIONAL_MEMORY: Emotionally-tagged memories
        - SPATIAL_MEMORY: Spatial relationships and navigation
        - LONG_TERM_MEMORY: Long-term storage
        - EXTERNAL_MEMORY: External system integrations
        - CACHE_LAYERS: Cache layer health and consistency
    """
    
    WORKING_MEMORY = "working_memory"
    EPISODIC_MEMORY = "episodic_memory"
    SEMANTIC_MEMORY = "semantic_memory"
    PROCEDURAL_MEMORY = "procedural_memory"
    AUTOBIOGRAPHICAL_MEMORY = "autobiographical_memory"
    WORLD_MODEL_MEMORY = "world_model_memory"
    SELF_MODEL_MEMORY = "self_model_memory"
    EMOTIONAL_MEMORY = "emotional_memory"
    SPATIAL_MEMORY = "spatial_memory"
    LONG_TERM_MEMORY = "long_term_memory"
    EXTERNAL_MEMORY = "external_memory"
    CACHE_LAYERS = "cache_layers"


# =============================================================================
# VALIDATION STATES - Individual validation results
# =============================================================================


class ValidationState(Enum):
    """
    States for individual validation checks.
    
    Each validation check produces one of these states:
        - PASSED: Check succeeded, no issues found
        - FAILED: Check failed, issue detected
        - WARNING: Check passed but with concerns
        - NOT_APPLICABLE: Check not relevant to this memory
        - SKIPPED: Check was skipped (e.g., unavailable data)
    """
    
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"
    SKIPPED = "skipped"


# =============================================================================
# REFERENCE TYPES - Reference validation categories
# =============================================================================


class ReferenceType(Enum):
    """
    Categories of memory references.
    
    Used for reference integrity validation:
        - PARENT: Reference to parent memory (hierarchical)
        - CHILD: Reference to child memory (hierarchical)
        - FORWARD: Forward reference (this → that)
        - BACKWARD: Backward reference (that → this)
        - SEMANTIC: Semantic relationship
        - EVIDENCE: Evidence supporting this memory
    """
    
    PARENT = "parent"
    CHILD = "child"
    FORWARD = "forward"
    BACKWARD = "backward"
    SEMANTIC = "semantic"
    EVIDENCE = "evidence"


# =============================================================================
# DATA INTEGRITY STATES - Integrity verification results
# =============================================================================


class DataIntegrityState(Enum):
    """
    States for data integrity verification.
    
    Used when checking memory artifact integrity:
        - VALID: Data passes all integrity checks
        - CORRUPTED: Data is corrupted or malformed
        - TRUNCATED: Data appears truncated
        - INCOMPLETE: Data is incomplete but not necessarily corrupt
        - UNCHECKABLE: Cannot verify (e.g., missing checksum)
    """
    
    VALID = "valid"
    CORRUPTED = "corrupted"
    TRUNCATED = "truncated"
    INCOMPLETE = "incomplete"
    UNCHECKABLE = "unchecked"


__all__ = [
    # Audit type identifiers
    "AuditTypes",
    # Certification outcomes
    "AuditCertificationStatus",
    # Finding severity levels
    "FindingSeverity",
    # Execution phases
    "AuditPhases",
    # Memory domain types
    "MemoryDomains",
    # Validation states
    "ValidationState",
    # Reference categories
    "ReferenceType",
    # Integrity states
    "DataIntegrityState",
]