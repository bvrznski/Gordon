# Memory Authorization - Phase 5.1.3 Canonical Access Control
# ===========================================================

"""
Memory Authorization: Policy-based access control for memory operations.

Authorization determines:
    - Whether a request may proceed
    - What constraints apply to the results
    - Which visibility rules should be applied

Authorization Laws:
    AUTHORIZATION-LAW-001: Every request undergoes authorization
    AUTHORIZATION-LAW-002: Authorization precedes projection selection
    AUTHORIZATION-LAW-003: Policies are explicit and inspectable
    AUTHORIZATION-LAW-004: Authorization never modifies Memory
    AUTHORIZATION-LAW-005: Decisions preserve evidence
    AUTHORIZATION-LAW-006: Authorization is reproducible
    AUTHORIZATION-LAW-007: Failures remain observable
    AUTHORIZATION-LAW-008: Authorization is deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# POLICY TYPES - What kind of policy?
# =============================================================================


class PolicyType(Enum):
    """
    Types of authorization policies.
    
    | Type      | Description                                  |
    |-----------|---------------------------------------------|
    | RBAC      | Role-based access control                    |
    | ABAC      | Attribute-based access control               |
    | CBAC      | Context-based access control                 |
    | HBAC      | History-based access control                 |
    """
    
    RBAC = "rbac"     # Role-Based Access Control
    ABAC = "abac"     # Attribute-Based Access Control
    CBAC = "cbac"     # Context-Based Access Control
    HBAC = "hbac"     # History-Based Access Control


# =============================================================================
# POLICY ACTIONS - What may be done?
# =============================================================================


class PolicyAction(Enum):
    """
    Actions that policies can permit or deny.
    
    | Action      | Description                              |
    |-------------|------------------------------------------|
    | READ        | Read artifacts                           |
    | WRITE       | Write/update artifacts                   |
    | QUERY       | Execute queries                          |
    | PROJECT     | Generate projections                     |
    | PUBLISH     | Publish to external consumers            |
    | ADMIN       | Administrative operations                |
    """
    
    READ = "read"
    WRITE = "write"
    QUERY = "query"
    PROJECT = "project"
    PUBLISH = "publish"
    ADMIN = "admin"


# =============================================================================
# POLICY RULE - A single authorization rule
# =============================================================================


@dataclass(frozen=True)
class PolicyRule:
    """
    Single authorization rule.
    
    Fields:
        rule_id:            Unique identifier for this rule
        
        # Match conditions
        subject_match:      Which subjects does this apply to?
        object_match:       Which objects does this apply to?
        context_match:      What context must be present?
        
        # Action
        action:             What action is affected?
        effect:             Allow or deny?
        
        # Metadata
        priority:           Higher priority rules evaluated first
        enabled:            Is this rule active?
    """
    
    rule_id: str
    
    # Match conditions
    subject_match: Dict[str, Any] = field(default_factory=dict)
    object_match: Dict[str, Any] = field(default_factory=dict)
    context_match: Dict[str, Any] = field(default_factory=dict)
    
    # Action
    action: PolicyAction = PolicyAction.READ
    effect: str = "allow"  # allow or deny
    
    # Metadata
    priority: int = 0
    enabled: bool = True


# =============================================================================
# POLICY - Collection of rules
# =============================================================================


@dataclass(frozen=True)
class AuthorizationPolicy:
    """
    Policy containing authorization rules.
    
    Fields:
        policy_id:          Unique identifier
        
        name:              Human-readable name
        description:       What does this policy do?
        
        # Rules
        rules:             Tuple of rules in this policy
        default_effect:    Effect if no rule matches
        
        # Scope
        subjects:          Which subjects does this apply to?
        objects:           Which objects does this apply to?
        
        # Metadata
        version:           Policy version
        created_at_utc:    When was it created?
        enabled:           Is this policy active?
    """
    
    policy_id: str
    
    name: str
    description: Optional[str] = None
    
    rules: Tuple[PolicyRule, ...] = field(default_factory=tuple)
    default_effect: str = "deny"  # deny by default (principle of least privilege)
    
    subjects: Tuple[str, ...] = field(default_factory=tuple)
    objects: Tuple[str, ...] = field(default_factory=tuple)
    
    version: int = 1
    created_at_utc: float = field(default_factory=time.time)
    enabled: bool = True
    
    @property
    def rule_count(self) -> int:
        """Count of rules in this policy."""
        return len(self.rules)


# =============================================================================
# AUTHORIZATION DECISION - Result of authorization evaluation
# =============================================================================


@dataclass(frozen=True)
class AuthorizationDecision:
    """
    Result of evaluating authorization for a request.
    
    Fields:
        decision_id:        Unique identifier
        
        outcome:            ALLOW, DENY, or LIMIT
        matched_rules:      Which rules were used?
        denied_by:          If denied, which rule caused it?
        
        # Constraints
        visibility_filter:  What artifacts should be hidden?
        result_limit:       Maximum results allowed
        
        # Evidence
        evaluation_time_ms: How long did evaluation take?
        notes:              Explanation of decision
    """
    
    decision_id: str
    
    outcome: str = "allow"  # allow, deny, limit
    matched_rules: Tuple[str, ...] = field(default_factory=tuple)
    denied_by: Optional[str] = None  # If denied, which rule?
    
    visibility_filter: Dict[str, Any] = field(default_factory=dict)
    result_limit: int = 0  # 0 means no limit
    
    evaluation_time_ms: float = 0.0
    notes: Optional[str] = None
    
    @property
    def is_allowed(self) -> bool:
        """Check if access was granted."""
        return self.outcome == "allow"
    
    @property
    def is_denied(self) -> bool:
        """Check if access was denied."""
        return self.outcome == "deny"
    
    @property
    def is_limited(self) -> bool:
        """Check if access was granted with limitations."""
        return self.outcome == "limit"


# =============================================================================
# AUTHORIZER - Core authorization engine
# =============================================================================


class MemoryAuthorizer:
    """
    Core authorization engine for memory access.
    
    Processes requests through:
        1. Parse request context
        2. Match against policy rules
        3. Apply constraints
        4. Return decision
    
    The authorizer never modifies Memory - it only evaluates permissions.
    """
    
    def __init__(self):
        self._policies: Dict[str, AuthorizationPolicy] = {}
        self._rules: Dict[str, PolicyRule] = {}  # rule_id -> rule mapping
        self._evaluation_count: int = 0
    
    @property
    def policy_count(self) -> int:
        """Count of registered policies."""
        return len(self._policies)
    
    @property
    def evaluation_count(self) -> int:
        """Total evaluations performed."""
        return self._evaluation_count
    
    def register_policy(self, policy: AuthorizationPolicy) -> None:
        """
        Register a new authorization policy.
        
        Args:
            policy: Policy to add
        """
        self._policies[policy.policy_id] = policy
        for rule in policy.rules:
            if rule.enabled:
                self._rules[rule.rule_id] = rule
    
    def register_rule(self, rule: PolicyRule) -> None:
        """Register a standalone rule."""
        self._rules[rule.rule_id] = rule
    
    def evaluate(
        self,
        session: Any,
        request: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> AuthorizationDecision:
        """
        Evaluate authorization for a request.
        
        Args:
            session: MemoryAccessSession making the request
            request: MemoryAccessRequest being evaluated
            context: Additional evaluation context (optional)
            
        Returns:
            AuthorizationDecision with outcome and constraints
            
        The decision is deterministic - same inputs always produce same output.
        """
        start_time = time.time()
        
        # Build evaluation context
        eval_context = self._build_evaluation_context(session, request, context or {})
        
        # Find matching policies
        applicable_policies = self._find_applicable_policies(eval_context)
        
        # Evaluate rules (highest priority first)
        matched_rules: List[str] = []
        outcome = "deny"  # Default deny
        visibility_filter: Dict[str, Any] = {}
        result_limit = 0
        
        for policy in applicable_policies:
            if not policy.enabled:
                continue
            
            # Sort rules by priority (highest first)
            sorted_rules = sorted(
                [r for r in policy.rules if r.enabled],
                key=lambda r: -r.priority
            )
            
            for rule in sorted_rules:
                rule_match, constraint = self._evaluate_rule(rule, eval_context)
                
                if rule_match:
                    matched_rules.append(rule.rule_id)
                    
                    # Track the most specific match
                    if outcome == "deny" or rule.effect == "allow":
                        outcome = rule.effect
                    
                    # Merge constraints (most restrictive wins)
                    visibility_filter.update(constraint.get("visibility", {}))
                    constraint_limit = constraint.get("result_limit", 0)
                    if constraint_limit > 0:
                        result_limit = min(result_limit, constraint_limit) if result_limit > 0 else constraint_limit
        
        evaluation_time_ms = (time.time() - start_time) * 1000
        self._evaluation_count += 1
        
        return AuthorizationDecision(
            decision_id=str(time.time_ns()),
            outcome=outcome,
            matched_rules=tuple(matched_rules),
            visibility_filter=visibility_filter,
            result_limit=result_limit,
            evaluation_time_ms=evaluation_time_ms,
            notes=self._build_notes(outcome, matched_rules),
        )
    
    def _build_evaluation_context(
        self,
        session: Any,
        request: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build complete evaluation context."""
        return {
            "session_id": getattr(session, "session_id", None),
            "requester_id": getattr(session, "requester_id", None),
            "requester_type": getattr(session, "requester_type", "unknown"),
            "permissions": tuple(getattr(session, "permissions", ())),
            "artifact_ids": tuple(getattr(request, "artifact_ids", ())),
            "query_kind": getattr(request, "query_kind", "unknown"),
            "projection_type": str(getattr(request, "projection_type", "unknown")),
            **context,
        }
    
    def _find_applicable_policies(
        self,
        context: Dict[str, Any],
    ) -> Tuple[AuthorizationPolicy, ...]:
        """Find policies that apply to this evaluation."""
        applicable = []
        
        for policy in self._policies.values():
            if not policy.enabled:
                continue
            
            # Check subject match
            subjects = set(policy.subjects)
            requester_type = context.get("requester_type", "unknown")
            
            if subjects and requester_type not in subjects:
                continue
            
            # Check object match (if specified)
            objects = set(policy.objects)
            if objects:
                artifact_ids = context.get("artifact_ids", ())
                if not any(aid in objects for aid in artifact_ids):
                    continue
            
            applicable.append(policy)
        
        return tuple(applicable)
    
    def _evaluate_rule(
        self,
        rule: PolicyRule,
        context: Dict[str, Any],
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate a single rule against the context.
        
        Returns:
            (matched, constraints) where constraints contain visibility rules
        """
        if not rule.enabled:
            return False, {}
        
        # Check subject match
        if not self._match_dict(rule.subject_match, context):
            return False, {}
        
        # Check action match
        query_kind = context.get("query_kind", "unknown")
        action_to_kind = {
            "read": ("artifact",),
            "query": ("summary", "subgraph"),
            "project": ("artifact", "subgraph", "summary"),
            "publish": ("artifact", "subgraph", "summary"),
        }
        
        allowed_kinds = action_to_kind.get(rule.action.value, ())
        if query_kind not in allowed_kinds:
            return False, {}
        
        # Rule matched - apply effect
        constraints = {
            "visibility": dict(rule.context_match),
        }
        
        if rule.effect == "deny":
            constraints["result_limit"] = 0
        
        return True, constraints
    
    def _match_dict(
        self,
        pattern: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        """Check if context matches a pattern."""
        for key, expected in pattern.items():
            actual = context.get(key)
            
            if expected is None:
                # None means "any value"
                continue
            
            if isinstance(expected, (list, tuple)):
                # List means "must be one of these values"
                if actual not in expected:
                    return False
            else:
                # Exact match required
                if actual != expected:
                    return False
        
        return True
    
    def _build_notes(
        self,
        outcome: str,
        matched_rules: Tuple[str, ...],
    ) -> Optional[str]:
        """Build human-readable explanation of decision."""
        if not matched_rules:
            return f"No matching rules found; outcome: {outcome}"
        
        rule_info = ", ".join(matched_rules[:5])  # Show first 5
        if len(matched_rules) > 5:
            rule_info += f" (+{len(matched_rules) - 5} more)"
        
        return f"Outcome: {outcome}; Rules matched: {rule_info}"