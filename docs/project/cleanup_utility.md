# Cleanup Utility

## Overview
Python script to safely delete all generated files (audio, images, videos, logs, caches) to enable clean regeneration from scratch.

## Location
- Script: [src/cleanup.py](../../src/cleanup.py)
- Launch configs: [.vscode/launch.json](../../.vscode/launch.json) (lines 414-455)

## What Gets Deleted
- `audio/*.wav` - TTS-generated audio files
- `audio_cache/*.json` - Audio metadata cache
- `images/*.{png,jpg,jpeg}` - Generated scene images
- `videos/*.{mp4,avi,mov}` - Generated videos
- `logs/*.log` - Generation logs
- `prompt_cache/*.txt` - Cached image prompts
- `temp/` - Temporary directory (MoviePy/FFmpeg)
- `__pycache__/` - Python bytecode (root and src/ only, excludes venv/)
- `.cache/` - Cache directory
- `huggingface/` - HuggingFace cache

## What Gets Preserved
- `.gitkeep` files (maintains directory structure)
- `voices/` - Voice sample files (source assets)
- `.env` - Environment variables
- `venv/` - Python virtual environment
- `src/` - All Python scripts (source code)
- `docs/` - All manuscript and reference files
- `.vscode/` - VSCode configuration

## Usage

```bash
# Preview what will be deleted (ALWAYS RUN THIS FIRST)
./venv/Scripts/python src/cleanup.py --dry-run

# Execute cleanup with confirmation prompt
./venv/Scripts/python src/cleanup.py

# Execute without confirmation (dangerous!)
./venv/Scripts/python src/cleanup.py --yes

# Verbose mode (see each file)
./venv/Scripts/python src/cleanup.py --verbose
```

## VSCode Launch Configurations

Three debug configurations available:
1. **Cleanup: Dry Run** - Safe preview mode
2. **Cleanup: Execute** - With confirmation prompt
3. **Cleanup: Execute (No Confirmation)** - Immediate deletion

## Directory Structure

All generated file directories are defined in [src/config.py](../../src/config.py) and match [.gitignore](../../.gitignore) patterns:

| Directory | Purpose | Defined in config.py |
|-----------|---------|---------------------|
| `audio/` | TTS-generated audio files | `AUDIO_DIR` |
| `audio_cache/` | Audio metadata cache | `AUDIO_CACHE_DIR` |
| `images/` | Generated scene images | `OUTPUT_DIR` |
| `videos/` | Generated YouTube videos | `VIDEO_DIR` |
| `logs/` | Generation logs | `LOG_DIR` |
| `prompt_cache/` | Cached image prompts | `PROMPT_CACHE_DIR` |
| `temp/` | Temporary files | `TEMP_DIR` |

All directories contain `.gitkeep` files to preserve structure in git.

## Consistency Across Scripts

All Python scripts use the constants defined in `config.py` for directory paths:
- [generate_scene_images.py](../../src/generate_scene_images.py) - Uses `OUTPUT_DIR`, `LOG_DIR`, `PROMPT_CACHE_DIR`
- [generate_scene_audio.py](../../src/generate_scene_audio.py) - Uses `AUDIO_DIR`, `AUDIO_CACHE_DIR`, `LOG_DIR`
- [generate_video.py](../../src/generate_video.py) - Uses `VIDEO_DIR`, `TEMP_DIR`
- [cleanup.py](../../src/cleanup.py) - Cleans all directories consistently

## Safety Features
- Confirmation prompt (unless --yes flag used)
- Dry-run mode to preview deletions
- Preserves .gitkeep files
- Excludes venv directory from __pycache__ cleanup
- Error handling for permission issues
- Statistics summary before deletion

## After Cleanup
All generation directories will remain with .gitkeep files intact. Ready to regenerate all content from scratch using existing generation scripts.
