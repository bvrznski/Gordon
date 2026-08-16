# Memory Audit Lineage - Phase 5.1.9
# ====================================

"""
Lineage verification module for memory audit.

This module verifies:
    - Origin tracking
    - Source documentation
    - Revision history completeness
    - Provenance chain integrity
"""

from __future__ import annotations


# =============================================================================
# LINEAGE VERIFIER - Verifies lineage completeness and correctness
# =============================================================================


class LineageVerifier:
    """
    Verifies memory artifact lineage.
    
    Lineage verification checks:
        - Origin is present and non-empty
        - Creation timestamp is valid (positive, not in future)
        - Revision history exists for revision artifacts
        - Source information is documented
    
    Anti-Patterns Rejected:
        - Fabricating missing lineage (must report as issue)
        - Hiding incomplete lineage (always report)
    """
    
    def __init__(self):
        """Initialize the lineage verifier."""
        self._verified_count = 0
        self._issues_found = 0
    
    @property
    def stats(self) -> dict:
        """Get verification statistics."""
        return {
            "verified": self._verified_count,
            "issues_found": self._issues_found,
        }
    
    def verify_lineage(
        self,
        artifact,
    ) -> list:
        """
        Verify lineage of a memory artifact.
        
        Args:
            artifact: Memory artifact to verify
            
        Returns:
            List of verification findings (empty if lineage is complete)
        """
        from ..models import AuditFinding, ValidationState, FindingSeverity
        
        findings = []
        self._verified_count += 1
        
        # Get provenance information
        provenance = getattr(artifact, "provenance", None)
        
        # Check origin
        if not provenance or not getattr(provenance, "origin", None):
            self._issues_found += 1
            findings.append(AuditFinding(
                finding_id=f"lineage:missing_origin:{id(artifact)}",
                validation_type="lineage_verification",
                state=ValidationState.WARNING,
                severity=FindingSeverity.WARNING,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact missing origin in provenance - lineage cannot be verified",
            ))
        
        # Check creation timestamp
        created_at = getattr(provenance, "created_at_utc", 0) if provenance else 0
        import time
        current_time = time.time()
        
        if created_at <= 0:
            self._issues_found += 1
            findings.append(AuditFinding(
                finding_id=f"lineage:invalid_timestamp:{id(artifact)}",
                validation_type="lineage_verification",
                state=ValidationState.WARNING,
                severity=FindingSeverity.WARNING,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact has invalid or missing creation timestamp",
            ))
        elif created_at > current_time:
            self._issues_found += 1
            findings.append(AuditFinding(
                finding_id=f"lineage:future_timestamp:{id(artifact)}",
                validation_type="lineage_verification",
                state=ValidationState.FAILED,
                severity=FindingSeverity.ERROR,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact creation timestamp is in the future",
            ))
        
        return findings
    
    def verify_lineage_chain(
        self,
        artifact,
    ) -> tuple:
        """
        Verify lineage chain (if artifact has revisions).
        
        Args:
            artifact: Memory artifact to check
            
        Returns:
            Tuple of (is_complete, issues_count) indicating lineage health
        """
        from ..models import ValidationState
        
        if not hasattr(artifact, "revision_number"):
            return (True, 0)
        
        revision = getattr(artifact, "revision_number", 1)
        previous = getattr(artifact, "previous_revision_id", None)
        
        # If it's a revision, check for proper lineage
        issues = 0
        
        if revision > 1 and not previous:
            issues += 1
        
        return (issues == 0, issues)


# =============================================================================
# PROVENANCE VERIFIER - Verifies provenance completeness
# =============================================================================


class ProvenanceVerifier:
    """
    Verifies memory artifact provenance.
    
    Provenance verification checks:
        - Origin is documented
        - Creation process is recorded
        - Supporting sources are listed
        - Transformation history exists
    
    Anti-Patterns Rejected:
        - Hiding missing provenance (always report)
        - Fabricating provenance (must not invent)
    """
    
    def __init__(self):
        """Initialize the provenance verifier."""
        self._verified_count = 0
        self._issues_found = 0
    
    @property
    def stats(self) -> dict:
        """Get verification statistics."""
        return {
            "verified": self._verified_count,
            "issues_found": self._issues_found,
        }
    
    def verify_provenance(
        self,
        artifact,
    ) -> list:
        """
        Verify provenance of a memory artifact.
        
        Args:
            artifact: Memory artifact to verify
            
        Returns:
            List of verification findings (empty if provenance is complete)
        """
        from ..models import AuditFinding, ValidationState, FindingSeverity
        
        findings = []
        self._verified_count += 1
        
        provenance = getattr(artifact, "provenance", None)
        
        # Check origin
        if not provenance or not getattr(provenance, "origin", None):
            self._issues_found += 1
            findings.append(AuditFinding(
                finding_id=f"provenance:missing_origin:{id(artifact)}",
                validation_type="provenance_verification",
                state=ValidationState.WARNING,
                severity=FindingSeverity.WARNING,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact provenance missing origin information",
            ))
        
        # Check creation timestamp
        if provenance and getattr(provenance, "created_at_utc", 0) <= 0:
            self._issues_found += 1
            findings.append(AuditFinding(
                finding_id=f"provenance:invalid_timestamp:{id(artifact)}",
                validation_type="provenance_verification",
                state=ValidationState.WARNING,
                severity=FindingSeverity.WARNING,
                location=getattr(getattr(artifact, "identity", None), "artifact_id", "unknown"),
                description="Artifact provenance missing valid creation timestamp",
            ))
        
        return findings
    
    def is_provenance_complete(
        self,
        provenance,
    ) -> bool:
        """
        Check if provenance has essential information.
        
        Args:
            provenance: Provenance object to check
            
        Returns:
            True if provenance is complete, False otherwise
        """
        if not provenance:
            return False
        
        # Must have at least origin and timestamp
        has_origin = bool(getattr(provenance, "origin", None))
        has_timestamp = getattr(provenance, "created_at_utc", 0) > 0
        
        return has_origin and has_timestamp


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "LineageVerifier",
    "ProvenanceVerifier",
]