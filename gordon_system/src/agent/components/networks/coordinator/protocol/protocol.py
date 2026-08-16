# Gordon Cognitive Architecture - Phase 4.11.5
# ===========================================

"""
Cognitive Coordination Protocol (CCP) Main Module
==================================================

This module provides the canonical protocol implementation including:

- Protocol identity management
- Version compatibility checking
- Message validation
- Publication processing
- Subscription matching
- Processing pipeline

This is a pure semantic layer. It does NOT handle transport.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# CCP PROTOCOL - Main protocol specification and processing
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPProtocol:
    """
    Canonical immutable protocol specification.
    
    PROTOCOL-LAW-001: Protocol has one stable semantic identity
    PROTOCOL-LAW-002: Protocol is independent from runtime implementation
    PROTOCOL-LAW-003: Protocol version compatibility is explicit
    """
    identity: str = ""
    """Protocol identity string."""
    
    version: Optional[str] = None
    """Protocol version string (e.g., '1.0.0')."""
    
    supported_message_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Message kinds this protocol supports."""
    
    supported_payload_kinds: tuple[str, ...] = field(default_factory=tuple)
    """Payload kinds this protocol supports."""
    
    compatibility_policy: str = "strict"
    """Compatibility policy (strict, flexible, etc.)."""
    
    publication_policy: str = "explicit_validation"
    """Publication validation policy."""
    
    subscription_policy: str = "declarative_matching"
    """Subscription matching policy."""
    
    acknowledgement_policy: str = "distinct_from_acceptance"
    """Acknowledgement semantics policy."""
    
    negotiation_policy: str = "declarative_selection"
    """Negotiation policy."""
    
    synchronization_policy: str = "semantic_barrier"
    """Synchronization policy."""
    
    recovery_policy: str = "declarative_proposal"
    """Recovery policy."""
    
    validation_policy: str = "deep_validation"
    """Validation depth policy."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Protocol findings (e.g., deprecated features)."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Known protocol limitations."""
    
    provenance: str = ""
    """Protocol specification provenance."""
    
    @property
    def is_active(self) -> bool:
        """Check if this protocol version is active."""
        return self.version is not None and len(self.version) > 0
    
    @classmethod
    def v1_0(cls) -> CCPProtocol:
        """Create CCP v1.0 protocol specification."""
        return cls(
            identity="gordon_ccp:v1.0.0",
            version="1.0.0",
            supported_message_kinds=tuple(kind.value for kind in [
                # TODO: Enum iteration - currently using string literals
                "projection_publication",  # CCPMessageKind.PROJECTION_PUBLICATION.value,
                "state_publication",
                "capability_advertisement",
                "requirement_declaration",
                "subscription_declaration",
                "acknowledgement",
                "acceptance",
                "rejection",
                "deferral",
            ]),
            supported_payload_kinds=tuple(kind.value for kind in [
                # TODO: Enum iteration
                "network_projection",
                "coordination_state",
                "capability_advertisement",
                "requirement_declaration",
                "subscription_declaration",
                "negotiation_request",
                "synchronization_request",
                "transition_intention",
            ]),
            compatibility_policy="strict",
            publication_policy="explicit_validation",
            subscription_policy="declarative_matching",
            acknowledgement_policy="distinct_from_acceptance",
            negotiation_policy="declarative_selection",
            synchronization_policy="semantic_barrier",
            recovery_policy="declarative_proposal",
            validation_policy="deep_validation",
            findings=(),
            limitations=(),
            provenance="gordon_cognitive_architecture_ccp_v1.0",
        )


