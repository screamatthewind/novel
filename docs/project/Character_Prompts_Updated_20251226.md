# Character Reference Prompts - Updated for Illustrated Style

**Date:** 2025-12-26
**Status:** ✅ COMPLETE - Prompts updated for graphic novel illustration style

## What Was Changed

Updated [src/generate_character_references.py](../../src/generate_character_references.py) to generate **illustrated character references** instead of photographic portraits.

### Problem Identified
- Original prompts used "professional portrait **photograph**" language
- Negative prompts **blocked** illustration styles
- Generated photorealistic images unsuitable for YouTube video production

### Solution Implemented
- Changed all prompts to "**graphic novel character reference**" style
- Updated to use illustration/comic book art terminology
- Modified negative prompts to **allow** illustration while blocking photographs

## Changes Made

### File Modified
**[src/generate_character_references.py](../../src/generate_character_references.py)** (Lines 15-67)

### Before → After

**Base Prompt Style:**
- ❌ Before: "professional portrait photograph of..."
- ✅ After: "graphic novel character reference, [character], comic book illustration style, clean character design, digital art, concept art"

**Technical Terms:**
- ❌ Removed: "studio lighting", "professional headshot", "sharp focus", "natural lighting"
- ✅ Added: "comic book illustration style", "clean character design", "digital art", "concept art", "graphic novel style", "cel shading"

**Variations:**
- ❌ Before: "front-facing portrait", "slight angle portrait"
- ✅ After: "front view character portrait", "three-quarter view", "character design"

**Negative Prompt:**
- ❌ Before: Blocked "illustration, painting, drawing, art, sketch"
- ✅ After: Blocks "photograph, photo, photorealistic, realistic photo, 3d render"

## Updated Character Prompts

All 6 characters updated with consistent illustrated style:

### Emma Chen
**Base:** "graphic novel character reference, Asian American woman mid-40s, dark hair, intelligent analytical expression, practical business attire, sensible appearance, competent professional woman, comic book illustration style, clean character design, digital art, sharp lines, professional character concept art"

### Tyler Chen
**Base:** "graphic novel character reference, Asian American teenage boy age 16, casual clothing, slouched posture, intelligent but initially disengaged expression, modern teenager with earbuds, comic book illustration style, clean character design, digital art, concept art"

### Elena Volkov
**Base:** "graphic novel character reference, Russian American woman approximately 60 years old, short gray hair, sharp penetrating eyes that take in everything, slight frame, intellectually rigorous appearance, analytical demeanor, comic book illustration style, clean character design, digital art, concept art"

### Maxim Orlov
**Base:** "graphic novel character reference, Russian working-class man mid-40s, hands that know labor, practical working-class appearance, resilient and weathered features, factory worker, comic book illustration style, clean character design, digital art, concept art"

### Amara Okafor
**Base:** "graphic novel character reference, Kenyan woman late 40s to early 50s, former government minister, fierce and pragmatic appearance, professional attire, carries weight of responsibility, comic book illustration style, clean character design, digital art, concept art"

### Wei Chen
**Base:** "graphic novel character reference, Chinese man, intellectual strategist appearance, brilliant analytical demeanor, professional business attire, cold analytical expression, comic book illustration style, clean character design, digital art, concept art"

## Validation Against Novel Bible

All character descriptions remain **100% faithful** to canonical descriptions in [The_Obsolescence_Novel_Bible.md](../reference/The_Obsolescence_Novel_Bible.md:85-202):

| Character | Age | Ethnicity | Canon Alignment |
|-----------|-----|-----------|-----------------|
| Emma Chen | Mid-40s | Asian American | ✅ Matches |
| Tyler Chen | 16 | Asian American | ✅ Matches |
| Elena Volkov | ~60 | Russian American | ✅ Matches |
| Maxim Orlov | Mid-40s | Russian | ✅ Matches |
| Amara Okafor | Late 40s-50s | Kenyan | ✅ Matches |
| Wei Chen | Not specified | Chinese | ✅ Matches |

## Next Steps

### To Generate Character References
```bash
cd src
../venv/Scripts/python generate_character_references.py --characters all
```

**Or in VS Code:** Press F5 → Select "CharRef: Generate All Characters"

### Expected Output
- Illustrated character designs (NOT photographs)
- Comic book/graphic novel style artwork
- Suitable for YouTube video production
- Consistent visual style across all characters

## Important Notes

### Project Context
This project creates **YouTube videos with illustrated scenes** for "The Obsolescence" novel:
- Scene images generated in illustrated/graphic novel style
- Character references used by IP-Adapter for face consistency
- Audio generated with TTS (Chatterbox)
- Combined into videos with MoviePy

### Reference Documents (Stable Canon)
The following docs/ files define the project and **rarely change**:
- [The_Obsolescence_Novel_Bible.md](../reference/The_Obsolescence_Novel_Bible.md) - Character descriptions, world-building (SOURCE OF TRUTH)
- [The_Obsolescence_Novel_Outline.md](../reference/The_Obsolescence_Novel_Outline.md) - Story structure, emotional arcs

**Always validate character prompts against the Novel Bible.**

## Files Modified

- ✅ [src/generate_character_references.py](../../src/generate_character_references.py) - Updated CHARACTER_PROMPTS dictionary and NEGATIVE_PROMPT

## Related Documentation

- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Overall project status
- [Phase_2_IP_Adapter_Summary.md](Phase_2_IP_Adapter_Summary.md) - Character consistency system
- [The_Obsolescence_Novel_Bible.md](../reference/The_Obsolescence_Novel_Bible.md) - Canonical character descriptions
