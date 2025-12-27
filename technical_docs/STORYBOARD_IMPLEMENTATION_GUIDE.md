# Storyboard Analysis Implementation Guide

## Quick Start

This guide walks you through implementing sentence-by-sentence storyboard analysis for "The Obsolescence" image generation system.

## What This Does

Transforms image generation from basic keyword extraction to detailed visual analysis:

**Before**: "A Asian American woman 40s in a factory with shocked expression."

**After**: "Medium close-up, eye level. Emma shocked reading tablet, industrial window light. Graphic novel art, bold lines, high contrast, dramatic mood."

## Key Features

1. **Claude Haiku API** analyzes each sentence for visual details (camera angle, expression, composition, mood)
2. **Aggressive caching** prevents redundant API calls (~$0.02 first run, $0.00 subsequent runs per chapter)
3. **Smart image reuse** based on visual composition changes, not just keywords
4. **Fully automatic** - no manual intervention required
5. **Backward compatible** - existing scripts work unchanged

## Files to Create

### 1. src/storyboard_analyzer.py (NEW)
**Purpose**: Core storyboard analysis engine with Haiku integration and caching

**Key Classes**:
- `StoryboardAnalysis` (dataclass) - Stores analysis results
- `StoryboardAnalyzer` - Main analyzer with cache-first API calls
- `SceneVisualHistory` - Tracks visual state across sentences

**Critical Features**:
- **Cache-first**: Always check cache before calling Haiku API
- **Content hashing**: Detect changed sentences to invalidate stale cache
- **Persistent storage**: `storyboard_cache/{chapter:02d}/sentence_{num:03d}.json`
- **Index tracking**: `storyboard_cache/index.json` for quick lookups

**Haiku System Prompt**:
```
You are a visual storyboard consultant analyzing fiction for graphic novel adaptation.

For each sentence, extract:
1. PEOPLE: All mentioned (names/pronouns), their roles (acting/speaking/spoken-to/referenced)
2. CAMERA: Framing (close-up, medium, wide, two-shot, POV, over-shoulder) and angle (high, level, low)
3. COMPOSITION: Visual arrangement, focal points, depth
4. CHARACTER DETAILS: Expression, posture, gesture specific to this moment
5. VISUAL CONTINUITY: Props, clothing, positions from context
6. MOOD/TONE: Emotional atmosphere
7. VISUAL FOCUS: What the viewer's eye should be drawn to

Output brief, actionable descriptions optimized for SDXL prompts. No explanations.
```

**Method Flow**:
```python
def analyze_sentence(sentence: Sentence, ...) -> StoryboardAnalysis:
    # 1. Generate cache key from sentence content
    cache_key = self._generate_cache_key(sentence)

    # 2. Check cache FIRST
    cached = self.get_cached_analysis(cache_key)
    if cached:
        log("Using cached storyboard analysis")
        return cached

    # 3. Only call API if cache miss
    analysis = self._call_haiku_api(sentence, ...)

    # 4. Save to cache for future runs
    self.save_analysis(cache_key, analysis)

    return analysis
```

### 2. src/novel_context.py (NEW)
**Purpose**: Parse Novel Bible for canonical character descriptions

**Key Class**:
- `NovelContext` - Extracts character descriptions from Novel Bible

**Functionality**:
```python
class NovelContext:
    def __init__(self, bible_path: str = "../book/reference/The_Obsolescence_Novel_Bible.md"):
        self.character_descriptions = self._extract_characters()

    def get_character_context(self, character_name: str) -> str:
        # Returns: "Mid-40s Asian American woman, practical professional, sensible shoes"
```

**Character Descriptions to Extract**:
- Emma Chen: "Mid-40s Asian American woman, practical professional, sensible shoes"
- Tyler Chen: "16-year-old, typical teenager, slouch, earbuds, phone"
- Elena Volkov: "60s, short gray hair, sharp eyes, slight frame, analytical"
- Maxim Orlov: "Mid-40s Russian, working-class, hands that know labor"
- Amara Okafor: "Late 40s-50s Kenyan, fierce, pragmatic"

