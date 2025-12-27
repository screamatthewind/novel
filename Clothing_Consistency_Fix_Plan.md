# Clothing Consistency Fix Plan
**Date:** 2025-12-27
**Status:** Ready for Implementation

## Problem Statement

Emma's face remains consistent across storyboard images (via IP-Adapter FaceID), but her **clothing varies randomly** between sentences. This breaks visual continuity for the storyboard.

**Canonical Outfit (from [character_attributes.py](../../src/character_attributes.py)):**
- Navy blue fitted blazer
- Crisp white button-up shirt
- Black slacks
- Black leather flats

**Current State:** ~40% of images show correct outfit
**Target State:** 90%+ consistency

## Root Causes

### 1. Reference Images Show Wrong Outfits
**Location:** [character_references/emma/](../../character_references/emma/)

The 8 reference portraits used by IP-Adapter show Emma in varying clothing:
- Reference 1: Beige/tan blazer with white shirt
- Reference 4: Gray blazer with light blue shirt
- Others: Various "business attire" interpretations

**Impact:** IP-Adapter's CLIP encoder learns inconsistent clothing patterns from these references.

### 2. Prompt Compression Drops Clothing
**Location:** [src/attribute_state_manager.py:139](../../src/attribute_state_manager.py#L139)

When prompts exceed 77 tokens (SDXL limit), progressive compression occurs:
```python
# Current logic (BROKEN):
elif max_tokens >= 12:
    parts = [self.face, self.clothing]
else:
    return self.face  # ❌ CLOTHING DROPPED!
```

**Impact:** When token budget is tight, clothing descriptions are completely removed.

### 3. Vague Metadata Description
**Location:** [character_references/emma/metadata.json:4](../../character_references/emma/metadata.json#L4)

Current description: `"practical business attire"`
**Impact:** Too generic, doesn't specify the exact canonical outfit.

## Solution Overview

Three-tier implementation focusing on high-impact, low-complexity fixes first.

### TIER 1: Foundation Fixes (High Impact)

#### Fix 1: Regenerate Emma's Reference Images ⭐ CRITICAL
**File to Create:** [src/regenerate_emma_references.py](../../src/regenerate_emma_references.py)

Generate 8 new reference portraits with **identical clothing**:
- Seeds: 42-50 (for facial variation)
- Prompt: `"mid-40s Asian American woman, intelligent brown eyes, wearing navy blue fitted blazer, crisp white button-up shirt, black slacks, professional standing pose, neutral gray background, portrait photography"`
- Output: Replace all files in [character_references/emma/](../../character_references/emma/)
- Backup old references to `character_references/emma/old_backup/`

**Why this works:** IP-Adapter's CLIP encoder will learn consistent clothing patterns from uniform references.

**Expected Impact:** 40-60% improvement immediately.

---

#### Fix 2: Make Clothing REQUIRED in Compression ⭐ CRITICAL
**File to Modify:** [src/attribute_state_manager.py](../../src/attribute_state_manager.py) (lines 107-141)

```python
def to_compressed_string(self, max_tokens: int = 15) -> str:
    """Never compress below face + clothing minimum."""
    if max_tokens >= 25:
        return self.to_prompt_string()
    elif max_tokens >= 18:
        parts = [self.face, self.hair, self.clothing]
        return ", ".join(parts)
    else:
        # CRITICAL: NEVER drop below face + clothing
        # Even if max_tokens is 5, we MUST include clothing
        parts = [self.face, self.clothing]
        return ", ".join(parts)
```

**Expected Impact:** 100% of prompts will include clothing (vs current ~40%).

---

#### Fix 3: Compress BASE_STYLE to Free Tokens
**File to Modify:** [src/config.py](../../src/config.py) (line 76)

```python
# OLD (15 tokens):
BASE_STYLE = "clean graphic novel illustration, professional comic book art, sharp focus, highly detailed, clear composition, bold clean lines, single subject focus, uncluttered background, high contrast"

# NEW (10 tokens):
BASE_STYLE = "graphic novel art, sharp focus, detailed, clean lines, high contrast, professional comic style"
```

**Expected Impact:** Frees 5 tokens for character clothing descriptions.

---

#### Fix 4: Update Emma's Metadata
**File to Modify:** [character_references/emma/metadata.json](../../character_references/emma/metadata.json) (line 4)

```json
{
  "description": "Asian American woman mid-40s, dark hair, intelligent analytical expression, navy blue fitted blazer, crisp white button-up shirt, black slacks, professional appearance"
}
```

---

### TIER 2: Token Budget Optimization (After Tier 1 Validated)

#### Optimize Prompt Generation Strategy
**File to Modify:** [src/prompt_generator.py](../../src/prompt_generator.py) (lines 728-740)

**Current Problem:** Starts with 20-token character description, then compresses if needed.
**New Strategy:** Start with guaranteed minimum (face + clothing), then add extras.

```python
if attribute_manager:
    char_state = attribute_manager.get_current_attributes(primary_char)
    if char_state:
        # GUARANTEED MINIMUM: face + clothing (never less)
        char_desc = char_state.to_compressed_string(max_tokens=15)
    else:
        char_desc = get_compressed_description(primary_char, max_tokens=15)
```

**Token Budget Reallocation:**
```
CURRENT:
- Camera: 8 tokens
- Character: 25-30 tokens (often compressed to 8!)
- Action: 8 tokens
- Mood: 5 tokens
- Style: 15 tokens
- Spatial: 15 tokens

OPTIMIZED:
- Camera: 5 tokens
- Character (face + clothing REQUIRED): 15 tokens
- Expression: 3 tokens
- Action: 5 tokens
- Style: 10 tokens (compressed)
- Visual focus: 5 tokens
- Buffer: 34 tokens (for mood/composition)
```

---

### TIER 3: Validation & Testing (Optional)

#### Validation Script
**File to Create:** [src/validate_clothing_consistency.py](../../src/validate_clothing_consistency.py)

- Generate 20 test images of Emma from Chapter 1
- Use Claude Vision API to verify: "Is this person wearing a navy blue blazer and white shirt?"
- Report consistency percentage
- Target: 90%+ accuracy

**Cost:** ~$0.06 for 20 validations ($0.003 per image)

#### Unit Test
**File to Create:** [src/tests/test_clothing_compression.py](../../src/tests/test_clothing_compression.py)

```python
def test_compression_never_drops_clothing():
    """Ensure clothing is never removed during compression."""
    manager = AttributeStateManager(chapter_num=1)
    emma = manager.get_current_attributes("emma")

    for token_limit in [77, 50, 30, 20, 15, 12, 10, 5]:
        compressed = emma.to_compressed_string(max_tokens=token_limit)
        assert "blazer" in compressed.lower() or "clothing" in compressed.lower()
```

---

## Implementation Steps

### Step 1: Regenerate References
1. Create [regenerate_emma_references.py](../../src/regenerate_emma_references.py)
2. Run script: `python src/regenerate_emma_references.py`
3. Visual QA: Verify all 8 images show navy blazer + white shirt
4. Backup old references
5. Replace with new references

**Time Estimate:** 30 minutes (8 images × 5-7 min generation time)

---

### Step 2: Update Compression Logic
1. Edit [attribute_state_manager.py:139](../../src/attribute_state_manager.py#L139) to never return face-only
2. Edit [config.py:76](../../src/config.py#L76) to compress BASE_STYLE
3. Edit [metadata.json:4](../../character_references/emma/metadata.json#L4) with exact outfit

**Time Estimate:** 15 minutes

---

### Step 3: Test Initial Results
1. Generate 20 Emma images from Chapter 1 scenes
2. Visual inspection: Count how many show navy blazer + white shirt
3. Success threshold: 80%+ consistency

**Time Estimate:** 45 minutes (generation + review)

---

### Step 4: Optimize Token Budget (If Needed)
1. Edit [prompt_generator.py:728-740](../../src/prompt_generator.py#L728-L740)
2. Ensure character minimum is always face + clothing
3. Re-test with 20 more images
4. Success threshold: 90%+ consistency

**Time Estimate:** 30 minutes

---

### Step 5: Create Validation Tools (Optional)
1. Create validation script
2. Create unit tests
3. Run automated validation on 50 images

**Time Estimate:** 1 hour

---

### Step 6: Expand to Other Characters
Apply same fixes to Tyler, Elena, Maxim, Amara:
1. Regenerate reference images with canonical outfits
2. Update metadata.json descriptions
3. Validate consistency

**Time Estimate:** 1 hour per character

---

## Success Criteria

- ✅ **90%+ of Emma images** show correct outfit (navy blazer, white shirt, black slacks)
- ✅ **100% of prompts** include clothing description (verified via logs)
- ✅ **No quality degradation** in facial consistency, composition, or lighting
- ✅ **Same performance:** 5-7 min per image generation time

## Risk Mitigation

| Risk | Mitigation | Fallback |
|------|------------|----------|
| New references break facial consistency | Test 10 images before full replacement | Keep old references backed up |
| Clothing compression too aggressive | Accept 85-90% threshold | Dynamic minimum (12-15 tokens) |
| BASE_STYLE compression hurts quality | A/B test 5 images before/after | Revert to 12-token version |

## Files Summary

### Files to Modify
1. [src/attribute_state_manager.py](../../src/attribute_state_manager.py) - Lines 107-141
2. [src/config.py](../../src/config.py) - Line 76
3. [character_references/emma/metadata.json](../../character_references/emma/metadata.json) - Line 4
4. [src/prompt_generator.py](../../src/prompt_generator.py) - Lines 728-740 (Tier 2)

### Files to Create
1. [src/regenerate_emma_references.py](../../src/regenerate_emma_references.py) - Reference generation script
2. [src/validate_clothing_consistency.py](../../src/validate_clothing_consistency.py) - Validation script (optional)
3. [src/tests/test_clothing_compression.py](../../src/tests/test_clothing_compression.py) - Unit tests (optional)

## Future Enhancements (Deferred)

**Not included in this plan** - evaluate after Tier 1-2 results:

- **Flux.1 Migration:** 512-token limit (vs SDXL's 77) eliminates all compression issues
- **ControlNet:** Add pose/clothing structure guidance (requires 1-2GB extra VRAM)
- **Character LoRA:** Train custom LoRA on Emma's exact outfit (requires 50-100 training images, 4-hour training)

These are unnecessary if we achieve 90%+ consistency with Tier 1-2 fixes.

---

## Technical Background

### Why IP-Adapter FaceID Ensures Face Consistency
- Extracts 512-dim face embedding using InsightFace (CPU)
- Encodes reference image with CLIP for image embedding
- Both embeddings passed to IP-Adapter during generation
- `ip_adapter_scale`: 0.75 (image embedding influence)
- `faceid_scale`: 0.6 (face structure influence)

**Key Insight:** FaceID encodes facial features ONLY, not clothing. CLIP encoder includes clothing, but text prompts have stronger influence.

### Why Clothing Varies
1. IP-Adapter references show different outfits → CLIP learns inconsistent patterns
2. Text prompts often omit clothing due to compression → SDXL improvises
3. Without clothing in prompt, SDXL interprets generic "business attire" differently each time

### The Fix
1. Uniform reference images → Consistent CLIP patterns
2. Guaranteed clothing in prompts → No improvisation
3. Exact metadata → Clear specifications

---

## Related Documentation

- [Character Attributes System](../../src/character_attributes.py)
- [Attribute State Manager](../../src/attribute_state_manager.py)
- [Storyboard Implementation Guide](STORYBOARD_IMPLEMENTATION_GUIDE.md)
- [Character References Quick Guide](Character_References_Quick_Guide.md)
- [Troubleshooting](TROUBLESHOOTING.md)
