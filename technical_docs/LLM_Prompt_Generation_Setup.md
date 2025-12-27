# LLM-Based Prompt Generation Setup

## Overview

The image generation system now supports three prompt generation methods:
1. **Keyword** - Original rule-based extraction (fast, simple, generic)
2. **Ollama** - Local Llama 3.1 8B (free, private, requires setup)
3. **Claude Haiku** - Anthropic API (best quality, minimal cost, requires API key)

## Configuration

### 1. Create `.env` File

Copy the example file and add your API key:
```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
```

Get an API key from: https://console.anthropic.com/

### 2. Install Dependencies

The `anthropic` library is already installed in the venv. To verify:
```bash
cd src
../venv/Scripts/pip list | grep anthropic
```

## Usage

### Compare All Methods

Generate prompts with all three methods (no images created):
```bash
cd src
../venv/Scripts/python test_prompt_comparison.py
```

This shows you the difference between methods on the first sentence of Chapter 1.

### Generate Images with Specific Method

**Using Keyword (default):**
```bash
../venv/Scripts/python generate_scene_images.py --chapters 1
```

**Using Claude Haiku:**
```bash
../venv/Scripts/python generate_scene_images.py --chapters 1 --llm haiku
```

**Using Ollama (requires Ollama running):**
```bash
../venv/Scripts/python generate_scene_images.py --chapters 1 --llm ollama
```

**Comparison mode (saves all prompts, no images):**
```bash
../venv/Scripts/python generate_scene_images.py --chapters 1 --llm compare --dry-run
```

## Prompt Quality Comparison

### Example Sentence
> "Emma Chen checked the line supervisor's tablet and smiled."

### Keyword Method (Original)
```
A Asian American woman 40s, dark hair, business attire, analytical in a
factory with neutral mood. clean graphic novel illustration, professional
comic book art, sharp focus, highly detailed, clear composition, bold clean
lines, single subject focus, uncluttered background, high contrast
```

**Issues:**
- Misses the tablet entirely
- Misses the smile
- Generic "factory" setting
- Wrong mood ("neutral" when she's smiling)

### Claude Haiku Method (LLM)
```
Detailed comic book illustration of Emma Chen smiling confidently, checking
digital tablet screen in industrial setting, wearing professional business
attire, clean lines, sharp focus, high contrast, bold graphic novel style,
uncluttered workspace background
```

**Improvements:**
- ✅ Captures the tablet specifically
- ✅ Captures the smile and confidence
- ✅ Uses Emma's name
- ✅ Better action description
- ✅ More specific to the sentence

## Cost Estimate

**Claude Haiku pricing (as of Dec 2024):**
- Input: $0.25 per million tokens
- Output: $1.25 per million tokens

**For this novel:**
- ~192 sentences per chapter × 12 chapters = ~2,300 sentences
- ~300 tokens input + ~50 tokens output per sentence
- Total cost: ~$1-2 for all 12 chapters

**Much cheaper than regenerating bad images!**

## Ollama Setup (Optional)

For free local LLM generation:

1. Download Ollama from https://ollama.com/download
2. Install and start Ollama
3. Pull the model:
   ```bash
   ollama pull llama3.1:8b
   ```
4. Verify it's running:
   ```bash
   ollama list
   ```

Quality is slightly lower than Haiku but still better than keyword method.

## Files Modified

- [`src/config.py`](../src/config.py) - Added LLM configuration, loads `.env`
- [`src/prompt_generator.py`](../src/prompt_generator.py) - Added LLM generation functions
- [`src/generate_scene_images.py`](../src/generate_scene_images.py) - Added `--llm` flag
- [`src/test_prompt_comparison.py`](../src/test_prompt_comparison.py) - New test script
- [`.env.example`](../.env.example) - Configuration template

## Recommendation

**Use Claude Haiku** for image generation:
- Best quality prompts that match sentence content
- Minimal cost (~$1-2 for entire novel)
- No local setup required
- Faster than Ollama

Only use keyword method for quick testing or if you want to avoid API costs entirely.
