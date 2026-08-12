# Development Tooling Contracts
# ==============================
"""
Tooling contracts define the interface specifications for development tools.

This module establishes the canonical contracts that all tooling must implement,
ensuring consistency, interoperability, and deterministic behavior across the
entire development ecosystem.

ARCHITECTURAL PRINCIPLES:
- Contracts are stable and versioned
- Tool implementations must conform to their contracts
- Runtime execution is independent of development tools
- All contracts support structured reports and metadata
- Extension points are well-defined
"""
from abc import ABC, abstractmethod
from typing import (
    Protocol,
    Dict,
    List,
    Optional,
    Any,
    TypeVar,
    Generic,
)
from dataclasses import dataclass, field
from enum import Enum
import datetime


# =============================================================================
# VERSIONING & METADATA
# =============================================================================

@dataclass(frozen=True)
class ToolVersion:
    """Immutable version representation."""
    major: int = 0
    minor: int = 0
    patch: int = 0
    pre_release: Optional[str] = None
    build_metadata: Optional[str] = None
    
    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            base += f"-{self.pre_release}"
        if self.build_metadata:
            base += f"+{self.build_metadata}"
        return base
    
    @classmethod
    def parse(cls, version_str: str) -> "ToolVersion":
        """Parse a semantic version string."""
        # Strip build metadata first
        if "+" in version_str:
            version_str, _ = version_str.split("+", 1)
        
        pre_release = None
        if "-" in version_str:
            version_str, pre_release = version_str.split("-", 1)
        
        parts = version_str.split(".")
        return cls(
            major=int(parts[0]) if len(parts) > 0 else 0,
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0,
            pre_release=pre_release,
        )
    
    def satisfies(self, constraint: str) -> bool:
        """Check if this version satisfies a semantic version constraint."""
        # Simplified constraint parsing
        if not constraint:
            return True
        
        constraint = constraint.strip()
        
        if constraint.startswith("=="):
            return self == ToolVersion.parse(constraint[2:].strip())
        elif constraint.startswith(">="):
            return self >= ToolVersion.parse(constraint[2:].strip())
        elif constraint.startswith("<="):
            return self <= ToolVersion.parse(constraint[2:].strip())
        elif constraint.startswith(">"):
            return self > ToolVersion.parse(constraint[1:].strip())
        elif constraint.startswith("<"):
            return self < ToolVersion.parse(constraint[1:].strip())
        else:
            # Assume exact match
            return self == ToolVersion.parse(constraint)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ToolVersion):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre_release == other.pre_release
        )
    
    def __lt__(self, other: "ToolVersion") -> bool:
        if not isinstance(other, ToolVersion):
            return NotImplemented
        if (self.major, self.minor, self.patch) != (
            other.major,
            other.minor,
            other.patch,
        ):
            return (self.major, self.minor, self.patch) < (
                other.major,
                other.minor,
                other.patch,
            )
        # Pre-release versions are less than release versions
        if self.pre_release is None and other.pre_release is not None:
            return False
        if self.pre_release is not None and other.pre_release is None:
            return True
        return (self.pre_release or "") < (other.pre_release or "")
    
    def __le__(self, other: "ToolVersion") -> bool:
        return self == other or self < other
    
    def __gt__(self, other: "ToolVersion") -> bool:
        return not self <= other
    
    def __ge__(self, other: "ToolVersion") -> bool:
        return not self < other


@dataclass(frozen=True)
class ToolMetadata:
    """Immutable metadata for a development tool."""
    name: str
    version: ToolVersion = field(default_factory=ToolVersion)
    description: str = ""
    category: str = "general"
    capabilities: List[str] = field(default_factory=list)
    dependencies: List["ToolDependency"] = field(default_factory=list)
    configuration_schema: Optional[Dict[str, Any]] = None
    documentation_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolMetadata":
        """Create metadata from a dictionary."""
        return cls(
            name=data.get("name", ""),
            version=ToolVersion.parse(data.get("version", "0.0.0"))
            if isinstance(data.get("version"), str)
            else ToolVersion(**data.get("version", {})),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            capabilities=data.get("capabilities", []),
            dependencies=[
                ToolDependency.from_dict(d) for d in data.get("dependencies", [])
            ],
            configuration_schema=data.get("configuration_schema"),
            documentation_url=data.get("documentation_url"),
        )


