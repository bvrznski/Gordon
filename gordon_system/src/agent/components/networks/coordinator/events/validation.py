# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Validation Models - Semantic Event Validation

This module defines how cognitive events are validated before publication.
"""

from dataclasses import dataclass, field
from enum import Enum, unique


@unique
class ValidationFindingCode(Enum):
    """
    Codes for validation findings.
    
    VALIDATION FINDING LAWS (VALID-FIND-LAW)
    ----------------------------------------
    VALID-FIND-LAW-001: Each finding has exactly one code
    VALID-FIND-LAW-002: Findings are explicit and inspectable
    """
    
    INVALID_EVENT_KIND = "invalid_event_kind"
    """Event kind is not recognized."""
    
    INVALID_PAYLOAD = "invalid_payload"
    """Payload reference is invalid or inaccessible."""
    
    INVALID_CORRELATION = "invalid_correlation"
    """Correlation identity references unknown event."""
    
    INVALID_CAUSATION = "invalid_causation"
    """Causation references circular or impossible relationships."""
    
    INVALID_SOURCE_NETWORK = "invalid_source_network"
    """Source network is not registered or invalid."""
    
    DUPLICATE_EVENT = "duplicate_event"
    """Event with same identity already exists."""
    
    STALE_EVENT = "stale_event"
    """Event is outdated relative to known state."""
    
    INVALID_REVISION = "invalid_revision"
    """Revision has invalid lineage or reference."""


@dataclass(frozen=True)
class ValidationFinding:
    """
    A single validation finding.
    
    VALIDATION FINDING LAWS (FINDING-LAW)
    -------------------------------------
    FINDING-LAW-001: Each finding has a code and description
    FINDING-LAW-002: Findings are immutable
    """
    
    # Finding code
    _finding_code: ValidationFindingCode
    
    # Description of the issue
    _description: str
    
    # Contextual information
    _context: dict = field(default_factory=dict)
    
    @property
    def finding_code(self) -> ValidationFindingCode:
        """Get the finding code."""
        return self._finding_code
    
    @property
    def description(self) -> str:
        """Get the description."""
        return self._description
    
    @property
    def context(self) -> dict:
        """Get the contextual information."""
        return self._context
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "finding_code": self._finding_code.value,
            "description": self._description,
            "context": dict(self._context),
        }


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of event validation.
    
    VALIDATION RESULT LAWS (RESULT-LAW)
    -----------------------------------
    RESULT-LAW-001: Validation is side-effect free
    RESULT-LAW-002: Results include all findings
    RESULT-LAW-003: Validation is deterministic
    """
    
    # Whether validation passed
    _is_valid: bool
    
    # List of all findings (empty if valid)
    _findings: tuple[ValidationFinding, ...] = field(default_factory=tuple)
    
    # Limitations of the validation
    _limitations: dict = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return self._is_valid
    
    @property
    def findings(self) -> tuple[ValidationFinding, ...]:
        """Get all validation findings."""
        return self._findings
    
    @property
    def limitations(self) -> dict:
        """Get the limitations."""
        return self._limitations
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "is_valid": self._is_valid,
            "findings": [f.to_dict() for f in self._findings],
            "limitations": dict(self._limitations),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ValidationResult":
        """
        Create a validation result from a dictionary.
        
        Args:
            data: Dictionary with validation result data
            
        Returns:
            New ValidationResult instance
        """
        return cls(
            _is_valid=data.get("is_valid", True),
            _findings=tuple(
                ValidationFinding(
                    finding_code=ValidationFindingCode(f["finding_code"]),
                    description=f["description"],
                    context=dict(f.get("context", {})),
                )
                for f in data.get("findings", [])
            ),
            _limitations=dict(data.get("limitations", {})),
            _provenance=dict(data.get("provenance", {})),
        )


class CognitiveEventValidationEngine:
    """
    Engine for validating cognitive events.
    
    The validation engine checks event requests against all rules before
    allowing event construction and publication.
    
    ENGINE LAWS (ENGINE-LAW)
    ------------------------
    ENGINE-LAW-001: Validation is deterministic
    ENGINE-LAW-002: Validation is side-effect free
    ENGINE-LAW-003: All rules must pass for valid events
    """
    
    def validate_event_request(
        self, event_kind: str, source_network: str, payload_reference: str
    ) -> ValidationResult:
        """
        Validate an event request.
        
        Args:
            event_kind: The kind of event
            source_network: Source network identifier
            payload_reference: Reference to the semantic payload
            
        Returns:
            ValidationResult indicating pass/failure with findings
        """
        findings = []
        
        # Check event kind is valid
        if not self._is_valid_event_kind(event_kind):
            findings.append(
                ValidationFinding(
                    finding_code=ValidationFindingCode.INVALID_EVENT_KIND,
                    description=f"Unknown event kind: '{event_kind}'",
                )
            )
        
        # Check source network is registered (simplified - would check against
        # known networks in real implementation)
        if not source_network or len(source_network) < 1:
            findings.append(
                ValidationFinding(
                    finding_code=ValidationFindingCode.INVALID_SOURCE_NETWORK,
                    description="Source network identifier is empty or invalid",
                )
            )
        
        # Check payload reference exists (simplified check)
        if not payload_reference or len(payload_reference) < 1:
            findings.append(
                ValidationFinding(
                    finding_code=ValidationFindingCode.INVALID_PAYLOAD,
                    description="Payload reference is empty or invalid",
                )
            )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            findings=tuple(findings),
            limitations={},
            provenance={"validated_by": "CognitiveEventValidationEngine"},
        )
    
    def _is_valid_event_kind(self, kind: str) -> bool:
        """Check if the event kind is recognized."""
        # Simplified - in real implementation would check against enum
        return len(kind) > 0 and kind.isalpha()
    
    def validate_event(
        self,
        event_identity: str,
        event_kind: str,
        source_network: str,
        payload_reference: str,
        revision: int = 1,
    ) -> ValidationResult:
        """
        Validate an event against all rules.
        
        Args:
            event_identity: Event's unique identity
            event_kind: Event kind/type
            source_network: Source network identifier
            payload_reference: Reference to semantic payload
            revision: Event revision number
            
        Returns:
            ValidationResult with findings if any validation fails
        """
        result = self.validate_event_request(
            event_kind=event_kind,
            source_network=source_network,
            payload_reference=payload_reference,
        )
        
        # Additional event-specific validations
        if not event_identity or len(event_identity) < 1:
            result._findings += (
                ValidationFinding(
                    finding_code=ValidationFindingCode.INVALID_EVENT_KIND,
                    description="Event identity is empty",
                ),
            )
        
        if revision < 1:
            result._findings += (
                ValidationFinding(
                    finding_code=ValidationFindingCode.INVALID_REVISION,
                    description=f"Revision must be >= 1, got {revision}",
                ),
            )
        
        return result