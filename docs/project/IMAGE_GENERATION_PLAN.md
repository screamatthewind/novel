# Implementation Plan: Novel Scene Image Generation System

## Overview

Build a Python CLI program to parse chapter markdown files, extract scenes, and generate SDXL images optimized for RTX 3080 10GB GPU.

**Scope:** 4 chapters → ~29 scenes → 29 graphic novel-style images saved to `/images/` directory

**User Selections:**
- Parse scenes using `* * *` separators (one image per scene)
- Generate with SDXL (Stable Diffusion XL) for RTX 3080
- Simple Python CLI script (no UI)
- Save to `/images/` with descriptive filenames
- **Graphic novel illustration style** (not photorealistic)

---

## Project Structure

Create the following files in the novel directory:

```
novel/
├── generate_scene_images.py      # Main CLI script
├── scene_parser.py                # Markdown parsing utilities
├── prompt_generator.py            # Scene-to-prompt conversion
├── image_generator.py             # SDXL generation engine
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
├── README_IMAGE_GEN.md           # Usage documentation
├── images/                        # Output directory (exists)
├── logs/                          # Generation logs (create)
└── prompt_cache/                  # Saved prompts (create)
```

---

## Implementation Steps

### 1. Setup & Dependencies

**Create `requirements.txt`:**
```txt
torch==2.1.2+cu118
torchvision==0.16.2+cu118
diffusers==0.25.1
transformers==4.36.2
accelerate==0.25.0
xformers==0.0.23.post1
safetensors==0.4.1
Pillow==10.1.0
tqdm==4.66.1
```

**Installation:**
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

**Note:** First run downloads ~13GB SDXL model from HuggingFace

---

### 2. Scene Parser (`scene_parser.py`)

**Key Requirements:**
- Parse chapter markdown files
- Split on `* * *` separator (regex: `r'^\*\s+\*\s+\*\s*$'`)
- **Exclude CRAFT NOTES sections** (find `^CRAFT NOTES`, truncate)
- Extract chapter number from filename (One=1, Two=2, Three=3, Four=4)
- Return Scene objects with metadata

**Scene Object:**
```python
@dataclass
class Scene:
    chapter_num: int
    chapter_title: str
    scene_num: int
    content: str
    word_count: int
```

**Expected Output:**
- Chapter 1: 7 scenes
- Chapter 2: 9 scenes
- Chapter 3: 5 scenes
- Chapter 4: 9 scenes
- **Total: ~30 scenes**

---

### 3. Prompt Generator (`prompt_generator.py`)

**Strategy:** Rule-based extraction of visual elements from scene text

**Extract from each scene:**
- **Setting:** Factory, office, kitchen, train, rowhouse, cafeteria, etc.
- **Characters:** Emma (professional woman, 40s), Maxim (factory worker), Elena (older woman), Tyler (teenage boy)
- **Time of day:** Morning, afternoon, evening, night → lighting descriptors
- **Mood:** Shock, warmth, reflection, nervous → atmospheric descriptors
- **Action:** Reading email, checking tablet, viewing monitors, working assembly line

**Prompt Structure:**
```
[characters] in [setting], [action], [mood], [time/lighting],
graphic novel illustration, comic book art style, detailed line work,
dramatic shading, cel shading, high contrast lighting, professional comic art
```

**Example:**
```
Scene content: "Emma stared at the email on her tablet. The factory floor hummed..."
Generated prompt: "professional woman in factory setting, reading tablet screen,
shocked expression, dramatic shadows, afternoon sunlight, graphic novel illustration,
comic book art style, detailed line work, high contrast"
```

**Negative Prompt (all images):**
```
photorealistic, photo, photograph, 3d render, blurry, low quality,
distorted anatomy, extra limbs, deformed, amateur, watermark
```

**Filename Generation:**
- Format: `chapter_01_scene_02_layoff_notification.png`
- Extract 2-4 key words from setting/action
- Zero-pad chapter/scene numbers for sorting

---

### 4. SDXL Generator (`image_generator.py`)

**Model:** `stabilityai/stable-diffusion-xl-base-1.0`

**Critical RTX 3080 Optimizations:**
```python
# Float16 precision
pipe = StableDiffusionXLPipeline.from_pretrained(
    model_id, torch_dtype=torch.float16, variant="fp16"
)

# Memory optimizations
pipe.enable_xformers_memory_efficient_attention()  # Flash attention
pipe.enable_model_cpu_offload()  # Move UNet to CPU when idle
pipe.enable_vae_slicing()  # Process images in slices
pipe.enable_vae_tiling()  # Enable higher resolutions

# Fast scheduler
pipe.scheduler = DPMSolverMultistepScheduler.from_config(...)
```

