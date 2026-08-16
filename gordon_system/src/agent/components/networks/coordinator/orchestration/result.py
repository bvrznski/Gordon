# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Cognitive Orchestration Result Model
====================================

The result of an orchestration process.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """
    Immutable validation finding.
    
    VALIDATION-LAW-001: Every orchestration request shall validate before planning
    
    Suggested findings per spec:
        INVALID_DEPENDENCY - dependency is malformed or invalid
        MISSING_PARTICIPANT - required participant not specified
        UNSATISFIED_CONSTRAINT - constraint cannot be satisfied
        RESOURCE_CONFLICT - resources conflict with each other
        BARRIER_INCONSISTENT - barrier configuration inconsistent
        INVALID_COMPLETION_POLICY - completion policy invalid
        CYCLE_DETECTED - circular dependency detected
    """
    
    finding_code: str = ""
    """Code identifying the type of finding."""
    
    context_ref: str = ""
    """Reference to the context where finding occurred."""
    
    description: str = ""
    """Human-readable description of the finding."""
    
    severity: str = "warning"
    """Severity level (info, warning, error)."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    def __str__(self) -> str:
        return f"ValidationFinding({self.finding_code}, context={self.context_ref})"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Immutable validation result.
    
    VALIDATION-LAW-002: Every orchestration plan shall validate before publication
    VALIDATION-LAW-007: Validation shall remain side-effect free
    """
    
    is_valid: bool = False
    """Whether the validated artifact passed all checks."""
    
    findings: tuple[ValidationFinding, ...] = ()
    """Findings from validation."""
    
    validated_identity_ref: str = ""
    """Reference to the identity that was validated."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def valid(cls, validated_identity_ref: str) -> ValidationResult:
        return cls(is_valid=True, validated_identity_ref=validated_identity_ref)
    
    @classmethod
    def invalid(cls, findings: tuple[ValidationFinding, ...], validated_identity_ref: str = "") -> ValidationResult:
        return cls(is_valid=False, findings=findings, validated_identity_ref=validated_identity_ref)
    
    def __str__(self) -> str:
        if self.is_valid:
            return "ValidationResult(valid)"
        return f"ValidationResult(invalid, {len(self.findings)} findings)"


@dataclass(frozen=True, slots=True)
class CognitiveOrchestrationResult:
    """
    Immutable orchestration result model.
    
    Suggested fields per spec:
        request_reference
        orchestration_plan
        validation_result
        findings
        limitations
        trace
        status
        provenance
    """
    
    request_ref: str = ""
    """Reference to the original orchestration request."""
    
    plan_ref: str = ""
    """Reference to the generated orchestration plan."""
    
    validation_result: ValidationResult = None  # type: ignore
    """Validation result for the plan."""
    
    findings: tuple[ValidationFinding, ...] = ()
    """Additional findings from orchestration."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on the orchestration."""
    
    trace: tuple[str, ...] = ()
    """Trace of orchestration steps."""
    
    status: str = ""
    """Overall status (from Status enum)."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def success(cls, plan_ref: str) -> CognitiveOrchestrationResult:
        return cls(
            plan_ref=plan_ref,
            validation_result=ValidationResult.valid(plan_ref),
            status="ready",
        )
    
    def is_success(self) -> bool:
        """Check if orchestration was successful."""
        return self.validation_result and self.validation_result.is_valid
    
    def __str__(self) -> str:
        if self.is_success():
            return f"CognitiveOrchestrationResult(success, plan={self.plan_ref})"
        return f"CognitiveOrchestrationResult(failed, {len(self.findings)} findings)"