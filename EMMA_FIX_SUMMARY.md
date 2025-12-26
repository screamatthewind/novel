# Emma Character Reference Fix - Summary

**Date**: 2025-12-26
**Status**: ✅ FIXED AND TESTED

## Problem
Generated images of Emma looked nothing like the reference images in `character_references/emma/`.

## Root Causes Identified

### 1. Wrong Model Weights
- **Before**: Used `ip-adapter-plus-face_sdxl_vit-h.safetensors` (standard IP-Adapter)
- **After**: Using `ip-adapter-faceid-plusv2_sdxl.bin` (FaceID Plus V2 for SDXL)
- **Impact**: Wrong model architecture caused state_dict loading errors

### 2. Missing `face_image` Parameter
- **Before**: Only passed FaceID embeddings to IP-Adapter
- **After**: Pass BOTH reference PIL image AND FaceID embeddings
- **Impact**: IP-Adapter Plus requires dual-pathway input for full character consistency

### 3. Missing `scale` Parameter
- **Before**: IP-Adapter scale parameter not passed
- **After**: Pass `scale` parameter to control image embedding influence
- **Impact**: Without this, the reference image had no influence on generation

### 4. Incorrect `num_tokens`
- **Before**: Set to 16 tokens
- **After**: Set to 4 tokens (correct for FaceID Plus V2)
- **Impact**: Caused tensor dimension mismatches during weight loading

## Files Modified

### 1. `src/config.py` (Lines 142-147)
```python
IP_ADAPTER_MODEL = "h94/IP-Adapter-FaceID"
IP_ADAPTER_SUBFOLDER = ""
IP_ADAPTER_WEIGHT_NAME = "ip-adapter-faceid-plusv2_sdxl.bin"
```

### 2. `src/image_generator.py` (Lines 250-309)
- Modified `get_character_reference()` to load PIL Images
- Returns both image paths and PIL Images for dual-pathway encoding

### 3. `src/image_generator.py` (Lines 446-460)
- Added `face_image=reference_image` parameter
- Added `scale=ip_scale` parameter
- Set `num_tokens=4`

## How It Works Now

The system uses **dual-pathway character consistency**:

1. **FaceID Embeddings** (InsightFace):
   - Extracts facial geometry/structure from reference images
   - Averaged across 5 reference images for robustness
   - Passed via `faceid_embeds` parameter

2. **CLIP Image Embeddings**:
   - Captures visual appearance, colors, style from reference image
   - Uses first reference image as primary visual guide
   - Passed via `face_image` parameter

3. **Scale Parameters**:
   - `scale` (IP-Adapter): Controls CLIP image embedding influence (default: 0.75)
   - `s_scale` (FaceID): Controls facial structure influence (default: 0.6)

## Usage

### From launch.json (VSCode)
Run any of these configurations:
- **Image: Dry Run - Chapter 1** - Preview prompts without generating
- **Image: Chapter 1** - Generate Chapter 1 with Emma character consistency
- **Image: ALL Chapters** - Generate all chapters

### From Command Line
```bash
cd src

# Dry run (preview only)
../venv/Scripts/python generate_scene_images.py --chapters 1 --enable-ip-adapter --dry-run

# Full generation
../venv/Scripts/python generate_scene_images.py --chapters 1 --enable-ip-adapter --llm haiku
```

## Character Detection
IP-Adapter automatically activates when these character names are detected in sentences:
- Emma / Emma Chen
- Tyler / Tyler Chen
- Elena / Elena Volkov
- Maxim / Maxim Orlov
- Amara / Amara Okafor
- Wei / Wei Chen

## Test Results
✅ IP-Adapter FaceID Plus loaded successfully
✅ Used 5 Emma reference images with embedding averaging
✅ Generated test image with proper character consistency
✅ All launch.json configurations verified

## Next Steps
The fix is complete and tested. You can now:
1. Generate images for any chapter using launch.json
2. Emma will automatically match her reference images
3. Same system applies to all other characters with reference images
