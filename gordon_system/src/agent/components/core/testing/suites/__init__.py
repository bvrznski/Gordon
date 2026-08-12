# Suites Subpackage - Testing Infrastructure
# ==========================================

"""
Suites subpackage for test suite definitions and management.

This module provides:
- TestSuite: Aggregated tests with shared configuration
- Suite selection policies (all, changed_files, risk_based)
- Suite composition utilities
"""

from .definitions import (
    TestSuite,
    SuiteDefinition,
    SuiteSelectionPolicy,
)
from .selection import (
    select_suites,
    select_tests_by_change,
)

__all__ = [
    # Definitions
    "TestSuite",
    "SuiteDefinition",
    "SuiteSelectionPolicy",
    
    # Selection
    "select_suites",
    "select_tests_by_change",
]