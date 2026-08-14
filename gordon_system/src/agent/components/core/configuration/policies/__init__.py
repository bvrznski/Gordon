# Canonical Policy Architecture - Phase 3.18
# ==========================================
"""
Policy foundation for the Gordon Core.

This module establishes one canonical policy architecture that governs:

* Policy Identity & Authority
* Policy Scope & Applicability  
* Policy Resolution & Conflict Handling
* Policy Evaluation & Enforcement

Architectural Principles:
-------------------------
1. Policies are DECLUSIVE - they never execute runtime work
2. Policies are DECLARATIVE - they describe constraints, not implementations
3. Policies are CANONICAL - one policy per responsibility domain
4. Policies are IMMUTABLE after publication
5. Policies are DETERMINISTIC in evaluation

Policies govern:
- What configuration is allowed
- How runtime behavior is constrained
- Which capabilities may be activated
- When and where operations may execute

The Policy Architecture is orthogonal to the Configuration Architecture:

┌─────────────────────────────────────────────────────────────┐
│                    Policy Layer                             │
│  (Constraints, Rules, Authority)                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Configuration Layer                            │
│  (Values, Structure, Schema)                                │
└─────────────────────────────────────────────────────────────┘

Policy Authority Hierarchy:
---------------------------
1. Global Policies (system-wide constraints)
2. Subsystem Policies (domain-specific rules)
3. Component Policies (specific behavior controls)
4. Profile Policies (operational mode adjustments)

No Policy Conflict Shall Remain Ambiguous:
- All conflicts must be detectable
- All conflicts must have determinate resolution
- All conflict resolutions must be traceable

Phase 3.18.9 — Policy Foundations
Phase 3.18.10 — Policy Identity, Scope & Authority  
Phase 3.18.11 — Policy Resolution & Conflict Handling
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
from enum import Enum
import time


# =============================================================================
# Policy Identity & Versioning
# =============================================================================

@dataclass(frozen=True)
class PolicyId:
    """Unique identifier for a policy."""
    value: str
    
    @classmethod
    def generate(cls) -> "PolicyId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "PolicyId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PolicyVersion:
    """Version of a policy artifact."""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def next_major(self) -> "PolicyVersion":
        return PolicyVersion(major=self.major + 1, minor=0, patch=0)
    
    def next_minor(self) -> "PolicyVersion":
        return PolicyVersion(major=self.major, minor=self.minor + 1, patch=0)
    
    def next_patch(self) -> "PolicyVersion":
        return PolicyVersion(major=self.major, minor=self.minor, patch=self.patch + 1)


@dataclass(frozen=True)
class PolicyGenerationId:
    """Unique identifier for a policy generation (snapshot)."""
    value: str
    
    @classmethod
    def generate(cls) -> "PolicyGenerationId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "PolicyGenerationId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Policy Authority & Scope
# =============================================================================

class PolicyAuthority(Enum):
    """Authority levels for policy application."""
    SYSTEM = "system"           # System-wide policies (highest priority)
    SUBSYSTEM = "subsystem"     # Subsystem-specific policies
    COMPONENT = "component"     # Component-specific policies
    PROFILE = "profile"         # Operational profile policies


class PolicyScope(Enum):
    """Scopes of policy applicability."""
    GLOBAL = "global"
    NAMESPACE = "namespace"
    RUNTIME = "runtime"
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    OPERATION = "operation"


@dataclass(frozen=True)
class PolicyOwner:
    """Owner of a policy artifact."""
    team: str
    contact: Optional[str] = None
    created_at: float = field(default_factory=time.monotonic)


# =============================================================================
# Policy Structure & Content
# =============================================================================

@dataclass(frozen=True)
class PolicyConstraint:
    """
    A declarative constraint expressed by a policy.
    
    Constraints are NEVER executable code. They are machine-readable
    statements that can be evaluated or verified.
    """
    constraint_type: str  # e.g., "allow", "deny", "require", "forbid"
    target: str           # What the constraint applies to (component, capability, etc.)
    condition: Dict[str, Any]  # Machine-readable condition
    description: Optional[str] = None


@dataclass(frozen=True)
class PolicyRule:
    """
    A rule within a policy.
    
    Rules define:
    - When the policy applies
    - What is allowed/denied/required
    - The scope of application
    """
    rule_id: str
    priority: int  # Higher = higher priority
    condition: Dict[str, Any]
    effect: PolicyConstraint
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDocument:
    """
    A complete policy document with multiple rules.
    
    Policy Documents are immutable after publication.
    Each document represents one coherent set of constraints.
    """
    policy_id: PolicyId
    version: PolicyVersion
    
    # Identity & provenance
    namespace: str
    authority: PolicyAuthority
    scope: PolicyScope
    
    # Content
    rules: Tuple[PolicyRule, ...]
    
    # Lifecycle metadata
    owner: Optional[PolicyOwner] = None
    created_at: float = field(default_factory=time.monotonic)
    effective_from: Optional[float] = None  # When policy becomes active
    expires_at: Optional[float] = None      # When policy expires
    
    # Activation rules
    activation_conditions: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Policy Resolution & Conflict Handling
# =============================================================================

class PrecedenceMode(Enum):
    """How conflicts are resolved when policies overlap."""
    DENY_OVERRODES_ALLOW = "deny_overrides_allow"
    ALLOW_OVERRODES_DENY = "allow_overrides_deny"
    HIGHEST_PRECEDENCE = "highest_precedence"
    SPECIFIC_OVER_GENERAL = "specific_over_general"


@dataclass(frozen=True)
class PolicyConflict:
    """
    A detected conflict between policies.
    
    All conflicts must be detectable and resolvable deterministically.
    """
    conflict_id: str
    conflicting_policies: Tuple[PolicyId, ...]
    conflict_type: str  # "incompatible", "overlapping", "contradictory"
    affected_targets: Tuple[str, ...]
    resolution_suggestion: Optional[str] = None


@dataclass(frozen=True)
class PolicyResolution:
    """
    The result of policy resolution.
    
    Contains:
    - Effective policies (after precedence application)
    - Conflicts detected
    - Resolutions applied
    """
    effective_policies: Tuple[PolicyDocument, ...]
    conflicts: Tuple[PolicyConflict, ...] = field(default_factory=tuple)
    resolutions_applied: Dict[str, str] = field(default_factory=dict)  # target -> resolution


# =============================================================================
# Policy Evaluation
# =============================================================================

class PolicyEvaluationResult(Enum):
    """Result of policy evaluation."""
    ALLOWED = "allowed"
    DENIED = "denied"
    CONDITIONAL = "conditional"  # May be allowed with conditions
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PolicyEvaluation:
    """
    The result of evaluating policies against a target.
    
    This is NOT executable - it's a diagnostic report showing which
    policies applied and what their collective effect is.
    """
    evaluation_id: str
    target: str  # What was evaluated (component, capability, etc.)
    effective_policies: Tuple[PolicyDocument, ...]
    constraints_applied: Tuple[PolicyConstraint, ...]
    result: PolicyEvaluationResult
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Operational Profiles
# =============================================================================

class OperationalProfile(Enum):
    """Operational runtime profiles."""
    SAFE_MODE = "safe_mode"           # Minimal capabilities, safety-first
    RECOVERY_MODE = "recovery_mode"   # Recovery-focused operations
    MAINTENANCE_MODE = "maintenance_mode"  # Maintenance operations only
    OFFLINE_MODE = "offline_mode"     # No external connections
    EMERGENCY_MODE = "emergency_mode"  # Critical path only
    MINIMAL_MODE = "minimal_mode"     # Bare minimum functionality
    SIMULATION_MODE = "simulation_mode"  # Simulated execution
    BENCHMARK_MODE = "benchmark_mode"   # Performance testing
    DEBUG_MODE = "debug_mode"         # Full diagnostics enabled
    DEVELOPMENT_MODE = "development_mode"  # Development-friendly settings
    PRODUCTION_MODE = "production_mode"    # Production constraints


@dataclass(frozen=True)
class ProfilePolicies:
    """
    Policies specific to an operational profile.
    
    Each profile defines which capabilities are enabled/disabled,
    what configuration changes are allowed, and other profile-specific rules.
    """
    profile: OperationalProfile
    enabled_capabilities: Tuple[str, ...]
    disabled_capabilities: Tuple[str, ...]
    allowed_configuration_changes: Tuple[str, ...]
    forbidden_configuration_changes: Tuple[str, ...]
    
    # Profile behavior adjustments
    scheduling_behavior: Dict[str, Any] = field(default_factory=dict)
    execution_restrictions: Dict[str, Any] = field(default_factory=dict)
    recovery_strategy: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    # Identity & Versioning
    "PolicyId",
    "PolicyVersion",
    "PolicyGenerationId",
    
    # Authority & Scope
    "PolicyAuthority",
    "PolicyScope",
    "PolicyOwner",
    
    # Policy Structure
    "PolicyConstraint",
    "PolicyRule",
    "PolicyDocument",
    
    # Resolution
    "PrecedenceMode",
    "PolicyConflict",
    "PolicyResolution",
    
    # Evaluation
    "PolicyEvaluationResult",
    "PolicyEvaluation",
    
    # Profiles
    "OperationalProfile",
    "ProfilePolicies",
]