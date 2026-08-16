# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Cognitive Coordination Observatory (CCO)
======================================

The Cognitive Coordination Observatory provides continuous meta-observation
of the entire cognitive architecture without participating in cognition.

This module implements:

* Observation models and metrics
* Health indicators and evaluation
* Diagnostic findings
* Anomaly detection
* Trend analysis
* Optimization recommendations

ARCHITECTURAL PRINCIPLES
------------------------

1. OBSERVATION IS PASSIVE
   The Observatory observes but never intervenes.
   
2. METRICS ARE EVIDENCE-BASED
   All measurements derive from concrete observations.
   
3. HEALTH DERIVES FROM INDICATORS
   Health assessments come from measurable indicators.
   
4. DIAGNOSTICS PRESERVE CAUTION
   Diagnostics distinguish evidence from hypotheses.
   
5. RECOMMENDATIONS ARE ADVISORY
   Recommendations remain suggestions, never automatic actions.

OBSERVATORY LAYERS
------------------

1. Core Models (observation.py, metric.py)
   Fundamental data structures for observations and metrics.
   
2. Evaluation Layer (health.py, diagnostic.py)
   Evaluate architecture state and produce findings.
   
3. Detection Layer (anomaly.py, bottleneck.py, trend.py)
   Detect patterns, anomalies, and trends.
   
4. Recommendation Layer (optimization.py)
   Generate optimization recommendations.
   
5. Query Layer (query.py)
   Interface for requesting observations.

ARCHITECTURAL INTEGRATION
-------------------------

The Observatory integrates with:

* COE (Cognitive Orchestration Engine): Evaluates orchestration quality
* CCP (Coordination Protocol): Analyzes communication patterns  
* GCG (Global Coordination Graph): Observes graph evolution
* CEM (Cognitive Event Model): Consumes events for observation

CRITICAL BOUNDARY
-----------------

The Observatory NEVER:

* Modifies cognitive state
* Executes recommendations automatically
* Creates or modifies events
* Alters the coordination graph
* Makes architectural decisions

The Observatory only: OBSERVE, MEASURE, EXPLAIN, RECOMMEND.
"""

from __future__ import annotations

# Core models
from .observation import Observation, ObservationKind, ObservationWindow
from .metric import ObservatoryMetric, MetricHistory
from .observation import ObservationRequest, ObservationResult
from .session import ObservationSession

# Evaluation
from .health import HealthIndicator, HealthReport, HealthDimension
from .diagnostic import DiagnosticFinding, DiagnosticReport

# Detection
from .bottleneck import Bottleneck, BottleneckReport
from .anomaly import Anomaly, AnomalyReport
from .trend import Trend, TrendDirection, TrendReport

# Recommendation
from .optimization import OptimizationRecommendation, OptimizationReport

# Query interface
from .query import ObservatoryQuery, QueryType

# Validation
from .validation import validate_observation, validate_metric, validate_health

__all__ = [
    # Core models
    "Observation",
    "ObservationKind",
    "ObservatoryMetric",
    "MetricHistory",
    "ObservationRequest",
    "ObservationResult",
    "ObservationSession",
    
    # Evaluation
    "HealthIndicator",
    "HealthReport",
    "HealthDimension",
    "DiagnosticFinding",
    "DiagnosticReport",
    
    # Detection
    "Bottleneck",
    "BottleneckReport",
    "Anomaly",
    "AnomalyReport",
    "Trend",
    "TrendDirection",
    "TrendReport",
    
    # Recommendation
    "OptimizationRecommendation",
    "OptimizationReport",
    
    # Query interface
    "ObservatoryQuery",
    "QueryType",
    
    # Validation
    "validate_observation",
    "validate_metric",
    "validate_health",
]

__version__ = "4.11.8"