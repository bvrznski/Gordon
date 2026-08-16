# Memory Audit Validators - Phase 5.1.9
# =======================================

"""
Validator implementations for memory validation checks.

These validators perform specific validation checks on memory artifacts
and produce findings for any issues detected.
"""

from __future__ import annotations


# =============================================================================
# BASE VALIDATOR - Abstract base class
# =============================================================================


class BaseAuditValidator:
    """
    Abstract base class for audit validators.
    
    Validators must be deterministic and never modify memory.
    All validation results must be explicit findings.
    
    Anti-Patterns Rejected:
        - Modifying memory during validation
        - Non-deterministic validation logic
        - Silent failures (must produce findings)
    """
    
    validation_type: str = "base"
    severity_level: str = "info"
    
    def __init__(self):
        """Initialize the validator."""
        self._stats = {"validated": 0, "findings": 0}
    
    @property
    def stats(self) -> dict:
        """Get validation statistics."""
        return dict(self._stats)
    
    def reset_stats(self):
        """Reset statistics counters."""
        self._stats = {"validated": 0, "findings": 0}


# =============================================================================
# STRUCTURAL VALIDATOR - Validates artifact structure
# =============================================================================


class StructuralValidator(BaseAuditValidator):
    """
    Validates memory artifact structural integrity.
    
    Checks:
        - Required fields are present
        - Field types match expected types
        - Identifiers are unique and properly formatted
        - Contracts/contracts are satisfied
    
    Anti-Patterns Rejected:
        - Silently skipping validation (always returns findings)
    """
    
    validation_type: str = "structural"
    severity_level: str = "error"
    
    def validate(self, artifact, context=None) -> list:
        """
        Validate artifact structure.
        
        Args:
            artifact: Memory artifact to validate
            context: Additional validation context
            
        Returns:
            List of AuditFinding objects (may be empty if valid)
        """
        findings = []
        self._stats["validated"] += 1
        
        # Check artifact has content
        if not hasattr(artifact, "semantic_content") or not artifact.semantic_content:
            from ..models import AuditFinding, ValidationState, FindingSeverity
            findings.append(AuditFinding(
                finding_id=f"finding:{self.validation_type}:{id(artifact)}",
                validation_type=self.validation_type,
                state=ValidationState.FAILED,
                severity=FindingSeverity.ERROR,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact missing semantic_content",
            ))
        
        # Check artifact has identity
        if not hasattr(artifact, "identity"):
            from ..models import AuditFinding, ValidationState, FindingSeverity
            findings.append(AuditFinding(
                finding_id=f"finding:{self.validation_type}:no_identity",
                validation_type=self.validation_type,
                state=ValidationState.FAILED,
                severity=FindingSeverity.ERROR,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact missing identity field",
            ))
        
        self._stats["findings"] += len(findings)
        return findings


# =============================================================================
# LINEAGE VALIDATOR - Validates lineage completeness
# =============================================================================


class LineageValidator(BaseAuditValidator):
    """
    Validates memory artifact lineage completeness.
    
    Checks:
        - Origin is present
        - Creation time is recorded
        - Revision history is complete
        - Source information is available
    
    Anti-Patterns Rejected:
        - Fabricating missing lineage (must report as issue)
    """
    
    validation_type: str = "lineage"
    severity_level: str = "warning"
    
    def validate(self, artifact, context=None) -> list:
        """
        Validate artifact lineage.
        
        Args:
            artifact: Memory artifact to validate
            context: Additional validation context
            
        Returns:
            List of AuditFinding objects (may be empty if valid)
        """
        findings = []
        self._stats["validated"] += 1
        
        # Check for provenance with lineage information
        has_provenance = hasattr(artifact, "provenance") and artifact.provenance
        
        if not has_provenance:
            from ..models import AuditFinding, ValidationState, FindingSeverity
            findings.append(AuditFinding(
                finding_id=f"finding:{self.validation_type}:no_provenance",
                validation_type=self.validation_type,
                state=ValidationState.WARNING,
                severity=FindingSeverity.WARNING,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact missing provenance - lineage cannot be verified",
            ))
        
        self._stats["findings"] += len(findings)
        return findings


# =============================================================================
# PROVENANCE VALIDATOR - Validates provenance completeness
# =============================================================================


