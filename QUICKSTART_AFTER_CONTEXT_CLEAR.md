# Quick Start After Context Clear

## Current Status: ✅ TTS SYSTEM READY

All bugs fixed. System is fully functional with CUDA acceleration (RTX 3080).

## What Was Fixed (Dec 24, 2025)

1. ✅ MeCab error - installed unidic-lite dictionary
2. ✅ PyTorch 2.6 security - patched TTS to use weights_only=False
3. ✅ Transformers incompatibility - downgraded to 4.40.2
4. ✅ XTTS v2 speaker config - uses default "Claribel Dervla" speaker
5. ✅ Windows console Unicode - replaced symbols with ASCII

See [TTS_FIXES_DEC24.md](TTS_FIXES_DEC24.md) for full details.

## Test the System

### 1. Verify CUDA is working
```bash
cd src
python check_cuda.py
```
Expected: Shows RTX 3080 with CUDA 11.8

### 2. Test TTS model loading
```bash
python audio_generator.py
```
Expected: Generates test audio successfully, saves to `audio/test_generation.wav`

### 3. Test dialogue parsing (dry run)
```bash
python generate_scene_audio.py --chapters 1 --dry-run
```
Expected: Shows parsed dialogue segments without generating audio

### 4. Generate audio for one scene
```bash
python generate_scene_audio.py --chapters 1 --resume 1 1
```
Expected: Generates WAV file in `audio/` directory (~2-3 minutes with GPU)

## If Something Goes Wrong

### MeCab Error Returns
```bash
pip uninstall -y mecab-python3
pip install unidic-lite
pip install mecab-python3
```

### PyTorch weights_only Error
Code in `src/audio_generator.py` lines 89-95 should handle this.
If error persists, check that file wasn't reverted.

### Transformers Import Error
```bash
pip install "transformers<4.41.0"
```

### CUDA Not Detected
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Generate Novel Audio

### Single scene (testing)
```bash
cd src
python generate_scene_audio.py --chapters 1 --resume 1 1
```

### Full chapter
```bash
python generate_scene_audio.py --chapters 1
```

### All chapters
```bash
python generate_scene_audio.py
```

## Output Location

- Audio files: `novel/audio/`
- Dialogue cache: `novel/audio_cache/`
- Logs: `novel/logs/`

## Performance (with RTX 3080)

- ~2-3 minutes per scene (500 words)
- ~10-15 minutes per chapter (4 scenes)
- Real-time factor: ~0.7 (faster than real-time)

## Current Voice Setup

All characters use the default XTTS v2 speaker "Claribel Dervla" because custom voice WAV files don't exist yet.

To add custom voices:
1. Record 10-30 second WAV samples of different voices
2. Save to `voices/` directory with names matching `src/voice_config.py`
3. System will automatically use them for voice cloning

## Key Files Reference

- **Main script:** `src/generate_scene_audio.py`
- **TTS engine:** `src/audio_generator.py` (contains all the fixes)
- **Voice config:** `src/voice_config.py`
- **Dialogue parser:** `src/dialogue_parser.py`
- **Quick reference:** [README_TTS.md](README_TTS.md)
- **Fix details:** [TTS_FIXES_DEC24.md](TTS_FIXES_DEC24.md)

## Modified Files (Don't Revert!)

1. `src/audio_generator.py` - PyTorch 2.6 patch, MeCab suppression, speaker config
2. `src/generate_scene_audio.py` - Windows console Unicode fix
3. `requirements.txt` - Added transformers version constraint

---

**System is ready to generate audio narration for your novel!**
