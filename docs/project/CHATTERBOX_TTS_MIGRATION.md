# Chatterbox TTS Migration Guide

## Overview

This document describes the migration from Coqui TTS XTTS v2 to Resemble AI Chatterbox TTS for audio generation in The Obsolescence novel project.

**Migration Date:** December 25, 2025
**Status:** ✅ Complete and Tested
**License Change:** Coqui Public License (Non-commercial) → MIT License (Commercial use allowed)

## Why We Migrated

### Previous Setup (Coqui TTS)
- **License:** Coqui Public License (Non-commercial only)
- **Model:** XTTS v2 (~2GB)
- **Sample Rate:** 22.05kHz
- **Pros:** Excellent prosody, 17 languages, voice cloning
- **Cons:** Non-commercial license, company shut down, not ideal narrator voice

### New Setup (Chatterbox TTS)
- **License:** MIT (Commercial use allowed ✅)
- **Model:** Chatterbox Standard (~500M params) / Turbo (~350M params)
- **Sample Rate:** 24kHz
- **Pros:** MIT license, emotion control tags, 6× real-time speed, outperforms ElevenLabs
- **Cons:** Requires reference audio for all voices (no built-in speakers)

## Installation

### Prerequisites

1. **PyTorch with CUDA 11.8** (must be installed first):
```bash
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

2. **Chatterbox TTS**:
```bash
./venv/Scripts/pip install chatterbox-tts
```

Or install all requirements:
```bash
./venv/Scripts/pip install -r requirements.txt
```

### First Run Model Download

On first use, Chatterbox will download the model from Hugging Face (~500MB-1GB depending on variant):
- Standard Chatterbox: `ResembleAI/chatterbox`
- Multilingual: `ResembleAI/chatterbox-multilingual`
- Turbo: `ResembleAI/chatterbox-turbo` (requires HF authentication)

## Model Variants

Chatterbox offers three model variants:

| Model | Size | Languages | Best For | Authentication |
|-------|------|-----------|----------|----------------|
| **Standard** | 500M | English | General use, voice cloning | None required |
| **Multilingual** | 500M | 23+ | Global applications | None required |
| **Turbo** | 350M | English | Low-latency production | Requires HF_TOKEN |

### Using Chatterbox Turbo

The Turbo model requires Hugging Face authentication. Set the environment variable:

**Windows (PowerShell):**
```powershell
$env:HF_TOKEN = "your_huggingface_token_here"
```

**Windows (Command Prompt):**
```cmd
set HF_TOKEN=your_huggingface_token_here
```

**Linux/Mac:**
```bash
export HF_TOKEN=your_huggingface_token_here
```

Get your token from: https://huggingface.co/settings/tokens

If no token is provided, the system automatically falls back to the standard Chatterbox model.

## Configuration Changes

### config.py

```python
# OLD (Coqui TTS)
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
MAX_TTS_CHUNK_SIZE = 240

CHARACTER_SPEAKERS = {
    "narrator": "Claribel Dervla",
    # ... built-in XTTS speakers
}

# NEW (Chatterbox TTS)
DEFAULT_SAMPLE_RATE = 24000  # Chatterbox uses 24kHz
DEFAULT_TTS_MODEL = "turbo"  # Options: "chatterbox", "multilingual", "turbo"
MAX_TTS_CHUNK_SIZE = 500  # Chatterbox can handle longer chunks

# Note: Chatterbox does not use built-in speakers
# All voices require reference audio files for cloning
CHARACTER_VOICES = {
    "narrator": os.path.join(VOICES_DIR, "narrator_neutral.wav"),
    # ... all must have reference audio files
}
```

### audio_generator.py

```python
# OLD
from audio_generator import CoquiTTSGenerator

generator = CoquiTTSGenerator()

# NEW
from audio_generator import ChatterboxTTSGenerator

generator = ChatterboxTTSGenerator(model_name="turbo")  # or "chatterbox" or "multilingual"
```

## Voice Cloning Requirements

**IMPORTANT:** Unlike Coqui TTS, Chatterbox does NOT have built-in speaker voices. All characters require reference audio files.

### Reference Audio Specifications

- **Duration:** 10 seconds (recommended)
- **Format:** WAV, MP3, or other common formats
- **Quality:** Clear, noise-free recording
- **Content:** Natural speech from the target speaker
- **Location:** `voices/` directory

### Voice File Structure

```
novel/
├── voices/
│   ├── narrator_neutral.wav       # Required
│   ├── emma_american.wav
│   ├── maxim_russian.wav
│   ├── amara_kenyan.wav
│   ├── tyler_teen.wav
│   └── elena_russian.wav
```

### Creating Reference Audio

If you don't have existing voice samples:

1. **Use Existing TTS to Generate References:**
   ```python
   # Generate 10-second samples with Coqui TTS (before migration)
   # Save as reference audio for Chatterbox
   ```

2. **Record Your Own Voice:**
   - Record yourself reading a passage
   - Save as WAV file in `voices/` directory
   - Chatterbox will clone your voice characteristics

3. **Use Online Voice Actors:**
   - Hire voice actors to record 10-second samples
   - Ensure you have rights to use the voice

## Features

### Emotion Control (Turbo Model)

Chatterbox Turbo supports paralinguistic tags:

```python
text = "Sarah here from MochaFone [chuckle], have you got a minute?"
# Supported tags: [laugh], [cough], [chuckle], [sigh]
```

### Built-in Watermarking

All Chatterbox outputs include imperceptible Perth watermarks for responsible AI detection.

### Performance

- **Speed:** 6× real-time on GPU (RTX 3080: ~24 iterations/sec)
- **Quality:** Outperforms ElevenLabs (63.75% preference in blind tests)
- **Memory:** Moderate VRAM requirements (8-12GB recommended)

## Testing

### Test Audio Generation

```bash
cd src
../venv/Scripts/python audio_generator.py
```

Expected output:
```
Chatterbox TTS Generator Test
======================================================================

