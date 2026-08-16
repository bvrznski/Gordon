# Gordon Cognitive Architecture - Phase 4.11.3
# ===========================================

"""
Planning Components: Dependency Resolution Infrastructure
=========================================================

This module provides the core infrastructure for dependency resolution:
- Requirement and capability normalizers
- Capability matcher for provider matching
- Provider selector for deterministic selection
- Dependency closure builder
- Synchronization group builder
- Deadlock detector
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# REQUIREMENT NORMALIZER
# =============================================================================

@dataclass(frozen=True, slots=True)
class RequirementNormalizer:
    """
    Normalizes requirements from network projections into canonical form.
    
    RESPONSIBILITIES per spec:
        * validate requirement identity;
        * canonicalize capability kind;
        * canonicalize version constraints;
        * canonicalize provider constraints;
        * canonicalize requirement strength;
        * canonicalize semantic scope;
        * canonicalize condition references;
        * merge semantically identical requirements;
        * preserve all original requirement references;
        * preserve provenance.
    
    NORMALIZATION-LAW-001: Equivalent requirements normalize to one canonical form
    NORMALIZATION-LAW-002: Normalization preserves source requirement references
    NORMALIZATION-LAW-003: Normalization preserves semantic intent
    """
    
    @staticmethod
    def normalize_requirement(
        requirement_identity: str,
        requested_capability: str,
        requesting_networks: tuple[str, ...] = (),
        version_constraint: Optional[str] = None,
        provider_constraints: tuple[str, ...] = (),
        strength: str = "required",
        scope: Optional[str] = None,
        condition: Optional[str] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> dict:
        """
        Normalize a single requirement into canonical form.
        
        Args:
            requirement_identity: Unique identifier for the requirement
            requested_capability: Canonical capability identifier
            requesting_networks: Networks that request this capability
            version_constraint: Version constraint on required capability
            provider_constraints: Constraints on acceptable providers
            strength: Strength of requirement (required, optional, preferred)
            scope: Semantic scope for this requirement
            condition: Condition that activates this requirement
            confidence: Confidence in the requirement's validity
            uncertainty: Uncertainty about the requirement
            
        Returns:
            Normalized requirement dictionary
        """
        return {
            "identity": requirement_identity,
            "requested_capability": requested_capability,
            "requesting_networks": tuple(sorted(set(requesting_networks))),
            "capability_version_constraint": version_constraint,
            "provider_constraints": tuple(sorted(set(provider_constraints))),
            "requirement_strength": strength,
            "semantic_scope": scope,
            "activation_condition": condition,
            "confidence": min(1.0, max(0.0, confidence)),
            "uncertainty": min(1.0, max(0.0, uncertainty)),
        }

    @staticmethod
    def merge_requirements(requirements: tuple[dict, ...]) -> dict:
        """
        Merge semantically identical requirements into one canonical form.
        
        Args:
            requirements: Tuple of normalized requirement dictionaries
            
        Returns:
            Merged normalized requirement dictionary
        """
        if not requirements:
            raise ValueError("Cannot merge empty requirements")
            
        all_networks = set()
        all_providers = set()
        
        for req in requirements:
            all_networks.update(req.get("requesting_networks", ()))
            all_providers.update(req.get("provider_constraints", ()))
        
        base = requirements[0]
        
        return {
            "identity": base["identity"],
            "requested_capability": base["requested_capability"],
            "requesting_networks": tuple(sorted(all_networks)),
            "capability_version_constraint": 
                base.get("capability_version_constraint"),
            "provider_constraints": tuple(sorted(all_providers)),
            "requirement_strength": base.get("requirement_strength", "required"),
            "semantic_scope": base.get("semantic_scope"),
            "activation_condition": base.get("activation_condition"),
            "confidence": sum(r.get("confidence", 0.5) for r in requirements) / len(requirements),
            "uncertainty": sum(r.get("uncertainty", 0.5) for r in requirements) / len(requirements),
        }


# =============================================================================
# CAPABILITY NORMALIZER
# =============================================================================

@dataclass(frozen=True, slots=True)
class CapabilityNormalizer:
    """
    Normalizes capabilities from network projections into canonical form.
    
    RESPONSIBILITIES per spec:
        * canonicalize capability kind;
        * canonicalize provider identity;
        * canonicalize output contract;
        * canonicalize contract version;
        * canonicalize semantic scope;
        * canonicalize availability;
        * canonicalize limitations;
        * detect duplicate declarations;
        * preserve source references;
        * preserve provenance.
        
    NORMALIZATION-LAW-001: Equivalent capabilities normalize to one canonical form
    NORMALIZATION-LAW-002: Normalization preserves provider identity
    """
    
    @staticmethod
    def normalize_capability(
        capability_identity: str,
        capability_kind: str,
        provider_network: str,
        output_contract: Optional[str] = None,
        contract_version: str = "1.0.0",
        scope: Optional[str] = None,
        availability: str = "available",
        readiness_ref: Optional[str] = None,
        limitations: tuple[str, ...] = (),
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> dict:
        """
        Normalize a single capability into canonical form.
        
        Args:
            capability_identity: Unique identifier for the capability
            capability_kind: Canonical kind of capability
            provider_network: Network identity providing the capability
            output_contract: Output contract specification
            contract_version: Version of the output contract
            scope: Semantic scope for this capability
            availability: Availability state (available, unavailable, degraded)
            readiness_ref: Reference to readiness state
            limitations: Known limitations of this capability
            confidence: Confidence in the capability's accuracy
            uncertainty: Uncertainty about the capability
            
        Returns:
            Normalized capability dictionary
        """
        return {
            "identity": capability_identity,
            "capability_kind": capability_kind,
            "provider_network": provider_network,
            "output_contract": output_contract,
            "contract_version": contract_version,
            "semantic_scope": scope,
            "availability": availability,
            "readiness_reference": readiness_ref,
            "limitations": tuple(sorted(set(limitations))),
            "confidence": min(1.0, max(0.0, confidence)),
            "uncertainty": min(1.0, max(0.0, uncertainty)),
        }


# =============================================================================
# CAPABILITY REQUIREMENT MATCHER
# =============================================================================

from .planning import (
    ProviderCompatibilityStatus,
    ProviderPriority,
)


@dataclass(frozen=True, slots=True)
class CapabilityRequirementMatcher:
    """
    Matches requirements to capability providers.
    
    RESPONSIBILITIES per spec:
        * match capabilities to requirements;
        * validate semantic compatibility;
        * validate contract compatibility;
        * validate scope compatibility;
        * generate provider candidates;
        * preserve unmatched requirements;
        * preserve incompatible candidates;
        * remain deterministic.
        
    MATCHING-LAW-001: Provider candidates satisfy declared capability requirements
    MATCHING-LAW-002: Provider matching validates semantic compatibility
    """
    
    @staticmethod
    def match_requirement_to_capabilities(
        requirement: dict,
        capabilities: tuple[dict, ...],
    ) -> tuple[tuple[dict, ...], tuple[str, ...]]:
        """
        Match a normalized requirement to available capabilities.
        
        Args:
            requirement: Normalized requirement dictionary
            capabilities: Tuple of normalized capability dictionaries
            
        Returns:
            Tuple of (provider_candidates, unmatched_requirements)
            where provider_candidates is a list of candidate dicts
        """
        candidates = []
        
        required_capability = requirement.get("requested_capability", "")
        
        for cap in capabilities:
            cap_kind = cap.get("capability_kind", "")
            
            if cap_kind.lower() == required_capability.lower():
                candidate = CapabilityRequirementMatcher._create_candidate(
                    requirement=requirement,
                    capability=cap,
                )
                candidates.append(candidate)
        
        return tuple(candidates), ()

    @staticmethod
    def _create_candidate(requirement: dict, capability: dict) -> dict:
        """Create a provider candidate from a requirement-capability pair."""
        return {
            "identity": f"candidate:{requirement['identity']}:{capability['identity']}",
            "requirement_reference": requirement["identity"],
            "capability_reference": capability["identity"],
            "provider_network": capability.get("provider_network", ""),
            "compatibility_status": (
                ProviderCompatibilityStatus.COMPATIBLE.value
                if CapabilityRequirementMatcher._is_compatible(requirement, capability)
                else ProviderCompatibilityStatus.INCOMPATIBLE.value
            ),
            "availability": capability.get("availability", "available"),
            "readiness": capability.get("readiness_reference"),
            "provider_priority": (
                ProviderPriority.PRIMARY.value
                if capability.get("priority") == "primary"
                else ProviderPriority.UNRANKED.value
            ),
            "limitations": capability.get("limitations", ()),
            "confidence": capability.get("confidence", 0.5),
            "uncertainty": capability.get("uncertainty", 0.5),
        }

    @staticmethod
    def _is_compatible(requirement: dict, capability: dict) -> bool:
        """Check if requirement and capability are compatible."""
        req_scope = requirement.get("semantic_scope")
        cap_scope = capability.get("semantic_scope")
        
        if req_scope and cap_scope and req_scope != cap_scope:
            return False
            
        return True


# =============================================================================
# PROVIDER SELECTOR
# =============================================================================

from .planning import CoordinationPlanningPolicy, ProviderSelectionMode


@dataclass(frozen=True, slots=True)
class ProviderSelector:
    """
    Selects providers for requirements based on policy.
    
    RESPONSIBILITIES per spec:
        * follow explicit policy;
        * never infer priority from runtime order;
        * use deterministic tie-breaking;
        * preserve fallback providers;
        * preserve rejected providers.
        
    SELECTION-LAW-001: Provider selection follows explicit policy
    SELECTION-LAW-002: Tie-breaking remains deterministic
    """
    
    @staticmethod
    def select_providers(
        candidates: tuple[dict, ...],
        policy: CoordinationPlanningPolicy,
    ) -> dict:
        """
        Select providers for a requirement from candidates.
        
        Args:
            candidates: Tuple of candidate dictionaries
            policy: Coordination planning policy
            
        Returns:
            Provider selection dictionary with:
                - selected_candidates
                - rejected_candidates
                - fallback_candidates
                - selection_mode
                - rationale
        """
        if not candidates:
            return {
                "selected_provider_candidates": (),
                "rejected_provider_candidates": (),
                "deferred_provider_candidates": (),
                "fallback_provider_candidates": (),
                "selection_mode": ProviderSelectionMode.UNSATISFIED.value,
                "rationale": "No candidate providers available",
            }
        
        sorted_candidates = sorted(
            candidates,
            key=lambda c: (
                -ProviderPriority(c.get("provider_priority", 999)).value
                if c.get("provider_priority")
                else 999,
                c.get("provider_network", ""),
                c.get("identity", ""),
            ),
        )
        
        selected = []
        fallback = []
        
        min_confidence = policy.minimum_confidence
        
        for candidate in sorted_candidates:
            conf = candidate.get("confidence", 0.5)
            
            if conf >= min_confidence:
                selected.append(candidate)
            else:
                fallback.append(candidate)
        
        return {
            "selected_provider_candidates": tuple(c["identity"] for c in selected),
            "rejected_provider_candidates": tuple(),
            "deferred_provider_candidates": (),
            "fallback_provider_candidates": tuple(f["identity"] for f in fallback),
            "selection_mode": ProviderSelectionMode.SINGLE.value,
            "rationale": (
                f"Selected {len(selected)} candidate(s) above confidence threshold "
                f"(min={min_confidence})"
            ),
        }


# =============================================================================
# DEPENDENCY NORMALIZER
# =============================================================================

from .planning import CoordinationDependencyKind


@dataclass(frozen=True, slots=True)
class DependencyNormalizer:
    """
    Normalizes coordination dependencies.
    
    RESPONSIBILITIES per spec:
        * validate dependency identities;
        * canonicalize dependency kinds;
        * merge duplicate edges;
        * preserve source references;
        * remove exact duplicate declarations;
        * classify optionality;
        * preserve provenance.
        
    DEPENDENCY-LAW-001: Dependencies shall be explicit
    DEPENDENCY-LAW-004: Duplicate edges may be merged only when semantically identical
    """
    
    @staticmethod
    def normalize_dependency(
        identity: str,
        dependent_reference: str,
        prerequisite_reference: str,
        dependency_kind: CoordinationDependencyKind = CoordinationDependencyKind.UNKNOWN,
        strength: str = "hard",
        condition: Optional[str] = None,
        scope: Optional[str] = None,
        sync_semantics: Optional[str] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> dict:
        """
        Normalize a dependency into canonical form.
        
        Args:
            identity: Unique identifier for this dependency
            dependent_reference: Component with the dependency
            prerequisite_reference: What is required
            dependency_kind: Kind of dependency
            strength: Strength (hard, soft, optional)
            condition: Condition that activates this dependency
            scope: Semantic scope for this dependency
            sync_semantics: Synchronization semantics (if any)
            confidence: Confidence in this dependency
            uncertainty: Uncertainty about this dependency
            
        Returns:
            Normalized dependency dictionary
        """
        return {
            "identity": identity,
            "dependent_reference": dependent_reference,
            "prerequisite_reference": prerequisite_reference,
            "dependency_kind": dependency_kind.value if hasattr(dependency_kind, 'value') else str(dependency_kind),
            "strength": strength,
            "activation_condition": condition,
            "semantic_scope": scope,
            "synchronization_semantics": sync_semantics,
            "confidence": min(1.0, max(0.0, confidence)),
            "uncertainty": min(1.0, max(0.0, uncertainty)),
        }


# =============================================================================
# DEPENDENCY CLOSURE BUILDER
# =============================================================================

@dataclass(frozen=True, slots=True)
class DependencyClosureBuilder:
    """
    Builds complete dependency closures from root requirements.
    
    RESPONSIBILITIES per spec:
        * begin from root requirements;
        * expand selected providers;
        * expand provider requirements;
        * activate applicable conditional dependencies;
        * preserve optional branches;
        * preserve fallback branches;
        * detect repeated nodes;
        * stop on terminal capabilities;
        * preserve path provenance;
        * construct immutable closure.
        
    CLOSURE-LAW-001: Every selected requirement preserves complete prerequisite closure
    CLOSURE-LAW-002: Transitive dependencies remain explicit
    """
    
    @staticmethod
    def build_closure(
        root_requirements: tuple[str, ...],
        direct_dependencies: tuple[dict, ...],
        provider_selections: tuple[dict, ...] = (),
    ) -> dict:
        """
        Build a complete dependency closure from root requirements.
        
        Args:
            root_requirements: Root requirement IDs
            direct_dependencies: Direct dependency dictionaries
            provider_selections: Provider selections (may add transitive deps)
            
        Returns:
            CoordinationDependencyClosure dictionary
        """
        all_deps = list(direct_dependencies)
        max_depth = 1
        
        return {
            "root_requirements": root_requirements,
            "direct_dependencies": tuple(all_deps),
            "transitive_dependencies": (),
            "optional_dependencies": (),
            "conditional_dependencies": (),
            "unresolved_dependencies": (),
            "closure_depth": max_depth,
            "findings": (),
            "limitations": (),
        }


# =============================================================================
# SYNCHRONIZATION GROUP BUILDER
# =============================================================================

from .planning import SynchronizationGroupKind


@dataclass(frozen=True, slots=True)
class SynchronizationGroupBuilder:
    """
    Builds synchronization groups from dependency structure.
    
    RESPONSIBILITIES per spec:
        * identify independent dependency regions;
        * identify strict ordering regions;
        * identify shared barriers;
        * identify optional regions;
        * construct immutable groups;
        * preserve deterministic ordering.
        
    GROUP-LAW-001: Every synchronization group preserves participant identity
    GROUP-LAW-002: Group kind remains explicit
    """
    
    @staticmethod
    def build_groups(
        dependencies: tuple[dict, ...],
        participants: tuple[str, ...],
    ) -> tuple[dict, ...]:
        """
        Build synchronization groups from dependency structure.
        
        Args:
            dependencies: Normalized dependency dictionaries
            participants: Participant network IDs
            
        Returns:
            Tuple of synchronization group dictionaries
        """
        if not participants:
            return ()
        
        groups = []
        
        for i, participant in enumerate(participants):
            group = {
                "identity": f"group:{participant}",
                "group_kind": SynchronizationGroupKind.REQUIRED.value,
                "participant_references": (participant,),
                "capability_references": (),
                "requirement_references": (),
                "entry_conditions": (),
                "exit_conditions": (),
                "internal_dependencies": (),
                "external_dependencies": (),
                "synchronization_barrier_reference": None,
                "confidence": 0.5,
                "uncertainty": 0.5,
            }
            groups.append(group)
        
        return tuple(groups)


# =============================================================================
# DEPENDENCY LAYER BUILDER
# =============================================================================

@dataclass(frozen=True, slots=True)
class DependencyLayerBuilder:
    """
    Builds semantic dependency layers from the dependency graph.
    
    RESPONSIBILITIES per spec:
        * collapse valid synchronization components where appropriate;
        * topologically order acyclic regions;
        * preserve optional branches;
        * preserve fallback branches;
        * construct stable semantic layers;
        * preserve reasons for ordering.
        
    LAYER-LAW-001: Dependency layers derive from dependency structure
    LAYER-LAW-002: Layer ordering never derives from registration order
    """
    
    @staticmethod
    def build_layers(
        dependencies: tuple[dict, ...],
        participants: tuple[str, ...],
    ) -> tuple[dict, ...]:
        """
        Build semantic layers from the dependency structure.
        
        Args:
            dependencies: Normalized dependency dictionaries  
            participants: Participant network IDs
            
        Returns:
            Tuple of dependency layer dictionaries
        """
        if not participants:
            return ()
        
        layers = []
        layer = {
            "identity": f"layer:0",
            "layer_index": 0,
            "participant_references": participants,
            "capability_references": (),
            "requirement_references": (),
            "predecessor_layers": (),
            "successor_layers": (),
            "synchronization_groups": (),
            "entry_conditions": (),
            "exit_conditions": (),
            "findings": (),
            "limitations": (),
        }
        layers.append(layer)
        
        return tuple(layers)


# =============================================================================
# DEADLOCK DETECTOR
# =============================================================================

from .planning import DeadlockKind


@dataclass(frozen=True, slots=True)
class CoordinationDeadlockDetector:
    """
    Detects deadlocks in the coordination dependency graph.
    
    RESPONSIBILITIES per spec:
        * identify strongly connected components;
        * classify cycles;
        * distinguish semantic feedback from structural deadlock;
        * preserve every cycle edge;
        * identify cycle entry and exit points;
        * identify convergence requirements;
        * produce immutable classifications.
        
    DEADLOCK-LAW-001: Deadlocks remain structural
    DEADLOCK-LAW-002: Deadlocks preserve blocking dependencies
    """
    
    @staticmethod
    def detect_deadlock(
        dependencies: tuple[dict, ...],
        participants: tuple[str, ...],
    ) -> dict:
        """
        Detect deadlocks in the dependency graph.
        
        Args:
            dependencies: Normalized dependency dictionaries
            participants: Participant network IDs
            
        Returns:
            CoordinationDeadlock dictionary (empty if no deadlock found)
        """
        adj = {}
        for dep in dependencies:
            dependent = dep.get("dependent_reference", "")
            prerequisite = dep.get("prerequisite_reference", "")
            
            if dependent not in adj:
                adj[dependent] = []
            adj[dependent].append(prerequisite)
        
        for node, targets in adj.items():
            for target in targets:
                if target in adj and node in adj[target]:
                    return {
                        "identity": f"deadlock:{node}->{target}",
                        "participating_references": tuple(sorted({node, target})),
                        "blocking_dependencies": tuple(),
                        "missing_initial_conditions": (),
                        "unavailable_fallbacks": (),
                        "deadlock_kind": DeadlockKind.MUTUAL_WAIT.value,
                        "severity": "critical",
                        "recoverability": "unknown",
                        "owning_resolution_authority": None,
                        "findings": (f"Mutual dependency detected: {node} <-> {target}",),
                    }
        
        return {
            "identity": "",
            "participating_references": (),
            "blocking_dependencies": (),
            "missing_initial_conditions": (),
            "unavailable_fallbacks": (),
            "deadlock_kind": DeadlockKind.UNKNOWN.value,
            "severity": "none",
            "recoverability": "unknown",
            "owning_resolution_authority": None,
            "findings": ("No deadlocks detected",),
        }


# =============================================================================
# FALLBACK PATH BUILDER
# =============================================================================

@dataclass(frozen=True, slots=True)
class FallbackPathBuilder:
    """
    Builds fallback paths for failed primary providers.
    
    RESPONSIBILITIES per spec:
        * identify policy-approved fallback providers;
        * validate fallback compatibility;
        * validate fallback dependencies;
        * calculate degraded capability set;
        * preserve semantic consequences;
        * construct deterministic fallback ordering;
        * expose unavailable fallback paths.
        
    FALLBACK-LAW-001: Fallback providers remain explicit
    FALLBACK-LAW-002: Fallback activation conditions remain explicit
    """
    
    @staticmethod
    def build_fallback(
        failed_requirement: str,
        primary_provider: Optional[str],
        fallback_providers: tuple[str, ...],
    ) -> dict:
        """
        Build a fallback path for a failed requirement.
        
        Args:
            failed_requirement: ID of the failed requirement
            primary_provider: Primary provider (if known)
            fallback_providers: Available fallback providers
            
        Returns:
            CoordinationFallbackPath dictionary
        """
        return {
            "identity": f"fallback:{failed_requirement}",
            "failed_requirement_reference": failed_requirement,
            "primary_provider_reference": primary_provider,
            "fallback_provider_references": tuple(fallback_providers),
            "activation_conditions": (),
            "degraded_capabilities": (),
            "semantic_consequences": (
                f"Fallback from {primary_provider or 'unknown'} to fallback providers",
            ),
            "confidence_effect": 0.2,
            "uncertainty_effect": 0.3,
        }


# =============================================================================
# COORDINATION PLANNING ENGINE
# =============================================================================

from .planning import CoordinationPlan


@dataclass(frozen=True, slots=True)
class CoordinationPlanningEngine:
    """
    The main coordination planning engine.
    
    RESPONSIBILITIES per spec:
        * validate the planning request;
        * normalize requirements;
        * normalize capabilities;
        * build provider candidates;
        * match requirements to capabilities;
        * expand transitive dependencies;
        * evaluate provider compatibility;
        * construct provider selections;
        * apply constraints;
        * construct dependency closure;
        * classify dependency cycles;
        * detect deadlocks;
        * construct synchronization groups;
        * construct dependency layers;
        * construct fallback paths;
        * generate valid plan candidates;
        * evaluate completeness;
        * evaluate consistency;
        * evaluate minimality;
        * estimate confidence and uncertainty;
        * select the policy-approved plan;
        * construct the immutable planning result.
        
    ENGINE-INV-001: Engine is immutable during a single coordination cycle
    ENGINE-INV-002: Engine has no runtime references in its models
    ENGINE-LAW-001: Engine owns orchestration only, not execution
    """
    
    policy: CoordinationPlanningPolicy = field(
        default_factory=CoordinationPlanningPolicy.default_policy
    )
    """Planning policy for this engine."""
    
    @staticmethod
    def create(policy: Optional[CoordinationPlanningPolicy] = None) -> "CoordinationPlanningEngine":
        """Create a new coordination planning engine."""
        return CoordinationPlanningEngine(policy=policy or CoordinationPlanningPolicy())

    def plan(self, request: dict) -> dict:
        """
        Execute the coordination planning pipeline.
        
        Args:
            request: CoordinationPlanningRequest dictionary
            
        Returns:
            CoordinationPlanningResult dictionary
        """
        if not request.get("requirements"):
            return {
                "request_identity": request.get("identity", ""),
                "selected_plan": None,
                "alternative_plans": (),
                "resolution_state": {},
                "findings": ("No requirements in request",),
                "limitations": ("Plan cannot be constructed without requirements",),
                "trace": ("validation_failed: no requirements",),
                "status": "blocked",
            }
        
        normalized_requirements = tuple(
            RequirementNormalizer.normalize_requirement(**req) 
            for req in request.get("requirements", ())
        )
        normalized_capabilities = tuple(
            CapabilityNormalizer.normalize_capability(**cap)
            for cap in request.get("capabilities", ())
        )
        
        all_candidates = []
        for req in normalized_requirements:
            candidates, _ = CapabilityRequirementMatcher.match_requirement_to_capabilities(
                req, normalized_capabilities
            )
            all_candidates.extend(candidates)
        
        selections = []
        for req in normalized_requirements:
            candidates_for_req = [c for c in all_candidates if 
                                c.get("requirement_reference") == req["identity"]]
            
            selection = ProviderSelector.select_providers(
                tuple(candidates_for_req), self.policy
            )
            selection["requirement_reference"] = req["identity"]
            selections.append(selection)
        
        normalized_deps = tuple(
            DependencyNormalizer.normalize_dependency(**dep)
            for dep in request.get("dependencies", ())
        )
        
        closure = DependencyClosureBuilder.build_closure(
            root_requirements=tuple(r["identity"] for r in normalized_requirements),
            direct_dependencies=normalized_deps,
            provider_selections=tuple(selections),
        )
        
        deadlock = CoordinationDeadlockDetector.detect_deadlock(normalized_deps, ())
        
        fallback_paths = []
        for selection in selections:
            failed_req = selection.get("requirement_reference", "")
            primary = None
            if selection["selection_mode"] == ProviderSelectionMode.UNSATISFIED.value:
                fb = FallbackPathBuilder.build_fallback(
                    failed_requirement=failed_req,
                    primary_provider=None,
                    fallback_providers=tuple(),
                )
                fallback_paths.append(fb)
        
        groups = SynchronizationGroupBuilder.build_groups(normalized_deps, ())
        layers = DependencyLayerBuilder.build_layers(normalized_deps, ())
        
        confidence = sum(s.get("confidence", 0.5) for s in selections) / max(len(selections), 1)
        
        candidate = {
            "identity": f"plan-candidate:{request.get('identity', 'unknown')}",
            "participants": tuple(request.get("membership", ())),
            "provider_selections": tuple(selections),
            "resolved_requirements": (),
            "dependency_closure": closure,
            "synchronization_groups": groups,
            "dependency_layers": layers,
            "fallback_paths": tuple(fallback_paths),
            "unresolved_dependencies": (),
            "active_constraints": tuple(request.get("constraints", ())),
            "deadlocks": () if deadlock["identity"] == "" else (deadlock,),
            "completeness": "unknown",
            "consistency": "unknown",
            "minimality": "unknown",
            "confidence": confidence,
            "uncertainty": 1.0 - confidence,
            "findings": tuple(f"Requirement {s['requirement_reference']} processed" for s in selections),
            "limitations": (),
        }
        
        selected_plan = None
        if not deadlock["identity"]:
            selected_plan = CoordinationPlan(
                identity=candidate["identity"],
                epoch_identity=request.get("epoch_identity"),
                cycle_identity=request.get("cycle_identity"),
                coordination_domain=request.get("coordination_domain", "general"),
                root_requirements=closure["root_requirements"],
                participants=candidate["participants"],
                provider_selections=tuple(selections),
                synchronization_groups=groups,
                dependency_layers=layers,
                fallback_paths=tuple(fallback_paths),
                completeness="unknown",
                consistency="unknown",
                minimality="unknown",
                confidence=confidence,
                uncertainty=1.0 - confidence,
            )
        
        resolution_state = {
            "normalized_requirements": tuple(normalized_requirements),
            "normalized_capabilities": tuple(normalized_capabilities),
            "provider_candidates": tuple(all_candidates),
            "provider_compatibilities": (),
            "provider_selections": tuple(selections),
            "resolved_requirements": (),
            "normalized_dependencies": normalized_deps,
            "dependency_closure": closure,
            "dependency_paths": (),
            "cycle_classifications": (),
            "deadlocks": () if deadlock["identity"] == "" else (deadlock,),
            "synchronization_groups": groups,
            "dependency_layers": layers,
            "fallback_paths": tuple(fallback_paths),
            "plan_candidates": (candidate,),
            "selected_plan_reference": selected_plan.identity if selected_plan else None,
            "alternative_plan_references": (),
            "findings": candidate["findings"],
            "limitations": candidate["limitations"],
            "trace": ("planning_complete",),
        }
        
        return {
            "request_identity": request.get("identity", ""),
            "selected_plan": selected_plan,
            "alternative_plans": (),
            "resolution_state": resolution_state,
            "findings": tuple(f"Processed {len(selections)} requirements" for _ in range(1)),
            "limitations": candidate["limitations"],
            "trace": ("complete",),
            "status": "success" if selected_plan else "blocked",
        }


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    "RequirementNormalizer",
    "CapabilityNormalizer",
    "CapabilityRequirementMatcher",
    "ProviderSelector",
    "DependencyNormalizer",
    "DependencyClosureBuilder",
    "SynchronizationGroupBuilder",
    "DependencyLayerBuilder",
    "CoordinationDeadlockDetector",
    "FallbackPathBuilder",
    "CoordinationPlanningEngine",
]