# Governance Foundations: Philosophy, Architecture & Invariants
# =============================================================

"""
Governance Foundations - The philosophical and architectural bedrock of Runtime Governance.

This module defines:
- Governance philosophy: Core principles guiding governance design
- Operational philosophy: How operations should be governed
- Supervision philosophy: Continuous runtime supervision principles
- Terminology: Canonical governance vocabulary
- Architectural boundaries: What governance does and does not do
- Ownership model: Who owns governance artifacts
- Invariants: Unchanging truths of the governance system
- Lifecycle: Governance decision lifecycle

Governance is NOT cognition, planning, or reasoning.
Governance IS continuous supervision, constraint enforcement, and control authority.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum, auto
import uuid
import time


# =============================================================================
# GOVERNANCE PHILOSOPHY
# =============================================================================

class GovernancePhilosophy:
    """
    Core governance philosophy for the Gordon Runtime.
    
    Governance is the architectural layer responsible for ensuring that every 
    subsystem operates according to architectural principles, runtime policies,
    operational constraints, safety guarantees, resource budgets, and 
    organizational objectives.
    
    Key Principles:
    1. One canonical governance architecture throughout the repository
    2. Governance supervises but never replaces subsystem implementations
    3. Every decision is governed, constrained, observable, auditable, explainable
    4. Runtime continuously determines: what, why, should, compliance, intervention needs
    5. Governance exists above execution but below cognition/planning
    """
    
    @staticmethod
    def get_core_principles() -> List[str]:
        """Return the core governance principles."""
        return [
            "One canonical governance architecture throughout the repository",
            "Governance supervises but never replaces subsystem implementations",
            "Every runtime decision is governed, constrained, observable, auditable, explainable",
            "Runtime continuously determines: what, why, should, compliance, intervention needs",
            "Governance exists above execution but below cognition/planning",
        ]
    
    @staticmethod
    def get_separation_of_concerns() -> Dict[str, List[str]]:
        """
        Define clear separation between governance and other concerns.
        
        Returns:
            Dictionary mapping each concern to its responsibilities
        """
        return {
            "Governance": [
                "Supervision of subsystem behavior",
                "Policy evaluation and enforcement",
                "Constraint validation",
                "Authority management",
                "Decision making with evidence",
                "Arbitration of conflicts",
                "Intervention when needed",
                "Adaptation based on policies",
            ],
            "Execution": ["Performing operations", "Running tasks", "Executing code"],
            "Planning": ["Making decisions", "Reasoning about goals", "Creating plans"],
            "Cognition": ["Thinking", "Learning", "Understanding"],
            "Policy": ["Defining rules declaratively", "Setting constraints"],
        }
    
    @staticmethod
    def get_runtime_questions() -> List[str]:
        """
        Questions the runtime must continuously answer.
        
        Returns:
            List of governance questions the runtime answers
        """
        return [
            "What is currently executing?",
            "Why is it executing?",
            "Should it continue executing?",
            "Does it still satisfy operational objectives?",
            "Does it violate architectural policies?",
            "Does it violate resource budgets?",
            "Should intervention occur?",
            "Should execution be suspended?",
            "Should priorities change?",
            "Should recovery begin?",
            "Should degradation occur?",
            "Should operators be notified?",
        ]


# =============================================================================
# OPERATIONAL PHILOSOPHY
# =============================================================================

class OperationalPhilosophy:
    """
    Philosophy of operational control in the Gordon Runtime.
    
    Operations exist to serve objectives. Governance ensures operations
    remain aligned with objectives while respecting constraints and policies.
    """
    
    @staticmethod
    def get_operational_principles() -> List[str]:
        """Return operational principles."""
        return [
            "Operations must serve declared objectives",
            "Governance continuously evaluates objective alignment",
            "Constraint violations trigger intervention",
            "Policies provide declarative boundaries",
            "Adaptation is policy-driven, not ad-hoc",
        ]
    
    @staticmethod
    def get_operational_states() -> List[str]:
        """Return operational state categories."""
        return [
            "Normal",      # All objectives met, no violations
            "Warning",      # Some objective degradation detected
            "Degraded",    # Objectives not fully met, requires attention
            "Critical",     # Violation occurred, intervention needed
            "Emergency",   # Immediate action required
        ]


# =============================================================================
# SUPERVISION PHILOSOPHY
# =============================================================================

class SupervisionPhilosophy:
    """
    Philosophy of continuous runtime supervision.
    
    Supervision is continuous, not periodic. The runtime must always know:
    - What's happening now
    - Why it's happening
    - Whether it should continue
    """
    
    @staticmethod
    def get_supervision_principles() -> List[str]:
        """Return supervision principles."""
        return [
            "Supervision is continuous, not periodic",
            "Every subsystem is supervised according to its domain",
            "Supervision produces evidence for decisions",
            "Supervision is policy-driven and objective-aligned",
            "Supervision enables deterministic intervention",
        ]
    
    @staticmethod
    def get_supervised_subsystems() -> List[str]:
        """Return list of subsystems under continuous supervision."""
        return [
            "Runtime state",
            "Services",
            "Capabilities",
            "Schedulers",
            "Execution units",
            "Resources (CPU, memory, I/O)",
            "Communication channels",
            "Persistence operations",
            "Recovery processes",
            "Lifecycle transitions",
        ]


# =============================================================================
# TERMINOLOGY
# =============================================================================

class GovernanceTerminology:
    """
    Canonical governance terminology for the Gordon Runtime.
    
    Each term has a precise meaning to ensure unambiguous communication
    and implementation across the system.
    """
    
    @staticmethod
    def get_core_terms() -> Dict[str, str]:
        """Return core governance terms with definitions."""
        return {
            "Governance": (
                "The architectural layer responsible for ensuring that every "
                "subsystem operates according to architectural principles, runtime "
                "policies, operational constraints, safety guarantees, resource "
                "budgets, and organizational objectives."
            ),
            "Supervision": (
                "Continuous observation and evaluation of subsystem behavior against "
                "policy, objective, and constraint specifications."
            ),
            "Intervention": (
                "Runtime action taken when policy violations, objective failures, or "
                "constraint breaches are detected to restore合规 (compliance)."
            ),
            "Arbitration": (
                "Deterministic resolution of conflicts between subsystems, resources, "
                "or operational demands using established policies and rules."
            ),
            "Adaptation": (
                "Policy-driven adjustment of runtime behavior in response to changing "
                "conditions while maintaining objective alignment."
            ),
            "Constraint": (
                "Declarative specification of what must NOT happen during runtime. "
                "Violations trigger governance actions."
            ),
            "Objective": (
                "Declarative specification of what MUST be achieved. Governance "
                "evaluates compliance with objectives continuously."
            ),
            "Policy": (
                "Declarative rules that define acceptable behavior patterns, constraints, "
                "and operational boundaries."
            ),
            "Authority": (
                "Explicit authorization to make governance decisions and perform "
                "interventions within defined scope."
            ),
            "Decision": (
                "Governance conclusion with evidence trail: observation -> evaluation "
                "-> risk assessment -> decision -> execution -> verification."
            ),
        }
    
    @staticmethod
    def get_distinctions() -> Dict[str, List[Tuple[str, str]]]:
        """
        Return architectural distinctions to prevent semantic confusion.
        
        Returns:
            Dictionary mapping primary concepts to pairs of (what_it_is, what_it_is_not)
        """
        return {
            "Governance": (
                ("Supervision and control of runtime behavior",),
                ("Cognition", "Planning", "Reasoning", "Execution")
            ),
            "Policy": (
                ("Declarative rules defining constraints and acceptable behavior",),
                ("Implementation logic", "Procedural code", "Executable instructions")
            ),
            "Authority": (
                ("Explicit authorization to make governance decisions",),
                ("Cognitive ability", "Planning capability", "Execution power")
            ),
            "Intervention": (
                ("Runtime action taken when compliance is violated",),
                ("Cognitive decision", "Planning process", "Normal execution")
            ),
        }


# =============================================================================
# ARCHITECTURAL BOUNDARIES
# =============================================================================

class GovernanceArchitectureBoundaries:
    """
    Define architectural boundaries: what governance does and does not do.
    
    Clear boundaries prevent semantic overlap and ensure each component
    has exactly one responsibility.
    """
    
    @staticmethod
    def get_governance_responsibilities() -> List[str]:
        """Return responsibilities that ARE governance's job."""
        return [
            "Supervising subsystem behavior",
            "Evaluating policies against runtime state",
            "Validating constraints and detecting violations",
            "Making governance decisions with evidence",
            "Authorizing interventions when needed",
            "Arbitrating conflicts between subsystems",
            "Adapting runtime behavior based on policy",
            "Coordinating cross-cutting concerns",
            "Producing audit trails and evidence",
        ]
    
    @staticmethod
    def get_governance_prohibitions() -> List[str]:
        """Return responsibilities that governance MUST NOT do."""
        return [
            "Implementing business logic",
            "Performing execution (running code)",
            "Making cognitive decisions (reasoning, planning)",
            "Replacing subsystem implementations",
            "Bypassing validation",
            "Bypassing security mechanisms",
            "Directly modifying implementation code at runtime",
        ]
    
    @staticmethod
    def get_boundary_matrix() -> Dict[str, List[str]]:
        """
        Return boundary matrix for governance vs other components.
        
        Returns:
            Matrix showing what each component does and doesn't do
        """
        return {
            "Governance": GovernanceArchitectureBoundaries.get_governance_responsibilities(),
            "NOT Governance (Governance must NOT)": GovernanceArchitectureBoundaries.get_governance_prohibitions(),
            "Execution": ["Performing operations", "Running code", "Executing tasks"],
            "Planning": ["Making decisions", "Creating plans", "Reasoning about goals"],
            "Policy": ["Defining rules declaratively", "Setting constraints", "Specifying objectives"],
        }


