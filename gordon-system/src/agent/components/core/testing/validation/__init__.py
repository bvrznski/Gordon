# Validation Subpackage - Testing Infrastructure
# ==============================================

"""
Validation subpackage for source, configuration, and artifact validation.

This module provides validation authorities per domain:
- SourceValidator: Validates source code compilation and syntax
- ConfigValidator: Validates configuration files and schemas
- ImportValidator: Validates imports for side effects and cycles
- PackageValidator: Validates package structure and exports
- APIDocValidator: Validates API documentation
"""

from .source import (
    SourceValidator,
    validate_source_code,
    check_syntax_errors,
    analyze_imports,
)

from .imports import (
    ImportValidator,
    check_import_cycles,
    detect_side_effects,
    validate_import_paths,
)

from .packages import (
    PackageValidator,
    validate_package_structure,
    verify_exports,
    check_module_visibility,
)

from .api import (
    APIDocValidator,
    validate_public_api,
    check_stability_annotations,
    verify_example_code,
)

from .documentation import (
    DocumentationValidator,
    validate_docstrings,
    check_readme_commands,
    validate_mermaid_syntax,
)

from .artifacts import (
    ArtifactValidator,
    validate_wheel_artifact,
    validate_source_distribution,
    verify_checksums,
)

from .release import (
    ReleaseValidator,
    validate_release_notes,
    check_changelog_completeness,
    verify_migration_paths,
)

# Backward compatibility aliases for Coordinator imports
ValidationManager = None  # To be implemented in coordination with coordinator.py
ConfigValidator = None  # To be implemented

__all__ = [
    # Source validation
    "SourceValidator",
    "validate_source_code",
    "check_syntax_errors",
    "analyze_imports",
    
    # Import validation
    "ImportValidator",
    "check_import_cycles",
    "detect_side_effects",
    "validate_import_paths",
    
    # Package validation
    "PackageValidator",
    "validate_package_structure",
    "verify_exports",
    "check_module_visibility",
    
    # API validation
    "APIDocValidator",
    "validate_public_api",
    "check_stability_annotations",
    "verify_example_code",
    
    # Documentation validation
    "DocumentationValidator",
    "validate_docstrings",
    "check_readme_commands",
    "validate_mermaid_syntax",
    
    # Artifact validation
    "ArtifactValidator",
    "validate_wheel_artifact",
    "validate_source_distribution",
    "verify_checksums",
    
    # Release validation
    "ReleaseValidator",
    "validate_release_notes",
    "check_changelog_completeness",
    "verify_migration_paths",
]
