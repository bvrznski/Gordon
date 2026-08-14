# Remediation Module - Phase 3.24
# ================================
#
# Automatic remediation for validation findings.

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from . import ValidationSeverity, ValidationFinding, ValidationResult


class RemediationType(Enum):
    """Types of remediations."""
    AUTOMATIC = "automatic"
    SEMIAUTOMATIC = "semiautomatic"
    MANUAL = "manual"


@dataclass(frozen=True)
class RemediationProposal:
    """
    A proposed remediation for a finding.
    
    REMEDIATION PRINCIPLES:
        - Remediation never violates architectural contracts
        - All remediations generate evidence
        - Automatic remediation is safe and reversible
    """
    
    proposal_id: str = field(default_factory=lambda: f"rem_{time.time_ns()}")
    finding_id: str
    remediation_type: RemediationType = RemediationType.AUTOMATIC
    description: Optional[str] = None
    proposed_action: Optional[str] = None
    
    # Evidence
    timestamp_utc: float = field(default_factory=time.time)
    proposer: str = "unknown"
    
    @property
    def is_safe(self) -> bool:
        """Check if remediation is safe."""
        return self.remediation_type == RemediationType.AUTOMATIC


@dataclass(frozen=True)
class RemediationEvidence:
    """
    Evidence of remediation applied.
    
    INVARIANTS:
        EVD-001: Evidence is immutable once created
        EVD-002: Evidence includes timestamp and proposer
    """
    
    evidence_id: str = field(default_factory=lambda: f"evd_{time.time_ns()}")
    remediation_id: str
    finding_id: str
    
    # Remediation details
    applied_at_utc: float = field(default_factory=time.time)
    applied_by: str = "unknown"
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# AUTOMATIC REMEDIATION PROPOSERS
# =============================================================================

class DuplicateRemovalProposer:
    """Proposes removal of duplicate implementations."""
    
    def __init__(self):
        self.name = "duplicate_removal_proposer"
    
    def propose(self, duplicates: Tuple[str, ...]) -> List[RemediationProposal]:
        """
        Propose remediation for duplicate implementations.
        
        Args:
            duplicates: IDs of duplicate implementations
            
        Returns:
            List of remediation proposals
        """
        if len(duplicates) < 2:
            return []
        
        return [
            RemediationProposal(
                finding_id=dup,
                remediation_type=RemediationType.AUTOMATIC,
                description=f"Remove duplicate implementation: {dup}",
                proposed_action=f"delete_or_deprecate:{dup}",
            )
            for dup in duplicates[1:]  # Keep first, propose removal of others
        ]


class MetadataConsistencyProposer:
    """Proposes remediation for metadata inconsistencies."""
    
    def __init__(self):
        self.name = "metadata_consistency_proposer"
    
    def propose(
        self, 
        entity_id: str,
        missing_field: str,
        expected_value: Optional[str] = None
    ) -> RemediationProposal:
        """
        Propose remediation for missing metadata field.
        
        Args:
            entity_id: ID of entity with inconsistent metadata
            missing_field: Name of missing field
            expected_value: Expected value for the field
            
        Returns:
            Remediation proposal
        """
        return RemediationProposal(
            finding_id=entity_id,
            remediation_type=RemediationType.SEMIAUTOMATIC,
            description=f"Add missing metadata field: {missing_field}",
            proposed_action=f"add_metadata:{missing_field}={expected_value or 'auto-generated'}",
        )


class DependencyViolationProposer:
    """Proposes remediation for dependency violations."""
    
    def __init__(self):
        self.name = "dependency_violation_proposer"
    
    def propose(
        self,
        entity_id: str,
        violation_type: str,
        fix_action: str
    ) -> RemediationProposal:
        """
        Propose remediation for dependency violation.
        
        Args:
            entity_id: ID of entity with dependency issue
            violation_type: Type of dependency violation
            fix_action: How to fix the violation
            
        Returns:
            Remediation proposal
        """
        return RemediationProposal(
            finding_id=entity_id,
            remediation_type=RemediationType.AUTOMATIC,
            description=f"Fix {violation_type} for {entity_id}",
            proposed_action=fix_action,
        )


# =============================================================================
# COMPOSITE REMEDIATOR
# =============================================================================

class Remediator:
    """
    Composite remediator that proposes automatic remediations.
    
    REMEDIATION PRINCIPLES:
        - Automatic remediation is safe and reversible
        - Never violates architectural contracts
        - All remediations generate evidence
    """
    
    def __init__(self):
        self.duplicate_removal = DuplicateRemovalProposer()
        self.metadata_consistency = MetadataConsistencyProposer()
        self.dependency_violation = DependencyViolationProposer()
    
    def name(self) -> str:
        return "composite_remediator"
    
    def propose_remediations(
        self,
        findings: Tuple[ValidationFinding, ...]
    ) -> List[RemediationProposal]:
        """
        Propose remediations for all findings.
        
        Args:
            findings: Findings to remediate
            
        Returns:
            List of proposed remediations
        """
        proposals = []
        
        for finding in findings:
            # Skip informational findings
            if finding.is_info:
                continue
            
            # Propose based on category
            if finding.category == "duplicate":
                proposals.append(
                    RemediationProposal(
                        finding_id=finding.finding_id,
                        remediation_type=RemediationType.AUTOMATIC,
                        description=f"Remove duplicate: {finding.entity_id}",
                        proposed_action=f"remove:{finding.entity_id}",
                    )
                )
            elif finding.category == "metadata":
                proposals.append(
                    RemediationProposal(
                        finding_id=finding.finding_id,
                        remediation_type=RemediationType.SEMIAUTOMATIC,
                        description=f"Fix metadata for {finding.entity_id}",
                        proposed_action="update_metadata",
                    )
                )
            elif finding.category == "dependency":
                proposals.append(
                    RemediationProposal(
                        finding_id=finding.finding_id,
                        remediation_type=RemediationType.AUTOMATIC,
                        description=f"Fix dependency issue: {finding.message}",
                        proposed_action="fix_dependency",
                    )
                )
        
        return proposals
    
    def apply_remediation(
        self,
        proposal: RemediationProposal
    ) -> RemediationEvidence:
        """
        Apply a remediation and generate evidence.
        
        Args:
            proposal: The remediation to apply
            
        Returns:
            Evidence of the applied remediation
        """
        # In real implementation, this would execute the fix
        return RemediationEvidence(
            remediation_id=proposal.proposal_id,
            finding_id=proposal.finding_id,
            applied_at_utc=time.time(),
            applied_by=self.name(),
            success=True,
            details={
                "action": proposal.proposed_action,
                "description": proposal.description,
            }
        )


__all__ = [
    "RemediationType",
    "RemediationProposal",
    "RemediationEvidence",
    "DuplicateRemovalProposer",
    "MetadataConsistencyProposer",
    "DependencyViolationProposer",
    "Remediator",
]