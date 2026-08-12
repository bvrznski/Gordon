# Core Recovery Architecture (Phase 3.7.10)
# ===========================================

"""
Core recovery architecture for Phase 3.7.10.

Recovery restores an acceptable operational state when failures occur.
This may be:
    - Full operation (original functionality restored)
    - Degraded operation (reduced capability but functional)
    - Safe operation (no data loss, minimal impact)

Key principles:
    - ONE canonical recovery authority (RecoveryCoordinator)
    - Plans validated before execution
    - Independent verification required for success declaration
    - Recovery may involve rollback, restart, retry, etc.
"""

from .coordinator import RecoveryCoordinator, DefaultRecoveryCoordinator
from .eligibility import RecoveryEligibilityEvaluator, RecoveryEligibilityResult
from .planner import RecoveryPlanner, RecoveryPlan

__all__ = [
    # Canonical authority
    "RecoveryCoordinator",
    "DefaultRecoveryCoordinator",
    
    # Eligibility evaluation  
    "RecoveryEligibilityEvaluator",
    "RecoveryEligibilityResult",
    
    # Planning
    "RecoveryPlanner",
    "RecoveryPlan",
]