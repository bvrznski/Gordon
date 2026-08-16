# Oriented Network Executive Integration Types
# ============================================

"""
Executive Integration Types for Phase 4.7.6.

OWNERSHIP (Executive Network):
    - executive control
    - arbitration
    - executive supervision
    - executive directives
    
ORIENTED NETWORK ROLE:
    - consumes executive guidance
    - never performs executive control
    - maintains semantic reference to executive state

SEMANTIC INTEGRATION LAWS (Phase 4.7.6):
    INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
    INTEGRATION-LAW-007: Integration never transfers ownership.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional


# =============================================================================
# EXECUTIVE REFERENCE - Semantic reference to executive state or directive
# =============================================================================

@dataclass(frozen=True)
class ExecutiveReference:
    """
    Reference to an executive state, directive, or control signal.
    
    ARCHITECTURAL PRINCIPLES:
        ER-INV-001: Reference is immutable and semantic only
        ER-INV-002: Reference never owns executive capability
        ER-INV-003: Reference points to externally owned executive state
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-013: Every reference shall be explicit.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this reference"""
    
    executive_state_id: Optional[str] = None
    """Reference to executive state (if any)"""
    
    directive_id: Optional[str] = None
    """Reference to executive directive (if any)"""
    
    priority_level: Optional[int] = None
    """Priority level of the referenced directive (1-10 scale, optional)"""
    
    authority_source: str = "executive"
    """Source of authority for this reference"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "executive_state_id": self.executive_state_id,
            "directive_id": self.directive_id,
            "priority_level": self.priority_level,
            "authority_source": self.authority_source,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveReference:
        return cls(
            identity=data.get("identity", "unnamed"),
            executive_state_id=data.get("executive_state_id"),
            directive_id=data.get("directive_id"),
            priority_level=data.get("priority_level"),
            authority_source=data.get("authority_source", "executive"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.priority_level is not None and (self.priority_level < 1 or self.priority_level > 10):
            errors.append("priority_level must be between 1 and 10")
        return (len(errors) == 0, tuple(errors))


# =============================================================================
# EXECUTIVE DIRECTIVE - Semantic representation of an executive directive
# =============================================================================

@dataclass(frozen=True)
class ExecutiveDirective:
    """
    Semantic representation of an executive directive or control signal.
    
    ARCHITECTURAL PRINCIPLES:
        ED-INV-001: Directive is immutable and semantic only
        ED-INV-002: Directive never implements executive control
        ED-INV-003: Directive expresses intent, not command
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-015: Integration shall never invoke subsystem algorithms.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this directive"""
    
    directive_type: str = "orientation"
    """Type of directive (e.g., 'orientation', 'priority_adjustment')"""
    
    target_subsystem: Optional[str] = None
    """Target subsystem for the directive"""
    
    intent: str = ""
    """Semantic intent expressed by the directive"""
    
    priority_level: int = 5
    """Priority level (1-10 scale)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "directive_type": self.directive_type,
            "target_subsystem": self.target_subsystem,
            "intent": self.intent,
            "priority_level": self.priority_level,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveDirective:
        return cls(
            identity=data.get("identity", "unnamed"),
            directive_type=data.get("directive_type", "orientation"),
            target_subsystem=data.get("target_subsystem"),
            intent=data.get("intent", ""),
            priority_level=data.get("priority_level", 5),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.priority_level < 1 or self.priority_level > 10:
            errors.append("priority_level must be between 1 and 10")
        return (len(errors) == 0, tuple(errors))


# =============================================================================
# EXECUTIVE CONTEXT - Executive context information for orientation
# =============================================================================

@dataclass(frozen=True)
class ExecutiveContext:
    """
    Executive context information consumed by the Oriented Network.
    
    ARCHITECTURAL PRINCIPLES:
        EC-INV-001: Context is immutable and semantic only
        EC-INV-002: Context never owns executive control
        EC-INV-003: Context provides orienting information
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-015: Integration shall never invoke subsystem algorithms.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this context"""
    
    active_goals: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active goals"""
    
    active_commitments: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of active commitments"""
    
    priority_ordering: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered list of priorities"""
    
    control_level: str = "normal"
    """Current control level (normal, elevated, critical)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "active_goals": self.active_goals,
            "active_commitments": self.active_commitments,
            "priority_ordering": self.priority_ordering,
            "control_level": self.control_level,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveContext:
        return cls(
            identity=data.get("identity", "unnamed"),
            active_goals=tuple(data.get("active_goals", [])),
            active_commitments=tuple(data.get("active_commitments", [])),
            priority_ordering=tuple(data.get("priority_ordering", [])),
            control_level=data.get("control_level", "normal"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


# =============================================================================
# EXECUTIVE INFLUENCE - Executive influence on orientation
# =============================================================================

@dataclass(frozen=True)
class ExecutiveInfluence:
    """
    Semantic representation of executive influence on orientation.
    
    ARCHITECTURAL PRINCIPLES:
        EI-INV-001: Influence is immutable and semantic only
        EI-INV-002: Influence never implements executive control
        EI-INV-003: Influence shapes, not commands, orientation
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-015: Integration shall never invoke subsystem algorithms.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this influence"""
    
    influence_type: str = "priority_adjustment"
    """Type of influence (e.g., 'priority_adjustment', 'goal_emphasis')"""
    
    affected_orientation_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of orientations influenced"""
    
    strength: float = 0.5
    """Influence strength (0.0 to 1.0)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "influence_type": self.influence_type,
            "affected_orientation_ids": self.affected_orientation_ids,
            "strength": self.strength,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveInfluence:
        return cls(
            identity=data.get("identity", "unnamed"),
            influence_type=data.get("influence_type", "priority_adjustment"),
            affected_orientation_ids=tuple(data.get("affected_orientation_ids", [])),
            strength=float(data.get("strength", 0.5)),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.strength < 0.0 or self.strength > 1.0:
            errors.append("strength must be between 0.0 and 1.0")
        return (len(errors) == 0, tuple(errors))


# =============================================================================
# EXECUTIVE RELATIONSHIP - Oriented-Executive relationship
# =============================================================================

@dataclass(frozen=True)
class ExecutiveRelationship:
    """
    Semantic relationship between Oriented Network and Executive Network.
    
    ARCHITECTURAL PRINCIPLES:
        ER-REL-INV-001: Relationship is immutable and semantic only
        ER-REL-INV-002: Orientation never owns executive control
        ER-REL-INV-003: Relationship expresses coordination, not integration
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-015: Integration shall never invoke subsystem algorithms.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this relationship"""
    
    orientation_id: str = ""
    """ID of oriented network instance"""
    
    executive_authority: str = "executive"
    """Authority source for executive control"""
    
    coordination_mode: str = "consume_directives"
    """How orientation consumes executive signals (consume_directives, observe_state)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "orientation_id": self.orientation_id,
            "executive_authority": self.executive_authority,
            "coordination_mode": self.coordination_mode,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveRelationship:
        return cls(
            identity=data.get("identity", "unnamed"),
            orientation_id=data.get("orientation_id", ""),
            executive_authority=data.get("executive_authority", "executive"),
            coordination_mode=data.get("coordination_mode", "consume_directives"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if not self.orientation_id:
            errors.append("orientation_id must be non-empty")
        return (len(errors) == 0, tuple(errors))


# =============================================================================
# EXECUTIVE AUTHORITY - Executive authority information
# =============================================================================

@dataclass(frozen=True)
class ExecutiveAuthority:
    """
    Authority information for executive network integration.
    
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-008: Every subsystem possesses exactly one architectural authority.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this authority"""
    
    source: str = "executive_network"
    """Source of executive authority"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scope of authority (e.g., 'control', 'arbitration', 'supervision')"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "source": self.source,
            "scope": self.scope,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExecutiveAuthority:
        return cls(
            identity=data.get("identity", "unnamed"),
            source=data.get("source", "executive_network"),
            scope=tuple(data.get("scope", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        return (len(errors) == 0, tuple(errors))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ExecutiveReference",
    "ExecutiveDirective",
    "ExecutiveContext",
    "ExecutiveInfluence",
    "ExecutiveRelationship",
    "ExecutiveAuthority",
]