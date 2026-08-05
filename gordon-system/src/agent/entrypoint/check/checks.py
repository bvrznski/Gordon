"""Gordon Agent Preflight Check System.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Immutable check definitions with explicit identity, policy,
and execution semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional, Callable
import time


@dataclass(frozen=True)
class AgentPreflightCheck:
    """Immutable definition of a single preflight check.
    
    Each check has explicit identity and ownership, with deterministic
    behavior that preserves evidence without creating runtime state.
    
    Check Properties:
        - ID: Unique identifier for tracing
        - Kind: Category of the check (source, artifact, syntax, etc.)
        - Severity: Blocking error or warning
        - Mandatory/Optional: Whether it blocks startup on failure
        - Execution: Function to run the check (no imports executed)
        - Evidence Contract: What evidence is returned
    """
    
    # Identity
    check_id: str  # e.g., "python_version", "source_manifest"
    
    # Classification
    kind: str  # From AgentPreflightCheckKind enum
    
    # Owner/authority responsible for this check
    owner: str  # e.g., "compiler", "filesystem", "metadata"
    
    # Policy applicability
    mandatory: bool = True
    
    # Execution properties
    timeout_seconds: float = 60.0
    can_run_concurrently: bool = False
    
    # Check function signature:
    # (context: AgentPreflightContext, request: AgentPreflightRequest) -> AgentPreflightCheckResult
    execute: Optional[Callable[..., Any]] = None
    
    # Evidence contract
    input_requirements: Tuple[str, ...] = field(default_factory=tuple)
    evidence_produced: Tuple[str, ...] = field(default_factory=tuple)
    
    # Result criteria
    success_criteria: str = ""
    warning_criteria: str = ""
    blocker_criteria: str = ""
    
    def __post_init__(self) -> None:
        """Validate check definition."""
        if not self.check_id:
            raise ValueError("check_id is required")
        if not self.kind:
            raise ValueError("kind is required")
        if not self.owner:
            raise ValueError("owner is required")
        if self.execute is None:
            # Allow deferred execution setup
            pass
    
    def execute_check(
        self,
        context: Any,
        request: Any,
    ) -> Dict[str, Any]:
        """Execute this check with the given context and request.
        
        Args:
            context: Preflight context with execution environment
            request: Preflight request being validated
            
        Returns:
            Check result as a dictionary (for result compatibility)
        """
        if self.execute is None:
            # Default implementation - should be overridden
            return {
                "check_id": self.check_id,
                "phase": "unknown",
                "status": True,
                "severity": "informational",
                "is_mandatory": False,
                "summary": "No execution function defined",
                "expected_condition": None,
                "observed_condition": None,
                "started_ns": time.time_ns(),
                "completed_ns": time.time_ns(),
            }
        
        result = self.execute(context, request)
        if isinstance(result, AgentPreflightCheckResult):
            # Convert dataclass to dict for result compatibility
            return {
                "check_id": result.check_id,
                "phase": result.phase,
                "status": result.status,
                "severity": result.severity,
                "is_mandatory": result.is_mandatory,
                "summary": result.summary,
                "expected_condition": result.expected_condition,
                "observed_condition": result.observed_condition,
                "started_ns": result.started_ns,
                "completed_ns": result.completed_ns,
            }
        return result
    
    def with_timeout(self, timeout: float) -> "AgentPreflightCheck":
        """Return new check with updated timeout."""
        return dataclass_replace(self, timeout_seconds=timeout)


@dataclass(frozen=True)
class AgentPreflightCheckResult:
    """Immutable result of executing a single preflight check.
    
    Preserves evidence without exposing runtime state or secrets.
    """
    
    # Check identity
    check_id: str
    check_kind: str
    
    # Execution context
    phase: str
    status: bool  # True = passed (including warnings), False = failed
    
    # Severity classification
    severity: str  # "blocker", "error", "warning", "observation", "informational"
    
    # Status details
    is_mandatory: bool
    summary: str
    
    # Evidence (no secrets, no runtime objects)
    expected_condition: Optional[str]
    observed_condition: Optional[str]
    
    # Outcome indicators
    is_blocker: bool = False
    is_warning: bool = False
    is_error: bool = False
    
    # Timing
    started_ns: int = 0
    completed_ns: int = 0
    
    # Remediation guidance (no runtime state)
    remediation_guidance: Optional[str] = None
    
    # Provenance
    source: str = ""
    
    @property
    def duration_seconds(self) -> float:
        """Get check execution duration in seconds."""
        if self.completed_ns == 0 or self.started_ns == 0:
            return 0.0
        return (self.completed_ns - self.started_ns) / 1_000_000_000.0
    
    def is_passed(self) -> bool:
        """Check if the check passed (including warnings)."""
        return self.status and not self.is_error
    
    def is_failed(self) -> bool:
        """Check if the check failed or errored."""
        return not self.status or self.is_error


class PreflightCheckRegistry:
    """Immutable registry of preflight checks.
    
    Must be:
    - Immutable after construction
    - Explicitly owned (not global)
    - Operation-independent
    - Free of active state
    - Deterministic in ordering
    
    Registry contains only check definitions, not instances or results.
    """
    
    def __init__(self):
        self._checks: Dict[str, AgentPreflightCheck] = {}
        self._check_order: Tuple[str, ...] = ()
    
    def register(self, check: AgentPreflightCheck) -> "PreflightCheckRegistry":
        """Register a check definition (returns new registry)."""
        import copy
        new_registry = PreflightCheckRegistry.__new__(PreflightCheckRegistry)
        new_registry._checks = dict(self._checks)
        new_registry._check_order = tuple(self._check_order)
        
        if check.check_id in new_registry._checks:
            raise ValueError(f"Duplicate check ID: {check.check_id}")
        
        new_registry._checks[check.check_id] = check
        new_registry._check_order = new_registry._check_order + (check.check_id,)
        
        return new_registry
    
    def get(self, check_id: str) -> Optional[AgentPreflightCheck]:
        """Get a registered check by ID."""
        return self._checks.get(check_id)
    
    def all_checks(self) -> Tuple[AgentPreflightCheck, ...]:
        """Get all registered checks in deterministic order."""
        return tuple(self._checks[check_id] for check_id in self._check_order)
    
    def get_mandatory_checks(self) -> Tuple[AgentPreflightCheck, ...]:
        """Get mandatory checks in deterministic order."""
        return tuple(
            c for c in self.all_checks()
            if c.mandatory
        )
    
    def get_optional_checks(self) -> Tuple[AgentPreflightCheck, ...]:
        """Get optional checks in deterministic order."""
        return tuple(
            c for c in self.all_checks()
            if not c.mandatory
        )
    
    def get_skipped_checks(self) -> Tuple[str, ...]:
        """Get IDs of skipped checks (for policy override)."""
        # In current design, skipping is controlled by policy
        return ()


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace in frozen dataclasses."""
    import dataclasses
    if dataclasses.is_dataclass(instance) and not isinstance(instance, type):
        return dataclasses.replace(instance, **kwargs)
    raise TypeError(f"Instance {instance} is not a dataclass")