## Files to Modify

### 3. src/prompt_generator.py (MODIFY)
**Add Function**: `generate_storyboard_informed_prompt()`

**Purpose**: Convert storyboard analysis into 77-token SDXL prompts

**Token Budget Strategy**:
- 12 tokens: Character description
- 8 tokens: Camera angle/framing
- 8 tokens: Primary action/pose
- 8 tokens: Mood/expression
- 10 tokens: Composition/focus
- 8 tokens: Setting/context
- 15 tokens: Style (BASE_STYLE)
- 8 tokens: Buffer

**Prompt Template**:
```
{camera_framing} {camera_angle}. {character_desc} {expression} {action}.
{composition}. {mood}. {BASE_STYLE}
```

**Example**:
```python
def generate_storyboard_informed_prompt(
    sentence: Sentence,
    storyboard_analysis: StoryboardAnalysis,
    scene_context: str = None
) -> str:
    # Build prompt from storyboard metadata
    # Prioritize most important visual elements to fit 77-token limit
    # Use existing validate_prompt_length() to verify
```

### 4. src/visual_change_detector.py (MODIFY)
**Add Method**: `analyze_with_storyboard()`

**Purpose**: Smarter image reuse decisions based on visual composition

**Enhanced Decision Logic**:
```python
def analyze_with_storyboard(
    self,
    sentence: Sentence,
    storyboard: StoryboardAnalysis
) -> Tuple[bool, str]:
    """
    Decision rules:
    1. Special techniques (flashback, montage) → New image
    2. Character entry/exit → New image
    3. Camera angle change → New image
    4. Expression/mood dramatically different → New image
    5. Spatial position change → New image
    6. Same framing, characters, mood → Reuse
    """
```

### 5. src/generate_scene_images.py (MODIFY)
**Command-Line Arguments**:
```python
--storyboard-cache-dir   # Cache directory (default: ../storyboard_cache)
--rebuild-storyboard     # Force rebuild cache (ignore existing)
```

**Note:** Storyboard analysis is now enabled by default and always active.

**Integration Flow**:
```python
# Initialize (always active)
storyboard_analyzer = StoryboardAnalyzer(
    cache_dir=args.storyboard_cache_dir,
    rebuild_cache=args.rebuild_storyboard
)
novel_context = NovelContext()
scene_history = SceneVisualHistory()

    # Process each sentence
    for sentence in all_sentences:
        # Get character context
        char_context = novel_context.get_character_context(...)

        # Analyze with storyboard (cache-first)
        analysis = storyboard_analyzer.analyze_sentence(
            sentence,
            character_context=char_context,
            scene_history=scene_history.get_continuity_context()
        )

        # Enhanced change detection
        needs_new_image, reason = detector.analyze_with_storyboard(
            sentence, analysis
        )

        # Generate prompt
        if needs_new_image:
            prompt = generate_storyboard_informed_prompt(
                sentence, analysis, scene_context
            )
            # Generate image with SDXL...

        # Update visual history
        scene_history.update_from_storyboard(analysis)
```

### 6. src/config.py (MODIFY)
**Add Settings**:
```python
# Storyboard analysis settings
STORYBOARD_CACHE_DIR = "../storyboard_cache"
STORYBOARD_REPORT_DIR = "../storyboard_reports"

# Storyboard analyzer settings (always enabled)
STORYBOARD_MODEL = "claude-3-5-haiku-20241022"
STORYBOARD_MAX_TOKENS = 500  # Detailed analysis
STORYBOARD_BATCH_SIZE = 10

# Visual history settings
TRACK_SCENE_VISUAL_HISTORY = True
SCENE_RESET_AT_BOUNDARIES = True  # Reset at * * * separator
```

## Data Structures

