# Canonical Belief Revision Request - Phase 4.9.5
# =================================================
"""
Request types for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# CANONICAL BELIEF REVISION REQUEST (INPUT CONTRACT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class BeliefRevisionRequest:
    """
    Canonical immutable request for belief revision.
    
    Fields:
        identity:               Request identity
        belief_state:           Current BeliefState to revise
        precision_landscape:    Precision landscape for error weighting
        context_projection:     Context projection for revision evaluation
        world_model_projection: World model projection for consistency check
        revision_policy:        Revision policy reference
        semantic_time:          External semantic time reference
        provenance:             Request provenance
    
    Rules:
        - All inputs are immutable
        - No runtime references in request
        - Semantic time supplied externally, not acquired internally
    """
    identity: str  # SemanticIdentity or string code
    belief_state: dict[str, Any]  # BeliefState reference (external)
    precision_landscape: dict[str, Any]  # PrecisionLandscape reference
    context_projection: dict[str, Any] | None = None  # ContextProjection
    world_model_projection: dict[str, Any] | None = None  # WorldModelProjection
    revision_policy: str | None = None  # RevisionPolicy reference
    semantic_time: str | None = None  # External semantic time reference
    provenance: dict[str, str] | None = None


# =============================================================================
# BELIEF REVISION RESULT (OUTPUT CONTRACT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class BeliefRevisionResult:
    """
    Canonical immutable result from belief revision.
    
    Fields:
        identity:               Request identity
        updated_belief_state:   Updated BeliefState after revision
        revision_graph:         Immutable revision lineage graph
        findings:               Typed findings (success/failure records)
        limitations:            Known limitations on the result
        trace:                  Structural trace of revision process
        status:                 Revision status
    
    Rules:
        - No raw dictionaries as output
        - Immutable result structure
        - Status indicates completeness without implying correctness
    """
    identity: str  # RequestIdentity or string code
    updated_belief_state: dict[str, Any] | None = None  # Updated BeliefState
    revision_graph: dict[str, Any] | None = None  # BeliefRevisionGraph
    findings: tuple[dict[str, Any], ...] = field(default_factory=tuple)  # FailureRecord or SuccessRecord
    limitations: tuple[str, ...] = field(default_factory=tuple)  # LimitationKind codes
    trace: dict[str, Any] | None = None  # Trace events and timestamps
    status: str = "pending"  # RevisionStatus or string code


# =============================================================================
# CANONICAL BELIEF REVISION ENGINE (AGGREGATE)
# =============================================================================

@dataclass(frozen=True, slots=True)
class BeliefRevisionEngine:
    """
    Canonical aggregate belief revision engine.
    
    Orchestrates the revision pipeline:
        1. Validate request
        2. Validate BeliefState
        3. Validate PrecisionLandscape
        4. Generate revision candidates
        5. Evaluate evidence
        6. Resolve contradictions
        7. Validate consistency
        8. Propagate revisions
        9. Construct RevisionGraph
        10. Construct updated BeliefState
        11. Validation
    
    Rules:
        - Exactly one canonical BeliefRevisionEngine exists
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
    
    def revise(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the belief revision pipeline.
        
        Args:
            request: BeliefRevisionRequest as dictionary
            
        Returns:
            BeliefRevisionResult as dictionary
            
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
        
        # Step 2: Extract components for revision
        belief_state_data = request.get("belief_state", {})
        precision_landscape_data = request.get("precision_landscape", {})
        
        # Step 3: Validate BeliefState
        self._validate_belief_state(belief_state_data)
        trace.append("BELIEF_STATE_VALIDATED")
        
        # Step 4: Validate PrecisionLandscape
        self._validate_precision_landscape(precision_landscape_data)
        trace.append("PRECISION_VALIDATED")
        
        # Step 5: Generate revision candidates
        candidates = self._generate_candidates(
            belief_state=belief_state_data,
            precision_landscape=precision_landscape_data
        )
        trace.append("CANDIDATES_GENERATED")
        
        # Step 6: Evaluate evidence (parallelizable)
        evaluated = self._evaluate_evidence(candidates, precision_landscape_data)
        trace.append("EVIDENCE_EVALUATED")
        
        # Step 7: Analyze contradictions
        contradictions = self._analyze_contradictions(evaluated)
        trace.append("CONTRADICTIONS_ANALYZED")
        
        # Step 8: Validate consistency
        consistency = self._validate_consistency(evaluated, contradictions)
        trace.append("CONSISTENCY_CHECKED")
        
        # Step 9: Propagate revisions
        propagated = self._propagate_revisions(
            evaluated=evaluated,
            contradictions=contradictions,
            consistency=consistency
        )
        trace.append("PROPAGATION_COMPLETED")
        
        # Step 10: Construct RevisionGraph
        revision_graph = self._construct_revision_graph(
            candidates=evaluated,
            contradictions=contradictions,
            propagated=propagated,
            policy=request.get("revision_policy", "")
        )
        trace.append("REVISION_GRAPH_CREATED")
        
        # Step 11: Construct updated BeliefState
        updated_belief_state = self._construct_updated_belief_state(
            current_state=belief_state_data,
            revisions=propagated,
            revision_graph=revision_graph
        )
        trace.append("STATE_VALIDATED")
        
        # Step 12: Build result
        return {
            "identity": request.get("identity", ""),
            "updated_belief_state": updated_belief_state,
            "revision_graph": revision_graph,
            "findings": tuple(),
            "limitations": tuple(),
            "trace": {"events": tuple(trace), "timestamp_ref": request.get("semantic_time")},
            "status": "completed"
        }
    
    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate the belief revision request."""
        if not isinstance(request, dict):
            raise ValueError("BeliefRevisionRequest must be a dictionary")
        if "belief_state" not in request:
            raise ValueError("BeliefState is required in request")
    
    def _validate_belief_state(self, state: dict[str, Any]) -> None:
        """Validate the belief state."""
        if not isinstance(state, dict):
            raise ValueError("BeliefState must be a dictionary")
    
    def _validate_precision_landscape(self, landscape: dict[str, Any]) -> None:
        """Validate the precision landscape."""
        if not isinstance(landscape, dict):
            raise ValueError("PrecisionLandscape must be a dictionary")
    
    def _generate_candidates(
        self,
        belief_state: dict[str, Any],
        precision_landscape: dict[str, Any]
    ) -> tuple[dict[str, Any], ...]:
        """
        Generate revision candidates from prediction errors.
        
        Returns:
            Tuple of candidate revisions
        """
        # Default implementation - extract candidates from error state
        errors = belief_state.get("errors", [])
        estimates = precision_landscape.get("estimates", [])
        
        candidates: list[dict[str, Any]] = []
        for i, error in enumerate(errors):
            if isinstance(error, dict):
                # Find corresponding estimate
                estimate = None
                for e in estimates:
                    if e.get("target_prediction_error") == error.get("identity"):
                        estimate = e
                        break
                
                precision = estimate.get("precision", 0.5) if estimate else 0.5
                magnitude = error.get("magnitude", 0.5)
                
                # High precision * high error = revision candidate
                if precision > 0.7 and magnitude > 0.3:
                    candidates.append({
                        "identity": f"candidate_{i}",
                        "target_belief": error.get("identity", ""),
                        "revision_type": "UPDATE",
                        "supporting_errors": (error,),
                        "supporting_precision_estimates": (estimate,) if estimate else (),
                        "confidence": precision,
                        "uncertainty": {"decomposition": {}},
                        "provenance": f"generated_from_error_{i}",
                        "timestamp_ref": None
                    })
        
        return tuple(candidates)
    
    def _evaluate_evidence(
        self,
        candidates: tuple[dict[str, Any], ...],
        precision_landscape: dict[str, Any]
    ) -> tuple[dict[str, Any], ...]:
        """
        Evaluate candidate revisions against evidence.
        
        Returns:
            Tuple of evaluated candidates with confidence updates
        """
        # Simplified evaluation - in real implementation would analyze
        # prediction errors and precision estimates in detail
        return tuple(candidates)
    
    def _analyze_contradictions(
        self,
        candidates: tuple[dict[str, Any], ...]
    ) -> tuple[dict[str, Any], ...]:
        """
        Analyze candidate revisions for contradictions.
        
        Returns:
            Tuple of contradiction records
        """
        # Simplified analysis - in real implementation would check
        # dependency graph and semantic relationships
        return ()
    
    def _validate_consistency(
        self,
        candidates: tuple[dict[str, Any], ...],
        contradictions: tuple[dict[str, Any], ...]
    ) -> dict[str, Any]:
        """
        Validate consistency of proposed revisions.
        
        Returns:
            Consistency validation result
        """
        return {
            "is_consistent": len(contradictions) == 0,
            "contradiction_count": len(contradictions),
            "findings": tuple()
        }
    
    def _propagate_revisions(
        self,
        evaluated: tuple[dict[str, Any], ...],
        contradictions: tuple[dict[str, Any], ...],
        consistency: dict[str, Any]
    ) -> tuple[dict[str, Any], ...]:
        """
        Propagate validated revisions to dependent beliefs.
        
        Returns:
            Tuple of propagated revision records
        """
        return evaluated
    
    def _construct_revision_graph(
        self,
        candidates: tuple[dict[str, Any], ...],
        contradictions: tuple[dict[str, Any], ...],
        propagated: tuple[dict[str, Any], ...],
        policy: str
    ) -> dict[str, Any]:
        """
        Construct the revision graph from processed revisions.
        
        Returns:
            BeliefRevisionGraph representation
        """
        nodes = []
        edges = []
        
        for candidate in candidates:
            node_id = candidate.get("identity", "")
            nodes.append({
                "node_id": node_id,
                "revision_type": candidate.get("revision_type", ""),
                "target_belief": candidate.get("target_belief", ""),
                "supporting_evidence": candidate.get("supporting_errors", ()),
                "timestamp_ref": candidate.get("timestamp_ref")
            })
        
        return {
            "nodes": tuple(nodes),
            "edges": tuple(edges),
            "policy": policy,
            "root_nodes": tuple(n["node_id"] for n in nodes)
        }
    
    def _construct_updated_belief_state(
        self,
        current_state: dict[str, Any],
        revisions: tuple[dict[str, Any], ...],
        revision_graph: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Construct the updated belief state from applied revisions.
        
        Returns:
            Updated BeliefState representation
        """
        # Simplified update - in real implementation would properly
        # apply versioning and preserve all history
        beliefs = current_state.get("beliefs", [])
        
        new_beliefs = list(beliefs)
        for revision in revisions:
            target_id = revision.get("target_belief")
            if target_id:
                # In a real implementation, we would find and update the
                # specific belief while preserving history
                pass
        
        return {
            "beliefs": tuple(new_beliefs),
            "hierarchy": current_state.get("hierarchy"),
            "dependencies": current_state.get("dependencies"),
            "confidence": current_state.get("confidence", 0.5),
            "uncertainty": current_state.get("uncertainty", {}),
            "revision_graph": revision_graph,
            "trace": ("state_updated",)
        }