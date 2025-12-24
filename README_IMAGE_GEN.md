# Novel Scene Image Generation System

Automated SDXL-based image generation for novel scenes, optimized for RTX 3080 10GB GPU.

## Overview

This system parses your novel's chapter markdown files, extracts individual scenes, and generates graphic novel-style illustrations using Stable Diffusion XL (SDXL). It's designed to run efficiently on an RTX 3080 with 10GB VRAM.

**Key Features:**
- Automatic scene detection using `* * *` separators
- Intelligent prompt generation from scene content
- RTX 3080 memory optimizations (xFormers, CPU offload, VAE slicing)
- Resumable generation with progress tracking
- Descriptive filenames for easy organization

## Quick Start

### 1. Setup (One-Time)

Create a virtual environment and install dependencies:

```bash
python -m venv venv
.\venv\Scripts\activate

# Install packages from requirements.txt first
pip install -r requirements.txt

# Then install torch with CUDA support (overwrites CPU version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install xformers for memory optimization (optional but recommended)
pip install xformers --index-url https://download.pytorch.org/whl/cu118

# Verify CUDA is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Note:** First run will download ~13GB SDXL model from HuggingFace.

### 2. Generate All Scene Images

```bash
python generate_scene_images.py
```

This will:
- Parse all 4 chapters
- Extract ~29 scenes (excluding CRAFT NOTES sections)
- Generate graphic novel-style illustrations for each scene
- Save to `/images/` directory
- Take approximately 3-4 hours on RTX 3080

### 3. Review Outputs

- **Images:** Check `/images/` for generated PNG files
- **Prompts:** Review `/prompt_cache/` to see prompts used
- **Logs:** Check `/logs/` for generation details and any errors

## Usage Examples

### Generate Specific Chapters

```bash
# Only generate images for Chapters 1 and 3
python generate_scene_images.py --chapters 1 3
```

### Resume From Specific Scene

```bash
# Resume from Chapter 2, Scene 5
python generate_scene_images.py --resume 2 5
```

### Dry Run (Preview Prompts)

```bash
# Show what would be generated without creating images
python generate_scene_images.py --dry-run
```

### High Quality Mode

```bash
# Use more inference steps for higher quality
python generate_scene_images.py --steps 40 --guidance 8.0
```

### Custom Resolution

```bash
# Generate at different resolution
python generate_scene_images.py --width 1024 --height 1024
```

## System Architecture

### Components

1. **[config.py](config.py)** - Central configuration (paths, model settings, prompts)
2. **[scene_parser.py](scene_parser.py)** - Extracts scenes from chapter markdown files
3. **[prompt_generator.py](prompt_generator.py)** - Converts scene text to SDXL prompts
4. **[image_generator.py](image_generator.py)** - SDXL engine with RTX 3080 optimizations
5. **[generate_scene_images.py](generate_scene_images.py)** - Main CLI orchestration script

### Directory Structure

```
novel/
├── generate_scene_images.py      # Main CLI script
├── scene_parser.py                # Markdown parsing
├── prompt_generator.py            # Prompt generation
├── image_generator.py             # SDXL engine
├── config.py                      # Configuration
├── requirements.txt               # Dependencies
├── images/                        # Generated images (output)
├── logs/                          # Generation logs
└── prompt_cache/                  # Saved prompts
```

## How It Works

### Scene Parsing

The parser:
- Finds chapter files matching `The_Obsolescence_Chapter_*.md`
- Splits content on `* * *` separators
- **Excludes CRAFT NOTES sections** (editorial content)
- Extracts chapter number from filename (One=1, Two=2, etc.)

### Prompt Generation

For each scene, the system extracts:
- **Characters:** Emma, Maxim, Elena, Tyler, Amara
- **Setting:** Factory, office, kitchen, train, rowhouse, etc.
- **Time of day:** Morning, afternoon, evening, night
- **Mood:** Shock, warmth, tension, reflection, urgency
- **Action:** Reading, working, talking, walking, watching

These elements are combined into a graphic novel illustration prompt:

```
[characters] in [setting], [action], [mood], [time/lighting],
graphic novel illustration, comic book art style, detailed line work,
dramatic shading, cel shading, high contrast lighting, professional comic art
```

### Image Generation

**Model:** `stabilityai/stable-diffusion-xl-base-1.0`

**Generation Parameters:**
- Resolution: 1344x768 (16:9 cinematic)
- Inference steps: 30 (quality/speed balance)
- Guidance scale: 7.5
- Seed: 42 + chapter*100 + scene (reproducible but varied)

**RTX 3080 Optimizations:**
- Float16 precision
- xFormers flash attention
- Model CPU offload
- VAE slicing and tiling
- DPM++ scheduler

**Performance:**
- Model load: ~45 seconds
- Per scene: ~5-7 minutes
- Total for 29 scenes: ~3-4 hours
- VRAM usage: 8-9GB (safe for 10GB card)

### Output Files

**Images** (`/images/`)
- Format: `chapter_01_scene_02_emma_factory_reading.png`
- Resolution: 1344x768 (or custom)
- Size: ~2-3MB per image

**Prompts** (`/prompt_cache/`)
- Format: `chapter_01_scene_02_emma_factory_reading.txt`
- Contains both positive and negative prompts
- Useful for manual regeneration or tweaking

**Logs** (`/logs/`)
- Format: `generation_YYYYMMDD_HHMMSS.log`
- Contains timestamps, prompts, errors, and performance metrics

## Iterating on Results

### Regenerate Specific Scene

1. Review the image in `/images/`
2. Edit the prompt in `/prompt_cache/chapter_XX_scene_YY.txt` if needed
3. Delete the image file
4. Re-run: `python generate_scene_images.py --resume X Y`

### Adjust Generation Quality

```bash
# Higher quality (slower, more VRAM)
python generate_scene_images.py --steps 40 --guidance 8.5

