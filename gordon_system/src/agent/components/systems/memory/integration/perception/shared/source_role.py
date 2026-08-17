# Source Role - Cross-System Artifact Labeling
# ================================================

"""
Source Role: Epistemic labeling for artifacts in Memory-Perception Integration.

Every artifact participating in cross-system processing shall have one explicit
Source Role. This prevents remembered, expected or inferred content from being
presented as current observation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# SOURCE ROLE KINDS
# =============================================================================


class SourceRoleKind(Enum):
    """
    Kinds of source roles that artifacts may possess.
    
    Roles prevent confusion between:
        - what is currently observed (CURRENT_OBSERVATION)
        - what was previously remembered (HISTORICAL_MEMORY)
        - what is recognized as similar (RECOGNITION_CANDIDATE)
        - what is recollected for context (RECOLLECTION)
        - what is expected to happen (EXPECTATION)
        - what is inferred across a gap (CONTINUITY_CANDIDATE)
        - what conflicts with another source (CONFLICTED)
    """
    
    # Primary roles
    CURRENT_OBSERVATION = "current_observation"     # From Perception, current observation
    HISTORICAL_MEMORY = "historical_memory"         # From Memory, retained experience
    
    # Integration candidate roles
    RECOGNITION_CANDIDATE = "recognition_candidate"  # Perceived may match remembered
    RECOLLECTION = "recollection"                    # Remembered for current context
    EXPECTATION = "expectation"                      # Expected future content
    CONTINUITY_CANDIDATE = "continuity_candidate"   # Same entity across gap
    
    # Result roles
    MISMATCH = "mismatch"                            # Expectation vs observation
    CONTEXT = "context"                              # Enriching context
    
    # Metadata roles
    INFERENCE = "inference"                          # Derived from other content
    UNKNOWN = "unknown"                              # Role not determined


# =============================================================================
# SOURCE ROLE METADATA
# =============================================================================


@dataclass(frozen=True)
class SourceRoleMetadata:
    """
    Metadata for an artifact's source role.
    
    Every cross-system artifact shall have explicit source role metadata that
    survives serialization, caching, and replay.
    """
    
    # Identity
    role_identity: str                               # Unique ID for this role assignment
    
    # The role itself (required)
    role_kind: SourceRoleKind                        # What kind of source is this?
    
    # Ownership
    owning_system: str                               # "perception" or "memory"
    
    # Temporal status
    temporal_status: str = "current"                 # current, recent, stale, gapped
    
    # Observational status (for perception-originated content)
    observational_status: str = "direct"             # direct, inferred, reconstructed
    
    # Persistence status
    persistence_status: str = "transient"            # transient, candidate, admitted
    
    # Authority (domain-specific, not universal epistemic authority)
    authority: Optional[str] = None                  # e.g., "perception_visual"
    
    # Confidence and uncertainty at source role assignment time
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Provenance - how was this role assigned?
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_current_observation(
        cls,
        source_identity: str,
        authority: Optional[str] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "SourceRoleMetadata":
        """Create metadata for current observation."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.CURRENT_OBSERVATION,
            owning_system="perception",
            temporal_status="current",
            observational_status="direct",
            persistence_status="transient",
            authority=authority,
            confidence=confidence,
            uncertainty=uncertainty,
            provenance={
                "assignment_method": "perception_projection",
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_historical_memory(
        cls,
        source_identity: str,
        memory_artifact_id: str,
        confidence: float = 0.9,
        uncertainty: float = 0.1,
    ) -> "SourceRoleMetadata":
        """Create metadata for historical memory."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.HISTORICAL_MEMORY,
            owning_system="memory",
            temporal_status="stale",  # Memory is by definition past
            observational_status="recorded",
            persistence_status="admitted",
            authority=None,
            confidence=confidence,
            uncertainty=uncertainty,
            provenance={
                "assignment_method": "memory_admission",
                "original_artifact_id": memory_artifact_id,
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_recognition_candidate(
        cls,
        source_identity: str,
        recognition_kind: str,
        similarity: float = 0.5,
    ) -> "SourceRoleMetadata":
        """Create metadata for recognition candidate."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.RECOGNITION_CANDIDATE,
            owning_system="integration",
            temporal_status="current",
            observational_status="candidate",
            persistence_status="transient",
            authority=None,
            confidence=similarity,
            uncertainty=1.0 - similarity,
            provenance={
                "assignment_method": "recognition_comparison",
                "recognition_kind": recognition_kind,
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_recollection(
        cls,
        source_identity: str,
        trigger_artifact_id: str,
        relevance: float = 0.7,
    ) -> "SourceRoleMetadata":
        """Create metadata for recollection context."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.RECOLLECTION,
            owning_system="memory",
            temporal_status="stale",
            observational_status="contextual",
            persistence_status="admitted",
            authority=None,
            confidence=relevance * 0.5 + 0.5,  # Relevance is not truth
            uncertainty=1.0 - (relevance * 0.5 + 0.5),
            provenance={
                "assignment_method": "recollection_query",
                "trigger_artifact_id": trigger_artifact_id,
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_expectation(
        cls,
        source_identity: str,
        expectation_kind: str,
        confidence: float = 0.7,
        uncertainty: float = 0.3,
    ) -> "SourceRoleMetadata":
        """Create metadata for expectation."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.EXPECTATION,
            owning_system="integration",
            temporal_status="future",
            observational_status="prospective",
            persistence_status="transient",
            authority=None,
            confidence=confidence,
            uncertainty=uncertainty,
            provenance={
                "assignment_method": "expectation_generation",
                "expectation_kind": expectation_kind,
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_continuity_candidate(
        cls,
        source_identity: str,
        gap_duration_seconds: float,
        confidence: float = 0.6,
    ) -> "SourceRoleMetadata":
        """Create metadata for continuity candidate."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.CONTINUITY_CANDIDATE,
            owning_system="integration",
            temporal_status="gapped",
            observational_status="inferred",
            persistence_status="transient",
            authority=None,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            provenance={
                "assignment_method": "continuity_analysis",
                "gap_duration_seconds": gap_duration_seconds,
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_mismatch(
        cls,
        source_identity: str,
        mismatch_kind: str,
    ) -> "SourceRoleMetadata":
        """Create metadata for mismatch report."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.MISMATCH,
            owning_system="integration",
            temporal_status="current",
            observational_status="diagnostic",
            persistence_status="transient",
            authority=None,
            confidence=0.8,  # Mismatch is descriptive, not inferential
            uncertainty=0.2,
            provenance={
                "assignment_method": "mismatch_detection",
                "mismatch_kind": mismatch_kind,
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_context(
        cls,
        source_identity: str,
        confidence: float = 0.5,
    ) -> "SourceRoleMetadata":
        """Create metadata for contextual enrichment."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.CONTEXT,
            owning_system="integration",
            temporal_status="current",
            observational_status="enrichment",
            persistence_status="transient",
            authority=None,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            provenance={
                "assignment_method": "contextualization",
                "timestamp_utc": time.time(),
            },
        )
    
    @classmethod
    def from_inference(
        cls,
        source_identity: str,
        inference_kind: str,
        confidence: float = 0.5,
    ) -> "SourceRoleMetadata":
        """Create metadata for inferred content."""
        return cls(
            role_identity=f"source_role:{source_identity}",
            role_kind=SourceRoleKind.INFERENCE,
            owning_system="integration",
            temporal_status="current",
            observational_status="inferred",
            persistence_status="transient",
            authority=None,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            provenance={
                "assignment_method": f"reasoning:{inference_kind}",
                "timestamp_utc": time.time(),
            },
        )
    
    def is_current_observation(self) -> bool:
        """Check if this role represents current perception."""
        return self.role_kind == SourceRoleKind.CURRENT_OBSERVATION
    
    def is_historical_memory(self) -> bool:
        """Check if this role represents retained memory."""
        return self.role_kind == SourceRoleKind.HISTORICAL_MEMORY
    
    def is_candidate(self) -> bool:
        """Check if this role represents a candidate (not committed)."""
        return self.role_kind in (
            SourceRoleKind.RECOGNITION_CANDIDATE,
            SourceRoleKind.CONTINUITY_CANDIDATE,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "role_identity": self.role_identity,
            "role_kind": self.role_kind.value,
            "owning_system": self.owning_system,
            "temporal_status": self.temporal_status,
            "observational_status": self.observational_status,
            "persistence_status": self.persistence_status,
            "authority": self.authority,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceRoleMetadata":
        """Create metadata from dictionary."""
        return cls(
            role_identity=data.get("role_identity", str(id(data))),
            role_kind=SourceRoleKind(data.get("role_kind", "unknown")),
            owning_system=data.get("owning_system", "integration"),
            temporal_status=data.get("temporal_status", "current"),
            observational_status=data.get("observational_status", "direct"),
            persistence_status=data.get("persistence_status", "transient"),
            authority=data.get("authority"),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# SOURCE ROLE VALIDATOR
# =============================================================================


class SourceRoleValidator:
    """
    Validates source role assignments in cross-system artifacts.
    
    Ensures that:
        - Every artifact has exactly one primary source role
        - CURRENT_OBSERVATION is only assigned to perception-originated content
        - HISTORICAL_MEMORY is only assigned to memory-admitted artifacts
        - Candidate roles never masquerade as current observation
    """
    
    @staticmethod
    def validate_role_assignment(
        artifact_identity: str,
        role_metadata: SourceRoleMetadata,
        source_system: Optional[str] = None,
    ) -> Tuple[bool, list]:
        """
        Validate that a source role assignment is legitimate.
        
        Args:
            artifact_identity: ID of the artifact being labeled
            role_metadata: The role metadata to validate
            source_system: The actual system of origin (optional)
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Rule 1: Every artifact must have a valid role kind
        try:
            _ = SourceRoleKind(role_metadata.role_kind.value)
        except ValueError:
            errors.append(f"Invalid source role kind: {role_metadata.role_kind}")
        
        # Rule 2: CURRENT_OBSERVATION only from perception
        if (role_metadata.role_kind == SourceRoleKind.CURRENT_OBSERVATION and
                role_metadata.owning_system != "perception"):
            errors.append(
                f"CURRENT_OBSERVATION role assigned to non-perception artifact: "
                f"{artifact_identity}"
            )
        
        # Rule 3: HISTORICAL_MEMORY only from memory
        if (role_metadata.role_kind == SourceRoleKind.HISTORICAL_MEMORY and
                role_metadata.owning_system != "memory"):
            errors.append(
                f"HISTORICAL_MEMORY role assigned to non-memory artifact: "
                f"{artifact_identity}"
            )
        
        # Rule 4: Candidate roles are not current observations
        if (role_metadata.role_kind in (
                SourceRoleKind.RECOGNITION_CANDIDATE,
                SourceRoleKind.CONTINUITY_CANDIDATE)):
            if role_metadata.observational_status == "direct":
                errors.append(
                    f"Candidate role {role_metadata.role_kind.value} should not "
                    f"have observational_status='direct' for artifact: {artifact_identity}"
                )
        
        # Rule 5: Source role must survive serialization
        try:
            _ = SourceRoleMetadata.from_dict(role_metadata.to_dict())
        except Exception as e:
            errors.append(f"Source role metadata not serializable: {e}")
        
        return len(errors) == 0, errors


__all__ = [
    "SourceRoleKind",
    "SourceRoleMetadata",
    "SourceRoleValidator",
]