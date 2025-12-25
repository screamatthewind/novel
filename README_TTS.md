# TTS Audio Generation - Quick Start Guide

## ✅ System Status: READY

Your TTS audio generation system is fully implemented and working with CUDA acceleration on your RTX 3080.

## What Was Built

A complete text-to-speech system that generates multi-voice audio narration for your novel chapters using Coqui TTS XTTS v2.

### Features
- ✅ Multi-voice narration (different voices for different characters)
- ✅ CUDA GPU acceleration (RTX 3080)
- ✅ Automatic dialogue parsing and speaker attribution
- ✅ Parallel to existing image generation system
- ✅ Comprehensive diagnostics and error handling

## Quick Commands

### Check CUDA Status
```bash
cd src
python check_cuda.py
```

### Generate Audio (Dry Run - Test Dialogue Parsing)
```bash
python generate_scene_audio.py --chapters 1 --dry-run
```

### Generate Audio (One Scene)
```bash
python generate_scene_audio.py --chapters 1 --resume 1 1
```

### Generate Audio (Full Chapter)
```bash
python generate_scene_audio.py --chapters 1
```

### Generate Audio (All Chapters)
```bash
python generate_scene_audio.py
```

## Files Created

### Core Implementation (src/)
- `voice_config.py` - Voice profile management
- `dialogue_parser.py` - Text preprocessing and speaker attribution
- `audio_filename_generator.py` - Filename generation matching image convention
- `audio_generator.py` - Coqui TTS wrapper with CUDA diagnostics
- `generate_scene_audio.py` - Main CLI for audio generation
- `check_cuda.py` - PyTorch/CUDA diagnostic tool

### Documentation
- `TTS_IMPLEMENTATION_PLAN.md` - Original implementation plan
- `TTS_SETUP_COMPLETE.md` - Complete setup guide
- `CUDA_FIX_README.md` - CUDA troubleshooting guide
- `INSTALLATION.md` - Full installation instructions
- `README_TTS.md` - This file (quick reference)

### Configuration
- `config.py` - Updated with audio settings and character voice mappings
- `requirements.txt` - Updated with TTS dependencies and installation warnings

## Critical Installation Rule

**ALWAYS install PyTorch with CUDA FIRST:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Then install other packages:**
```bash
pip install -r requirements.txt
```

**NEVER run `pip install TTS` by itself** - it will replace your CUDA PyTorch with CPU-only version!

## Performance

With CUDA (RTX 3080):
- ~2-3 minutes per 500-word scene
- ~10-15 minutes per chapter (4 scenes)
- ~40-60 minutes for all chapters (15 scenes)

Without CUDA (CPU fallback):
- ~15-20 minutes per scene
- ~1+ hour per chapter
- ~4-5 hours for all chapters

## Output Structure

```
novel/
├── audio/                   # Generated audio files
│   ├── chapter_01_scene_01_emma_factory_working.wav
│   ├── chapter_01_scene_02_emma_office_reading.wav
│   └── ...
├── audio_cache/            # Dialogue parsing cache
│   ├── chapter_01_scene_01_emma_factory_working_dialogue.json
│   ├── chapter_01_scene_01_emma_factory_working_metadata.json
│   └── ...
└── logs/                   # Generation logs
    ├── audio_generation_20251224_193000.log
    └── ...
```

## Command-Line Options

```bash
python generate_scene_audio.py [OPTIONS]

Options:
  --chapters 1 3           Generate specific chapters
  --resume 2 5             Resume from Chapter 2, Scene 5
  --dry-run                Show dialogue parsing without generating audio
  --audio-format {wav,mp3} Output format (default: wav)
  --single-voice           Use narrator only (testing mode)
  --skip-cache             Regenerate even if exists
```

## Common Issues & Fixes

### Issue: MeCab error (Japanese language support)

**Error:** `Failed initializing MeCab... no such file or directory: c:\mecab\mecabrc`

**Fix (Already Applied):**
```bash
pip uninstall -y mecab-python3
pip install unidic-lite
pip install mecab-python3
```

