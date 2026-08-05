# Environments Subpackage - Testing Infrastructure
# ==========================================

"""
Environments subpackage for test environment specifications.

This module provides:
- Environment specifications (LOCAL, ISOLATED, CONTAINER, CI, GPU)
- Environment reproducibility metadata
- Environment setup/cleanup utilities
"""

from .specifications import (
    TestEnvironment,
    TestEnvironmentConfig,
    EnvironmentType,
)
from .local import (
    LocalEnvironment,
)
from .isolated import (
    IsolatedEnvironment,
)
from .container import (
    ContainerEnvironment,
)
from .ci import (
    CIEnvironment,
)

__all__ = [
    # Specifications
    "TestEnvironment",
    "TestEnvironmentConfig",
    "EnvironmentType",
    
    # Environment types
    "LocalEnvironment",
    "IsolatedEnvironment",
    "ContainerEnvironment",
    "CIEnvironment",
]