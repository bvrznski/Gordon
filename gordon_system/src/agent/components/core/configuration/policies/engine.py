# Policy Resolution Engine - Phase 3.18
# =====================================
"""
Policy resolution engine for determining effective policies.

This module provides deterministic policy evaluation:
- Conflict detection and resolution
- Precedence application
- Scope validation
- Evaluation tracing

All policy operations are pure and return diagnostic results.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import time

from . import (
    PolicyDocument,
    PolicyRule,
    PolicyConstraint,
    PolicyId,
    PolicyScope,
    PolicyConflict,
    PrecedenceMode,
    PolicyEvaluationResult,
)


# =============================================================================
# Policy Resolution Engine
# =============================================================================

@dataclass(frozen=True)
class ResolutionContext:
    """Context for policy resolution."""
    runtime_id: str
    target_type: str  # component, capability, operation, etc.
    target_id: str
    timestamp: float


class ConflictStrategy(Enum):
    """How to handle conflicting policies."""
    DETECT_ONLY = "detect_only"          # Report conflicts but don't resolve
    DENY_OVERRODES_ALLOW = "deny_overrides_allow"
    ALLOW_OVERRODES_DENY = "allow_overrides_deny"
    HIGHEST_PRECEDENCE = "highest_precedence"


@dataclass(frozen=True)
class PolicyResolutionResult:
    """
    Result of policy resolution for a target.
    
    Contains all effective policies and any conflicts detected.
    """
    context: ResolutionContext
    effective_policies: Tuple[PolicyDocument, ...]
    effective_rules: Tuple[PolicyRule, ...]
    effective_constraints: Tuple[PolicyConstraint, ...]
    
    # Conflict information
    conflicts_detected: Tuple[PolicyConflict, ...] = field(default_factory=tuple)
    conflicts_resolved: Dict[str, str] = field(default_factory=dict)  # conflict_id -> resolution
    
    # Evaluation metadata
    evaluation_mode: PrecedenceMode
    timestamp: float


# =============================================================================
# Policy Evaluator
# =============================================================================

class PolicyEvaluator:
    """
    Deterministic policy evaluator.
    
    The evaluator NEVER executes runtime behavior. It only produces
    diagnostic information about what policies apply and their effects.
    
    Invariants:
    - Evaluation is pure (no side effects)
    - Same input always produces same output
    - All conflicts must be detectable
    - Diagnostics are complete for traceability
    """
    
    def __init__(
        self,
        precedence_mode: PrecedenceMode = PrecedenceMode.SPECIFIC_OVER_GENERAL,
        conflict_strategy: ConflictStrategy = ConflictStrategy.DETECT_ONLY
    ):
        self._precedence_mode = precedence_mode
        self._conflict_strategy = conflict_strategy
    
    @property
    def precedence_mode(self) -> PrecedenceMode:
        return self._precedence_mode
    
    def evaluate(
        self,
        policies: Tuple[PolicyDocument, ...],
        context: ResolutionContext
    ) -> PolicyResolutionResult:
        """
        Evaluate policies against a target in a specific context.
        
        Args:
            policies: All applicable policy documents
            context: Resolution context (runtime, target type/ID)
            
        Returns:
            Complete resolution result with effective policies and diagnostics
            
        Invariants:
        - Deterministic output for same input
        - No runtime state modified
        - All conflicts detected and documented
        """
        # Phase 1: Collect all rules from policies
        all_rules = self._collect_all_rules(policies)
        
        # Phase 2: Apply precedence and deduplicate
        effective_rules = self._apply_precedence(all_rules, context.target_id)
        
        # Phase 3: Extract effective constraints
        effective_constraints = tuple(
            rule.effect for rule in effective_rules
        )
        
        # Phase 4: Detect conflicts
        conflicts = self._detect_conflicts(policies, effective_rules)
        
        # Phase 5: Resolve conflicts (if strategy allows)
        resolved_conflicts = {}
        if self._conflict_strategy != ConflictStrategy.DETECT_ONLY:
            for conflict in conflicts:
                resolution = self._resolve_conflict(conflict)
                resolved_conflicts[conflict.conflict_id] = resolution
        
        # Phase 6: Determine final evaluation result
        eval_result = self._determine_evaluation_result(effective_constraints, context.target_type)
        
        return PolicyResolutionResult(
            context=context,
            effective_policies=policies,
            effective_rules=effective_rules,
            effective_constraints=effective_constraints,
            conflicts_detected=conflicts,
            conflicts_resolved=resolved_conflicts,
            evaluation_mode=self._precedence_mode,
            timestamp=context.timestamp
        )
    
    def _collect_all_rules(self, policies: Tuple[PolicyDocument, ...]) -> List[Tuple[PolicyDocument, PolicyRule]]:
        """Collect all rules from all policies."""
        all_rules = []
        for policy in policies:
            for rule in policy.rules:
                all_rules.append((policy, rule))
        return all_rules
    
    def _apply_precedence(
        self,
        rules: List[Tuple[PolicyDocument, PolicyRule]],
        target_id: str
    ) -> Tuple[PolicyRule, ...]:
        """Apply precedence and deduplicate rules."""
        # Group by rule priority (higher = more specific)
        prioritized: Dict[int, List[Tuple[PolicyDocument, PolicyRule]]] = {}
        for policy, rule in rules:
            if rule.priority not in prioritized:
                prioritized[rule.priority] = []
            prioritized[rule.priority].append((policy, rule))
        
        # Return highest priority rules (sorted by priority descending)
        result = []
        for priority in sorted(prioritized.keys(), reverse=True):
            result.extend(rule for _, rule in prioritized[priority])
        
        return tuple(result)
    
    def _detect_conflicts(
        self,
        policies: Tuple[PolicyDocument, ...],
        effective_rules: Tuple[PolicyRule, ...]
    ) -> Tuple[PolicyConflict, ...]:
        """Detect conflicts between policies."""
        conflicts = []
        conflict_counter = 0
        
        # Check for contradictory constraints on same target
        target_constraints: Dict[str, List[Tuple[PolicyDocument, PolicyConstraint]]] = {}
        for policy in policies:
            for rule in policy.rules:
                target_id = rule.effect.target
                if target_id not in target_constraints:
                    target_constraints[target_id] = []
                target_constraints[target_id].append((policy, rule.effect))
        
        # Find conflicting constraints (same target with different constraint types)
        for target_id, constraint_list in target_constraints.items():
            if len(constraint_list) < 2:
                continue
            
            constraint_types = set(c.effect.constraint_type for _, c in constraint_list)
            
            # If we have both ALLOW and DENY on same target, that's a conflict
            if "allow" in constraint_types and "deny" in constraint_types:
                conflicts.append(PolicyConflict(
                    conflict_id=f"conflict-{conflict_counter}",
                    conflicting_policies=tuple(set(p.policy_id for p, _ in constraint_list)),
                    conflict_type="contradictory",
                    affected_targets=(target_id,),
                    resolution_suggestion="Apply precedence: higher priority wins"
                ))
                conflict_counter += 1
        
        return tuple(conflicts)
    
    def _resolve_conflict(self, conflict: PolicyConflict) -> str:
        """Resolve a single conflict."""
        if self._precedence_mode == PrecedenceMode.DENY_OVERRODES_ALLOW:
            return "deny_overrides_allow"
        elif self._precedence_mode == PrecedenceMode.ALLOW_OVERRODES_DENY:
            return "allow_overrides_deny"
        else:
            # Generic resolution
            return f"highest_precedence_wins ({conflict.conflicting_policies[0]})"
    
    def _determine_evaluation_result(
        self,
        constraints: Tuple[PolicyConstraint, ...],
        target_type: str
    ) -> PolicyEvaluationResult:
        """Determine the overall evaluation result."""
        constraint_types = set(c.constraint_type for c in constraints)
        
        if "deny" in constraint_types:
            return PolicyEvaluationResult.DENIED
        elif "allow" in constraint_types:
            return PolicyEvaluationResult.ALLOWED
        else:
            # No explicit constraints - use default behavior based on target type
            if target_type == "component":
                return PolicyEvaluationResult.ALLOWED  # Components allowed by default
            else:
                return PolicyEvaluationResult.UNKNOWN


# =============================================================================
# Policy Registry
# =============================================================================

@dataclass(frozen=True)
class RegisteredPolicy:
    """A policy that has been registered in the registry."""
    policy: PolicyDocument
    registered_at: float = field(default_factory=time.monotonic)
    version: int = 1


class PolicyRegistry:
    """
    Canonical registry for policy documents.
    
    Responsibilities:
    - Register policies with unique IDs
    - Retrieve policies by ID or scope
    - List all registered policies
    - Provide snapshot capability
    
    Invariants:
    - Each policy_id is unique
    - Policies are immutable after registration
    - Registry provides consistent snapshots
    """
    
    def __init__(self):
        self._policies: Dict[str, RegisteredPolicy] = {}
        self._lock = _import_threading().Lock()
    
    def register(self, policy: PolicyDocument) -> RegisteredPolicy:
        """Register a new policy."""
        with self._lock:
            policy_id_str = str(policy.policy_id)
            if policy_id_str in self._policies:
                existing = self._policies[policy_id_str]
                # Update version
                new_version = existing.version + 1
            else:
                new_version = 1
            
            registered = RegisteredPolicy(
                policy=policy,
                registered_at=time.monotonic(),
                version=new_version
            )
            self._policies[policy_id_str] = registered
            return registered
    
    def get(self, policy_id: PolicyId) -> Optional[RegisteredPolicy]:
        """Get a registered policy by ID."""
        with self._lock:
            return self._policies.get(str(policy_id))
    
    def list_by_scope(self, scope: PolicyScope) -> Tuple[PolicyDocument, ...]:
        """List all policies for a given scope."""
        with self._lock:
            return tuple(
                reg.policy for reg in self._policies.values()
                if reg.policy.scope == scope
            )
    
    def list_all(self) -> Tuple[PolicyDocument, ...]:
        """List all registered policies."""
        with self._lock:
            return tuple(reg.policy for reg in self._policies.values())
    
    def snapshot(self) -> Tuple[RegisteredPolicy, ...]:
        """Create an immutable snapshot of current registry state."""
        with self._lock:
            return tuple(self._policies.values())


def _import_threading():
    """Import threading module lazily to avoid circular imports."""
    import threading
    return threading


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Context & Types
    "ResolutionContext",
    "ConflictStrategy",
    
    # Resolution Result
    "PolicyResolutionResult",
    
    # Engine
    "PolicyEvaluator",
    
    # Registry
    "RegisteredPolicy",
    "PolicyRegistry",
]