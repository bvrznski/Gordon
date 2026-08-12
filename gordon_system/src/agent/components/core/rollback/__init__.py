# Core Rollback Architecture
# ==========================

"""
Core rollback architecture for Phase 3.7.10.

Rollback restores a known prior operational state where exact restoration
is possible. This is different from compensation which attempts to counteract
effects where exact restoration is not possible.

Key principles:
    - ONE global rollback authority (RollbackCoordinator)
    - Rollback is dependency-ordered (reverse of successful execution)
    - Rollback completion requires independent verification
    - Unknown outcome cannot be treated as rollbackable
"""

from .coordinator import RollbackCoordinator, DefaultRollbackCoordinator
from .eligibility import (
    RollbackEligibility,
    RollbackEligibilityResult,
    RollbackEligibilityContext,
    RollbackMode,
    RollbackEligibilityEvaluator,
)
from .planner import RollbackPlanner, RollbackPlan
from .actions import (
    RollbackActionProtocol,
    RollbackStep,
    RollbackActionType,
    RollbackAction,
)

__all__ = [
    # Coordinators (canonical authority)
    "RollbackCoordinator",
    "DefaultRollbackCoordinator",
    
    # Eligibility evaluation
    "RollbackEligibilityEvaluator",
    "RollbackEligibilityResult",
    
    # Planning
    "RollbackPlanner",
    "RollbackPlan",
    
    # Actions and steps
    "RollbackActionProtocol",
    "RollbackStep",
]