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

### 2025-12-27: Character Selection Fix (CRITICAL)
- **Issue**: Wrong characters appearing in images due to multiple bugs in character selection logic
- **Problems**:
  1. Minor characters without descriptions (Ramirez, Mark, Diane) caused undefined character names in prompts → inconsistent/wrong faces
  2. Referenced characters (Tyler in "text from Tyler") incorrectly prioritized over acting characters
  3. Token compression code path had separate bug that bypassed role filtering
- **Root Cause**: System blindly selected `characters_present[0]` without considering character roles or checking if character has a description
- **Solution**:
  - Added `filter_acting_characters()` with priority: Acting > Passive > Referenced
  - Character selection now skips characters without descriptions, falls back to next available
  - Applied same logic to BOTH normal generation AND token compression path
- **Files Modified**:
  - `src/prompt_generator.py`:
    - Lines 18-56: New `filter_acting_characters()` utility
    - Lines 717-771: Role-based character selection with description validation
    - Lines 841-885: Fixed token compression to use same filtering
- **Impact**: Only defined characters (Emma, Tyler, Elena, Maxim, Amara) appear in images; minor characters gracefully fall back
- **Example**: Ramirez scene now uses Emma's description instead of undefined "ramirez"
- **See**: [CHANGELOG.md](../CHANGELOG.md)

### 2025-12-27: Documentation Cleanup
- **Action**: Cleaned up `technical_docs/` folder (21 files → 11 files, 48% reduction)
- **Removed**: Session summaries, bug fix docs, and obsolete/redundant documentation
- **Kept**: Core operational guides (PROJECT_STATUS, TROUBLESHOOTING, storyboard docs, phase summaries, cost tracking)
- **See**: [CHANGELOG.md](../CHANGELOG.md)

### 2025-12-27: Character Clothing Consistency Fix
- **Issue**: Clothing colors/styles changed randomly between sentences in same scene
- **Cause**: Character name mismatch ("Emma Chen" vs "emma") prevented attribute lookups
- **Fix**: Added character name normalization + enhanced compression to always include clothing
- **Result**: All prompts now include consistent clothing (e.g., "navy blue blazer white shirt black")
- **See**: [CHANGELOG.md](../CHANGELOG.md)

## Additional Instructions

For detailed rules, see:
- Python environment and scripts: @.claude/rules/python.md
- Novel writing guidelines: @.claude/rules/writing.md
