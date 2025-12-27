---
paths: "{src/**/*.py,*.py}"
---

# Python Environment

**CRITICAL: ALWAYS use the virtual environment for ALL Python commands**

## Running Python Scripts

All Python scripts MUST be run using the virtual environment Python interpreter:

```bash
# From project root
./venv/Scripts/python src/script_name.py

# Or from src/ directory
cd src
../venv/Scripts/python script_name.py
```

## Installing Packages

Always install packages into the virtual environment:

```bash
./venv/Scripts/pip install package_name
```

## Available Scripts

1. **Image Generation**: `src/generate_scene_images.py` - Generate scene images using Stable Diffusion XL
2. **Audio Generation**: `src/generate_scene_audio.py` - Generate scene audio using Coqui TTS
3. **Video Generation**: `src/generate_video.py` - Generate YouTube videos from images and audio
4. **Scene Parser**: `src/scene_parser.py` - Parse chapters into scenes

## Running Scripts

```bash
cd src

# Image generation
../venv/Scripts/python generate_scene_images.py --chapters 1

# Audio generation
../venv/Scripts/python generate_scene_audio.py --chapters 1

# Video generation
../venv/Scripts/python generate_video.py --chapter 1
../venv/Scripts/python generate_video.py --chapters 1 2 3 --combine
```

**Note**: Scripts use relative paths from `src/` directory, so always run from `src/` or adjust paths accordingly.

## Troubleshooting

If you encounter installation or runtime errors, refer to:
- [docs/project/TROUBLESHOOTING.md](docs/project/TROUBLESHOOTING.md) - Common issues and solutions
- [requirements.txt](requirements.txt) - Critical installation order and warnings (lines 1-18)

**Most Common Issue:** TTS model loading error
- **Cause:** PyTorch installed without CUDA support or chatterbox-tts installed instead of Coqui TTS
- **Solution:** See TROUBLESHOOTING.md for step-by-step fix

## CRITICAL: launch.json Updates

**ALWAYS add launch configurations to `.vscode/launch.json` when creating new Python scripts.** This is a required step for all new scripts.
