# Data Subpackage - Testing Infrastructure
# ==========================================

"""
Data subpackage for test data generation and management.

This module provides:
- Synthetic data generators (deterministic, seed-reproducible)
- Production-derived data (sanitized, authorized)
- Golden files and snapshots
- Test corpus management
"""

from .generator import (
    TestDataGenerator,
    generate_synthetic_data,
)
from .golden import (
    GoldenData,
    verify_golden,
)
from .snapshots import (
    SnapshotTest,
    update_snapshot,
)

__all__ = [
    # Data generation
    "TestDataGenerator",
    "generate_synthetic_data",
    
    # Golden data
    "GoldenData",
    "verify_golden",
    
    # Snapshots
    "SnapshotTest",
    "update_snapshot",
]