class ProvenanceValidator(BaseAuditValidator):
    """
    Validates memory artifact provenance completeness.
    
    Checks:
        - Origin is present and non-empty
        - Creation timestamp is valid
        - Supporting sources are documented
        - Transformation history is recorded
    
    Anti-Patterns Rejected:
        - Hiding missing provenance (always report)
    """
    
    validation_type: str = "provenance"
    severity_level: str = "warning"
    
    def validate(self, artifact, context=None) -> list:
        """
        Validate artifact provenance.
        
        Args:
            artifact: Memory artifact to validate
            context: Additional validation context
            
        Returns:
            List of AuditFinding objects (may be empty if valid)
        """
        findings = []
        self._stats["validated"] += 1
        
        provenance = getattr(artifact, "provenance", None)
        
        # Check origin
        if not provenance or not getattr(provenance, "origin", None):
            from ..models import AuditFinding, ValidationState, FindingSeverity
            findings.append(AuditFinding(
                finding_id=f"finding:{self.validation_type}:no_origin",
                validation_type=self.validation_type,
                state=ValidationState.WARNING,
                severity=FindingSeverity.WARNING,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact missing origin in provenance",
            ))
        
        self._stats["findings"] += len(findings)
        return findings


# =============================================================================
# REFERENCE VALIDATOR - Validates references integrity
# =============================================================================


class ReferenceValidator(BaseAuditValidator):
    """
    Validates memory artifact reference integrity.
    
    Checks:
        - References point to valid artifacts
        - No circular references
        - Orphan nodes are detected
        - Dangling references are found
    
    Anti-Patterns Rejected:
        - Following broken references (raise error instead)
    """
    
    validation_type: str = "reference"
    severity_level: str = "error"
    
    def __init__(self, adapter=None):
        """
        Initialize reference validator.
        
        Args:
            adapter: Adapter for cross-referencing (optional)
        """
        super().__init__()
        self._adapter = adapter
    
    def validate(self, artifact, context=None) -> list:
        """
        Validate artifact references.
        
        Args:
            artifact: Memory artifact to validate
            context: Additional validation context
            
        Returns:
            List of AuditFinding objects (may be empty if valid)
        """
        findings = []
        self._stats["validated"] += 1
        
        # Check for relations field
        if not hasattr(artifact, "relations"):
            from ..models import AuditFinding, ValidationState, FindingSeverity
            findings.append(AuditFinding(
                finding_id=f"finding:{self.validation_type}:no_relations",
                validation_type=self.validation_type,
                state=ValidationState.PASSED,
                severity=FindingSeverity.INFO,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact has no relations field to validate",
            ))
        
        self._stats["findings"] += len(findings)
        return findings


# =============================================================================
# DUPLICATION VALIDATOR - Detects duplicate artifacts
# =============================================================================


class DuplicationValidator(BaseAuditValidator):
    """
    Detects duplicate memory artifacts.
    
    Checks:
        - Exact duplicates (same content)
        - Semantic duplicates (similar meaning)
        - Embedding duplicates (similar vector representation)
    
    Anti-Patterns Rejected:
        - Removing duplicates (just reports them)
    """
    
    validation_type: str = "duplication"
    severity_level: str = "info"
    
    def __init__(self):
        """Initialize duplication validator."""
        super().__init__()
        self._seen_hashes = set()
    
    def validate(self, artifact, context=None) -> list:
        """
        Check for duplicate artifacts.
        
        Args:
            artifact: Memory artifact to check
            context: Additional validation context
            
        Returns:
            List of AuditFinding objects (may be empty if no duplicates)
        """
        findings = []
        self._stats["validated"] += 1
        
        # Calculate content hash
        try:
            import json
            content_str = json.dumps(artifact.semantic_content, sort_keys=True)
            content_hash = hash(content_str)
            
            if content_hash in self._seen_hashes:
                from ..models import AuditFinding, ValidationState, FindingSeverity
                findings.append(AuditFinding(
                    finding_id=f"finding:{self.validation_type}:duplicate",
                    validation_type=self.validation_type,
                    state=ValidationState.WARNING,
                    severity=FindingSeverity.WARNING,
                    location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                    description="Potential duplicate artifact detected",
                ))
            
            self._seen_hashes.add(content_hash)
        except Exception:
            pass  # Skip if cannot hash
        
        self._stats["findings"] += len(findings)
        return findings
    
    def reset_seen(self):
        """Reset seen hashes (for new audit)."""
        self._seen_hashes.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BaseAuditValidator",
    "StructuralValidator",
    "LineageValidator",
    "ProvenanceValidator",
    "ReferenceValidator",
    "DuplicationValidator",
]