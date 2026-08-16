# Modality Precision Estimators - Phase 4.9.4
# =============================================

"""
Modality-specific precision estimation models.

Provides reliability estimates for different sensory and cognitive modalities:
    * Vision
    * Audio  
    * Language
    * Memory
    * Latent representations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# MODALITY PRECISION ESTIMATOR
# =============================================================================


@dataclass(frozen=True)
class ModalityPrecisionEstimator:
    """
    Estimator for modality-specific precision.
    
    Each modality (vision, audio, language, memory, latent) has its own
    reliability characteristics that are estimated independently.
    """
    
    def estimate_vision_precision(self, vision_data: dict[str, Any]) -> float:
        """
        Estimate precision for visual data.
        
        Args:
            vision_data: Visual modality data
            
        Returns:
            Vision precision in [0.0, 1.0]
        """
        # Base confidence from available visual quality indicators
        base_confidence = 0.5
        
        if "confidence" in vision_data:
            base_confidence = float(vision_data["confidence"])
        
        if "quality_score" in vision_data:
            base_confidence = max(base_confidence, float(vision_data["quality_score"]))
            
        # Adjust for lighting conditions
        if "lighting_condition" in vision_data:
            lighting = vision_data["lighting_condition"].lower()
            if lighting == "poor":
                base_confidence *= 0.7
            elif lighting == "excellent":
                base_confidence *= 1.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def estimate_audio_precision(self, audio_data: dict[str, Any]) -> float:
        """
        Estimate precision for audio data.
        
        Args:
            audio_data: Audio modality data
            
        Returns:
            Audio precision in [0.0, 1.0]
        """
        base_confidence = 0.5
        
        if "confidence" in audio_data:
            base_confidence = float(audio_data["confidence"])
            
        # Adjust for noise level
        if "noise_level" in audio_data:
            noise = audio_data["noise_level"].lower()
            if noise == "high":
                base_confidence *= 0.6
            elif noise == "low":
                base_confidence *= 1.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def estimate_language_precision(self, language_data: dict[str, Any]) -> float:
        """
        Estimate precision for language data.
        
        Args:
            language_data: Language modality data
            
        Returns:
            Language precision in [0.0, 1.0]
        """
        base_confidence = 0.5
        
        if "confidence" in language_data:
            base_confidence = float(language_data["confidence"])
            
        # Adjust for ambiguity
        if "ambiguity_score" in language_data:
            ambiguity = float(language_data["ambiguity_score"])
            base_confidence *= (1.0 - ambiguity * 0.5)
        
        return max(0.0, min(1.0, base_confidence))
    
    def estimate_memory_precision(self, memory_data: dict[str, Any]) -> float:
        """
        Estimate precision for memory data.
        
        Args:
            memory_data: Memory modality data
            
        Returns:
            Memory precision in [0.0, 1.0]
        """
        base_confidence = 0.5
        
        if "confidence" in memory_data:
            base_confidence = float(memory_data["confidence"])
            
        # Adjust for recall quality
        if "recall_quality" in memory_data:
            quality = memory_data["recall_quality"].lower()
            if quality == "high":
                base_confidence *= 1.2
            elif quality == "low":
                base_confidence *= 0.7
        
        return max(0.0, min(1.0, base_confidence))
    
    def estimate_latent_precision(self, latent_data: dict[str, Any]) -> float:
        """
        Estimate precision for latent representations.
        
        Args:
            latent_data: Latent modality data
            
        Returns:
            Latent precision in [0.0, 1.0]
        """
        base_confidence = 0.5
        
        if "confidence" in latent_data:
            base_confidence = float(latent_data["confidence"])
            
        # Adjust for embedding distance
        if "distance" in latent_data:
            distance = float(latent_data["distance"])
            # Larger distance indicates more uncertainty
            base_confidence *= max(0.5, 1.0 - distance * 0.1)
        
        return max(0.0, min(1.0, base_confidence))