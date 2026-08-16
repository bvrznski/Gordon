# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Constitutional Principles
===================================================================

Canonical immutable constitutional principle definitions.
All principles are deeply frozen to ensure deterministic behavior.

This module implements:

* ConstitutionalPrinciple - fundamental architectural constraints
* Principle inheritance and evaluation
* Deterministic principle processing

Following:
* PRINCIPLE-LAW-001 through PRINCIPLE-LAW-008
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


# =============================================================================
# PRINCIPLE ENFORCEMENT MODES
# =============================================================================

class PrincipleEnforcement(Enum):
    """
    Modes of constitutional principle enforcement.
    
    GOVERNANCE-PRINC-LAW-001: Principles shall define architectural constraints
    GOVERNANCE-PRINC-LAW-002: Principles shall remain implementation-independent
    
    CCG-PRINC-LAW-001: Enforcement modes are canonical and immutable
    """
    STRICT = "strict"
    """Principle must be fully satisfied."""
    
    MONITORING = "monitoring"
    """Principle violations are monitored but not blocked."""
    
    NOT_APPLICABLE = "not_applicable"
    """Principle does not apply in this context."""


# =============================================================================
# CONSTITUTIONAL PRINCIPLE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConstitutionalPrinciple:
    """
    Immutable constitutional principle.
    
    A constitutional principle defines an architectural constraint that must
    be preserved across all system evolution.
    
    PRINCIPLE-LAW-001: Every constitutional principle possesses one stable identity
    PRINCIPLE-LAW-002: Principles shall define architectural constraints
    PRINCIPLE-LAW-003: Principles shall remain implementation-independent
    PRINCIPLE-LAW-004: Principles shall preserve affected domains
    PRINCIPLE-LAW-005: Principles shall preserve provenance
    PRINCIPLE-LAW-006: Historical principles shall remain inspectable
    PRINCIPLE-LAW-007: Principle revisions shall preserve lineage
    PRINCIPLE-LAW-008: Principle evaluation shall remain deterministic
    
    CCG-PRINC-INV-001: Principles are immutable (deeply frozen)
    CCG-PRINC-INV-002: Principles have no runtime references
    """
    principle_identity: str
    """Unique stable identity for this principle."""
    
    principle_name: str
    """Human-readable name of the principle."""
    
    description: str
    """Description of what this principle enforces."""
    
    mandatory: bool = True
    """Whether violation constitutes a critical error."""
    
    affected_domains: tuple[str, ...] = field(default_factory=tuple)
    """Domains affected by this principle."""
    
    enforcement_mode: PrincipleEnforcement = PrincipleEnforcement.STRICT
    """How this principle is enforced."""
    
    revision: int = 1
    """Revision number of this principle."""
    
    provenance_ref: str | None = None
    """Reference to provenance record."""
    
    @classmethod
    def of(
        cls,
        name: str,
        description: str,
        mandatory: bool = True,
        domains: tuple[str, ...] | None = None,
        enforcement: PrincipleEnforcement = PrincipleEnforcement.STRICT,
    ) -> ConstitutionalPrinciple:
        """
        Create a constitutional principle with stable identity.
        
        Args:
            name: Principle name
            description: What this principle enforces
            mandatory: Whether violation is critical
            domains: Affected architectural domains
            enforcement: Enforcement mode
            
        Returns:
            A new ConstitutionalPrinciple instance
        """
        return cls(
            principle_identity=f"principle:{name}",
            principle_name=name,
            description=description,
            mandatory=mandatory,
            affected_domains=domains or (),
            enforcement_mode=enforcement,
            revision=1,
            provenance_ref=None,
        )


# =============================================================================
# CANONICAL CONSTITUTIONAL PRINCIPLES
# =============================================================================

