# Perception Integration Engine - Phase 5.2.3
# ===========================================

"""
Integration Engine: Orchestrates multimodal evidence integration.

The engine validates requests, evaluates correspondences, constructs bindings,
and produces fused perceptual artifacts while preserving source independence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid

# Import shared contracts
from gordon_system.src.agent.components.systems.perception.integration.shared.request import (
    PerceptionIntegrationRequest,
    IntegrationScope,
    BindingPolicy,
    FusionPolicy,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.result import (
    PerceptionIntegrationResult,
    IntegrationStatus,
    IntegrationOutcome,
    CorrespondenceRecord,
    BindingRecord,
    FusionRecord,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.evidence_group import (
    PerceptualEvidenceGroup,
    GroupingBasis,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.source_dependency import (
    SourceDependencyAssessment,
    DependencyKind,
)


# =============================================================================
# INTEGRATION ENGINE - Orchestrates integration operations
# =============================================================================


class PerceptionIntegrationEngine:
    """
    Engine that orchestrates multimodal perception integration.
    
    Responsibilities:
        - Validate Integration Requests
        - Resolve eligible source artifacts
        - Evaluate source dependencies
        - Construct candidate Evidence Groups
        - Evaluate intermodal correspondences
        - Construct temporal bindings
        - Construct spatial bindings
        - Detect conflicts
        - Select approved fusion strategies
        - Compute source weights
        - Construct integrated perceptual artifacts
        - Propagate confidence and uncertainty
        - Preserve field-level provenance
        - Validate final outputs
        - Publish immutable Integration Results
    
    Properties:
        identity:          Unique engine identifier
        active_config:     Current configuration revision
        health_status:     Operational health
        
    Example:
        engine = PerceptionIntegrationEngine()
        
        request = PerceptionIntegrationRequest.create(
            candidate_artifact_ids=["artifact1", "artifact2"],
            participating_modalities=["console", "vision"],
        )
        
        result = engine.execute(request)
    """
    
    def __init__(
        self,
        identity: Optional[str] = None,
    ):
        """
        Initialize the integration engine.
        
        Args:
            identity: Unique identifier (auto-generated if None)
        """
        self._identity = identity or f"integration_engine:{uuid.uuid4().hex[:16]}"
        self._active_config: int = 1
        self._health_status = {"status": "healthy", "last_check": time.time()}
    
    @property
    def identity(self) -> str:
        """Unique engine identifier."""
        return self._identity
    
    @property
    def active_config(self) -> int:
        """Current configuration revision."""
        return self._active_config
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Operational health status."""
        return dict(self._health_status)
    
    def validate_request(
        self,
        request: PerceptionIntegrationRequest,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that an integration request is valid.
        
        Args:
            request: The request to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not request.request_identity:
            errors.append("Request identity is required")
        
        if len(request.candidate_artifacts) == 0:
            errors.append("At least one candidate artifact is required")
        
        if len(request.participating_modalities) == 0:
            errors.append("At least one modality is required")
        
        return len(errors) == 0, errors
    
    def execute(
        self,
        request: PerceptionIntegrationRequest,
    ) -> PerceptionIntegrationResult:
        """
        Execute integration for a request.
        
        Args:
            request: The integration request
            
        Returns:
            Integration result with traceability
        """
        # Validate request first
        is_valid, errors = self.validate_request(request)
        if not is_valid:
            return PerceptionIntegrationResult.failed(
                request_reference=request.request_identity,
                failure_message=f"Request validation failed: {errors}",
            )
        
        start_time = time.time()
        
        # Stage 1: Source Dependency Analysis
        dependency_assessments, dependency_issues = self._analyze_source_dependencies(request)
        
        # Stage 2: Evidence Grouping
        evidence_groups = self._group_evidence(request, dependency_assessments)
        
        if not evidence_groups:
            return PerceptionIntegrationResult.partial(
                request_reference=request.request_identity,
                integrated_artifact_ids=(),
                missing_artifact_count=len(request.candidate_artifacts),
                limitations=("No eligible evidence found for integration",),
            )
        
        # Stage 3: Intermodal Correspondence
        correspondences, correspondence_issues = self._evaluate_correspondences(
            request,
            evidence_groups,
            dependency_assessments,
        )
        
        if not correspondences:
            return PerceptionIntegrationResult.partial(
                request_reference=request.request_identity,
                integrated_artifact_ids=(),
                missing_artifact_count=len(request.candidate_artifacts),
                limitations=("No intermodal correspondences found",),
            )
        
        # Stage 4: Temporal Binding
        temporal_bindings = self._construct_temporal_bindings(request, evidence_groups)
        
        # Stage 5: Spatial Binding
        spatial_bindings = self._construct_spatial_bindings(request, evidence_groups)
        
        # Stage 6: Conflict Detection
        conflicts = self._detect_conflicts(correspondences)
        
        # Determine outcome based on results
        if len(conflicts) > 0:
            return PerceptionIntegrationResult.ambiguous(
                request_reference=request.request_identity,
                integrated_artifact_ids=tuple(e.group_identity for e in evidence_groups),
                plausible_structures=len(conflicts) + 1,
                alternatives=tuple(str(c.conflict_identity) for c in conflicts[:3]),
            )
        
        # Stage 7: Fusion
        fused_artifacts = self._apply_fusion(
            request,
            correspondences,
            temporal_bindings,
            spatial_bindings,
            dependency_assessments,
        )
        
        elapsed_time = time.time() - start_time
        
        return PerceptionIntegrationResult.success(
            request_reference=request.request_identity,
            integrated_artifact_ids=tuple(fused_artifacts),
            correspondence_records=correspondences,
            binding_records=temporal_bindings + spatial_bindings,
            fusion_records=[FusionRecord(
                fusion_identity=f"fusion:{uuid.uuid4().hex[:16]}",
                source_artifact_ids=tuple(request.candidate_artifacts),
                fusion_strategy=request.fusion_policy.value if hasattr(request.fusion_policy, 'value') else str(request.fusion_policy),
            )],
        )
    
    def _analyze_source_dependencies(
        self,
        request: PerceptionIntegrationRequest,
    ) -> Tuple[List[SourceDependencyAssessment], List[str]]:
        """Analyze dependencies between evidence sources."""
        assessments = []
        issues = []
        
        # For now, assume different modalities are independent
        unique_modalities = set(request.participating_modalities)
        
        if len(unique_modalities) > 1:
            assessments.append(SourceDependencyAssessment(
                assessment_identity=f"dependency:{uuid.uuid4().hex[:16]}",
                source_artifacts=request.candidate_artifacts,
                source_modalities=tuple(request.participating_modalities),
                dependency_kind=DependencyKind.INDEPENDENT,
                confidence=0.85,
            ))
        else:
            assessments.append(SourceDependencyAssessment(
                assessment_identity=f"dependency:{uuid.uuid4().hex[:16]}",
                source_artifacts=request.candidate_artifacts,
                source_modalities=tuple(request.participating_modalities),
                dependency_kind=DependencyKind.COMMON_OBSERVATION,
                shared_observation=True,
                dependency_strength=0.75,
                confidence=0.7,
            ))
        
        return assessments, issues
    
    def _group_evidence(
        self,
        request: PerceptionIntegrationRequest,
        dependency_assessments: List[SourceDependencyAssessment],
    ) -> List[PerceptualEvidenceGroup]:
        """Group candidate artifacts into evidence groups."""
        if len(request.candidate_artifacts) == 0:
            return []
        
        # Create a single group containing all artifacts
        return [PerceptualEvidenceGroup(
            group_identity=f"evidence_group:{uuid.uuid4().hex[:16]}",
            member_artifacts=request.candidate_artifacts,
            grouping_basis=GroupingBasis.TEMPORAL_PROXIMITY,
            participating_modalities=tuple(request.participating_modalities),
            source_dependency_summary=self._summarize_dependencies(dependency_assessments),
        )]
    
    def _summarize_dependencies(
        self,
        assessments: List[SourceDependencyAssessment],
    ) -> Dict[str, Any]:
        """Summarize dependency analysis for evidence groups."""
        if not assessments:
            return {
                "total_sources": 0,
                "independent_count": 0,
                "partially_dependent_count": 0,
                "common_source_count": 0,
                "dependency_kind": "unknown",
            }
        
        independent = sum(1 for a in assessments if a.dependency_kind == DependencyKind.INDEPENDENT)
        dependent = len(assessments) - independent
        
        return {
            "total_sources": len(assessments),
            "independent_count": independent,
            "partially_dependent_count": dependent,
            "common_source_count": dependent,
            "dependency_kind": "partially_dependent" if dependent > 0 else "independent",
        }
    
    def _evaluate_correspondences(
        self,
        request: PerceptionIntegrationRequest,
        evidence_groups: List[PerceptualEvidenceGroup],
        dependency_assessments: List[SourceDependencyAssessment],
    ) -> Tuple[List[CorrespondenceRecord], List[str]]:
        """Evaluate correspondences between artifacts."""
        correspondences = []
        issues = []
        
        # For now, create a single correspondence for all artifacts
        if evidence_groups:
            group = evidence_groups[0]
            
            # If multiple modalities, consider them potentially corresponding
            unique_modalities = set(request.participating_modalities)
            
            if len(unique_modalities) > 1:
                correspondences.append(CorrespondenceRecord(
                    correspondence_identity=f"correspondence:{uuid.uuid4().hex[:16]}",
                    participating_artifact_ids=group.member_artifacts,
                    correspondence_kind="same_event_candidate",
                    temporal_compatibility=0.85,
                    spatial_compatibility=0.85,
                    confidence=0.7,
                ))
            else:
                correspondences.append(CorrespondenceRecord(
                    correspondence_identity=f"correspondence:{uuid.uuid4().hex[:16]}",
                    participating_artifact_ids=group.member_artifacts,
                    correspondence_kind="related_but_distinct",
                    temporal_compatibility=0.95,
                    spatial_compatibility=0.95,
                    confidence=0.5,  # Lower since same modality
                ))
        
        return correspondences, issues
    
    def _construct_temporal_bindings(
        self,
        request: PerceptionIntegrationRequest,
        evidence_groups: List[PerceptualEvidenceGroup],
    ) -> List[BindingRecord]:
        """Construct temporal bindings for artifacts."""
        bindings = []
        
        if evidence_groups:
            group = evidence_groups[0]
            
            # Create a binding window based on temporal scope
            binding_window = request.temporal_scope.copy() if request.temporal_scope else {
                "start": time.time() - 60,  # Last 60 seconds
                "end": time.time(),
                "tolerance": 1.0,
            }
            
            bindings.append(BindingRecord(
                binding_identity=f"temporal_binding:{uuid.uuid4().hex[:16]}",
                bound_artifact_ids=group.member_artifacts,
                binding_window=binding_window,
                confidence=0.75,
            ))
        
        return bindings
    
    def _construct_spatial_bindings(
        self,
        request: PerceptionIntegrationRequest,
        evidence_groups: List[PerceptualEvidenceGroup],
    ) -> List[BindingRecord]:
        """Construct spatial bindings for artifacts."""
        bindings = []
        
        if evidence_groups:
            group = evidence_groups[0]
            
            # Create a binding window based on spatial scope
            binding_window = request.spatial_scope.copy() if request.spatial_scope else {
                "region": "global",
                "tolerance_meters": 10.0,
            }
            
            bindings.append(BindingRecord(
                binding_identity=f"spatial_binding:{uuid.uuid4().hex[:16]}",
                bound_artifact_ids=group.member_artifacts,
                binding_window=binding_window,
                confidence=0.75,
            ))
        
        return bindings
    
    def _detect_conflicts(
        self,
        correspondences: List[CorrespondenceRecord],
    ) -> List[Dict[str, Any]]:
        """Detect conflicts in correspondences."""
        conflicts = []
        
        # Check for conflicting temporal/spatial compatibilities
        for corr in correspondences:
            if corr.temporal_compatibility < 0.5 or corr.spatial_compatibility < 0.5:
                conflicts.append({
                    "conflict_identity": f"conflict:{uuid.uuid4().hex[:16]}",
                    "correspondence_id": corr.correspondence_identity,
                    "participating_artifacts": list(corr.participating_artifact_ids),
                    "type": "compatibility_conflict",
                    "severity": 0.3,
                })
        
        return conflicts
    
    def _apply_fusion(
        self,
        request: PerceptionIntegrationRequest,
        correspondences: List[CorrespondenceRecord],
        temporal_bindings: List[BindingRecord],
        spatial_bindings: List[BindingRecord],
        dependency_assessments: List[SourceDependencyAssessment],
    ) -> List[str]:
        """Apply fusion strategy to produce integrated artifacts."""
        fused_ids = []
        
        # Create fused artifact IDs based on fusion strategy
        for corr in correspondences:
            fused_id = f"fused:{uuid.uuid4().hex[:16]}"
            
            # If corroborative fusion, boost confidence
            if request.fusion_policy == FusionPolicy.CORROBORATIVE:
                if len(corr.participating_artifact_ids) > 1 and any(
                    a.dependency_kind == DependencyKind.INDEPENDENT
                    for a in dependency_assessments
                ):
                    pass  # Confidence already from correspondence
            
            fused_ids.append(fused_id)
        
        return fused_ids


__all__ = ["PerceptionIntegrationEngine"]