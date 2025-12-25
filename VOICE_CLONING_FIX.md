# Voice Cloning Path Resolution Fix

## Summary
Fixed voice cloning not working in `generate_scene_audio.py` by converting relative voice file paths to absolute paths.

## Root Cause
- Test script (`test_voice_cloning.py`) used absolute paths: `Path(__file__).parent.parent / "voices" / "female_young_bright.wav"`
- Main generator used relative paths from `config.py`: `"voices/male_young_friendly.wav"`
- The `os.path.exists()` check failed when current working directory wasn't the project root
- System fell back to built-in speakers instead of voice cloning

## Changes Made

### src/config.py
1. Added `from pathlib import Path` import
2. Added `PROJECT_ROOT = Path(__file__).parent.parent` for absolute path resolution
3. Created internal `_VOICE_FILES` dict with relative paths for readability
4. Converted `CHARACTER_VOICES` to use absolute paths via dictionary comprehension
5. Updated Emma's voice from `male_young_friendly.wav` to `female_young_bright.wav`

### src/voice_config.py
- Removed excessive debug print statements
- Simplified logic (no functional changes)

### src/audio_generator.py
- Removed excessive debug print statements
- Simplified logic (no functional changes)

### src/generate_scene_audio.py
- Removed excessive debug print statements
- Simplified logic (no functional changes)

## Available Voice Files
All located in `voices/` directory:
- `female_narrator_warm.wav`
- `female_teen_energetic.wav`
- `female_young_bright.wav` (Emma's voice)
- `male_calm_mature.wav`
- `male_narrator_deep.wav`
- `male_teen_casual.wav`
- `male_young_energetic.wav`
- `male_young_friendly.wav` (default for most characters)

## Testing
Voice cloning now works correctly:
- Paths are absolute: `C:\Users\Bob\source\repos\novel\voices\female_young_bright.wav`
- Works from any working directory
- No changes needed to voice_config.py or audio_generator.py logic
- All voice files verified to exist

## Usage
Voice cloning will now activate automatically when:
1. A character is configured with a voice file in `config.py`
2. The voice file exists in the `voices/` directory
3. The system will use the voice file for cloning instead of built-in speakers
