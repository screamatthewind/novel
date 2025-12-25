# CUDA Device Detection Fix

## Problem Identified

The TTS audio generator was reporting "device is cpu" because **PyTorch was installed without CUDA support**.

Running the diagnostic showed:
```
PyTorch installed: 2.9.1+cpu
CUDA available: False
```

The "+cpu" suffix indicates this is a CPU-only build of PyTorch.

## Root Cause

When you installed PyTorch with:
```bash
pip install torch
```

This installs the CPU-only version by default. To get CUDA support, you need to specify the CUDA index URL.

## Solution

### Step 1: Check Your Current Setup
Run the diagnostic script:
```bash
cd src
python check_cuda.py
```

This will tell you:
- Whether PyTorch is installed with CUDA support
- Your GPU details if CUDA is available
- Specific instructions if CUDA is not available

### Step 2: Reinstall PyTorch with CUDA Support

If the diagnostic shows PyTorch without CUDA:

1. **Uninstall current PyTorch:**
   ```bash
   pip uninstall torch torchvision torchaudio
   ```

2. **Reinstall with CUDA 11.8 support:**
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

   **Note:** This matches the installation instructions in `requirements.txt` (lines 1-2).

3. **Install TTS dependencies (if not already installed):**
   ```bash
   pip install TTS soundfile scipy pydub
   ```

   **Important:** Do NOT run `pip install TTS` by itself, as it may replace your CUDA PyTorch with the CPU version. If TTS is already installed, you're good to go.

4. **Verify the installation:**
   ```bash
   python check_cuda.py
   ```

   You should now see:
   ```
   [OK] PyTorch installed: 2.9.1+cu118
   CUDA available: True
   Device 0: NVIDIA GeForce RTX 3080
   ```

### Step 3: Test Audio Generation

Once CUDA is detected, test the audio generation:

```bash
# Dry run to verify dialogue parsing
python generate_scene_audio.py --chapters 1 --dry-run

# Generate audio for first scene only
python generate_scene_audio.py --chapters 1 --resume 1 1
```

## What Was Fixed

### Enhanced Diagnostics ([src/audio_generator.py](src/audio_generator.py))

1. **Added `check_cuda_availability()` function** (lines 16-40)
   - Detects why CUDA is unavailable
   - Provides specific error messages
   - Suggests remediation steps

2. **Improved `__init__()` method** (lines 49-79)
   - Shows clear diagnostic messages
   - Warns when falling back to CPU
   - Confirms when CUDA is detected

3. **Enhanced `load_model()` logging** (lines 81-118)
   - Verifies model device matches expected device
   - Shows detailed error traces
   - Confirms successful loading

### New Diagnostic Tool ([src/check_cuda.py](src/check_cuda.py))

A standalone script to check PyTorch and CUDA setup before running audio generation.

## Performance Impact

- **With CUDA (RTX 3080):** ~2.5-3 minutes per 500-word scene
- **With CPU only:** ~15-20 minutes per 500-word scene (5-7x slower)

For your novel with ~15 scenes across 4 chapters:
- **CUDA:** ~40-60 minutes total
- **CPU:** ~4-5 hours total

## Verification

After reinstalling PyTorch with CUDA, you should see output like:

```
CUDA detected: NVIDIA GeForce RTX 3080 (CUDA 11.8)

Loading TTS model: tts_models/multilingual/multi-dataset/xtts_v2
Target device: cuda
Model device: cuda:0
[OK] Model loaded successfully! Sample rate: 24000 Hz
```

## Troubleshooting

### If CUDA is still not detected after reinstalling:

1. **Check NVIDIA drivers:**
   ```bash
   nvidia-smi
   ```
   This should show your RTX 3080 and driver version.

2. **Verify driver supports CUDA 11.8:**
   - CUDA 11.8 requires driver version 450.80.02 or newer
   - Your RTX 3080 should support this

3. **Try different CUDA version:**
   If your drivers are older:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
   ```

4. **Check PyTorch version after installation:**
   ```python
   import torch
   print(torch.__version__)  # Should show "+cu118" or "+cu117", NOT "+cpu"
   ```

## Additional Resources

- PyTorch CUDA installation: https://pytorch.org/get-started/locally/
- NVIDIA driver download: https://www.nvidia.com/download/index.aspx
- CUDA compatibility: https://docs.nvidia.com/deploy/cuda-compatibility/
