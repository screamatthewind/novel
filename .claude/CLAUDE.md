# The Obsolescence - Project Memory

This is a creative writing project for a novel titled "The Obsolescence".

## CRITICAL GIT RULES

**DO NOT EVER use git commands.** The user manages all git operations manually.

- ❌ NEVER run: `git add`, `git commit`, `git push`, `git pull`, etc.
- ✅ You can: Read files, make edits, suggest changes
- ✅ If changes need committing: Tell the user what was changed, let them handle git

## Project Overview

### Novel Documents
- **[docs/reference/The_Obsolescence_Novel_Bible.md](docs/reference/The_Obsolescence_Novel_Bible.md)** - World-building reference, character profiles, and core concepts
- **[docs/reference/The_Obsolescence_Novel_Outline.md](docs/reference/The_Obsolescence_Novel_Outline.md)** - Story structure and chapter-by-chapter outline
- **[docs/manuscript/](docs/manuscript/)** - Individual chapter manuscripts (All 12 chapters complete)

### Image Generation, Audio & Video System
- **[src/](src/)** - Python scripts for generating scene images (Stable Diffusion XL), audio (Coqui TTS), and videos (MoviePy)
- **[images/](images/)** - Generated scene images
- **[audio/](audio/)** - Generated scene audio files
- **[videos/](videos/)** - Generated YouTube-ready videos
- **[docs/project/](docs/project/)** - Image, audio, and video generation documentation
- **[docs/project/TROUBLESHOOTING.md](docs/project/TROUBLESHOOTING.md)** - Troubleshooting guide for common issues
- **[venv/](venv/)** - Python virtual environment (**ALWAYS use this for all Python commands**)

## Directory Structure

```
novel/
├── docs/
│   ├── manuscript/          # Chapter files (The_Obsolescence_Chapter_*.md)
│   ├── reference/           # Novel Bible and Outline
│   └── project/             # Project documentation and plans
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

## Additional Instructions

For detailed rules, see:
- Python environment and scripts: @.claude/rules/python.md
- Novel writing guidelines: @.claude/rules/writing.md