### StoryboardAnalysis Dataclass
```python
@dataclass
class StoryboardAnalysis:
    # Source info
    chapter_num: int
    scene_num: int
    sentence_num: int
    sentence_content: str

    # Character presence
    characters_present: List[str]  # ["Emma", "Tyler"]
    character_roles: Dict[str, str]  # {"Emma": "acting"}

    # Camera and framing
    camera_framing: str  # "close-up", "medium shot", "wide shot"
    camera_angle: str    # "high angle", "level", "low angle"
    camera_movement: Optional[str]  # "pan", "zoom", "steady"

    # Composition
    composition: str  # Visual arrangement description
    visual_focus: str  # What draws the eye first
    depth_cues: str   # Foreground/midground/background

    # Character details
    expressions: Dict[str, str]      # Character -> expression
    body_language: Dict[str, str]    # Character -> posture/gesture
    movement: Optional[str]          # Physical movement

    # Visual continuity
    props: List[str]           # Objects present
    clothing_state: Optional[str]  # Clothing details
    spatial_context: str       # Where this is happening

    # Special techniques
    special_techniques: List[str]  # "flashback", "montage"

    # Mood and tone
    mood: str  # Emotional atmosphere
    tone: str  # Narrative tone
    lighting_suggestion: str  # "harsh shadows", "soft light"

    # Continuity tracking
    continuity_from_previous: Optional[str]
    continuity_to_next: Optional[str]

    # Metadata
    confidence: float  # 0.0-1.0
    analysis_timestamp: datetime
    api_tokens: Dict[str, int]  # {"input": 387, "output": 102}
```

## Cache System Details

### Directory Structure
```
storyboard_cache/
├── 01/                           # Chapter 1
│   ├── sentence_001.json        # Scene 1, Sent 1 analysis
│   ├── sentence_002.json
│   └── ...
├── 02/                          # Chapter 2
│   └── ...
└── index.json                    # Global index
```

### Cache Key Generation
```python
def _generate_cache_key(self, sentence: Sentence) -> str:
    # Use content hash to detect changes
    content_hash = hashlib.md5(sentence.content.encode()).hexdigest()[:8]
    return f"ch{sentence.chapter_num:02d}_sc{sentence.scene_num:02d}_s{sentence.sentence_num:03d}_{content_hash}"
```

### Cache Hit Rate Expectations
- **First run** (cold cache): 0% hit rate, all API calls
- **Second run** (warm cache, unchanged text): 99%+ hit rate
- **Incremental changes**: Only modified sentences trigger API calls

## Cost Analysis

### Haiku Pricing (as of Jan 2025)
- Input: $0.80 per million tokens
- Output: $4.00 per million tokens

### Per-Chapter Estimates
- **First run**: ~$0.01-0.02
  - 100-150k input tokens (sentence + context + system prompt)
  - 25-40k output tokens (detailed analysis)
- **Subsequent runs**: ~$0.00 (cache hits)

### Full 12-Chapter Novel
- **First analysis**: $0.12-0.24 total
- **Re-runs**: Nearly free (99%+ cache hits)

### Cost Tracking Output
```
Storyboard Analysis:
- Cache hits: 142/150 (94.7%)
- API calls: 8 (new sentences)
- Input tokens: 3,040
- Output tokens: 760
- Cost: $0.006
```

## Usage Examples

### Generate Images (Storyboard always enabled)
```bash
cd src
../venv/Scripts/python generate_scene_images.py \
  --chapters 1 \
  --llm haiku
```

### Dry-Run (Analysis Only, No Images)
```bash
../venv/Scripts/python generate_scene_images.py \
  --chapters 1 \
  --dry-run
```

### Rebuild Cache (Force Re-Analysis)
```bash
../venv/Scripts/python generate_scene_images.py \
  --chapters 1 \
  --rebuild-storyboard
```

### Compare Methods
```bash
../venv/Scripts/python generate_scene_images.py \
  --chapters 1 \
  --llm compare
```

## Output Files

### Storyboard Reports
**File**: `storyboard_reports/chapter_{num:02d}_storyboard_report.md`

