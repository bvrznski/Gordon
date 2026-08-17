# Observation Memory Candidate - Phase 5.3 Admission
# ===================================================

"""
Observation Memory Candidate: Transportable proposal from Perception to Memory.

The candidate remains a transportable proposal until Memory admits it as an
artifact. It is not a Memory Artifact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# OBSERVATION MEMORY CANDIDATE
# =============================================================================


@dataclass(frozen=True)
class ObservationMemoryCandidate:
    """
    Candidate for Memory admission from Perception.
    
    This is a transportable proposal - it becomes an admitted artifact only
    after Memory accepts it. The candidate remains observational and preserves
    its source role as CURRENT_OBSERVATION until admitted.
    
    Fields:
        candidate_identity:       Unique ID for this candidate (distinct from future Memory identity)
        
        source_projection:        Reference to source Perception projection
        
        source_artifacts:         Original perceptual artifacts involved
        source_roles:             Source roles preserved through integration
        
        observation_window:       Temporal window of the observation
        
        temporal_scope:           Time range covered
        spatial_scope:            Spatial region covered
        
        active_context:           Current workspace/task context
        related_memory_references:  References to potentially related memories
        
        conflicts:                Conflicts detected during preparation
        ambiguities:              Ambiguities in the evidence
        missing_evidence:         Evidence that could not be observed
        
        confidence:               Confidence in this candidate (0.0-1.0)
        uncertainty:              Uncertainty about this candidate (0.0-1.0)
        
        limitations:            Known limitations
        revision:                 Candidate revision number
        provenance:             Origin tracking
    """
    
    # Identity (required - distinct from future Memory identity)
    candidate_identity: str
    
    # Source projection reference (required)
    source_projection: str  # Projection ID
    
    # Source artifacts involved in this observation
    source_artifacts: Tuple[str, ...]  # Percept/Scene/Event IDs
    
    # Source roles preserved through integration (required)
    source_roles: Tuple[Dict[str, Any], ...]
    
    # Observation window (required)
    observation_window: Dict[str, Any]  # Time range, scope info
    
    # Scope parameters
    temporal_scope: Optional[Dict[str, Any]] = None   # Time range coverage
    spatial_scope: Optional[Dict[str, Any]] = None    # Spatial region coverage
    
    # Context information
    active_context: Dict[str, Any] = field(default_factory=dict)  # Current workspace/task
    related_memory_references: Tuple[str, ...] = field(default_factory=tuple)  # Related memory IDs
    
    # Quality metrics (required)
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Problem visibility (required)
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    ambiguities: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    missing_evidence: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Metadata (required)
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_projection(
        cls,
        projection_id: str,
        projection_kind: str,
        source_artifact_ids: List[str],
        source_roles: Tuple[Dict[str, Any], ...],
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "ObservationMemoryCandidate":
        """
        Create a candidate from a Perception projection.
        
        Args:
            projection_id: ID of the source projection
            projection_kind: Kind of projection (percept, scene, event)
            source_artifact_ids: IDs of artifacts in this projection
            source_roles: Source role metadata for each artifact
            confidence: Overall confidence in the observation (0.0-1.0)
            uncertainty: Uncertainty about the observation (0.0-1.0)
            
        Returns:
            New ObservationMemoryCandidate
        """
        now = time.time()
        
        return cls(
            candidate_identity=f"candidate:{projection_id}",
            source_projection=projection_id,
            source_artifacts=tuple(source_artifact_ids),
            source_roles=source_roles,
            observation_window={
                "start_utc": now - 5.0,  # Last 5 seconds
                "end_utc": now,
                "kind": projection_kind,
            },
            temporal_scope={"start_utc": now - 5.0, "end_utc": now},
            spatial_scope={"reference_frame": "global"},
            confidence=confidence,
            uncertainty=uncertainty,
            provenance={
                "origin": "admission_preparation",
                "projection_id": projection_id,
                "created_at_utc": now,
            },
        )
    
    @classmethod
    def from_events(
        cls,
        event_ids: List[str],
        percepts: Tuple[str, ...] = (),
        scenes: Tuple[str, ...] = (),
        source_roles: Tuple[Dict[str, Any], ...] = (),
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "ObservationMemoryCandidate":
        """
        Create a candidate from events with supporting percepts and scenes.
        
        Args:
            event_ids: Event IDs that form the core observation
            percepts: Supporting percept IDs (optional)
            scenes: Supporting scene IDs (optional)
            source_roles: Source role metadata for all artifacts
            confidence: Overall confidence
            uncertainty: Uncertainty about the observation
            
        Returns:
            New ObservationMemoryCandidate
        """
        now = time.time()
        
        all_artifacts = tuple(list(percepts) + list(scenes) + list(event_ids))
        roles = source_roles if source_roles else tuple(
            {"role_kind": "current_observation", "owning_system": "perception"}
            for _ in all_artifacts
        )
        
        return cls(
            candidate_identity=f"candidate:{event_ids[0] if event_ids else str(now)}",
            source_projection="",
            source_artifacts=all_artifacts,
            source_roles=roles,
            observation_window={
                "start_utc": now - 5.0,
                "end_utc": now,
                "kind": "event",
            },
            temporal_scope={"start_utc": now - 5.0, "end_utc": now},
            spatial_scope={"reference_frame": "global"},
            confidence=confidence,
            uncertainty=uncertainty,
            provenance={
                "origin": "admission_preparation",
                "created_at_utc": now,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary for serialization."""
        return {
            "candidate_identity": self.candidate_identity,
            "source_projection": self.source_projection,
            "source_artifacts": list(self.source_artifacts),
            "source_roles": list(self.source_roles),
            "observation_window": dict(self.observation_window),
            "temporal_scope": dict(self.temporal_scope) if self.temporal_scope else {},
            "spatial_scope": dict(self.spatial_scope) if self.spatial_scope else {},
            "active_context": dict(self.active_context),
            "related_memory_references": list(self.related_memory_references),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "conflicts": list(self.conflicts),
            "ambiguities": list(self.ambiguities),
            "missing_evidence": list(self.missing_evidence),
            "limitations": list(self.limitations),
            "revision": self.revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservationMemoryCandidate":
        """Create candidate from dictionary."""
        return cls(
            candidate_identity=data.get("candidate_identity", str(id(data))),
            source_projection=data.get("source_projection", ""),
            source_artifacts=tuple(data.get("source_artifacts", [])),
            source_roles=tuple(data.get("source_roles", [])),
            observation_window=dict(data.get("observation_window", {})),
            temporal_scope=dict(data.get("temporal_scope", {})) or None,
            spatial_scope=dict(data.get("spatial_scope", {})) or None,
            active_context=dict(data.get("active_context", {})),
            related_memory_references=tuple(data.get("related_memory_references", [])),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            conflicts=tuple(data.get("conflicts", [])),
            ambiguities=tuple(data.get("ambiguities", [])),
            missing_evidence=tuple(data.get("missing_evidence", [])),
            limitations=tuple(data.get("limitations", [])),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    @property
    def is_ready_for_admission(self) -> bool:
        """Check if candidate has minimal required data for admission."""
        return (
            len(self.candidate_identity) > 0 and
            len(self.source_projection) > 0 and
            len(self.source_artifacts) > 0 and
            self.confidence >= 0.0 and
            self.confidence <= 1.0 and
            self.uncertainty >= 0.0 and
            self.uncertainty <= 1.0
        )


# =============================================================================
# EVIDENCE BUNDLE - Complete evidence path
# =============================================================================


@dataclass(frozen=True)
class PerceptionMemoryEvidenceBundle:
    """
    Evidence bundle preserving the complete path from acquisition to candidate.
    
    Every candidate shall have an explicit evidence bundle that tracks:
        - Source observations and modalities
        - Processing references (integration steps)
        - Projection references
        - Dependencies
    """
    
    # Identity
    bundle_identity: str                    # Unique ID for this bundle
    
    # Source observations
    source_observations: Tuple[str, ...]    # Raw observation IDs
    source_percepts: Tuple[str, ...]        # Percept IDs
    source_scenes: Tuple[str, ...]          # Scene IDs  
    source_events: Tuple[str, ...]          # Event IDs
    
    # Processing references
    processing_references: Tuple[str, ...]  # Processing steps
    integration_references: Tuple[str, ...] # Integration references
    
    # Projection reference (source of this evidence)
    projection_reference: str               # Final projection ID
    
    # Source dependencies
    source_dependencies: Tuple[Dict[str, Any], ...]
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Limitations and provenance
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_candidate(
        cls,
        candidate: ObservationMemoryCandidate,
        source_observations: List[str],
    ) -> "PerceptionMemoryEvidenceBundle":
        """
        Create an evidence bundle for a candidate.
        
        Args:
            candidate: The candidate this bundle supports
            source_observations: Raw observation IDs involved
            
        Returns:
            New EvidenceBundle
        """
        return cls(
            bundle_identity=f"evidence:{candidate.candidate_identity}",
            source_observations=tuple(source_observations),
            source_percepts=candidate.source_artifacts if len(candidate.source_artifacts) > 0 else (),
            source_scenes=(),
            source_events=(),
            processing_references=(),
            integration_references=(),
            projection_reference=candidate.source_projection,
            source_dependencies=(),
            confidence=candidate.confidence,
            uncertainty=candidate.uncertainty,
            provenance=dict(candidate.provenance),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bundle_identity": self.bundle_identity,
            "source_observations": list(self.source_observations),
            "source_percepts": list(self.source_percepts),
            "source_scenes": list(self.source_scenes),
            "source_events": list(self.source_events),
            "processing_references": list(self.processing_references),
            "integration_references": list(self.integration_references),
            "projection_reference": self.projection_reference,
            "source_dependencies": list(self.source_dependencies),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "provenance": dict(self.provenance),
        }


# =============================================================================
# CONTEXT BUNDLE - Context for admission
# =============================================================================


@dataclass(frozen=True)
class ObservationAdmissionContextBundle:
    """
    Context bundle providing additional information about the observation.
    
    Context assists Memory but never decides Memory admission. It includes:
        - Active workspace context
        - Current task
        - Identity context  
        - Temporal neighborhood (recent observations)
        - Spatial neighborhood
        - Related memories (from recognition)
    """
    
    # Current context
    current_task_reference: Optional[str] = None  # Task ID if applicable
    active_workspace_reference: Optional[str] = None  # Workspace ID
    
    # Identity and temporal context
    identity_context: Dict[str, Any] = field(default_factory=dict)  # Agent state, etc.
    temporal_neighborhood: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Recent observations
    spatial_neighborhood: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)   # Nearby entities
    
    # Memory-related context
    recent_observations: Tuple[str, ...] = field(default_factory=tuple)
    related_memory_candidates: Tuple[str, ...] = field(default_factory=tuple)
    
    # Environmental state
    environmental_state_reference: Optional[str] = None  # Environment snapshot ID
    
    # Context quality metrics
    context_confidence: float = 0.75
    context_uncertainty: float = 0.25
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        current_task: Optional[str] = None,
        workspace_ref: Optional[str] = None,
        identity_context: Optional[Dict[str, Any]] = None,
    ) -> "ObservationAdmissionContextBundle":
        """
        Create a context bundle.
        
        Args:
            current_task: Current task reference (optional)
            workspace_ref: Workspace reference (optional)  
            identity_context: Agent state context (optional)
            
        Returns:
            New ContextBundle
        """
        return cls(
            current_task_reference=current_task,
            active_workspace_reference=workspace_ref,
            identity_context=dict(identity_context or {}),
            provenance={
                "created_at_utc": time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_task_reference": self.current_task_reference,
            "active_workspace_reference": self.active_workspace_reference,
            "identity_context": dict(self.identity_context),
            "temporal_neighborhood": list(self.temporal_neighborhood),
            "spatial_neighborhood": list(self.spatial_neighborhood),
            "recent_observations": list(self.recent_observations),
            "related_memory_candidates": list(self.related_memory_candidates),
            "environmental_state_reference": self.environmental_state_reference,
            "context_confidence": self.context_confidence,
            "context_uncertainty": self.context_uncertainty,
            "provenance": dict(self.provenance),
        }


# =============================================================================
# ADMISSION SUBMISSION - Complete package for Memory
# =============================================================================


@dataclass(frozen=True)
class ObservationAdmissionSubmission:
    """
    Complete admission submission package for Memory.
    
    This package contains everything Memory needs to evaluate the candidate:
        - The candidate itself
        - Evidence bundle (complete evidence path)
        - Context bundle (additional context)
        - Target contract reference (which Memory interface)
        - Authorization context (permissions)
    """
    
    # Identity
    submission_identity: str                # Unique ID for this submission
    
    # Core candidate (required)
    candidate: ObservationMemoryCandidate   # The candidate to admit
    
    # Evidence and context bundles (required)
    evidence_bundle: PerceptionMemoryEvidenceBundle
    context_bundle: ObservationAdmissionContextBundle
    
    # Target information
    target_memory_contract: str = "default"  # Memory interface contract name
    submission_revision: int = 1             # Submission revision number
    compatibility_revision: int = 1          # Compatibility level
    
    # Authorization and provenance (required)
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        candidate: ObservationMemoryCandidate,
        evidence_bundle: PerceptionMemoryEvidenceBundle,
        context_bundle: ObservationAdmissionContextBundle,
        target_contract: str = "default",
    ) -> "ObservationAdmissionSubmission":
        """
        Create an admission submission.
        
        Args:
            candidate: The candidate to submit
            evidence_bundle: Evidence bundle for this candidate
            context_bundle: Context bundle for this candidate
            target_contract: Memory interface contract name
            
        Returns:
            New ObservationAdmissionSubmission
        """
        return cls(
            submission_identity=f"submission:{uuid.uuid4().hex[:16]}",
            candidate=candidate,
            evidence_bundle=evidence_bundle,
            context_bundle=context_bundle,
            target_memory_contract=target_contract,
            provenance={
                "created_at_utc": time.time(),
                "candidate_id": candidate.candidate_identity,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "submission_identity": self.submission_identity,
            "candidate": self.candidate.to_dict(),
            "evidence_bundle": self.evidence_bundle.to_dict(),
            "context_bundle": self.context_bundle.to_dict(),
            "target_memory_contract": self.target_memory_contract,
            "submission_revision": self.submission_revision,
            "compatibility_revision": self.compatibility_revision,
            "authorization_context": dict(self.authorization_context),
            "provenance": dict(self.provenance),
        }


__all__ = [
    "ObservationMemoryCandidate",
    "PerceptionMemoryEvidenceBundle", 
    "ObservationAdmissionContextBundle",
    "ObservationAdmissionSubmission",
]