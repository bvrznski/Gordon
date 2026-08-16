# Phase metadata for Prediction Error Processing Engine
# ======================================================
"""
PHASE 4.9.3 METADATA
--------------------
This module contains version and phase information for the
Prediction Error Processing Engine.
"""

__version__: str = "4.9.3"
__phase_name__: str = "prediction_error_processing"
__phase_number__: str = "4.9.3"

# Phase status: complete, draft, blocked, incomplete
__status__: str = "draft"

# Dependencies (other phases this phase depends on)
__dependencies__: tuple[str, ...] = (
    "4.9.1",  # Prediction Generation
    "4.9.2",  # Error Representation
)

# Depended upon by (phases that depend on this one)
__dependents__: tuple[str, ...] = (
    "4.9.4",  # Precision Estimation
)