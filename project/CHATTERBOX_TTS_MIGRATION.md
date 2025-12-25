# Chatterbox TTS Migration Guide

## Overview

This document describes the migration from Coqui TTS XTTS v2 to Resemble AI Chatterbox TTS for audio generation in The Obsolescence novel project.

**Migration Date:** December 25, 2025
**Status:** ✅ Complete and Tested - Voice Cloning Configured
**License Change:** Coqui Public License (Non-commercial) → MIT License (Commercial use allowed)
**Voice Setup:** ✅ 8 real human voices downloaded (5 male + 3 female + teens)

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

**IMPORTANT CORRECTION:** Chatterbox HAS a default voice built into the model, but does NOT provide a downloadable voice library.

### Voice Options:
1. **Default Voice** (built-in, no files needed) - Works immediately, single voice
2. **Voice Cloning** (requires reference audio files) - For character differentiation

**NOTE:** Chatterbox does NOT provide downloadable voice files. To use multiple distinct voices, you must provide your own 10-second reference audio samples.

### Reference Audio Specifications

- **Duration:** 10 seconds (recommended)
- **Format:** WAV, MP3, or other common formats
- **Quality:** Clear, noise-free recording
- **Content:** Natural speech from the target speaker
- **Location:** `voices/` directory

### Voice File Structure (OPTIONAL - for voice cloning)

```
novel/
├── voices/
│   ├── narrator_neutral.wav       # Optional (default voice used if missing)
│   ├── emma_american.wav          # Optional
│   ├── maxim_russian.wav          # Optional
│   ├── amara_kenyan.wav           # Optional
│   ├── tyler_teen.wav             # Optional
│   └── elena_russian.wav          # Optional
```

### How to Get Multiple Voices

**Chatterbox does NOT provide downloadable voice files.** You have these options:

#### Option 1: Download Free Public Domain Voice Datasets (RECOMMENDED) ⭐

Use existing high-quality voice recordings from public datasets:

1. **VCTK Corpus** - 110 speakers with various English accents (BEST OPTION)
   - Download: https://datashare.ed.ac.uk/handle/10283/3443
   - Hugging Face: https://huggingface.co/datasets/CSTR-Edinburgh/vctk
   - Size: ~11GB, Format: 48kHz WAV/FLAC, License: Creative Commons 4.0
   - Perfect for: Character voices (includes American, Russian, Indian, African accents)
   - Character matching: Emma (American female), Maxim (Eastern European male), Amara (African female), etc.

2. **LibriSpeech** - 1000 hours from audiobooks
   - Download: https://www.openslr.org/12 (dev-clean subset is only 337MB)
   - Format: 16kHz WAV, License: Public domain
   - Perfect for: Narrator voices from professional audiobook readers

3. **LJSpeech** - Professional female narrator
   - Download: https://keithito.com/LJ-Speech-Dataset/
   - Direct link: http://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2
   - Format: 22.05kHz WAV, License: Public domain
   - Perfect for: High-quality female narrator

4. **Mozilla Common Voice** - 32,000+ hours, 104 languages
   - Download: https://commonvoice.mozilla.org/en/datasets
   - Hugging Face: https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0
   - Format: MP3, License: CC0
   - Perfect for: Multilingual voices and accent diversity

**How to use dataset voices:**
1. Download one of the datasets above
2. Extract 10-second audio clips from different speakers
3. Resample to 24kHz WAV (Chatterbox's sample rate)
4. Save to `voices/` directory with appropriate names
5. Use voice extractor script (see below)

#### Option 2: Use Default Voice (Simplest)
- No setup required
- Audio generation works immediately
- Single voice for all narration
- Command: `cd src && ../venv/Scripts/python generate_scene_audio.py --chapters 1 --single-voice`

#### Option 3: Record Custom Audio
1. **Record Your Own Voice:**
   - Record yourself or friends reading passages
   - Each character needs unique 10-second sample
   - Free but time-consuming

2. **Hire Voice Actors:**
   - Services like Fiverr for professional recordings
   - Costs money but professional quality
   - Ensure you have commercial rights

#### Option 4: Switch to Commercial TTS
- **ElevenLabs** - Has pre-made voice library (costs money, requires API key)
- **Azure Cognitive Services** - Has neural voice library (costs money)
- **Google Cloud TTS** - Has voice selection (costs money)

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
- [x] Create/obtain reference audio files for all characters (Dec 25: Downloaded 8 real human voices - 5 male + 3 female, including teens, from LibriSpeech dataset)
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

## Voice Dataset Resources

### Free Voice Datasets
- [VCTK Corpus (University of Edinburgh)](https://datashare.ed.ac.uk/handle/10283/3443)
- [VCTK on Hugging Face](https://huggingface.co/datasets/CSTR-Edinburgh/vctk)
- [LibriSpeech (OpenSLR)](https://www.openslr.org/12)
- [LJSpeech Dataset](https://keithito.com/LJ-Speech-Dataset/)
- [Mozilla Common Voice](https://commonvoice.mozilla.org/en/datasets)
- [Common Voice on Hugging Face](https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0)

### Voice Dataset Collections
- [GitHub: 95+ Voice Datasets](https://github.com/jim-schwoebel/voice_datasets)
- [40 Open-Source Audio Datasets for ML](https://towardsdatascience.com/40-open-source-audio-datasets-for-ml-59dc39d48f06/)

## References

- [Chatterbox GitHub](https://github.com/resemble-ai/chatterbox)
- [Chatterbox Hugging Face](https://huggingface.co/ResembleAI/chatterbox)
- [Chatterbox Demo Page](https://resemble-ai.github.io/chatterbox_demopage/)
- [Original TTS Comparison Research](TTS_COMPARISON.md)

## Credits

- **Resemble AI** - Chatterbox TTS development
- **Hugging Face** - Model hosting and distribution
- **The Obsolescence Project** - Novel and audio production