**Expected VRAM Usage:** 8-9GB during generation (safe for 10GB card)

**Generation Parameters:**
- Resolution: 1344x768 (16:9 cinematic)
- Inference steps: 30 (optimal quality/speed balance)
- Guidance scale: 7.5 (how closely to follow prompt)
- Seed: 42 + scene_index (reproducible but varied)

**Performance:** 5-7 minutes per image on RTX 3080

---

### 5. Main CLI (`generate_scene_images.py`)

**Core Workflow:**
```python
1. Parse command-line arguments
2. Load chapter markdown files
3. Extract scenes (exclude CRAFT NOTES)
4. Load SDXL model with optimizations
5. For each scene:
   a. Generate prompt from scene content
   b. Create descriptive filename
   c. Skip if image already exists
   d. Generate image with SDXL
   e. Save to /images/ directory
   f. Save prompt to /prompt_cache/
   g. Clean up CUDA memory
6. Log all operations to /logs/
```

**Command-Line Arguments:**
```bash
# Basic usage
python generate_scene_images.py

# Specific chapters only
python generate_scene_images.py --chapters 1 3

# Resume from Chapter 2, Scene 5
python generate_scene_images.py --resume 2 5

# Dry run (show prompts without generating)
python generate_scene_images.py --dry-run

# High quality mode
python generate_scene_images.py --steps 40 --guidance 8.0
```

**Error Handling:**
- CUDA OOM → reduce resolution, retry
- Model download failure → clear error message with instructions
- Invalid scene parse → log error, continue with next scene
- Generation failure → log error, save prompt for manual retry

---

### 6. Configuration (`config.py`)

**Central configuration:**
```python
# Paths
CHAPTER_DIR = "."
OUTPUT_DIR = "./images"
LOG_DIR = "./logs"
PROMPT_CACHE_DIR = "./prompt_cache"

# Model settings
DEFAULT_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
DEVICE = "cuda"

# Generation parameters
DEFAULT_WIDTH = 1344
DEFAULT_HEIGHT = 768
DEFAULT_STEPS = 30
DEFAULT_GUIDANCE = 7.5

# Style template - Graphic novel style
BASE_STYLE = "graphic novel illustration, comic book art style, detailed line work, professional comic art, dramatic shading, cel shading, sequential art, published graphic novel quality, high contrast lighting, expressive illustration"

# Negative prompt - Avoid photorealism
NEGATIVE_PROMPT = "photorealistic, photo, photograph, 3d render, blurry, low quality, distorted anatomy, extra limbs, deformed, ugly, oversaturated, watermark, signature, amateur, sketch, unfinished"
```

---

## Critical Files to Reference

**For parsing implementation:**
- [The_Obsolescence_Chapter_One.md](The_Obsolescence_Chapter_One.md) - Scene structure example, CRAFT NOTES location
- [The_Obsolescence_Chapter_Two.md](The_Obsolescence_Chapter_Two.md) - More complex scenes with technical descriptions

**For prompt generation:**
- [The_Obsolescence_Novel_Bible.md](The_Obsolescence_Novel_Bible.md) - Character appearances, setting details, tonal guidance
- All chapter files - Visual descriptions for extracting prompt elements

**Output:**
- [images/](images/) - Destination directory for generated PNG files

---

## Testing & Validation

**Unit Testing:**
1. Test scene parser on Chapter 1 → verify 7 scenes extracted
2. Verify CRAFT NOTES exclusion → no "CRAFT NOTES" text in scenes
3. Test prompt generator → all prompts >20 chars, contain expected keywords
4. Test filename generation → valid, sortable, unique

**Integration Testing:**
1. Dry run: `python generate_scene_images.py --dry-run`
2. Single scene test: `python generate_scene_images.py --resume 1 1`
3. Full Chapter 1: `python generate_scene_images.py --chapters 1`
4. Monitor VRAM usage: Should stay ≤9.5GB

**Quality Validation:**
- [ ] All 29 scenes generate images
- [ ] Images match scene content (manual review)
- [ ] Filenames are descriptive and sortable
- [ ] No CUDA OOM errors during generation
- [ ] Total time: 3-4 hours for all scenes

