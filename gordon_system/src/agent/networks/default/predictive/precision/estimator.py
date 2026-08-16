# Precision Estimator - Phase 4.9.4
# ===================================
"""
Precision Estimation Engine for Gordon Cognitive Architecture.

This module implements the canonical precision estimator:
    * Validates requests
    * Estimates modality reliability
    * Estimates contextual reliability  
    * Combines evidence deterministically
    * Constructs precision landscape

ARCHITECTURAL RESPONSIBILITY:
    This subsystem owns:
        - Request validation
        - Reliability estimation
        - Precision combination
        - Landscape construction
        
    This subsystem NEVER owns:
        - Prediction generation
        - Observation comparison
        - Belief revision
        - Action selection

INPUT:  PrecisionRequest (PredictionErrorState, Context, Policy)
OUTPUT: PrecisionResult (PrecisionLandscape, Trace, Status)

All computations are deterministic, stateless, and explainable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# PRECISION ESTIMATOR
# =============================================================================


@dataclass(frozen=True)
class PrecisionEstimator:
    """
    Canonical aggregate precision estimator.
    
    Orchestrates the precision estimation pipeline:
        1. Validate request
        2. Estimate modality reliability  
        3. Estimate contextual reliability
        4. Combine evidence deterministically
        5. Construct precision landscape
    
    Rules:
        - Exactly one aggregate Precision Estimator exists
        - Stateless and deterministic
        - Does not invoke other estimators directly
        - Preserves all provenance
        
    Fields:
        combination_policy:   Policy for combining reliability sources
        propagation_policy:   Policy for hierarchical propagation
        trace_events:         Trace of estimation process
    """
    
    combination_policy: str = "weighted_average"  # Policy reference
    propagation_policy: str = "hierarchical"      # Policy reference
    trace_events: tuple[str, ...] = field(default_factory=tuple)
    
    def estimate(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the precision estimation pipeline.
        
        Args:
            request: PrecisionRequest as dictionary
            
        Returns:
            PrecisionResult as dictionary
            
        Rules:
            - Deterministic output for deterministic inputs
            - Preserves provenance throughout
            - No modifications to input state
        """
        # Trace events
        trace = []
        
        # Step 1: Validate request
        self._validate_request(request)
        trace.append("REQUEST_VALIDATED")
        
        # Step 2: Extract components for estimation
        error_state = request.get("prediction_error_state", {})
        context = request.get("context", {})
        policy_ref = request.get("policy")
        
        # Step 3: Estimate modality reliability (parallel)
        modality_estimates = self._estimate_modality_reliability(error_state, context)
        trace.append("MODALITY_ESTIMATED")
        
        # Step 4: Estimate contextual reliability
        context_reliability = self._estimate_context_reliability(context)
        trace.append("CONTEXT_ESTIMATED")
        
        # Step 5: Combine evidence
        combined_precision = self._combine_estimates(modality_estimates, context_reliability)
        trace.append("PRECISION_COMBINED")
        
        # Step 6: Construct landscape
        landscape = self._construct_landscape(
            error_state=error_state,
            modality_estimates=modality_estimates,
            context_reliability=context_reliability,
            combined_precision=combined_precision,
            trace=tuple(trace)
        )
        trace.append("LANDSCAPE_CREATED")
        
        return {
            "request_identity": request.get("identity", ""),
            "landscape": landscape,
            "findings": tuple(),
            "limitations": tuple(),
            "trace": {"events": tuple(trace), "timestamp_ref": None},
            "status": "completed"
        }
    
    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate the precision estimation request."""
        if not isinstance(request, dict):
            raise ValueError("PrecisionRequest must be a dictionary")
        if "prediction_error_state" not in request:
            raise ValueError("PredictionErrorState is required")
    
    def _estimate_modality_reliability(
        self, 
        error_state: dict[str, Any], 
        context: dict[str, Any] | None
    ) -> dict[str, float]:
        """
        Estimate reliability for each modality.
        
        Returns:
            Dictionary mapping modality names to precision values [0.0, 1.0]
        """
        # Default fallback - modality estimates derived from error state
        errors = error_state.get("errors", [])
        
        modalities: dict[str, list[float]] = {}
        for error in errors:
            if isinstance(error, dict):
                modality = error.get("modality", "unknown")
                magnitude = error.get("magnitude", 0.5)
                # Inverse relationship: larger error → lower precision (simplified)
                precision = max(0.0, min(1.0, 1.0 - float(magnitude)))
                if modality not in modalities:
                    modalities[modality] = []
                modalities[modality].append(precision)
        
        # Average per modality
        return {
            modality: sum(vals) / len(vals) 
            for modality, vals in modalities.items()
            if vals
        }
    
    def _estimate_context_reliability(self, context: dict[str, Any] | None) -> float:
        """
        Estimate contextual reliability.
        
        Returns:
            Context reliability value [0.0, 1.0]
        """
        if not context:
            return 0.5  # Unknown context → medium reliability
        
        # Check for completeness indicators
        completeness = 1.0
        missing_keys = []
        
        required_context_fields = ["temporal", "spatial", "semantic"]
        for field in required_context_fields:
            if field not in context:
                missing_keys.append(field)
                completeness -= 0.2
        
        # Check for contradictions
        contradictory = context.get("contradictory", False)
        if contradictory:
            completeness -= 0.3
        
        return max(0.0, min(1.0, completeness))
    
    def _combine_estimates(
        self,
        modality_estimates: dict[str, float],
        context_reliability: float
    ) -> float:
        """
        Combine modality and contextual estimates into single precision.
        
        Returns:
            Combined precision value [0.0, 1.0]
        """
        if not modality_estimates:
            return context_reliability
        
        # Weighted average of modality estimates
        modality_weights = {m: 1.0 / len(modality_estimates) for m in modality_estimates}
        
        weighted_sum = sum(
            precision * modality_weights[modality]
            for modality, precision in modality_estimates.items()
        )
        
        # Weight context reliability at 25% and modality at 75%
        combined = weighted_sum * 0.75 + context_reliability * 0.25
        
        return max(0.0, min(1.0, combined))
    
    def _construct_landscape(
        self,
        error_state: dict[str, Any],
        modality_estimates: dict[str, float],
        context_reliability: float,
        combined_precision: float,
        trace: tuple[str, ...]
    ) -> dict[str, Any]:
        """
        Construct the complete precision landscape.
        
        Returns:
            PrecisionLandscape as dictionary
        """
        # Build estimates for each error
        errors = error_state.get("errors", [])
        estimate_list = []
        
        for i, error in enumerate(errors):
            if isinstance(error, dict):
                modality = error.get("modality", "unknown")
                modality_precision = modality_estimates.get(modality, combined_precision)
                
                estimate_list.append({
                    "identity": f"precision_{i}",
                    "target_prediction_error": error.get("identity", ""),
                    "precision": modality_precision,
                    "confidence": context_reliability * 0.5 + 0.3,
                    "uncertainty": {"decomposition": {}},
                    "sources": [
                        {
                            "source_type": "modality",
                            "value": modality_precision,
                            "weight": 1.0
                        },
                        {
                            "source_type": "context",
                            "value": context_reliability,
                            "weight": 0.25
                        }
                    ],
                    "provenance": f"estimated_from_{modality}_reliability",
                    "revision": 1
                })
        
        # Build hierarchy mapping (sensory → contextual → abstract)
        hierarchy = self._build_hierarchy(modality_estimates)
        
        return {
            "estimates": tuple(estimate_list),
            "hierarchy": hierarchy,
            "modalities": modality_estimates,
            "timescales": {},
            "cross_level_precision": [],
            "trace": {"events": trace, "timestamp_ref": None},
            "findings": (),
            "limitations": ()
        }
    
    def _build_hierarchy(self, modality_estimates: dict[str, float]) -> dict[str, Any]:
        """
        Build hierarchy mapping for precision estimates.
        
        Returns:
            Hierarchy dictionary with level mappings
        """
        sensory_modalities = {"vision", "audio", "visual", "auditory"}
        abstract_modalities = {"language", "semantic", "conceptual"}
        
        sensory_precision = {}
        contextual_precision = {}
        abstract_precision = {}
        
        for modality, precision in modality_estimates.items():
            if modality.lower() in sensory_modalities:
                sensory_precision[modality] = precision
            elif modality.lower() in abstract_modalities:
                abstract_precision[modality] = precision
            else:
                contextual_precision[modality] = precision
        
        return {
            "sensory": sensory_precision,
            "contextual": contextual_precision,
            "abstract": abstract_precision
        }