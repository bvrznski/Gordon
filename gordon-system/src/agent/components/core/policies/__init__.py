# Core Policy Infrastructure
# ==========================
"""
Policy evaluation system for configuration and runtime decisions.

Provides:
- Runtime-wide policy authority (single source of truth)
- Rule-based decision making
- Policy precedence and composition
- Conflict detection

Phase 3.7.14: Configuration, Policy, Feature Flags & Runtime Reconfiguration
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
    Callable,
)
from enum import Enum
import time


# =============================================================================
# Policy IDs
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
    """Version of a policy."""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def next_major(self) -> "PolicyVersion":
        return PolicyVersion(major=self.major + 1, minor=0, patch=0)
    
    def next_minor(self) -> "PolicyVersion":
        return PolicyVersion(major=self.major, minor=self.minor + 1, patch=0)
    
    def next_patch(self) -> "PolicyVersion":
        return PolicyVersion(major=self.major, minor=self.minor, patch=self.patch + 1)


# =============================================================================
# Policy Rules
# =============================================================================

class RuleEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class PolicyRule:
    """A single policy rule."""
    rule_id: str
    name: str
    description: Optional[str] = None
    
    # Match criteria
    domain: Optional[str] = None  # e.g., "kernel", "runtime"
    field_path: Optional[str] = None  # e.g., "kernel.timeout"
    
    # Evaluation conditions (functions that return True to match)
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    
    # Effect
    effect: RuleEffect = RuleEffect.ALLOW


# =============================================================================
# Policy Context
# =============================================================================

@dataclass(frozen=True)
class PolicyContext:
    """Context for policy evaluation."""
    runtime_id: str
    timestamp: float = field(default_factory=time.monotonic)
    user_id: Optional[str] = None
    operation: Optional[str] = None


# =============================================================================
# Policy Decision
# =============================================================================

@dataclass(frozen=True)
class PolicyDecision:
    """Result of policy evaluation."""
    allowed: bool
    rule_id: Optional[str] = None
    explanation: Optional[str] = None
    decision_time_ms: float = 0.0


# =============================================================================
# Policy Engine
# =============================================================================

@dataclass(frozen=True)
class PolicySnapshot:
    """
    Snapshot of policy state at a point in time.
    
    Used for:
    - Drift detection (compare to effective config)
    - Rollback support
    - Historical analysis
    - Multi-runtime isolation
    """
    
    snapshot_id: str
    runtime_id: str
    effective_config_version: int
    applied_version: Optional[int] = None
    
    # Policy state
    active_policies: Tuple[str, ...] = field(default_factory=tuple)
    rule_counts: Dict[str, int] = field(default_factory=dict)  # domain -> count
    
    created_at: float = field(default_factory=time.monotonic)
    
    def is_current(self) -> bool:
        return self.applied_version is None or self.applied_version == self.effective_config_version


class PolicyEngine:
    """
    Runtime-wide policy evaluation engine.
    
    This is the single authoritative source for policy decisions in a runtime.
    
    Invariants:
    - Side-effect-free during evaluation
    - Deterministic results for equivalent inputs
    - Versioned and immutable policies
    - Explainable decisions
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._rules: Dict[str, List[PolicyRule]] = {}  # domain -> rules
        self._policy_versions: Dict[str, int] = {}  # policy_id -> version
        self._lock = __import__("threading").Lock()
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def load_rules(
        self,
        domain: str,
        rules: Tuple[PolicyRule, ...],
        version: int = 1
    ) -> None:
        """
        Load policy rules for a domain.
        
        Args:
            domain: Domain to add rules to (e.g., "runtime", "kernel")
            rules: Rules to load
            version: Version number for this rule set
        """
        with self._lock:
            if domain not in self._rules:
                self._rules[domain] = []
            
            self._rules[domain].extend(rules)
            # Store version - highest version wins
    
    def evaluate(
        self,
        context: PolicyContext,
        field_path: str,
        value: Any
    ) -> PolicyDecision:
        """
        Evaluate policy for a configuration field.
        
        Args:
            context: Evaluation context (runtime_id, timestamp, etc.)
            field_path: Field being evaluated (e.g., "kernel.timeout")
            value: Value to evaluate
            
        Returns:
            PolicyDecision with allowed status and explanation
        """
        start_time = time.monotonic()
        
        # Find matching rules for this domain and path
        domain = field_path.split('.')[0] if '.' in field_path else ""
        
        matching_rules = []
        with self._lock:
            if domain in self._rules:
                for rule in self._rules[domain]:
                    # Check if rule matches
                    matches = True
                    
                    if rule.field_path and rule.field_path != field_path:
                        matches = False
                    
                    if rule.condition and not rule.condition({"field": field_path, "value": value}):
                        matches = False
                    
                    if matches:
                        matching_rules.append(rule)
        
        # Determine decision
        allowed = True
        explanation = f"No explicit policy rule for {field_path}"
        
        for rule in matching_rules:
            if rule.effect == RuleEffect.DENY:
                allowed = False
                explanation = f"Policy rule '{rule.name}' denied access to {field_path}"
                break
        
        decision_time_ms = (time.monotonic() - start_time) * 1000
        
        return PolicyDecision(
            allowed=allowed,
            rule_id=matching_rules[0].rule_id if matching_rules else None,
            explanation=explanation,
            decision_time_ms=decision_time_ms
        )
    
    def get_snapshot(self, effective_config_version: int) -> PolicySnapshot:
        """Create a snapshot of current policy state."""
        import uuid
        
        # Count rules by domain
        rule_counts = {domain: len(rules) for domain, rules in self._rules.items()}
        
        return PolicySnapshot(
            snapshot_id=str(uuid.uuid4()),
            runtime_id=self._runtime_id,
            effective_config_version=effective_config_version,
            applied_version=None,
            active_policies=tuple(self._policy_versions.keys()),
            rule_counts=rule_counts,
            created_at=time.monotonic()
        )
    
    def get_rule_count(self) -> int:
        """Return total number of rules loaded."""
        with self._lock:
            return sum(len(rules) for rules in self._rules.values())


# =============================================================================
# Policy Conflict
# =============================================================================

@dataclass(frozen=True)
class PolicyConflict:
    """
    A detected conflict between policy rules.
    
    Policies may be overridden by:
    - Emergency policies
    - Operator overrides
    - System constraints
    
    Conflicts are detected and reported but not automatically resolved.
    """
    
    conflict_id: str
    affected_decision: str  # e.g., "runtime.startup_enabled"
    conflicting_rules: Tuple[str, ...]  # rule IDs
    policy_sources: Tuple[str, ...]
    precedence_result: str  # Which policy won
    unresolved: bool = False


# =============================================================================
# Public API exports
# =============================================================================

__all__ = [
    # Policy IDs
    "PolicyId",
    "PolicyVersion",
    
    # Rules
    "RuleEffect",
    "PolicyRule",
    
    # Context and Decision
    "PolicyContext",
    "PolicyDecision",
    
    # Engine
    "PolicySnapshot",
    "PolicyEngine",
    
    # Conflicts
    "PolicyConflict",
]