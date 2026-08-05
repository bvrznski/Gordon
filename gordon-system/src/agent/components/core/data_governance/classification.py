# Classification Authority - Canonical Authority
# ==============================================

"""
Classification authority for information classification,
sensitivity level assignment, and evidence recording.

PHASE 3.7.21 REMEDIATION:
- Classification is part of the InformationRecord itself
- Authority validates and records classification decisions
- Records own their classification field
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .models import (
    ClassificationLevel,
    ClassificationEvidence,
    ClassificationDecision,
)


# =============================================================================
# Classification Rules Engine
# =============================================================================

class RuleResult(Enum):
    """Result of a classification rule evaluation."""
    MATCH = "match"
    NO_MATCH = "no_match"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class ClassificationRule:
    """
    A classification rule for evaluating information.
    
    Args:
        rule_id: Unique identifier
        name: Human-readable name
        pattern: Pattern to match (regex or simple string)
        level: Classification level if matched
        confidence: Confidence weight (0.0-1.0)
    """
    
    rule_id: str
    name: str
    pattern: str
    level: ClassificationLevel
    confidence: float = 1.0


class RulesEngine:
    """Evaluation engine for classification rules."""
    
    def __init__(self) -> None:
        self._rules: Dict[str, ClassificationRule] = {}
        self._lock = threading.RLock()
    
    def register_rule(self, rule: ClassificationRule) -> None:
        """Register a new classification rule."""
        with self._lock:
            self._rules[rule.rule_id] = rule
    
    def get_rule(self, rule_id: str) -> Optional[ClassificationRule]:
        """Get a registered rule by ID."""
        with self._lock:
            return self._rules.get(rule_id)
    
    def evaluate(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[ClassificationDecision]:
        """
        Evaluate rules against content and metadata.
        
        Args:
            content: Information content to classify
            metadata: Metadata dictionary
            
        Returns:
            List of classification decisions from matching rules
        """
        with self._lock:
            decisions: List[ClassificationDecision] = []
            
            for rule in self._rules.values():
                if rule.pattern.lower() in content.lower():
                    decision = ClassificationDecision(
                        information_id=metadata.get("information_id", "unknown"),
                        level=rule.level,
                        evidence=ClassificationEvidence(
                            classifier_id=rule.rule_id,
                            criteria=rule.pattern,
                            factors={"confidence": rule.confidence},
                            timestamp=time.time()
                        ),
                        assigned_by=rule.name
                    )
                    decisions.append(decision)
            
            return decisions


# =============================================================================
# Classification Authority - PHASE 3.7.21 REMEDIATION
# =============================================================================

class ClassificationAuthority:
    """
    Canonical authority for classification management.
    
    PHASE 3.7.21 REMEDIATION:
    - Records own their classification field (part of InformationRecord)
    - Authority validates and records classification decisions
    - Evidence is part of the decision, not managed separately
    
    Core Responsibilities:
    1. Classification rules management
    2. Decision recording and evidence preservation
    3. Classification lookup and verification
    4. Policy enforcement
    
    Non-Responsibilities (moved to record):
    - Storing classification on records (InformationRecord.classification)
    
    Usage:
        # Create authority
        authority = ClassificationAuthority()
        
        # Record a classification decision for provenance
        decision = await authority.record_classification(
            information_id="data-123",
            level=ClassificationLevel.CONFIDENTIAL,
            classifier_id="rule-based",
            confidence=0.95
        )
        
        # The record itself owns the classification field:
        record = InformationRecord(
            information_id="data-123",
            content_hash="hash123",
            owner=OwnerIdentity(...),
            classification=ClassificationLevel.CONFIDENTIAL,  # Record owns this
            lifecycle_state=LifecycleState.ACTIVE,
        )
    """
    
    def __init__(self) -> None:
        """Initialize the classification authority."""
        self._lock = threading.RLock()
        
        # Rules engine for evaluation
        self._rules_engine = RulesEngine()
        
        # Classification history by ID (for provenance)
        self._classifications: Dict[str, List[ClassificationDecision]] = {}
        
        # Statistics
        self._stats = {
            "total_classified": 0,
            "by_level": {level.value: 0 for level in ClassificationLevel},
        }
    
    def register_rule(self, rule: ClassificationRule) -> None:
        """Register a classification rule."""
        with self._lock:
            self._rules_engine.register_rule(rule)
    
    async def evaluate(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[ClassificationDecision]:
        """
        Evaluate rules against content and metadata.
        
        Args:
            content: Information content to classify
            metadata: Metadata dictionary
            
        Returns:
            List of classification decisions from matching rules
        """
        return self._rules_engine.evaluate(content, metadata)
    
    async def record_classification(
        self,
        information_id: str,
        level: ClassificationLevel,
        classifier_id: str = "system",
        confidence: float = 1.0,
        assigned_by: str = "system",
        criteria: str = "",
        factors: Optional[Dict[str, Any]] = None,
    ) -> ClassificationDecision:
        """
        Record a classification decision for provenance.
        
        PHASE 3.7.21: The record itself owns the classification field.
        This method only records the decision for audit/provenance.
        
        Args:
            information_id: ID of the classified information
            level: Assigned classification level
            classifier_id: Entity that made the classification
            confidence: Confidence level (0.0-1.0)
            assigned_by: Who/what performed the assignment
            criteria: Classification criteria applied
            factors: Additional factors for the decision
            
        Returns:
            ClassificationDecision recorded for provenance
        """
        with self._lock:
            evidence = ClassificationEvidence(
                classifier_id=classifier_id,
                criteria=criteria or f"assigned_by_{assigned_by}",
                factors=factors or {"confidence": confidence},
                timestamp=time.time(),
                confidence=confidence
            )
            
            decision = ClassificationDecision(
                information_id=information_id,
                level=level,
                evidence=evidence,
                assigned_by=assigned_by
            )
            
            # Store for provenance tracking
            if information_id not in self._classifications:
                self._classifications[information_id] = []
            self._classifications[information_id].append(decision)
            
            # Update stats
            self._stats["total_classified"] += 1
            self._stats["by_level"][level.value] += 1
            
            return decision
    
    async def get_classification(self, information_id: str) -> Optional[ClassificationDecision]:
        """
        Get the most recent classification decision for an item.
        
        Args:
            information_id: ID of the information
            
        Returns:
            Most recent classification decision, or None if not classified
        """
        with self._lock:
            decisions = self._classifications.get(information_id)
            if decisions:
                return decisions[-1]
            return None
    
    async def get_classification_history(self, information_id: str) -> List[ClassificationDecision]:
        """Get full classification history for an item."""
        with self._lock:
            return list(self._classifications.get(information_id, []))
    
    async def verify_classification(
        self,
        information_id: str,
        required_level: ClassificationLevel,
    ) -> bool:
        """
        Verify if information meets a minimum classification level.
        
        Args:
            information_id: ID of the information
            required_level: Minimum required classification level
            
        Returns:
            True if classified at or above the required level
        """
        decision = await self.get_classification(information_id)
        if decision is None:
            return False
        
        return decision.level.access_level >= required_level.access_level
    
    def get_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        with self._lock:
            return {
                "total_classified": self._stats["total_classified"],
                "by_level": dict(self._stats["by_level"]),
                "records_with_classification": len(self._classifications),
            }


__all__ = [
    "RuleResult",
    "ClassificationRule",
    "RulesEngine",
    "ClassificationAuthority",
]