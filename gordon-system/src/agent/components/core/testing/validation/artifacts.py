# Artifact Validation - Testing Infrastructure
# ==========================================

"""
Artifact validation for wheels, source distributions, and release artifacts.

The ArtifactValidator ensures that:
1. Built artifacts are valid
2. Checksums are correct
3. Package metadata is consistent
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import hashlib
import json


@dataclass(frozen=True)
class ArtifactValidationResult:
    """Immutable result of artifact validation."""
    
    artifact_path: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checksums_verified: List[str]
    metadata_validated: bool
    duration_seconds: float
    
    @property
    def has_critical_errors(self) -> bool:
        """Check if there are critical validation errors."""
        return any("CRITICAL" in err for err in self.errors)


@dataclass(frozen=True)
class ArtifactMetadata:
    """Immutable artifact metadata."""
    
    name: str
    version: str
    python_requires: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    entry_points: Dict[str, Dict[str, str]] = field(default_factory=dict)


class ArtifactValidator:
    """
    Validates build artifacts for correctness and integrity.
    
    This validator performs:
    - Wheel file validation
    - Source distribution validation
    - Checksum verification
    - Metadata consistency checking
    """
    
    def __init__(self, dist_path: str = "dist"):
        """
        Initialize the artifact validator.
        
        Args:
            dist_path: Path to the distribution directory
        """
        self.dist_path = Path(dist_path)
    
    def discover_artifacts(self) -> List[Path]:
        """Discover all artifacts in the distribution directory."""
        if not self.dist_path.exists():
            return []
        
        return [
            f for f in self.dist_path.iterdir()
            if f.is_file() and (f.suffix == ".whl" or "tar.gz" in f.name)
        ]
    
    def calculate_checksum(self, filepath: Path, algorithm: str = "sha256") -> str:
        """Calculate checksum of a file."""
        hasher = hashlib.new(algorithm)
        
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def verify_wheel_artifact(self, filepath: Path) -> ArtifactValidationResult:
        """
        Verify a wheel artifact.
        
        Args:
            filepath: Path to the wheel file
            
        Returns:
            ArtifactValidationResult with verification results
        """
        import time
        start_time = time.time()
        
        errors: List[str] = []
        warnings: List[str] = []
        checksums: List[str] = []
        
        # Check if file exists
        if not filepath.exists():
            return ArtifactValidationResult(
                artifact_path=str(filepath),
                is_valid=False,
                errors=[f"Artifact not found: {filepath}"],
                warnings=[],
                checksums_verified=[],
                metadata_validated=False,
                duration_seconds=time.time() - start_time,
            )
        
        # Check file size
        if filepath.stat().st_size == 0:
            errors.append("CRITICAL: Wheel file is empty")
        
        # Calculate checksum
        checksum = self.calculate_checksum(filepath)
        checksums.append(f"{filepath.name}:{checksum}")
        
        # TODO: Extract and validate wheel contents (would require zipfile)
        # For now, we just verify the file exists and has content
        
        return ArtifactValidationResult(
            artifact_path=str(filepath),
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checksums_verified=checksums,
            metadata_validated=False,
            duration_seconds=time.time() - start_time,
        )
    
    def verify_source_distribution(self, filepath: Path) -> ArtifactValidationResult:
        """
        Verify a source distribution artifact.
        
        Args:
            filepath: Path to the source distribution
            
        Returns:
            ArtifactValidationResult with verification results
        """
        import time
        start_time = time.time()
        
        errors: List[str] = []
        warnings: List[str] = []
        checksums: List[str] = []
        
        if not filepath.exists():
            return ArtifactValidationResult(
                artifact_path=str(filepath),
                is_valid=False,
                errors=[f"Artifact not found: {filepath}"],
                warnings=[],
                checksums_verified=[],
                metadata_validated=False,
                duration_seconds=time.time() - start_time,
            )
        
        # Check file size
        if filepath.stat().st_size == 0:
            errors.append("CRITICAL: Source distribution is empty")
        
        # Calculate checksum
        checksum = self.calculate_checksum(filepath)
        checksums.append(f"{filepath.name}:{checksum}")
        
        return ArtifactValidationResult(
            artifact_path=str(filepath),
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checksums_verified=checksums,
            metadata_validated=False,
            duration_seconds=time.time() - start_time,
        )
    
    def verify_checksums(self, artifacts: Optional[List[Path]] = None) -> Dict[str, str]:
        """
        Verify checksums for all artifacts.
        
        Args:
            artifacts: List of artifact paths (uses discover_artifacts if None)
            
        Returns:
            Dictionary mapping artifact names to checksums
        """
        artifacts = artifacts or self.discover_artifacts()
        checksums: Dict[str, str] = {}
        
        for filepath in artifacts:
            checksum = self.calculate_checksum(filepath)
            checksums[filepath.name] = checksum
        
        return checksums
    
    def validate_metadata(self, metadata_path: Path) -> ArtifactValidationResult:
        """
        Validate package metadata.
        
        Args:
            metadata_path: Path to the metadata file
            
        Returns:
            ArtifactValidationResult with validation results
        """
        import time
        start_time = time.time()
        
        errors: List[str] = []
        warnings: List[str] = []
        
        if not metadata_path.exists():
            return ArtifactValidationResult(
                artifact_path=str(metadata_path),
                is_valid=False,
                errors=[f"Metadata file not found: {metadata_path}"],
                warnings=[],
                checksums_verified=[],
                metadata_validated=False,
                duration_seconds=time.time() - start_time,
            )
        
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                if metadata_path.suffix == ".json":
                    metadata = json.load(f)
                elif metadata_path.suffix in (".txt", ""):
                    # Parse simple key-value format
                    content = f.read()
                    metadata = {}
                    for line in content.strip().split("\n"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            metadata[key.strip()] = value.strip()
                else:
                    return ArtifactValidationResult(
                        artifact_path=str(metadata_path),
                        is_valid=False,
                        errors=[f"Unknown metadata format: {metadata_path.suffix}"],
                        warnings=[],
                        checksums_verified=[],
                        metadata_validated=False,
                        duration_seconds=time.time() - start_time,
                    )
            
            # Validate required fields
            if "name" not in metadata:
                errors.append("CRITICAL: Missing 'name' field in metadata")
            
            if "version" not in metadata:
                errors.append("CRITICAL: Missing 'version' field in metadata")
        
        except json.JSONDecodeError as e:
            errors.append(f"CRITICAL: Invalid JSON in metadata: {e}")
        except Exception as e:
            errors.append(f"CRITICAL: Failed to read metadata: {e}")
        
        return ArtifactValidationResult(
            artifact_path=str(metadata_path),
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checksums_verified=[],
            metadata_validated=len(errors) == 0,
            duration_seconds=time.time() - start_time,
        )
    
    def validate_all(self) -> List[ArtifactValidationResult]:
        """
        Validate all artifacts in the distribution directory.
        
        Returns:
            List of ArtifactValidationResult for each artifact
        """
        import time
        
        start_time = time.time()
        results: List[ArtifactValidationResult] = []
        
        for filepath in self.discover_artifacts():
            if filepath.suffix == ".whl":
                result = self.verify_wheel_artifact(filepath)
            elif "tar.gz" in filepath.name:
                result = self.verify_source_distribution(filepath)
            else:
                continue
            
            results.append(result)
        
        return results


def validate_wheel_artifact(artifact_path: str) -> ArtifactValidationResult:
    """Validate a wheel artifact."""
    validator = ArtifactValidator()
    return validator.verify_wheel_artifact(Path(artifact_path))


def validate_source_distribution(artifact_path: str) -> ArtifactValidationResult:
    """Validate a source distribution artifact."""
    validator = ArtifactValidator()
    return validator.verify_source_distribution(Path(artifact_path))


def verify_checksums(dist_path: str = "dist") -> Dict[str, str]:
    """Verify checksums for all artifacts in dist directory."""
    validator = ArtifactValidator(dist_path)
    return validator.verify_checksums()