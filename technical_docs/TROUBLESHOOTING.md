# Troubleshooting Guide

Common issues and solutions for the novel generation system.

## Inconsistent Clothing/Appearance Between Sentences (FIXED 2025-12-27)

**Symptoms:**
- Character clothing colors/styles change randomly between consecutive sentences in the same scene
- Emma appears in different outfits from sentence to sentence (navy blazer → gray sweater → etc.)
- Inconsistent visual appearance despite using storyboard mode

**Root Cause:**
Character name mismatch between storyboard analyzer (returns "Emma Chen") and canonical attributes dictionary (uses "emma"). This caused:
1. Attribute lookups to fail → `char_state` was `None`
2. Fallback returned character name instead of description
3. No clothing info in prompts → SDXL generated random clothing

**Solution (Applied):**
Fixed in commit 2025-12-27:
- Added `normalize_character_name()` function in [src/prompt_generator.py](../src/prompt_generator.py)
- Enhanced `to_compressed_string()` to always include clothing (even at extreme compression)
- Fixed dry-run mode to pass `attribute_manager` parameter
- All prompts now include: "mid-40s Asian American woman, intelligent brown eyes, analytical expression, navy blue blazer white shirt black"

**To Apply Fix to Existing Images:**
```bash
cd src
../venv/Scripts/python.exe generate_scene_images.py --chapters 1 --rebuild-storyboard
```

This deletes old cache/images and regenerates with consistent clothing.

## TTS Model Loading Error

**Error Message:**
```
ERROR: Failed to load TTS model
Please install Coqui TTS: pip install TTS
Note: Ensure PyTorch with CUDA is installed first!
```

**Root Cause:**
PyTorch was installed without CUDA support, or conflicting package (chatterbox-tts) was installed instead of Coqui TTS.

**Solution:**

1. Uninstall conflicting packages:
```bash
./venv/Scripts/pip uninstall -y torch torchvision torchaudio chatterbox-tts
```

2. Reinstall PyTorch with CUDA 11.8 FIRST:
```bash
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. Reinstall requirements:
```bash
./venv/Scripts/pip install -r requirements.txt
```

4. Verify installation:
```bash
cd src
../venv/Scripts/python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Important:**
- NEVER install TTS before PyTorch+CUDA
- NEVER install PyTorch without the `--index-url` flag
- The project uses Coqui TTS (package name: `TTS`), NOT chatterbox-tts
- Working versions: PyTorch 2.7.1+cu118, NumPy 1.24-1.25.x

## CUDA Out of Memory (OOM)

**Symptoms:**
- Script crashes with CUDA OOM error during image generation
- VRAM usage exceeds GPU capacity

**Solutions:**
- Verify face encoder is on CPU (check generation logs)
- Reduce batch size or image resolution
- Disable IP-Adapter temporarily with `--enable-ip-adapter` flag omitted
- Close other GPU-intensive applications

## Character Not Detected

**Symptoms:**
- Character references not being used for scenes where character appears

**Solution:**
- Check character name mapping in `src/generate_scene_images.py` (lines 251-258)
- Add character name variations if needed
- Verify character metadata.json exists in character references directory

## Audio Generation Issues

**Missing voice files:**
- Ensure voice sample files exist in `voices/` directory
- Check `src/voice_config.py` for correct file paths

**Audio quality issues:**
- Verify sample rate is 24000 Hz (XTTS v2 default)
- Check voice reference files are clear, high-quality WAV files
- Avoid background noise in voice samples

## Video Generation Issues

**MoviePy errors:**
- Ensure FFmpeg is available (installed via imageio-ffmpeg)
- Check that all required audio and image files exist
- Verify temp directory is writable

## General Installation Issues

**Package conflicts:**
- Always follow the two-step installation in requirements.txt
- Uninstall conflicting packages before reinstalling
- Use virtual environment exclusively (`./venv/Scripts/...`)

**Version mismatches:**
- Check requirements.txt for exact version constraints
- Some packages (numpy, torch) must match specific version ranges
- Use `pip list` to verify installed versions

---

Last updated: 2025-12-26
