# Changelog

All notable changes to The Obsolescence novel generation project.

## [2025-12-27] - Character Clothing Consistency Fix

### Fixed
- **Inconsistent clothing/appearance between sentences in same scene**
  - Root cause: Character name mismatch between storyboard analyzer ("Emma Chen") and canonical attributes ("emma")
  - Added `normalize_character_name()` function to handle name variations
  - Enhanced `AttributeStateManager.to_compressed_string()` to always include clothing at all compression levels
  - Fixed dry-run mode to initialize and pass `attribute_manager` parameter
  - Modified compression strategy to use 8-token budget ensuring clothing is included

### Changed
- `src/prompt_generator.py`: Added character name normalization for all lookups
- `src/attribute_state_manager.py`: Enhanced compression to always include clothing
- `src/generate_scene_images.py`: Fixed attribute_manager initialization in dry-run mode

### Impact
- All image prompts now consistently include character clothing descriptions
- Example prompt now includes: "navy blue blazer white shirt black"
- Fixes random clothing changes between consecutive sentences

### Migration
To regenerate existing images with consistent clothing:
```bash
cd src
../venv/Scripts/python.exe generate_scene_images.py --chapters 1 --rebuild-storyboard
```

## [2025-12-25] - Project Initialization

### Added
- Initial novel manuscript (12 chapters)
- Stable Diffusion XL image generation system
- Coqui TTS audio generation system
- MoviePy video generation system
- Storyboard analysis with Claude API
- Character attribute state management
- IP-Adapter FaceID for character consistency
