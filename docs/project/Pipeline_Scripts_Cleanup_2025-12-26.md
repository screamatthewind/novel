# Pipeline Scripts Cleanup - December 26, 2025

## Summary

Cleaned up redundant `run_full_pipeline` scripts from 4 files down to 2.

---

## Files Removed

### 1. run_full_pipeline.sh (Root Directory)
**Reason**: Redundant with better version in src/

**Issues**:
- Hardcoded to run all chapters (no flexibility)
- Activated venv with `source venv/Scripts/activate` (Windows-specific path in bash script)
- Always enabled `--enable-smart-detection` and `--enable-ip-adapter` (no choice)
- Less user-friendly than interactive version

### 2. src/run_full_pipeline.py
**Reason**: Redundant with shell script versions

**Issues**:
- Hardcoded to run all chapters (no flexibility)
- Always enabled `--enable-smart-detection` and `--enable-ip-adapter` (no choice)
- No interactive prompts or cleanup options
- Shell scripts are more standard for pipeline orchestration

---

## Files Kept

### 1. src/run_full_pipeline.bat ✅
**Platform**: Windows (CMD/PowerShell)

**Features**:
- ✅ Interactive chapter selection (or all)
- ✅ Runs cleanup step with --yes flag
- ✅ Confirmation prompt before starting
- ✅ Clear progress messages
- ✅ Error handling with exit codes
- ✅ Summary of output locations

**Usage**:
```cmd
cd src
run_full_pipeline.bat
```

### 2. src/run_full_pipeline.sh ✅
**Platform**: Linux/macOS/Git Bash (Bash)

**Features**:
- ✅ Interactive chapter selection (or all)
- ✅ Optional cleanup step (user choice)
- ✅ Confirmation prompt before starting
- ✅ Clear progress messages
- ✅ Error handling with `set -e`
- ✅ Summary of output locations

**Usage**:
```bash
cd src
./run_full_pipeline.sh
```

---

## Why These Versions Are Better

### Interactive Chapter Selection
```
Enter chapter numbers to process (e.g., 1 2 3) or press Enter for all:
> 1 2 3
```

Users can:
- Generate specific chapters only
- Test pipeline on small subset
- Regenerate single chapters

### Optional Cleanup
```bash
Cleanup existing generated files before starting? (y/N):
```

Users can:
- Choose to keep existing files
- Overwrite as needed per step
- Or start completely fresh

### Smart Confirmations
```
Selected: Chapters 1 2 3
Continue with full pipeline for chapters 1 2 3? (y/N):
```

Prevents accidental:
- Full pipeline runs
- File deletions
- Long processing jobs

---

## Pipeline Steps

Both scripts run the same 4-step pipeline:

1. **Cleanup** (optional) - Delete existing generated files
   ```bash
   python cleanup.py --yes
   ```

2. **Generate Images** - Create scene images
   ```bash
   python generate_scene_images.py --chapters [CHAPTERS]
   ```

3. **Generate Audio** - Create scene audio
   ```bash
   python generate_scene_audio.py --chapters [CHAPTERS]
   ```

4. **Generate Video** - Create final video
   ```bash
   python generate_video.py --chapters [CHAPTERS]
   # or: --all for all chapters
   ```

---

## Migration Notes

If you were using the old scripts:

**Before (root/run_full_pipeline.sh)**:
```bash
./run_full_pipeline.sh  # No options, always all chapters
```

**After (src/run_full_pipeline.sh)**:
```bash
cd src
./run_full_pipeline.sh
# Then: Interactive prompts for chapter selection
```

**Before (src/run_full_pipeline.py)**:
```bash
cd src
python run_full_pipeline.py  # No options, always all chapters
```

**After (src/run_full_pipeline.bat or .sh)**:
```bash
cd src
./run_full_pipeline.sh  # (or .bat on Windows)
# Then: Interactive prompts for chapter selection
```

---

## Remaining Pipeline Files

After cleanup:

```
src/
├── run_full_pipeline.bat    ✅ Windows version (interactive)
└── run_full_pipeline.sh     ✅ Bash version (interactive)
```

Both files serve the same purpose but for different platforms.

---

## Related Documentation

- **Pipeline Usage**: See scripts themselves for inline documentation
- **Individual Scripts**:
  - `generate_scene_images.py` - Image generation
  - `generate_scene_audio.py` - Audio generation
  - `generate_video.py` - Video generation
  - `cleanup.py` - File cleanup utility

---

**Date**: 2025-12-26
**Status**: ✅ Cleanup complete
