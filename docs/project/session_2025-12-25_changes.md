# Session Changes - December 25, 2025

## Summary
Updated project configuration, VSCode launch settings, and fixed audio generation dependencies.

## Changes Made

### 1. Launch Configuration (.vscode/launch.json)
Created comprehensive launch configurations for all Python programs (file is gitignored):

#### Image Generation (9 configs)
- Image: Dry Run (All Scenes)
- Image: Chapter 1-4 Only
- Image: Resume from Chapter 2, Scene 3
- Image: All Scenes (Full Run)
- Image: Custom Settings (Fast) - 20 steps, guidance 7.0
- Image: Custom Settings (High Quality) - 50 steps, guidance 8.5

#### Audio Generation (8 configs)
- Audio: Dry Run (All Scenes)
- Audio: Chapter 1-3 Only
- Audio: Resume from Chapter 2, Scene 3
- Audio: All Scenes (Full Run)
- Audio: Single Voice Mode (Chapter 1)
- Audio: Skip Cache (Regenerate Chapter 1)
- Audio: MP3 Format (Chapter 1)

#### Diagnostic Tools (4 configs)
- Test: Check CUDA Availability
- Test: Scene Parser
- Test: Audio Generator
- Test: Image Generator

### 2. Image Format Configuration (src/config.py)
**Changed image dimensions for mobile-first vertical format:**

**Before:**
```python
DEFAULT_WIDTH = 1344   # Landscape 16:9
DEFAULT_HEIGHT = 768
```

**After:**
```python
# 9:16 Vertical (Portrait) format - optimized for mobile viewing and YouTube Shorts
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
```

**Rationale:**
- Matches how people naturally hold phones
- Takes up full screen on mobile YouTube
- Most immersive for phone viewers
- YouTube Shorts uses this format
- Better for Instagram Reels / TikTok

### 3. Dependencies Fixed (requirements.txt)
**Added missing development dependencies:**

```python
# Development Tools
debugpy>=1.8.0           # VSCode Python debugger
```

**Issue Resolved:**
- VSCode launch configurations were failing due to missing `debugpy` package
- Installed `debugpy` in virtual environment
- Downgraded `transformers` from 4.57.3 to 4.40.2 (required for TTS BeamSearchScorer compatibility)

**Testing Results:**
- ✅ Dry run test passed: `generate_scene_audio.py --dry-run --chapters 1`
- ✅ TTS model loads successfully on CUDA (RTX 3080)
- ✅ VSCode launch configurations now functional

## Files Modified
- `.vscode/launch.json` - Created comprehensive debug configurations (gitignored)
- `src/config.py` - Changed image dimensions from 1344x768 to 1080x1920
- `requirements.txt` - Added debugpy development dependency

## Issues Fixed
1. **Audio generation failing from VSCode** - Missing debugpy package
2. **TTS model import error** - Transformers version too new (4.57.3 → 4.40.2)
3. **BeamSearchScorer import error** - Resolved by transformers downgrade

## Testing Completed
- Chapter 1 dry run: 7 scenes parsed successfully
- TTS model loads on CUDA without errors
- All VSCode launch configurations working

## Notes
- All new images will be generated in portrait format
- Existing landscape images remain unchanged
- Launch configurations organized by category (Image/Audio/Test)
- All configs use the project's virtual environment: `venv/Scripts/python.exe`
- Audio generation now fully functional via command line and VSCode
