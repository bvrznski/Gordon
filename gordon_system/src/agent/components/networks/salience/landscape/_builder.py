# Salience Network Landscape Builder
# ===================================

"""
Canonical Global Salience Landscape builder (Phase 4.8.8).

The LandscapeBuilder constructs immutable LandscapeState from validated inputs.
It performs deterministic aggregation of Candidate dynamics into a global landscape.

LANDSCAPE BUILDER INVARIANTS:
    LB-INV-001: Builder is stateless (pure functions only)
    LB-INV-002: Deterministic output for equivalent input
    LB-INV-003: No runtime behavior or scheduling
    LB-INV-004: All estimations are advisory only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

# Relative imports for module-level usage
from ._request import (
    LandscapeRequest,
    LandscapePolicy,
    ContextProjection,
)
from ._state import (
    GlobalActivation,
    BaselineSalience,
    ResourcePressure,
    CognitiveLoad,
    EnvironmentalLoad,
    NoveltyDensity,
    ConflictDensity,
    UncertaintyDensity,
    UrgencyDensity,
    ContextualGradient,
    SalienceHotspot,
    SystemCoherence,
    SystemReadiness,
    LandscapeState,
    GLOBAL_ACTIVATION_LEVELS,
    PRESSURE_LEVELS,
    COGNITIVE_LOAD_LEVELS,
    ENVIRONMENTAL_LOAD_LEVELS,
    NOVELTY_LEVELS,
    CONFLICT_LEVELS,
    UNCERTAINTY_LEVELS,
    URGENCY_LEVELS,
    COHERENCE_LEVELS,
    READINESS_LEVELS,
)


@dataclass(frozen=True)
class LandscapeBuilder:
    """
    Immutable builder for Global Salience Landscape.
    
    The builder performs pure function aggregation of Candidate states
    into a global salience landscape without runtime behavior.
    
    BUILDER INVARIANTS:
        LB-INV-001: Builder is stateless (pure functions only)
        LB-INV-002: Deterministic output for equivalent input
        LB-INV-003: No runtime behavior or scheduling
        LB-INV-004: All estimations are advisory only
    """
    
    # Policy reference (immutable)
    policy: LandscapePolicy = field(default_factory=LandscapePolicy)
    """Construction policy for estimations."""
    
    # Request context (for traceability)
    request: LandscapeRequest | None = None
    """Source request being built."""
    
    def build_landscape(self, request: LandscapeRequest) -> Tuple[LandscapeState, Tuple[str, ...]]:
        """
        Construct Global Salience Landscape from validated inputs.
        
        Pipeline:
            1. Validate request
            2. Normalize Candidate influence
            3. Aggregate activation estimates
            4. Estimate baseline salience
            5. Estimate resource pressure
            6. Estimate cognitive load
            7. Estimate environmental load
            8. Estimate density metrics (novelty, conflict, uncertainty)
            9. Detect hotspots
            10. Estimate contextual gradients
            11. Estimate coherence
            12. Estimate readiness
            13. Construct trace
            
        Args:
            request: Validated LandscapeRequest
            
        Returns:
            Tuple of (LandscapeState, trace records)
            
        Raises:
            ValueError: If request validation fails
        """
        # Validate inputs
        validation_errors = self._validate_request(request)
        if validation_errors:
            raise ValueError(f"Invalid LandscapeRequest: {validation_errors}")
        
        traces = ["LANDSCAPE_BUILD"]
        
        # 1. Aggregate Candidate dynamics (normalization + aggregation)
        normalized_candidates, norm_trace = self._normalize_candidates(request.candidate_states, request.adaptive_states, request.landscape_policy)
        traces.extend(norm_trace)
        
        # 2. Estimate global activation
        global_activation, act_trace = self._estimate_activation(normalized_candidates, request.landscape_policy)
        traces.extend(act_trace)
        
        # 3. Estimate baseline salience
        baseline_salience, base_trace = self._estimate_baseline(request.candidate_states, global_activation, request.context_projection, request.landscape_policy)
        traces.extend(base_trace)
        
        # 4. Estimate resource pressure
        resource_pressure, pres_trace = self._estimate_resource_pressure(normalized_candidates, request.competition_result, request.landscape_policy)
        traces.extend(pres_trace)
        
        # 5. Estimate cognitive load
        cognitive_load, load_trace = self._estimate_cognitive_load(normalized_candidates, resource_pressure, request.context_projection, request.landscape_policy)
        traces.extend(load_trace)
        
        # 6. Estimate environmental load
        environmental_load, env_trace = self._estimate_environmental_load(request.context_projection, request.candidate_states, request.landscape_policy)
        traces.extend(env_trace)
        
        # 7. Estimate density metrics
        novelty_density, nov_trace = self._estimate_novelty_density(normalized_candidates, request.landscape_policy)
        traces.extend(nov_trace)
        
        conflict_density, conf_trace = self._estimate_conflict_density(normalized_candidates, request.competition_result, request.landscape_policy)
        traces.extend(conf_trace)
        
        uncertainty_density, unc_trace = self._estimate_uncertainty_density(normalized_candidates, request.landscape_policy)
        traces.extend(unc_trace)
        
        urgency_density, urg_trace = self._estimate_urgency_density(normalized_candidates, request.competition_result, request.context_projection, request.landscape_policy)
        traces.extend(urg_trace)
        
        # 8. Detect hotspots
        hotspots, hotspot_trace = self._detect_hotspots(normalized_candidates, request.landscape_policy)
        traces.extend(hotspot_trace)
        
        # 9. Estimate contextual gradients
        gradients, grad_trace = self._estimate_gradients(request.context_projection, normalized_candidates, request.landscape_policy)
        traces.extend(grad_trace)
        
        # 10. Estimate coherence
        coherence, coh_trace = self._estimate_coherence(normalized_candidates, conflict_density, uncertainty_density, request.landscape_policy)
        traces.extend(coh_trace)
        
        # 11. Estimate readiness
        readiness, ready_trace = self._estimate_readiness(global_activation, cognitive_load, resource_pressure, coherent_system=coherence.is_coherent or coherence.is_partially_coherent)
        traces.extend(ready_trace)
        
        # 12. Construct final state
        landscape_state = LandscapeState(
            identity=request.identity,
            global_activation=global_activation,
            baseline_salience=baseline_salience,
            resource_pressure=resource_pressure,
            cognitive_load=cognitive_load,
            environmental_load=environmental_load,
            novelty_density=novelty_density,
            conflict_density=conflict_density,
            uncertainty_density=uncertainty_density,
            urgency_density=urgency_density,
            contextual_gradients=gradients,
            salience_hotspots=hotspots,
            system_coherence=coherence,
            system_readiness=readiness,
            trace=tuple(traces),
        )
        
        return landscape_state, tuple(traces)
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def _validate_request(self, request: LandscapeRequest) -> Tuple[str, ...]:
        """
        Validate LandscapeRequest structure.
        
        Args:
            request: Request to validate
            
        Returns:
            Tuple of error messages (empty if valid)
        """
        errors = []
        
        # Check candidate states
        if not isinstance(request.candidate_states, tuple):
            errors.append("candidate_states must be tuple")
        
        for i, cand in enumerate(request.candidate_states):
            if not isinstance(cand, dict):
                errors.append(f"candidate_states[{i}] must be dict")
                continue
            if "state_identity" not in cand:
                errors.append(f"candidate_states[{i}] missing state_identity")
        
        # Check adaptive states
        for i, adap in enumerate(request.adaptive_states):
            if not isinstance(adap, dict):
                errors.append(f"adaptive_states[{i}] must be dict")
                continue
            if "candidate_id" not in adap:
                errors.append(f"adaptive_states[{i}] missing candidate_id")
        
        return tuple(errors)
    
    # =========================================================================
    # NORMALIZATION
    # =========================================================================
    
    def _normalize_candidates(self, candidates: Tuple[dict, ...], adaptive: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[Tuple[dict, ...], Tuple[str, ...]]:
        """
        Normalize Candidate influence scores.
        
        Normalization preserves:
            - Evidence
            - Authority  
            - Confidence
            - Uncertainty
        
        Args:
            candidates: Candidate state dictionaries
            adaptive: Adaptive state dictionaries
            policy: Construction policy
            
        Returns:
            Tuple of (normalized_candidates, traces)
        """
        if not policy.normalize_activation or len(candidates) == 0:
            return candidates, ("NORMALIZATION_SKIPPED",)
        
        # Collect all values for normalization bounds
        values = []
        for cand in candidates:
            value = cand.get("overall_level", 0.5)
            values.append(value)
        
        if not values:
            return candidates, ("NORMALIZATION_EMPTY",)
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val != min_val else 1.0
        
        # Normalize to policy scale
        normalized = []
        traces = ["NORMALIZATION"]
        
        for i, cand in enumerate(candidates):
            value = cand.get("overall_level", 0.5)
            
            if range_val == 0:
                norm_value = policy.activation_scale_min + (policy.activation_scale_max - policy.activation_scale_min) * 0.5
            else:
                # Normalize to 0-1, then scale to policy range
                normalized_01 = (value - min_val) / range_val
                norm_value = policy.activation_scale_min + (policy.activation_scale_max - policy.activation_scale_min) * normalized_01
            
            # Create copy with normalized value
            new_cand = dict(cand)
            new_cand["normalized_level"] = round(norm_value, 4)
            
            # Apply adaptive modifiers if available
            for adap in adaptive:
                if adap.get("candidate_id") == cand.get("state_identity"):
                    habituation = adap.get("habituation_level", 0.0)
                    recovery = adap.get("recovery_state", {}).get("level", 1.0)
                    # Apply habituation reduction and recovery boost
                    new_cand["normalized_level"] *= (1.0 - habituation) * recovery
            
            normalized.append(new_cand)
        
        traces.append(f"NORMALIZED_{len(normalized)}_CANDIDATES")
        
        return tuple(normalized), tuple(traces)
    
    # =========================================================================
    # ACTIVATION ESTIMATION
    # =========================================================================
    
    def _estimate_activation(self, candidates: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[GlobalActivation, Tuple[str, ...]]:
        """
        Estimate global activation from normalized Candidates.
        
        Args:
            candidates: Normalized candidate states
            policy: Construction policy
            
        Returns:
            Tuple of (GlobalActivation, traces)
        """
        if not candidates:
            return GlobalActivation(level="QUIESCENT", value=0.0), ("ACTIVATION_QUIESCENT",)
        
        # Calculate aggregate activation from all candidates
        values = [cand.get("normalized_level", 0.5) for cand in candidates]
        avg_activation = sum(values) / len(values) if values else 0.0
        
        traces = ["ACTIVATION"]
        
        # Determine level based on threshold
        if avg_activation < 0.1:
            level = "QUIESCENT"
        elif avg_activation < 0.3:
            level = "LOW"
        elif avg_activation < 0.6:
            level = "MODERATE"
        elif avg_activation < 0.9:
            level = "HIGH"
        else:
            level = "EXTREME"
        
        traces.append(f"ACTIVATION_LEVEL_{level}")
        
        return GlobalActivation(
            level=level,
            value=round(avg_activation, 4),
            evidence_basis=tuple(c.get("state_identity", "") for c in candidates[:5]),  # Top 5 candidates
        ), tuple(traces)
    
    # =========================================================================
    # BASELINE ESTIMATION
    # =========================================================================
    
    def _estimate_baseline(self, candidates: Tuple[dict, ...], activation: GlobalActivation, context: ContextProjection, policy: LandscapePolicy) -> Tuple[BaselineSalience, Tuple[str, ...]]:
        """
        Estimate baseline salience for current semantic environment.
        
        Args:
            candidates: Normalized candidate states
            activation: Current global activation
            context: Semantic context projection
            policy: Construction policy
            
        Returns:
            Tuple of (BaselineSalience, traces)
        """
        if not candidates and not policy.auto_adjust_baseline:
            return BaselineSalience(level=policy.baseline_reference_level), ("BASELINE_FIXED",)
        
        # Adjust baseline based on activation level
        if policy.auto_adjust_baseline:
            if activation.level == "QUIESCENT":
                level = "LOW"
            elif activation.level in ("LOW", "MODERATE"):
                level = "MODERATE"
            else:
                level = "HIGH"
        else:
            level = policy.baseline_reference_level
        
        traces = ["BASELINE", f"BASELINE_LEVEL_{level}"]
        
        return BaselineSalience(
            level=level,
            reference_delta=0,  # Would be provided externally
            context_basis=context.context_ids if context.context_ids else ("default",),
        ), tuple(traces)
    
    # =========================================================================
    # RESOURCE PRESSURE ESTIMATION
    # =========================================================================
    
    def _estimate_resource_pressure(self, candidates: Tuple[dict, ...], competition: dict, policy: LandscapePolicy) -> Tuple[ResourcePressure, Tuple[str, ...]]:
        """
        Estimate semantic competition for cognitive resources.
        
        Args:
            candidates: Normalized candidate states
            competition: Competition result dictionary
            policy: Construction policy
            
        Returns:
            Tuple of (ResourcePressure, traces)
        """
        if not candidates:
            return ResourcePressure(level="MINIMAL", value=0.0), ("PRESSURE_MINIMAL",)
        
        # Calculate pressure from multiple factors
        candidate_count_factor = min(1.0, len(candidates) / 20.0)  # Scale to 20 candidates max
        
        # Conflict factor from competition result
        conflict_score = self._extract_conflict_score(competition)
        
        # Urgency factor from candidates
        urgency_values = [cand.get("urgency", {}).get("level", 0) for cand in candidates]
        avg_urgency = sum(urgency_values) / len(urgency_values) if urgency_values else 0.0
        
        # Calculate composite pressure
        pressure_value = (
            candidate_count_factor * 0.3 +
            conflict_score * policy.conflict_weight * 0.4 +
            avg_urgency * policy.urgency_weight * 0.3
        )
        
        traces = ["PRESSURE"]
        
        if pressure_value < 0.1:
            level = "MINIMAL"
        elif pressure_value < 0.3:
            level = "LOW"
        elif pressure_value < 0.6:
            level = "MODERATE"
        elif pressure_value < 0.9:
            level = "HIGH"
        else:
            level = "CRITICAL"
        
        traces.append(f"PRESSURE_LEVEL_{level}")
        traces.append(f"CANDIDATE_COUNT_CONTRIBUTION={round(candidate_count_factor, 2)}")
        traces.append(f"CONFLICT_CONTRIBUTION={round(conflict_score, 2)}")
        traces.append(f"URGENCY_CONTRIBUTION={round(avg_urgency, 2)}")
        
        return ResourcePressure(
            level=level,
            value=round(pressure_value, 4),
            contributors=tuple(f"candidate_count:{len(candidates)}", f"conflict_score:{round(conflict_score, 2)}"),
            pressure_basis=("semantic_competition_for_resources",),
        ), tuple(traces)
    
    def _extract_conflict_score(self, competition: dict) -> float:
        """Extract conflict score from competition result."""
        # Check for dominance relationships
        dominance_graph = competition.get("dominance_graph", {})
        if isinstance(dominance_graph, dict):
            edges = len(dominance_graph.get("edges", []))
            return min(1.0, edges / 10.0)
        return 0.0
    
    # =========================================================================
    # COGNITIVE LOAD ESTIMATION
    # =========================================================================
    
    def _estimate_cognitive_load(self, candidates: Tuple[dict, ...], pressure: ResourcePressure, context: ContextProjection, policy: LandscapePolicy) -> Tuple[CognitiveLoad, Tuple[str, ...]]:
        """
        Estimate overall processing demand.
        
        Args:
            candidates: Normalized candidate states
            pressure: Current resource pressure estimate
            context: Semantic context projection
            policy: Construction policy
            
        Returns:
            Tuple of (CognitiveLoad, traces)
        """
        if not candidates:
            return CognitiveLoad(level="MINIMAL", value=0.0), ("LOAD_MINIMAL",)
        
        # Calculate load from factors
        candidate_complexity = sum(
            len(cand.get("assessment", {}).get("conflict", {}).get("level", 0)) > 2
            for cand in candidates
        ) / max(1, len(candidates))
        
        uncertainty_factor = sum(
            cand.get("uncertainty", {}).get("level", 0) > 0.7
            for cand in candidates
        ) / max(1, len(candidates))
        
        # Combine factors with pressure contribution
        load_value = (
            min(1.0, len(candidates) / 15.0) * 0.2 +
            candidate_complexity * 0.3 +
            uncertainty_factor * 0.3 +
            pressure.value * 0.2
        )
        
        traces = ["COGNITIVE_LOAD"]
        
        if load_value < 0.2:
            level = "MINIMAL"
        elif load_value < 0.4:
            level = "LOW"
        elif load_value < 0.7:
            level = "MODERATE"
        elif load_value < 0.9:
            level = "HIGH"
        else:
            level = "OVERLOADED"
        
        traces.append(f"LOAD_LEVEL_{level}")
        traces.append(f"CANDIDATES:{len(candidates)}")
        traces.append(f"COMPLEXITY_FACTOR:{round(candidate_complexity, 2)}")
        
        return CognitiveLoad(
            level=level,
            value=round(load_value, 4),
            processing_demand=("semantic_evaluation", "conflict_resolution"),
            load_basis=tuple(context.context_ids) if context.context_ids else ("default",),
        ), tuple(traces)
    
    # =========================================================================
    # ENVIRONMENTAL LOAD ESTIMATION
    # =========================================================================
    
    def _estimate_environmental_load(self, context: ContextProjection, candidates: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[EnvironmentalLoad, Tuple[str, ...]]:
        """
        Estimate external complexity and event density.
        
        Args:
            context: Semantic context projection
            candidates: Normalized candidate states
            policy: Construction policy
            
        Returns:
            Tuple of (EnvironmentalLoad, traces)
        """
        # Calculate from context descriptors
        event_density = len(context.context_ids) * 2  # Rough estimate
        
        observation_diversity = len(set(
            cand.get("state_identity", "")[:10]
            for cand in candidates
        ))
        
        change_rate = min(1.0, len(candidates) / 10.0)
        
        traces = ["ENVIRONMENTAL_LOAD"]
        
        if event_density < 3 and observation_diversity < 5:
            level = "LOW"
        elif event_density < 6 and observation_diversity < 10:
            level = "MODERATE"
        elif event_density < 10 and observation_diversity < 20:
            level = "HIGH"
        else:
            level = "EXTREME"
        
        traces.append(f"ENVIRONMENT_LEVEL_{level}")
        traces.append(f"EVENT_DENSITY:{event_density}")
        
        return EnvironmentalLoad(
            level=level,
            event_density=event_density,
            observation_diversity=observation_diversity,
            change_rate=round(change_rate, 2),
            environmental_basis=tuple(context.context_ids) if context.context_ids else ("default",),
        ), tuple(traces)
    
    # =========================================================================
    # DENSITY ESTIMATION
    # =========================================================================
    
    def _estimate_novelty_density(self, candidates: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[NoveltyDensity, Tuple[str, ...]]:
        """
        Estimate concentration of novel information.
        
        Args:
            candidates: Normalized candidate states
            policy: Construction policy
            
        Returns:
            Tuple of (NoveltyDensity, traces)
        """
        if not candidates:
            return NoveltyDensity(level="NONE", value=0.0), ("NOVELTY_NONE",)
        
        # Count novel candidates based on assessment novelty level
        novel_candidates = [
            c.get("state_identity", "")
            for c in candidates
            if c.get("assessment", {}).get("novelty", {}).get("level", 0) > 2
        ]
        
        density_value = len(novel_candidates) / max(1, len(candidates))
        
        traces = ["NOVELTY_DENSITY"]
        
        if density_value == 0:
            level = "NONE"
        elif density_value < 0.2:
            level = "LOW"
        elif density_value < 0.4:
            level = "MODERATE"
        elif density_value < 0.7:
            level = "HIGH"
        else:
            level = "SATURATED"
        
        traces.append(f"NOVELTY_LEVEL_{level}")
        traces.append(f"NOVELTY_CANDIDATES:{len(novel_candidates)}")
        
        return NoveltyDensity(
            level=level,
            value=round(density_value, 4),
            novel_candidates=tuple(novel_candidates),
            novelty_basis=("assessment_novelty_detection",),
        ), tuple(traces)
    
    def _estimate_conflict_density(self, candidates: Tuple[dict, ...], competition: dict, policy: LandscapePolicy) -> Tuple[ConflictDensity, Tuple[str, ...]]:
        """
        Estimate concentration of unresolved conflicts.
        
        Args:
            candidates: Normalized candidate states
            competition: Competition result dictionary
            policy: Construction policy
            
        Returns:
            Tuple of (ConflictDensity, traces)
        """
        conflict_candidates = []
        
        # Check each candidate for conflict indicators
        for cand in candidates:
            if cand.get("assessment", {}).get("conflict", {}).get("level", 0) > 2:
                conflict_candidates.append(cand.get("state_identity", ""))
        
        density_value = len(conflict_candidates) / max(1, len(candidates))
        
        traces = ["CONFLICT_DENSITY"]
        
        if density_value < 0.1:
            level = "LOW"
        elif density_value < 0.3:
            level = "MODERATE"
        elif density_value < 0.6:
            level = "HIGH"
        else:
            level = "EXTREME"
        
        traces.append(f"CONFLICT_LEVEL_{level}")
        traces.append(f"CONFLICT_CANDIDATES:{len(conflict_candidates)}")
        
        return ConflictDensity(
            level=level,
            value=round(density_value, 4),
            conflict_count=len(conflict_candidates),
            unresolved_conflicts=tuple(conflict_candidates),
            conflict_types=("goal_conflict", "evidence_conflict") if conflict_candidates else (),
        ), tuple(traces)
    
    def _estimate_uncertainty_density(self, candidates: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[UncertaintyDensity, Tuple[str, ...]]:
        """
        Estimate global uncertainty level.
        
        Args:
            candidates: Normalized candidate states
            policy: Construction policy
            
        Returns:
            Tuple of (UncertaintyDensity, traces)
        """
        if not candidates:
            return UncertaintyDensity(level="LOW", value=0.1), ("UNCERTAINTY_LOW_DEFAULT",)
        
        # Count high-uncertainty candidates
        uncertain_candidates = [
            c.get("state_identity", "")
            for c in candidates
            if c.get("confidence", 1.0) < 0.5
        ]
        
        density_value = len(uncertain_candidates) / max(1, len(candidates))
        
        traces = ["UNCERTAINTY_DENSITY"]
        
        if density_value < 0.2:
            level = "LOW"
        elif density_value < 0.4:
            level = "MODERATE"
        elif density_value < 0.7:
            level = "HIGH"
        else:
            level = "EXTREME"
        
        traces.append(f"UNCERTAINTY_LEVEL_{level}")
        traces.append(f"UNCERTAIN_CANDIDATES:{len(uncertain_candidates)}")
        
        return UncertaintyDensity(
            level=level,
            value=round(density_value, 4),
            uncertain_candidates=tuple(uncertain_candidates),
            missing_information_count=len(uncertain_candidates) * 2,
        ), tuple(traces)
    
    def _estimate_urgency_density(self, candidates: Tuple[dict, ...], competition: dict, context: ContextProjection, policy: LandscapePolicy) -> Tuple[UrgencyDensity, Tuple[str, ...]]:
        """
        Estimate distribution of urgent Candidates.
        
        Args:
            candidates: Normalized candidate states
            competition: Competition result dictionary
            context: Semantic context projection
            policy: Construction policy
            
        Returns:
            Tuple of (UrgencyDensity, traces)
        """
        if not candidates:
            return UrgencyDensity(level="SPARSE", value=0.0), ("URGENCY_SPARSE_DEFAULT",)
        
        # Find urgent candidates
        urgent_candidates = [
            c.get("state_identity", "")
            for c in candidates
            if c.get("assessment", {}).get("urgency", {}).get("level", 0) > 3
        ]
        
        # Calculate distribution based on context gradients
        density_value = len(urgent_candidates) / max(1, len(candidates))
        
        traces = ["URGENCY_DENSITY"]
        
        if len(urgent_candidates) == 0:
            level = "SPARSE"
        elif len(urgent_candidates) <= 2:
            level = "LOCALIZED"
        elif density_value < 0.3:
            level = "DISTRIBUTED"
        elif density_value < 0.6:
            level = "WIDESPREAD"
        else:
            level = "CRITICAL"
        
        traces.append(f"URGENCY_LEVEL_{level}")
        traces.append(f"URGENT_CANDIDATES:{len(urgent_candidates)}")
        
        return UrgencyDensity(
            level=level,
            value=round(density_value, 4),
            urgent_candidates=tuple(urgent_candidates),
            urgency_basis=tuple(c.get("state_identity", "") for c in candidates[:3]),
        ), tuple(traces)
    
    # =========================================================================
    # HOTSPOT DETECTION
    # =========================================================================
    
    def _detect_hotspots(self, candidates: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[Tuple[SalienceHotspot, ...], Tuple[str, ...]]:
        """
        Detect concentrated regions of salience.
        
        Args:
            candidates: Normalized candidate states
            policy: Construction policy
            
        Returns:
            Tuple of (hotspots tuple, traces)
        """
        hotspots = []
        traces = ["HOTSPOT_DETECTION"]
        
        # Group candidates by high-activation regions
        high_activation_candidates = [
            c for c in candidates if c.get("normalized_level", 0) >= policy.hotspot_threshold
        ]
        
        if not high_activation_candidates:
            return tuple(hotspots), ("NO_HOTSPOTS",)
        
        traces.append(f"HIGH_ACTIVATION_CANDIDATES:{len(high_activation_candidates)}")
        
        # Detect hotspots by category
        categories_found = set()
        
        for cand in high_activation_candidates:
            assessment = cand.get("assessment", {})
            
            # Check each dimension for hotspot potential
            if assessment.get("urgency", {}).get("level", 0) > 3 and "URGENCY" not in categories_found:
                hotspots.append(SalienceHotspot(
                    hotspot_id=f"hotspot_urgency_{len(hotspots)}",
                    category="THREAT",  # Urgent often correlates with threat
                    strength=cand.get("normalized_level", 0),
                    extent=0.5,
                    candidate_ids=(cand.get("state_identity", ""),),
                    hotspot_basis=("high_urgency_detection",),
                ))
                categories_found.add("URGENCY")
            
            if assessment.get("novelty", {}).get("level", 0) > 2 and "NOVELTY" not in categories_found:
                hotspots.append(SalienceHotspot(
                    hotspot_id=f"hotspot_novelty_{len(hotspots)}",
                    category="NOVELTY",
                    strength=cand.get("normalized_level", 0),
                    extent=0.5,
                    candidate_ids=(cand.get("state_identity", ""),),
                    hotspot_basis=("high_novelty_detection",),
                ))
                categories_found.add("NOVELTY")
            
            if assessment.get("conflict", {}).get("level", 0) > 2 and "CONFLICT" not in categories_found:
                hotspots.append(SalienceHotspot(
                    hotspot_id=f"hotspot_conflict_{len(hotspots)}",
                    category="CONFLICT",
                    strength=cand.get("normalized_level", 0),
                    extent=0.5,
                    candidate_ids=(cand.get("state_identity", ""),),
                    hotspot_basis=("high_conflict_detection",),
                ))
                categories_found.add("CONFLICT")
        
        traces.append(f"HOTSPOTS_DETECTED:{len(hotspots)}")
        
        return tuple(hotspots), tuple(traces)
    
    # =========================================================================
    # CONTEXTUAL GRADIENT ESTIMATION
    # =========================================================================
    
    def _estimate_gradients(self, context: ContextProjection, candidates: Tuple[dict, ...], policy: LandscapePolicy) -> Tuple[Tuple[ContextualGradient, ...], Tuple[str, ...]]:
        """
        Estimate semantic gradients across contexts.
        
        Args:
            context: Semantic context projection
            candidates: Normalized candidate states
            policy: Construction policy
            
        Returns:
            Tuple of (gradients tuple, traces)
        """
        gradients = []
        traces = ["CONTEXTUAL_GRADIENTS"]
        
        # Create gradient for each active context
        for ctx_id in context.context_ids[:5]:  # Limit to top 5 contexts
            gradients.append(ContextualGradient(
                gradient_id=f"gradient_{ctx_id}",
                context_basis=(ctx_id,),
                direction=0.0,
                strength=0.5,
                active_candidates=tuple(c.get("state_identity", "") for c in candidates[:3]),
            ))
        
        traces.append(f"GRADIENTS_ESTIMATED:{len(gradients)}")
        
        return tuple(gradients), tuple(traces)
    
    # =========================================================================
    # COHERENCE ESTIMATION
    # =========================================================================
    
    def _estimate_coherence(self, candidates: Tuple[dict, ...], conflict_density: ConflictDensity, uncertainty_density: UncertaintyDensity, policy: LandscapePolicy) -> Tuple[SystemCoherence, Tuple[str, ...]]:
        """
        Estimate semantic coherence of the landscape.
        
        Args:
            candidates: Normalized candidate states
            conflict_density: Current conflict density estimate
            uncertainty_density: Current uncertainty density estimate
            policy: Construction policy
            
        Returns:
            Tuple of (SystemCoherence, traces)
        """
        if not candidates:
            return SystemCoherence(level="COHERENT", value=1.0), ("COHERENCE_COHERENT_DEFAULT",)
        
        # Calculate coherence from factors
        base_coherence = 1.0
        
        # Reduce for conflicts
        conflict_penalty = min(0.5, conflict_density.value * policy.coherence_conflict_weight)
        
        # Reduce for uncertainty
        uncertainty_penalty = min(0.3, uncertainty_density.value * policy.coherence_uncertainty_weight)
        
        coherence_value = base_coherence - conflict_penalty - uncertainty_penalty
        coherence_value = max(0.0, min(1.0, coherence_value))
        
        traces = ["COHERENCE_ESTIMATION"]
        
        if coherence_value > 0.8:
            level = "COHERENT"
        elif coherence_value > 0.6:
            level = "PARTIALLY_COHERENT"
        elif coherence_value > 0.4:
            level = "FRAGMENTED"
        else:
            level = "CONFLICTED"
        
        traces.append(f"COHERENCE_LEVEL_{level}")
        traces.append(f"FINAL_SCORE:{round(coherence_value, 2)}")
        
        return SystemCoherence(
            level=level,
            value=round(coherence_value, 4),
            consistency_score=coherence_value,
            conflict_score=conflict_density.value,
            coherence_basis=tuple(c.get("state_identity", "") for c in candidates[:5]),
        ), tuple(traces)
    
    # =========================================================================
    # READINESS ESTIMATION
    # =========================================================================
    
    def _estimate_readiness(self, activation: GlobalActivation, cognitive_load: CognitiveLoad, pressure: ResourcePressure, coherent_system: bool) -> Tuple[SystemReadiness, Tuple[str, ...]]:
        """
        Estimate readiness for downstream Attention processing.
        
        Args:
            activation: Current global activation estimate
            cognitive_load: Current cognitive load estimate
            pressure: Current resource pressure estimate
            coherent_system: Whether system is coherent
            
        Returns:
            Tuple of (SystemReadiness, traces)
        """
        # Calculate readiness score from factors
        base_readiness = 1.0
        
        # Reduce for extreme activation
        if activation.level == "EXTREME":
            base_readiness -= 0.4
        elif activation.level == "HIGH":
            base_readiness -= 0.2
        
        # Reduce for overload
        if cognitive_load.level == "OVERLOADED":
            base_readiness -= 0.5
        elif cognitive_load.level == "HIGH":
            base_readiness -= 0.3
        
        # Reduce for critical pressure
        if pressure.level == "CRITICAL":
            base_readiness -= 0.4
        elif pressure.level == "HIGH":
            base_readiness -= 0.2
        
        # Boost for coherence
        if coherent_system:
            base_readiness += 0.1
        
        readiness_value = max(0.0, min(1.0, base_readiness))
        
        traces = ["READINESS_ESTIMATION"]
        
        if readiness_value > 0.8:
            level = "READY"
        elif readiness_value > 0.6:
            level = "LIMITED"
        elif readiness_value > 0.4:
            level = "DEGRADED"
        else:
            level = "UNSTABLE"
        
        traces.append(f"READINESS_LEVEL_{level}")
        traces.append(f"FINAL_SCORE:{round(readiness_value, 2)}")
        
        return SystemReadiness(
            level=level,
            value=round(readiness_value, 4),
            capacity_available=readiness_value,
            readiness_basis=tuple([
                f"activation:{activation.level}",
                f"load:{cognitive_load.level}",
                f"pressure:{pressure.level}",
            ]),
        ), tuple(traces)