**Format**:
```markdown
# Chapter 1 Storyboard Analysis Report

Generated: 2025-12-26 14:30:00
Total Sentences: 47
Cache Hits: 45/47 (95.7%)
API Calls: 2
Cost: $0.003

---

## Scene 1: "Ahead of Schedule"

### Sentence 1
**Text**: "Emma stared at the email on her tablet..."

**Analysis**:
- Camera: Medium close-up, eye level
- Character: Emma (acting)
- Expression: Shocked, disbelief
- Focus: Tablet screen, Emma's face
- Mood: Sudden realization, dread

**Generated Prompt**:
"Medium close-up of Emma staring at tablet, shocked expression.
Afternoon light through industrial windows. Graphic novel style,
bold lines, high contrast, dramatic mood."

**Token Count**: 28/77
```

### JSON Metadata
Each analysis persists to `storyboard_cache/{chapter}/sentence_{num}.json` for programmatic access.

## Error Handling

### Graceful Degradation
```python
try:
    analysis = storyboard_analyzer.analyze_sentence(sentence)
    prompt = generate_storyboard_informed_prompt(sentence, analysis)
except (APIError, TimeoutError) as e:
    log_message(f"Storyboard analysis failed: {e}")
    log_message("Falling back to keyword-based method")
    prompt = generate_prompt(sentence, scene_context)
```

### Fallback Priority
1. Try storyboard analysis
2. Check cache if API fails
3. Fall back to keyword-based method
4. Log all failures for debugging

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create `storyboard_analyzer.py` with `StoryboardAnalysis` dataclass
- [ ] Implement Haiku API integration
- [ ] Add cache system (check before call, save after response)
- [ ] Test with single chapter

### Phase 2: Integration (Week 2)
- [ ] Create `novel_context.py` to parse Novel Bible
- [ ] Add `generate_storyboard_informed_prompt()` to `prompt_generator.py`
- [ ] Add command-line flags to `generate_scene_images.py`
- [ ] Test full chapter generation

### Phase 3: Enhancement (Week 3)
- [ ] Add `analyze_with_storyboard()` to `visual_change_detector.py`
- [ ] Implement `SceneVisualHistory` tracking
- [ ] Add storyboard report generation
- [ ] Optimize token usage in prompts

### Phase 4: Validation (Week 4)
- [ ] Compare storyboard vs non-storyboard image quality
- [ ] Measure actual costs
- [ ] Refine prompts based on SDXL output
- [ ] Document best practices

## Testing Strategy

### Unit Tests
```python
# test_storyboard_analyzer.py
def test_cache_hit():
    # Verify cache prevents redundant API calls

def test_cache_invalidation():
    # Verify changed sentence content invalidates cache

def test_token_counting():
    # Verify prompts stay under 77 tokens
```

### Integration Tests
```python
# test_storyboard_integration.py
def test_full_scene_analysis():
    # Analyze all sentences in scene

def test_visual_continuity():
    # Check visual history tracking

def test_prompt_generation():
    # Verify storyboard-informed prompts are valid
```

## Key Benefits

1. **Better Story Accuracy**: Images reflect narrative beats, emotions, visual composition
2. **Improved Character Consistency**: Expression/pose details work with IP-Adapter FaceID
3. **Smarter Image Reuse**: Visual composition-based detection reduces unnecessary generation
4. **Minimal Cost**: Aggressive caching keeps costs ~$0.12-0.24 for entire 12-chapter novel
5. **Fully Automatic**: No manual intervention required
6. **Backward Compatible**: Existing workflows unchanged

## Critical Notes

- **Always use virtual environment**: `./venv/Scripts/python`
- **Cache is persistent**: Survives across script runs
- **Git operations**: User handles all git operations (per CLAUDE.md)
- **SDXL 77-token limit**: Prompt engineering prioritizes most important elements
- **No new dependencies**: Uses existing `anthropic` library

## Reference Files

- **Novel Bible**: [book/reference/The_Obsolescence_Novel_Bible.md](book/reference/The_Obsolescence_Novel_Bible.md)
- **Current prompt generator**: [src/prompt_generator.py](src/prompt_generator.py)
- **Current visual detector**: [src/visual_change_detector.py](src/visual_change_detector.py)
- **Scene parser**: [src/scene_parser.py](src/scene_parser.py)
- **Config**: [src/config.py](src/config.py)
