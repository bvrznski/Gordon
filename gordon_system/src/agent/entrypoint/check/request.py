"""Gordon Agent Preflight Request Model.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Immutable preflight request that preserves all necessary context
for a single preflight operation without including runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional
from pathlib import PurePath

from .types import (
    AgentLaunchIdentity,
    AgentProcessIdentity,
    AgentRuntimeIdentity,
    AgentCompilationPolicy,
)


@dataclass(frozen=True)
class AgentPreflightRequest:
    """Immutable preflight request that preserves launch identity.
    
    This is the contract between the entrypoint and the preflight checker.
    It must be immutable, deterministic, and contain no runtime state.
    
    Request Flow:
        Launch Request (from main.py)
            ↓
        Preflight Request (this class)
            ↓
        Preflight Checker
            ↓
        Preflight Result
    
    The request preserves:
    - Launch identity for result binding
    - Process identity for evidence provenance
    - Policy references for check behavior
    - Source/artifact roots for validation
    - Configuration generation for freshness tracking
    """
    
    # Identity (immutable, preserved through preflight)
    request_id: str
    launch_identity: AgentLaunchIdentity
    process_identity: AgentProcessIdentity
    runtime_identity: Optional[AgentRuntimeIdentity] = None
    
    # Roots (approved paths for validation)
    approved_source_roots: Tuple[str, ...] = field(default_factory=tuple)
    approved_artifact_roots: Tuple[str, ...] = field(default_factory=tuple)
    
    # Configuration context
    configuration_generation: int = 0
    config_request_path: Optional[str] = None
    profile: str = "default"
    environment: str = "production"
    
    # Policy references (by name or path for determinism)
    preflight_policy_name: Optional[str] = None
    compilation_policy: AgentCompilationPolicy = AgentCompilationPolicy.TARGETED
    
    # Operational mode flags
    safe_mode_enabled: bool = False
    offline_mode_enabled: bool = False
    is_validation_only: bool = False
    
    # Deadlines and control
    startup_deadline_seconds: float = 30.0
    cancellation_requested: bool = False
    
    # Evidence tracking
    source_fingerprint: Optional[str] = None
    artifact_fingerprint: Optional[str] = None
    configuration_generation_evidence: str = ""
    
    # Runtime directory policy
    runtime_directory_policy: Dict[str, Any] = field(default_factory=dict)
    
    def get_approved_source_root_paths(self) -> Tuple[PurePath, ...]:
        """Convert approved source roots to Path objects."""
        return tuple(PurePath(root) for root in self.approved_source_roots)
    
    def get_approved_artifact_root_paths(self) -> Tuple[PurePath, ...]:
        """Convert approved artifact roots to Path objects."""
        return tuple(PurePath(artifact) for artifact in self.approved_artifact_roots)
    
    @classmethod
    def create(
        cls,
        request_id: Optional[str] = None,
        launch_identity: Optional[AgentLaunchIdentity] = None,
        process_identity: Optional[AgentProcessIdentity] = None,
        **kwargs
    ) -> "AgentPreflightRequest":
        """Create a preflight request with defaults."""
        import uuid
        import time
        
        return cls(
            request_id=request_id or str(uuid.uuid4()),
            launch_identity=launch_identity or AgentLaunchIdentity(
                launch_id=str(uuid.uuid4()),
                timestamp_ns=time.time_ns(),
                invocation_surface="UNKNOWN"
            ),
            process_identity=process_identity or AgentProcessIdentity(
                process_id=0,
                parent_process_id=None
            ),
            **kwargs
        )
    
    def with_source_roots(self, *roots: str) -> "AgentPreflightRequest":
        """Return new request with additional source roots."""
        new_roots = self.approved_source_roots + tuple(roots)
        return dataclass_replace(self, approved_source_roots=new_roots)
    
    def with_artifact_roots(self, *roots: str) -> "AgentPreflightRequest":
        """Return new request with additional artifact roots."""
        new_roots = self.approved_artifact_roots + tuple(roots)
        return dataclass_replace(self, approved_artifact_roots=new_roots)
    
    def with_compilation_policy(self, policy: AgentCompilationPolicy) -> "AgentPreflightRequest":
        """Return new request with updated compilation policy."""
        return dataclass_replace(self, compilation_policy=policy)


# Helper for dataclass immutability
def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Replacement for dataclasses.replace in frozen dataclasses."""
    import dataclasses
    if dataclasses.is_dataclass(instance) and not isinstance(instance, type):
        return dataclasses.replace(instance, **kwargs)
    raise TypeError(f"Instance {instance} is not a dataclass")


@dataclass(frozen=True)
class PreflightRequestValidationError:
    """Immutable error information from request validation."""
    
    field_name: str
    error_type: str  # e.g., "missing", "invalid_value", "type_error"
    message: str
    
    @classmethod
    def missing(cls, field_name: str) -> "PreflightRequestValidationError":
        """Create a missing field error."""
        return cls(
            field_name=field_name,
            error_type="missing",
            message=f"Required field '{field_name}' is missing"
        )
    
    @classmethod
    def invalid_value(cls, field_name: str, value: Any, reason: str) -> "PreflightRequestValidationError":
        """Create an invalid value error."""
        return cls(
            field_name=field_name,
            error_type="invalid_value",
            message=f"Invalid value for '{field_name}': {value} - {reason}"
        )