# =============================================================================
# CCP PROCESSING REQUEST - Protocol processing input
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPProcessingRequest:
    """
    Immutable protocol processing request.
    
    PROCESSING-LAW-001: Processing validates before classification
    PROCESSING-LAW-002: Processing is side-effect free
    PROCESSING-LAW-003: Processing never invokes cognitive networks
    """
    protocol: Optional[CCPProtocol] = None
    """Protocol specification for processing."""
    
    publication: Optional[str] = None  # CCPPublication reference as string
    """ Publication to process (reference)."""
    
    active_subscriptions: tuple[str, ...] = field(default_factory=tuple)
    """Active subscription references for matching."""
    
    coordination_context: str = ""
    """Coordination context for processing (cycle identity, etc.)."""
    
    compatibility_policy: str = "strict"
    """Compatibility policy override."""
    
    processing_policy: str = "full_validation"
    """Processing depth policy."""
    
    semantic_time: Optional[str] = None
    """Semantic time reference for this processing."""
    
    provenance: str = ""
    """Processing request provenance."""
    
    @property
    def has_publication(self) -> bool:
        """Check if a publication is present."""
        return self.publication is not None
    
    @classmethod
    def create(
        cls,
        protocol: CCPProtocol,
        publication_ref: str,
        coordination_context: str = "",
    ) -> CCPProcessingRequest:
        """Create a processing request."""
        return cls(
            protocol=protocol,
            publication=publication_ref,
            active_subscriptions=(),
            coordination_context=coordination_context,
            compatibility_policy="strict",
            processing_policy="full_validation",
            provenance=f"processing_request:{publication_ref}",
        )


# =============================================================================
# CCP PROCESSING RESULT - Protocol processing output
# =============================================================================

@dataclass(frozen=True, slots=True)
class CCPProcessingResult:
    """
    Immutable protocol processing result.
    
    PROCESSING-LAW-007: Processing results are immutable
    PROCESSING-LAW-008: Processing is deterministic
    """
    request_reference: Optional[str] = None
    """Reference to original processing request."""
    
    validated_publication: Optional[str] = None
    """Validated publication reference (if any)."""
    
    compatibility: str = ""
    """Compatibility status result."""
    
    subscription_matches: tuple[str, ...] = field(default_factory=tuple)
    """Matched subscription references."""
    
    generated_acknowledgements: tuple[str, ...] = field(default_factory=tuple)
    """Generated acknowledgement references."""
    
    correlation_updates: tuple[str, ...] = field(default_factory=tuple)
    """Correlation state updates."""
    
    negotiation_updates: tuple[str, ...] = field(default_factory=tuple)
    """Negotiation state updates."""
    
    synchronization_updates: tuple[str, ...] = field(default_factory=tuple)
    """Synchronization state updates."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Protocol findings during processing."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Protocol limitations encountered."""
    
    trace: tuple[str, ...] = field(default_factory=tuple)
    """Processing trace events."""
    
    status: str = ""
    """Final processing status."""
    
    provenance: str = ""
    """Result provenance."""


# =============================================================================
# CCP MESSAGE VALIDATOR - Message validation interface
# =============================================================================

class CCPMessageValidator:
    """
    Immutable message validator.
    
    Validates messages against protocol rules without modifying them.
    """
    
    @staticmethod
    def validate_identity(identity: str) -> tuple[bool, Optional[str]]:
        """
        Validate message identity format.
        
        Returns:
            Tuple of (valid, error_message)
        """
        if not identity or len(identity) == 0:
            return False, "Identity cannot be empty"
        # Identity validation rules can be extended
        return True, None
    
    @staticmethod
    def validate_version(version: str) -> tuple[bool, Optional[str]]:
        """Validate protocol version format."""
        if not version:
            return False, "Version cannot be empty"
        # Version format validation (e.g., semver)
        parts = version.split(".")
        if len(parts) != 3:
            return False, "Version must be in format major.minor.patch"
        try:
            int(parts[0])
            int(parts[1])
            int(parts[2])
        except ValueError:
            return False, "Version components must be integers"
        return True, None
    
    @staticmethod
    def validate_confidence(confidence: float) -> tuple[bool, Optional[str]]:
        """Validate confidence value range."""
        if not isinstance(confidence, (int, float)):
            return False, "Confidence must be numeric"
        if confidence < 0.0 or confidence > 1.0:
            return False, "Confidence must be between 0.0 and 1.0"
        return True, None
    
    @staticmethod
    def validate_uncertainty(uncertainty: float) -> tuple[bool, Optional[str]]:
        """Validate uncertainty value range."""
        if not isinstance(uncertainty, (int, float)):
            return False, "Uncertainty must be numeric"
        if uncertainty < 0.0 or uncertainty > 1.0:
            return False, "Uncertainty must be between 0.0 and 1.0"
        return True, None


