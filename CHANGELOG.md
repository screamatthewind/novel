# Changelog

All notable changes to The Obsolescence novel generation project.

## [2025-12-27] - Character Selection Fix (Major)

### Fixed
- **Critical: Wrong characters appearing in images**
  - Issue #1: Minor characters without descriptions (e.g., Ramirez) caused system to use undefined character names in prompts
  - Issue #2: Referenced characters (e.g., Tyler in "text from Tyler") were incorrectly prioritized over acting characters
  - Issue #3: Token compression code path had separate bug that reverted to old character selection logic

### Root Cause
- Prompt generator blindly selected `characters_present[0]` without considering character roles
- No fallback logic when selected character lacked a description in `CHARACTER_CANONICAL_ATTRIBUTES`
- Token compression path (line 841) had duplicate logic that wasn't updated with role filtering

### Solution Implemented
- Added `filter_acting_characters()` function with priority: Acting > Passive > Referenced
- Character selection now skips characters without descriptions and falls back to next available character
- Applied same filtering logic to BOTH normal prompt generation AND token compression path

### Changes
- **src/prompt_generator.py**:
  - Lines 18-56: New `filter_acting_characters()` utility function
  - Lines 717-771: Updated character selection with role filtering and description validation
  - Lines 841-885: Fixed token compression path to use same filtering logic

### Example Fixes
- **Sentence 5 (Ramirez scene)**:
  - Before: `"ramirez. broad, satisfied grin"` (no description)
  - After: `"mid-40s Asian American woman, intelligent brown eyes, analytical expression. broad, satisfied grin"` (Emma's description)
  - Ramirez (no description) skipped → Emma (passive role, has description) selected

- **Sentence 15 (Tyler text)**:
  - Correctly uses Emma (passive: receiving message) over Tyler (referenced: sender of message)
  - Image shows Emma looking at phone, not Tyler

### Character Priority Levels
1. **Acting**: speaking, walking, examining, confirming (highest priority)
2. **Passive**: receiving, listening, observing, watching (medium priority)
3. **Referenced**: mentioned, sender of, off-screen (lowest priority)

### Impact
- Only defined characters (Emma, Tyler, Elena, Maxim, Amara) appear in images
- Minor characters (Ramirez, Mark, Diane, etc.) gracefully fall back to defined characters in scene
- Correct character context (e.g., Emma receiving Tyler's message, not Tyler himself)

### Migration
To regenerate prompts with correct character selection:
```bash
# Delete old prompts and regenerate
rm prompt_cache/chapter_01_*.txt
venv/Scripts/python.exe src/generate_scene_images.py --chapters 1 --dry-run
```

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
