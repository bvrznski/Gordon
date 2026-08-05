# Privacy Controls - Data-Oriented Authority
# ===========================================

"""
Privacy controls for information privacy, personal data identification,
and access filtering.

PHASE 3.7.21 REMEDIATION:
- Privacy controls are DATA-ORIENTED, not managed by a central authority
- Redaction and filtering happen at point of use
- Records specify their privacy requirements, controls are applied locally
"""

import threading
import time
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from .models import (
    PrivacyLevel,
    PersonalDataIndicator,
    PrivacyPolicy,
    PrivacyDecision,
    ClassificationLevel,
)


# =============================================================================
# Personal Data Detector - LOCALIZED CONTROL
# =============================================================================

class PersonalDataType(Enum):
    """Types of personal data that trigger privacy controls."""
    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    SSN = "ssn"
    PASSPORT = "passport"
    FINANCIAL = "financial"
    HEALTH = "health"
    LOCATION = "location"
    BIOMETRIC = "biometric"


class PersonalDataDetector:
    """
    LOCALIZED personal data detection engine.
    
    PHASE 3.7.21 REMEDIATION: Detection happens at point of use,
    not centralized in a PrivacyManager.
    """
    
    PATTERNS: Dict[PersonalDataType, List[str]] = {
        PersonalDataType.NAME: [r"[A-Z][a-z]+ [A-Z][a-z]+"],
        PersonalDataType.EMAIL: [
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        ],
        PersonalDataType.PHONE: [r"\+?[0-9]{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"],
        PersonalDataType.ADDRESS: [
            r"\d+\s+[A-Za-z]+\s+(Street|St|Avenue|Av|Boulevard|Blvd|Road|Rd)",
            r"[A-Z]{2}\s+\d{5}"
        ],
        PersonalDataType.DATE_OF_BIRTH: [r"\d{4}-\d{2}-\d{2}"],
        PersonalDataType.SSN: [r"\d{3}-\d{2}-\d{4}"],
    }
    
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._compiled_patterns: Dict[PersonalDataType, re.Pattern] = {}
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns (lazy initialization)."""
        with self._lock:
            for ptype, patterns in self.PATTERNS.items():
                if ptype not in self._compiled_patterns:
                    self._compiled_patterns[ptype] = re.compile(patterns[0], re.IGNORECASE)
    
    def analyze(self, content: str) -> PersonalDataIndicator:
        """
        Analyze content for personal data.
        
        PHASE 3.7.21: This is LOCALIZED detection at point of use,
        NOT a centralized PrivacyManager function.
        
        Args:
            content: Content to analyze
            
        Returns:
            PersonalDataIndicator with detection results
        """
        self._compile_patterns()
        
        detected_types: List[str] = []
        
        for ptype, pattern in self._compiled_patterns.items():
            if pattern.search(content):
                detected_types.append(ptype.value)
        
        return PersonalDataIndicator(
            detected=len(detected_types) > 0,
            types=detected_types,
            confidence=1.0 if detected_types else 0.0,
            timestamp=time.time()
        )
    
    def redact(self, content: str, indicator: PersonalDataIndicator) -> str:
        """
        REDACT personal data from content.
        
        PHASE 3.7.21: Redaction is LOCALIZED at point of use,
        NOT managed by a central authority.
        
        Args:
            content: Original content
            indicator: Detection result
            
        Returns:
            Redacted content with placeholders
        """
        redacted = content
        
        for ptype_str in indicator.types:
            if ptype_str == PersonalDataType.EMAIL.value:
                redacted = re.sub(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                    "[EMAIL_REDACTED]",
                    redacted
                )
            elif ptype_str == PersonalDataType.PHONE.value:
                redacted = re.sub(
                    r"\+?[0-9]{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
                    "[PHONE_REDACTED]",
                    redacted
                )
            elif ptype_str == PersonalDataType.SSN.value:
                redacted = re.sub(
                    r"\d{3}-\d{2}-\d{4}",
                    "[SSN_REDACTED]",
                    redacted
                )
        
        return redacted


# =============================================================================
# Privacy Controls - Data-Oriented Authority (PHASE 3.7.21 REMEDIATION)
# =============================================================================

class PrivacyControls:
    """
    Data-oriented privacy controls for filtering and redaction.
    
    PHASE 3.7.21 REMEDIATION PRINCIPLES:
    1. Privacy controls remain DATA-ORIENTED
    2. Prefer REDACTION, FIELD FILTERING over global managers
    3. Privacy is a property of the data, not managed centrally
    
    Core Responsibilities (LOCALIZED):
    1. Personal data detection at point of use
    2. Field-level redaction and filtering
    3. Privacy indicator recording for audit
    
    Non-Responsibilities (moved to record types):
    - Central privacy policy management (policies embedded in records)
    - Global privacy enforcement (applied locally where data is used)
    
    Usage:
        # Create controls instance
        privacy = PrivacyControls()
        
        # Detect personal data at point of use
        content = "Contact John Doe at john@example.com"
        indicator = privacy.detect(content)
        
        # Redact if needed
        if indicator.detected:
            safe_content = privacy.redact(content, indicator)
        
        # Or apply field-level filtering on a record
        filtered_record = privacy.filter_fields(record, allowed_fields=["name"])
    """
    
    def __init__(self) -> None:
        """Initialize privacy controls."""
        self._lock = threading.RLock()
        self._detector = PersonalDataDetector()
        
        # Privacy policy history (for audit/provenance)
        self._policies: Dict[str, List[PrivacyPolicy]] = {}
        
        # Statistics
        self._stats = {
            "total_analyzed": 0,
            "with_personal_data": 0,
        }
    
    def detect(self, content: str) -> PersonalDataIndicator:
        """
        Detect personal data in content.
        
        PHASE 3.7.21: This is LOCALIZED detection at point of use.
        
        Args:
            content: Content to analyze
            
        Returns:
            PersonalDataIndicator with detection results
        """
        indicator = self._detector.analyze(content)
        
        with self._lock:
            self._stats["total_analyzed"] += 1
            if indicator.detected:
                self._stats["with_personal_data"] += 1
        
        return indicator
    
    def redact(self, content: str, indicator: Optional[PersonalDataIndicator] = None) -> str:
        """
        REDACT personal data from content.
        
        PHASE 3.7.21: Redaction is LOCALIZED at point of use.
        
        Args:
            content: Original content
            indicator: Detection result (auto-detects if not provided)
            
        Returns:
            Redacted content with placeholders
        """
        if indicator is None:
            indicator = self.detect(content)
        
        return self._detector.redact(content, indicator)
    
    def filter_fields(self, data: Dict[str, Any], allowed_fields: Set[str]) -> Dict[str, Any]:
        """
        FILTER data to only include allowed fields.
        
        PHASE 3.7.21: Field-level filtering is LOCALIZED at point of use.
        
        Args:
            data: Original data dictionary
            allowed_fields: Set of field names to keep
            
        Returns:
            Filtered dictionary with only allowed fields
        """
        return {k: v for k, v in data.items() if k in allowed_fields}
    
    def sanitize(self, content: str) -> str:
        """
        SANITIZE content by removing personal data.
        
        PHASE 3.7.21: Sanitization is LOCALIZED at point of use.
        
        Args:
            content: Content to sanitize
            
        Returns:
            Sanitized content with personal data redacted
        """
        indicator = self.detect(content)
        return self.redact(content, indicator)
    
    def record_policy(
        self,
        information_id: str,
        policy: PrivacyPolicy,
    ) -> None:
        """
        Record a privacy policy for provenance.
        
        PHASE 3.7.21: The record itself owns its privacy requirements.
        This method only records the policy for audit/provenance.
        
        Args:
            information_id: ID of the information
            policy: Privacy policy to record
        """
        with self._lock:
            if information_id not in self._policies:
                self._policies[information_id] = []
            self._policies[information_id].append(policy)
    
    def get_policy(self, information_id: str) -> Optional[PrivacyPolicy]:
        """Get the most recent policy for an item."""
        with self._lock:
            policies = self._policies.get(information_id)
            if policies:
                return policies[-1]
            return None
    
    def check_compliance(
        self,
        content: str,
        required_level: PrivacyLevel,
    ) -> bool:
        """
        Check if content meets privacy requirements.
        
        PHASE 3.7.21: Compliance is checked LOCALIZED at point of use.
        
        Args:
            content: Content to check
            required_level: Minimum required privacy level
            
        Returns:
            True if compliant (or if no personal data detected)
        """
        indicator = self.detect(content)
        
        # If no personal data, always compliant
        if not indicator.detected:
            return True
        
        # Personal data detected - need more restrictive policy
        # For simplicity: if personal data exists, check for PERSONAL_DATA level
        return required_level in (PrivacyLevel.PERSONAL_DATA,)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get privacy statistics."""
        with self._lock:
            return {
                "total_analyzed": self._stats["total_analyzed"],
                "with_personal_data": self._stats["with_personal_data"],
                "records_with_policy": len(self._policies),
            }


__all__ = [
    "PersonalDataType",
    "PersonalDataDetector",
    "PrivacyControls",
]