@dataclass(frozen=True)
class ToolDependency:
    """A dependency on another tool."""
    name: str
    version_constraint: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolDependency":
        """Create a dependency from a dictionary."""
        return cls(
            name=data.get("name", ""),
            version_constraint=data.get("version_constraint"),
        )


# =============================================================================
# EXECUTION CONTEXT & ENVIRONMENT
# =============================================================================

@dataclass(frozen=True)
class ToolExecutionContext:
    """Immutable context for tool execution."""
    working_directory: str
    environment_variables: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: Optional[float] = None
    dry_run: bool = False
    verbose: bool = False
    output_format: str = "text"
    
    def merge(self, other: "ToolExecutionContext") -> "ToolExecutionContext":
        """Merge contexts, with 'other' taking precedence."""
        return ToolExecutionContext(
            working_directory=other.working_directory or self.working_directory,
            environment_variables={**self.environment_variables, **other.environment_variables},
            timeout_seconds=other.timeout_seconds or self.timeout_seconds,
            dry_run=other.dry_run if other.dry_run is not None else self.dry_run,
            verbose=other.verbose if other.verbose is not None else self.verbose,
            output_format=other.output_format or self.output_format,
        )


# =============================================================================
# TOOL CONTRACTS (Protocols)
# =============================================================================

T = TypeVar("T")


class Tool(ABC):
    """Base abstract class for all development tools."""
    
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        raise NotImplementedError
    
    @abstractmethod
    def execute(
        self,
        context: Optional[ToolExecutionContext] = None,
        **kwargs: Any,
    ) -> "ToolResult":
        """Execute the tool with optional context and arguments."""
        raise NotImplementedError


class Validatable(Protocol):
    """Protocol for tools that can validate inputs."""
    
    @abstractmethod
    def validate(self, input_data: Any) -> bool:
        """Validate input data against tool requirements."""
        return False
    
    @property
    @abstractmethod
    def validation_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for validation."""
        return {}


class Configurable(Protocol):
    """Protocol for tools that support configuration."""
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the tool with the provided settings."""
        pass
    
    @property
    @abstractmethod
    def configured_options(self) -> Dict[str, Any]:
        """Return currently configured options."""
        return {}


# =============================================================================
# TOOL RESULTS
# =============================================================================