# =============================================================================
# OWNERSHIP
# =============================================================================

@dataclass(frozen=True)
class GovernanceOwnership:
    """
    Ownership model for governance artifacts.
    
    Every governance artifact must have explicit ownership for:
    - Accountability
    - Auditability
    - Traceability
    - Revocability
    """
    
    artifact_id: str
    owner_id: str
    scope: str  # Runtime, service, component, etc.
    created_at: float = field(default_factory=time.time)
    policy_references: List[str] = field(default_factory=list)
    objective_references: List[str] = field(default_factory=list)
    
    @property
    def artifact_type(self) -> str:
        """Return the type of governance artifact."""
        return self.__class__.__name__
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique identifier for an artifact."""
        return f"governance_artifact_{uuid.uuid4().hex[:12]}"


# =============================================================================
# GOVERNANCE INVARIANTS
# =============================================================================

class GovernanceInvariants:
    """
    Invariant properties that must always hold in the governance system.
    
    These are unchanging truths about the governance architecture that
    all implementations must satisfy.
    """
    
    @staticmethod
    def get_structural_invariants() -> List[str]:
        """Return structural invariants (system must always be true)."""
        return [
            "One canonical governance architecture exists throughout repository",
            "Governance is separate from execution, planning, cognition",
            "All subsystems use the same governance framework",
            "No independent governance implementations exist",
        ]
    
    @staticmethod
    def get_behavioral_invariants() -> List[str]:
        """Return behavioral invariants (runtime behavior must satisfy)."""
        return [
            "Every runtime decision has a governance origin",
            "Policy violations trigger intervention",
            "Constraints are evaluated before operations proceed",
            "Governance decisions are traceable and auditable",
        ]
    
    @staticmethod
    def get_evidence_invariants() -> List[str]:
        """Return evidence invariants (all actions must produce evidence)."""
        return [
            "Every governance decision produces evidence",
            "Intervention actions produce evidence",
            "Policy evaluations produce evidence",
            "Arbitration decisions produce evidence",
        ]
    
    @staticmethod
    def get_invariants() -> List[str]:
        """Return all invariants."""
        return (
            GovernanceInvariants.get_structural_invariants()
            + GovernanceInvariants.get_behavioral_invariants()
            + GovernanceInvariants.get_evidence_invariants()
        )


# =============================================================================
# GOVERNANCE LIFECYCLE
# =============================================================================

class LifecyclePhase(Enum):
    """Phases in the governance decision lifecycle."""
    
    OBSERVATION = "observation"          # Runtime state observed
    POLICY_EVALUATION = "policy_evaluation"  # Policies evaluated against state
    OBJECTIVE_EVALUATION = "objective_evaluation"  # Objectives checked
    CONSTRAINT_EVALUATION = "constraint_evaluation"  # Constraints validated
    RISK_ASSESSMENT = "risk_assessment"     # Risk analysis performed
    DECISION_FORMATION = "decision_formation"  # Decision made
    AUTHORIZATION = "authorization"         # Authority verified
    EXECUTION = "execution"                 # Decision executed
    VERIFICATION = "verification"           # Result verified
    EVIDENCE_PUBLICATION = "evidence_publication"  # Evidence recorded
    DIAGNOSTICS = "diagnostics"             # Diagnostics generated
    ARCHIVAL = "archival"                   # Archived for audit


@dataclass
class GovernanceLifecycle:
    """
    Lifecycle of a governance decision.
    
    Every governance operation follows this lifecycle:
    
    Observation -> Policy Evaluation -> Objective Evaluation -> 
    Constraint Evaluation -> Risk Assessment -> Decision Formation ->
    Authorization -> Execution -> Verification -> Evidence Publication ->
    Diagnostics -> Archival
    
    Each transition is observable and reproducible.
    """
    
    lifecycle_id: str
    phase: LifecyclePhase = LifecyclePhase.OBSERVATION
    timestamp_utc: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    evidence_chain: List[Dict[str, Any]] = field(default_factory=list)
    
    def transition_to(self, new_phase: LifecyclePhase) -> None:
        """Transition to a new lifecycle phase."""
        old_phase = self.phase
        self.evidence_chain.append({
            "from_phase": old_phase.value,
            "to_phase": new_phase.value,
            "timestamp_utc": time.time(),
            "context": self.context.copy(),
        })
        self.phase = new_phase
    
    def get_full_history(self) -> List[Dict[str, Any]]:
        """Return full lifecycle history."""
        return [
            {
                "lifecycle_id": self.lifecycle_id,
                "phase": self.phase.value,
                "timestamp_utc": self.timestamp_utc,
                "evidence_chain": self.evidence_chain,
            }
        ]
    
    @staticmethod
    def create(lifecycle_id: Optional[str] = None) -> "GovernanceLifecycle":
        """Create a new governance lifecycle."""
        return GovernanceLifecycle(
            lifecycle_id=lifecycle_id or f"governance_lifecycle_{uuid.uuid4().hex[:12]}"
        )


# =============================================================================
# GOVERNANCE SESSION
# =============================================================================

@dataclass
class GovernanceSession:
    """
    A governance session represents a complete governance operation.
    
    Each session has a clear start, execution through lifecycle phases,
    and end with full evidence trail.
    """
    
    session_id: str
    started_at: float = field(default_factory=time.time)
    lifecycle: Optional[GovernanceLifecycle] = None
    policies_evaluated: List[str] = field(default_factory=list)
    constraints_validated: List[str] = field(default_factory=list)
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)
    interventions_performed: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        """Check if session reached archival phase."""
        return self.lifecycle and self.lifecycle.phase == LifecyclePhase.ARCHIVAL
    
    def complete(self) -> Dict[str, Any]:
        """Complete the session and return final report."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "completed_at": time.time(),
            "policies_evaluated": len(set(self.policies_evaluated)),
            "constraints_validated": len(set(self.constraints_validated)),
            "decisions_made": len(self.decisions_made),
            "interventions_performed": len(self.interventions_performed),
            "lifecycle_complete": self.is_complete,
        }
    
    @staticmethod
    def create(session_id: Optional[str] = None) -> "GovernanceSession":
        """Create a new governance session."""
        return GovernanceSession(
            session_id=session_id or f"governance_session_{uuid.uuid4().hex[:12]}"
        )


__all__ = [
    "GovernancePhilosophy",
    "OperationalPhilosophy", 
    "SupervisionPhilosophy",
    "GovernanceTerminology",
    "GovernanceArchitectureBoundaries",
    "GovernanceOwnership",
    "GovernanceInvariants",
    "LifecyclePhase",
    "GovernanceLifecycle",
    "GovernanceSession",
]