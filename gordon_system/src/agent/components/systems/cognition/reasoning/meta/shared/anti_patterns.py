# Meta-Reasoning Anti-Patterns - Phase 7.27 Part 3
# ================================================

"""
Architectural anti-patterns that should be REJECTED in Meta-Reasoning implementations.

This module identifies and provides detection for anti-patterns specified in
Part 3 of Phase 7.27.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AntiPatternCategory(Enum):
    """Categories of anti-patterns to detect."""
    
    STRATEGY = "strategy"               # Strategy selection issues
    COORDINATION = "coordination"       # Coordination topology issues
    ESCALATION = "escalation"           # Escalation justification issues  
    TERMINATION = "termination"         # Premature termination issues
    VALIDATION = "validation"           # Validation bypass issues
    GOVERNANCE = "governance"           # Governance bypass issues


class AntiPatternSeverity(Enum):
    """Severity levels for detected anti-patterns."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class DetectedAntiPattern:
    """
    A detected architectural anti-pattern in meta-reasoning.
    
    Anti-patterns are REJECTED implementations per Part 3 specifications.
    """
    
    # Identity
    pattern_id: str                       # Unique identifier
    timestamp_utc: float                  # When detected
    
    # Classification
    category: AntiPatternCategory         # Which category?
    anti_pattern_type: str                # Specific type name
    
    # Description
    description: str                      # What's wrong?
    evidence: str                         # Supporting evidence
    
    # Severity
    severity: AntiPatternSeverity = AntiPatternSeverity.WARNING
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Execution context
    
    @classmethod
    def create(
        cls,
        category: AntiPatternCategory,
        anti_pattern_type: str,
        description: str,
        evidence: str,
        severity: AntiPatternSeverity = AntiPatternSeverity.WARNING,
        context: Optional[Dict[str, Any]] = None,
    ) -> DetectedAntiPattern:
        """Create a new detected anti-pattern."""
        return cls(
            pattern_id=f"anti_pattern:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            category=category,
            anti_pattern_type=anti_pattern_type,
            description=description,
            evidence=evidence,
            severity=severity,
            context=context or {},
        )


# ============================================================================
# ANTI-PATTERN DEFINITIONS (from Part 3 Architectural Anti-Patterns section)
# ============================================================================


def detect_implicit_strategy_selection(
    selected_strategies: List[str],
    justification: Optional[Dict[str, Any]] = None,
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Selecting reasoning strategies without explicit justification.
    
    Part 3 specifies: "Strategies shall never be selected without explicit
    justification."
    """
    if not selected_strategies:
        return None
    
    if justification is None or not any(
        key in justification for key in 
        ["rationale", "evidence", "justification", "selection_policy"]
    ):
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.STRATEGY,
            anti_pattern_type="implicit_strategy_selection",
            description="Reasoning strategy selected without explicit justification",
            evidence=f"Selected strategies: {selected_strategies}, no justification provided",
            severity=AntiPatternSeverity.ERROR,
        )
    return None


def detect_hidden_coordination_dependencies(
    coordination: Dict[str, List[str]],
    dependencies: Dict[str, List[str]],
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Coordinating reasoning through hidden dependencies.
    
    Part 3 specifies: "Coordination shall never introduce hidden reasoning
    dependencies."
    """
    if not coordination:
        return None
    
    # Check for circular dependencies (hidden or explicit)
    visited = set()
    recursion_stack = set()
    
    def has_cycle(node: str) -> bool:
        visited.add(node)
        recursion_stack.add(node)
        
        for neighbor in dependencies.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True
                
        recursion_stack.remove(node)
        return False
    
    for node in coordination.keys():
        if node not in visited:
            if has_cycle(node):
                return DetectedAntiPattern.create(
                    category=AntiPatternCategory.COORDINATION,
                    anti_pattern_type="hidden_dependency_cycle",
                    description="Hidden dependency cycle detected in reasoning coordination",
                    evidence=f"Circular dependencies found involving: {node}",
                    severity=AntiPatternSeverity.ERROR,
                    context={"nodes": list(coordination.keys())},
                )
    
    return None


def detect_unjustified_escalation(
    escalation_trigger: str,
    justification: Optional[Dict[str, Any]] = None,
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Escalating reasoning without explicit justification.
    
    Part 3 specifies: "Escalation shall never allocate additional reasoning
    resources without explicit policy authorization."
    """
    if not justification:
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.ESCALATION,
            anti_pattern_type="unjustified_escalation",
            description=f"Escalation triggered by '{escalation_trigger}' without policy authorization",
            evidence="No escalation policy or justification provided",
            severity=AntiPatternSeverity.ERROR,
        )
    
    return None


def detect_arbitrary_termination(
    termination_conditions: List[str],
    confidence_threshold: Optional[float] = None,
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Terminating reasoning arbitrarily.
    
    Part 3 specifies: "Reasoning shall never terminate without satisfying an
    explicit stopping policy."
    """
    if not termination_conditions:
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.TERMINATION,
            anti_pattern_type="arbitrary_termination",
            description="Termination without any conditions specified",
            evidence="No termination conditions or stopping policy defined",
            severity=AntiPatternSeverity.ERROR,
        )
    
    # Check if confidence threshold is properly set
    if confidence_threshold is None and "confidence_threshold" not in str(termination_conditions):
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.TERMINATION,
            anti_pattern_type="insufficient_termination_policy",
            description="Termination lacks proper stopping policy",
            evidence=f"Conditions: {termination_conditions}, no confidence threshold defined",
            severity=AntiPatternSeverity.WARNING,
        )
    
    return None


