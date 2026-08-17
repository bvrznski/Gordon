# Knowledge Concepts - Validation - Phase 6.3
# ============================================

"""
Validation utilities for Gordon's Concept Subsystem.

This module provides validation functions for concepts, instances,
and their relationships according to the normative specifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# VALIDATION FINDING TYPES
# =============================================================================


@dataclass(frozen=True)
class ValidationFinding:
    """
    Individual validation finding.
    
    Records a specific validation issue detected during semantic integrity check.
    """
    identity: str
    kind: str  # "error", "warning", or "info"
    component: str  # Component that failed (e.g., "concept.identity")
    message: str
    severity: str = "low"  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "kind": self.kind,
            "component": self.component,
            "message": self.message,
            "severity": self.severity,
        }


# =============================================================================
# VALIDATION RESULTS
# =============================================================================


@dataclass(frozen=True)
class ValidationResult:
    """
    Complete validation result.
    
    Aggregates all findings from a validation pass.
    """
    identity: str
    validated_object: str  # Type of object validated (e.g., "Concept")
    is_valid: bool
    findings: Tuple[ValidationFinding, ...] = field(default_factory=tuple)
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def finding_count(self) -> int:
        return len(self.findings)
    
    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.kind == "error")
    
    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.kind == "warning")
    
    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.kind == "info")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "validated_object": self.validated_object,
            "is_valid": self.is_valid,
            "findings": [f.to_dict() for f in self.findings],
            "finding_count": len(self.findings),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================


def validate_concept_identity(identity: str) -> Tuple[bool, List[str]]:
    """
    Validate a concept identity string.
    
    Requirements:
        - Must start with "concept:" prefix
        - Must contain valid UUID-like format after prefix
    
    Args:
        identity: The identity string to validate
        
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    if not identity:
        issues.append("Concept identity is empty")
        return False, issues
    
    if not identity.startswith("concept:"):
        issues.append(f"Concept identity must start with 'concept:': {identity}")
    
    # Check format
    rest = identity[8:] if identity.startswith("concept:") else identity
    if len(rest) < 8:
        issues.append(f"Concept identity suffix too short: {rest}")
    
    return len(issues) == 0, issues


def validate_canonical_name(name: str) -> Tuple[bool, List[str]]:
    """
    Validate a canonical concept name.
    
    Args:
        name: The name to validate
        
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    if not name:
        issues.append("Canonical name is empty")
        return False, issues
    
    if len(name) > 128:
        issues.append(f"Canonical name too long: {len(name)} characters")
    
    # Basic format check
    if "  " in name:
        issues.append("Canonical name contains multiple consecutive spaces")
    
    return len(issues) == 0, issues


def validate_confidence(confidence: float) -> Tuple[bool, List[str]]:
    """
    Validate a confidence value.
    
    Args:
        confidence: Confidence value (should be 0.0-1.0)
        
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    if not isinstance(confidence, (int, float)):
        issues.append(f"Confidence must be numeric: {confidence}")
        return False, issues
    
    if confidence < 0.0 or confidence > 1.0:
        issues.append(f"Confidence must be between 0.0 and 1.0: {confidence}")
    
    return len(issues) == 0, issues


# =============================================================================
# MAIN VALIDATION ENGINE
# =============================================================================


