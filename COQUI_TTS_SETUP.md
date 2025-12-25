# Coqui TTS Setup Guide

## Date: 2025-12-25

## Overview

The audio generation system has been converted from Chatterbox TTS to Coqui TTS, providing better voice quality and more flexibility with voice selection.

## System Requirements

### CRITICAL: espeak-ng Backend

Coqui TTS requires the `espeak-ng` text-to-speech backend to be installed system-wide.

#### Windows Installation

**Option 1: Using Chocolatey (Recommended)**
```bash
choco install espeak-ng
```

**Option 2: Manual Installation**
1. Download the installer from: https://github.com/espeak-ng/espeak-ng/releases
2. Download: `espeak-ng-X64.msi` (latest version)
3. Run the installer
4. Restart your terminal after installation

#### Linux Installation
```bash
sudo apt-get update
sudo apt-get install espeak-ng
```

#### macOS Installation
```bash
brew install espeak-ng
```

### Verify Installation

After installing espeak-ng, verify it's accessible:
```bash
espeak-ng --version
```

You should see version information. If you get "command not found", you may need to restart your terminal or add espeak-ng to your PATH.

## Python Package Installation

### Step 1: Install PyTorch with CUDA (if not already installed)

```bash
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 2: Uninstall Chatterbox TTS (if previously installed)

```bash
./venv/Scripts/pip uninstall chatterbox-tts -y
```

### Step 3: Install Coqui TTS

```bash
./venv/Scripts/pip install TTS
```

**Note**: This will download TTS models (~200MB-2GB) on first run.

## Configuration

### Voice Models

The system supports two voice generation modes:

#### Mode 1: VCTK Multi-Speaker (Default)
- **Model**: `tts_models/en/vctk/vits`
- **Speakers**: 109 built-in voices
- **Speed**: Fast
- **Quality**: Good
- **Setup**: No reference audio needed
- **Current Config**: See [src/config.py](src/config.py:74-86)

#### Mode 2: XTTS Voice Cloning
- **Model**: `tts_models/multilingual/multi-dataset/xtts_v2`
- **Speakers**: Clone any voice from ~10 seconds of reference audio
- **Speed**: Slower
- **Quality**: Excellent (matches reference voice)
- **Setup**: Requires reference audio files in `voices/` directory
- **Config**: Uncomment alternative configuration in [src/config.py](src/config.py:88-100)

### Character Voice Mapping

Current configuration (VCTK mode):
```python
CHARACTER_VOICES = {
    "narrator": "p226",  # Male young
    "emma": "p225",      # Female young
    "maxim": "p227",     # Male
    "amara": "p228",     # Female
    "tyler": "p232",     # Male young
    "elena": "p229",     # Female
    "mark": "p230",      # Male
    "diane": "p231",     # Female
    "ramirez": "p233"    # Male
}
```

Available VCTK speakers: p225-p376 (see Coqui TTS documentation for full list)

## Testing the Installation

### Test 1: Voice Configuration Check

```bash
cd src
../venv/Scripts/python voice_config.py
```

Expected output:
```
Coqui TTS Voice Configuration Test
==================================================

Configured characters:
  - narrator
  - emma
  - maxim
  ...

Voice configuration status:
  narrator        ✓ VALID (speaker)                  p226
  emma            ✓ VALID (speaker)                  p225
  ...
```

### Test 2: TTS Generator Test

```bash
cd src
../venv/Scripts/python audio_generator.py
```

Expected output:
```
Coqui TTS Generator Test
======================================================================

1. Loading model...
Loading Coqui TTS model: tts_models/en/vctk/vits
[TTS] Downloading model...
[OK] Model loaded successfully! Sample rate: 22050 Hz

2. Generating test audio with built-in speaker...
   Generated X.XX seconds of audio
   ...
