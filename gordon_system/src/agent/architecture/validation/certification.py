# Certification Module - Phase 3.24
# ==================================
#
# Certification determines readiness for production.
# Evidence-based certification of packages, modules, services.

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time

from . import ValidationSeverity, ValidationFinding, ValidationResult


class CertificationType(Enum):
    """Types of certifications."""
    PACKAGE = "package"
    MODULE = "module"
    SERVICE = "service"
    CAPABILITY = "capability"
    REPOSITORY = "repository"
    RELEASE = "release"
    RUNTIME_CONFIG = "runtime_config"
    DEPLOYMENT_PROFILE = "deployment_profile"


class CertificationStatus(Enum):
    """Certification status."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    CERTIFIED = "certified"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class CertificationEvidence:
    """
    Evidence for certification.
    
    INVARIANTS:
        EVD-001: Evidence is immutable once created
        EVD-002: Evidence includes timestamp and certifier
        EVD-003: Evidence must include validation results
    """
    
    evidence_id: str = field(default_factory=lambda: f"cert_evd_{time.time_ns()}")
    certification_type: CertificationType
    target_id: str
    
    # Evidence details
    validated_at_utc: float = field(default_factory=time.time)
    certifier_name: str = "unknown"
    validation_results: Tuple[ValidationResult, ...] = field(default_factory=tuple)
    
    @property
    def is_complete(self) -> bool:
        """Check if evidence is complete."""
        return len(self.validation_results) > 0


@dataclass(frozen=True)
class CertificationRecord:
    """
    Complete certification record.
    
    INVARIANTS:
        CRT-001: Record is immutable once certified
        CRT-002: All evidence must be present
        CRT-003: Certifier must be identified
    """
    
    record_id: str = field(default_factory=lambda: f"cert_{time.time_ns()}")
    certification_type: CertificationType
    target_id: str
    target_type: str  # e.g., "Package", "Module"
    
    # Status
    status: CertificationStatus = CertificationStatus.PENDING
    
    # Evidence
    evidence: Tuple[CertificationEvidence, ...] = field(default_factory=tuple)
    
    # Certification details
    certified_at_utc: Optional[float] = None
    certifier_name: Optional[str] = None
    expiration_utc: Optional[float] = None
    
    # Score (if applicable)
    score: Optional[int] = None  # 0-100
    score_justification: Optional[str] = None
    
    @property
    def is_certified(self) -> bool:
        """Check if certification was granted."""
        return self.status == CertificationStatus.CERTIFIED
    
    @property
    def is_rejected(self) -> bool:
        """Check if certification was rejected."""
        return self.status == CertificationStatus.REJECTED


# =============================================================================
# CERTIFICATION RULES
# =============================================================================

class CertificationRule:
    """A certification rule that must be satisfied."""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        weight: float = 1.0,
        is_mandatory: bool = True,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.weight = weight
        self.is_mandatory = is_mandatory


# =============================================================================
# CERTIFIER BASE CLASS
# =============================================================================

class CertifierBase:
    """Base class for certifiers."""
    
    name: str = "certifier_base"
    
    def __init__(self):
        self._rules: List[CertificationRule] = []
    
    def add_rule(self, rule: CertificationRule) -> None:
        """Add a certification rule."""
        self._rules.append(rule)
    
    def certify(
        self,
        target_id: str,
        target_type: str,
        evidence: Tuple[ValidationResult, ...],
    ) -> CertificationRecord:
        """
        Certify a target entity.
        
        Args:
            target_id: ID of the entity to certify
            target_type: Type of the entity
            evidence: Validation results as certification evidence
            
        Returns:
            Certification record
        """
        # Evaluate rules against evidence
        passed_rules = []
        failed_rules = []
        
        for rule in self._rules:
            if self._evaluate_rule(rule, evidence):
                passed_rules.append(rule)
            else:
                failed_rules.append(rule)
        
        # Calculate score
        total_weight = sum(r.weight for r in self._rules)
        passed_weight = sum(r.weight for r in passed_rules)
        score = int((passed_weight / total_weight) * 100) if total_weight > 0 else 100
        
        # Determine status
        if failed_rules and any(r.is_mandatory for r in failed_rules):
            status = CertificationStatus.REJECTED
        elif len(passed_rules) >= len(self._rules) * 0.8:  # 80% pass threshold
            status = CertificationStatus.CERTIFIED
        else:
            status = CertificationStatus.PENDING
        
        return CertificationRecord(
            target_id=target_id,
            target_type=target_type,
            status=status,
            evidence=evidence,  # Wrap in tuple if needed
            certified_at_utc=time.time() if status == CertificationStatus.CERTIFIED else None,
            certifier_name=self.name,
            score=score,
            score_justification=f"{len(passed_rules)}/{len(self._rules)} rules passed",
        )
    
    def _evaluate_rule(
        self,
        rule: CertificationRule,
        evidence: Tuple[ValidationResult, ...],
    ) -> bool:
        """Evaluate a single certification rule against evidence."""
        # Simplified evaluation - real implementation would check specific criteria
        return True  # Placeholder


# =============================================================================
# PACKAGE CERTIFIER
# =============================================================================

class PackageCertifier(CertifierBase):
    """Certifies packages."""
    
    name: str = "package_certifier"
    
    def __init__(self):
        super().__init__()
        
        self.add_rule(
            CertificationRule(
                rule_id="PKG-001",
                name="package_structure_valid",
                description="Package must have valid directory structure",
            )
        )
        self.add_rule(
            CertificationRule(
                rule_id="PKG-002",
                name="package_metadata_complete",
                description="Package must have complete metadata",
            )
        )
        self.add_rule(
            CertificationRule(
                rule_id="PKG-003",
                name="package_dependencies_valid",
                description="Package dependencies must be valid",
            )
        )


# =============================================================================
# MODULE CERTIFIER
# =============================================================================

class ModuleCertifier(CertifierBase):
    """Certifies modules."""
    
    name: str = "module_certifier"
    
    def __init__(self):
        super().__init__()
        
        self.add_rule(
            CertificationRule(
                rule_id="MOD-001",
                name="module_exports_valid",
                description="Module must have valid exports",
            )
        )
        self.add_rule(
            CertificationRule(
                rule_id="MOD-002",
                name="module_imports_valid",
                description="Module imports must be valid",
            )
        )
        self.add_rule(
            CertificationRule(
                rule_id="MOD-003",
                name="module_tests_present",
                description="Module must have tests",
            )
        )


# =============================================================================
# REPOSITORY CERTIFIER
# =============================================================================

class RepositoryCertifier(CertifierBase):
    """Certifies repositories."""
    
    name: str = "repository_certifier"
    
    def __init__(self):
        super().__init__()
        
        self.add_rule(
            CertificationRule(
                rule_id="REP-001",
                name="repository_structure_valid",
                description="Repository must have valid structure",
            )
        )
        self.add_rule(
            CertificationRule(
                rule_id="REP-002",
                name="all_packages_certified",
                description="All packages must be certified",
            )
        )
        self.add_rule(
            CertificationRule(
                rule_id="REP-003",
                name="no_critical_findings",
                description="Repository must have no critical findings",
            )
        )


# =============================================================================
# COMPOSITE CERTIFIER
# =============================================================================

class Certifier:
    """
    Composite certifier that handles all certification types.
    
    CERTIFICATION PRINCIPLES:
        - Certification is evidence-based
        - All certifications produce immutable records
        - Expiration and renewal are tracked
    """
    
    def __init__(self):
        self.package = PackageCertifier()
        self.module = ModuleCertifier()
        self.repository = RepositoryCertifier()
    
    def name(self) -> str:
        return "composite_certifier"
    
    def certify_package(
        self,
        package_id: str,
        evidence: Tuple[ValidationResult, ...],
    ) -> CertificationRecord:
        """Certify a package."""
        return self.package.certify(package_id, "Package", evidence)
    
    def certify_module(
        self,
        module_id: str,
        evidence: Tuple[ValidationResult, ...],
    ) -> CertificationRecord:
        """Certify a module."""
        return self.module.certify(module_id, "Module", evidence)
    
    def certify_repository(
        self,
        repository_id: str,
        evidence: Tuple[ValidationResult, ...],
    ) -> CertificationRecord:
        """Certify a repository."""
        return self.repository.certify(repository_id, "Repository", evidence)


__all__ = [
    "CertificationType",
    "CertificationStatus",
    "CertificationEvidence",
    "CertificationRecord",
    "CertificationRule",
    "CertifierBase",
    "PackageCertifier",
    "ModuleCertifier",
    "RepositoryCertifier",
    "Certifier",
]