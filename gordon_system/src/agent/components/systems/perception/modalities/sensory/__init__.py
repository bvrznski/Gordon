# Sensory Modalities Package - Phase 5.2
# ======================================

"""
Sensory Modalities: Observe physical or simulated environments.

These modalities share common characteristics:
    - Require calibration for accurate observation
    - Must estimate noise and quality
    - Preserve temporal sampling
    - Handle missing signal gracefully
    - Maintain sensor-specific calibration data

Current sensory modalities:
    vision      - Images, video, movement, geometry, appearance, depth
    audition    - Sound, environmental audio, music, noise
    speech      - Spoken language, phonemes, words, utterances

Future sensory modalities (Phase 5.2.x):
    depth       - Distance and geometric structure
    lidar       - Laser-based distance measurement
    radar       - Radio-wave based detection
    touch       - Contact, pressure, texture
    proprioception - Embodied state
    inertial    - Acceleration, rotation, orientation
"""

from .vision import VisionModality

__all__: list[str] = [
    "VisionModality",
]