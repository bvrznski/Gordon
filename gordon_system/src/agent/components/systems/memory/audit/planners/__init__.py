# Memory Audit Planners - Phase 5.1.9
# =====================================

"""
Audit planners that create execution plans for audit operations.

Planners analyze audit requests and determine:
    - Which validators to run
    - In what order
    - With what parameters
"""

from __future__ import annotations


# =============================================================================
# BASE PLANNER - Abstract base class
# =============================================================================


class BaseAuditPlanner:
    """
    Abstract base class for audit planners.
    
    Planners must be deterministic and create complete plans.
    
    Anti-Patterns Rejected:
        - Non-deterministic planning
        - Missing validation strategies
        - Hidden plan dependencies
    """
    
    def __init__(self):
        """Initialize the planner."""
        self._plan_count = 0
    
    @property
    def stats(self) -> dict:
        """Get planner statistics."""
        return {"plans_created": self._plan_count}
    
    def create_plan(
        self,
        request,
    ) -> dict:
        """
        Create an audit execution plan from a request.
        
        Args:
            request: MemoryAuditRequest to plan for
            
        Returns:
            Dictionary with plan details
        """
        self._plan_count += 1
        return {}
    
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
        return True


# =============================================================================
# DEFAULT PLANNER - Standard planning logic
# =============================================================================


class DefaultAuditPlanner(BaseAuditPlanner):
    """
    Default planner for audit execution.
    
    Creates comprehensive plans that include:
        - Structural validation
        - Lineage verification
        - Provenance verification  
        - Reference validation
        - Duplication analysis
    
    Anti-Patterns Rejected:
        - Skipping critical validations
        - Non-deterministic plan order
    """
    
    def create_plan(
        self,
        request,
    ) -> dict:
        """
        Create an audit execution plan from a request.
        
        Args:
            request: MemoryAuditRequest to plan for
            
        Returns:
            Dictionary with validators, order, and parameters
        """
        self._plan_count += 1
        
        # Determine which validators to include based on audit type
        validators = []
        
        if request.audit_type in (
            "full_system",
            "structural",
            "integrity",
            "reference",
            "consistency",
        ):
            validators.append({
                "name": "structural_validator",
                "type": "base_audit_validator.StructuralValidator",
                "priority": 1,
            })
        
        if request.validate_lineage:
            validators.append({
                "name": "lineage_validator",
                "type": "base_audit_validator.LineageValidator",
                "priority": 2,
            })
        
        if request.validate_provenance:
            validators.append({
                "name": "provenance_validator",
                "type": "base_audit_validator.ProvenanceValidator",
                "priority": 2,
            })
        
        if request.check_references:
            validators.append({
                "name": "reference_validator",
                "type": "base_audit_validator.ReferenceValidator",
                "priority": 3,
            })
        
        if request.audit_type in (
            "full_system",
            "duplication",
        ):
            validators.append({
                "name": "duplication_validator",
                "type": "base_audit_validator.DuplicationValidator",
                "priority": 4,
            })
        
        return {
            "validators": validators,
            "order": [v["name"] for v in sorted(validators, key=lambda x: x["priority"])],
            "target_ids": list(request.target_ids) if request.target_ids else None,
            "depth": request.depth,
            "start_time_utc": request.timestamp_utc,
        }


# =============================================================================
# HEALTH CHECK PLANNER - Quick health assessment planner
# =============================================================================


class HealthCheckPlanner(BaseAuditPlanner):
    """
    Planner for quick health assessments.
    
    Creates minimal plans that focus on:
        - Adapter health checks
        - Basic structural validation
        - Reference integrity
    
    Anti-Patterns Rejected:
        - Skipping essential checks even in fast mode
    """
    
    def create_plan(
        self,
        request,
    ) -> dict:
        """
        Create a minimal health check plan.
        
        Args:
            request: MemoryAuditRequest to plan for
            
        Returns:
            Dictionary with validators, order, and parameters
        """
        self._plan_count += 1
        
        return {
            "validators": [
                {
                    "name": "structural_validator",
                    "type": "base_audit_validator.StructuralValidator",
                    "priority": 1,
                },
                {
                    "name": "reference_validator",
                    "type": "base_audit_validator.ReferenceValidator",
                    "priority": 2,
                },
            ],
            "order": ["structural_validator", "reference_validator"],
            "target_ids": list(request.target_ids) if request.target_ids else None,
            "depth": "basic",
            "start_time_utc": request.timestamp_utc,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BaseAuditPlanner",
    "DefaultAuditPlanner",
    "HealthCheckPlanner",
]