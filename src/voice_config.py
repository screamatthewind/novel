"""
Voice configuration and management for Coqui TTS audio generation.
Handles voice profile selection and reference audio management.
"""

from dataclasses import dataclass
from typing import Optional, Dict
import os
from config import CHARACTER_VOICES, CHARACTER_SPEAKERS, VOICES_DIR


@dataclass
class VoiceProfile:
    """Voice profile for a character."""
    character_name: str
    voice_file_path: str
    language: str = "en"


def get_voice_for_speaker(speaker_name: str) -> Dict[str, str]:
    """
    Get voice configuration for a character.

    Prioritizes voice cloning files, falls back to built-in XTTS speakers.

    Args:
        speaker_name: Name of the character speaking

    Returns:
        Dictionary with 'type' ('speaker' or 'file') and 'value' (speaker name or path)
    """
    # Normalize speaker name to lowercase
    normalized_name = speaker_name.lower().strip()

    # Get voice file path from configuration
    voice_file = CHARACTER_VOICES.get(normalized_name, CHARACTER_VOICES.get("narrator"))

    # Check if voice file exists for voice cloning
    if voice_file and os.path.exists(voice_file):
        return {'type': 'file', 'value': voice_file}

    # Fall back to built-in XTTS speaker
    speaker = CHARACTER_SPEAKERS.get(normalized_name, CHARACTER_SPEAKERS.get("narrator", "Claribel Dervla"))
    return {'type': 'speaker', 'value': speaker}


def get_all_characters() -> list[str]:
    """
    Get list of all configured character names.

    Returns:
        List of character names
    """
    return list(CHARACTER_VOICES.keys())


def validate_voice_files() -> dict[str, bool]:
    """
    Check which voice files exist (for XTTS mode) or speakers are valid (for VCTK mode).

    Returns:
        Dictionary mapping character names to existence/validity status
    """
    status = {}
    for character, voice in CHARACTER_VOICES.items():
        if isinstance(voice, str):
            if voice.endswith('.wav'):
                # File-based voice (XTTS)
                status[character] = os.path.exists(voice)
            else:
                # Speaker name (VCTK) - assume valid
                status[character] = True
        else:
            status[character] = False
    return status


if __name__ == "__main__":
    # Test voice configuration for Coqui TTS
    print("Coqui TTS Voice Configuration Test")
    print("=" * 50)

    print("\nConfigured characters:")
    for char in get_all_characters():
        print(f"  - {char}")

    print("\nVoice configuration status:")
    status = validate_voice_files()
    for character, valid in status.items():
        voice = CHARACTER_VOICES[character]
        if isinstance(voice, str) and voice.endswith('.wav'):
            status_str = "✓ EXISTS" if valid else "✗ MISSING (file)"
            print(f"  {character:15} {status_str:35} {voice}")
        else:
            status_str = "✓ VALID (speaker)"
            print(f"  {character:15} {status_str:35} {voice}")

    print("\nTesting voice selection:")
    test_speakers = ["Emma", "maxim", "RAMIREZ", "unknown_character"]
    for speaker in test_speakers:
        voice = get_voice_for_speaker(speaker)
        if voice['type'] == 'file':
            exists = os.path.exists(voice['value'])
            status = "✓" if exists else "✗"
            print(f"  {speaker:20} -> {status} {voice['type']}: {voice['value']}")
        else:
            print(f"  {speaker:20} -> ✓ {voice['type']}: {voice['value']}")
