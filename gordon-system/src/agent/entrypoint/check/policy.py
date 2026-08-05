"""Gordon Agent Preflight and Compilation Policy Models.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Policy models for preflight execution and compilation behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional


@dataclass(frozen=True)
class AgentPreflightPolicy:
    """Immutable policy controlling preflight check behavior.
    
    Defines which checks are mandatory, optional, or skipped,
    along with timeout and cleanup policies.
    """
    
    # Check policies - list of check IDs
    mandatory_checks: Tuple[str, ...] = field(default_factory=tuple)
    optional_checks: Tuple[str, ...] = field(default_factory=tuple)
    skipped_checks: Tuple[str, ...] = field(default_factory=tuple)
    
    # Severity elevation (e.g., warning -> blocker)
    severity_elevations: Dict[str, str] = field(default_factory=dict)
    
    # Timeout policy (seconds)
    default_timeout_seconds: float = 60.0
    check_timeouts: Dict[str, float] = field(default_factory=dict)
    
    # Mode policies
    source_mode: bool = True  # Source deployment vs packaged artifact
    validation_only: bool = False
    
    # Outcome policies
    allow_warnings: bool = True
    fail_fast_on_first_blocker: bool = True
    
    # Cleanup policies
    cleanup_temporary_files: bool = True
    release_temporary_ports: bool = True
    terminate_subprocesses: bool = True
    
    @classmethod
    def default(cls) -> "AgentPreflightPolicy":
        """Return a sensible default policy."""
        return cls(
            mandatory_checks=(),
            optional_checks=(),
            skipped_checks=(),
            severity_elevations={},
            default_timeout_seconds=60.0,
            check_timeouts={},
            source_mode=True,
            validation_only=False,
            allow_warnings=True,
            fail_fast_on_first_blocker=True,
            cleanup_temporary_files=True,
            release_temporary_ports=True,
            terminate_subprocesses=True
        )
    
    @classmethod
    def strict(cls) -> "AgentPreflightPolicy":
        """Return a strict policy that fails on any issue."""
        return cls(
            mandatory_checks=(),
            optional_checks=(),
            skipped_checks=(),
            severity_elevations={},
            default_timeout_seconds=30.0,
            check_timeouts={},
            source_mode=True,
            validation_only=False,
            allow_warnings=False,
            fail_fast_on_first_blocker=True,
            cleanup_temporary_files=True,
            release_temporary_ports=True,
            terminate_subprocesses=True
        )
    
    @classmethod
    def development(cls) -> "AgentPreflightPolicy":
        """Return a development policy with relaxed requirements."""
        return cls(
            mandatory_checks=(),
            optional_checks=("python_version",),
            skipped_checks=(),
            severity_elevations={},
            default_timeout_seconds=120.0,
            check_timeouts={},
            source_mode=True,
            validation_only=False,
            allow_warnings=True,
            fail_fast_on_first_blocker=False,  # Collect all issues
            cleanup_temporary_files=True,
            release_temporary_ports=True,
            terminate_subprocesses=True
        )
    
    def is_mandatory(self, check_id: str) -> bool:
        """Check if a check is mandatory."""
        return check_id in self.mandatory_checks
    
    def is_optional(self, check_id: str) -> bool:
        """Check if a check is optional."""
        return check_id in self.optional_checks
    
    def is_skipped(self, check_id: str) -> bool:
        """Check if a check is skipped."""
        return check_id in self.skipped_checks
    
    def get_check_timeout(self, check_id: str) -> Optional[float]:
        """Get timeout for a specific check, or default."""
        return self.check_timeouts.get(check_id, self.default_timeout_seconds)
    
    def elevate_severity(self, original: str) -> str:
        """Get elevated severity if configured."""
        return self.severity_elevations.get(original, original)


@dataclass(frozen=True)
class AgentCompilationPolicy:
    """Immutable policy controlling compilation behavior during preflight.
    
    Determines which source files are compiled and where output is placed.
    """
    
    # Policy mode
    mode: str  # none, targeted, changed, component_descriptors, full_agent, full_gordon, packaged_artifact
    
    # Source roots for compilation
    approved_source_roots: Tuple[str, ...] = field(default_factory=tuple)
    
    # Compilation targets (if known)
    include_patterns: Tuple[str, ...] = field(default_factory=tuple)
    exclude_patterns: Tuple[str, ...] = field(default_factory=tuple)
    
    # Output policy
    output_root: Optional[str] = None  # Where to place compiled files
    cache_policy: str = "system_pycache"  # system_pycache, temporary_cache, none
    
    # Compilation behavior
    verify_only: bool = False  # Only verify, don't write output
    deterministic_order: bool = True  # Ensure deterministic target ordering
    
    @classmethod
    def from_string(cls, mode_str: str) -> "AgentCompilationPolicy":
        """Create a policy from a string representation."""
        valid_modes = {
            "none",
            "targeted",
            "changed", 
            "component_descriptors",
            "full_agent",
            "full_gordon",
            "packaged_artifact"
        }
        
        if mode_str not in valid_modes:
            raise ValueError(f"Invalid compilation mode: {mode_str}")
        
        return cls(
            mode=mode_str,
            approved_source_roots=(),
            include_patterns=(),
            exclude_patterns=(),
            output_root=None,
            cache_policy="system_pycache",
            verify_only=False,
            deterministic_order=True
        )
    
    @classmethod
    def none(cls) -> "AgentCompilationPolicy":
        """Return a policy that skips compilation."""
        return cls.from_string("none")
    
    @classmethod
    def targeted(cls) -> "AgentCompilationPolicy":
        """Return a policy that compiles only startup modules."""
        return cls.from_string("targeted")
    
    @classmethod
    def full_agent(cls) -> "AgentCompilationPolicy":
        """Return a policy that compiles the complete Agent source tree."""
        return cls.from_string("full_agent")
    
    @classmethod
    def full_gordon(cls) -> "AgentCompilationPolicy":
        """Return a policy that compiles Agent + Assistant + bridge."""
        return cls.from_string("full_gordon")
    
    @classmethod
    def packaged_artifact(cls) -> "AgentCompilationPolicy":
        """Return a policy for validated packaged deployment (no compilation)."""
        return cls.from_string("packaged_artifact")
    
    def should_compile(self, source_path: str) -> bool:
        """Determine if a source file should be compiled based on patterns."""
        # If no patterns specified, compile everything in approved roots
        if not self.include_patterns and not self.exclude_patterns:
            return True
        
        # Check exclusions first
        for pattern in self.exclude_patterns:
            if pattern in source_path:
                return False
        
        # Check inclusions (if any specified)
        if self.include_patterns:
            for pattern in self.include_patterns:
                if pattern in source_path:
                    return True
            return False
        
        return True


def get_default_compilation_policy(source_mode: bool) -> AgentCompilationPolicy:
    """Get the default compilation policy based on deployment mode.
    
    Args:
        source_mode: True for source deployment, False for packaged artifact
    
    Returns:
        Appropriate compilation policy
    """
    if source_mode:
        return AgentCompilationPolicy.targeted()
    else:
        return AgentCompilationPolicy.packaged_artifact()