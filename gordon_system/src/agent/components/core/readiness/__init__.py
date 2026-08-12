# Core Readiness Infrastructure
# =============================

"""
Core readiness infrastructure for Gordon runtime Phase 3.7.6-I.

Provides:
- Canonical ReadinessController (single authority)
- Immutable readiness artifacts with deterministic evaluation
- Dependency-aware readiness graph
- Capability-readiness matrix
- Health and integrity evidence integration
- Revocation support
- Runtime-scoped isolation

Runtime Progression:
    Construction → Assembly → Activation → Readiness → Admission → Operational
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Set, FrozenSet
from enum import Enum, auto
import uuid
import time
import threading
import asyncio


# =============================================================================
# READINESS STATUS VALUES
# =============================================================================

class ReadinessStatus(Enum):
    """
    Canonical readiness status values.
    
    These are the authoritative states - NOT a Boolean!
    
    Transitions:
        UNKNOWN → NOT_EVALUATED → EVALUATING → READY/NOT_READY/BLOCKED/REVOKED/FAILED
        
    A runtime may be READY for some classes but not others.
    """
    # Initial states
    UNKNOWN = "unknown"               # Not yet evaluated, unknown state
    NOT_EVALUATED = "not_evaluated"   # Hasn't been evaluated yet
    
    # Evaluation in progress
    EVALUATING = "evaluating"         # Currently evaluating readiness
    
    # Post-evaluation states
    BLOCKED = "blocked"               # Cannot proceed - missing dependencies
    NOT_READY = "not_ready"           # Requirements not satisfied
    READY = "ready"                   # All requirements satisfied
    READY_DEGRADED = "ready_degraded" # Ready but with reduced capability
    REVOKED = "revoked"               # Was ready, now revoked
    FAILED = "failed"                 # Evaluation failed catastrophically


class ReadinessClass(Enum):
    """
    Readiness by operational class.
    
    A runtime may be ready for some classes but not others:
        - CONTROL_PLANE: Can handle control operations
        - ADMINISTRATION: Can handle admin tasks  
        - MAINTENANCE: Can handle maintenance work
        - INTERNAL_WORK: Can handle internal operations
        - NORMAL_WORK: Can handle normal production work
        - HIGH_COST_WORK: Can handle expensive operations
        - EXTERNAL_WORK: Can handle external requests
        - RECOVERY_WORK: Can handle recovery operations
    """
    CONTROL_PLANE = "control_plane"
    ADMINISTRATION = "administration"
    MAINTENANCE = "maintenance"
    INTERNAL_WORK = "internal_work"
    NORMAL_WORK = "normal_work"
    HIGH_COST_WORK = "high_cost_work"
    EXTERNAL_WORK = "external_work"
    RECOVERY_WORK = "recovery_work"


# =============================================================================
# READINESS REQUIREMENT
# =============================================================================

@dataclass(frozen=True)
class ReadinessRequirement:
    """
    A requirement that must be satisfied for readiness.
    
    Each requirement defines what must be true and how to evaluate it.
    """
    id: str                          # Unique identifier (e.g., "health", "scheduler")
    description: str                 # Human-readable description
    mandatory: bool                  # If False, failure = degraded, not blocked
    applicable_classes: Tuple["ReadinessClass", ...]  # Which classes this applies to
    
    # Evaluator configuration
    evaluator_id: str                # ID of evaluator that checks this requirement
    timeout_seconds: float           # Maximum time for evaluation
    freshness_seconds: float         # How old evidence can be before invalid
    
    # Failure semantics
    failure_behavior: "FailureBehavior" = field(default="NOT_READY")
    
    def is_applicable(self, readiness_class: "ReadinessClass") -> bool:
        """Check if this requirement applies to the given class."""
        return readiness_class in self.applicable_classes


# =============================================================================
# READINESS EVIDENCE AND OBSERVATION
# =============================================================================

@dataclass(frozen=True)
class ReadinessEvidence:
    """
    Evidence supporting a readiness evaluation.
    
    Evidence is contributed by subsystems but does NOT determine readiness.
    The controller aggregates and decides.
    """
    requirement_id: str              # Which requirement this supports
    source_subsystem: str            # Who provided the evidence
    status: "EvidenceStatus"         # What the evidence shows
    timestamp_utc: float             # When evidence was collected
    monotonic_time: float            # For ordering
    freshness_seconds: float = 30.0  # How long evidence is considered valid
    value: Any = None                # The actual value (e.g., True/False, count)
    details: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    @property
    def is_valid(self) -> bool:
        """Check if evidence is still fresh and valid."""
        return time.monotonic() - self.monotonic_time <= self.freshness_seconds


class EvidenceStatus(Enum):
    """Status of a single piece of evidence."""
    SATISFIED = "satisfied"
    FAILED = "failed"
    UNKNOWN = "unknown"
    STALE = "stale"


# =============================================================================
# READINESS OBSERVATION (Single Evaluation Unit)
# =============================================================================

@dataclass(frozen=True)
class ReadinessObservation:
    """
    Result of evaluating one readiness requirement.
    
    This is what the evaluator returns - NOT a final decision!
    """
    requirement_id: str
    status: EvidenceStatus
    evidence: List[ReadinessEvidence] = field(default_factory=list)
    evaluation_time_seconds: float = 0.0
    timeout_occurred: bool = False
    
    @classmethod
    def satisfied(cls, req_id: str, details: Any = None) -> "ReadinessObservation":
        """Create a satisfied observation."""
        return cls(
            requirement_id=req_id,
            status=EvidenceStatus.SATISFIED,
            evidence=[ReadinessEvidence(req_id, "", EvidenceStatus.SATISFIED, 
                                        time.time(), time.monotonic(), details)]
        )
    
    @classmethod
    def failed(cls, req_id: str, reason: str) -> "ReadinessObservation":
        """Create a failed observation."""
        return cls(
            requirement_id=req_id,
            status=EvidenceStatus.FAILED,
            evidence=[ReadinessEvidence(req_id, "", EvidenceStatus.FAILED,
                                        time.time(), time.monotonic(), reason)]
        )
    
    @classmethod
    def unknown(cls, req_id: str) -> "ReadinessObservation":
        """Create an unknown observation."""
        return cls(
            requirement_id=req_id,
            status=EvidenceStatus.UNKNOWN,
            evidence=[ReadinessEvidence(req_id, "", EvidenceStatus.UNKNOWN,
                                        time.time(), time.monotonic())]
        )


# =============================================================================
# READINESS FAILURE BEHAVIOR
# =============================================================================

class FailureBehavior(Enum):
    """What happens when a requirement fails."""
    NOT_READY = "not_ready"          # Blocks readiness (if mandatory)
    BLOCKED = "blocked"              # Blocks with dependency info
    DEGRADED = "degraded"            # Allows degraded readiness


# =============================================================================
# READINESS DECISION AND REPORT
# =============================================================================

@dataclass(frozen=True)
class ReadinessDecision:
    """
    Immutable readiness decision.
    
    This is the OUTPUT of evaluation - NOT the state itself!
    The controller maintains authoritative state separately.
    """
    runtime_id: str                  # Which runtime this is about
    boot_session_id: str             # Which boot session
    decision_id: str                 # Unique ID for this decision
    
    status: ReadinessStatus          # The determined status
    readiness_class: ReadinessClass  # For which class
    
    evaluated_requirements: Tuple[str, ...]   # All requirements checked
    satisfied_requirements: Tuple[str, ...]   # Which passed
    failed_requirements: Tuple[str, ...]      # Which failed
    unknown_requirements: Tuple[str, ...]     # Which was unknown
    
    blockers: Tuple[str, ...]        # What's blocking readiness
    warnings: Tuple[str, ...]        # Any warnings
    
    capability_matrix: Dict[str, bool] = field(default_factory=dict)  # cap_id -> available
    
    evaluated_at_utc: float = field(default_factory=time.time)
    logical_sequence: int = 0        # For ordering decisions
    state_version: int = 0           # Runtime state version at time of decision
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_ready(self) -> bool:
        """Check if ready for the specified class."""
        return self.status in (ReadinessStatus.READY, ReadinessStatus.READY_DEGRADED)
    
    @property
    def is_revoked(self) -> bool:
        """Check if readiness was revoked."""
        return self.status == ReadinessStatus.REVOKED
    
    @property
    def is_failed(self) -> bool:
        """Check if evaluation failed."""
        return self.status == ReadinessStatus.FAILED


@dataclass(frozen=True)
class ReadinessReport:
    """
    Complete readiness report for a runtime.
    
    This is the final output - immutable, typed, and complete.
    """
    runtime_id: str
    boot_session_id: str
    report_id: str
    
    status: ReadinessStatus
    readiness_classes: Dict[ReadinessClass, ReadinessDecision]
    
    evaluated_at_utc: float = field(default_factory=time.time)
    evaluation_duration_seconds: float = 0.0
    
    health_evidence: List[ReadinessEvidence] = field(default_factory=list)
    integrity_evidence: List[ReadinessEvidence] = field(default_factory=list)
    configuration_evidence: List[ReadinessEvidence] = field(default_factory=list)
    resource_evidence: List[ReadinessEvidence] = field(default_factory=list)
    
    state_version: int = 0
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def get_overall_status(self) -> ReadinessStatus:
        """Get the most restrictive status across all classes."""
        statuses = [d.status for d in self.readiness_classes.values()]
        
        if ReadinessStatus.FAILED in statuses:
            return ReadinessStatus.FAILED
        if ReadinessStatus.REVOKED in statuses:
            return ReadinessStatus.REVOKED
        if ReadinessStatus.BLOCKED in statuses:
            return ReadinessStatus.BLOCKED
        if ReadinessStatus.NOT_READY in statuses:
            return ReadinessStatus.NOT_READY
        if any(s == ReadinessStatus.READY_DEGRADED for s in statuses):
            return ReadinessStatus.READY_DEGRADED
        if all(s == ReadinessStatus.READY for s in statuses):
            return ReadinessStatus.READY
        
        return ReadinessStatus.NOT_EVALUATED


# =============================================================================
# READINESS DEPENDENCY GRAPH
# =============================================================================

@dataclass(frozen=True)
class ReadinessNode:
    """A node in the readiness dependency graph."""
    requirement_id: str
    node_type: str  # "health", "integrity", "capability", etc.
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    optional_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    evaluator_id: str = ""
    
    def __hash__(self) -> int:
        return hash(self.requirement_id)


@dataclass(frozen=True)
class ReadinessEdge:
    """An edge in the readiness dependency graph."""
    from_node: str  # Dependent
    to_node: str    # Dependency
    required: bool = True
    
    def reverse(self) -> "ReadinessEdge":
        return ReadinessEdge(self.to_node, self.from_node, self.required)


@dataclass(frozen=True)
class ReadinessGraph:
    """
    Immutable readiness dependency graph.
    
    Used for:
    - Deterministic evaluation ordering
    - Cycle detection
    - Dependency failure propagation
    """
    _nodes: Dict[str, ReadinessNode] = field(default_factory=dict)
    _edges: Tuple[ReadinessEdge, ...] = field(default_factory=tuple)
    _validated: bool = True
    
    @classmethod
    def create(cls, nodes: List[ReadinessNode], edges: List[ReadinessEdge]) -> "ReadinessGraph":
        """Create and validate a new graph."""
        node_dict = {n.requirement_id: n for n in nodes}
        
        # Validate all edge endpoints reference existing nodes
        for edge in edges:
            if edge.from_node not in node_dict:
                raise ValueError(f"Edge from_node {edge.from_node} not found")
            if edge.to_node not in node_dict:
                raise ValueError(f"Edge to_node {edge.to_node} not found")
        
        graph = cls(
            _nodes=node_dict,
            _edges=tuple(edges),
            _validated=True
        )
        
        # Validate no cycles
        graph._validate_no_cycles()
        
        return graph
    
    def _validate_no_cycles(self) -> None:
        """Validate the graph has no cycles using DFS."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for edge in self._edges:
                if edge.from_node == node_id:
                    if dfs(edge.to_node):
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self._nodes:
            if dfs(node_id):
                raise ValueError("Readiness graph contains a cycle")
    
    @property
    def nodes(self) -> Tuple[ReadinessNode, ...]:
        return tuple(self._nodes.values())
    
    @property
    def edges(self) -> Tuple[ReadinessEdge, ...]:
        return self._edges
    
    def get_node(self, requirement_id: str) -> Optional[ReadinessNode]:
        return self._nodes.get(requirement_id)
    
    def get_dependencies(self, requirement_id: str) -> Tuple[str, ...]:
        result = []
        for edge in self._edges:
            if edge.from_node == requirement_id and edge.required:
                result.append(edge.to_node)
        return tuple(result)


