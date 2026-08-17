# Knowledge Model Prediction - Phase 6.7
# ======================================

"""
Model Predictions: Estimate future states based on model dynamics.

Predictions are distinct from beliefs - they represent what a model would produce
given certain inputs, not what is currently accepted as true.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PREDICTION SESSION - Context for making predictions
# =============================================================================


@dataclass(frozen=True)
class PredictionSession:
    """
    Context for model prediction operations.
    
    A prediction session owns the state and parameters needed to make predictions.
    
    Fields:
        session_identity:      Unique identifier for this prediction session
        model:                 ID of the model making predictions
        inputs:                Input states for prediction
        assumptions:           Active assumptions during prediction
        predicted_states:      States predicted by the model
        confidence:            Confidence in predictions (0.0-1.0)
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    session_identity: str               # Unique ID for this session
    
    # Model reference (required)
    model: str                          # ID of the prediction model
    
    # Input state
    inputs: Dict[str, Any] = field(default_factory=dict)  # Input states
    
    # Active assumptions
    assumptions: Tuple[str, ...] = field(default_factory=tuple)  # Assumption IDs
    
    # Predicted outputs
    predicted_states: Tuple[str, ...] = field(default_factory=tuple)  # Output states
    
    # Confidence metrics (required)
    confidence: float = 0.5             # Confidence in predictions (0.0-1.0)
    
    # Uncertainty tracking
    uncertainty: float = 0.5            # Uncertainty about predictions (0.0-1.0)
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if prediction session has minimal required data."""
        return (
            len(self.session_identity) > 0 and
            len(self.model) > 0
        )
    
    @property
    def confidence_complement(self) -> float:
        """Calculate 1 - confidence (uncertainty measure)."""
        return max(0.0, min(1.0, 1.0 - self.confidence))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_identity": self.session_identity,
            "model": self.model,
            "inputs": dict(self.inputs),
            "assumptions": list(self.assumptions),
            "predicted_states": list(self.predicted_states),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredictionSession":
        """Create session from dictionary."""
        return cls(
            session_identity=data.get("session_identity", str(uuid.uuid4())),
            model=data.get("model", ""),
            inputs=dict(data.get("inputs", {})),
            assumptions=tuple(data.get("assumptions", [])),
            predicted_states=tuple(data.get("predicted_states", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        model: str,
        inputs: Optional[Dict[str, Any]] = None,
        assumptions: Optional[List[str]] = None,
    ) -> "PredictionSession":
        """
        Create a new prediction session.
        
        Args:
            model: ID of the model making predictions
            inputs: Input states (optional)
            assumptions: Active assumptions (optional)
            
        Returns:
            A new prediction session
        """
        return cls(
            session_identity=f"prediction_session:{uuid.uuid4().hex[:16]}",
            model=model,
            inputs=dict(inputs or {}),
            assumptions=tuple(assumptions or []),
            confidence=0.5,
            uncertainty=0.5,
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def add_input(
        self,
        input_name: str,
        value: Any,
    ) -> "PredictionSession":
        """Create a revision with an additional input."""
        return PredictionSession(
            session_identity=self.session_identity,
            model=self.model,
            inputs={**self.inputs, input_name: value},
            assumptions=self.assumptions,
            predicted_states=self.predicted_states,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance={
                **self.provenance,
                "input_added": input_name,
                "revised_at_utc": time.time(),
            },
        )


# =============================================================================
# MODEL PREDICTION - Record of a specific prediction
# =============================================================================


@dataclass(frozen=True)
class ModelPrediction:
    """
    Canonical representation of a model prediction in Gordon's knowledge system.
    
    Predictions remain distinguishable from beliefs and are probabilistic.
    
    Fields:
        prediction_identity:   Unique identifier for this prediction
        source_model:          ID of the model making the prediction
        predicted_state:       The state that was predicted
        confidence:            Confidence level (0.0-1.0)
        uncertainty:           Uncertainty about the prediction (0.0-1.0)
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    prediction_identity: str            # Unique ID for this prediction
    
    # Source model reference (required)
    source_model: str                   # Model making the prediction
    
    # Predicted state (required) - can be any state description
    predicted_state: str                # Description of the predicted state
    
    # Quality metrics (required)
    confidence: float = 0.5             # Confidence level (0.0-1.0)
    uncertainty: float = 0.5            # Uncertainty (0.0-1.0)
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if prediction has minimal required data."""
        return (
            len(self.prediction_identity) > 0 and
            len(self.source_model) > 0
        )
    
    @classmethod
    def create(
        cls,
        source_model: str,
        predicted_state: str,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> "ModelPrediction":
        """
        Create a new model prediction.
        
        Args:
            source_model: ID of the model making the prediction
            predicted_state: Description of the predicted state
            confidence: Confidence level (0.0-1.0)
            uncertainty: Uncertainty about the prediction (0.0-1.0)
            
        Returns:
            A new prediction record
        """
        return cls(
            prediction_identity=f"prediction:{uuid.uuid4().hex[:16]}",
            source_model=source_model,
            predicted_state=predicted_state,
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


__all__ = [
    "PredictionSession",
    "ModelPrediction",
]