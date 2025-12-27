# Character Attribute Consistency Fix - Implementation Plan

## Problem Summary

Character visual attributes (clothing, hair, hats, eyes, accessories) are changing randomly between consecutive sentences in generated images. Each sentence generates independently, and generic descriptions like "business attire" or "dark hair" are interpreted differently by SDXL each time.

**Root Cause**: Minimal 8-token character descriptions in `CHARACTER_DESCRIPTIONS` dict ([prompt_generator.py:15-21](src/prompt_generator.py#L15-L21)) combined with no persistence mechanism across sentences.

## Solution Overview

Implement a **three-layer attribute management system**:

1. **Canonical Attributes Layer**: Detailed baseline descriptions (25-30 tokens per character)
2. **Runtime State Manager**: Tracks current attributes per chapter, persists across sentences
3. **Enhanced Storyboard Analyzer**: Detects story-driven attribute changes (e.g., "removed her blazer")

**User Requirements**:
- Maximum detail specifications (25-30 tokens per character)
- Change attributes ONLY when story explicitly mentions it
- Enable storyboard analysis by default for attribute tracking

## Implementation Plan

### Step 1: Create Canonical Character Attributes

**CREATE**: [src/character_attributes.py](src/character_attributes.py)

Define detailed attributes for all main characters:

```python
CHARACTER_CANONICAL_ATTRIBUTES = {
    "emma": {
        "hair": "shoulder-length straight dark brown hair, NO hat, NO hair accessories",
        "face": "mid-40s Asian American woman, intelligent brown eyes, analytical expression",
        "clothing": "navy blue fitted blazer, crisp white button-up shirt, black slacks, black leather flats",
        "accessories": "NO glasses, NO jewelry, practical wristwatch",
        "skin": "light brown skin tone, professional appearance",
        "build": "average build, professional posture"
    },
    # ... tyler, elena, maxim, amara
}
```

**Functions to include**:
- `get_full_description(character)`: Combine all attributes into single string
- `get_compressed_description(character, max_tokens)`: Budget-aware compression
- `get_attribute(character, attribute_type)`: Get specific attribute (hair, clothing, etc.)

**Token Budget**: ~25-30 tokens per character full description

---

### Step 2: Create Attribute State Manager

**CREATE**: [src/attribute_state_manager.py](src/attribute_state_manager.py)

**Purpose**: Track and persist character attributes across sentences within a chapter.

**Key Classes**:

```python
@dataclass
class CharacterAttributeState:
    """Current visual state for a single character."""
    character_name: str
    hair: str
    face: str  # Read-only (IP-Adapter controls facial features)
    clothing: str
    accessories: str
    skin: str  # Read-only
    build: str  # Read-only
    last_updated_sentence: int
    change_history: list

    def to_prompt_string(self) -> str:
        """Generate SDXL-ready description (25-30 tokens)."""

    def to_compressed_string(self, max_tokens: int) -> str:
        """Generate compressed description when needed."""

class AttributeStateManager:
    """Manages character state across chapter."""

    def __init__(self, chapter_num: int)

    def initialize_character(self, character_name: str) -> CharacterAttributeState:
        """Initialize from canonical attributes."""

    def get_current_attributes(self, character_name: str) -> CharacterAttributeState:
        """Get current state (lazy initialization)."""

    def update_attribute(self, character_name, attribute_type, new_value, sentence_num, reason):
        """Update attribute when story explicitly mentions change."""

    def reset_for_new_scene(self, scene_num: int):
        """Called at '* * *' boundaries (does NOT reset attributes)."""

    def reset_for_new_chapter(self, chapter_num: int):
        """Called for new chapter (resets to canonical)."""

    def get_statistics(self) -> dict:
        """Get change statistics for logging."""
```

**Persistence Strategy**:
- Attributes persist across sentences within chapter
- Attributes persist across scenes ('* * *') within chapter
- Attributes reset to canonical at chapter boundaries
- Changes only on explicit story mentions

---

### Step 3: Enhance Storyboard Analyzer

**MODIFY**: [src/storyboard_analyzer.py](src/storyboard_analyzer.py)

**A. Add AttributeChange dataclass** (after line 19):

```python
@dataclass
class AttributeChange:
    """Specific attribute change detected in sentence."""
    character_name: str
    attribute_type: str  # "hair", "clothing", "accessories"
    old_state: str
    new_state: str
    explicit_mention: str  # Text that triggered it
    confidence: float  # 0.0-1.0
```

**B. Update StoryboardAnalysis dataclass** (line 51):

Add new field:
```python
attribute_changes: List[AttributeChange] = None
```

Update `__post_init__` to initialize to empty list.

**C. Enhance SYSTEM_PROMPT** (lines 138-174):

Add section on attribute change detection:
```
**CRITICAL - Attribute Change Detection:**
Only report attribute changes when EXPLICITLY mentioned in text:
- "removed her blazer" → clothing change
- "tied her hair back" → hair change
- "put on glasses" → accessory change

DO NOT infer changes - only explicit textual mentions!
```

Update JSON response format to include `attribute_changes` array.

**D. Update JSON parsing** (~line 354):

Parse `attribute_changes` from response and create `AttributeChange` objects.

**E. Add new method**:

```python
def apply_attribute_changes_to_manager(self, analysis: StoryboardAnalysis,
                                       manager: AttributeStateManager,
                                       sentence_num: int):
    """Apply detected changes to state manager (confidence >= 0.8 only)."""
```

**F. Update SceneVisualHistory class** (lines 87-134):

- Add `current_character_attributes` dict field
- Update `get_continuity_context()` to accept `manager` parameter and include current attributes
- Update `update_from_storyboard()` to accept `manager` and cache attributes

---

### Step 4: Update Prompt Generator

**MODIFY**: [src/prompt_generator.py](src/prompt_generator.py)

**A. Replace CHARACTER_DESCRIPTIONS import** (lines 15-21):

```python
from character_attributes import (
    CHARACTER_CANONICAL_ATTRIBUTES,
    get_full_description,
    get_compressed_description
)

# Backward compatibility for non-storyboard mode
CHARACTER_DESCRIPTIONS = {
    char: get_compressed_description(char, max_tokens=8)
    for char in CHARACTER_CANONICAL_ATTRIBUTES.keys()
}
```

**B. Update generate_storyboard_informed_prompt()** (lines 602-729):

Add `attribute_manager` parameter.

**Token Budget Strategy** (77 tokens total):
- 25-30 tokens: Character description (from manager's current state)
- 8 tokens: Camera angle/framing
- 8 tokens: Primary action/pose
- 5 tokens: Mood/expression
- 15 tokens: BASE_STYLE
- 6-11 tokens: Buffer

**Character description logic**:
```python
if attribute_manager:
    char_state = attribute_manager.get_current_attributes(primary_char)
    if char_state:
        char_desc = char_state.to_prompt_string()
    else:
        # Fallback to canonical
        char_desc = get_compressed_description(primary_char, max_tokens=28)
else:
    # Legacy mode
    char_desc = CHARACTER_DESCRIPTIONS.get(primary_char)
```

**Progressive compression** if over 77 tokens:
1. Remove mood
2. Remove action
3. Compress character to face + clothing (`to_compressed_string(max_tokens=20)`)
4. Further compress to face only

---

### Step 5: Integrate into Main Generation Loop

**MODIFY**: [src/generate_scene_images.py](src/generate_scene_images.py)

**A. Update process_sentence() signature** (line 96):

Add parameter:
```python
attribute_manager=None  # AttributeStateManager instance
```

**B. Update storyboard analysis section** (lines 138-160):

After analyzing sentence:
```python
# Apply attribute changes to manager
if attribute_manager and storyboard_analysis.attribute_changes:
    storyboard_analyzer.apply_attribute_changes_to_manager(
        storyboard_analysis,
        attribute_manager,
        sentence.sentence_num
    )

# Update scene history with manager
if scene_history:
    scene_history.update_from_storyboard(storyboard_analysis, manager=attribute_manager)
```

Pass `manager=attribute_manager` to `get_continuity_context()`.

**C. Update prompt generation call** (line 249):

Pass manager:
```python
prompt = generate_storyboard_informed_prompt(
    sentence.content,
    storyboard_analysis,
    scene_context=sentence.scene_context,
    attribute_manager=attribute_manager
)
```

**D. Update main() function**:

Initialize managers per chapter (~line 700-740):

```python
# Add new tracking dict
attribute_manager_by_chapter = {}

# In chapter initialization section
if args.enable_storyboard:
    from attribute_state_manager import AttributeStateManager

    attribute_manager_by_chapter[chapter_num] = AttributeStateManager(chapter_num)
    log_message(log_file, f"-> Initialized attribute manager for Chapter {chapter_num}")
```

Get manager for sentence processing (~line 755):
```python
attribute_manager = attribute_manager_by_chapter.get(chapter_num) if args.enable_storyboard else None
```

Pass to `process_sentence()`.

**E. Add statistics logging** (~line 810):

```python
# Print attribute change statistics
if args.enable_storyboard and attribute_manager_by_chapter:
    log_message(log_file, "\n" + "="*80)
    log_message(log_file, "Attribute Change Statistics")
    log_message(log_file, "="*80)
    for chapter_num, manager in attribute_manager_by_chapter.items():
        stats = manager.get_statistics()
        log_message(log_file, f"Chapter {chapter_num}: {stats['total_changes']} changes")
```

---

### Step 6: Enable Storyboard by Default

**MODIFY**: [src/config.py](src/config.py)

**Line 175**: Change `ENABLE_STORYBOARD = False` to:

```python
ENABLE_STORYBOARD = True  # Enabled by default for character attribute consistency
```

---

## Critical Files

### Must Create
1. [src/character_attributes.py](src/character_attributes.py) - Canonical attribute definitions
2. [src/attribute_state_manager.py](src/attribute_state_manager.py) - State management

### Must Modify
3. [src/storyboard_analyzer.py](src/storyboard_analyzer.py) - Lines 19, 51, 138-174, 354, 440+, 87-134
4. [src/prompt_generator.py](src/prompt_generator.py) - Lines 15-21, 602-729
5. [src/generate_scene_images.py](src/generate_scene_images.py) - Lines 96, 138-160, 249, 700+, 740+, 810+
6. [src/config.py](src/config.py) - Line 175

### Reference Only
7. [docs/reference/The_Obsolescence_Novel_Bible.md](docs/reference/The_Obsolescence_Novel_Bible.md) - Source for character descriptions

---

## Edge Cases Handled

1. **Character first appearance mid-chapter**: Lazy initialization in `get_current_attributes()`
2. **Multiple characters in sentence**: Storyboard prioritizes `characters_present[0]` (acting character)
3. **Token budget overflow**: Progressive compression (remove mood → action → compress character)
4. **Scene boundaries ('* * *')**: Attributes persist (do NOT reset)
5. **Chapter boundaries**: Attributes reset to canonical
6. **Low confidence changes**: Only apply if `confidence >= 0.8`
7. **Unknown characters**: Return `None`, prompt generator uses fallback
8. **Contradictory changes**: Last update wins, history preserved

---

## Testing Strategy

1. **Unit tests**: Test character_attributes.py (token counts, compression)
2. **Unit tests**: Test attribute_state_manager.py (initialization, updates, resets)
3. **Integration tests**: Test storyboard analyzer attribute change detection
4. **E2E tests**: Generate prompts for consecutive sentences, verify same attributes
5. **Visual validation**: Generate 10 consecutive Emma images, manually inspect consistency
6. **Attribute change test**: Create test chapter with explicit "removed blazer", verify visual change

---

## Migration Path

### Phase 1: Create Attributes (Manual - 2-4 hours)

For each character (Emma, Tyler, Elena, Maxim, Amara):
1. Read Novel Bible description
2. Expand to detailed attributes (hair, face, clothing, accessories, skin, build)
3. Ensure 25-30 tokens total
4. Be VERY specific: "navy blue fitted blazer" not "business attire"

### Phase 2: Implementation (Incremental)

**Week 1**: Create character_attributes.py (Emma only) + attribute_state_manager.py + tests

**Week 2**: Modify storyboard_analyzer.py + prompt_generator.py + test with Chapter 1

**Week 3**: Add all characters + modify generate_scene_images.py + enable by default

**Week 4**: Visual validation + tuning + full chapter generation

### Backward Compatibility

- Non-storyboard mode still works (uses 8-token descriptions)
- `--enable-storyboard False` disables attribute system
- Existing generated images unaffected
- Can regenerate with `--rebuild-storyboard`

---

## Expected Outcomes

✅ Character clothing remains consistent across sentences (unless story changes it)
✅ Hair style/length/accessories stay the same
✅ Eyes, skin tone, build remain constant (already handled by IP-Adapter + detailed prompts)
✅ Explicit story changes ("removed blazer") trigger attribute updates
✅ Changes persist for rest of chapter
✅ Statistics show which attributes changed when (debugging/validation)
✅ Token budget stays under 77 tokens with progressive compression

**Cost Impact**: ~$0.05-0.15 per chapter (existing storyboard cost, minimal overhead)

---

## Implementation Notes

- Start with Emma only for initial testing (most common character)
- Manually validate first 20 generated images before expanding to other characters
- Token counts are approximate - may need to adjust compression thresholds
- Confidence threshold (0.8) is tunable if false positives/negatives occur
- Change history in manager allows debugging contradictions
