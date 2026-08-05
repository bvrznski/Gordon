# Requirements Verification - Testing Infrastructure
# ==========================================

"""
RequirementVerifier: Verifies requirements are met through tests.

This module provides:
- Requirements traceability (linking tests to requirements)
- Requirement coverage analysis
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid


@dataclass(frozen=True)
class TraceabilityLink:
    """Immutable link between a requirement and evidence."""
    
    requirement_id: str
    test_id: str
    evidence_type: str  # unit_test, contract_test, system_test, etc.
    verification_status: str = "pending"  # pending, verified, failed
    
    def to_dict(self) -> Dict:
        return {
            "requirement_id": self.requirement_id,
            "test_id": self.test_id,
            "evidence_type": self.evidence_type,
            "verification_status": self.verification_status,
        }


@dataclass(frozen=True)
class RequirementVerificationResult:
    """Immutable result of requirement verification."""
    
    requirement_id: str
    is_met: bool
    linked_tests: List[TraceabilityLink]
    coverage_percentage: float = 0.0
    
    @property
    def has_test_coverage(self) -> bool:
        return len(self.linked_tests) > 0


class RequirementVerifier:
    """
    Verifies requirements through test evidence and traceability.
    
    This verifier:
    - Links tests to requirements via traceability matrix
    - Calculates requirement coverage from test results
    - Identifies untested requirements
    """
    
    def __init__(self):
        """Initialize the requirement verifier."""
        self._links: Dict[str, List[TraceabilityLink]] = {}  # req_id -> links
        self._test_results: Dict[str, str] = {}  # test_id -> status
    
    def add_traceability_link(
        self,
        requirement_id: str,
        test_id: str,
        evidence_type: str,
    ) -> None:
        """
        Add a traceability link between requirement and test.
        
        Args:
            requirement_id: ID of the requirement
            test_id: ID of the test
            evidence_type: Type of evidence (unit_test, contract_test, etc.)
        """
        if requirement_id not in self._links:
            self._links[requirement_id] = []
        
        link = TraceabilityLink(
            requirement_id=requirement_id,
            test_id=test_id,
            evidence_type=evidence_type,
        )
        self._links[requirement_id].append(link)
    
    def record_test_result(self, test_id: str, status: str) -> None:
        """
        Record the result of a test.
        
        Args:
            test_id: ID of the test
            status: Result status (passed, failed, skipped, etc.)
        """
        self._test_results[test_id] = status
    
    def verify_requirement(self, requirement_id: str) -> RequirementVerificationResult:
        """
        Verify a single requirement.
        
        Args:
            requirement_id: ID of the requirement
            
        Returns:
            RequirementVerificationResult with verification status
        """
        links = self._links.get(requirement_id, [])
        
        if not links:
            return RequirementVerificationResult(
                requirement_id=requirement_id,
                is_met=False,
                linked_tests=[],
                coverage_percentage=0.0,
            )
        
        # Check if at least one linked test passed
        met = False
        for link in links:
            status = self._test_results.get(link.test_id, "pending")
            
            if status == "passed":
                met = True
                break
        
        return RequirementVerificationResult(
            requirement_id=requirement_id,
            is_met=met,
            linked_tests=links,
            coverage_percentage=len(links) / max(1, len(self._links)),
        )
    
    def verify_all_requirements(self, requirement_ids: List[str]) -> Dict[str, RequirementVerificationResult]:
        """
        Verify multiple requirements.
        
        Args:
            requirement_ids: List of requirement IDs
            
        Returns:
            Dictionary mapping requirement_id to verification result
        """
        results = {}
        
        for req_id in requirement_ids:
            results[req_id] = self.verify_requirement(req_id)
        
        return results
    
    def get_missing_coverage(self, requirement_ids: List[str]) -> List[str]:
        """
        Get list of requirements without test coverage.
        
        Args:
            requirement_ids: List of requirement IDs
            
        Returns:
            List of requirement IDs with no test links
        """
        return [
            req_id for req_id in requirement_ids
            if req_id not in self._links or len(self._links[req_id]) == 0
        ]
    
    def get_coverage_matrix(self) -> List[TraceabilityLink]:
        """Get all traceability links."""
        matrix = []
        for links in self._links.values():
            matrix.extend(links)
        return matrix


def trace_requirement(
    requirement_id: str,
    test_id: str,
    verifier: Optional[RequirementVerifier] = None,
) -> None:
    """
    Trace a requirement to a test.
    
    Args:
        requirement_id: ID of the requirement
        test_id: ID of the test
        verifier: RequirementVerifier instance (creates new if None)
    """
    v = verifier or RequirementVerifier()
    v.add_traceability_link(requirement_id, test_id, "unit_test")


def verify_requirements(
    requirement_ids: List[str],
) -> Dict[str, RequirementVerificationResult]:
    """
    Verify a list of requirements.
    
    Args:
        requirement_ids: List of requirement IDs
        
    Returns:
        Dictionary mapping requirement_id to verification result
    """
    verifier = RequirementVerifier()
    return verifier.verify_all_requirements(requirement_ids)