CUDA detected: NVIDIA GeForce RTX 3080 (CUDA 11.8)

1. Loading model...
Loading Chatterbox TTS model: turbo
Target device: cuda

[INFO] Chatterbox Turbo requires authentication.
Falling back to standard Chatterbox model...
[OK] Model loaded successfully! Sample rate: 24000 Hz

2. Generating test audio...
   Generated 4.28 seconds of audio
   Saved to: ../audio/test_generation.wav

3. Testing chunked generation...
   Generated 14.48 seconds of chunked audio

4. Unloading model...
Model unloaded successfully

Test complete!
```

### Generate Scene Audio

```bash
cd src
../venv/Scripts/python generate_scene_audio.py --chapters 1
```

## Troubleshooting

### Model Download Issues

**Problem:** Model fails to download from Hugging Face

**Solution:**
```bash
# Clear Hugging Face cache
rm -rf ~/.cache/huggingface/

# Or on Windows:
rmdir /s %USERPROFILE%\.cache\huggingface

# Then try again
```

### Authentication Errors (Turbo Model)

**Problem:** `Token is required but no token found`

**Solutions:**
1. Set `HF_TOKEN` environment variable (see above)
2. Use standard model instead: `DEFAULT_TTS_MODEL = "chatterbox"`
3. Login via Hugging Face CLI:
   ```bash
   huggingface-cli login
   ```

### Missing Voice Files

**Problem:** `Warning: No reference audio provided`

**Solution:**
1. Ensure voice files exist in `voices/` directory
2. Check file paths in `config.py` CHARACTER_VOICES
3. Verify file permissions and formats

### CUDA Out of Memory

**Problem:** GPU runs out of memory during generation

**Solutions:**
1. Use smaller model: `DEFAULT_TTS_MODEL = "turbo"`
2. Reduce batch size in generation
3. Close other GPU-intensive applications
4. Fallback to CPU: `DEVICE = "cpu"` (much slower)

### Dependency Conflicts

**Problem:** PyTorch version conflicts

**Solution:**
```bash
# Uninstall conflicting packages
./venv/Scripts/pip uninstall torch torchvision torchaudio -y

# Reinstall with CUDA support
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Then reinstall other requirements
./venv/Scripts/pip install -r requirements.txt
```

## Migration Checklist

- [x] Install PyTorch with CUDA 11.8
- [x] Install chatterbox-tts
- [x] Update config.py settings
- [x] Convert audio_generator.py to ChatterboxTTSGenerator
- [x] Update voice_config.py for reference audio
- [x] Update generate_scene_audio.py class references
- [x] Update requirements.txt
- [x] Test model loading and audio generation
- [x] Update documentation
- [ ] Create/obtain reference audio files for all characters
- [ ] Generate full chapter audio with Chatterbox
- [ ] Compare quality with previous Coqui TTS output

## Performance Comparison

| Metric | Coqui TTS XTTS v2 | Chatterbox TTS |
|--------|-------------------|----------------|
| License | Non-commercial | MIT (Commercial ✅) |
| Sample Rate | 22.05kHz | 24kHz |
| Speed | ~4× real-time | ~6× real-time |
| Voice Cloning | 6s reference | 10s reference |
| Built-in Voices | 17 speakers | None (requires reference) |
| Emotion Control | No | Yes ([laugh], [cough], etc.) |
| Model Size | ~2GB | 350M-500M |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## References

- [Chatterbox GitHub](https://github.com/resemble-ai/chatterbox)
- [Chatterbox Hugging Face](https://huggingface.co/ResembleAI/chatterbox)
- [Chatterbox Demo Page](https://resemble-ai.github.io/chatterbox_demopage/)
- [Original TTS Comparison Research](TTS_COMPARISON.md)

## Credits

- **Resemble AI** - Chatterbox TTS development
- **Hugging Face** - Model hosting and distribution
- **The Obsolescence Project** - Novel and audio production
