# Installation Guide - TTS Audio Generation System

## Complete Setup Instructions

This guide covers the complete installation process for both image generation and TTS audio generation systems.

## Prerequisites

- **GPU**: NVIDIA GPU with CUDA support (RTX 3080 recommended)
- **Python**: Python 3.11 (tested version)
- **NVIDIA Drivers**: Version 450.80.02 or newer
- **Windows**: Tested on Windows 10/11 with MSYS/Git Bash

## Installation Steps

### Step 1: Install PyTorch with CUDA Support

**CRITICAL:** Install PyTorch with CUDA support BEFORE installing any other packages.

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verify Installation:**
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

**Expected output:**
```
PyTorch: 2.7.1+cu118
CUDA: True
```

If you see `+cpu` instead of `+cu118`, or if CUDA shows `False`, **STOP** and run the diagnostic:
```bash
cd src
python check_cuda.py
```

### Step 2: Install Other Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Image generation: diffusers, transformers, accelerate, safetensors, Pillow
- Audio generation: TTS, soundfile, scipy, pydub
- Common: numpy<2.0, tqdm

### Step 3: Install xformers (Optional, for Image Generation)

For faster image generation:

```bash
pip install xformers
```

**Note:** xformers must match your PyTorch version. If you get version conflicts, skip this step.

### Step 4: Verify Installation

Run the CUDA diagnostic:
```bash
cd src
python check_cuda.py
```

**Expected output:**
```
======================================================================
PyTorch & CUDA Diagnostic Tool
======================================================================

[OK] PyTorch installed: 2.7.1+cu118

CUDA available: True

======================================================================
CUDA IS AVAILABLE
======================================================================

PyTorch CUDA version: 11.8
CUDA device count: 1

Device 0:
  Name: NVIDIA GeForce RTX 3080
  Total memory: 10.0 GB
  Compute capability: 8.6

======================================================================
Testing CUDA Operations
======================================================================

[OK] CUDA test successful!
  Test tensor on device: cuda:0
  Computation result: [2. 4. 6.]

======================================================================
Summary
======================================================================
[OK] Your system is ready for GPU-accelerated audio generation!
  You can now run: python generate_scene_audio.py
======================================================================
```

## Common Issues

### Issue 1: PyTorch Installed Without CUDA

**Symptom:**
```
PyTorch: 2.9.1+cpu
CUDA available: False
```

**Cause:** You ran `pip install torch` or `pip install TTS` which installed CPU-only PyTorch.

**Fix:**
```bash
# 1. Uninstall PyTorch
pip uninstall torch torchvision torchaudio

# 2. Reinstall with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Verify
python check_cuda.py
```

### Issue 2: TTS Breaks PyTorch CUDA

**Symptom:** After running `pip install TTS`, PyTorch changes from `+cu118` to `+cpu`.

**Why:** TTS has a flexible PyTorch dependency that allows pip to "upgrade" to a newer CPU-only version.

**Prevention:**
1. Always install PyTorch with CUDA FIRST
2. Never run `pip install TTS` by itself
3. Use `pip install -r requirements.txt` which includes all dependencies

**Fix if it happens:**
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue 3: CUDA Drivers Not Detected

**Symptom:**
```
PyTorch: 2.7.1+cu118
CUDA available: False
Reason: CUDA drivers not detected or incompatible
```

**Fix:**
1. Check drivers are installed:
   ```bash
   nvidia-smi
   ```
2. Update NVIDIA drivers from: https://www.nvidia.com/download/index.aspx
3. Ensure driver version supports CUDA 11.8 (450.80.02+)

### Issue 4: Version Conflicts

**Symptom:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
xformers 0.0.27.post2+cu118 requires torch==2.4.0, but you have torch 2.7.1+cu118
```

**Fix:** These warnings are usually safe to ignore. The packages will work despite version mismatches. If you encounter actual errors, uninstall the conflicting package:
```bash
pip uninstall xformers
```

## Reinstallation from Scratch

If you need to start fresh:

```bash
# 1. Uninstall everything
pip uninstall torch torchvision torchaudio TTS diffusers transformers -y

# 2. Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Verify CUDA
cd src
python check_cuda.py

# 4. Install remaining dependencies
cd ..
pip install -r requirements.txt

# 5. Final verification
cd src
python check_cuda.py
```

## Testing Your Installation

### Test 1: Image Generation (if needed)
```bash
cd src
python generate_scene_images.py --dry-run
```

### Test 2: Audio Generation Dry Run
```bash
cd src
python generate_scene_audio.py --chapters 1 --dry-run
```

This tests:
- ✓ Scene parsing works
- ✓ Dialogue extraction works
- ✓ Filename generation works
- ✓ No actual TTS model loading (fast)

### Test 3: Audio Generation (One Scene)
```bash
python generate_scene_audio.py --chapters 1 --resume 1 1
```

This tests:
- ✓ TTS model downloads (~2GB first time)
- ✓ CUDA acceleration works
- ✓ Audio generation completes
- ✓ File is saved correctly

**Expected:** ~2-3 minutes on RTX 3080 with CUDA, ~15-20 minutes on CPU.

## Directory Structure After Installation

```
novel/
├── src/                     # Python scripts
├── docs/                    # Novel chapters and reference
├── images/                  # Generated scene images
├── audio/                   # Generated scene audio (created on first run)
├── audio_cache/             # Dialogue parsing cache (created on first run)
├── voices/                  # Voice reference files (created, initially empty)
├── logs/                    # Generation logs
├── prompt_cache/            # Image prompt cache
├── requirements.txt         # Dependencies
└── venv/                    # Virtual environment (if using one)
```

## Performance Expectations

### With CUDA (RTX 3080)
- **Image generation:** ~4-6 minutes per scene
- **Audio generation:** ~2-3 minutes per 500-word scene
- **Full chapter (4 scenes):**
  - Images: ~20-30 minutes
  - Audio: ~10-15 minutes

### Without CUDA (CPU fallback)
- **Image generation:** Not recommended (very slow)
- **Audio generation:** ~15-20 minutes per scene
- **Full chapter:** ~1+ hour for audio alone

## Getting Help

1. **CUDA Issues:** Run `python src/check_cuda.py` for diagnostics
2. **Installation Issues:** See [CUDA_FIX_README.md](CUDA_FIX_README.md)
3. **Usage Guide:** See [TTS_SETUP_COMPLETE.md](TTS_SETUP_COMPLETE.md)
4. **Implementation Details:** See [TTS_IMPLEMENTATION_PLAN.md](TTS_IMPLEMENTATION_PLAN.md)

## Quick Reference

### Essential Commands
```bash
# Check CUDA status
python src/check_cuda.py

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Generate audio (dry run)
python src/generate_scene_audio.py --chapters 1 --dry-run

# Generate audio (one scene)
python src/generate_scene_audio.py --chapters 1 --resume 1 1

# Generate audio (full chapter)
python src/generate_scene_audio.py --chapters 1
```

### Important URLs
- PyTorch CUDA installation: https://pytorch.org/get-started/locally/
- NVIDIA drivers: https://www.nvidia.com/download/index.aspx
- CUDA compatibility: https://docs.nvidia.com/deploy/cuda-compatibility/
