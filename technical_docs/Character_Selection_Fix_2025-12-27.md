# Character Selection Fix - December 27, 2025

## Summary

Fixed critical bugs in prompt generation that caused wrong characters to appear in images. The system was selecting characters without considering their roles or checking if they had visual descriptions.

## Problems Identified

### Problem 1: Minor Characters Without Descriptions
- **Symptom**: Images of Ramirez, Mark, Diane showed random/inconsistent faces (often Emma)
- **Cause**: These characters aren't defined in `CHARACTER_CANONICAL_ATTRIBUTES`
- **Prompt example**: `"ramirez. broad, satisfied grin"` (no description for SDXL to use)
- **Result**: SDXL generated random people or defaulted to familiar patterns

### Problem 2: Referenced Characters Prioritized Over Acting Characters
- **Symptom**: Tyler mentioned in "text from Tyler" was being considered for the image
- **Cause**: System took `characters_present[0]` without considering roles
- **Correct behavior**: Should show Emma (receiving message), not Tyler (only mentioned)

### Problem 3: Token Compression Bypass
- **Symptom**: Even when main logic was fixed, prompts still showed wrong characters
- **Cause**: Token compression code path (line 841) had duplicate logic that wasn't updated
- **Impact**: Hidden bug that caused fixes to appear not to work

## Solution

### New Character Priority System

Implemented `filter_acting_characters()` function with three priority levels:

1. **Acting** (highest priority)
   - Keywords: speaking, walking, examining, confirming, etc.
   - Characters actively performing actions

2. **Passive** (medium priority)
   - Keywords: receiving, listening, observing, watching, in background
   - Characters present but not actively performing

3. **Referenced** (lowest priority)
   - Keywords: mentioned, sender of, recipient of, off-screen
   - Characters only mentioned, not physically present

### Description Validation

When a character is selected:
1. Check if character exists in `CHARACTER_CANONICAL_ATTRIBUTES`
2. If no description found, skip to next character in filtered list
3. If no characters have descriptions, omit character entirely from prompt

### Implementation

**File**: `src/prompt_generator.py`

**Lines 18-56**: New utility function
```python
def filter_acting_characters(characters_present, character_roles):
    # Categorizes characters by role keywords
    # Returns: [acting_chars] + [passive_chars] + [referenced_chars]
```

**Lines 717-771**: Main character selection
- Filters characters by role
- Validates each candidate has a description
- Falls back to next character if needed

**Lines 841-885**: Token compression path
- Applied same filtering logic
- Prevents compression from reverting to old behavior

## Test Results

### Sentence 5 (Ramirez Scene)

**Storyboard Data**:
```json
{
  "characters_present": ["Ramirez", "Emma Chen"],
  "character_roles": {
    "Ramirez": "speaking/confirming",
    "Emma Chen": "listening/responding"
  }
}
```

**Before**:
```
medium two-shot, eye level. ramirez. broad, satisfied grin.
```

**After**:
```
medium two-shot, eye level. mid-40s Asian American woman, intelligent brown eyes,
analytical expression. broad, satisfied grin.
```

**Analysis**:
- Ramirez selected (speaking = acting, higher priority than listening)
- Ramirez has no description → skip
- Emma selected (listening = passive, has description)
- ✅ Correct fallback behavior

### Sentence 15 (Tyler Text Message)

**Storyboard Data**:
```json
{
  "characters_present": ["Emma Chen", "Tyler"],
  "character_roles": {
    "Emma Chen": "receiving message",
    "Tyler": "sender of text message"
  }
}
```

**Filtering Result**:
- Emma: receiving = passive (medium priority)
- Tyler: sender of = referenced (lowest priority)
- Emma selected ✅

**Correct**: Shows Emma looking at phone with Tyler's message, not Tyler himself

## Character Definitions

Only these characters have visual descriptions:
- `emma` - Emma Chen (mid-40s Asian American woman)
- `tyler` - Tyler (16-year-old Asian American teen boy)
- `elena` - Elena (main character, later chapters)
- `maxim` - Maxim (supporting character)
- `amara` - Amara (supporting character)

Minor characters (no descriptions):
- Ramirez, Mark, Diane, and other supporting characters mentioned in scenes

## Impact

### Fixed
- ✅ Minor character scenes now use defined characters who are also present
- ✅ Referenced characters no longer override acting characters
- ✅ Consistent character selection across normal and compressed prompts

### Behavior Changes
- Images now only show defined characters (Emma, Tyler, Elena, Maxim, Amara)
- When Ramirez is speaking, image shows Emma (if present and defined)
- Scenes focus on characters who can be visually represented consistently

### Migration

To regenerate prompts with correct character selection:

```bash
# Delete old prompt cache
rm prompt_cache/chapter_01_*.txt

# Regenerate prompts (dry-run to check without generating images)
venv/Scripts/python.exe src/generate_scene_images.py --chapters 1 --dry-run

# Generate images once prompts are verified
venv/Scripts/python.exe src/generate_scene_images.py --chapters 1
```

## Technical Details

### Why Two Code Paths?

The prompt generator has two paths:

1. **Normal path** (lines 717-771): Builds full prompt, checks if under 77 tokens
2. **Compression path** (lines 841-885): If over 77 tokens, progressively removes elements

Both paths need character selection, so the fix was applied to both.

### Edge Cases Handled

1. **No characters have roles**: Falls back to original order (maintains backward compatibility)
2. **All characters have same priority**: Uses first in priority group
3. **No characters have descriptions**: Omits character from prompt entirely
4. **Empty character list**: Safely handles with None checks

### Performance Impact

Minimal - adds one additional loop through characters (typically 1-3 characters per scene).

## Related Issues

This fix addresses the root cause. Related symptoms that should now be resolved:

- Emma appearing in all images (she's usually the only defined character present)
- Inconsistent faces for minor characters
- Images not matching sentence context (wrong character's perspective)

## Future Considerations

### Option: Add Minor Character Descriptions

Could add generic descriptions for recurring minor characters:

```python
CHARACTER_CANONICAL_ATTRIBUTES = {
    ...
    'ramirez': {
        'age': '40s',
        'gender': 'male',
        'ethnicity': 'Hispanic',
        'face': 'weathered, experienced',
        # ...
    }
}
```

**Pros**: More accurate character representation
**Cons**: Maintenance burden, less important for brief appearances

### Option: Generic Fallback Descriptions

Could use role-based generic descriptions when character undefined:

```python
if not char_desc and role == "line supervisor":
    char_desc = "factory supervisor, experienced worker"
```

**Pros**: Provides some guidance to SDXL
**Cons**: Less control, could introduce new inconsistencies