# =============================================================================
# CCP PUBLICATION VALIDATOR - Publication validation interface
# =============================================================================

class CCPPublicationValidator:
    """
    Immutable publication validator.
    
    Validates publications against protocol rules.
    """
    
    @staticmethod
    def validate_status(status: str) -> tuple[bool, Optional[str]]:
        """Validate publication status."""
        valid_statuses = (
            "created", "submitted", "validating",
            "published", "published_with_limitations",
            "withheld", "rejected", "deferred",
            "superseded", "withdrawn", "invalid"
        )
        if status not in valid_statuses:
            return False, f"Invalid publication status: {status}"
        return True, None
    
    @staticmethod
    def validate_visibility_scope(scope: str) -> tuple[bool, Optional[str]]:
        """Validate visibility scope."""
        valid_scopes = (
            "private_to_coordination", "targeted_networks",
            "domain_scoped", "core_networks",
            "observers", "global_coordination", "archival"
        )
        if scope not in valid_scopes:
            return False, f"Invalid visibility scope: {scope}"
        return True, None


# =============================================================================
# CCP SUBSCRIPTION MATCHER - Subscription matching engine
# =============================================================================

class CCPSubscriptionMatcher:
    """
    Immutable subscription matcher.
    
    Matches publications against subscriptions deterministically.
    """
    
    @staticmethod
    def match_kind(
        publication_kind: str,
        subscription_kinds: tuple[str, ...],
    ) -> bool:
        """Check if publication kind matches subscription kinds."""
        return publication_kind in subscription_kinds
    
    @staticmethod
    def match_payload(
        publication_payload: str,
        subscription_payloads: tuple[str, ...],
    ) -> bool:
        """Check if publication payload matches subscription payloads."""
        return publication_payload in subscription_payloads
    
    @staticmethod
    def match_version(
        publication_version: str,
        subscription_versions: tuple[str, ...],
    ) -> bool:
        """Check if publication version is compatible with subscription."""
        return publication_version in subscription_versions
    
    @classmethod
    def matches_all(cls, pub_kind: str, pub_payload: str, pub_version: str,
                    sub_kinds: tuple[str, ...], sub_payloads: tuple[str, ...],
                    sub_versions: tuple[str, ...]) -> bool:
        """Check if publication matches all subscription criteria."""
        return (
            cls.match_kind(pub_kind, sub_kinds) and
            cls.match_payload(pub_payload, sub_payloads) and
            cls.match_version(pub_version, sub_versions)
        )


# =============================================================================
# CCP COMPATIBILITY CHECKER - Protocol compatibility evaluation
# =============================================================================

class CCPCompatibilityChecker:
    """
    Immutable compatibility checker.
    
    Evaluates protocol version compatibility deterministically.
    """
    
    @staticmethod
    def check_major_version_match(
        publisher_version: str,
        consumer_version: str,
    ) -> bool:
        """Check if major versions match."""
        pub_parts = publisher_version.split(".")
        cons_parts = consumer_version.split(".")
        
        if len(pub_parts) < 1 or len(cons_parts) < 1:
            return False
        
        return pub_parts[0] == cons_parts[0]
    
    @classmethod
    def check_compatibility(cls, pub_ver: str, cons_ver: str) -> str:
        """
        Check full compatibility between versions.
        
        Returns:
            Compatibility status string
        """
        if not cls.check_major_version_match(pub_ver, cons_ver):
            return "incompatible"
        
        pub_parts = pub_ver.split(".")
        cons_parts = cons_ver.split(".")
        
        # Same major version implies backward compatibility for minor/patch
        if len(pub_parts) >= 2 and len(cons_parts) >= 2:
            pub_minor = int(pub_parts[1])
            cons_minor = int(cons_parts[1])
            
            if pub_minor <= cons_minor:
                return "fully_compatible"
            else:
                return "forward_compatible"
        
        return "fully_compatible"