class ConceptValidationEngine:
    """
    Engine for validating concept data structures.
    """
    
    def __init__(
        self,
        check_identity: bool = True,
        check_name: bool = True,
        check_confidence: bool = True,
        check_hierarchy: bool = True,
    ):
        """
        Initialize the validation engine.
        
        Args:
            check_identity: Validate concept identity format
            check_name: Validate canonical name
            check_confidence: Validate confidence values
            check_hierarchy: Check hierarchy constraints (no cycles, etc.)
        """
        self._check_identity = check_identity
        self._check_name = check_name
        self._check_confidence = check_confidence
        self._check_hierarchy = check_hierarchy
    
    def validate_concept(
        self,
        concept_data: Dict[str, Any],
    ) -> ValidationResult:
        """
        Validate a concept data structure.
        
        Args:
            concept_data: The concept to validate
            
        Returns:
            ValidationResult with all findings
        """
        findings = []
        identity = concept_data.get("identity", "unknown")
        concept_type = "Concept"
        
        # Check required fields
        if self._check_identity:
            is_valid, issues = validate_concept_identity(identity)
            for issue in issues:
                findings.append(ValidationFinding(
                    identity=f"vf:{identity[:8] if len(identity) > 8 else identity}",
                    kind="error",
                    component="concept.identity",
                    message=issue,
                    severity="high" if "empty" in issue.lower() else "medium",
                ))
        
        if self._check_name:
            name = concept_data.get("canonical_name", "")
            is_valid, issues = validate_canonical_name(name)
            for issue in issues:
                findings.append(ValidationFinding(
                    identity=f"vf:{identity[:8] if len(identity) > 8 else identity}",
                    kind="error",
                    component="concept.canonical_name",
                    message=issue,
                    severity="high" if "empty" in issue.lower() else "medium",
                ))
        
        if self._check_confidence:
            confidence = concept_data.get("confidence", 0.5)
            is_valid, issues = validate_confidence(confidence)
            for issue in issues:
                findings.append(ValidationFinding(
                    identity=f"vf:{identity[:8] if len(identity) > 8 else identity}",
                    kind="error",
                    component="concept.confidence",
                    message=issue,
                    severity="medium",
                ))
        
        return ValidationResult(
            identity=f"validation:{identity[:8] if len(identity) > 8 else identity}",
            validated_object=concept_type,
            is_valid=len(findings) == 0,
            findings=tuple(findings),
        )
    
    def validate_instance(
        self,
        instance_data: Dict[str, Any],
    ) -> ValidationResult:
        """
        Validate an instance data structure.
        
        Args:
            instance_data: The instance to validate
            
        Returns:
            ValidationResult with all findings
        """
        findings = []
        identity = instance_data.get("identity", "unknown")
        
        # Check required concept_ids
        concept_ids = instance_data.get("concept_ids", [])
        if not isinstance(concept_ids, (list, tuple)) or len(concept_ids) == 0:
            findings.append(ValidationFinding(
                identity=f"vf:{identity[:8] if len(identity) > 8 else identity}",
                kind="error",
                component="instance.concept_ids",
                message="Instance must reference at least one concept",
                severity="high",
            ))
        
        # Validate confidence
        confidence = instance_data.get("confidence", 0.5)
        is_valid, issues = validate_confidence(confidence)
        for issue in issues:
            findings.append(ValidationFinding(
                identity=f"vf:{identity[:8] if len(identity) > 8 else identity}",
                kind="error",
                component="instance.confidence",
                message=issue,
                severity="medium",
            ))
        
        return ValidationResult(
            identity=f"validation:{identity[:8] if len(identity) > 8 else identity}",
            validated_object="Instance",
            is_valid=len(findings) == 0,
            findings=tuple(findings),
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def validate_concept_fast(concept_data: Dict[str, Any]) -> bool:
    """
    Fast validation of a concept (returns just boolean).
    
    Args:
        concept_data: The concept to validate
        
    Returns:
        True if valid, False otherwise
    """
    engine = ConceptValidationEngine()
    result = engine.validate_concept(concept_data)
    return result.is_valid


def validate_instance_fast(instance_data: Dict[str, Any]) -> bool:
    """
    Fast validation of an instance (returns just boolean).
    
    Args:
        instance_data: The instance to validate
        
    Returns:
        True if valid, False otherwise
    """
    engine = ConceptValidationEngine()
    result = engine.validate_instance(instance_data)
    return result.is_valid


__all__ = [
    # Finding and results
    "ValidationFinding",
    "ValidationResult",
    # Validation utilities
    "validate_concept_identity",
    "validate_canonical_name",
    "validate_confidence",
    # Engine
    "ConceptValidationEngine",
    # Convenience functions
    "validate_concept_fast",
    "validate_instance_fast",
]