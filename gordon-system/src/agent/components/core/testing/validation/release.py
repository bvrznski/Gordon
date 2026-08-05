# Release Validation - Testing Infrastructure
# ==========================================

"""
Release validation for release notes, changelogs, and migration paths.

The ReleaseValidator ensures that:
1. Release notes are complete and accurate
2. Changelog entries follow conventions
3. Migration paths are documented and tested
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path


@dataclass(frozen=True)
class ReleaseValidationError:
    """Immutable error descriptor for release validation failures."""
    
    path: str
    issue_type: str  # missing_entry, invalid_format, etc.
    description: str
    severity: str = "warning"
    
    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "issue_type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class ReleaseValidationResult:
    """Immutable result of release validation."""
    
    release_files_checked: int
    files_with_issues: List[ReleaseValidationError]
    changelog_entries: int
    migration_paths_documented: bool
    duration_seconds: float
    
    @property
    def is_valid(self) -> bool:
        """Check if all release validation passed."""
        critical_errors = [
            err for err in self.files_with_issues 
            if err.severity == "error"
        ]
        return len(critical_errors) == 0


class ReleaseValidator:
    """
    Validates release artifacts and documentation.
    
    This validator performs:
    - Release notes completeness checking
    - Changelog format validation
    - Migration path documentation verification
    """
    
    def __init__(self, docs_path: str = "docs"):
        """
        Initialize the release validator.
        
        Args:
            docs_path: Path to the documentation directory
        """
        self.docs_path = Path(docs_path)
    
    def validate_release_notes(self) -> List[ReleaseValidationError]:
        """
        Validate release notes completeness and format.
        
        Returns:
            List of validation errors found
        """
        errors: List[ReleaseValidationError] = []
        
        # Check for common release note locations
        release_note_paths = [
            self.docs_path / "RELEASE.md",
            self.docs_path / "release-notes.md",
            Path("CHANGELOG.md"),
            Path("CHANGES.md"),
        ]
        
        found_notes = False
        
        for path in release_note_paths:
            if path.exists():
                found_notes = True
                
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Check for basic sections
                    required_sections = [
                        "# Release",
                        "## Changes",
                        "### Breaking Changes",
                        "### Bug Fixes",
                        "### Features",
                    ]
                    
                    missing_sections = [
                        section 
                        for section in required_sections 
                        if section not in content
                    ]
                    
                    for section in missing_sections:
                        errors.append(
                            ReleaseValidationError(
                                path=str(path),
                                issue_type="missing_section",
                                description=f"Missing release note section: {section}",
                                severity="warning",
                            )
                        )
                
                except Exception as e:
                    errors.append(
                        ReleaseValidationError(
                            path=str(path),
                            issue_type="read_error",
                            description=f"Failed to read release notes: {e}",
                            severity="error",
                        )
                    )
        
        if not found_notes:
            errors.append(
                ReleaseValidationError(
                    path=str(self.docs_path),
                    issue_type="missing_release_notes",
                    description="No release notes file found in expected locations",
                    severity="warning",
                )
            )
        
        return errors
    
    def validate_changelog(self) -> List[ReleaseValidationError]:
        """
        Validate changelog format and entries.
        
        Returns:
            List of validation errors found
        """
        errors: List[ReleaseValidationError] = []
        
        changelog_paths = [
            self.docs_path / "CHANGELOG.md",
            Path("CHANGELOG.md"),
            Path("HISTORY.md"),
        ]
        
        for path in changelog_paths:
            if not path.exists():
                continue
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Count version entries
                import re
                
                # Look for version headers (## v1.0.0, ## 1.0.0, etc.)
                version_pattern = r"##\s*[vV]?\d+\.\d+\.\d+"
                versions_found = len(re.findall(version_pattern, content))
                
                if versions_found == 0:
                    errors.append(
                        ReleaseValidationError(
                            path=str(path),
                            issue_type="no_versions",
                            description="No version entries found in changelog",
                            severity="warning",
                        )
                    )
                
                # Check for entry format (bullet list)
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if re.match(version_pattern, line):
                        # Next non-empty line should be an entry
                        next_lines = [
                            l for l in lines[i+1:i+5]
                            if l.strip() and not l.strip().startswith("#")
                        ]
                        
                        if next_lines:
                            first_entry = next_lines[0].strip()
                            
                            if not (first_entry.startswith("-") or first_entry.startswith("*")):
                                errors.append(
                                    ReleaseValidationError(
                                        path=str(path),
                                        issue_type="invalid_entry_format",
                                        description=f"Changelog entry should start with bullet: {first_entry[:50]}",
                                        severity="info",
                                    )
                                )
            
            except Exception as e:
                errors.append(
                    ReleaseValidationError(
                        path=str(path),
                        issue_type="read_error",
                        description=f"Failed to read changelog: {e}",
                        severity="error",
                    )
                )
        
        return errors
    
    def validate_migration_paths(self) -> bool:
        """
        Validate that migration paths are documented.
        
        Returns:
            True if migration documentation exists, False otherwise
        """
        migration_doc_paths = [
            self.docs_path / "MIGRATION.md",
            self.docs_path / "migration-guide.md",
            Path("MIGRATION.md"),
            Path("UPGRADE.md"),
        ]
        
        return any(path.exists() for path in migration_doc_paths)
    
    def validate_all(self) -> ReleaseValidationResult:
        """
        Perform all release validations.
        
        Returns:
            ReleaseValidationResult with validation results
        """
        import time
        
        start_time = time.time()
        
        release_errors = self.validate_release_notes()
        changelog_errors = self.validate_changelog()
        migration_documented = self.validate_migration_paths()
        
        all_errors = release_errors + changelog_errors
        
        return ReleaseValidationResult(
            release_files_checked=2,  # Release notes + changelog
            files_with_issues=all_errors,
            changelog_entries=0,  # Would need actual parsing to count
            migration_paths_documented=migration_documented,
            duration_seconds=time.time() - start_time,
        )


def validate_release_notes(docs_path: str = "docs") -> List[ReleaseValidationError]:
    """Validate release notes."""
    validator = ReleaseValidator(docs_path)
    return validator.validate_release_notes()


def check_changelog_completeness(docs_path: str = "docs") -> List[ReleaseValidationError]:
    """Check changelog completeness and format."""
    validator = ReleaseValidator(docs_path)
    return validator.validate_changelog()


def verify_migration_paths(docs_path: str = "docs") -> bool:
    """Verify migration paths are documented."""
    validator = ReleaseValidator(docs_path)
    return validator.validate_migration_paths()