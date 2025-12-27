# Character Consistency Investigation Plan

## Problem Statement

Emma Chen's appearance changes dramatically between sentence 1 and sentence 2 of Chapter 1, Scene 1:

- **Sentence 1**: Asian woman with distinct features, darker skin, work coveralls/apron
- **Sentence 2**: Much lighter skin, less Asian features, different outfit (white jacket), different hairstyle

Despite IP-Adapter FaceID Plus V2 being enabled and configured.

## Initial Investigation Findings

### What's Working
1. IP-Adapter FaceID is enabled and loaded
2. Character reference system is in place with 8 reference images for Emma
3. Face embeddings are being generated and averaged from multiple references
4. Character detection is working (both images detected "emma chen" character)
5. Storyboard analysis is providing consistent character metadata

### Reference Images Analysis
Emma's reference images (emma_ref_01 through emma_ref_08) show:
- Consistent Asian features
- Professional business attire (suits, jackets)
- Dark hair typically pulled back in bun/ponytail
- Clear Asian American appearance matching Novel Bible description

### Generated Images Analysis
- **Sentence 1**: Uses IP-Adapter, shows Asian woman in work coveralls
- **Sentence 2**: Uses IP-Adapter, but shows different features - lighter skin, different clothing

### Prompts Used
**Sentence 1**: `medium shot, slightly low, empowering angle. emma chen. hand moving while returning tablet. focus on tablet screen and Emma's hand. in industrial manufacturing floor. professional satisfaction, bright, clinical indust.`

**Sentence 2**: `medium shot over-shoulder, slightly low. emma chen. focus on Tablet screen showing production metrics. in Manufacturing floor. professional satisfaction, bright, industrial over.`

## ROOT CAUSE CONFIRMED ✓

**Sentence 2 did NOT use IP-Adapter at all!**

### Evidence from Logs
- Sentence 1: `-> Using character reference: emma` ✓
- Sentence 2: NO "Using character reference" message ✗

### Why This Happened

The character detection logic in [src/generate_scene_images.py:299-317](src/generate_scene_images.py#L299-L317) uses `extract_characters()` which only searches for character names **in the sentence text**:

```python
characters = extract_characters(sentence.content)  # Line 303
```

**Sentence 1**: "Emma Chen checked the line supervisor's tablet and smiled."
- Contains "Emma" → `extract_characters()` returns `["emma"]` → IP-Adapter used ✓

**Sentence 2**: "Production was ahead of schedule."
- Does NOT contain "Emma" → `extract_characters()` returns `[]` → NO IP-Adapter ✗
- Falls back to standard SDXL generation
- Different person generated each time!

### The Problem

The `extract_characters()` function ([src/prompt_generator.py:64-83](src/prompt_generator.py#L64-L83)) is too simplistic:
```python
def extract_characters(text: str) -> list:
    """Extract character names mentioned in the scene."""
    characters = []
    text_lower = text.lower()

    # Check for each known character
    if "emma" in text_lower:
        characters.append("emma")
    # ... etc
```

This fails for:
- Sentences without explicit character names
- Sentences with pronouns ("She smiled")
- Sentences describing actions ("The tablet displayed...")
- Narrative sentences like "Production was ahead of schedule"

## IMPLEMENTATION PLAN

### Solution: Use Storyboard Analysis for Character Detection

Replace character detection in [src/generate_scene_images.py:299-317](src/generate_scene_images.py#L299-L317) to use storyboard `characters_present` instead of naive keyword extraction.

### Code Changes

**File**: `src/generate_scene_images.py`
**Lines**: 299-317

**Replace with**:
```python
# Detect character and use IP-Adapter if enabled
character_name = None
if generator.enable_ip_adapter and generator.ip_adapter_loaded:
    # Map character full names to short names for metadata lookup
    char_mapping = {
        'emma': 'emma', 'emma chen': 'emma',
        'tyler': 'tyler', 'tyler chen': 'tyler',
        'elena': 'elena', 'elena volkov': 'elena',
        'maxim': 'maxim', 'maxim orlov': 'maxim',
        'amara': 'amara', 'amara okafor': 'amara',
        'wei': 'wei', 'wei chen': 'wei'
    }

    # Try storyboard analysis first (more reliable than keyword extraction)
    characters = []
    if storyboard_analysis and storyboard_analysis.characters_present:
        # Extract characters from storyboard analysis
        storyboard_chars = storyboard_analysis.characters_present
        log_message(log_file, f"-> Storyboard characters: {storyboard_chars}")

        # Map full names to short names
        for char in storyboard_chars:
            char_lower = char.lower()
            if char_lower in char_mapping:
                characters.append(char_mapping[char_lower])

        # Prioritize "acting" characters over "referenced" ones
        if characters and storyboard_analysis.character_roles:
            acting_chars = [
                char for char in characters
                if any(
                    role in ['acting', 'acting/speaking', 'acting/listening']
                    for name, role in storyboard_analysis.character_roles.items()
                    if name.lower() in char_mapping and char_mapping[name.lower()] == char
                )
            ]
            if acting_chars:
                character_name = acting_chars[0]  # Use first acting character
            else:
                character_name = characters[0]  # Fall back to first character
        elif characters:
            character_name = characters[0]

    # Fallback: Extract characters from sentence text (original method)
    if not character_name:
        characters = extract_characters(sentence.content)
        for char in characters:
            if char in char_mapping:
                character_name = char_mapping[char]
                break
```

### How It Works

1. **Primary**: Use `storyboard_analysis.characters_present` (e.g., `["Emma Chen", "Ramirez"]`)
2. **Map**: Convert full names to short names using `char_mapping` (`"Emma Chen"` → `"emma"`)
3. **Prioritize**: Prefer "acting" characters from `character_roles`
4. **Fallback**: If no storyboard, use original `extract_characters(sentence.content)` method

### Testing

```bash
cd src
../venv/Scripts/python generate_scene_images.py --chapters 1 --enable-storyboard --enable-ip-adapter --dry-run
```

**Expected output for sentence 2**:
```
Sentence: Production was ahead of schedule.
-> Storyboard characters: ['Emma Chen', 'Ramirez']
-> Acting characters: ['emma']
-> Selected character: emma
-> Using character reference: emma
```

### Success Criteria

- ✓ Sentence 2 uses IP-Adapter for Emma (currently fails)
- ✓ Backward compatible (non-storyboard mode still works)
- ✓ Graceful fallback for missing data
- ✓ Emma's appearance consistent across all scene 1 sentences

## Critical Files
- **[src/generate_scene_images.py:299-317](src/generate_scene_images.py#L299-L317)** - MODIFY: Character detection logic
- [src/storyboard_analyzer.py](src/storyboard_analyzer.py) - Reference: Storyboard data structure
- [src/prompt_generator.py:64-83](src/prompt_generator.py#L64-L83) - Reference: Fallback extraction function
- [storyboard_cache/01/](storyboard_cache/01/) - Reference: Cached storyboard data
