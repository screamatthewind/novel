# The Obsolescence

A novel about economic dependency, technological displacement, and human meaning.

## Repository Structure

- **[docs/manuscript/](docs/manuscript/)** - Novel chapters
- **[docs/reference/](docs/reference/)** - Novel Bible and Outline
- **[docs/project/](docs/project/)** - Project documentation
- **[src/](src/)** - Image generation scripts
- **[images/](images/)** - Generated scene images

## Image Generation

Automated scene image generation using Stable Diffusion XL in graphic novel style.

### Quick Start

```bash
# Generate all scene images
cd src
python generate_scene_images.py

# Test prompt generation
python prompt_generator.py

# Resume from specific chapter/scene
python generate_scene_images.py --resume 2 3
```

### System Status
✅ Token optimization complete (prompts: 53/77 tokens)
✅ Deprecated APIs updated (diffusers 0.40.0+ compatible)
✅ Token validation added for all prompts
