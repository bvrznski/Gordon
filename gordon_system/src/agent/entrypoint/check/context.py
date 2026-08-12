"""Gordon Agent Preflight Context for Check Execution.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Context for check execution that provides narrow interfaces to
execution environment without exposing mutable state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional, Callable
import time


@dataclass(frozen=True)
class AgentPreflightContext:
    """Immutable or safely evolving operation-scoped context for checks.
    
    Provides narrow interfaces to execution environment while maintaining
    isolation between preflight operations and runtime.
    
    Context provides:
    - Monotonic clock for timing
    - Approved root resolution
    - Source/artifact manifest providers  
    - Compiler facade (no module execution)
    - Environment evidence provider
    - Filesystem evidence provider
    - Executable/native-library resolvers
    - Diagnostics interface
    
    Context does NOT provide:
    - Runtime objects or services
    - Mutable state access
    - Configuration secrets
    - Active resource handles
    """
    
    # Identity (operation-scoped)
    preflight_id: str
    launch_id: str
    process_id: int
    
    # Time sources
    start_time_ns: int  # Monotonic timestamp when context was created
    
    # Root resolution (approved paths only)
    approved_source_roots: Tuple[str, ...] = field(default_factory=tuple)
    approved_artifact_roots: Tuple[str, ...] = field(default_factory=tuple)
    
    # Manifest providers
    source_manifest_data: Dict[str, Any] = field(default_factory=dict)
    artifact_manifest_data: Dict[str, Any] = field(default_factory=dict)
    
    # Evidence providers (frozen snapshots)
    environment_facts: Dict[str, Any] = field(default_factory=dict)
    filesystem_evidence: Dict[str, Any] = field(default_factory=dict)
    executable_evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Compilation interface (no module execution)
    compile_callable: Optional[Callable[[str], Tuple[bool, str]]] = None
    
    # Timeout tracking
    check_timeouts: Dict[str, float] = field(default_factory=dict)
    
    def get_current_time_ns(self) -> int:
        """Get current monotonic time in nanoseconds."""
        return time.time_ns()
    
    def get_elapsed_seconds(self) -> float:
        """Get seconds elapsed since context creation."""
        now = self.get_current_time_ns()
        return (now - self.start_time_ns) / 1_000_000_000.0
    
    def resolve_source_root(self, root_name: str) -> Optional[str]:
        """Resolve a source root by name to its path."""
        # In the current context, roots are already resolved
        if root_name in self.approved_source_roots:
            return root_name
        return None
    
    def resolve_artifact_root(self, root_name: str) -> Optional[str]:
        """Resolve an artifact root by name to its path."""
        if root_name in self.approved_artifact_roots:
            return root_name
        return None
    
    def get_environment_fact(self, fact_name: str, default: Any = None) -> Any:
        """Get an environment fact value."""
        return self.environment_facts.get(fact_name, default)
    
    def get_filesystem_evidence(self, path: str) -> Optional[Dict[str, Any]]:
        """Get filesystem evidence for a path."""
        return self.filesystem_evidence.get(path)
    
    def get_check_timeout(self, check_id: str) -> float:
        """Get timeout for a specific check, or default."""
        return self.check_timeouts.get(check_id, 60.0)
    
    @classmethod
    def create(
        cls,
        preflight_id: str,
        launch_id: str,
        process_id: int,
        approved_source_roots: Tuple[str, ...] = (),
        approved_artifact_roots: Tuple[str, ...] = (),
        environment_facts: Dict[str, Any] = None,
        **kwargs
    ) -> "AgentPreflightContext":
        """Create a new preflight context."""
        if environment_facts is None:
            environment_facts = {}
        
        return cls(
            preflight_id=preflight_id,
            launch_id=launch_id,
            process_id=process_id,
            start_time_ns=time.time_ns(),
            approved_source_roots=approved_source_roots,
            approved_artifact_roots=approved_artifact_roots,
            environment_facts=environment_facts or {},
            **kwargs
        )
    
    def with_env_fact(self, name: str, value: Any) -> "AgentPreflightContext":
        """Return new context with an additional environment fact."""
        new_facts = dict(self.environment_facts)
        new_facts[name] = value
        return dataclass_replace(self, environment_facts=new_facts)
    
    def with_filesystem_evidence(self, path: str, evidence: Dict[str, Any]) -> "AgentPreflightContext":
        """Return new context with filesystem evidence."""
        new_evidence = dict(self.filesystem_evidence)
        new_evidence[path] = evidence
        return dataclass_replace(self, filesystem_evidence=new_evidence)


# Helper for dataclass immutability
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace in frozen dataclasses."""
    import dataclasses
    if dataclasses.is_dataclass(instance) and not isinstance(instance, type):
        return dataclasses.replace(instance, **kwargs)
    raise TypeError(f"Instance {instance} is not a dataclass")


@dataclass(frozen=True)
class CheckExecutionState:
    """Immutable state of a check execution at a point in time.
    
    Used to track progress through the preflight phases.
    """
    
    check_id: str
    phase: str  # Current sub-phase
    started_ns: int
    completed_ns: Optional[int] = None
    
    status: str = "pending"  # pending, running, passed, failed, skipped
    
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        """Check if the check execution is complete."""
        return self.completed_ns is not None
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds (0.0 if not complete)."""
        if self.completed_ns is None:
            return 0.0
        return (self.completed_ns - self.started_ns) / 1_000_000_000.0
    
    def with_status(self, new_status: str) -> "CheckExecutionState":
        """Return new state with updated status."""
        return dataclass_replace(
            self,
            status=new_status,
            completed_ns=self.get_current_time_ns() if new_status in ("passed", "failed") else None
        )
    
    def get_current_time_ns(self) -> int:
        """Get current monotonic time."""
        import time
        return time.time_ns()