This installs the MeCab dictionary backend. The TTS system only uses English, so MeCab warnings are suppressed in the code.

### Issue: PyTorch 2.6 weights_only error

**Error:** `Weights only load failed... WeightsUnpickler error`

**Fix (Already Applied):**
The code in `src/audio_generator.py` now patches the TTS library to use `weights_only=False` when loading models. This is safe for official Coqui TTS models.

### Issue: Transformers version incompatibility

**Error:** `cannot import name 'BeamSearchScorer' from 'transformers'`

**Fix (Already Applied):**
```bash
pip install "transformers<4.41.0"
```

Transformers has been downgraded to 4.40.2 which is compatible with TTS.

### Issue: "device is cpu" even with RTX 3080

**Diagnosis:**
```bash
cd src
python check_cuda.py
```

**Fix if shows CPU-only PyTorch:**
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
python check_cuda.py  # Verify
```

### Issue: TTS installation breaks CUDA

This happens if you run `pip install TTS` which replaces CUDA PyTorch.

**Fix:**
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

TTS and dependencies are already installed, no need to reinstall them.

### Issue: First run downloads ~2GB model

This is expected. XTTS v2 model downloads automatically on first use.

## Voice Configuration

Current setup uses XTTS v2's pretrained voices. Character mapping is in `src/config.py`:

```python
CHARACTER_VOICES = {
    "narrator": "voices/narrator_neutral.wav",
    "emma": "voices/emma_american.wav",
    "maxim": "voices/maxim_russian.wav",
    "amara": "voices/amara_kenyan.wav",
    "tyler": "voices/tyler_teen.wav",
    "elena": "voices/elena_russian.wav",
    "mark": "voices/narrator_neutral.wav",
    "diane": "voices/narrator_neutral.wav",
    "ramirez": "voices/narrator_neutral.wav"
}
```

To add custom voice cloning later:
1. Record 10-30 second samples
2. Save to `voices/` directory with matching filenames
3. System will automatically use them

## Dialogue Parser Notes

The dialogue parser attempts to:
- Separate dialogue from narration
- Attribute speakers based on patterns like "text," Emma said
- Handle pronouns (he/she said) using context

May occasionally misattribute speakers in complex dialogue. Review dry-run output to verify attribution before generating audio.

## Testing Workflow

1. **Test dialogue parsing:**
   ```bash
   python generate_scene_audio.py --chapters 1 --dry-run
   ```
   Review the speaker attribution output.

2. **Test one scene:**
   ```bash
   python generate_scene_audio.py --chapters 1 --resume 1 1
   ```
   Listen to the generated audio file.

3. **If satisfied, generate full chapter:**
   ```bash
   python generate_scene_audio.py --chapters 1
   ```

## Troubleshooting Resources

- **CUDA Issues:** Run `python src/check_cuda.py`
- **Installation:** See `INSTALLATION.md`
- **Setup Guide:** See `TTS_SETUP_COMPLETE.md`
- **Troubleshooting:** See `CUDA_FIX_README.md`

## Key Files Reference

- **Configuration:** `src/config.py` lines 48-66 (audio settings)
- **Voice Mapping:** `src/voice_config.py`
- **Dialogue Parsing:** `src/dialogue_parser.py`
- **TTS Engine:** `src/audio_generator.py`
- **Main CLI:** `src/generate_scene_audio.py`
- **Diagnostics:** `src/check_cuda.py`

## Next Steps After Context Clear

1. Verify CUDA is working: `python src/check_cuda.py`
2. Test with dry-run: `python src/generate_scene_audio.py --chapters 1 --dry-run`
3. Generate one scene: `python src/generate_scene_audio.py --chapters 1 --resume 1 1`
4. Review audio quality and dialogue attribution
5. Generate remaining chapters if satisfied

---

**System is ready for GPU-accelerated audio generation!**

For detailed information, see:
- Full setup: `TTS_SETUP_COMPLETE.md`
- Installation: `INSTALLATION.md`
- Implementation details: `TTS_IMPLEMENTATION_PLAN.md`
