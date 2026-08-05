# Development, Tooling & Maintenance Infrastructure
# ==================================================
"""
Phase 3.8.9 - Development Infrastructure Foundation

This package provides the canonical foundation for development tooling,
build automation, quality assurance, maintenance workflows, developer
utilities, repository hygiene and engineering contracts.

ARCHITECTURAL PRINCIPLES:
- Tooling is deterministic (same inputs always produce same outputs)
- Build processes are reproducible (anyone can reproduce artifacts)
- Developer utilities never bypass Core contracts
- Maintenance workflows are automated where practical
- Tool interfaces are stable and documented
- Repository hygiene is continuously enforced
- Quality gates are explicit
- Duplicate tooling is prohibited
- All engineering actions are auditable

PACKAGE STRUCTURE:
    core/development/
        __init__.py         This file - module exports
        exceptions.py       Exception hierarchy for tooling errors
        contracts.py        Tool contracts and interfaces
        taxonomy.py         Tooling taxonomy and abstractions
        registry.py         Tool registry and discovery
        build/              Build system infrastructure
        cicd/               CI/CD pipeline framework
        validation/         Validation pipelines
        migration/          Migration workflows
        maintenance/        Maintenance automation
        documentation/      Documentation tools
        utilities/          Developer utilities
        orchestration/      Development orchestration

PHASES:
    3.8.9.1   Foundations, model & contracts (this phase)
    3.8.9.2   Build system, toolchain, CI/CD & repository automation
    3.8.9.3   Code generation, validation, migration & maintenance
    3.8.9.4   Documentation, DX & engineering utilities
    3.8.9.5   Runtime integration, quality gates & orchestration
    3.8.9.6   Testing, certification & final audit

See docs/agent/architecture/phase-3.8.9.* for detailed specifications.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.development import exceptions, contracts, taxonomy, registry

# Import submodules
from . import exceptions
from . import contracts
from . import taxonomy
from . import registry
from . import build
from . import cicd
from . import validation
from . import migration
from . import maintenance
from . import documentation
from . import utilities
from . import orchestration

# Re-export exception classes
from .exceptions import (
    ToolingError,
    BuildError,
    BuildPipelineError,
    ToolchainError,
    DependencyError,
    ValidationError,
    QualityGateError,
    ArchitectureValidationError,
    MigrationError,
    MigrationWorkflowError,
    CompatibilityMigrationError,
    CodeGenerationError,
    TemplateError,
    MaintenanceError,
    RepositoryError,
    DocumentationError,
    DocumentationGenerationError,
    DeveloperToolError,
    OrchestrationError,
    QualityGateExecutionError,
)

# Re-export contract classes
from .contracts import (
    ToolVersion,
    ToolMetadata,
    ToolDependency,
    ToolExecutionContext,
    Tool,
    Validatable,
    Configurable,
    ExecutionStatus,
    ToolResult,
    ToolArtifact,
    BuildStage,
    BuildPipelineStep,
    BuildPipelineConfig,
    GateLevel,
    QualityGateResult,
    QualityGateConfig,
    ReportMetadata,
    Report,
)

# Re-export registry classes
from .registry import (
    ToolEntry,
    RegistryState,
    ToolRegistry,
    ToolRegistryBuilder,
)

# Re-export taxonomy classes
from .taxonomy import (
    ToolCategory,
    ToolAbstraction,
    DeveloperContext,
    ExecutionStatus as TaxonomyExecutionStatus,
    GateLevel as TaxonomyGateLevel,
    ToolReport,
)

__all__ = [
    "exceptions",
    "contracts", 
    "taxonomy",
    "registry",
    # Subpackages
    "build",
    "cicd",
    "validation",
    "migration",
    "maintenance",
    "documentation",
    "utilities",
    "orchestration",
    # Exception classes
    "ToolingError",
    "BuildError",
    "BuildPipelineError",
    "ToolchainError",
    "DependencyError",
    "ValidationError",
    "QualityGateError",
    "ArchitectureValidationError",
    "MigrationError",
    "MigrationWorkflowError",
    "CompatibilityMigrationError",
    "CodeGenerationError",
    "TemplateError",
    "MaintenanceError",
    "RepositoryError",
    "DocumentationError",
    "DocumentationGenerationError",
    "DeveloperToolError",
    "OrchestrationError",
    "QualityGateExecutionError",
    # Contract classes
    "ToolVersion",
    "ToolMetadata",
    "ToolDependency",
    "ToolExecutionContext",
    "Tool",
    "Validatable",
    "Configurable",
    "ExecutionStatus",
    "ToolResult",
    "ToolArtifact",
    "BuildStage",
    "BuildPipelineStep",
    "BuildPipelineConfig",
    "GateLevel",
    "QualityGateResult",
    "QualityGateConfig",
    "ReportMetadata",
    "Report",
    # Registry classes
    "ToolEntry",
    "RegistryState",
    "ToolRegistry",
    "ToolRegistryBuilder",
    # Taxonomy classes
    "ToolCategory",
    "ToolAbstraction",
    "DeveloperContext",
    "TaxonomyExecutionStatus",
    "TaxonomyGateLevel",
    "ToolReport",
]