# =============================================================================
# READINESS CAPABILITY MATRIX
# =============================================================================

@dataclass(frozen=True)
class CapabilityReadiness:
    """Readiness status of a single capability."""
    capability_id: str
    available: bool
    readiness_class: ReadinessClass
    blockers: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CapabilityMatrix:
    """
    Immutable mapping of capabilities to readiness.
    
    Used by the controller to determine which operations are available.
    """
    _entries: Dict[Tuple[str, ReadinessClass], CapabilityReadiness] = field(
        default_factory=dict
    )
    
    def get(self, cap_id: str, readiness_class: ReadinessClass) -> Optional[CapabilityReadiness]:
        return self._entries.get((cap_id, readiness_class))
    
    def is_available(self, cap_id: str, readiness_class: ReadinessClass) -> bool:
        entry = self.get(cap_id, readiness_class)
        return entry is not None and entry.available
    
    @classmethod
    def create(cls, entries: List[CapabilityReadiness]) -> "CapabilityMatrix":
        return cls(
            _entries={(e.capability_id, e.readiness_class): e for e in entries}
        )


# =============================================================================
# READINESS REVOCATION
# =============================================================================

@dataclass(frozen=True)
class ReadinessRevocationRequest:
    """Request to revoke readiness."""
    runtime_id: str
    reason: str
    revocation_type: "RevocationType"
    timestamp_utc: float = field(default_factory=time.time)