```

### Test 3: Generate Scene Audio (Dry Run)

```bash
cd src
../venv/Scripts/python generate_scene_audio.py --chapters 1 --dry-run
```

This will show what would be generated without actually creating audio files.

### Test 4: Generate Actual Audio

```bash
cd src
../venv/Scripts/python generate_scene_audio.py --chapters 1
```

## Troubleshooting

### Error: "No espeak backend found"

**Solution**: Install espeak-ng system-wide (see System Requirements above)

### Error: "Model not found" or Download Fails

**Solution**:
1. Check internet connection
2. Try running with verbose output: `TTS --list_models`
3. Manually specify model path if needed

### Error: CUDA Out of Memory

**Solutions**:
1. Reduce chunk size in config.py: `MAX_TTS_CHUNK_SIZE = 250`
2. Use CPU mode (slower): Set `DEVICE = "cpu"` in config.py
3. Process fewer chapters at once

### Poor Voice Quality

**Solutions**:
1. Switch to XTTS mode with voice cloning for better quality
2. Adjust speaker selection in CHARACTER_VOICES
3. Try different VCTK speakers to find better voice matches

## Files Modified

### Core Files
1. [requirements.txt](requirements.txt) - Updated TTS dependency and installation instructions
2. [src/audio_generator.py](src/audio_generator.py) - Completely rewritten for Coqui TTS
3. [src/config.py](src/config.py:61-100) - Updated TTS configuration
4. [src/generate_scene_audio.py](src/generate_scene_audio.py) - Updated imports and references
5. [src/voice_config.py](src/voice_config.py) - Enhanced to support both speaker names and file paths

### Key Changes
- Renamed class: `ChatterboxTTSGenerator` → `CoquiTTSGenerator`
- Default sample rate: 24000 Hz → 22050 Hz
- Voice configuration: File paths → Speaker IDs (with file path option)
- Model selection: More flexible with multiple Coqui model options

## Next Steps

1. **Install espeak-ng** (if not already done)
2. **Install Coqui TTS**: `./venv/Scripts/pip install TTS`
3. **Test installation**: Run the test commands above
4. **Generate audio**: `cd src && ../venv/Scripts/python generate_scene_audio.py --chapters 1`
5. **Optional**: Switch to XTTS mode if you want voice cloning with custom voices

## Additional Resources

- Coqui TTS Documentation: https://docs.coqui.ai/
- Coqui TTS Models List: Run `tts --list_models` to see all available models
- espeak-ng Project: https://github.com/espeak-ng/espeak-ng
- VCTK Speaker Samples: https://datashare.ed.ac.uk/handle/10283/3443

## CRITICAL Bug Fix: Voice Cloning API (2025-12-25)

### Problem
Voice cloning with XTTS v2 was not working due to incorrect API usage.

### Root Cause
The `get_conditioning_latents()` method is not available on the TTS API wrapper object, but on the underlying model object.

### Solution
**WRONG (original code):**
```python
gpt_cond_latent, speaker_embedding = self.model.get_conditioning_latents(
    audio_path=[speaker_wav]
)
```

**CORRECT (fixed code):**
```python
gpt_cond_latent, speaker_embedding = self.model.synthesizer.tts_model.get_conditioning_latents(
    audio_path=[speaker_wav]
)
```

### Files Modified
- `src/audio_generator.py:170-172` - Updated to use correct API path

### Key Learning
When using Coqui TTS XTTS v2 model:
- The TTS API wrapper (`TTS` class) provides high-level methods like `.tts()`
- Voice cloning requires accessing the underlying model: `self.model.synthesizer.tts_model`
- The conditioning latents method is XTTS-specific and not available on the wrapper

### Testing
Test voice cloning works:
```bash
cd src
../venv/Scripts/python -c "
from audio_generator import CoquiTTSGenerator
gen = CoquiTTSGenerator()
gen.load_model()
audio = gen.generate_speech('Test', speaker_wav='../voices/male_young_friendly.wav')
print('SUCCESS' if audio is not None else 'FAILED')
gen.unload_model()
"
```

## Status

✅ All code files updated and converted to Coqui TTS
✅ Configuration ready with VCTK multi-speaker mode
✅ Voice cloning bug fixed (correct API usage)
✅ Debug logging added to all voice generation files
⚠️ **ACTION REQUIRED**: Install espeak-ng system dependency
⚠️ **ACTION REQUIRED**: Install Coqui TTS Python package
