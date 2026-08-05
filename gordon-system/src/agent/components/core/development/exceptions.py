# Development Tooling Exception Hierarchy
# =========================================
"""
Exception hierarchy for Development, Tooling & Maintenance Infrastructure.

This module defines all exception types used throughout the development
tooling system: build errors, validation failures, migration issues,
code generation problems, and more.

ARCHITECTURAL PRINCIPLES:
- All exceptions extend CoreError or appropriate base classes
- Exceptions preserve cause chains for debugging
- Structured error data provides actionable information
- Error types map to failure modes in the engineering workflow
"""
from typing import Optional, List, Any, Dict
from ..exceptions import CoreError


# =============================================================================
# TOOLING ERRORS (Base class for all tooling-related errors)
# =============================================================================

class ToolingError(CoreError):
    """Base exception for all development tooling errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        tool_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, cause=cause)
        self.tool_name = tool_name


# =============================================================================
# BUILD ERRORS (Build system failures)
# =============================================================================

class BuildError(ToolingError):
    """Base exception for build system errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        build_step: Optional[str] = None,
        stage: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="build", cause=cause)
        self.build_step = build_step
        self.stage = stage


class BuildPipelineError(BuildError):
    """Raised when the build pipeline fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        failed_step: Optional[str] = None,
        pipeline_stages: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, build_step="pipeline", cause=cause)
        self.failed_step = failed_step
        self.pipeline_stages = pipeline_stages or []


class ToolchainError(ToolingError):
    """Raised when toolchain operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        tool_name: Optional[str] = None,
        version: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name=tool_name or "toolchain", cause=cause)
        self.version = version


class DependencyError(ToolingError):
    """Raised when dependency management fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        missing_dependency: Optional[str] = None,
        conflict_version: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="dependencies", cause=cause)
        self.missing_dependency = missing_dependency
        self.conflict_version = conflict_version


# =============================================================================
# VALIDATION ERRORS (Quality gate and validation failures)
# =============================================================================

class ValidationError(ToolingError):
    """Base exception for validation failures."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        validator_name: Optional[str] = None,
        failed_checks: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="validation", cause=cause)
        self.validator_name = validator_name
        self.failed_checks = failed_checks or []


class QualityGateError(ToolingError):
    """Raised when a quality gate check fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        gate_name: Optional[str] = None,
        gate_level: Optional[str] = None,
        failed_criteria: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="quality-gate", cause=cause)
        self.gate_name = gate_name
        self.gate_level = gate_level
        self.failed_criteria = failed_criteria or []


class ArchitectureValidationError(ToolingError):
    """Raised when architecture validation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        rule_violated: Optional[str] = None,
        affected_components: Optional[List[str]] = None,
        severity: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="architecture-validation", cause=cause)
        self.rule_violated = rule_violated
        self.affected_components = affected_components or []
        self.severity = severity


# =============================================================================
# MIGRATION ERRORS (Migration workflow failures)
# =============================================================================

class MigrationError(ToolingError):
    """Base exception for migration workflow errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        migration_type: Optional[str] = None,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="migration", cause=cause)
        self.migration_type = migration_type
        self.from_version = from_version
        self.to_version = to_version


class MigrationWorkflowError(MigrationError):
    """Raised when migration workflow execution fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        step_failed: Optional[str] = None,
        rollback_available: bool = False,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, migration_type="workflow", cause=cause)
        self.step_failed = step_failed
        self.rollback_available = rollback_available


class CompatibilityMigrationError(MigrationError):
    """Raised when compatibility migration fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        incompatible_component: Optional[str] = None,
        required_version: Optional[str] = None,
        current_version: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, migration_type="compatibility", cause=cause)
        self.incompatible_component = incompatible_component
        self.required_version = required_version
        self.current_version = current_version


# =============================================================================
# CODE GENERATION ERRORS (Generation failures)
# =============================================================================

class CodeGenerationError(ToolingError):
    """Raised when code generation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        generator_name: Optional[str] = None,
        template_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="codegen", cause=cause)
        self.generator_name = generator_name
        self.template_type = template_type


class TemplateError(ToolingError):
    """Raised when template processing fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        template_name: Optional[str] = None,
        missing_variable: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="template", cause=cause)
        self.template_name = template_name
        self.missing_variable = missing_variable


# =============================================================================
# MAINTENANCE ERRORS (Maintenance workflow failures)
# =============================================================================

class MaintenanceError(ToolingError):
    """Base exception for maintenance workflow errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        task_name: Optional[str] = None,
        task_type: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="maintenance", cause=cause)
        self.task_name = task_name
        self.task_type = task_type


class RepositoryError(ToolingError):
    """Raised when repository operations fail."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        operation: Optional[str] = None,
        repository_path: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="repository", cause=cause)
        self.operation = operation
        self.repository_path = repository_path


# =============================================================================
# DOCUMENTATION ERRORS (Documentation generation failures)
# =============================================================================

class DocumentationError(ToolingError):
    """Base exception for documentation errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        doc_type: Optional[str] = None,
        document_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="documentation", cause=cause)
        self.doc_type = doc_type
        self.document_name = document_name


class DocumentationGenerationError(DocumentationError):
    """Raised when documentation generation fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        format_failed: Optional[str] = None,
        source_files: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, doc_type="generation", cause=cause)
        self.format_failed = format_failed
        self.source_files = source_files or []


# =============================================================================
# DEVELOPER TOOL ERRORS (Developer utility failures)
# =============================================================================

class DeveloperToolError(ToolingError):
    """Base exception for developer tool errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        tool_name: Optional[str] = None,
        command_executed: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name=tool_name or "developer-tool", cause=cause)
        self.command_executed = command_executed


# =============================================================================
# ORCHESTRATION ERRORS (Workflow coordination failures)
# =============================================================================

class OrchestrationError(ToolingError):
    """Base exception for orchestration errors."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        workflow_name: Optional[str] = None,
        stage_failed: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, tool_name="orchestration", cause=cause)
        self.workflow_name = workflow_name
        self.stage_failed = stage_failed


class QualityGateExecutionError(OrchestrationError):
    """Raised when quality gate execution fails."""
    
    def __init__(
        self,
        message: str,
        *args: object,
        gate_name: Optional[str] = None,
        gates_passed: Optional[List[str]] = None,
        gates_failed: Optional[List[str]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, *args, workflow_name="quality-gates", stage_failed=gate_name, cause=cause)
        self.gate_name = gate_name
        self.gates_passed = gates_passed or []
        self.gates_failed = gates_failed or []


# =============================================================================
# UTILITY EXPORTS
# =============================================================================

__all__ = [
    # Base classes
    "ToolingError",
    
    # Build errors
    "BuildError",
    "BuildPipelineError",
    "ToolchainError",
    "DependencyError",
    
    # Validation errors
    "ValidationError",
    "QualityGateError",
    "ArchitectureValidationError",
    
    # Migration errors
    "MigrationError",
    "MigrationWorkflowError",
    "CompatibilityMigrationError",
    
    # Code generation errors
    "CodeGenerationError",
    "TemplateError",
    
    # Maintenance errors
    "MaintenanceError",
    "RepositoryError",
    
    # Documentation errors
    "DocumentationError",
    "DocumentationGenerationError",
    
    # Developer tool errors
    "DeveloperToolError",
    
    # Orchestration errors
    "OrchestrationError",
    "QualityGateExecutionError",
]