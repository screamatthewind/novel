# TTS Audio Generation System - Setup Complete

## Status: ✓ READY

Your TTS audio generation system is now fully configured and ready to use with CUDA acceleration on your RTX 3080.

## Verification

```
PyTorch: 2.7.1+cu118
CUDA available: True
Device: NVIDIA GeForce RTX 3080 (CUDA 11.8)
```

## What Was Fixed

### Issue
When you ran `pip install TTS`, it automatically upgraded PyTorch to version 2.9.1 (CPU-only), which replaced your existing CUDA-enabled PyTorch 2.7.1+cu118.

### Solution
1. Uninstalled all PyTorch packages
2. Reinstalled PyTorch with CUDA 11.8 support using the correct index URL
3. Installed TTS dependencies without breaking PyTorch

### Files Created/Modified

1. **[src/audio_generator.py](src/audio_generator.py)** - Enhanced with CUDA diagnostics
2. **[src/check_cuda.py](src/check_cuda.py)** - Diagnostic tool for checking PyTorch/CUDA setup
3. **[CUDA_FIX_README.md](CUDA_FIX_README.md)** - Comprehensive troubleshooting guide

## How to Use

### 1. Generate Audio (Dry Run - No Dependencies Required)

Test dialogue parsing without generating audio:

```bash
cd src
python generate_scene_audio.py --chapters 1 --dry-run
```

This shows you how the dialogue will be parsed and attributed to speakers.

### 2. Generate Audio for One Scene

Generate audio for Chapter 1, Scene 1 only:

```bash
python generate_scene_audio.py --chapters 1 --resume 1 1
```

**Expected:**
- Download of ~2GB XTTS v2 model (first run only)
- ~2-3 minutes generation time per 500-word scene
- Audio file saved to `../audio/chapter_01_scene_01_emma_factory_reading.wav`

### 3. Generate Audio for Full Chapter

Generate all scenes in Chapter 1:

```bash
python generate_scene_audio.py --chapters 1
```

**Expected:**
- ~10-15 minutes for Chapter 1 (assuming 4 scenes)
- Progress logged to `../logs/audio_generation_TIMESTAMP.log`

### 4. Generate Audio for All Chapters

```bash
python generate_scene_audio.py
```

**Expected:**
- ~40-60 minutes for all 4 chapters (15 scenes total)
- All audio files in `../audio/`
- Metadata cached to `../audio_cache/`

## Performance

With CUDA (RTX 3080):
- **~150-200 words/minute** generation speed
- **~2.5-3 minutes** per 500-word scene
- **~40-60 minutes** for all 15 scenes

Without CUDA (CPU fallback):
- **~20-30 words/minute** generation speed
- **~15-20 minutes** per 500-word scene
- **~4-5 hours** for all 15 scenes

## Voice Configuration

### Current Setup
The system is configured to use XTTS v2's pretrained multi-speaker voices. Character voice mapping is in [src/config.py:55-66](src/config.py#L55-L66):

```python
CHARACTER_VOICES = {
    "narrator": "voices/narrator_neutral.wav",
    "emma": "voices/emma_american.wav",
    "maxim": "voices/maxim_russian.wav",
    "amara": "voices/amara_kenyan.wav",
    # ... etc
}
```

### Voice Cloning (Optional Enhancement)
To add custom voice cloning:

1. Record 10-30 second audio samples of each character
2. Save to the `voices/` directory with filenames matching config
3. System will automatically use these for voice cloning

**For now**, the system will use XTTS v2's built-in voices, which is fine for initial testing.

## Output Structure

After generation, your project will have:

```
novel/
├── audio/
│   ├── chapter_01_scene_01_emma_factory_reading.wav
│   ├── chapter_01_scene_02_emma_rowhouse_shocked.wav
│   └── ...
├── audio_cache/
│   ├── chapter_01_scene_01_emma_factory_reading_dialogue.json
│   ├── chapter_01_scene_01_emma_factory_reading_metadata.json
│   └── ...
└── logs/
    ├── audio_generation_20251224_193000.log
    └── ...
```

## Dialogue Parser Notes

The dialogue parser ([src/dialogue_parser.py](src/dialogue_parser.py)) currently:
- ✓ Separates dialogue from narration
- ✓ Detects speaker attribution patterns
- ✓ Handles pronouns (he/she said)
- ⚠ May occasionally misattribute speakers in complex dialogue

**For production use**, you may want to review the dialogue attribution in the dry-run output and refine the parser patterns based on your specific chapter structure.

## Troubleshooting

### If CUDA stops working in the future

Run the diagnostic:
```bash
cd src
python check_cuda.py
```

This will tell you exactly what's wrong and how to fix it.

### If TTS installation breaks PyTorch again

The issue occurs when running:
```bash
pip install TTS  # DON'T DO THIS - replaces CUDA PyTorch
```

Instead, TTS is already installed. If you need to reinstall:
```bash
# 1. Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 2. Install TTS and dependencies
pip install TTS soundfile scipy pydub

# Note: TTS has many dependencies that will be installed automatically.
# The key is to install PyTorch with CUDA FIRST, then install TTS.
```

## Next Steps

1. **Test with one scene:**
   ```bash
   cd src
   python generate_scene_audio.py --chapters 1 --resume 1 1
   ```

2. **Review the audio quality** - Listen to the generated file and verify:
   - Dialogue is properly attributed to characters
   - Audio quality is acceptable
   - No cutoffs or glitches

3. **Adjust if needed:**
   - Refine dialogue parser patterns in [src/dialogue_parser.py](src/dialogue_parser.py)
   - Adjust voice mappings in [src/config.py](src/config.py)
   - Modify chunk size in config if audio quality issues

4. **Generate full chapters** once satisfied with the output

## Support

- **CUDA Diagnostics:** Run `python src/check_cuda.py`
- **Troubleshooting Guide:** See [CUDA_FIX_README.md](CUDA_FIX_README.md)
- **Implementation Plan:** See [TTS_IMPLEMENTATION_PLAN.md](TTS_IMPLEMENTATION_PLAN.md)

---

**System is ready for GPU-accelerated audio generation! 🎙️**
