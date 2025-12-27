# Changelog

All notable changes to The Obsolescence novel generation project.

## [2025-12-27] - Documentation Cleanup

### Changed
- **Cleaned up technical_docs/ folder** (21 files → 11 files, 48% reduction)
  - Removed 10 obsolete files (session summaries, bug fix docs, redundant documentation)
  - Kept core operational guides: PROJECT_STATUS, TROUBLESHOOTING, storyboard docs, phase summaries, cost tracking
  - Updated Character_References_Quick_Guide.md to reference current docs only

### Removed Files
- Session summaries: `SESSION_SUMMARY.md`, `Session_Summary_20251226.md`, `consistency_update_summary.md`
- Bug fix docs: `Character_Reference_Bug_Fixes_2025-12-26.md`, `Character_Prompts_Updated_20251226.md`
- Completed work: `completed-2025-12-27-project-cleanup-restructure.md`, `Pipeline_Scripts_Cleanup_2025-12-26.md`
- Redundant/obsolete: `Fix_Summary_2025-12-26_TTS_CUDA.md`, `Character_References_8_Image_Implementation.md`, `LLM_Prompt_Generation_Setup.md`

### Rationale
- Session summaries are historical records; information preserved in git history
- Bug fix documentation superseded by fixes in code
- Redundant information consolidated into core docs (TROUBLESHOOTING.md, Phase summaries)
- LLM prompt generation superseded by storyboard analysis (now default method)

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
