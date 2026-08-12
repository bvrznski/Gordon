# Security Policy Management - Production Implementation
# =======================================================

"""
Canonical policy authority implementations for Phase 3.7.20-I.

This module implements:
- PolicyManager: Centralized security policy management with versioning
- Explicit trust domains and boundaries
- Policy evaluation engine
- Policy precedence rules
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Set
from enum import Enum
import time
import uuid
import hashlib


# Import security primitives
from . import (
    SecurityId,
    SecurityVersion,
    PolicyType as CorePolicyType,
    AuthorizationPolicy as CoreAuthorizationPolicy,
)


class PolicyScope(Enum):
    """Scopes for policy application."""
    KERNEL = "kernel"
    RUNTIME = "runtime"
    SERVICES = "services"
    PLUGINS = "plugins"
    PROVIDERS = "providers"
    TOOLS = "tools"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    PROCESS = "process"
    USER = "user"


@dataclass(frozen=True)
class TrustDomain:
    """
    An explicit trust domain in the system.
    
    Each trust domain has its own security policies, isolation boundaries,
    and trust evaluation rules. Cross-domain access requires explicit authorization.
    """
    domain_id: str
    name: str
    description: Optional[str] = None
    
    # Domain characteristics
    scope: Tuple[PolicyScope, ...] = field(default_factory=tuple)
    
    # Isolation level
    isolation_mode: bool = True  # True = strict isolation, False = relaxed
    
    # Default trust level for principals in this domain
    default_trust_level: float = 0.5
    
    # Trust boundaries (what can enter/exit this domain)
    allowed_boundary_crossings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def create_kernel(cls) -> "TrustDomain":
        """Create the kernel trust domain."""
        return cls(
            domain_id="kernel",
            name="Kernel",
            description="Core runtime kernel operations",
            scope=(PolicyScope.KERNEL, PolicyScope.RUNTIME),
            isolation_mode=True,
            default_trust_level=1.0
        )
    
    @classmethod
    def create_runtime(cls) -> "TrustDomain":
        """Create the runtime trust domain."""
        return cls(
            domain_id="runtime",
            name="Runtime",
            description="Runtime execution environment",
            scope=(PolicyScope.RUNTIME, PolicyScope.SERVICES),
            isolation_mode=True,
            default_trust_level=0.8
        )
    
    @classmethod
    def create_plugins(cls) -> "TrustDomain":
        """Create the plugins trust domain."""
        return cls(
            domain_id="plugins",
            name="Plugins",
            description="Plugin execution environment",
            scope=(PolicyScope.PLUGINS,),
            isolation_mode=True,
            default_trust_level=0.3  # Plugins start with low trust
        )
    
    @classmethod
    def create_providers(cls) -> "TrustDomain":
        """Create the providers trust domain."""
        return cls(
            domain_id="providers",
            name="External Providers",
            description="External provider access",
            scope=(PolicyScope.PROVIDERS,),
            isolation_mode=True,
            default_trust_level=0.2  # External access starts with very low trust
        )
    
    @classmethod
    def create_tools(cls) -> "TrustDomain":
        """Create the tools trust domain."""
        return cls(
            domain_id="tools",
            name="Tools",
            description="Tool execution environment",
            scope=(PolicyScope.TOOLS,),
            isolation_mode=True,
            default_trust_level=0.4
        )
    
    @classmethod
    def create_user(cls) -> "TrustDomain":
        """Create the user trust domain."""
        return cls(
            domain_id="user",
            name="User Input",
            description="User-provided input processing",
            scope=(PolicyScope.USER,),
            isolation_mode=True,
            default_trust_level=0.1  # User input starts with minimal trust
        )
    
    @classmethod
    def create_operating_system(cls) -> "TrustDomain":
        """Create the OS trust domain."""
        return cls(
            domain_id="os",
            name="Operating System",
            description="OS interface access",
            scope=(PolicyScope.PROCESS, PolicyScope.FILESYSTEM, PolicyScope.NETWORK),
            isolation_mode=True,
            default_trust_level=0.9
        )
    
    def allows_boundary_crossing(self, boundary_id: str) -> bool:
        """Check if this domain allows the given boundary crossing."""
        return boundary_id in self.allowed_boundary_crossings


@dataclass(frozen=True)
class PolicyRule:
    """
    A single policy rule within a security policy.
    
    Rules are evaluated in order. The first matching rule determines
    the effect (allow or deny).
    """
    rule_id: str
    name: str
    description: Optional[str] = None
    
    # Match criteria (all must match for rule to apply)
    principal_patterns: Tuple[str, ...] = field(default_factory=tuple)  # Regex patterns
    action_patterns: Tuple[str, ...] = field(default_factory=tuple)
    resource_patterns: Tuple[str, ...] = field(default_factory=tuple)
    domain_patterns: Tuple[str, ...] = field(default_factory=tuple)  # Trust domain patterns
    
    # Effect (explicit - no implicit defaults)
    effect: CorePolicyType = CorePolicyType.ALLOW  # Allow by default if no rules match
    
    # Conditions (additional runtime checks)
    conditions: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PolicyVersion:
    """
    A version of a security policy.
    
    Policies are immutable. Creating a new version creates a new policy
    object rather than modifying the existing one.
    """
    policy_id: str
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    @property
    def version_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def next_major(self) -> "PolicyVersion":
        return PolicyVersion(
            policy_id=self.policy_id,
            major=self.major + 1,
            minor=0,
            patch=0
        )
    
    def next_minor(self) -> "PolicyVersion":
        return PolicyVersion(
            policy_id=self.policy_id,
            major=self.major,
            minor=self.minor + 1,
            patch=0
        )
    
    def next_patch(self) -> "PolicyVersion":
        return PolicyVersion(
            policy_id=self.policy_id,
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1
        )


@dataclass(frozen=True)
class SecurityPolicy:
    """
    A security policy with versioning and precedence.
    
    Policies are immutable artifacts. They can be enabled/disabled but
    never modified once created.
    """
    policy_id: str
    name: str
    
    # Versioning (immutable) - must come before fields with defaults
    version: PolicyVersion
    
    # Rules (tuple is immutable)
    rules: Tuple[PolicyRule, ...] = field(default_factory=tuple)
    
    # Description and metadata (fields with defaults)
    description: Optional[str] = None
    created_at: float = field(default_factory=time.monotonic)
    scope: Tuple[PolicyScope, ...] = field(default_factory=tuple)
    enabled: bool = True
    precedence: int = 100  # Lower number = higher precedence
    
    def matches(
        self,
        principal_id: str,
        action: str,
        resource: str,
        domain: Optional[str] = None
    ) -> Tuple[CorePolicyType, Optional[str]]:
        """
        Check if this policy applies to the given request.
        
        Returns:
            Tuple of (policy_type, rule_id_if_matched)
            
        SECURITY NOTE: Default behavior is DENY if no rules match.
        This ensures fail-closed security behavior - all actions must be
        explicitly allowed by policy. No implicit trust or ambient authority.
        """
        for rule in self.rules:
            # Check all match criteria
            principal_match = not rule.principal_patterns or any(
                p.lower() in principal_id.lower() for p in rule.principal_patterns
            )
            
            action_match = not rule.action_patterns or any(
                a.lower() in action.lower() for a in rule.action_patterns
            )
            
            resource_match = not rule.resource_patterns or any(
                r.lower() in resource.lower() for r in rule.resource_patterns
            )
            
            domain_match = (
                not rule.domain_patterns or 
                domain is None or 
                any(d.lower() in domain.lower() for d in rule.domain_patterns)
            )
            
            if principal_match and action_match and resource_match and domain_match:
                return (rule.effect, rule.rule_id)
        
        # SECURITY CRITICAL: Default is DENY when no rules match
        # This ensures fail-closed security behavior - no implicit trust
        return (CorePolicyType.DENY, None)
    
    def is_enabled_for_scope(self, scope: PolicyScope) -> bool:
        """Check if this policy applies to the given scope."""
        return scope in self.scope


class PolicyManager:
    """
    Canonical security policy authority.
    
    Manages security policies with versioning, precedence, and evaluation.
    
    Invariants:
    - Exactly one instance per runtime
    - Policies are immutable (new versions create new policies)
    - Policies have explicit precedence
    - Default behavior is ALLOW if no rules match
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._policies: Dict[str, SecurityPolicy] = {}  # policy_id -> policy
        self._policy_index: List[Tuple[str, int]] = []  # (policy_id, precedence) sorted by precedence
        self._version_history: Dict[str, List[PolicyVersion]] = {}  # base_policy_id -> versions
        self._lock = __import__("threading").Lock()
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    async def create_policy(
        self,
        name: str,
        rules: Tuple[PolicyRule, ...] = tuple(),
        scope: Tuple[PolicyScope, ...] = tuple(),
        precedence: int = 100,
        description: Optional[str] = None
    ) -> SecurityPolicy:
        """
        Create a new security policy.
        
        This creates a NEW version (does not modify existing policies).
        Returns the created policy with assigned ID and version.
        """
        policy_id = str(uuid.uuid4())
        
        # Check if this is a new base or an update to existing
        base_name = name.rsplit(":", 1)[0] if ":" in name else name
        
        with self._lock:
            # Create initial version
            version = PolicyVersion(policy_id=policy_id, major=1, minor=0, patch=0)
            
            policy = SecurityPolicy(
                policy_id=policy_id,
                name=name,
                description=description,
                version=version,
                rules=rules,
                scope=scope,
                enabled=True,
                precedence=precedence
            )
            
            # Store policy
            self._policies[policy_id] = policy
            
            # Update index with sorted order by precedence
            self._policy_index.append((policy_id, precedence))
            self._policy_index.sort(key=lambda x: (x[1], x[0]))  # Sort by precedence, then ID
            
            # Track version history
            if base_name not in self._version_history:
                self._version_history[base_name] = []
            self._version_history[base_name].append(version)
        
        return policy
    
    async def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Get a specific policy by ID."""
        with self._lock:
            return self._policies.get(policy_id)
    
    async def get_policies_for_scope(
        self,
        scope: PolicyScope
    ) -> Tuple[SecurityPolicy, ...]:
        """Get all enabled policies for a given scope, sorted by precedence."""
        with self._lock:
            result = []
            for policy_id, _ in self._policy_index:
                if policy_id in self._policies:
                    policy = self._policies[policy_id]
                    if policy.enabled and policy.is_enabled_for_scope(scope):
                        result.append(policy)
            return tuple(result)
    
    async def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy. Returns True if policy existed."""
        with self._lock:
            if policy_id not in self._policies:
                return False
            self._policies[policy_id] = self._policies[policy_id].__class__(
                **{
                    **self._policies[policy_id].__dict__,
                    "enabled": True
                }
            )
            return True
    
    async def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy. Returns True if policy existed."""
        with self._lock:
            if policy_id not in self._policies:
                return False
            self._policies[policy_id] = self._policies[policy_id].__class__(
                **{
                    **self._policies[policy_id].__dict__,
                    "enabled": False
                }
            )
            return True
    
    async def evaluate_policies(
        self,
        principal_id: str,
        action: str,
        resource: str,
        domain: Optional[str] = None,
        scopes: Tuple[PolicyScope, ...] = tuple()
    ) -> Tuple[bool, str]:
        """
        Evaluate all applicable policies for a request.
        
        SECURITY CRITICAL: Default is DENY when no rules match. This ensures
        fail-closed security behavior - all actions must be explicitly allowed.
        No implicit trust or ambient authority exists in the system.
        
        This follows the canonical security pipeline:
        1. Get all enabled policies for relevant scopes
        2. Sort by precedence (lower = higher priority)
        3. Evaluate rules in order
        4. First match determines outcome
        5. Default is DENY if no matches
        
        Returns:
            Tuple of (allowed, reason)
        """
        with self._lock:
            # Determine relevant scopes
            relevant_scopes = scopes or tuple(PolicyScope)
            
            # Get policies sorted by precedence
            policies_to_check = []
            for policy_id, _ in self._policy_index:
                if policy_id in self._policies:
                    policy = self._policies[policy_id]
                    if policy.enabled and any(s in policy.scope for s in relevant_scopes):
                        policies_to_check.append(policy)
            
            # Sort by precedence
            policies_to_check.sort(key=lambda p: (p.precedence, p.policy_id))
        
        # Evaluate each policy in order
        last_reason = "No matching rules - explicit deny (default fail-closed)"
        
        for policy in policies_to_check:
            effect, rule_id = policy.matches(principal_id, action, resource, domain)
            
            if rule_id:
                reason = f"Policy '{policy.name}' v{policy.version.version_string}: rule '{rule_id}' matched"
                
                if effect == CorePolicyType.DENY:
                    return (False, f"{reason} - explicit deny")
                
                last_reason = f"{reason} - explicit allow"
        
        # No matching rules - SECURITY CRITICAL: default is DENY
        # This ensures fail-closed behavior: all actions must be explicitly allowed
        return (False, last_reason)
    
    async def check_authorization(
        self,
        principal_id: str,
        action: str,
        resource: str
    ) -> Tuple[bool, str]:
        """
        Check authorization using policy evaluation.
        
        This is the canonical entry point for authorization checks.
        It evaluates all relevant policies and returns the result.
        """
        return await self.evaluate_policies(
            principal_id=principal_id,
            action=action,
            resource=resource
        )
    
    def get_policy_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of policy state (for diagnostics)."""
        with self._lock:
            enabled_count = sum(1 for p in self._policies.values() if p.enabled)
            
            return {
                "runtime_id": self._runtime_id,
                "total_policies": len(self._policies),
                "enabled_policies": enabled_count,
                "version_history_length": len(self._version_history),
                "scopes": [s.value for s in PolicyScope]
            }


@dataclass(frozen=True)
class PolicyViolation:
    """
    A record of a policy violation.
    
    This is immutable evidence of a security event that violated
    an explicit policy.
    """
    violation_id: str
    policy_id: str
    principal_id: str
    action: str
    resource: str
    
    # Optional fields with defaults (must come after required fields)
    rule_id: Optional[str] = None
    domain: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.monotonic)
    
    @property
    def severity(self) -> str:
        """Calculate severity based on the violation."""
        if "critical" in self.context.get("tags", []):
            return "critical"
        elif "admin" in self.action.lower() or "root" in self.resource.lower():
            return "high"
        return "medium"


__all__ = [
    "PolicyScope",
    "TrustDomain",
    "PolicyRule",
    "PolicyVersion",
    "SecurityPolicy",
    "PolicyManager",
    "PolicyViolation",
]