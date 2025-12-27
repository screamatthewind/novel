# Project Directory Structure

## Overview

This document defines the canonical directory structure for "The Obsolescence" novel project. All scripts use centralized path constants from [src/config.py](../../src/config.py).

## Directory Layout

```
novel/
├── .vscode/              # VSCode configuration
├── audio/                # Generated audio files (TTS)
├── audio_cache/          # Audio metadata cache
├── docs/
│   ├── manuscript/       # Chapter markdown files (source)
│   ├── reference/        # Novel Bible and Outline (source)
│   └── project/          # Project documentation
├── images/               # Generated scene images
├── logs/                 # Generation logs
├── prompt_cache/         # Cached image prompts
├── src/                  # Python scripts (source)
├── temp/                 # Temporary files (auto-created, auto-cleaned)
├── venv/                 # Python virtual environment
├── videos/               # Generated YouTube videos
└── voices/               # Voice sample files for TTS (source)
```

## Directory Definitions

All paths defined in [src/config.py](../../src/config.py):

### Source Directories (Never Auto-Deleted)

| Directory | Constant | Purpose |
|-----------|----------|---------|
| `book/manuscript/` | `CHAPTER_DIR` | Chapter markdown files |
| `voices/` | `VOICES_DIR` | Voice sample WAV files for TTS cloning |
| `src/` | - | Python generation scripts |
| `venv/` | - | Python virtual environment |

### Generated Directories (Can Be Safely Deleted)

| Directory | Constant | Purpose | Created By |
|-----------|----------|---------|------------|
| `audio/` | `AUDIO_DIR` | TTS-generated WAV files | `generate_scene_audio.py` |
| `audio_cache/` | `AUDIO_CACHE_DIR` | Audio metadata JSON files | `generate_scene_audio.py` |
| `images/` | `OUTPUT_DIR` | Scene images (PNG/JPG) | `generate_scene_images.py` |
| `videos/` | `VIDEO_DIR` | Final MP4 videos | `generate_video.py` |
| `logs/` | `LOG_DIR` | Generation logs | All generation scripts |
| `prompt_cache/` | `PROMPT_CACHE_DIR` | Cached image prompts | `generate_scene_images.py` |
| `temp/` | `TEMP_DIR` | Temporary files | `generate_video.py`, voice download scripts |

### Cache Directories (Auto-Managed)

| Directory | Purpose | Auto-Created By |
|-----------|---------|-----------------|
| `.cache/` | General cache | Various libraries |
| `huggingface/` | HuggingFace model cache | Transformers library |
| `__pycache__/` | Python bytecode | Python interpreter |

## File Patterns

### .gitkeep Files

All generated directories contain `.gitkeep` files to preserve directory structure in git:
- `audio/.gitkeep`
- `audio_cache/.gitkeep`
- `images/.gitkeep`
- `videos/.gitkeep`
- `logs/.gitkeep`
- `prompt_cache/.gitkeep`
- `temp/.gitkeep`

### Generated File Patterns

Per [.gitignore](../../.gitignore):

```
audio/*.wav, audio/*.mp3
audio_cache/*.json
images/*.png, images/*.jpg, images/*.jpeg
videos/*.mp4, videos/*.avi, videos/*.mov
logs/*.log
prompt_cache/*.txt
temp/*
```

## Script Usage

### Image Generation
Uses: `OUTPUT_DIR`, `LOG_DIR`, `PROMPT_CACHE_DIR`
```bash
./venv/Scripts/python src/generate_scene_images.py --chapters 1
```

### Audio Generation
Uses: `AUDIO_DIR`, `AUDIO_CACHE_DIR`, `LOG_DIR`, `VOICES_DIR`
```bash
./venv/Scripts/python src/generate_scene_audio.py --chapters 1
```

### Video Generation
Uses: `VIDEO_DIR`, `TEMP_DIR`, `AUDIO_DIR`, `OUTPUT_DIR`
```bash
./venv/Scripts/python src/generate_video.py --chapter 1
```

### Cleanup
Cleans: All generated directories while preserving `.gitkeep` files
```bash
./venv/Scripts/python src/cleanup.py --dry-run
```

## Adding New Directories

When adding a new generated directory:

1. **Define in config.py**:
   ```python
   NEW_DIR = "../new_directory"
   os.makedirs(NEW_DIR, exist_ok=True)
   ```

2. **Update .gitignore**:
   ```
   new_directory/*
   !new_directory/.gitkeep
   ```

3. **Create .gitkeep**:
   ```bash
   touch new_directory/.gitkeep
   ```

4. **Update cleanup.py**:
   ```python
   CLEANUP_TARGETS = {
       'new_directory': ['*.ext'],
   }
   ```

5. **Update this document** with the new directory details

## Consistency Rules

1. **ALWAYS use config.py constants** - Never hardcode paths in scripts
2. **ALWAYS preserve .gitkeep files** - Required for git structure
3. **ALWAYS update all 4 locations** when adding directories:
   - `config.py` (define constant)
   - `.gitignore` (exclude generated files)
   - `cleanup.py` (add to cleanup targets)
   - This documentation

## Related Documentation

- [cleanup_utility.md](cleanup_utility.md) - Detailed cleanup utility documentation
- [src/config.py](../../src/config.py) - Central configuration file
- [.gitignore](../../.gitignore) - Git ignore patterns
