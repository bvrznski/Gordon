# Development Tooling Taxonomy
# ==============================
"""
Tooling taxonomy defines the canonical abstractions and categories for
development tools in Gordon.

This module establishes a consistent classification system for all development
tooling, enabling discovery, composition, and management of engineering
artifacts.

ARCHITECTURAL PRINCIPLES:
- Each abstraction has one canonical owner
- Tools are categorized by function, not implementation
- Taxonomy supports extensibility without duplication
- All tool categories map to concrete engineering workflows
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
    Callable,
    Tuple,
)
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


# =============================================================================
# TOOL CATEGORIES & ABSTRACTIONS
# =============================================================================

class ToolCategory(Enum):
    """High-level categories for development tools."""
    # Build & Deployment
    BUILD = "build"
    DEPLOY = "deploy"
    
    # Code Quality
    LINT = "lint"
    FORMAT = "format"
    VALIDATE = "validate"
    
    # Testing
    TEST = "test"
    COVERAGE = "coverage"
    
    # Documentation
    DOCUMENT = "document"
    GENERATE = "generate"
    
    # Maintenance
    MIGRATE = "migrate"
    CLEANUP = "cleanup"
    ANALYZE = "analyze"
    
    # Release Management
    RELEASE = "release"
    VERSION = "version"
    
    # CI/CD & Automation
    CI = "ci"
    CD = "cd"
    AUTOMATE = "automate"


@dataclass(frozen=True)
class ToolAbstraction:
    """Canonical abstraction for a type of development tool."""
    name: str
    category: ToolCategory
    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)


# =============================================================================
# TOOL REGISTRY & DISCOVERY
# =============================================================================

class ToolRegistry(Protocol):
    """Protocol for tool registration and discovery."""
    
    @abstractmethod
    def register(self, name: str, tool_class: Any) -> bool:
        """Register a tool class by name."""
        ...
    
    @abstractmethod
    def get(self, name: str) -> Optional[Any]:
        """Get a registered tool class."""
        ...
    
    @abstractmethod
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        ...
    
    @abstractmethod
    def unregister(self, name: str) -> bool:
        """Unregister a tool by name."""
        ...


# =============================================================================
# BUILD PIPELINE ABSTRACTIONS
# =============================================================================

class BuildPipeline(Protocol):
    """Protocol for build pipelines."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Pipeline name."""
        ...
    
    @abstractmethod
    def add_stage(
        self,
        stage_name: str,
        commands: List[str],
        dependencies: Optional[List[str]] = None,
    ) -> "BuildPipeline":
        """Add a stage to the pipeline."""
        ...
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the build pipeline."""
        ...
    
    @abstractmethod
    def dry_run(self, **kwargs: Any) -> Dict[str, Any]:
        """Simulate pipeline execution without changes."""
        ...


# =============================================================================
# QUALITY GATE ABSTRACTIONS
# =============================================================================

class QualityGate(Protocol):
    """Protocol for quality gates."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Gate name."""
        ...
    
    @property
    @abstractmethod
    def level(self) -> "GateLevel":
        """Gate severity level."""
        ...
    
    @abstractmethod
    def check(self, **kwargs: Any) -> bool:
        """Execute the quality gate check."""
        ...
    
    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """Get detailed results from the last check."""
        ...


class GateLevel(Enum):
    """Quality gate severity levels."""
    OPTIONAL = "optional"
    WARNING = "warning"
    CRITICAL = "critical"
    MANDATORY = "mandatory"


# =============================================================================
# MAINTENANCE TASK ABSTRACTIONS
# =============================================================================

class MaintenanceTask(Protocol):
    """Protocol for maintenance tasks."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Task name."""
        ...
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Task description."""
        ...
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> bool:
        """Execute the maintenance task."""
        ...
    
    @abstractmethod
    def validate_prerequisites(self) -> bool:
        """Check if prerequisites are met."""
        ...


class CodeGenerator(Protocol):
    """Protocol for code generators."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Generator name."""
        ...
    
    @abstractmethod
    def generate(
        self,
        output_path: str,
        template_context: Dict[str, Any],
    ) -> str:
        """Generate code to the specified path."""
        ...
    
    @abstractmethod
    def validate_template(self, context: Dict[str, Any]) -> bool:
        """Validate that the template context is valid."""
        ...


# =============================================================================
# DEVELOPER CONTEXT ABSTRACTIONS
# =============================================================================

@dataclass(frozen=True)
class DeveloperContext:
    """Immutable context for developer tool execution."""
    project_root: str
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    user: Optional[str] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def from_environment(cls) -> "DeveloperContext":
        """Create context from current environment."""
        import os
        
        return cls(
            project_root=os.getcwd(),
            environment=dict(os.environ),
        )