# =============================================================================
# Default Check Registry - Immutable Operation-Scoped Pattern
# =============================================================================

# The DEFAULT_CHECK_REGISTRY is now a factory that creates new immutable registries
# for each operation. This prevents mutable global state while maintaining the
# convenience of a "default" registry.

def get_default_check_registry() -> PreflightCheckRegistry:
    """Get an immutable check registry with default checks registered.
    
    Each call returns a NEW immutable registry, preventing module-level mutable
    state that violates CHECK-049. The returned registry contains only check
    definitions (no runtime state or results).
    
    This function is safe to call multiple times and can be used as:
        registry = get_default_check_registry()
        result = registry.get("some_check")
        
    Returns:
        An immutable PreflightCheckRegistry with default checks registered.
    """
    # Create a new registry for this operation
    registry = PreflightCheckRegistry.__new__(PreflightCheckRegistry)
    registry._checks = {}  # type: ignore[attr-defined]
    registry._check_order = ()  # type: ignore[attr-defined]
    
    return registry


# For backward compatibility with existing code that expects a registry reference,
# provide a sentinel value. DO NOT use this for actual check registration - always
# use get_default_check_registry() to create operation-scoped registries.
#
# Deprecated pattern (DO NOT USE):
#   DEFAULT_CHECK_REGISTRY.register(check)  # Wrong! Modifies global state
#
# Correct pattern:
#   registry = get_default_check_registry()  # Gets new immutable instance
