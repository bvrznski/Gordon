# Evidence Collector - Gordon Executive Network Audit Subsystem
# =============================================================

"""
Evidence collection module for audit sessions.

This module handles gathering raw data from executive components,
extracting relevant observations, and transforming them into
evidence items that can be analyzed.
"""

from dataclasses import dataclass, field
from typing import Protocol, Optional, List, Dict, Any, Tuple
import time

from gordon_system.src.agent.networks.executive.audit.adapters.executive import (
    ExecutiveStateAdapter,
    ExecutiveContextAdapter,
    ExecutiveProgramAdapter,
    ExecutiveConflictAdapter,
    ExecutiveDemandAdapter,
)
from gordon_system.src.agent.networks.executive.audit.models import AuditEvidence


@dataclass
class EvidenceCollector:
    """
    Collects evidence from executive components during an audit session.
    
    The collector is stateful and accumulates evidence as it queries
    different components. It never modifies any component state - it only
    observes and records what it finds.
    """
    
    config: Dict[str, Any]
    """Configuration for collection behavior."""
    
    adapters: Dict[str, Any] = field(default_factory=dict)
    """Adapter instances for querying executive components."""
    
    collected_evidence: List[AuditEvidence] = field(default_factory=list)
    """Evidence items collected during this session."""
    
    start_time_utc: float = field(default_factory=time.time)
    """When collection started."""
    
    def add_adapter(self, name: str, adapter: Any) -> None:
        """
        Register an adapter for evidence collection.
        
        Args:
            name: Name of the adapter (e.g., 'state', 'context')
            adapter: Adapter instance implementing the expected protocol
        """
        self.adapters[name] = adapter
    
    def collect_state_evidence(self, state_data: Dict[str, Any]) -> List[AuditEvidence]:
        """
        Collect evidence from executive state data.
        
        Args:
            state_data: Raw state dictionary to analyze
            
        Returns:
            List of evidence items created from the state
        """
        evidence = []
        timestamp = time.time()
        
        # Mode observation
        if "mode" in state_data:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_mode",
                timestamp_utc=timestamp,
                source_type="state",
                source_id=state_data.get("state_id"),
                key="executive_mode",
                value=state_data["mode"],
            ))
        
        # Task set observation
        task_sets = state_data.get("active_task_set_ids", [])
        evidence.append(AuditEvidence(
            evidence_id=f"evidence_{timestamp}_taskset_count",
            timestamp_utc=timestamp,
            source_type="state",
            source_id=state_data.get("state_id"),
            key="task_set_count",
            value=len(task_sets),
        ))
        
        # Goal observation
        goals = state_data.get("active_goal_ids", [])
        evidence.append(AuditEvidence(
            evidence_id=f"evidence_{timestamp}_goal_count",
            timestamp_utc=timestamp,
            source_type="state",
            source_id=state_data.get("state_id"),
            key="goal_count",
            value=len(goals),
        ))
        
        # Commitment observation
        commitments = state_data.get("active_commitment_ids", [])
        evidence.append(AuditEvidence(
            evidence_id=f"evidence_{timestamp}_commitment_count",
            timestamp_utc=timestamp,
            source_type="state",
            source_id=state_data.get("state_id"),
            key="commitment_count",
            value=len(commitments),
        ))
        
        # Consistency observation
        if "consistency_class" in state_data:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_consistency",
                timestamp_utc=timestamp,
                source_type="state",
                source_id=state_data.get("state_id"),
                key="state_consistency",
                value=state_data["consistency_class"],
            ))
        
        self.collected_evidence.extend(evidence)
        return evidence
    
    def collect_context_evidence(self, context_data: Dict[str, Any]) -> List[AuditEvidence]:
        """
        Collect evidence from executive context data.
        
        Args:
            context_data: Raw context dictionary to analyze
            
        Returns:
            List of evidence items created from the context
        """
        evidence = []
        timestamp = time.time()
        
        # Projection count observation
        projections = context_data.get("projections", [])
        evidence.append(AuditEvidence(
            evidence_id=f"evidence_{timestamp}_projection_count",
            timestamp_utc=timestamp,
            source_type="context",
            source_id=context_data.get("context_id"),
            key="projection_count",
            value=len(projections),
        ))
        
        # Missing projections observation
        missing = context_data.get("required_projections_missing", [])
        if missing:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_missing_projections",
                timestamp_utc=timestamp,
                source_type="context",
                source_id=context_data.get("context_id"),
                key="missing_required_projections",
                value=len(missing),
                expected_value=0,
            ))
        
        self.collected_evidence.extend(evidence)
        return evidence
    
    def collect_program_evidence(self, program_data: Dict[str, Any]) -> List[AuditEvidence]:
        """
        Collect evidence from executive program data.
        
        Args:
            program_data: Raw program dictionary to analyze
            
        Returns:
            List of evidence items created from the program
        """
        evidence = []
        timestamp = time.time()
        
        # Status observation
        if "status" in program_data:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_program_status",
                timestamp_utc=timestamp,
                source_type="programs",
                source_id=program_data.get("program_id"),
                key="program_status",
                value=program_data["status"],
            ))
        
        # Progress observation
        if "progress" in program_data:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_program_progress",
                timestamp_utc=timestamp,
                source_type="programs",
                source_id=program_data.get("program_id"),
                key="program_progress",
                value=program_data["progress"],
            ))
        
        # Error observation
        errors = program_data.get("errors", [])
        if errors:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_program_errors",
                timestamp_utc=timestamp,
                source_type="programs",
                source_id=program_data.get("program_id"),
                key="error_count",
                value=len(errors),
            ))
        
        self.collected_evidence.extend(evidence)
        return evidence
    
    def collect_conflict_evidence(self, conflicts: List[Dict[str, Any]]) -> List[AuditEvidence]:
        """
        Collect evidence from executive conflict data.
        
        Args:
            conflicts: List of raw conflict dictionaries
            
        Returns:
            List of evidence items created from the conflicts
        """
        evidence = []
        timestamp = time.time()
        
        # Conflict count observation
        if conflicts:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_conflict_count",
                timestamp_utc=timestamp,
                source_type="conflicts",
                source_id=None,
                key="active_conflict_count",
                value=len(conflicts),
            ))
        
        # Critical conflict observation
        critical = [c for c in conflicts if c.get("severity") == "critical"]
        if critical:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_critical_conflicts",
                timestamp_utc=timestamp,
                source_type="conflicts",
                source_id=None,
                key="critical_conflict_count",
                value=len(critical),
            ))
        
        self.collected_evidence.extend(evidence)
        return evidence
    
    def collect_demand_evidence(self, demand_data: Dict[str, Any]) -> List[AuditEvidence]:
        """
        Collect evidence from executive demand data.
        
        Args:
            demand_data: Raw demand dictionary to analyze
            
        Returns:
            List of evidence items created from the demand
        """
        evidence = []
        timestamp = time.time()
        
        # Demand level observation
        if "demand_level" in demand_data:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_demand_level",
                timestamp_utc=timestamp,
                source_type="demand",
                source_id=demand_data.get("source_id"),
                key="control_demand_level",
                value=demand_data["demand_level"],
            ))
        
        # Cognitive load observation
        if "estimated_cognitive_load" in demand_data:
            evidence.append(AuditEvidence(
                evidence_id=f"evidence_{timestamp}_cognitive_load",
                timestamp_utc=timestamp,
                source_type="demand",
                source_id=demand_data.get("source_id"),
                key="estimated_cognitive_load",
                value=demand_data["estimated_cognitive_load"],
            ))
        
        self.collected_evidence.extend(evidence)
        return evidence
    
    def get_collected_evidence(self) -> Tuple[AuditEvidence, ...]:
        """
        Get all evidence collected so far.
        
        Returns:
            Tuple of all AuditEvidence items
        """
        return tuple(self.collected_evidence)


class EvidenceCollectionAdapter(Protocol):
    """Protocol for adapters that support evidence collection."""
    
    def collect_all_evidence(self) -> List[Dict[str, Any]]:
        """
        Collect all available evidence from this component.
        
        Returns:
            List of raw evidence dictionaries
        """
        ...