def detect_validation_bypass(
    validation_passed: bool,
    validation_findings: List[str],
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Validation that mutates meta-reasoning artifacts.
    
    Part 3 specifies: "Validation shall never modify meta-reasoning artifacts
    directly."
    """
    if not validation_passed and len(validation_findings) == 0:
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.VALIDATION,
            anti_pattern_type="silent_validation_failure",
            description="Validation failed without proper findings recorded",
            evidence="Validation returned False but no findings were captured",
            severity=AntiPatternSeverity.ERROR,
        )
    
    if validation_passed and "FAILED" in str(validation_findings):
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.VALIDATION,
            anti_pattern_type="false_positive_validation",
            description="Validation passed but failure indicators found",
            evidence=f"Passed with findings: {validation_findings}",
            severity=AntiPatternSeverity.WARNING,
        )
    
    return None


def detect_governance_bypass(
    governance_evaluated: bool,
    violations_found: List[str],
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Governance that mutates meta-reasoning artifacts.
    
    Part 3 specifies: "Governance shall never modify meta-reasoning artifacts
    directly."
    """
    if not governance_evaluated and len(violations_found) > 0:
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.GOVERNANCE,
            anti_pattern_type="unobserved_governance_violation",
            description="Governance violations found but not observed",
            evidence=f"Violations: {violations_found}",
            severity=AntiPatternSeverity.ERROR,
        )
    
    return None


def detect_provenance_loss(
    provenance_chain: List[str],
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Losing provenance in meta-reasoning.
    
    Part 3 specifies: "Provenance must remain complete."
    """
    if not provenance_chain or len(provenance_chain) == 0:
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.COORDINATION,
            anti_pattern_type="missing_provenance",
            description="No provenance chain maintained for meta-reasoning session",
            evidence="Provenance list is empty or not tracked",
            severity=AntiPatternSeverity.ERROR,
        )
    
    return None


def detect_deterministic_violation(
    input_state_1: Dict[str, Any],
    input_state_2: Dict[str, Any],
    output_1: Dict[str, Any],
    output_2: Dict[str, Any],
) -> Optional[DetectedAntiPattern]:
    """
    Reject: Non-deterministic meta-reasoning given identical inputs.
    
    Part 3 specifies: "Meta-Reasoning shall remain deterministic given
    identical reasoning histories, resource constraints and governance policies."
    """
    if input_state_1 == input_state_2 and output_1 != output_2:
        return DetectedAntiPattern.create(
            category=AntiPatternCategory.COORDINATION,
            anti_pattern_type="non_deterministic_behavior",
            description="Meta-reasoning produces different outputs for identical inputs",
            evidence=f"Input states equal but outputs differ: {output_1} vs {output_2}",
            severity=AntiPatternSeverity.ERROR,
        )
    return None


# ============================================================================
# DETECTION ENGINE
# ============================================================================


@dataclass(frozen=True)
class AntiPatternDetector:
    """
    Engine for detecting architectural anti-patterns in meta-reasoning.
    
    Provides comprehensive detection across all specified categories.
    """
    
    # Detection results
    detected_patterns: List[DetectedAntiPattern] = field(default_factory=list)
    
    def add_detection(self, pattern: DetectedAntiPattern) -> None:
        """Add a detected anti-pattern to the collection."""
        self.detected_patterns.append(pattern)
    
    def get_all_patterns(self) -> List[DetectedAntiPattern]:
        """Get all detected patterns."""
        return list(self.detected_patterns)
    
    def get_error_patterns(self) -> List[DetectedAntiPattern]:
        """Get only ERROR severity patterns."""
        return [p for p in self.detected_patterns if p.severity == AntiPatternSeverity.ERROR]
    
    def has_critical_failures(self) -> bool:
        """Check if any critical failures detected."""
        return len(self.get_error_patterns()) > 0
    
    def to_report(self) -> Dict[str, Any]:
        """Generate a report of all detections."""
        return {
            "total_detections": len(self.detected_patterns),
            "error_count": len(self.get_error_patterns()),
            "warning_count": len([p for p in self.detected_patterns if p.severity == AntiPatternSeverity.WARNING]),
            "info_count": len([p for p in self.detected_patterns if p.severity == AntiPatternSeverity.INFO]),
            "patterns_by_category": {
                cat.value: [p for p in self.detected_patterns if p.category == cat]
                for cat in AntiPatternCategory
            },
        }


__all__ = [
    "AntiPatternDetector",
    "DetectedAntiPattern",
    "AntiPatternCategory",
    "AntiPatternSeverity",
    # Detection functions
    "detect_implicit_strategy_selection",
    "detect_hidden_coordination_dependencies",
    "detect_unjustified_escalation", 
    "detect_arbitrary_termination",
    "detect_validation_bypass",
    "detect_governance_bypass",
    "detect_provenance_loss",
    "detect_deterministic_violation",
]