class CanonicalPrinciples:
    """
    Canonical constitutional principles for Gordon.
    
    These are the fundamental architectural constraints that define
    what it means to be a Gordon architecture.
    """
    
    DETERMINISM = ConstitutionalPrinciple.of(
        name="determinism",
        description=(
            "The architecture must produce identical outputs for identical inputs "
            "across all executions."
        ),
        mandatory=True,
        domains=("orchestration", "coordination", "communication"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    IMMUTABILITY = ConstitutionalPrinciple.of(
        name="immutability",
        description=(
            "Once created, data structures and records shall not be modified. "
            "New versions create new identities."
        ),
        mandatory=True,
        domains=("memory", "history", "state"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    MODULARITY = ConstitutionalPrinciple.of(
        name="modularity",
        description=(
            "The architecture shall be composed of explicit, independently "
            "verifiable modules with well-defined boundaries."
        ),
        mandatory=True,
        domains=("architecture", "coordination"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    EXPLICIT_OWNERSHIP = ConstitutionalPrinciple.of(
        name="explicit_ownership",
        description=(
            "Every component and data structure shall have an explicitly "
            "defined owner with clear authority boundaries."
        ),
        mandatory=True,
        domains=("architecture", "authority"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    TRACEABILITY = ConstitutionalPrinciple.of(
        name="traceability",
        description=(
            "All architectural artifacts shall preserve complete provenance "
            "and be traceable to their origin."
        ),
        mandatory=True,
        domains=("history", "provenance", "audit"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    PROVENANCE = ConstitutionalPrinciple.of(
        name="provenance",
        description=(
            "Every piece of information shall carry its origin and derivation "
            "history as an inseparable part."
        ),
        mandatory=True,
        domains=("history", "evidence", "validation"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    SEMANTIC_CORRECTNESS = ConstitutionalPrinciple.of(
        name="semantic_correctness",
        description=(
            "All operations shall preserve the semantic meaning of data "
            "and maintain logical consistency."
        ),
        mandatory=True,
        domains=("communication", "coordination", "orchestration"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    SEPARATION_OF_CONCERNS = ConstitutionalPrinciple.of(
        name="separation_of_concerns",
        description=(
            "Architectural responsibilities shall be clearly separated into "
            "distinct, non-overlapping domains."
        ),
        mandatory=True,
        domains=("architecture", "coordination"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    REPLAYABILITY = ConstitutionalPrinciple.of(
        name="replayability",
        description=(
            "Architectural state transitions shall be reproducible from "
            "historical records."
        ),
        mandatory=True,
        domains=("history", "state", "coordination"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    EXPLAINABILITY = ConstitutionalPrinciple.of(
        name="explainability",
        description=(
            "Architectural decisions and behaviors shall be explainable through "
            "inspectable records and traceability."
        ),
        mandatory=True,
        domains=("coordination", "orchestration", "audit"),
        enforcement=PrincipleEnforcement.STRICT,
    )
    
    @classmethod
    def all_principles(cls) -> tuple[ConstitutionalPrinciple, ...]:
        """Return all canonical constitutional principles."""
        return (
            cls.DETERMINISM,
            cls.IMMUTABILITY,
            cls.MODULARITY,
            cls.EXPLICIT_OWNERSHIP,
            cls.TRACEABILITY,
            cls.PROVENANCE,
            cls.SEMANTIC_CORRECTNESS,
            cls.SEPARATION_OF_CONCERNS,
            cls.REPLAYABILITY,
            cls.EXPLAINABILITY,
        )
    
    @classmethod
    def all_names(cls) -> tuple[str, ...]:
        """Return names of all canonical principles."""
        return tuple(p.principle_name for p in cls.all_principles())
    
    @classmethod
    def get_by_name(cls, name: str) -> ConstitutionalPrinciple | None:
        """
        Get a principle by its name.
        
        Args:
            name: The principle name
            
        Returns:
            The principle or None if not found
        """
        for p in cls.all_principles():
            if p.principle_name == name:
                return p
        return None
    
    @classmethod
    def get_by_identity(cls, identity: str) -> ConstitutionalPrinciple | None:
        """
        Get a principle by its identity.
        
        Args:
            identity: The principle identity
            
        Returns:
            The principle or None if not found
        """
        for p in cls.all_principles():
            if p.principle_identity == identity:
                return p
        return None