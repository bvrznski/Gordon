# Multi-Domain Reward Engine - Taxonomy System (Phase 4.10.5)
# =============================================================

"""
RewardTaxonomy and DomainClassificationRules for Phase 4.10.5.

This module defines the canonical reward taxonomy system that remains explicit,
extensible, and immutable. The taxonomy shall never depend on runtime implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Set, Optional

from .domain import DomainType


# =============================================================================
# REWARD TAXONOMY (TAXONOMY-LAW-001 to TAXONOMY-LAW-008)
# =============================================================================

@dataclass(frozen=True)
class RewardTaxonomy:
    """
    Canonical reward taxonomy system.
    
    TAXONOMY-LAW-001: Exactly one canonical Reward Taxonomy exists.
    TAXONOMY-LAW-002: Reward taxonomy remains explicit.
    TAXONOMY-LAW-003: Reward taxonomy remains extensible.
    TAXONOMY-LAW-004: Domain identifiers remain stable.
    TAXONOMY-LAW-005: Domain semantics remain explicit.
    TAXONOMY-LAW-006: Domain revisions preserve compatibility.
    TAXONOMY-LAW-007: Taxonomy evolution preserves provenance.
    TAXONOMY-LAW-008: Taxonomy shall never depend on runtime implementation.
    
    PROPERTIES:
        • domain_types: Set of all canonical domain types
        • parent_domains: Mapping of domains to their parent domains (for hierarchy)
        • child_domains: Mapping of domains to their child domains (for hierarchy)
    
    NOT RESPONSIBLE FOR:
        • Runtime classification decisions
        • State modification
        • Motivation generation
    """
    
    # Core domain types (TAXONOMY-LAW-002: explicit)
    core_domain_types: Tuple[DomainType, ...] = field(default_factory=lambda: tuple(DomainType))
    """All canonical domain types in the taxonomy."""
    
    # Domain hierarchy relationships (optional, for cross-level mapping)
    parent_domains: Dict[str, Optional[str]] = field(
        default_factory=lambda: {
            "intrinsic": None,
            "extrinsic": None,
            "social": None,
            "epistemic": None,
            "competence": None,
            "autonomy": None,
            "curiosity": None,
            "mission": None,
            "normative": None,
            "safety": None,
            "resource": None,
            "identity": None,
            "unknown": None,
        }
    )
    """Mapping of domain ID to parent domain ID (None for root)."""
    
    child_domains: Dict[str, Tuple[str, ...]] = field(
        default_factory=lambda: {
            "intrinsic": (),
            "extrinsic": (),
            "social": (),
            "epistemic": (),
            "competence": (),
            "autonomy": (),
            "curiosity": (),
            "mission": (),
            "normative": (),
            "safety": (),
            "resource": (),
            "identity": (),
            "unknown": (),
        }
    )
    """Mapping of domain ID to child domain IDs (empty for leaf nodes)."""
    
    # Domain aliases (for semantic flexibility)
    domain_aliases: Dict[str, str] = field(
        default_factory=lambda: {
            # Intrinsic aliases
            "intrinsic_reward": "intrinsic",
            "internal_coherence": "intrinsic",
            "mastery": "intrinsic",
            # Extrinsic aliases  
            "extrinsic_reward": "extrinsic",
            "task_completion": "extrinsic",
            "objective_achievement": "extrinsic",
            # Social aliases
            "social_reward": "social",
            "cooperation": "social",
            "trust": "social",
            "approval": "social",
            # Epistemic aliases
            "epistemic_reward": "epistemic",
            "knowledge_acquisition": "epistemic",
            "uncertainty_reduction": "epistemic",
            # Competence aliases
            "competence_reward": "competence",
            "skill_improvement": "competence",
            "execution_quality": "competence",
            # Autonomy aliases
            "autonomy_reward": "autonomy",
            "self_directed": "autonomy",
            "independent_problem_solving": "autonomy",
            # Curiosity aliases
            "curiosity_reward": "curiosity",
            "exploration": "curiosity",
            "novelty_search": "curiosity",
            # Mission aliases
            "mission_reward": "mission",
            "long_term_alignment": "mission",
            "architectural_integrity": "mission",
            # Normative aliases
            "normative_reward": "normative",
            "principle_consistency": "normative",
            "ethical_compliance": "normative",
        }
    )
    """Mapping of alias to canonical domain ID."""
    
    @property
    def all_domain_types(self) -> Tuple[DomainType, ...]:
        """Get all domain types including extended domains."""
        return self.core_domain_types
    
    @property
    def domain_count(self) -> int:
        """Get total count of domain types in taxonomy."""
        return len(self.core_domain_types)
    
    def get_domain_type_by_alias(self, alias: str) -> Optional[DomainType]:
        """
        Get domain type by its alias.
        
        Returns:
            DomainType if alias exists, None otherwise
        """
        canonical_id = self.domain_aliases.get(alias.lower().replace("-", "_"))
        if canonical_id is None:
            return None
        
        try:
            return DomainType(canonical_id)
        except ValueError:
            return None
    
    def get_parent_domain(self, domain_type: DomainType) -> Optional[DomainType]:
        """Get parent domain for a given domain type."""
        parent_id = self.parent_domains.get(domain_type.value)
        if parent_id is None:
            return None
        try:
            return DomainType(parent_id)
        except ValueError:
            return None
    
    def get_child_domains(self, domain_type: DomainType) -> Tuple[DomainType, ...]:
        """Get child domains for a given domain type."""
        child_ids = self.child_domains.get(domain_type.value, ())
        result = []
        for cid in child_ids:
            try:
                result.append(DomainType(cid))
            except ValueError:
                pass
        return tuple(result)
    
    def get_all_descendants(self, domain_type: DomainType) -> Set[DomainType]:
        """Get all descendant domains recursively."""
        descendants = set()
        
        def _collect_children(dt: DomainType):
            for child in self.get_child_domains(dt):
                if child not in descendants:
                    descendants.add(child)
                    _collect_children(child)
        
        _collect_children(domain_type)
        return descendants
    
    def is_ancestor_of(self, ancestor: DomainType, descendant: DomainType) -> bool:
        """Check if one domain is an ancestor of another."""
        return descendant in self.get_all_descendants(ancestor)
    
    def to_dict(self) -> dict:
        """Convert taxonomy to dictionary representation."""
        return {
            "taxonomy_id": "canonical_reward_taxonomy",
            "domain_count": self.domain_count,
            "domain_types": [dt.value for dt in self.core_domain_types],
            "parent_domains": self.parent_domains,
            "child_domains": self.child_domains,
            "alias_count": len(self.domain_aliases),
        }
    
    @classmethod
    def create_canonical(cls) -> RewardTaxonomy:
        """
        Create the canonical reward taxonomy.
        
        This is the single authoritative instance of the taxonomy system.
        """
        return cls()
    
    def validate_domain_type(self, domain_type: DomainType) -> bool:
        """Validate that a domain type exists in this taxonomy."""
        return domain_type in self.core_domain_types
    
    def get_canonical_domains(self) -> Tuple[str, ...]:
        """Get tuple of all canonical domain identifiers."""
        return tuple(dt.value for dt in self.core_domain_types)


@dataclass(frozen=True)
class DomainClassificationRules:
    """
    Classification rules that govern how rewards are assigned to domains.
    
    CLASSIFICATION-LAW-001: Each classifier owns exactly one semantic domain.
    CLASSIFICATION-LAW-002: Classification preserves Reward Estimates.
    CLASSIFICATION-LAW-003: Classification preserves provenance.
    CLASSIFICATION-LAW-004: Classification preserves confidence.
    CLASSIFICATION-LAW-005: Classification preserves uncertainty.
    CLASSIFICATION-LAW-006: Classification remains deterministic.
    CLASSIFICATION-LAW-007: Classification shall never infer motivation.
    CLASSIFICATION-LAW-008: Classification shall never infer executive priorities.
    
    PROPERTIES:
        • classification_thresholds: Minimum confidence values for domain assignment
        • classification_rules: Domain-specific classification rules
        • relationship_rules: Rules for domain relationships
    
    NOT RESPONSIBLE FOR:
        • Actual classification (handled by classifiers)
        • State modification
        • Motivation generation
    """
    
    # Classification thresholds (CLASSIFICATION-LAW-004, 005)
    classification_thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "intrinsic": 0.5,
            "extrinsic": 0.5,
            "social": 0.5,
            "epistemic": 0.5,
            "competence": 0.5,
            "autonomy": 0.5,
            "curiosity": 0.5,
            "mission": 0.5,
            "normative": 0.5,
            "safety": 0.6,
            "resource": 0.5,
            "identity": 0.5,
        }
    )
    """Minimum confidence thresholds for domain assignment."""
    
    # Domain-specific classification criteria (CLASSIFICATION-LAW-002, 003)
    classification_criteria: Dict[str, Tuple[str, ...]] = field(
        default_factory=lambda: {
            "intrinsic": (
                "problem_solving",
                "understanding",
                "mastery",
                "internal_coherence",
                "creative_generation",
            ),
            "extrinsic": (
                "task_completion",
                "resource_acquisition",
                "objective_achievement",
                "environmental_success",
                "external_evaluation",
            ),
            "social": (
                "cooperation",
                "trust",
                "communication",
                "approval",
                "shared_goals",
                "relationship_maintenance",
            ),
            "epistemic": (
                "knowledge_acquisition",
                "uncertainty_reduction",
                "model_improvement",
                "hypothesis_validation",
                "concept_formation",
            ),
            "competence": (
                "skill_improvement",
                "execution_quality",
                "efficiency",
                "robustness",
                "reliability",
            ),
            "autonomy": (
                "independent_problem_solving",
                "self_directed_behavior",
                "minimal_external_intervention",
                "adaptive_self_regulation",
            ),
            "curiosity": (
                "exploration",
                "novel_discovery",
                "interesting_observations",
                "knowledge_opportunities",
            ),
            "mission": (
                "long_term_objective_alignment",
                "architectural_integrity",
                "system_objectives",
                "persistent_commitments",
            ),
            "normative": (
                "principle_consistency",
                "constraint_adherence",
                "policy_compliance",
                "ethical_frameworks",
            ),
        }
    )
    """Domain-specific classification criteria."""
    
    # Domain relationship rules (RELATIONSHIP-LAW-001 to 008)
    relationship_rules: Dict[str, Tuple[str, ...]] = field(
        default_factory=lambda: {
            "supports": ("intrinsic", "epistemic", "competence"),
            "conflicts_with": (),  # No conflicts by default
            "reinforces": ("mission",),
            "compensates": (),
            "competes_with": (),
            "independent_of": (),
        }
    )
    """Rules for domain relationship classification."""
    
    @property
    def threshold_count(self) -> int:
        """Get count of configured thresholds."""
        return len(self.classification_thresholds)
    
    def get_threshold(self, domain_type: str) -> float:
        """Get classification threshold for a domain type."""
        return self.classification_thresholds.get(domain_type, 0.5)
    
    def get_criteria(self, domain_type: str) -> Tuple[str, ...]:
        """Get classification criteria for a domain type."""
        return self.classification_criteria.get(domain_type, ())
    
    def validate_classification_confidence(
        self,
        domain_type: DomainType,
        confidence: float,
    ) -> bool:
        """
        Validate that confidence meets threshold for a domain type.
        
        Returns:
            True if classification is valid, False otherwise
        """
        threshold = self.get_threshold(domain_type.value)
        return confidence >= threshold
    
    def to_dict(self) -> dict:
        """Convert rules to dictionary representation."""
        return {
            "rules_id": "domain_classification_rules",
            "threshold_count": self.threshold_count,
            "domains_with_criteria": len(self.classification_criteria),
        }
    
    @classmethod
    def create_canonical(cls) -> DomainClassificationRules:
        """
        Create the canonical classification rules.
        
        This is the single authoritative instance of the rules system.
        """
        return cls()


__all__ = [
    "RewardTaxonomy",
    "DomainClassificationRules",
]