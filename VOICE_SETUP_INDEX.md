# Voice Setup - Quick Reference Index

**Last Updated:** December 25, 2025
**Status:** ✅ COMPLETE - Ready to Use

---

## Quick Start

### Test Voice Cloning
```bash
cd src
../venv/Scripts/python audio_generator.py
```

### Generate Chapter Audio
```bash
cd src
../venv/Scripts/python generate_scene_audio.py --chapters 1
```

---

## Current Configuration

- **Voice:** male_calm_mature (calm, authoritative male)
- **File:** [voices/male_calm_mature.wav](voices/male_calm_mature.wav)
- **Model:** Chatterbox TTS (standard, 24kHz)
- **GPU:** NVIDIA RTX 3080 with CUDA 11.8
- **Test Output:** [audio/test_generation.wav](audio/test_generation.wav)

---

## Available Voices (8 Total)

### Male (5)
1. `male_young_energetic.wav` - Young energetic
2. `male_teen_casual.wav` - Teen casual
3. `male_calm_mature.wav` ← **CURRENT**
4. `male_narrator_deep.wav` - Deep narrator
5. `male_young_friendly.wav` - Friendly young

### Female (3)
6. `female_young_bright.wav` - Young bright
7. `female_teen_energetic.wav` - Teen energetic
8. `female_narrator_warm.wav` - Warm narrator

**All voices:** [voices/](voices/) directory

---

## Key Documentation

### Essential Files
- **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - Complete session summary
- **[VOICE_CLONING_COMPLETE.md](VOICE_CLONING_COMPLETE.md)** - Setup details
- **[voices/README.md](voices/README.md)** - Voice documentation
- **[docs/project/CHATTERBOX_TTS_MIGRATION.md](docs/project/CHATTERBOX_TTS_MIGRATION.md)** - Migration guide

### Configuration Files
- **[src/audio_generator.py](src/audio_generator.py)** - Audio generation (line 341: voice selection)
- **[src/config.py](src/config.py)** - Main configuration

---

## How to Switch Voices

**Edit:** [src/audio_generator.py](src/audio_generator.py) line 341

```python
# Current:
voice_file = "../voices/male_calm_mature.wav"

# Change to:
voice_file = "../voices/male_young_energetic.wav"  # Example
```

---

## Context Clear Summary

✅ Downloaded 8 real human voices (LibriSpeech dataset)
✅ Configured Chatterbox TTS with male_calm_mature voice
✅ Generated test audio successfully (251 KB, 5.34s)
✅ All documentation updated
✅ Ready for production use

**See [SESSION_SUMMARY.md](SESSION_SUMMARY.md) for complete details.**
