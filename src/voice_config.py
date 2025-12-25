"""
Voice configuration and management for Chatterbox TTS audio generation.
Handles voice profile selection and reference audio management.
"""

from dataclasses import dataclass
from typing import Optional, Dict
import os
from config import CHARACTER_VOICES, VOICES_DIR


@dataclass
class VoiceProfile:
    """Voice profile for a character."""
    character_name: str
    voice_file_path: str
    language: str = "en"


def get_voice_for_speaker(speaker_name: str) -> Dict[str, str]:
    """
    Get voice configuration for a character.

    Returns a voice file path for Chatterbox voice cloning.
    Chatterbox requires reference audio files for all voices.

    Args:
        speaker_name: Name of the character speaking

    Returns:
        Dictionary with 'type' ('file') and 'value' (path to reference audio)
    """
    # Normalize speaker name to lowercase
    normalized_name = speaker_name.lower().strip()

    # Get voice path from configuration
    voice_path = CHARACTER_VOICES.get(normalized_name, CHARACTER_VOICES["narrator"])

    # Return the voice file path (Chatterbox always uses files)
    return {'type': 'file', 'value': voice_path}


def get_all_characters() -> list[str]:
    """
    Get list of all configured character names.

    Returns:
        List of character names
    """
    return list(CHARACTER_VOICES.keys())


def validate_voice_files() -> dict[str, bool]:
    """
    Check which voice files exist.

    Returns:
        Dictionary mapping character names to existence status
    """
    status = {}
    for character, voice_path in CHARACTER_VOICES.items():
        status[character] = os.path.exists(voice_path)
    return status


if __name__ == "__main__":
    # Test voice configuration for Chatterbox
    print("Chatterbox Voice Configuration Test")
    print("=" * 50)

    print("\nConfigured characters:")
    for char in get_all_characters():
        print(f"  - {char}")

    print("\nVoice file status:")
    status = validate_voice_files()
    for character, exists in status.items():
        status_str = "✓ EXISTS" if exists else "✗ MISSING (required for Chatterbox)"
        voice_path = CHARACTER_VOICES[character]
        print(f"  {character:15} {status_str:35} {voice_path}")

    print("\nTesting voice selection:")
    test_speakers = ["Emma", "maxim", "RAMIREZ", "unknown_character"]
    for speaker in test_speakers:
        voice = get_voice_for_speaker(speaker)
        exists = os.path.exists(voice['value'])
        status = "✓" if exists else "✗"
        print(f"  {speaker:20} -> {status} {voice['value']}")
