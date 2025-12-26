# Character References - Quick Reference Guide

## System Status: ✅ FULLY OPERATIONAL (as of 2025-12-26)

---

## Quick Start

Generate scene images with character consistency:

```bash
cd src

# Single chapter
../venv/Scripts/python generate_scene_images.py --chapters 1 --enable-ip-adapter

# Multiple chapters
../venv/Scripts/python generate_scene_images.py --chapters 1 2 3 --enable-ip-adapter

# All chapters (WARNING: ~19 hours per chapter!)
../venv/Scripts/python generate_scene_images.py --chapters 1 2 3 4 5 6 7 8 9 10 11 12 --enable-ip-adapter
```

---

## Character Coverage

| Character | Chapters | Reference Images | Status |
|-----------|----------|------------------|--------|
| Emma Chen | 1-12 | 8 images | ✅ Working |
| Tyler Chen | 1-3 | 8 images | ✅ Working |
| Elena Volkov | 4 | 8 images | ✅ Working |
| Maxim Orlov | 4-5 | 8 images | ✅ Working |
| Amara Okafor | 5 | 8 images | ✅ Working |
| Wei Chen | 6-9 | 8 images | ✅ Working |

---

## How to Verify System is Working

### Test 1: Character Detection
```bash
cd src
../venv/Scripts/python -c "from prompt_generator import extract_characters; print(extract_characters('Emma walked into the room with Wei'))"
```
**Expected output**: `['emma', 'wei']`

### Test 2: Reference Loading
```bash
cd src
../venv/Scripts/python -c "from image_generator import SDXLGenerator; gen = SDXLGenerator(); ref = gen.get_character_reference('emma'); print(f'Loaded {len(ref[\"pil_images\"])} images')"
```
**Expected output**: `Loaded 5 images`

### Test 3: Check Logs for Character Usage
After running scene generation, check the log file:
```bash
grep -i "Using character reference" logs/generation_*.log
```
**Expected**: Lines showing `-> Using character reference: emma`, `-> Using character reference: wei`, etc.

---

## Character Reference Files

```
character_references/
├── emma/
│   ├── emma_ref_01.png through emma_ref_08.png  (8 images)
│   └── metadata.json
├── tyler/
│   ├── tyler_ref_01.png through tyler_ref_08.png
│   └── metadata.json
├── elena/
│   ├── elena_ref_01.png through elena_ref_08.png
│   └── metadata.json
├── maxim/
│   ├── maxim_ref_01.png through maxim_ref_08.png
│   └── metadata.json
├── amara/
│   ├── amara_ref_01.png through amara_ref_08.png
│   └── metadata.json
└── wei/
    ├── wei_ref_01.png through wei_ref_08.png
    └── metadata.json
```

---

## Regenerating Character References

If you need to regenerate character reference images:

```bash
cd src

# Single character
../venv/Scripts/python generate_character_references.py --characters emma --num-variations 8

# All characters
../venv/Scripts/python generate_character_references.py --characters all --num-variations 8
```

**Note**: This overwrites existing reference images. Only do this if you need to change character appearance.

---

## Configuration Settings

Located in `src/config.py`:

```python
# Character reference settings
CHARACTER_REFERENCES_DIR = "../character_references"
IP_ADAPTER_SCALE_DEFAULT = 0.75      # Overall guidance strength
FACEID_SCALE_DEFAULT = 0.6           # Face structure strength
MAX_REFERENCE_IMAGES = 5             # Use first 5 of 8 images
REFERENCE_EMBEDDING_AVERAGING = True # Average embeddings
ENABLE_IP_ADAPTER = True             # Enabled by default
```

---

## Troubleshooting

### Problem: "Using character reference" not appearing in logs

**Check**:
1. Is `--enable-ip-adapter` flag used?
2. Does the sentence contain character name (emma, tyler, wei, etc.)?
3. Do reference images exist in `character_references/{character}/`?

**Solution**:
```bash
# Verify character detection works
cd src
../venv/Scripts/python -c "from prompt_generator import extract_characters; print(extract_characters('Your test sentence here'))"
```

### Problem: Character doesn't look consistent

**Possible causes**:
- Reference images are low quality or inconsistent
- IP-Adapter scales may need tuning
- Face not clearly visible in reference images

**Solution**: Regenerate character references with better prompts

### Problem: Script crashes with Unicode error

**Status**: ✅ FIXED (2025-12-26)

If you see `UnicodeEncodeError: 'charmap' codec can't encode character`, ensure you have the latest version of `generate_scene_images.py` with ASCII symbols instead of Unicode.

---

## Technical Details

### Why 8 reference images?

- **Images 1-4**: Geometric coverage (front, 3/4 left, profile, 3/4 right)
- **Images 5-8**: Expression/lighting variations

System uses first **5 images** for embedding averaging (research-backed optimal number).

### How averaging works

```python
# Each reference image → 512-dim face embedding
emb1 = extract_face_embedding(ref_01.png)  # Front view
emb2 = extract_face_embedding(ref_02.png)  # 3/4 left
emb3 = extract_face_embedding(ref_03.png)  # Profile
emb4 = extract_face_embedding(ref_04.png)  # 3/4 right
emb5 = extract_face_embedding(ref_05.png)  # Variation

# Average all embeddings
averaged = mean([emb1, emb2, emb3, emb4, emb5])

# Result: Robust face representation across angles/lighting
```

### IP-Adapter Scales

**IP-Adapter Scale (0.75)**:
- Controls how much overall character appearance is preserved
- Higher = more faithful to references, less scene adaptation
- Lower = more scene adaptation, less character consistency

**FaceID Scale (0.6)**:
- Controls how much face structure is preserved
- Higher = stricter face matching
- Lower = more variation allowed

Current settings (0.75/0.6) provide good balance between consistency and scene flexibility.

---

## Files Involved

**Core Generation**:
- `src/generate_scene_images.py` - Main scene generation script
- `src/image_generator.py` - SDXL generator with IP-Adapter integration
- `src/prompt_generator.py` - Character detection and prompt generation

**Character References**:
- `src/generate_character_references.py` - Reference image generation
- `character_references/*/metadata.json` - Character metadata and settings

**Configuration**:
- `src/config.py` - All system settings

---

## Documentation

- **Bug Fixes**: `docs/project/Character_Reference_Bug_Fixes_2025-12-26.md`
- **Implementation**: `docs/project/Phase_2_IP_Adapter_Summary.md`
- **8-Image System**: `docs/project/Character_References_8_Image_Implementation.md`

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review bug fix documentation
3. Verify test commands still work
4. Check generation logs in `logs/generation_*.log`

Last updated: December 26, 2025