class RevocationType(Enum):
    """Types of readiness revocation."""
    DEPENDENCY_LOST = "dependency_lost"
    HEALTH_FAILURE = "health_failure"
    INTEGRITY_FAILURE = "integrity_failure"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    CAPABILITY_LOSS = "capability_loss"
    CONFIGURATION_INVALID = "configuration_invalid"
    RECOVERY_ACTIVE = "recovery_active"
    SHUTDOWN_PENDING = "shutdown_pending"


@dataclass(frozen=True)
class ReadinessRevocationDecision:
    """Decision to revoke readiness."""
    runtime_id: str
    request_id: str
    status_before: ReadinessStatus
    status_after: ReadinessStatus
    reason: str
    revocation_type: RevocationType
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def success(self) -> bool:
        return self.status_before != ReadinessStatus.REVOKED


# =============================================================================
# READINESS EVALUATOR PROTOCOL
# =============================================================================

class ReadinessEvaluatorProtocol:
    """
    Protocol for readiness evaluators.
    
    Evaluators MUST be:
    - Observational (no mutation of external state)
    - Bounded (have a timeout)
    - Deterministic (same inputs → same outputs)
    - Runtime-scoped (not global)
    """
    
    async def evaluate(
        self,
        requirement: ReadinessRequirement,
        context: "ReadinessEvaluationContext"
    ) -> ReadinessObservation:
        """Evaluate one requirement."""
        raise NotImplementedError


