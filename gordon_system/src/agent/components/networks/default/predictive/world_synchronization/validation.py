# Canonical World Synchronization Validation - Phase 4.9.6
# =========================================================
"""
Validation system for WorldModelSynchronization subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Immutable validation result.
    
    Fields:
        status:         Validation outcome (PASSED/FAILED/SKIPPED/PENDING)
        findings:       Typed findings from validation checks
        error_message:  Human-readable error description if failed
    
    Rules:
        - Results are immutable once created
        - No side-effect data in result payload
    """
    status: str = "PENDING"  # PASSED, FAILED, SKIPPED, PENDING
    findings: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class SynchronizationValidator:
    """
    Validator interface for world synchronization.
    
    Methods:
        validate_request:   Validate incoming request
        validate_graph:     Validate graph structure
        validate_ontology:  Validate ontology consistency
        validate_snapshot:  Validate snapshot integrity
    
    Rules:
        - Validator remains immutable
        - No state mutation during validation
    """
    identity: str = "world_synchronization_validator"