# =============================================================================
# ENGINEERING ARTIFACT ABSTRACTIONS
# =============================================================================

class EngineeringArtifact(Protocol):
    """Protocol for engineering artifacts (build outputs, reports, etc.)."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Artifact name."""
        ...
    
    @property
    @abstractmethod
    def artifact_type(self) -> str:
        """Type of artifact (e.g., 'build', 'report', 'test-report')."""
        ...
    
    @property
    @abstractmethod
    def path(self) -> Optional[str]:
        """File system path to the artifact."""
        ...
    
    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Artifact metadata (version, timestamp, etc.)."""
        ...
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate artifact integrity."""
        ...


# =============================================================================
# TOOL EXECUTION ABSTRACTIONS
# =============================================================================

class ToolExecution(Protocol):
    """Protocol for tool execution results and tracking."""
    
    @property
    @abstractmethod
    def execution_id(self) -> str:
        """Unique execution identifier."""
        ...
    
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Name of the executed tool."""
        ...
    
    @property
    @abstractmethod
    def status(self) -> "ExecutionStatus":
        """Execution status."""
        ...
    
    @property
    @abstractmethod
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        ...
    
    @property
    @abstractmethod
    def output(self) -> str:
        """Standard output from execution."""
        ...
    
    @property
    @abstractmethod
    def error_output(self) -> str:
        """Error output from execution."""
        ...


class ExecutionStatus(Enum):
    """Status of tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


# =============================================================================
# REPORT ABSTRACTIONS
# =============================================================================

@dataclass(frozen=True)
class ToolReport:
    """Immutable report from tool execution."""
    report_id: str
    tool_name: str
    timestamp: str
    status: ExecutionStatus
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(cls, tool_name: str, summary: str, **kwargs: Any) -> "ToolReport":
        """Create a successful report."""
        return cls(
            report_id=str(uuid.uuid4()),
            tool_name=tool_name,
            timestamp=str(uuid.uuid4())[:8],
            status=ExecutionStatus.SUCCESS,
            summary=summary,
            details=kwargs,
        )
    
    @classmethod
    def failure(cls, tool_name: str, error_message: str, **kwargs: Any) -> "ToolReport":
        """Create a failed report."""
        return cls(
            report_id=str(uuid.uuid4()),
            tool_name=tool_name,
            timestamp=str(uuid.uuid4())[:8],
            status=ExecutionStatus.FAILURE,
            summary=error_message,
            details=kwargs,
        )


# =============================================================================
# VALIDATION TOOL ABSTRACTIONS
# =============================================================================

class ValidationTool(Protocol):
    """Protocol for validation tools."""
    
    @abstractmethod
    def validate(
        self,
        input_data: Any,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, List[str]]:
        """Validate input data against a schema or default rules.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        ...
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the validation schema being used."""
        ...


# =============================================================================
# MIGRATION TASK ABSTRACTIONS
# =============================================================================

class MigrationTask(Protocol):
    """Protocol for migration tasks."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Migration task name."""
        ...
    
    @property
    @abstractmethod
    def from_version(self) -> str:
        """Source version for the migration."""
        ...
    
    @property
    @abstractmethod
    def to_version(self) -> str:
        """Target version for the migration."""
        ...
    
    @abstractmethod
    def execute(self, **kwargs: Any) -> bool:
        """Execute the migration."""
        ...
    
    @abstractmethod
    def rollback(self, **kwargs: Any) -> bool:
        """Rollback the migration if supported."""
        ...


# =============================================================================
# DOCUMENTATION GENERATOR ABSTRACTIONS
# =============================================================================

class DocumentationGenerator(Protocol):
    """Protocol for documentation generators."""
    
    @property
    @abstractmethod
    def output_format(self) -> str:
        """Output format (e.g., 'html', 'markdown', 'pdf')."""
        ...
    
    @abstractmethod
    def generate(
        self,
        source_files: List[str],
        output_path: str,
        **kwargs: Any,
    ) -> EngineeringArtifact:
        """Generate documentation from source files."""
        ...
    
    @abstractmethod
    def validate_source(self, file_path: str) -> bool:
        """Validate that a source file can be processed."""
        ...


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

__all__ = [
    # Tool Categories
    "ToolCategory",
    
    # Abstractions
    "ToolAbstraction",
    "ToolRegistry",
    "BuildPipeline",
    "QualityGate",
    "MaintenanceTask",
    "CodeGenerator",
    "DeveloperContext",
    "EngineeringArtifact",
    "ToolExecution",
    "ToolReport",
    "ValidationTool",
    "MigrationTask",
    "DocumentationGenerator",
    
    # Enums
    "GateLevel",
    "ExecutionStatus",
]