# Faster (lower quality, less VRAM)
python generate_scene_images.py --steps 20 --guidance 7.0
```

### Troubleshooting CUDA OOM

If you get "CUDA out of memory" errors:

1. The script automatically retries with 75% resolution
2. Or manually reduce resolution:
   ```bash
   python generate_scene_images.py --width 1024 --height 576
   ```
3. Close other GPU-intensive applications
4. Reduce inference steps: `--steps 25`

## Testing Individual Components

### Test Scene Parser

```bash
python scene_parser.py
```

Expected output:
- Chapter 1: 7 scenes
- Chapter 2: 9 scenes
- Chapter 3: 5 scenes
- Chapter 4: 9 scenes

### Test Prompt Generator

```bash
python prompt_generator.py
```

Shows sample prompt generation from test scene.

### Test Image Generator

```bash
python image_generator.py
```

Generates single test image to verify SDXL setup.

## Performance Benchmarks

**Expected on RTX 3080:**
- Model load: 30-45 seconds
- 1344x768 @ 30 steps: 5-7 minutes per image
- 1024x576 @ 20 steps: 3-4 minutes per image

**VRAM Usage:**
- Idle with model loaded: ~6.5GB
- During generation: ~8.5-9.0GB
- Peak: ~9.2GB
- Safety margin: ~800MB

## Command-Line Reference

```
python generate_scene_images.py [OPTIONS]

Options:
  --chapters 1 3          Generate only specific chapters
  --resume 2 5            Resume from Chapter 2, Scene 5
  --dry-run               Show prompts without generating images
  --steps 30              Number of inference steps (default: 30)
  --guidance 7.5          Guidance scale (default: 7.5)
  --width 1344            Image width (default: 1344)
  --height 768            Image height (default: 768)
  -h, --help              Show help message
```

## Configuration

Edit [config.py](config.py) to customize:

- Output directories
- Model selection
- Default resolution
- Base style template
- Negative prompt
- Character descriptions

## Known Limitations

- Requires CUDA-capable GPU (RTX 3080 or similar)
- First run downloads ~13GB model
- Generation is slow (~6 min/image)
- Prompts are rule-based, not AI-generated
- Works best with descriptive scene text

## Support

For issues or questions:
1. Check `/logs/` for error messages
2. Verify CUDA installation: `python -c "import torch; print(torch.cuda.is_available())"`
3. Ensure ~20GB free disk space (model + images)
4. Review this README and command-line options

## License

This code is for personal use with your novel project.
