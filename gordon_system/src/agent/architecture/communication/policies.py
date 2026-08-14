# Gordon Core - Communication Policies (Phase 3.21.11)
# ======================================================
#
# Canonical communication policies for authorization, routing, and security
#
# Policies define rules for who can communicate with whom, how, and under
# what conditions.

"""
Canonical Communication Policies for Gordon Phase 3.21.11

POLICY CATEGORIES:
------------------
1. Authorization: Who is allowed to send/receive messages
2. Visibility: What endpoints can see each other
3. Routing: How messages are routed between endpoints
4. Rate Limiting: How many messages per time period
5. Encryption: Message encryption requirements

POLICY TYPES:
-------------
- AuthorizationRule: Determines if operation is permitted
- VisibilityRule: Controls endpoint discoverability
- RoutingRestriction: Constrains routing paths
- RateLimitConfig: Throttles message rate
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum, auto
import time


# =============================================================================
# AUTHORIZATION RULES
# =============================================================================

class AuthorizationType(Enum):
    """
    Canonical authorization rule types.
    """
    
    ALLOW = "allow"       # Explicitly permit the operation
    DENY = "deny"         # Explicitly forbid the operation
    CONDITIONAL = "conditional"  # Permit based on conditions


@dataclass(frozen=True)
class AuthorizationRule:
    """
    Immutable authorization rule.
    
    Args:
        rule_id: Unique identifier for this rule
        source_endpoint_type: Type of sender (None = all)
        target_endpoint_type: Type of receiver (None = all)
        action: Action being authorized (send, receive, subscribe, etc.)
        condition: Optional additional conditions that must be met
        auth_type: Whether this is an allow or deny rule
    """
    
    rule_id: str
    source_endpoint_type: Optional[str] = None
    target_endpoint_type: Optional[str] = None
    action: str = "send"
    condition: Dict[str, Any] = field(default_factory=dict)
    auth_type: AuthorizationType = AuthorizationType.ALLOW
    
    def matches(
        self,
        source_type: str,
        target_type: str,
        action: str,
    ) -> bool:
        """Check if this rule matches the given context."""
        # Match source type (if specified)
        if self.source_endpoint_type and self.source_endpoint_type != source_type:
            return False
        
        # Match target type (if specified)
        if self.target_endpoint_type and self.target_endpoint_type != target_type:
            return False
        
        # Match action
        if self.action != "any" and self.action != action:
            return False
        
        return True
    
    def is_allowed(
        self,
        source_type: str,
        target_type: str,
        action: str,
    ) -> bool:
        """Check if the operation is allowed by this rule."""
        if not self.matches(source_type, target_type, action):
            return True  # Rule doesn't apply
        
        if self.auth_type == AuthorizationType.DENY:
            return False
        return True


# =============================================================================
# VISIBILITY RULES
# =============================================================================

class VisibilityPolicy(Enum):
    """
    Canonical visibility policy types.
    """
    
    PUBLIC = "public"           # Visible to all endpoints
    PRIVATE = "private"         # Only visible to specific endpoints
    RESTRICTED = "restricted"   # Visible within specific scope


@dataclass(frozen=True)
class VisibilityRule:
    """
    Immutable visibility rule.
    
    Args:
        endpoint_type: Type of endpoint this applies to
        policy: The visibility policy type
        allowed_recipients: List of endpoint IDs that can see this
        disallowed_recipients: List of endpoint IDs explicitly excluded
    """
    
    endpoint_type: str
    policy: VisibilityPolicy = VisibilityPolicy.PUBLIC
    allowed_recipients: Tuple[str, ...] = field(default_factory=tuple)
    disallowed_recipients: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# ROUTING RESTRICTIONS
# =============================================================================

@dataclass(frozen=True)
class RoutingRestriction:
    """
    Immutable routing restriction.
    
    Args:
        restriction_id: Unique identifier
        source_scope: Source endpoint must be in this scope
        target_scope: Target endpoint must be in this scope
        allowed_route_types: Which route types are permitted
        max_hops: Maximum hops allowed (0 = unlimited)
    """
    
    restriction_id: str
    source_scope: Optional[str] = None
    target_scope: Optional[str] = None
    allowed_route_types: Tuple[str, ...] = field(default_factory=tuple)
    max_hops: int = 0


# =============================================================================
# RATE LIMIT CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class RateLimitConfig:
    """
    Immutable rate limit configuration.
    
    Args:
        messages_per_second: Maximum messages per second
        burst_size: Maximum burst size (consecutive messages)
        window_seconds: Sliding window size for averaging
        action_on_exceed: What to do when rate exceeded (drop, queue, error)
    """
    
    messages_per_second: float = 0.0  # 0 = unlimited
    burst_size: int = 10
    window_seconds: float = 1.0
    action_on_exceed: str = "queue"  # drop, queue, error


# =============================================================================
# ENCRYPTION POLICY
# =============================================================================

class EncryptionPolicy(Enum):
    """
    Canonical encryption policy types.
    """
    
    NONE = "none"              # No encryption required
    OPTIONAL = "optional"      # Encryption allowed but not required
    REQUIRED = "required"      # Encryption is mandatory
    ENFORCED = "enforced"      # End-to-end encryption enforced


@dataclass(frozen=True)
class EncryptionPolicyRule:
    """
    Immutable encryption policy rule.
    
    Args:
        policy: The encryption policy type
        algorithm: Required encryption algorithm (if any)
        key_rotation_days: How often keys should be rotated
        minimum_key_strength: Minimum key strength in bits
    """
    
    policy: EncryptionPolicy = EncryptionPolicy.NONE
    algorithm: Optional[str] = None  # e.g., "AES-256-GCM"
    key_rotation_days: int = 30
    minimum_key_strength: int = 128


# =============================================================================
# VALIDATION POLICY
# =============================================================================

class ValidationLevel(Enum):
    """
    Canonical validation level types.
    """
    
    NONE = "none"              # No validation performed
    BASIC = "basic"            # Basic structure validation only
    SCHEMA = "schema"          # Full schema validation
    STRICT = "strict"          # Strict validation with error on any issue


@dataclass(frozen=True)
class ValidationPolicy:
    """
    Immutable validation policy.
    
    Args:
        level: The validation level to apply
        allowed_payload_types: Tuple of permitted payload types (empty = all)
        max_message_size_bytes: Maximum message size (0 = unlimited)
        require_timestamp: Whether timestamp is required
    """
    
    level: ValidationLevel = ValidationLevel.BASIC
    allowed_payload_types: Tuple[str, ...] = field(default_factory=tuple)
    max_message_size_bytes: int = 0  # 0 = unlimited
    require_timestamp: bool = True


# =============================================================================
# COMMUNICATION POLICIES COLLECTION
# =============================================================================

@dataclass(slots=True)
class CommunicationPolicies:
    """
    Mutable collection of all communication policies.
    
    Provides methods to check and enforce policies.
    """
    
    _authorization_rules: Dict[str, AuthorizationRule] = field(
        default_factory=dict
    )
    _visibility_rules: Dict[str, VisibilityRule] = field(default_factory=dict)
    _rate_limits: Dict[str, RateLimitConfig] = field(default_factory=dict)
    _encryption_policies: Dict[str, EncryptionPolicyRule] = field(
        default_factory=dict
    )
    _validation_policy: Optional[ValidationPolicy] = None
    
    def add_authorization_rule(self, rule: AuthorizationRule) -> str:
        """Add an authorization rule and return its ID."""
        self._authorization_rules[rule.rule_id] = rule
        return rule.rule_id
    
    def check_authorization(
        self,
        source_type: str,
        target_type: str,
        action: str,
    ) -> bool:
        """Check if the operation is authorized."""
        # Check for deny rules first
        for rule in self._authorization_rules.values():
            if (
                rule.auth_type == AuthorizationType.DENY and
                rule.matches(source_type, target_type, action)
            ):
                return False
        
        # If no deny rules matched, allow by default (or check allow rules)
        for rule in self._authorization_rules.values():
            if (
                rule.auth_type == AuthorizationType.ALLOW and
                rule.matches(source_type, target_type, action)
            ):
                return True
        
        # No matching rule - allow by default (open policy)
        return True
    
    def get_visibility_rule(self, endpoint_type: str) -> Optional[VisibilityRule]:
        """Get the visibility rule for an endpoint type."""
        return self._visibility_rules.get(endpoint_type)
    
    def set_rate_limit(self, endpoint_type: str, config: RateLimitConfig) -> None:
        """Set rate limit configuration for an endpoint type."""
        self._rate_limits[endpoint_type] = config
    
    def get_rate_limit(self, endpoint_type: str) -> Optional[RateLimitConfig]:
        """Get rate limit configuration for an endpoint type."""
        return self._rate_limits.get(endpoint_type)
    
    def set_encryption_policy(
        self,
        endpoint_type: str,
        policy: EncryptionPolicyRule,
    ) -> None:
        """Set encryption policy for an endpoint type."""
        self._encryption_policies[endpoint_type] = policy
    
    def is_encryption_required(self, endpoint_type: str) -> bool:
        """Check if encryption is required for an endpoint type."""
        rule = self._encryption_policies.get(endpoint_type)
        if rule is None:
            return False
        return rule.policy in (
            EncryptionPolicy.REQUIRED,
            EncryptionPolicy.ENFORCED,
        )
    
    def set_validation_policy(self, policy: ValidationPolicy) -> None:
        """Set the global validation policy."""
        self._validation_policy = policy
    
    def get_validation_policy(self) -> Optional[ValidationPolicy]:
        """Get the current validation policy."""
        return self._validation_policy


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Authorization
    "AuthorizationType",
    "AuthorizationRule",
    
    # Visibility
    "VisibilityPolicy",
    "VisibilityRule",
    
    # Routing
    "RoutingRestriction",
    
    # Rate limiting
    "RateLimitConfig",
    
    # Encryption
    "EncryptionPolicy",
    "EncryptionPolicyRule",
    
    # Validation
    "ValidationLevel",
    "ValidationPolicy",
    
    # Policy collection
    "CommunicationPolicies",
]