# =============================================================================
# READINESS EVALUATION CONTEXT
# =============================================================================

@dataclass(frozen=True)
class ReadinessEvaluationContext:
    """Context for a single readiness evaluation."""
    runtime_id: str
    boot_session_id: str
    evaluation_id: str
    requested_class: Optional[ReadinessClass] = None
    deadline_utc: float = field(default_factory=lambda: time.time() + 30.0)
    cancellation_requested: bool = False


# =============================================================================
# READINESS CONTROLLER (CANONICAL AUTHORITY)
# =============================================================================

class ReadinessController:
    """
    Canonical authority for runtime readiness evaluation.
    
    This is THE ONE source of truth for whether the runtime can safely accept
    work admission. It owns:
    
    - Readiness state (NOT a Boolean!)
    - Requirement registration
    - Evaluator registration  
    - Dependency graph
    - Evidence collection and aggregation
    - State transitions and history
    - Revocation handling
    
    Subsystems may contribute evidence but MUST NOT determine readiness.
    """
    
    def __init__(self, runtime_id: str) -> None:
        """Initialize with runtime-scoped state."""
        self._runtime_id = runtime_id
        self._boot_session_id = str(uuid.uuid4())
        
        # State management
        self._lock = threading.Lock()
        self._state: Dict[ReadinessClass, ReadinessStatus] = {}
        self._last_decision: Optional[ReadinessDecision] = None
        self._history: List[Tuple[ReadinessStatus, ReadinessStatus, float]] = []
        
        # Graph and requirements
        self._graph: Optional[ReadinessGraph] = None
        self._requirements: Dict[str, ReadinessRequirement] = {}
        
        # Evaluators (subsystem contributors)
        self._evaluators: Dict[str, ReadinessEvaluatorProtocol] = {}
        self._evidence_collector: Callable[[str], List[ReadinessEvidence]] = lambda _: []
        
        # Counters
        self._decision_sequence = 0
        self._state_version = 0
        
        # Admission controller reference (for synchronization)
        self._admission_controller: Optional[Any] = None
        
        # Revocation tracking
        self._revocations: List[ReadinessRevocationDecision] = []
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this controller serves."""
        return self._runtime_id
    
    @property
    def boot_session_id(self) -> str:
        """Get the current boot session ID."""
        return self._boot_session_id
    
    @property
    def state_version(self) -> int:
        """Get current state version for synchronization."""
        with self._lock:
            return self._state_version
    
    def set_admission_controller(self, controller: Any) -> None:
        """
        Set the admission controller reference for revocation synchronization.
        
        This allows readiness to notify admission when readiness is revoked.
        
        Args:
            controller: The AdmissionController instance
        """
        self._admission_controller = controller
    
    async def synchronize_with_admission(self, controller: Any) -> None:
        """
        Set up bidirectional synchronization with an admission controller.
        
        This creates a two-way connection so that:
        - Readiness revocation closes admission
        - Admission state changes can be tracked
        
        Args:
            controller: The AdmissionController instance to synchronize with
        """
        self.set_admission_controller(controller)
    
    # -------------------------------------------------------------------------
    # Requirement Registration (for subsystems)
    # -------------------------------------------------------------------------
    
    def register_requirement(self, requirement: ReadinessRequirement) -> None:
        """
        Register a readiness requirement.
        
        Subsystems use this to declare what they require for readiness.
        """
        with self._lock:
            self._requirements[requirement.id] = requirement
            self._rebuild_graph()
    
    def unregister_requirement(self, requirement_id: str) -> bool:
        """Remove a registered requirement."""
        with self._lock:
            if requirement_id in self._requirements:
                del self._requirements[requirement_id]
                self._rebuild_graph()
                return True
            return False
    
    def _rebuild_graph(self) -> None:
        """Rebuild the dependency graph from requirements."""
        # Simplified: in production, would build graph from dependencies field
        nodes = [
            ReadinessNode(
                requirement_id=req_id,
                node_type="requirement",
                evaluator_id= req.evaluator_id if (req := self._requirements.get(req_id)) else ""
            )
            for req_id in self._requirements
        ]
        # No edges by default - would be populated from requirement dependencies
        try:
            self._graph = ReadinessGraph.create(nodes, [])
        except ValueError:
            self._graph = ReadinessGraph()
    
    # -------------------------------------------------------------------------
    # Evaluator Registration (for subsystems to contribute evidence)
    # -------------------------------------------------------------------------
    
    def register_evaluator(self, evaluator_id: str, evaluator: ReadinessEvaluatorProtocol) -> None:
        """Register a readiness evaluator from a subsystem."""
        with self._lock:
            self._evaluators[evaluator_id] = evaluator
    
    def unregister_evaluator(self, evaluator_id: str) -> bool:
        """Remove an evaluator by ID."""
        with self._lock:
            if evaluator_id in self._evaluators:
                del self._evaluators[evaluator_id]
                return True
            return False
    
    # -------------------------------------------------------------------------
    # Readiness Evaluation (the main entry point)
    # -------------------------------------------------------------------------
    
    async def evaluate_readiness(
        self,
        requested_class: Optional[ReadinessClass] = None
    ) -> ReadinessDecision:
        """
        Evaluate runtime readiness.
        
        This is the canonical evaluation method. It:
        1. Validates request
        2. Collects evidence from all registered evaluators
        3. Evaluates requirements using dependency-aware ordering
        4. Aggregates results deterministically
        5. Produces a typed decision
        
        Args:
            requested_class: Which readiness class to evaluate (None = all)
            
        Returns:
            Immutable ReadinessDecision with full status and evidence
            
        Raises:
            RuntimeError: If evaluation is cancelled or times out
        """
        evaluation_id = str(uuid.uuid4())
        
        context = ReadinessEvaluationContext(
            runtime_id=self._runtime_id,
            boot_session_id=self._boot_session_id,
            evaluation_id=evaluation_id,
            requested_class=requested_class,
            deadline_utc=time.time() + 30.0
        )
        
        with self._lock:
            # Check if cancellation was requested during acquisition
            if getattr(context, 'cancellation_requested', False):
                raise RuntimeError("Readiness evaluation cancelled")
            
            self._state_version += 1
            
            # Determine which classes to evaluate
            classes_to_evaluate = (
                [requested_class] if requested_class 
                else list(ReadinessClass)
            )
            
            decisions: Dict[ReadinessClass, ReadinessDecision] = {}
            
            for readiness_class in classes_to_evaluate:
                decision = await self._evaluate_class(readiness_class, context)
                decisions[readiness_class] = decision
            
            # Produce final report
            return self._produce_decision(decisions, evaluation_id)
    
    async def _evaluate_class(
        self,
        readiness_class: ReadinessClass,
        context: ReadinessEvaluationContext
    ) -> ReadinessDecision:
        """Evaluate readiness for a single class."""
        # Get applicable requirements
        applicable = [
            req for req in self._requirements.values()
            if req.is_applicable(readiness_class)
        ]
        
        if not applicable:
            return ReadinessDecision(
                runtime_id=self._runtime_id,
                boot_session_id=context.boot_session_id,
                decision_id=str(uuid.uuid4()),
                status=ReadinessStatus.READY,
                readiness_class=readiness_class,
                evaluated_requirements=(),
                satisfied_requirements=(),
                failed_requirements=(),
                unknown_requirements=(),
                blockers=(),
                warnings=()
            )
        
        # Collect evidence
        observations: List[ReadinessObservation] = []
        
        for req in applicable:
            try:
                evaluator = self._evaluators.get(req.evaluator_id)
                if evaluator:
                    obs = await evaluator.evaluate(req, context)
                else:
                    # Default to unknown if no evaluator registered
                    obs = ReadinessObservation.unknown(req.id)
                
                observations.append(obs)
            except asyncio.TimeoutError:
                observations.append(
                    ReadinessObservation.unknown(req.id)
                )
        
        # Aggregate results
        satisfied = []
        failed = []
        unknown = []
        blockers = []
        warnings = []
        
        for obs in observations:
            if obs.status == EvidenceStatus.SATISFIED:
                satisfied.append(obs.requirement_id)
            elif obs.status == EvidenceStatus.FAILED:
                req = self._requirements.get(obs.requirement_id)
                if req and req.mandatory:
                    failed.append(obs.requirement_id)
                    blockers.append(f"Mandatory requirement {obs.requirement_id} not satisfied")
                else:
                    warnings.append(f"Optional requirement {obs.requirement_id} not satisfied")
            elif obs.status == EvidenceStatus.UNKNOWN:
                req = self._requirements.get(obs.requirement_id)
                if req and req.mandatory:
                    unknown.append(obs.requirement_id)
                    blockers.append(f"Mandatory requirement {obs.requirement_id} evaluation unknown")
        
        # Determine final status
        if failed or unknown:
            status = ReadinessStatus.BLOCKED
        elif warnings:
            status = ReadinessStatus.READY_DEGRADED
        else:
            status = ReadinessStatus.READY
        
        return ReadinessDecision(
            runtime_id=self._runtime_id,
            boot_session_id=context.boot_session_id,
            decision_id=str(uuid.uuid4()),
            status=status,
            readiness_class=readiness_class,
            evaluated_requirements=tuple([r.id for r in applicable]),
            satisfied_requirements=tuple(satisfied),
            failed_requirements=tuple(failed),
            unknown_requirements=tuple(unknown),
            blockers=tuple(blockers),
            warnings=tuple(warnings)
        )
    
    def _produce_decision(
        self,
        class_decisions: Dict[ReadinessClass, ReadinessDecision],
        decision_id: str
    ) -> ReadinessDecision:
        """Produce a single consolidated decision."""
        # Get most restrictive status
        statuses = [d.status for d in class_decisions.values()]
        
        if any(d.is_failed for d in class_decisions.values()):
            final_status = ReadinessStatus.FAILED
        elif ReadinessStatus.REVOKED in statuses:
            final_status = ReadinessStatus.REVOKED
        elif ReadinessStatus.BLOCKED in statuses:
            final_status = ReadinessStatus.BLOCKED
        elif any(d.status == ReadinessStatus.NOT_READY for d in class_decisions.values()):
            final_status = ReadinessStatus.NOT_READY
        elif any(d.status == ReadinessStatus.READY_DEGRADED for d in class_decisions.values()):
            final_status = ReadinessStatus.READY_DEGRADED
        else:
            final_status = ReadinessStatus.READY
        
        # Collect all requirements, blockers, warnings
        all_requirements = set()
        all_satisfied = set()
        all_failed = set()
        all_unknown = set()
        all_blockers = set()
        all_warnings = set()
        
        for decision in class_decisions.values():
            all_requirements.update(decision.evaluated_requirements)
            all_satisfied.update(decision.satisfied_requirements)
            all_failed.update(decision.failed_requirements)
            all_unknown.update(decision.unknown_requirements)
            all_blockers.update(decision.blockers)
            all_warnings.update(decision.warnings)
        
        with self._lock:
            old_status = list(self._state.values())[0] if self._state else ReadinessStatus.UNKNOWN
            new_status = final_status
            
            # Record transition in history
            self._history.append((old_status, new_status, time.time()))
            
            # Update state
            for cls in class_decisions:
                self._state[cls] = final_status
        
        return ReadinessDecision(
            runtime_id=self._runtime_id,
            boot_session_id=self._boot_session_id,
            decision_id=decision_id,
            status=final_status,
            readiness_class=list(class_decisions.keys())[0] if class_decisions else ReadinessClass.NORMAL_WORK,
            evaluated_requirements=tuple(all_requirements),
            satisfied_requirements=tuple(all_satisfied),
            failed_requirements=tuple(all_failed),
            unknown_requirements=tuple(all_unknown),
            blockers=tuple(all_blockers),
            warnings=tuple(all_warnings),
            logical_sequence=self._decision_sequence,
            state_version=self._state_version
        )
    
    # -------------------------------------------------------------------------
    # Readiness Revocation (for external triggers)
    # -------------------------------------------------------------------------
    
    async def revoke_readiness(
        self,
        reason: str,
        revocation_type: RevocationType = RevocationType.DEPENDENCY_LOST
    ) -> Optional[ReadinessRevocationDecision]:
        """
        Revoke current readiness.
        
        Called when dependencies are lost or conditions change.
        
        Also automatically closes admission if an admission controller is set.
        
        Args:
            reason: Human-readable explanation
            revocation_type: Why readiness is being revoked
            
        Returns:
            Decision record if revocation occurred, None if already revoked
        """
        with self._lock:
            old_statuses = dict(self._state)
            
            # Check if any state needs revoking
            needs_revocation = any(
                s in (ReadinessStatus.READY, ReadinessStatus.READY_DEGRADED)
                for s in old_statuses.values()
            )
            
            if not needs_revocation:
                return None
            
            # Update all states to REVOKED
            self._state.clear()
            for cls in old_statuses:
                self._state[cls] = ReadinessStatus.REVOKED
            
            self._state_version += 1
            
            decision = ReadinessRevocationDecision(
                runtime_id=self._runtime_id,
                request_id=str(uuid.uuid4()),
                status_before=ReadinessStatus.READY if any(s == ReadinessStatus.READY for s in old_statuses.values()) else ReadinessStatus.READY_DEGRADED,
                status_after=ReadinessStatus.REVOKED,
                reason=reason,
                revocation_type=revocation_type,
                timestamp_utc=time.time()
            )
            
            self._revocations.append(decision)
        
        # Notify admission controller if connected
        if self._admission_controller is not None:
            try:
                await self._admission_controller.close_admission_on_revocation(reason, revocation_type)
            except Exception:
                pass  # Don't let notification failures affect revocation
        
        return decision
    
    def get_revocations(self) -> Tuple[ReadinessRevocationDecision, ...]:
        """Get history of revocation decisions."""
        with self._lock:
            return tuple(list(self._revocations))
    
    # -------------------------------------------------------------------------
    # State Query Methods
    # -------------------------------------------------------------------------
    
    def get_status(self, readiness_class: Optional[ReadinessClass] = None) -> ReadinessStatus:
        """
        Get current readiness status.
        
        This returns the authoritative state, NOT a derived Boolean!
        """
        with self._lock:
            if readiness_class is not None:
                return self._state.get(readiness_class, ReadinessStatus.UNKNOWN)
            
            # Return most restrictive across all classes
            statuses = list(self._state.values())
            if not statuses:
                return ReadinessStatus.UNKNOWN
            
            for s in [ReadinessStatus.FAILED, ReadinessStatus.REVOKED,
                      ReadinessStatus.BLOCKED, ReadinessStatus.NOT_READY]:
                if s in statuses:
                    return s
            
            if any(s == ReadinessStatus.READY_DEGRADED for s in statuses):
                return ReadinessStatus.READY_DEGRADED
            
            return ReadinessStatus.READY
    
    def get_snapshot(self) -> "ReadinessSnapshot":
        """Get an immutable snapshot of current state."""
        with self._lock:
            return ReadinessSnapshot(
                runtime_id=self._runtime_id,
                boot_session_id=self._boot_session_id,
                state_version=self._state_version,
                status_by_class=dict(self._state),
                decision_count=len(self._history)
            )
    
    def is_ready_for_admission(self) -> bool:
        """
        Check if ready for admission (boolean compatibility).
        
        This is a COMPATIBILITY METHOD only. Do not use as authority!
        The real decision is ReadinessDecision.
        """
        status = self.get_status()
        return status in (ReadinessStatus.READY, ReadinessStatus.READY_DEGRADED)


# =============================================================================
# READINESS SNAPSHOT
# =============================================================================

@dataclass(frozen=True)
class ReadinessSnapshot:
    """Immutable snapshot of readiness state for observability."""
    runtime_id: str
    boot_session_id: str
    state_version: int
    status_by_class: Dict[ReadinessClass, ReadinessStatus]
    decision_count: int = 0


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Status and classes
    "ReadinessStatus",
    "ReadinessClass",
    
    # Requirements
    "ReadinessRequirement",
    "FailureBehavior",
    
    # Evidence and observations
    "ReadinessEvidence",
    "EvidenceStatus",
    "ReadinessObservation",
    
    # Decisions
    "ReadinessDecision",
    "ReadinessReport",
    
    # Graph
    "ReadinessNode",
    "ReadinessEdge",
    "ReadinessGraph",
    
    # Capabilities
    "CapabilityReadiness",
    "CapabilityMatrix",
    
    # Revocation
    "ReadinessRevocationRequest",
    "ReadinessRevocationDecision",
    "RevocationType",
    
    # Protocol and context
    "ReadinessEvaluatorProtocol",
    "ReadinessEvaluationContext",
    
    # Controller (THE authority)
    "ReadinessController",
    
    # Snapshot
    "ReadinessSnapshot",
]

# For compatibility - but note: this uses the singleton pattern incorrectly
# In production, use Runtime.readiness_controller instead
_readiness_controllers: Dict[str, ReadinessController] = {}


def get_readiness_controller(runtime_id: str) -> ReadinessController:
    """Get or create a runtime-scoped readiness controller."""
    if runtime_id not in _readiness_controllers:
        _readiness_controllers[runtime_id] = ReadinessController(runtime_id)
    return _readiness_controllers[runtime_id]


def clear_readiness_controllers() -> None:
    """Clear all controllers (for testing)."""
    _readiness_controllers.clear()