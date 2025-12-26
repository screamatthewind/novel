# Troubleshooting Guide

Common issues and solutions for the novel generation system.

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
