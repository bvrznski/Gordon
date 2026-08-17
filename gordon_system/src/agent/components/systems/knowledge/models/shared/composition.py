# Knowledge Model Composition - Phase 6.7
# =======================================

"""
Model Composition: Combine multiple models into larger semantic systems.

Composition preserves individual model identities while creating higher-level
semantic structures for complex system representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# COMPOSITION STRATEGY - How models are combined
# =============================================================================


class CompositionStrategy(Enum):
    """
    Strategies for combining models.
    
    Each composition shall use an explicit strategy defining how components
    integrate.
    """
    
    NESTING = "nesting"               # Child model nested within parent
    MERGING = "merging"             # Models merged into unified whole
    CHAINING = "chaining"           # Sequential dependency chain
    PARALLEL = "parallel"           # Independent parallel models


# =============================================================================
# MODEL COMPOSITION - Canonical composition record
# =============================================================================


@dataclass(frozen=True)
class ModelComposition:
    """
    Canonical representation of model composition in Gordon's knowledge system.
    
    Composition preserves individual model identities while creating higher-level
    semantic structures.
    
    Fields:
        composition_identity:  Unique identifier for this composition event
        component_models:      IDs of models being composed
        resulting_model:       ID of the composite model created
        composition_strategy:  How the composition was performed
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    composition_identity: str           # Unique ID for this composition event
    
    # Component models (required)
    component_models: Tuple[str, ...]   # IDs of composed models
    
    # Result model reference
    resulting_model: str                # ID of the composite model created
    
    # Composition strategy
    composition_strategy: CompositionStrategy = CompositionStrategy.NESTING
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def component_count(self) -> int:
        """Get the number of component models."""
        return len(self.component_models)
    
    @property
    def is_nesting(self) -> bool:
        """Check if this is a nesting composition."""
        return self.composition_strategy == CompositionStrategy.NESTING
    
    @property
    def is_merging(self) -> bool:
        """Check if this is a merging composition."""
        return self.composition_strategy == CompositionStrategy.MERGING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert composition to dictionary for serialization."""
        return {
            "composition_identity": self.composition_identity,
            "component_models": list(self.component_models),
            "resulting_model": self.resulting_model,
            "composition_strategy": self.composition_strategy.value if self.composition_strategy else None,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelComposition":
        """Create composition from dictionary."""
        strategy_value = data.get("composition_strategy", "nesting")
        try:
            composition_strategy = CompositionStrategy(strategy_value)
        except ValueError:
            composition_strategy = CompositionStrategy.NESTING
        
        return cls(
            composition_identity=data.get("composition_identity", str(uuid.uuid4())),
            component_models=tuple(data.get("component_models", [])),
            resulting_model=data.get("resulting_model", ""),
            composition_strategy=composition_strategy,
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        component_models: List[str],
        resulting_model: str,
        strategy: CompositionStrategy = CompositionStrategy.NESTING,
    ) -> "ModelComposition":
        """
        Create a new model composition record.
        
        Args:
            component_models: IDs of models being composed
            resulting_model: ID of the composite model created
            strategy: How the composition was performed
            
        Returns:
            A new composition record
        """
        return cls(
            composition_identity=f"composition:{uuid.uuid4().hex[:16]}",
            component_models=tuple(component_models),
            resulting_model=resulting_model,
            composition_strategy=strategy,
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_component(
        self,
        component_id: str,
    ) -> "ModelComposition":
        """Create a revision with an additional component model."""
        if component_id in self.component_models:
            return self
        return ModelComposition(
            composition_identity=self.composition_identity,
            component_models=self.component_models + (component_id,),
            resulting_model=self.resulting_model,
            composition_strategy=self.composition_strategy,
            provenance={
                **self.provenance,
                "component_added": component_id,
                "revised_at_utc": time.time(),
            },
        )


# =============================================================================
# COMPOSITION BUILDER
# =============================================================================


class CompositionBuilder:
    """
    Builds and validates model compositions.
    
    Ensures composition preserves model identities and tracks provenance.
    """
    
    def __init__(
        self,
        require_components: bool = True,
        validate_strategy: bool = True,
    ):
        """
        Initialize the builder.
        
        Args:
            require_components: Whether component models are required
            validate_strategy: Whether to enforce strategy rules
        """
        self._require_components = require_components
        self._validate_strategy = validate_strategy
    
    def validate_composition(
        self,
        composition: ModelComposition,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a model composition.
        
        Args:
            composition: The composition to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if not composition.composition_identity or len(composition.composition_identity) == 0:
            issues.append("Missing composition identity")
        
        if self._require_components and len(composition.component_models) < 1:
            issues.append("Composition must have at least one component model")
        
        if not composition.resulting_model or len(composition.resulting_model) == 0:
            issues.append("Missing resulting model reference")
        
        if self._validate_strategy and (
            composition.composition_strategy not in CompositionStrategy
        ):
            issues.append(f"Invalid composition strategy: {composition.composition_strategy}")
        
        return len(issues) == 0, issues
    
    def build_composition(
        self,
        component_models: List[str],
        resulting_model: str,
        strategy: CompositionStrategy = CompositionStrategy.NESTING,
    ) -> ModelComposition:
        """
        Build a new model composition.
        
        Args:
            component_models: IDs of models to compose
            resulting_model: ID for the composite model
            strategy: How to combine the models
            
        Returns:
            A new composition record
        """
        return ModelComposition.create(
            component_models=component_models,
            resulting_model=resulting_model,
            strategy=strategy,
        )
    
    def build_nesting_composition(
        self,
        parent_model: str,
        child_model: str,
    ) -> ModelComposition:
        """
        Build a nesting composition (convenience method).
        
        Args:
            parent_model: ID of the parent model
            child_model: ID of the nested child model
            
        Returns:
            A new nesting composition record
        """
        return self.build_composition(
            component_models=[parent_model, child_model],
            resulting_model=f"{parent_model}_composite",
            strategy=CompositionStrategy.NESTING,
        )


__all__ = [
    "CompositionStrategy",
    "ModelComposition",
    "CompositionBuilder",
]