class ExecutionStatus(Enum):
    """Possible statuses for tool execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ToolResult:
    """Immutable result from tool execution."""
    status: ExecutionStatus
    output: str = ""
    error_output: str = ""
    exit_code: Optional[int] = None
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: List["ToolArtifact"] = field(default_factory=list)
    
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS
    
    def is_failure(self) -> bool:
        """Check if execution failed."""
        return self.status in (
            ExecutionStatus.FAILURE,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.CANCELLED,
        )
    
    @classmethod
    def success(cls, output: str = "", **kwargs: Any) -> "ToolResult":
        """Create a successful result."""
        return cls(status=ExecutionStatus.SUCCESS, output=output, **kwargs)
    
    @classmethod
    def failure(cls, error_output: str = "", exit_code: int = 1, **kwargs: Any) -> "ToolResult":
        """Create a failed result."""
        return cls(
            status=ExecutionStatus.FAILURE,
            error_output=error_output,
            exit_code=exit_code,
            **kwargs,
        )


@dataclass(frozen=True)
class ToolArtifact:
    """A file or data artifact produced by tool execution."""
    name: str
    path: Optional[str] = None
    content: Optional[Any] = None
    mime_type: str = "text/plain"
    checksum: Optional[str] = None


# =============================================================================
# BUILD PIPELINE CONTRACTS
# =============================================================================

class BuildStage(Enum):
    """Phases of a build pipeline."""
    PREPARE = "prepare"
    ANALYZE = "analyze"
    COMPILE = "compile"
    TEST = "test"
    PACKAGE = "package"
    PUBLISH = "publish"


@dataclass(frozen=True)
class BuildPipelineStep:
    """A single step in the build pipeline."""
    name: str
    stage: BuildStage
    command: List[str]
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    timeout_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "stage": self.stage.value,
            "command": self.command,
            "description": self.description,
            "dependencies": self.dependencies,
            "outputs": self.outputs,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class BuildPipelineConfig:
    """Configuration for a build pipeline."""
    name: str
    description: str = ""
    default_stage: BuildStage = BuildStage.TEST
    steps: List[BuildPipelineStep] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    
    def get_steps_by_stage(self, stage: BuildStage) -> List[BuildPipelineStep]:
        """Get all steps for a specific stage."""
        return [step for step in self.steps if step.stage == stage]


# =============================================================================
# QUALITY GATE CONTRACTS
# =============================================================================

class GateLevel(Enum):
    """Quality gate severity levels."""
    OPTIONAL = "optional"
    WARNING = "warning"
    CRITICAL = "critical"
    MANDATORY = "mandatory"


@dataclass(frozen=True)
class QualityGateResult:
    """Result of a quality gate check."""
    gate_name: str
    passed: bool
    details: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    
    @classmethod
    def pass_gate(cls, gate_name: str, **kwargs: Any) -> "QualityGateResult":
        """Create a passing gate result."""
        return cls(gate_name=gate_name, passed=True, **kwargs)
    
    @classmethod
    def fail_gate(cls, gate_name: str, details: Optional[List[str]] = None, **kwargs: Any) -> "QualityGateResult":
        """Create a failing gate result."""
        return cls(gate_name=gate_name, passed=False, details=details or [], **kwargs)


@dataclass(frozen=True)
class QualityGateConfig:
    """Configuration for a quality gate."""
    name: str
    level: GateLevel = GateLevel.MANDATORY
    enabled: bool = True
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "level": self.level.value,
            "enabled": self.enabled,
            "conditions": self.conditions,
        }


# =============================================================================
# REPORTING CONTRACTS
# =============================================================================

@dataclass(frozen=True)
class ReportMetadata:
    """Metadata for a report."""
    tool_name: str
    execution_id: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    duration_seconds: float = 0.0
    version: str = "1.0.0"
    
    @classmethod
    def create(cls, tool_name: str, execution_id: Optional[str] = None) -> "ReportMetadata":
        """Create report metadata."""
        return cls(tool_name=tool_name, execution_id=execution_id or "")


@dataclass(frozen=True)
class Report:
    """Immutable report structure."""
    metadata: ReportMetadata
    status: ExecutionStatus
    summary: str = ""
    details: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "metadata": {
                "tool_name": self.metadata.tool_name,
                "execution_id": self.metadata.execution_id,
                "timestamp": self.metadata.timestamp.isoformat(),
                "duration_seconds": self.metadata.duration_seconds,
                "version": self.metadata.version,
            },
            "status": self.status.value,
            "summary": self.summary,
            "details": self.details,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
        }


# =============================================================================
# EXTENSION POINTS
# =============================================================================

class ExtensionPoint(Protocol):
    """Protocol for extension points in the tooling system."""
    
    @abstractmethod
    def register_extension(self, name: str, extension: Any) -> bool:
        """Register an extension by name."""
        return False
    
    @abstractmethod
    def get_extension(self, name: str) -> Optional[Any]:
        """Get a registered extension."""
        return None
    
    @abstractmethod
    def list_extensions(self) -> List[str]:
        """List all registered extension names."""
        return []
    
    @abstractmethod
    def remove_extension(self, name: str) -> bool:
        """Remove an extension by name."""
        return False


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

__all__ = [
    # Versioning & Metadata
    "ToolVersion",
    "ToolMetadata",
    "ToolDependency",
    
    # Execution Context
    "ToolExecutionContext",
    
    # Tool Contracts
    "Tool",
    "Validatable",
    "Configurable",
    
    # Results
    "ExecutionStatus",
    "ToolResult",
    "ToolArtifact",
    
    # Build Pipeline
    "BuildStage",
    "BuildPipelineStep",
    "BuildPipelineConfig",
    
    # Quality Gates
    "GateLevel",
    "QualityGateResult",
    "QualityGateConfig",
    
    # Reporting
    "ReportMetadata",
    "Report",
    
    # Extension Points
    "ExtensionPoint",
]