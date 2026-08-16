# Memory Audit Base Classes - Phase 5.1.9
# =========================================

"""
Base classes and interfaces for Memory Audit components.

This module defines the abstract base classes that all audit components must
implement, ensuring consistent behavior across the subsystem.
"""

from __future__ import annotations

import abc
from typing import Protocol, runtime_checkable, Optional
from dataclasses import dataclass


# =============================================================================
# ADAPTER BASE - Interface for memory access adapters
# =============================================================================


@runtime_checkable
class MemoryAuditAdapter(Protocol):
    """
    Protocol for memory audit adapters.
    
    Adapters provide read-only access to memory systems for auditing purposes.
    They never modify memory, only retrieve and report on its state.
    
    Anti-Patterns Rejected:
        - Mutating memory through adapters
        - Non-deterministic retrieval
        - Hidden side effects
    
    Adapter Laws:
        ADAPTER-LAW-001: Adapters provide read-only access
        ADAPTER-LAW-002: Retrieval is deterministic (same input → same output)
        ADAPTER-LAW-003: Missing data raises appropriate errors
        ADAPTER-LAW-004: No side effects occur during retrieval
    """
    
    # Class attributes
    name: str  # Unique identifier for this adapter type
    
    @abc.abstractmethod
    def get_memory_artifacts(
        self,
        limit: int = 1000,
        offset: int = 0,
    ) -> tuple:
        """
        Retrieve memory artifacts from the system.
        
        Args:
            limit: Maximum number of artifacts to return
            offset: Number of artifacts to skip
            
        Returns:
            Tuple of memory artifacts (may be empty)
            
        Raises:
            MemoryAuditAdapterError: If retrieval fails
        """
        ...
    
    @abc.abstractmethod
    def get_memory_artifact_by_id(self, artifact_id: str):
        """
        Retrieve a specific memory artifact by ID.
        
        Args:
            artifact_id: Unique identifier of the artifact
            
        Returns:
            The requested memory artifact
            
        Raises:
            MemoryAuditNotFoundError: If artifact doesn't exist
            MemoryAuditAdapterError: If retrieval fails
        """
        ...
    
    @abc.abstractmethod
    def get_references_for_artifact(
        self,
        artifact_id: str,
        reference_type: Optional[str] = None,
    ) -> tuple:
        """
        Retrieve references associated with an artifact.
        
        Args:
            artifact_id: ID of the artifact
            reference_type: Filter by type (optional)
            
        Returns:
            Tuple of reference tuples (target_id, ref_type)
        """
        ...
    
    @abc.abstractmethod
    def get_health(self) -> bool:
        """
        Check if adapter can access memory.
        
        Returns:
            True if memory is accessible, False otherwise
        """
        ...


# =============================================================================
# VALIDATOR BASE - Interface for validation checks
# =============================================================================


@runtime_checkable
class MemoryAuditValidator(Protocol):
    """
    Protocol for audit validators.
    
    Validators perform specific validation checks on memory artifacts and
    produce AuditFindings for issues found.
    
    Anti-Patterns Rejected:
        - Validators that modify memory
        - Non-deterministic validation logic
        - Silent failure (always return a finding)
    
    Validator Laws:
        VALIDATOR-LAW-001: Validation is deterministic
        VALIDATOR-LAW-002: Missing data produces findings, not errors
        VALIDATOR-LAW-003: All validations produce explicit results
    """
    
    @property
    @abc.abstractmethod
    def validation_type(self) -> str:
        """Type of validation this validator performs."""
        ...
    
    @property
    @abc.abstractmethod
    def severity_level(self) -> str:
        """Default severity level for findings from this validator."""
        ...
    
    @abc.abstractmethod
    def validate(
        self,
        artifact,
        context: Optional[dict] = None,
    ) -> list:
        """
        Validate a memory artifact.
        
        Args:
            artifact: The memory artifact to validate
            context: Additional context for validation (optional)
            
        Returns:
            List of AuditFinding objects (may be empty if valid)
        """
        ...
    
    @abc.abstractmethod
    def get_statistics(self) -> dict:
        """
        Get statistics about this validator's operation.
        
        Returns:
            Dictionary with counts and metrics
        """
        ...


# =============================================================================
# PLANNER BASE - Interface for audit planning
# =============================================================================


@runtime_checkable
class MemoryAuditPlanner(Protocol):
    """
    Protocol for audit planners.
    
    Planners analyze audit requests and create execution plans that determine
    which validators to run, in what order, with what parameters.
    
    Anti-Patterns Rejected:
        - Non-deterministic planning
        - Missing validation strategies
        - Hidden plan dependencies
    
    Planner Laws:
        PLANNER-LAW-001: Plans are deterministic given same inputs
        PLANNER-LAW-002: All required validations are included
        PLANNER-LAW-003: Plan order respects dependencies
    """
    
    @abc.abstractmethod
    def create_plan(
        self,
        request,
    ) -> dict:
        """
        Create an audit execution plan from a request.
        
        Args:
            request: MemoryAuditRequest to plan for
            
        Returns:
            Dictionary with plan details (validators, order, parameters)
        """
        ...
    
    @abc.abstractmethod
    def validate_plan(
        self,
        plan: dict,
    ) -> bool:
        """
        Validate that a plan is well-formed.
        
        Args:
            plan: Plan dictionary to validate
            
        Returns:
            True if plan is valid, False otherwise
        """
        ...


# =============================================================================
# ANALYZER BASE - Interface for analysis operations
# =============================================================================


@runtime_checkable
class MemoryAuditAnalyzer(Protocol):
    """
    Protocol for audit analyzers.
    
    Analyzers perform deep analysis beyond basic validation, such as:
        - Lineage verification
        - Provenance consistency checks
        - Duplication detection
        - Integrity verification
    
    Anti-Patterns Rejected:
        - Modifying memory during analysis
        - Non-deterministic analysis results
    """
    
    @abc.abstractmethod
    def analyze(
        self,
        artifacts: tuple,
        context: Optional[dict] = None,
    ) -> list:
        """
        Perform deep analysis on memory artifacts.
        
        Args:
            artifacts: Tuple of memory artifacts to analyze
            context: Additional context (optional)
            
        Returns:
            List of analysis findings
        """
        ...
    
    @abc.abstractmethod
    def get_analysis_type(self) -> str:
        """Type of analysis this analyzer performs."""
        ...


# =============================================================================
# REPORT GENERATOR BASE - Interface for report creation
# =============================================================================


@runtime_checkable
class MemoryAuditReportGenerator(Protocol):
    """
    Protocol for audit report generators.
    
    Report generators create MemoryAuditReports from audit sessions,
    aggregating findings and computing health metrics.
    
    Anti-Patterns Rejected:
        - Mutable reports (reports must be immutable)
        - Hiding findings in reports
        - Non-deterministic report generation
    """
    
    @abc.abstractmethod
    def generate_report(
        self,
        session,
    ) -> dict:
        """
        Generate an audit report from a completed session.
        
        Args:
            session: Completed MemoryAuditSession
            
        Returns:
            Dictionary representation of MemoryAuditReport
        """
        ...
    
    @abc.abstractmethod
    def aggregate_health(
        self,
        findings: tuple,
    ) -> dict:
        """
        Aggregate health metrics from audit findings.
        
        Args:
            findings: Tuple of AuditFinding objects
            
        Returns:
            Health assessment dictionary
        """
        ...


__all__ = [
    # Base classes
    "MemoryAuditAdapter",
    "MemoryAuditValidator",
    "MemoryAuditPlanner",
    "MemoryAuditAnalyzer",
    "MemoryAuditReportGenerator",
]