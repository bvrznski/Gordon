# Knowledge Model Explanation - Phase 6.7
# =======================================

"""
Model Explanations: Connect observations to underlying mechanisms.

Explanations trace from observations through supporting relations and assertions
to the model that provides the explanatory framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# EXPLANATION PATH - Tracing through explanation graph
# =============================================================================


@dataclass(frozen=True)
class ExplanationPath:
    """
    Path through an explanation graph from observation to mechanism.
    
    Each path represents one way an observation can be explained by a model.
    
    Fields:
        path_identity:         Unique identifier for this explanation path
        observation:           The observed phenomenon
        underlying_mechanism:  The underlying cause or mechanism
        supporting_relations:  Relations used in the explanation chain
        supporting_assertions: Assertions used in the explanation chain
    """
    
    # Identity fields (required)
    path_identity: str                  # Unique ID for this path
    
    # Observation and mechanism (required)
    observation: str                    # The observed phenomenon
    underlying_mechanism: str           # The underlying cause/structure
    
    # Supporting semantic artifacts
    supporting_relations: Tuple[str, ...] = field(default_factory=tuple)  # Relation IDs
    supporting_assertions: Tuple[str, ...] = field(default_factory=tuple)  # Assertion IDs
    
    @property
    def path_length(self) -> int:
        """Get the total length of this explanation path."""
        return len(self.supporting_relations) + len(self.supporting_assertions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert path to dictionary for serialization."""
        return {
            "path_identity": self.path_identity,
            "observation": self.observation,
            "underlying_mechanism": self.underlying_mechanism,
            "supporting_relations": list(self.supporting_relations),
            "supporting_assertions": list(self.supporting_assertions),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExplanationPath":
        """Create path from dictionary."""
        return cls(
            path_identity=data.get("path_identity", str(uuid.uuid4())),
            observation=data.get("observation", ""),
            underlying_mechanism=data.get("underlying_mechanism", ""),
            supporting_relations=tuple(data.get("supporting_relations", [])),
            supporting_assertions=tuple(data.get("supporting_assertions", [])),
        )


# =============================================================================
# EXPLANATION GRAPH - Complete explanation structure
# =============================================================================


@dataclass(frozen=True)
class ExplanationGraph:
    """
    Canonical representation of model explanation in Gordon's knowledge system.
    
    Explanation graphs connect observations to models through supporting semantic
    artifacts and causal mechanisms.
    
    Fields:
        graph_identity:        Unique identifier for this explanation graph
        explained_observations: Observations being explained
        explanation_paths:     Complete paths from observation to model
        supporting_components: All components used in explanations
        confidence:            Confidence in the explanation (0.0-1.0)
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    graph_identity: str                 # Unique ID for this explanation graph
    
    # Explained observations (required)
    explained_observations: Tuple[str, ...]  # The observed phenomena
    
    # Explanation structure
    explanation_paths: Tuple[ExplanationPath, ...] = field(default_factory=tuple)  # Paths
    
    # Supporting semantic artifacts
    supporting_components: Tuple[str, ...] = field(default_factory=tuple)  # Component IDs
    
    # Confidence metrics (required)
    confidence: float = 0.5             # Confidence in explanation (0.0-1.0)
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def observation_count(self) -> int:
        """Get the number of explained observations."""
        return len(self.explained_observations)
    
    @property
    def path_count(self) -> int:
        """Get the number of explanation paths."""
        return len(self.explanation_paths)
    
    @property
    def is_valid(self) -> bool:
        """Check if explanation graph has minimal required data."""
        return (
            len(self.graph_identity) > 0 and
            len(self.explained_observations) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary for serialization."""
        return {
            "graph_identity": self.graph_identity,
            "explained_observations": list(self.explained_observations),
            "explanation_paths": [p.to_dict() for p in self.explanation_paths],
            "supporting_components": list(self.supporting_components),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExplanationGraph":
        """Create graph from dictionary."""
        paths_data = data.get("explanation_paths", [])
        explanation_paths = tuple(ExplanationPath.from_dict(p) for p in paths_data)
        
        return cls(
            graph_identity=data.get("graph_identity", str(uuid.uuid4())),
            explained_observations=tuple(data.get("explained_observations", [])),
            explanation_paths=explanation_paths,
            supporting_components=tuple(data.get("supporting_components", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        explained_observations: List[str],
        explanation_paths: Optional[List[ExplanationPath]] = None,
        supporting_components: Optional[List[str]] = None,
    ) -> "ExplanationGraph":
        """
        Create a new explanation graph.
        
        Args:
            explained_observations: The observed phenomena
            explanation_paths: Paths from observation to mechanism (optional)
            supporting_components: Components used in explanations (optional)
            
        Returns:
            A new explanation graph
        """
        return cls(
            graph_identity=f"explanation_graph:{uuid.uuid4().hex[:16]}",
            explained_observations=tuple(explained_observations),
            explanation_paths=tuple(explanation_paths or []),
            supporting_components=tuple(supporting_components or []),
            confidence=0.5,
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_explanation_path(
        self,
        path: ExplanationPath,
    ) -> "ExplanationGraph":
        """Create a revision with an additional explanation path."""
        return ExplanationGraph(
            graph_identity=self.graph_identity,
            explained_observations=self.explained_observations,
            explanation_paths=self.explanation_paths + (path,),
            supporting_components=self.supporting_components,
            confidence=self.confidence,
            provenance={
                **self.provenance,
                "path_added_at_utc": time.time(),
                "added_path_observation": path.observation,
            },
        )


# =============================================================================
# MODEL EXPLANATION - Wrapper for model-based explanations
# =============================================================================


@dataclass(frozen=True)
class ModelExplanation:
    """
    Canonical representation of a model's explanatory output.
    
    Explanations reference their originating model and provide traceable paths
    from observation to underlying mechanism.
    
    Fields:
        explanation_identity:  Unique identifier for this explanation
        source_model:          ID of the model providing the explanation
        explained_observations: Observations being explained
        explanation:           The explanatory account provided
        confidence:            Confidence in the explanation (0.0-1.0)
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    explanation_identity: str           # Unique ID for this explanation
    
    # Source model reference (required)
    source_model: str                   # Model providing the explanation
    
    # Explained observations (required)
    explained_observations: Tuple[str, ...]  # The phenomena being explained
    
    # Explanatory content
    explanation: str                    # The explanatory account
    
    # Quality metrics (required)
    confidence: float = 0.5             # Confidence in explanation (0.0-1.0)
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if explanation has minimal required data."""
        return (
            len(self.explanation_identity) > 0 and
            len(self.source_model) > 0
        )
    
    @classmethod
    def create(
        cls,
        source_model: str,
        explained_observations: List[str],
        explanation: str,
        confidence: float = 0.5,
    ) -> "ModelExplanation":
        """
        Create a new model explanation.
        
        Args:
            source_model: ID of the model providing the explanation
            explained_observations: The phenomena being explained
            explanation: The explanatory account provided
            confidence: Confidence in the explanation (0.0-1.0)
            
        Returns:
            A new explanation record
        """
        return cls(
            explanation_identity=f"explanation:{uuid.uuid4().hex[:16]}",
            source_model=source_model,
            explained_observations=tuple(explained_observations),
            explanation=explanation,
            confidence=max(0.0, min(1.0, float(confidence))),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


__all__ = [
    "ExplanationPath",
    "ExplanationGraph",
    "ModelExplanation",
]