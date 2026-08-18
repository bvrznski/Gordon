# Optimization Management - Phase 7.46
# =====================================

"""
Canonical optimization management for mathematical reasoning.

Optimization evaluates:
    - global optimum
    - local optimum
    - objective value
    - Pareto optimality
    - convergence
    - computational complexity

Optimization remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class OptimizationAnalysis:
    """
    Analysis of an optimization problem.
    
    An optimization analysis includes solution identification,
    convergence metrics, and optimality verification.
    """
    
    analysis_id: str                    # Unique identifier
    
    # Results
    objective_value: float              # Optimal value achieved
    is_global_optimum: bool             # Is this the global optimum?
    optimal_solution: Dict[str, Any]    # Solution variable values
    
    # Convergence
    convergence_status: str = "converged"  # converged, max_iterations, timeout, etc.
    iterations: int = 0                    # Number of iterations performed
    convergence_rate: Optional[float] = None
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    solve_time_seconds: Optional[float] = None
    
    @property
    def is_failed(self) -> bool:
        """Check if optimization failed."""
        return self.convergence_status in ("failed", "infeasible")
    
    @classmethod
    def create(
        cls,
        objective_value: float,
        optimal_solution: Dict[str, Any],
        is_global_optimum: bool = True,
        convergence_status: str = "converged",
        iterations: int = 0,
        solve_time_seconds: Optional[float] = None,
    ) -> OptimizationAnalysis:
        """Create a new optimization analysis."""
        return cls(
            analysis_id=f"optimization_analysis:{uuid.uuid4().hex[:16]}",
            objective_value=objective_value,
            optimal_solution=dict(optimal_solution),
            is_global_optimum=is_global_optimum,
            convergence_status=convergence_status,
            iterations=iterations,
            solve_time_seconds=solve_time_seconds,
        )


@dataclass(frozen=True)
class OptimizationProblem:
    """
    Complete optimization problem definition.
    
    Contains objective function, constraints, and solution space definition.
    """
    
    problem_id: str                     # Unique identifier
    name: str                           # Human-readable name
    
    # Components
    objective_function: str             # Expression to minimize/maximize
    constraints: List[str] = field(default_factory=list)
    variables: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)
    
    # Configuration
    optimization_type: str = "minimize"
    is_convex: bool = False
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        name: str,
        objective_function: str,
        optimization_type: str = "minimize",
        constraints: Optional[List[str]] = None,
        variables: Optional[Dict[str, Tuple[Any, Any]]] = None,
    ) -> OptimizationProblem:
        """Create a new optimization problem."""
        return cls(
            problem_id=f"optimization_problem:{uuid.uuid4().hex[:16]}",
            name=name,
            objective_function=objective_function,
            optimization_type=optimization_type,
            constraints=constraints or [],
            variables=variables or {},
        )


@dataclass(frozen=True)
class ObjectiveValue:
    """
    A measured or computed objective value.
    
    Tracks both the value and its confidence/quality metrics.
    """
    
    value_id: str                       # Unique identifier
    value: float                        # Objective function value
    quality_score: float = 1.0          # Quality metric (0-1)
    is_feasible: bool = True            # Is this solution feasible?
    
    @classmethod
    def create(cls, value: float) -> ObjectiveValue:
        """Create a new objective value."""
        return cls(
            value_id=f"objective_value:{uuid.uuid4().hex[:16]}",
            value=value,
        )


@dataclass(frozen=True)
class OptimalSolution:
    """
    A complete optimal solution.
    
    Contains the variable values that achieve the optimum.
    """
    
    solution_id: str                    # Unique identifier
    problem_id: str                     # ID of solved problem
    
    # Solution values
    variable_values: Dict[str, Any]     # Variable name -> value
    
    # Quality metrics
    objective_value: float              # Achieved objective value
    is_global_optimum: bool = True      # Confirmed global optimum?
    
    @classmethod
    def create(
        cls,
        problem_id: str,
        variable_values: Dict[str, Any],
        objective_value: float,
        is_global_optimum: bool = True,
    ) -> OptimalSolution:
        """Create a new optimal solution."""
        return cls(
            solution_id=f"optimal_solution:{uuid.uuid4().hex[:16]}",
            problem_id=problem_id,
            variable_values=dict(variable_values),
            objective_value=objective_value,
            is_global_optimum=is_global_optimum,
        )


@dataclass(frozen=True)
class ConvergenceMetrics:
    """
    Metrics tracking convergence behavior.
    
    Used to analyze and verify optimization algorithm convergence.
    """
    
    metrics_id: str                     # Unique identifier
    
    # Tracking
    iteration_count: int = 0            # Total iterations
    objective_history: List[float] = field(default_factory=list)
    parameter_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics
    final_convergence_rate: Optional[float] = None
    is_converged: bool = False          # Did algorithm converge?
    
    @classmethod
    def create(cls) -> ConvergenceMetrics:
        """Create new convergence metrics."""
        return cls(
            metrics_id=f"convergence_metrics:{uuid.uuid4().hex[:16]}",
        )


__all__ = [
    "OptimizationAnalysis",
    "OptimizationProblem",
    "ObjectiveValue",
    "OptimalSolution",
    "ConvergenceMetrics",
]