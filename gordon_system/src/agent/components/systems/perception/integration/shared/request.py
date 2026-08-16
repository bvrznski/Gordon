# Perception Integration Request - Phase 5.2.3
# =============================================

"""
Integration Request: Specification for what evidence to integrate.

A PerceptionIntegrationRequest describes the desired integration without being
an artifact itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# INTEGRATION SCOPE - What kind of integration is requested?
# =============================================================================


class IntegrationScope(Enum):
    """
    Scope of the integration request.
    
    Scopes:
        PERCEPT:      Integrate to produce a fused percept
        SCENE:        Integrate to produce a multimodal scene
        EVENT:        Integrate to produce a multimodal event
        CORRESPONDENCE: Evaluate correspondence between artifacts
        TEMPORAL_BINDING: Bind artifacts into temporal groups
        SPATIAL_BINDING: Bind artifacts into spatial structures
    """
    
    PERCEPT = "percept"              # Produce fused Percept
    SCENE = "scene"                  # Produce MultimodalScene
    EVENT = "event"                  # Produce MultimodalEvent
    CORRESPONDENCE = "correspondence"  # Evaluate correspondence
    TEMPORAL_BINDING = "temporal_binding"  # Temporal binding only
    SPATIAL_BINDING = "spatial_binding"    # Spatial binding only


# =============================================================================
# BINDING POLICY - How should artifacts be grouped?
# =============================================================================


class BindingPolicy(Enum):
    """
    Policy for grouping artifacts into bindings.
    
    Policies:
        STRICT:    Only bind when all constraints are satisfied
        ADAPTIVE:  Bind with tolerance when exact matches unavailable
        PERMISSIVE: Bind even with weak evidence, flag as uncertain
        conservative: Require strong evidence before binding
    """
    
    STRICT = "strict"          # Require full constraint satisfaction
    ADAPTIVE = "adaptive"      # Use tolerance windows
    PERMISSIVE = "permissive"  # Allow weak evidence, flag uncertainty
    CONSERVATIVE = "conservative"  # Require strong evidence


# =============================================================================
# FUSION POLICY - How should correlated artifacts be combined?
# =============================================================================


class FusionPolicy(Enum):
    """
    Policy for combining correlated evidence.
    
    Policies:
        COMPLEMENTARY: Combine distinct fields from compatible sources
        CORROBORATIVE: Aggregate independent supporting evidence
        COMPETITIVE: Preserve incompatible alternatives
        HIERARCHICAL: Preserve multiple abstraction levels
        FIELD_LEVEL: Integrate selected fields, preserve others separately
    """
    
    COMPLEMENTARY = "complementary"     # Combine non-overlapping fields
    CORROBORATIVE = "corroborative"     # Aggregate independent support
    COMPETITIVE = "competitive"         # Preserve alternatives
    HIERARCHICAL = "hierarchical"       # Preserve abstraction levels
    FIELD_LEVEL = "field_level"         # Field-level integration


# =============================================================================
# CONFIDENCE POLICY - How should confidence be aggregated?
# =============================================================================


class ConfidencePolicy(Enum):
    """
    Policy for integrating confidence across sources.
    
    Policies:
        AVERAGE:   Simple average of source confidences
        WEIGHTED:  Weight by source reliability and independence
        MINIMUM:   Use minimum confidence (conservative)
        MAXIMUM:   Use maximum confidence (optimistic)
        DEPENDENCY_AWARE: Account for source dependencies
    """
    
    AVERAGE = "average"           # Simple average
    WEIGHTED = "weighted"         # Weighted by reliability
    MINIMUM = "minimum"           # Conservative
    MAXIMUM = "maximum"           # Optimistic
    DEPENDENCY_AWARE = "dependency_aware"  # Account for dependencies


# =============================================================================
# UNCERTAINTY POLICY - How should uncertainty be aggregated?
# =============================================================================


class UncertaintyPolicy(Enum):
    """
    Policy for integrating uncertainty across sources.
    
    Policies:
        AVERAGE:   Simple average of source uncertainties
        WEIGHTED:  Weight by source reliability
        MAXIMUM:   Use maximum uncertainty (conservative)
        COMBINED:  Combine as independent sources
        DEPENDENCY_AWARE: Account for source dependencies
    """
    
    AVERAGE = "average"           # Simple average
    WEIGHTED = "weighted"         # Weighted by reliability
    MAXIMUM = "maximum"           # Conservative
    COMBINED = "combined"         # Independent combination
    DEPENDENCY_AWARE = "dependency_aware"  # Account for dependencies


# =============================================================================
# PERCEPTION INTEGRATION REQUEST - What integration to perform?
# =============================================================================


@dataclass(frozen=True)
class PerceptionIntegrationRequest:
    """
    Request for perception integration.
    
    Fields:
        request_identity:     Unique request identifier
        candidate_artifacts:  Artifacts to consider for integration (references only)
        participating_modalities: Which modalities are involved?
        integration_scope:    What kind of integration is requested?
        temporal_scope:       Temporal window for integration
        spatial_scope:        Spatial scope for integration
        binding_policy:       Policy for grouping artifacts
        fusion_policy:        Policy for combining evidence
        confidence_policy:    Policy for confidence aggregation
        uncertainty_policy:   Policy for uncertainty aggregation
        source_independence_requirements: Independence constraints
        constraints:          Integration constraints (timeout, resources)
        provenance:           Request origin tracking
    """
    
    request_identity: str                  # Unique ID
    
    candidate_artifacts: Tuple[str, ...]   # Artifact IDs to integrate
    
    participating_modalities: Tuple[str, ...]  # e.g., ("console", "vision")
    
    integration_scope: IntegrationScope = IntegrationScope.PERCEPT
    
    temporal_scope: Dict[str, Any] = field(default_factory=dict)  # time range, tolerance
    spatial_scope: Dict[str, Any] = field(default_factory=dict)   # coordinate system, bounds
    
    binding_policy: BindingPolicy = BindingPolicy.ADAPTIVE
    fusion_policy: FusionPolicy = FusionPolicy.COMPLEMENTARY
    confidence_policy: ConfidencePolicy = ConfidencePolicy.DEPENDENCY_AWARE
    uncertainty_policy: UncertaintyPolicy = UncertaintyPolicy.DEPENDENCY_AWARE
    
    source_independence_requirements: Tuple[str, ...] = field(default_factory=tuple)
    
    constraints: Dict[str, Any] = field(default_factory=dict)  # timeout, resources, etc.
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Request origin
    
    @property
    def is_valid(self) -> bool:
        """Check if request has minimal required data."""
        return (
            len(self.request_identity) > 0 and
            len(self.candidate_artifacts) > 0 and
            len(self.participating_modalities) > 0
        )
    
    @classmethod
    def create(
        cls,
        candidate_artifact_ids: List[str],
        participating_modalities: Optional[List[str]] = None,
        integration_scope: IntegrationScope = IntegrationScope.PERCEPT,
        temporal_scope: Optional[Dict[str, Any]] = None,
        spatial_scope: Optional[Dict[str, Any]] = None,
        binding_policy: BindingPolicy = BindingPolicy.ADAPTIVE,
        fusion_policy: FusionPolicy = FusionPolicy.COMPLEMENTARY,
    ) -> "PerceptionIntegrationRequest":
        """
        Create a new integration request.
        
        Args:
            candidate_artifact_ids: IDs of artifacts to integrate
            participating_modalities: Modalities involved (optional)
            integration_scope: What kind of integration?
            temporal_scope: Temporal window specification (optional)
            spatial_scope: Spatial scope specification (optional)
            binding_policy: Grouping policy
            fusion_policy: Combination policy
            
        Returns:
            New PerceptionIntegrationRequest
        """
        return cls(
            request_identity=f"integration:{uuid.uuid4().hex[:16]}",
            candidate_artifacts=tuple(candidate_artifact_ids),
            participating_modalities=tuple(participating_modalities or ["unknown"]),
            integration_scope=integration_scope,
            temporal_scope=temporal_scope or {},
            spatial_scope=spatial_scope or {},
            binding_policy=binding_policy,
            fusion_policy=fusion_policy,
            confidence_policy=ConfidencePolicy.DEPENDENCY_AWARE,
            uncertainty_policy=UncertaintyPolicy.DEPENDENCY_AWARE,
            source_independence_requirements=(),
            constraints={},
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_identity": self.request_identity,
            "candidate_artifacts": list(self.candidate_artifacts),
            "participating_modalities": list(self.participating_modalities),
            "integration_scope": self.integration_scope.value,
            "temporal_scope": dict(self.temporal_scope),
            "spatial_scope": dict(self.spatial_scope),
            "binding_policy": self.binding_policy.value,
            "fusion_policy": self.fusion_policy.value,
            "confidence_policy": self.confidence_policy.value,
            "uncertainty_policy": self.uncertainty_policy.value,
            "source_independence_requirements": list(self.source_independence_requirements),
            "constraints": dict(self.constraints),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionIntegrationRequest":
        """Create request from dictionary."""
        return cls(
            request_identity=data.get("request_identity", str(uuid.uuid4())),
            candidate_artifacts=tuple(data.get("candidate_artifacts", [])),
            participating_modalities=tuple(data.get("participating_modalities", ["unknown"])),
            integration_scope=IntegrationScope(data.get("integration_scope", "percept")),
            temporal_scope=dict(data.get("temporal_scope", {})),
            spatial_scope=dict(data.get("spatial_scope", {})),
            binding_policy=BindingPolicy(data.get("binding_policy", "adaptive")),
            fusion_policy=FusionPolicy(data.get("fusion_policy", "complementary")),
            confidence_policy=ConfidencePolicy(data.get("confidence_policy", "dependency_aware")),
            uncertainty_policy=UncertaintyPolicy(data.get("uncertainty_policy", "dependency_aware")),
            source_independence_requirements=tuple(data.get("source_independence_requirements", [])),
            constraints=dict(data.get("constraints", {})),
            provenance=dict(data.get("provenance", {})),
        )