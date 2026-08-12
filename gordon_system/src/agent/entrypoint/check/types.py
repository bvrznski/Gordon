"""Gordon Agent Preflight Types and Enumerations.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Core type definitions for the preflight system:
- Outcome enumerations
- Phase model
- Check categories and severities
- Compilation policies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Tuple, Optional


# =============================================================================
# Request Identity Models (for preflight request)
# =============================================================================

@dataclass(frozen=True)
class AgentLaunchIdentity:
    """Identity of the launch request being preflighted."""
    
    launch_id: str
    timestamp_ns: int
    invocation_surface: str


@dataclass(frozen=True)
class AgentProcessIdentity:
    """Identity of the process performing preflight."""
    
    process_id: int
    parent_process_id: Optional[int]


# =============================================================================
# Preflight Outcomes
# =============================================================================

class AgentPreflightOutcome(Enum):
    """Possible preflight execution outcomes.
    
    Only PASS and policy-permitted PASS_WITH_WARNINGS may proceed to initialization.
    """
    
    PASS = "pass"                    # All mandatory checks passed
    PASS_WITH_WARNINGS = "pass_with_warnings"  # Passed with non-blocking warnings
    BLOCKED = "blocked"              # Found blocking startup conditions
    FAILED = "failed"                # Preflight mechanism itself failed
    CANCELLED = "cancelled"          # Explicitly cancelled
    TIMED_OUT = "timed_out"          # Exceeded deadline
    
    def is_success(self) -> bool:
        """Check if this outcome permits initialization."""
        return self in (AgentPreflightOutcome.PASS, AgentPreflightOutcome.PASS_WITH_WARNINGS)
    
    @classmethod
    def from_result(cls, blockers: int, warnings: int, errors: int) -> "AgentPreflightOutcome":
        """Determine outcome based on check results.
        
        Args:
            blockers: Number of blocking failures
            warnings: Number of non-blocking warnings
            errors: Number of internal errors
        
        Returns:
            Appropriate outcome enum value
        """
        if errors > 0:
            return cls.FAILED
        elif blockers > 0:
            return cls.BLOCKED
        elif warnings > 0:
            return cls.PASS_WITH_WARNINGS
        else:
            return cls.PASS


# =============================================================================
# Preflight Phases
# =============================================================================

class AgentPreflightPhase(Enum):
    """Preflight execution phases.
    
    Defines the explicit phase model with valid transitions between phases.
    """
    
    CREATED = "created"
    VALIDATING_REQUEST = "validating_request"
    RESOLVING_POLICY = "resolving_policy"
    RESOLVING_ROOTS = "resolving_roots"
    VALIDATING_MANIFEST = "validating_manifest"
    FINGERPRINTING_SOURCE = "fingerprinting_source"
    FINGERPRINTING_ARTIFACT = "fingerprinting_artifact"
    VALIDATING_PACKAGE_LAYOUT = "validating_package_layout"
    VALIDATING_METADATA = "validating_metadata"
    VALIDATING_STARTUP_SYMBOLS = "validating_startup_symbols"
    VALIDATING_DESCRIPTOR_SYNTAX = "validating_descriptor_syntax"
    COMPILING = "compiling"
    VALIDATING_CONFIGURATION_ACCESS = "validating_configuration_access"
    VALIDATING_ENVIRONMENT = "validating_environment"
    VALIDATING_FILESYSTEM = "validating_filesystem"
    VALIDATING_EXECUTABLES = "validating_executables"
    VALIDATING_NATIVE_LIBRARIES = "validating_native_libraries"
    VALIDATING_COMPUTE_VISIBILITY = "validating_compute_visibility"
    VALIDATING_RESOURCE_FEASIBILITY = "validating_resource_feasibility"
    VALIDATING_ENDPOINTS = "validating_endpoints"
    VALIDATING_LOCK_STATE = "validating_lock_state"
    VALIDATING_SHUTDOWN_EVIDENCE = "validating_shutdown_evidence"
    VALIDATING_MIGRATION_COMPATIBILITY = "validating_migration_compatibility"
    VALIDATING_SCHEMA_COMPATIBILITY = "validating_schema_compatibility"
    VALIDATING_ARCHITECTURAL_BOUNDARIES = "validating_architectural_boundaries"
    AGGREGATING_RESULTS = "aggregating_results"
    COMPLETED = "completed"
    
    # Terminal states
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


# =============================================================================
# Check Kinds and Severities
# =============================================================================

class AgentPreflightCheckKind(Enum):
    """Categories of preflight checks."""
    
    SOURCE = "source"
    ARTIFACT = "artifact"
    SYNTAX = "syntax"
    COMPILATION = "compilation"
    PACKAGE_LAYOUT = "package_layout"
    METADATA = "metadata"
    ENTRYPOINT_CONTRACT = "entrypoint_contract"
    DESCRIPTOR_STATIC_VALIDITY = "descriptor_static_validity"
    CONFIGURATION_ACCESS = "configuration_access"
    ENVIRONMENT = "environment"
    FILESYSTEM = "filesystem"
    EXECUTABLE = "executable"
    NATIVE_LIBRARY = "native_library"
    COMPUTE_VISIBILITY = "compute_visibility"
    RESOURCE_FEASIBILITY = "resource_feasibility"
    ENDPOINT = "endpoint"
    LOCK_STATE = "lock_state"
    SHUTDOWN_EVIDENCE = "shutdown_evidence"
    MIGRATION_COMPATIBILITY = "migration_compatibility"
    SCHEMA_COMPATIBILITY = "schema_compatibility"
    ARCHITECTURE_BOUNDARY = "architecture_boundary"
    SECURITY = "security"
    TRUST = "trust"
    ASSISTANT_ISOLATION = "assistant_isolation"


class AgentPreflightSeverity(Enum):
    """Check result severities."""
    
    BLOCKER = "blocker"              # Blocks startup
    ERROR = "error"                  # Internal failure or non-blocking error
    WARNING = "warning"              # Non-blocking warning
    OBSERVATION = "observation"      # Informational observation
    INFORMATIONAL = "informational"  # Purely informational
    
    def is_blocking(self) -> bool:
        """Check if this severity blocks startup."""
        return self == AgentPreflightSeverity.BLOCKER


# =============================================================================
# Compilation Policies
# =============================================================================

class AgentCompilationPolicy(Enum):
    """Compilation policy options.
    
    Determines which source files are compiled during preflight.
    """
    
    NONE = "none"                    # Skip compilation, use only packaged artifact verification
    TARGETED = "targeted"            # Compile only canonical startup modules
    CHANGED = "changed"              # Compile changed files from manifest
    COMPONENT_DESCRIPTORS = "component_descriptors"  # Compile __load__.py files
    FULL_AGENT = "full_agent"        # Compile complete approved Agent source tree
    FULL_GORDON = "full_gordon"      # Compile Agent + Assistant + bridge
    PACKAGED_ARTIFACT = "packaged_artifact"  # Validate installed package, no compilation


# =============================================================================
# Request Models (base definitions)
# =============================================================================

@dataclass(frozen=True)
class AgentPreflightRequestID:
    """Unique identifier for a preflight request."""
    
    value: str
    
    @classmethod
    def generate(cls) -> "AgentPreflightRequestID":
        """Generate a new unique request ID."""
        import uuid
        return cls(value=str(uuid.uuid4()))


# Note: AgentLaunchIdentity, AgentProcessIdentity defined above

@dataclass(frozen=True)
class AgentRuntimeIdentity:
    """Runtime identity context."""
    
    runtime_id: str
    boot_session_id: str


# =============================================================================
# Context Data Models (for check execution)
# =============================================================================

@dataclass(frozen=True)
class EnvironmentFacts:
    """Collected environment facts during preflight.
    
    This is a snapshot of environment state at the time of preflight,
    not live mutable state.
    """
    
    python_version: str
    platform: str
    working_directory: str
    env_keys: Tuple[str, ...] = field(default_factory=tuple)
    environment_fingerprint: str = ""


@dataclass(frozen=True)
class FilesystemEvidence:
    """Evidence collected from filesystem validation.
    
    Contains information about paths, permissions, and file states
    without exposing actual file handles or contents.
    """
    
    directories_found: Tuple[str, ...] = field(default_factory=tuple)
    files_found: Tuple[str, ...] = field(default_factory=tuple)
    writable_paths: Tuple[str, ...] = field(default_factory=tuple)
    executable_paths: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutableEvidence:
    """Evidence about external executables.
    
    Contains verified information about required external tools
    without executing them arbitrarily.
    """
    
    name: str
    found_path: Optional[str]
    version: Optional[str]
    trusted: bool
    
    @classmethod
    def from_result(cls, name: str, path: Optional[str] = None,
                    version: Optional[str] = None, trusted: bool = True) -> "ExecutableEvidence":
        """Create executable evidence from a probe result."""
        return cls(
            name=name,
            found_path=path,
            version=version,
            trusted=trusted
        )


@dataclass(frozen=True)
class ComputeEvidence:
    """Coarse compute visibility evidence.
    
    Does NOT reserve resources or allocate devices.
    """
    
    cpu_count: int = 0
    memory_bytes: int = 0
    gpu_visible: bool = False
    gpu_count: int = 0
    
    @classmethod
    def from_system(cls) -> "ComputeEvidence":
        """Gather compute evidence without allocating resources."""
        import os
        return cls(
            cpu_count=os.cpu_count() or 0,
            memory_bytes=0,  # Bounded probe - don't allocate
            gpu_visible=False,  # No heavy GPU initialization
            gpu_count=0
        )


@dataclass(frozen=True)
class ResourceFeasibility:
    """Coarse resource feasibility assessment.
    
    Does NOT make reservations or allocations.
    """
    
    ram_feasible: bool = True
    storage_feasible: bool = True
    vram_feasible: bool = True
    
    @classmethod
    def feasible(cls) -> "ResourceFeasibility":
        """Return a feasible assessment."""
        return cls()


# =============================================================================
# Check Result Data Models
# =============================================================================

@dataclass(frozen=True)
class AgentPreflightCheckResult:
    """Immutable result of a single preflight check.
    
    Preserves evidence for each individual check without exposing
    live runtime objects or secrets.
    """
    
    check_id: str
    check_kind: AgentPreflightCheckKind
    phase: AgentPreflightPhase
    status: bool  # True = passed, False = failed/warning/blocker
    
    # Severity classification
    severity: AgentPreflightSeverity
    
    # Status details
    is_mandatory: bool
    summary: str
    
    # Evidence
    expected_condition: Optional[str]
    observed_condition: Optional[str]
    
    # Outcome indicators
    is_blocker: bool = False
    is_warning: bool = False
    is_error: bool = False
    
    # Timing
    started_ns: int = 0
    completed_ns: int = 0
    
    # Remediation guidance
    remediation_guidance: Optional[str] = None
    
    # Provenance
    source: str = ""
    
    def get_status(self) -> AgentPreflightOutcome:
        """Convert to outcome enum for this check."""
        if self.is_blocker:
            return AgentPreflightOutcome.BLOCKED
        elif self.is_error:
            return AgentPreflightOutcome.FAILED
        elif self.is_warning:
            return AgentPreflightOutcome.PASS_WITH_WARNINGS
        else:
            return AgentPreflightOutcome.PASS


@dataclass(frozen=True)
class PreflightCompilationResult:
    """Summary of compilation operations.
    
    Tracks which files were compiled and any errors encountered,
    without executing the source code.
    """
    
    total_targets: int = 0
    compiled_successfully: int = 0
    compilation_errors: Tuple[str, ...] = field(default_factory=tuple)
    syntax_errors: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PreflightDiagnostics:
    """Immutable diagnostics for a preflight operation.
    
    Bounded and secret-safe diagnostic information without live handles.
    """
    
    preflight_id: str
    launch_id: str
    process_id: int
    current_phase: AgentPreflightPhase
    
    # Summary counts
    completed_checks: int = 0
    skipped_checks: int = 0
    blocking_checks: int = 0
    warning_checks: int = 0
    
    # Outcome
    outcome: AgentPreflightOutcome = AgentPreflightOutcome.PASS
    primary_failure: Optional[str] = None
    
    # Timing
    start_ns: int = 0
    end_ns: int = 0


# =============================================================================
# Policy Models
# =============================================================================

@dataclass(frozen=True)
class AgentPreflightPolicy:
    """Immutable preflight policy configuration.
    
    Defines which checks are mandatory, optional, or skipped,
    along with other behavioral policies.
    """
    
    # Check policies
    mandatory_checks: Tuple[str, ...] = field(default_factory=tuple)
    optional_checks: Tuple[str, ...] = field(default_factory=tuple)
    skipped_checks: Tuple[str, ...] = field(default_factory=tuple)
    
    # Outcome policies
    allow_warnings: bool = True
    
    # Timeout policy (in seconds)
    default_timeout_seconds: float = 60.0
    
    # Mode policies
    source_mode: bool = True  # Source deployment vs packaged artifact
    validation_only: bool = False
    
    # Cleanup policies
    cleanup_temporary_files: bool = True
    release_temporary_ports: bool = True
    
    @classmethod
    def default(cls) -> "AgentPreflightPolicy":
        """Return a sensible default policy."""
        return cls(
            mandatory_checks=(),
            optional_checks=(),
            skipped_checks=(),
            allow_warnings=True,
            default_timeout_seconds=60.0,
            source_mode=True,
            validation_only=False,
            cleanup_temporary_files=True,
            release_temporary_ports=True
        )