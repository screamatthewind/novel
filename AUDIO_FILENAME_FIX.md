# Audio/Image Filename Inconsistency - Fix Summary

**Date:** 2025-12-25
**Issue:** Audio and image files had different location tags in filenames
**Status:** ✅ RESOLVED

## Problem

Audio and image files for the same scene had different location tags:
- Image: `chapter_01_scene_01_sent_001_emma_factory.png` ✓ Correct
- Audio: `chapter_01_scene_01_sent_001_emma_kitchen.wav` ✗ Wrong

**Root Cause:** Audio generation didn't pass `scene_context` parameter, so it extracted location from individual sentences instead of the full scene context (like images do).

## Solution Implemented

### 1. Code Changes (2 files modified)

#### File: [src/generate_scene_audio.py](src/generate_scene_audio.py#L130)
Added `scene_context=sentence.scene_context` parameter to `generate_audio_filename()` call.

#### File: [src/audio_filename_generator.py](src/audio_filename_generator.py#L15)
- Added `scene_context: str = None` parameter to function signature
- Updated to pass `scene_context` to `extract_key_words()` function
- Updated docstring

### 2. New Utility Script Created

#### File: [src/rename_audio_files.py](src/rename_audio_files.py) (NEW)
Script to rename existing audio files to match image filenames.

**Features:**
- `--dry-run` mode for safe testing
- `--chapter N` or `--chapters N M O` for targeted renaming
- Automatically renames cache files (`*_metadata.json`)
- Detects and reports orphan audio files (those without images)
- Comprehensive error handling and statistics

**Usage:**
```bash
# Dry run
python rename_audio_files.py --chapter 1 --dry-run

# Execute rename
python rename_audio_files.py --chapter 1
```

### 3. Pipeline Scripts Created

#### Files: [src/run_full_pipeline.bat](src/run_full_pipeline.bat) and [src/run_full_pipeline.sh](src/run_full_pipeline.sh)
Full automation scripts that run all four generation steps sequentially:
1. Cleanup
2. Image generation
3. Audio generation
4. Video generation

**Features:**
- Single chapter selection prompt at beginning
- Runs to completion without further interruption
- Error handling with informative messages
- Works with specific chapters or all chapters

**Usage:**
```bash
# Windows
cd src
run_full_pipeline.bat

# Unix/Linux/Mac
cd src
./run_full_pipeline.sh
```

## Results

### Chapter 1 Fix (Completed)
- ✅ **106 audio files renamed successfully** (0 errors)
- ✅ **106 cache files renamed successfully**
- ✅ **115/115 image/audio pairs now match perfectly**
- ✅ 9 files already had correct names
- ℹ️ 77 orphan audio files identified (beyond where image generation stopped)

### Backups Created
- 192 audio files: `backups/audio/`
- 192 cache files: `backups/audio_cache/`

## Testing Verification

✓ Code fix dry-run: Generates correct filenames matching images
✓ Rename script dry-run: Correctly identified 106 files to rename
✓ Actual rename: All 106 files + caches renamed with 0 errors
✓ File matching: 115/115 images have matching audio files
✓ Video generation: Can now find all matching file pairs

## Future Behavior

1. **New audio generation** will automatically use correct location tags (matching images)
2. **Orphan audio files** (77 files beyond sentence 115) will be corrected when corresponding images are generated
3. **Video generation** now works properly since all file pairs match

## Files Modified

- [src/generate_scene_audio.py](src/generate_scene_audio.py) - Line 130
- [src/audio_filename_generator.py](src/audio_filename_generator.py) - Lines 15, 36, docstring

## Files Created

- [src/rename_audio_files.py](src/rename_audio_files.py) - NEW utility script
- [src/run_full_pipeline.bat](src/run_full_pipeline.bat) - NEW Windows pipeline script
- [src/run_full_pipeline.sh](src/run_full_pipeline.sh) - NEW Unix pipeline script

## Technical Details

The fix ensures that both image and audio filename generation use the same `extract_key_words()` logic from [src/prompt_generator.py](src/prompt_generator.py). When `scene_context` is provided, the function extracts location from the entire scene text (consistent across all sentences), rather than from individual sentences (which often lack location keywords).

## Notes

- Only Chapter 1 currently has images (115 files), so only Chapter 1 needed renaming
- Future chapters will automatically generate with correct names
- Cache files are properly maintained with consistent naming
- Backups available for rollback if needed
