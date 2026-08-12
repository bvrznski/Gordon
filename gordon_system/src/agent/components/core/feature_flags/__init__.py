# Core Feature Flags Infrastructure
# ==================================
"""
Feature flag management system.

Provides:
- Flag definitions with targeting rules
- Deterministic evaluation (stable for experiments)
- Kill switches and rollout rules
- Variant assignments

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
)
from enum import Enum
import time


# =============================================================================
# Feature Flag IDs
# =============================================================================

@dataclass(frozen=True)
class FeatureFlagId:
    """Unique identifier for a feature flag."""
    value: str
    
    @classmethod
    def generate(cls) -> "FeatureFlagId":
        import uuid
        return cls(value=str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, s: str) -> "FeatureFlagId":
        return cls(value=s)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# Feature Flag Types
# =============================================================================

class FeatureFlagType(Enum):
    BOOLEAN = "boolean"
    VARIANT = "variant"  # Multiple discrete options
    PERCENTAGE = "percentage"  # Rollout percentage
    TARGETED = "targeted"  # User/tenant specific
    KILL_SWITCH = "kill_switch"


@dataclass(frozen=True)
class FeatureFlagVariant:
    """A variant value for a feature flag."""
    name: str
    value: Any


# =============================================================================
# Feature Flag Definition
# =============================================================================

@dataclass(frozen=True)
class FeatureFlagDefinition:
    """
    A feature flag definition.
    
    Flags should be:
    - Immutable after creation
    - Versioned
    - Have a clear owner and lifecycle
    
    Types:
        BOOLEAN: Simple on/off flag
        VARIANT: Multiple discrete options (A/B/C testing)
        PERCENTAGE: Gradual rollout by percentage
        TARGETED: Enable for specific users/tenants
        KILL_SWITCH: Emergency disable mechanism
    """
    
    flag_id: FeatureFlagId
    name: str
    flag_type: FeatureFlagType
    
    # Default value when flag is not matched
    default_value: Any
    
    # Lifecycle
    owner: Optional[str] = None  # Owner team/org
    lifecycle_stage: str = "development"  # development, preview, GA, deprecated, removed
    
    # Targeting and rollout
    enabled: bool = True
    percentage: int = 100  # For percentage flags (0-100)
    
    # Targeting rules
    tenant_ids: Optional[Tuple[str, ...]] = None  # Specific tenants
    user_segments: Optional[Tuple[str, ...]] = None  # User segment IDs
    
    # Dependencies (other flags this depends on)
    requires_flags: Tuple[FeatureFlagId, ...] = field(default_factory=tuple)
    
    # Metadata
    version: int = 1
    created_at: float = field(default_factory=time.monotonic)
    expires_at: Optional[float] = None
    
    # Technical debt tracking
    deprecation_notice: Optional[str] = None
    removal_version: Optional[int] = None


# =============================================================================
# Feature Flag Context
# =============================================================================

@dataclass(frozen=True)
class FeatureFlagContext:
    """Context for flag evaluation."""
    runtime_id: str
    timestamp: float = field(default_factory=time.monotonic)
    
    # Evaluation context
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    user_segments: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# Feature Flag Decision
# =============================================================================

@dataclass(frozen=True)
class FeatureFlagDecision:
    """Result of feature flag evaluation."""
    flag_id: str
    flag_name: str
    
    enabled: bool  # Is the flag effectively enabled?
    value: Any  # The resolved value (True/False, variant name, etc.)
    
    # How the decision was made
    source: str  # "default", "context_match", "percentage_rollout"
    reason: Optional[str] = None
    
    evaluation_time_ms: float = 0.0


# =============================================================================
# Feature Flag Snapshot
# =============================================================================

@dataclass(frozen=True)
class FeatureFlagSnapshot:
    """
    Snapshot of feature flag state at a point in time.
    
    Used for:
    - Drift detection
    - Rollback support
    - Historical analysis
    """
    
    snapshot_id: str
    runtime_id: str
    effective_config_version: int
    
    # Applied version (if different from effective)
    applied_version: Optional[int] = None
    
    # Flag states
    active_flags: Tuple[str, ...] = field(default_factory=tuple)
    flag_counts: Dict[str, int] = field(default_factory=dict)  # type -> count
    
    created_at: float = field(default_factory=time.monotonic)
    
    def is_current(self) -> bool:
        return self.applied_version is None or self.applied_version == self.effective_config_version


# =============================================================================
# Feature Flag Manager
# =============================================================================

class FeatureFlagManager:
    """
    Manages feature flags for a runtime.
    
    Provides:
    - Flag definition storage and retrieval
    - Deterministic evaluation (stable for experiments)
    - Percentage rollout with stable assignment
    
    Invariants:
    - Deterministic for equivalent context
    - Versioned flag definitions
    - Side-effect-free during evaluation
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._flags: Dict[str, FeatureFlagDefinition] = {}  # id -> definition
        self._lock = __import__("threading").Lock()
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def register_flag(self, flag_def: FeatureFlagDefinition) -> None:
        """Register a feature flag definition."""
        with self._lock:
            self._flags[flag_def.flag_id.value] = flag_def
    
    def get_flag(self, flag_id: str) -> Optional[FeatureFlagDefinition]:
        """Get a registered flag by ID."""
        return self._flags.get(flag_id)
    
    def evaluate(
        self,
        context: FeatureFlagContext,
        flag_id: str
    ) -> FeatureFlagDecision:
        """
        Evaluate a feature flag for given context.
        
        Args:
            context: Evaluation context (runtime, tenant, user, etc.)
            flag_id: ID of the flag to evaluate
            
        Returns:
            Decision with enabled status and value
        """
        start_time = time.monotonic()
        
        with self._lock:
            flag_def = self._flags.get(flag_id)
        
        if not flag_def or not flag_def.enabled:
            return FeatureFlagDecision(
                flag_id=flag_id,
                flag_name=flag_def.name if flag_def else "unknown",
                enabled=False,
                value=None,
                source="disabled_or_not_found",
                reason="Flag is disabled or not found" if flag_def else "Flag not registered"
            )
        
        # Check if tenant/user matches
        matched = False
        reason = None
        
        if flag_def.tenant_ids and context.tenant_id:
            matched = context.tenant_id in flag_def.tenant_ids
            if matched:
                reason = f"Tenant {context.tenant_id} in allowed list"
        
        if not matched and flag_def.user_segments:
            matched = any(seg in flag_def.user_segments for seg in context.user_segments)
            if matched:
                reason = "User in allowed segment"
        
        # Percentage rollout check
        if not matched and flag_def.flag_type == FeatureFlagType.PERCENTAGE:
            # Stable hash-based percentage (deterministic per runtime + context)
            import hashlib
            stable_hash = int(
                hashlib.md5(
                    f"{self._runtime_id}:{context.tenant_id or 'no_tenant'}".encode()
                ).hexdigest(), 16
            )
            percentage = stable_hash % 100
            matched = percentage < flag_def.percentage
            if matched:
                reason = f"Percentage rollout (hash: {percentage} < {flag_def.percentage})"
        
        # Determine final value based on type
        enabled = True
        
        if not matched:
            # Fall back to default
            enabled = False
            reason = "No matching rule, using default"
        
        # For variant flags, return the appropriate value
        if flag_def.flag_type == FeatureFlagType.VARIANT:
            value = None  # Could implement variant selection logic
        else:
            value = enabled
        
        decision_time_ms = (time.monotonic() - start_time) * 1000
        
        return FeatureFlagDecision(
            flag_id=flag_id,
            flag_name=flag_def.name,
            enabled=enabled,
            value=value,
            source="percentage_rollout" if "Percentage rollout" in reason else 
                   ("context_match" if matched else "default"),
            reason=reason,
            evaluation_time_ms=decision_time_ms
        )
    
    def get_all_flags(self) -> Dict[str, FeatureFlagDefinition]:
        """Get all registered flags."""
        with self._lock:
            return dict(self._flags)
    
    def get_flag_count(self) -> int:
        """Return total number of registered flags."""
        with self._lock:
            return len(self._flags)


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # IDs
    "FeatureFlagId",
    
    # Types
    "FeatureFlagType",
    "FeatureFlagVariant",
    
    # Definition
    "FeatureFlagDefinition",
    
    # Context and Decision
    "FeatureFlagContext",
    "FeatureFlagDecision",
    
    # Snapshot
    "FeatureFlagSnapshot",
    
    # Manager
    "FeatureFlagManager",
]