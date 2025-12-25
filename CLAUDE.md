# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a creative writing project for a novel titled "The Obsolescence". The repository contains:

### Novel Documents
- **[docs/reference/The_Obsolescence_Novel_Bible.md](docs/reference/The_Obsolescence_Novel_Bible.md)** - World-building reference, character profiles, and core concepts
- **[docs/reference/The_Obsolescence_Novel_Outline.md](docs/reference/The_Obsolescence_Novel_Outline.md)** - Story structure and chapter-by-chapter outline
- **[docs/manuscript/](docs/manuscript/)** - Individual chapter manuscripts (All 12 chapters complete)

### Image Generation System
- **[src/](src/)** - Python scripts for generating scene images using Stable Diffusion XL
- **[images/](images/)** - Generated scene images
- **[docs/project/](docs/project/)** - Image generation documentation and implementation notes

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
├── src/                     # Python scripts for image generation
├── images/                  # Generated scene images
├── logs/                    # Generation logs
├── prompt_cache/            # Cached image prompts
└── venv/                    # Python virtual environment
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