---

## Expected Performance

**Timing Estimates (RTX 3080):**
- Model load: 30-45 seconds (one-time)
- Per scene: ~6 minutes (prompt 1sec + generation 5-7min + cleanup 2sec)
- **Total for 29 scenes: ~3-4 hours**

**VRAM Profile:**
- Idle with model loaded: 6.5GB
- During generation: 8.5-9.0GB
- Peak: 9.2GB
- Safety margin: ~800MB

**Output:**
- 29 PNG images (1344x768, ~2-3MB each)
- 29 prompt text files in cache
- Generation log with timing and errors

---

## Usage Documentation

**Basic workflow for user:**

1. **Setup (one-time):**
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

2. **Generate all scenes:**
   ```bash
   python generate_scene_images.py
   ```

3. **Review outputs:**
   - Check `/images/` directory for generated PNGs
   - Review `/logs/` for any errors
   - Check `/prompt_cache/` to see prompts used

4. **Regenerate specific scenes:**
   ```bash
   # Regenerate Chapter 2, Scene 3 with different settings
   python generate_scene_images.py --resume 2 3 --steps 40
   ```

5. **Iterate on prompts:**
   - Edit prompts in `/prompt_cache/chapter_XX_scene_YY.txt`
   - Delete corresponding image in `/images/`
   - Re-run to regenerate with new prompt

---

## Success Criteria

- ✅ All 4 chapters successfully parsed
- ✅ ~29 scenes extracted (excluding CRAFT NOTES)
- ✅ All scenes generate valid SDXL prompts
- ✅ All images generated without CUDA OOM errors
- ✅ Images saved with descriptive filenames
- ✅ Generation completes in 3-4 hours
- ✅ VRAM usage stays under 10GB
- ✅ Images match scene content (manual review)

---

## Research Sources

**Image Generation Libraries (2025):**
- [Running FLUX/PixArt on Lower VRAM GPUs](https://medium.com/data-science/running-pixart-%CF%83-flux-1-image-generation-on-lower-vram-gpus-a-short-tutorial-in-python-62419f35596e)
- [Best GPUs for Stable Diffusion & FLUX](https://techtactician.com/best-gpu-for-stable-diffusion-sdxl-and-flux/)
- [Fastest AI Image Generation Models 2025](https://blog.segmind.com/best-ai-image-generation-models-guide/)
- [Stable Diffusion GPU Benchmarks](https://www.tomshardware.com/pc-components/gpus/stable-diffusion-benchmarks)

**Python Text-to-Image Tutorials:**
- [Generate Images from Text - Stable Diffusion](https://www.geeksforgeeks.org/deep-learning/generate-images-from-text-in-python-stable-diffusion/)
- [Local Text-to-Image with older Nvidia GPU](https://medium.com/@daniela.vorkel/local-text-to-image-generation-using-older-nvidia-gpu-and-gradio-interface-a41aff359f2a)
- [Running Local LLMs for Image Generation](https://www.bhaskar.blog/posts/2025-02-08-running-image-generation-models-locally)
- [How to Run Stable Diffusion Locally](https://www.assemblyai.com/blog/how-to-run-stable-diffusion-locally-to-generate-images/)

**Interface Comparisons:**
- [ComfyUI vs Stable Diffusion WebUI 2025](https://www.aifreeapi.com/en/posts/comfyui-vs-stable-diffusion)
- [ComfyUI vs A1111 vs Fooocus Comparison](https://www.propelrc.com/comfyui-vs-automatic1111-vs-fooocus/)
- [ComfyUI vs Automatic1111 Honest Comparison](https://apatero.com/blog/comfyui-vs-automatic1111-which-should-you-use-2025)

**Key Findings:**
- SDXL is optimal for RTX 3080 10GB (FLUX requires aggressive quantization)
- Diffusers library with PyTorch is the standard Python implementation
- xFormers and model CPU offload are essential for 10GB VRAM
- ComfyUI has better FLUX support, but A1111/direct Python scripts work great for SDXL
- Expected generation time: 3-6 seconds per image reported, but more realistic is 5-7 minutes for quality output at 1344x768

---

## Notes

- The novel has 4 completed chapters with consistent scene structure
- Empty `/images/` directory already exists in project
- No existing Python code - starting from scratch
- User prefers simple CLI over GUI
- Focus on graphic novel illustration style with professional comic art quality
- CRAFT NOTES sections must be excluded (editorial content, not narrative)
