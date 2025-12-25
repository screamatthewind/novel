# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL GIT RULES

**DO NOT EVER use git commands.** The user manages all git operations manually.

- ❌ NEVER run: `git add`, `git commit`, `git push`, `git pull`, etc.
- ✅ You can: Read files, make edits, suggest changes
- ✅ If changes need committing: Tell the user what was changed, let them handle git

## Project Overview

This is a creative writing project for a novel titled "The Obsolescence". The repository contains:

### Novel Documents
- **[docs/reference/The_Obsolescence_Novel_Bible.md](docs/reference/The_Obsolescence_Novel_Bible.md)** - World-building reference, character profiles, and core concepts
- **[docs/reference/The_Obsolescence_Novel_Outline.md](docs/reference/The_Obsolescence_Novel_Outline.md)** - Story structure and chapter-by-chapter outline
- **[docs/manuscript/](docs/manuscript/)** - Individual chapter manuscripts (All 12 chapters complete)

### Image Generation, Audio & Video System
- **[src/](src/)** - Python scripts for generating scene images (Stable Diffusion XL), audio (Chatterbox TTS), and videos (MoviePy)
- **[images/](images/)** - Generated scene images
- **[audio/](audio/)** - Generated scene audio files
- **[videos/](videos/)** - Generated YouTube-ready videos
- **[docs/project/](docs/project/)** - Image, audio, and video generation documentation
- **[venv/](venv/)** - Python virtual environment (**ALWAYS use this for all Python commands**)

## Working with This Project

### Document Priority

When assisting with this novel:

1. **Always consult the Novel Bible first** - It contains the canonical world-building, character details, and thematic elements that must remain consistent across all chapters
2. **Reference the Outline** - Check the outline to understand where each chapter fits in the overall story arc before making suggestions
3. **Maintain continuity** - When editing or reviewing chapters, cross-reference earlier chapters to ensure consistency in character voices, plot details, and world-building

### Directory Structure

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

### File Naming Convention

Chapter files follow the pattern: `The_Obsolescence_Chapter_[NN].md` where NN is the zero-padded chapter number (01, 02, 03, ..., 12).
All chapter files are located in [docs/manuscript/](docs/manuscript/)

### Project Structure

The novel is organized in four parts:
- **Part One: The Awakening** - Emma Chen's journey from layoff to understanding (Chapters 1-3)
- **Part Two: The Pattern** - Global perspectives: Maxim Orlov (Russia), Amara Okafor (Kenya) (Chapters 4-5)
- **Part Three: The Machines** - Time jump to 2029, humanoid robot deployment, Wei Chen's perspective (Chapters 6-9)
- **Part Four: The Obsolescence** - Speculative future 2032-2045, the Remainder communities (Chapters 10-12)

### Key Considerations

- All edits should be made directly to the Markdown files
- When providing edits, reference specific line numbers or sections
- Maintain the established tone, style, and voice present in existing chapters
- All statistics and data in Parts 1-2 are sourced from real-world research (see Novel Bible section 8)

### Tonal Guidance

**CRITICAL: This is entertainment first, education second**

- Technology has tonal range—thrilling, mundane, terrifying, often simultaneously
- The soft-sell is key: robots as backup dancers are genuinely cool before revealing they're the same models used in factories/military
- Climate change is background texture only—brief sensory details, never explained, makes everything else worse
- Information introduced gradually through character experience, never info-dumps
- Avoid one-note dystopian gloom—embrace complexity, uncertainty, earned emotions

## Python Environment

**CRITICAL: ALWAYS use the virtual environment for ALL Python commands**

### Running Python Scripts

All Python scripts MUST be run using the virtual environment Python interpreter:

```bash
# From project root
./venv/Scripts/python src/script_name.py

# Or from src/ directory
cd src
../venv/Scripts/python script_name.py
```

### Installing Packages

Always install packages into the virtual environment:

```bash
./venv/Scripts/pip install package_name
```

### Available Scripts

1. **Image Generation**: `src/generate_scene_images.py` - Generate scene images using Stable Diffusion XL
2. **Audio Generation**: `src/generate_scene_audio.py` - Generate scene audio using Coqui TTS
3. **Video Generation**: `src/generate_video.py` - Generate YouTube videos from images and audio
4. **Scene Parser**: `src/scene_parser.py` - Parse chapters into scenes

### Running Scripts

```bash
cd src

# Image generation
../venv/Scripts/python generate_scene_images.py --chapters 1

# Audio generation
../venv/Scripts/python generate_scene_audio.py --chapters 1

# Video generation
../venv/Scripts/python generate_video.py --chapter 1
../venv/Scripts/python generate_video.py --chapters 1 2 3 --combine
```

**Note**: Scripts use relative paths from `src/` directory, so always run from `src/` or adjust paths accordingly.

## CRITICAL: launch.json Updates

**ALWAYS add launch configurations to `.vscode/launch.json` when creating new Python scripts.** This is a required step for all new scripts.
