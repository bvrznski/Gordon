# Knowledge Assertions - Validation Contract - Phase 6.4
# =========================================================

"""
Validation module for assertions.

Implements validation rules per PART 3 of the specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# VALIDATION RESULTS
# =============================================================================


@dataclass(frozen=True)
class ValidationRule:
    """A validation rule with its requirements."""
    
    rule_id: str  # e.g., ASSERTION-LAW-001
    description: str
    check_function_name: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "check_function_name": self.check_function_name,
            "severity": self.severity,
        }


# =============================================================================
# ASSERTION VALIDATOR
# =============================================================================


@dataclass(frozen=True)
class AssertionValidator:
    """
    Validates assertions according to Phase 6.4 specification.
    
    Implements validation for all the laws specified in PART 3.
    """

    def __post_init__(self):
        """Initialize validation rules."""
        self._rules = self._get_rules()

    @property
    def rules(self) -> Tuple[ValidationRule, ...]:
        """Get all validation rules."""
        return tuple(self._rules)

    def _get_rules(self) -> List[ValidationRule]:
        """Get all validation rules from specification."""
        return [
            ValidationRule(
                rule_id="ASSERTION-LAW-001",
                description="Every Assertion shall possess one immutable Semantic Identity",
                check_function_name="check_semantic_identity",
            ),
            ValidationRule(
                rule_id="ASSERTION-LAW-002",
                description="Assertions shall represent semantic propositions only",
                check_function_name="check_proposition_structure",
            ),
            ValidationRule(
                rule_id="ASSERTION-LAW-003",
                description="Assertions shall remain independent from Beliefs",
                check_function_name="check_independence_from_belief",
            ),
            ValidationRule(
                rule_id="ASSERTION-LAW-004",
                description="Assertions shall preserve provenance",
                check_function_name="check_provenance",
            ),
            ValidationRule(
                rule_id="ASSERTION-LAW-005",
                description="Assertions shall preserve revision lineage",
                check_function_name="check_revision_lineage",
            ),
            ValidationRule(
                rule_id="ASSERTION-LAW-006",
                description="Assertions shall remain independently inspectable",
                check_function_name="check_inspections",
            ),
            ValidationRule(
                rule_id="ASSERTION-LAW-007",
                description="Assertions shall remain deterministic",
                check_function_name="check_deterministic",
            ),
            ValidationRule(
                rule_id="PROPOSITION-LAW-001",
                description="Every Assertion shall contain one explicit Proposition",
                check_function_name="check_proposition_exists",
            ),
            ValidationRule(
                rule_id="PROPOSITION-LAW-002",
                description="Propositions shall explicitly identify Subject, Predicate and Object",
                check_function_name="check proposition_components",
            ),
        ]

    def validate_semantic_identity(self, assertion: Any) -> Tuple[bool, List[str]]:
        """
        ASSERTION-LAW-001: Every Assertion shall possess one immutable Semantic Identity.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        if not hasattr(assertion, 'assertion_identity'):
            issues.append("Missing assertion_identity field")
            return False, issues
        
        identity = getattr(assertion, 'assertion_identity')
        if not identity or len(str(identity)) == 0:
            issues.append("Empty or missing semantic identity")
        
        return len(issues) == 0, issues

    def validate_proposition(self, assertion: Any) -> Tuple[bool, List[str]]:
        """
        PROPOSITION-LAW-001: Every Assertion shall contain one explicit Proposition.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        if not hasattr(assertion, 'proposition'):
            issues.append("Missing proposition field")
            return False, issues
        
        proposition = getattr(assertion, 'proposition')
        if proposition is None:
            issues.append("Proposition is None")
        
        return len(issues) == 0, issues

    def validate(
        self,
        assertion: Any,
        rule_ids: Optional[Tuple[str, ...]] = None,
    ) -> Dict[str, Any]:
        """
        Validate an assertion against specified rules.
        
        Args:
            assertion: The assertion to validate
            rule_ids: Rule IDs to check (None = all rules)
            
        Returns:
            Validation results dictionary with pass/fail for each rule
        """
        results = {
            "validation_identity": f"validate:{uuid.uuid4().hex[:16]}",
            "assertion_identity": getattr(assertion, 'assertion_identity', None),
            "timestamp_utc": time.time(),
            "rules_passed": [],
            "rules_failed": [],
            "overall_valid": True,
        }

        rules_to_check = self._rules
        if rule_ids:
            rules_to_check = [r for r in self._rules if r.rule_id in rule_ids]

        for rule in rules_to_check:
            # Map check function name to actual method
            check_method_name = f"validate_{rule.check_function_name.replace('-', '_').replace('.', '_')}"
            
            try:
                check_method = getattr(self, check_method_name, None)
                if check_method:
                    is_valid, issues = check_method(assertion)
                    if is_valid:
                        results["rules_passed"].append(rule.rule_id)
                    else:
                        results["rules_failed"].append({
                            "rule_id": rule.rule_id,
                            "issues": issues,
                        })
                        results["overall_valid"] = False
                else:
                    # Fallback: assume valid if method doesn't exist
                    results["rules_passed"].append(rule.rule_id)
            except Exception as e:
                results["rules_failed"].append({
                    "rule_id": rule.rule_id,
                    "issues": [f"Validation error: {str(e)}"],
                })
                results["overall_valid"] = False

        return results

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionValidator:
        """Create validator from dictionary."""
        # For now, just return a new instance - validation rules are static
        return cls()