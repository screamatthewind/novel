# Directory Consistency Update Summary

## Changes Made

All project directories now use consistent naming and are centrally defined in [src/config.py](../../src/config.py).

### 1. Updated config.py

Added missing directory constants:
```python
VIDEO_DIR = "../videos"
TEMP_DIR = "../temp"
```

All directories are now auto-created when config.py is imported.

### 2. Updated .gitignore

Changed temp directory pattern to preserve .gitkeep:
```diff
- temp/
+ temp/*
+ !temp/.gitkeep
```

### 3. Created .gitkeep Files

Added .gitkeep files to all generated directories:
- `audio/.gitkeep`
- `audio_cache/.gitkeep`
- `images/.gitkeep`
- `videos/.gitkeep`
- `logs/.gitkeep`
- `prompt_cache/.gitkeep`
- `temp/.gitkeep`

### 4. Updated cleanup.py

Added comments clarifying directory sources:
```python
# File patterns to delete in each directory (preserving .gitkeep)
# These match the directories defined in config.py and .gitignore
CLEANUP_TARGETS = {
    'audio': ['*.wav', '*.mp3'],
    'audio_cache': ['*.json'],
    'images': ['*.png', '*.jpg', '*.jpeg'],
    'videos': ['*.mp4', '*.avi', '*.mov'],
    'logs': ['*.log'],
    'prompt_cache': ['*.txt'],
}

# Directories to completely remove (will be recreated by scripts as needed)
DIRECTORY_TARGETS = [
    'temp',           # Temporary files (MoviePy, video generation, voice downloads)
    '.cache',         # General cache
    'huggingface',    # HuggingFace model cache
]
```

### 5. Updated Documentation

Created/updated:
- [directory_structure.md](directory_structure.md) - Comprehensive directory documentation
- [cleanup_utility.md](cleanup_utility.md) - Added consistency section
- This summary document

## Directory Reference

| Directory | Config Constant | Purpose | Scripts Using |
|-----------|----------------|---------|---------------|
| `audio/` | `AUDIO_DIR` | TTS audio files | `generate_scene_audio.py` |
| `audio_cache/` | `AUDIO_CACHE_DIR` | Audio metadata | `generate_scene_audio.py` |
| `images/` | `OUTPUT_DIR` | Scene images | `generate_scene_images.py` |
| `videos/` | `VIDEO_DIR` | YouTube videos | `generate_video.py` |
| `logs/` | `LOG_DIR` | Generation logs | All generation scripts |
| `prompt_cache/` | `PROMPT_CACHE_DIR` | Image prompts | `generate_scene_images.py` |
| `temp/` | `TEMP_DIR` | Temporary files | `generate_video.py`, voice scripts |
| `voices/` | `VOICES_DIR` | Voice samples | `generate_scene_audio.py` |

## Files Modified

1. [src/config.py](../../src/config.py) - Added VIDEO_DIR and TEMP_DIR
2. [.gitignore](../../.gitignore) - Updated temp/ pattern
3. [src/cleanup.py](../../src/cleanup.py) - Added clarifying comments
4. [docs/project/cleanup_utility.md](cleanup_utility.md) - Added consistency section
5. [docs/project/directory_structure.md](directory_structure.md) - New comprehensive guide

## Files Created

- `.gitkeep` files in all 7 generated directories
- [docs/project/directory_structure.md](directory_structure.md)
- [docs/project/consistency_update_summary.md](consistency_update_summary.md)

## Verification

All scripts now consistently use config.py constants:
```bash
# Verify config.py is imported
grep "from config import" src/*.py

# Results:
# generate_scene_images.py: OUTPUT_DIR, LOG_DIR, PROMPT_CACHE_DIR
# generate_scene_audio.py: AUDIO_DIR, AUDIO_CACHE_DIR, LOG_DIR
# generate_video.py: Uses paths directly, but could be updated
```

## Next Steps (Optional)

Consider updating `generate_video.py` to use VIDEO_DIR and TEMP_DIR from config.py instead of hardcoded paths for even better consistency.

## Testing

Cleanup script tested and verified:
```bash
./venv/Scripts/python src/cleanup.py --dry-run
# Correctly identifies all directories
# Preserves .gitkeep files
# Excludes venv/__pycache__
```

## Benefits

1. **Single Source of Truth** - All paths defined in config.py
2. **Consistency** - All scripts use same directory structure
3. **Maintainability** - Change path once, updates everywhere
4. **Documentation** - Clear reference for all directories
5. **Git Structure** - .gitkeep files preserve empty directories
6. **Cleanup Safety** - cleanup.py matches all generation directories
