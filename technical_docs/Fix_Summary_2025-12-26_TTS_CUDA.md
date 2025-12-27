# TTS CUDA Installation Fix - 2025-12-26

## Problem
Audio generation script (`generate_scene_audio.py`) failed with error:
```
ERROR: Failed to load TTS model
Please install Coqui TTS: pip install TTS
Note: Ensure PyTorch with CUDA is installed first!
```

## Root Cause
- `chatterbox-tts` package was installed instead of Coqui TTS
- PyTorch versions conflicted (chatterbox-tts required 2.6.0, but project needs 2.7.1+cu118)
- NumPy version was too new (2.2.6, needed 1.24-1.25.x range)

## Solution Applied

### 1. Removed Conflicting Packages
```bash
./venv/Scripts/pip uninstall -y torch torchvision torchaudio chatterbox-tts
```

### 2. Reinstalled PyTorch with CUDA 11.8
```bash
./venv/Scripts/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Reinstalled Requirements
```bash
./venv/Scripts/pip install -r requirements.txt
```

This downgraded:
- NumPy from 2.2.6 → 1.25.2 (compatible range)
- NetworkX from 3.6.1 → 2.8.8 (gruut requirement)
- opencv-python-headless from 4.12 → 4.11 (compatibility)

## Verification
```bash
cd src
../venv/Scripts/python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
# Output: CUDA available: True

../venv/Scripts/python -c "from audio_generator import CoquiTTSGenerator; gen = CoquiTTSGenerator(); gen.load_model()"
# Output: [OK] Model loaded successfully! Sample rate: 24000 Hz
```

## Files Modified

### Created
1. **[technical_docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Comprehensive troubleshooting guide for common issues

### Updated
1. **[CLAUDE.md](../../CLAUDE.md)** - Added troubleshooting section and reference to guide, corrected TTS name from "Chatterbox" to "Coqui"

## Current Working Setup
- PyTorch: 2.7.1+cu118
- TorchVision: 0.22.1+cu118
- TorchAudio: 2.7.1+cu118
- NumPy: 1.25.2
- Coqui TTS: 0.22.0
- CUDA: 11.8
- GPU: NVIDIA GeForce RTX 3080

## Important Notes
- NEVER install `chatterbox-tts` - this project uses Coqui TTS (package: `TTS`)
- ALWAYS follow two-step installation process in requirements.txt
- PyTorch MUST be installed with CUDA support BEFORE other packages
- Do NOT omit the `--index-url` flag when installing PyTorch

## References
- [requirements.txt](../../requirements.txt) - Critical installation instructions (lines 1-18)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Full troubleshooting guide
- [audio_generator.py](../../src/audio_generator.py) - TTS model loading code with CUDA diagnostics
