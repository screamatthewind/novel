# The Obsolescence - Project Memory

This is a creative writing project for a novel titled "The Obsolescence".

## CRITICAL GIT RULES

**DO NOT EVER use git commands.** The user manages all git operations manually.

- ❌ NEVER run: `git add`, `git commit`, `git push`, `git pull`, etc.
- ✅ You can: Read files, make edits, suggest changes
- ✅ If changes need committing: Tell the user what was changed, let them handle git

## Project Overview

### Novel Documents
- **[book/reference/The_Obsolescence_Novel_Bible.md](book/reference/The_Obsolescence_Novel_Bible.md)** - World-building reference, character profiles, and core concepts
- **[book/reference/The_Obsolescence_Novel_Outline.md](book/reference/The_Obsolescence_Novel_Outline.md)** - Story structure and chapter-by-chapter outline
- **[book/manuscript/](book/manuscript/)** - Individual chapter manuscripts (All 12 chapters complete)

### Image Generation, Audio & Video System
- **[src/](src/)** - Python scripts for generating scene images (Stable Diffusion XL), audio (Coqui TTS), and videos (MoviePy)
- **[images/](images/)** - Generated scene images
- **[audio/](audio/)** - Generated scene audio files
- **[videos/](videos/)** - Generated YouTube-ready videos
- **[technical_docs/](technical_docs/)** - Image, audio, and video generation documentation
- **[technical_docs/TROUBLESHOOTING.md](technical_docs/TROUBLESHOOTING.md)** - Troubleshooting guide for common issues
- **[venv/](venv/)** - Python virtual environment (**ALWAYS use this for all Python commands**)

## Directory Structure

```
novel/
├── book/
│   ├── manuscript/          # Chapter files (The_Obsolescence_Chapter_*.md)
│   └── reference/           # Novel Bible and Outline
├── technical_docs/          # Project documentation and guides
├── src/                     # Python scripts for image, audio, and video generation
├── images/                  # Generated scene images
├── audio/                   # Generated scene audio files
├── videos/                  # Generated YouTube videos
├── audio_cache/             # Audio metadata and dialogue caches
├── voices/                  # Voice sample files for TTS
├── logs/                    # Generation logs
├── prompt_cache/            # Cached image prompts
├── temp/                    # Temporary files (MoviePy video generation, etc.)
└── venv/                    # Python virtual environment (**ALWAYS USE THIS**)
```

## Recent Changes

### 2025-12-27: Documentation Cleanup
- **Action**: Cleaned up `technical_docs/` folder (21 files → 11 files, 48% reduction)
- **Removed**: Session summaries, bug fix docs, and obsolete/redundant documentation
- **Kept**: Core operational guides (PROJECT_STATUS, TROUBLESHOOTING, storyboard docs, phase summaries, cost tracking)
- **Rationale**:
  - Session summaries are historical; information preserved in git history
  - Bug fixes documented in code and TROUBLESHOOTING.md
  - LLM prompt generation superseded by storyboard analysis (now default)
- **See**: [CHANGELOG.md](../CHANGELOG.md) for full list of removed files

### 2025-12-27: Fixed Character Clothing Consistency
- **Issue**: Clothing colors/styles changed randomly between sentences in same scene
- **Cause**: Character name mismatch ("Emma Chen" vs "emma") prevented attribute lookups
- **Fix**: Added character name normalization + enhanced compression to always include clothing
- **Files Modified**:
  - `src/prompt_generator.py` - Added `normalize_character_name()` function
  - `src/attribute_state_manager.py` - Enhanced `to_compressed_string()` to always include clothing
  - `src/generate_scene_images.py` - Fixed `attribute_manager` initialization in dry-run mode
- **Result**: All prompts now include consistent clothing (e.g., "navy blue blazer white shirt black")
- **See**: [CHANGELOG.md](../CHANGELOG.md) and [technical_docs/TROUBLESHOOTING.md](../technical_docs/TROUBLESHOOTING.md)

## Additional Instructions

For detailed rules, see:
- Python environment and scripts: @.claude/rules/python.md
- Novel writing guidelines: @.claude/rules/writing.md
