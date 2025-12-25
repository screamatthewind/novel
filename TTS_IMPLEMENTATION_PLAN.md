# TTS Audio Generation Implementation Plan

## Overview
Add realistic text-to-speech audio generation to the novel's existing image generation pipeline. Each scene will have a corresponding audio file with multi-voice narration using Coqui TTS (local, RTX 3080 GPU).

## Requirements Summary
- **TTS Engine**: Coqui TTS XTTS v2 (local, no API costs)
- **Audio Content**: Full scene narration (all prose + dialogue from Scene.content)
- **Voice System**: Multiple character voices (Emma, Maxim, Amara, narrator)
- **Output**: One audio file per scene matching image naming convention
- **Integration**: Parallel to existing image generation pipeline

## Implementation Strategy

### Phase 1: Core Audio Infrastructure

#### 1. Update Configuration (src/config.py)
Add audio-specific settings mirroring the existing image configuration pattern:

```python
# Audio directories (parallel to OUTPUT_DIR, LOG_DIR, PROMPT_CACHE_DIR)
AUDIO_DIR = "../audio"
AUDIO_CACHE_DIR = "../audio_cache"
VOICES_DIR = "../voices"

# Create directories
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)

# Audio generation parameters
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
MAX_TTS_CHUNK_SIZE = 500  # Characters per TTS call

# Character-to-voice mapping
CHARACTER_VOICES = {
    "narrator": "voices/narrator_neutral.wav",
    "emma": "voices/emma_american.wav",
    "maxim": "voices/maxim_russian.wav",
    "amara": "voices/amara_kenyan.wav",
    "tyler": "voices/tyler_teen.wav",
    "elena": "voices/elena_russian.wav",
    # Secondary characters fall back to narrator
    "mark": "voices/narrator_neutral.wav",
    "diane": "voices/narrator_neutral.wav",
    "ramirez": "voices/narrator_neutral.wav"
}
```

#### 2. Create Voice Configuration Module (src/voice_config.py)
New file for voice profile management:

```python
from dataclasses import dataclass
from typing import Optional
import os
from config import CHARACTER_VOICES, VOICES_DIR

@dataclass
class VoiceProfile:
    character_name: str
    voice_file_path: str
    language: str = "en"

def get_voice_for_speaker(speaker_name: str) -> str:
    """
    Get voice file path for a character. Falls back to narrator if not found.
    Returns path to voice reference audio file.
    """
    voice_path = CHARACTER_VOICES.get(speaker_name.lower(), CHARACTER_VOICES["narrator"])

    # If voice file doesn't exist, fall back to narrator
    if not os.path.exists(voice_path):
        return CHARACTER_VOICES["narrator"]

    return voice_path
```

### Phase 2: Dialogue Parsing & Text Preprocessing

#### 3. Create Dialogue Parser (src/dialogue_parser.py)
New file to extract dialogue and attribute speakers:

**Key Functions:**
- `DialogueSegment` dataclass: Stores text, speaker, and type (dialogue/narration)
- `parse_scene_text(scene_content: str) -> List[DialogueSegment]`
  - Uses regex to detect dialogue in double quotes
  - Patterns: `"text" Emma said` or `Emma said: "text"`
  - Extracts speaker names: Emma, Maxim, Amara, Tyler, Mark, Elena, Diane, Ramirez
  - Handles unattributed dialogue by context (previous paragraph mentions character)
  - Marks all non-dialogue as narration
- `clean_markdown(text: str) -> str`
  - Remove `*italics*` markers (preserve content)
  - Replace em-dashes `—` with `, ` (pause)
  - Strip scene separators `* * *`
  - Normalize whitespace
- `chunk_text(text: str, max_chars: int = 500) -> List[str]`
  - Split on sentence boundaries (`.`, `!`, `?`)
  - Keep chunks under 500 chars for Coqui TTS optimal quality
  - Preserve sentence integrity

**Example Dialogue Patterns from Chapter One:**
```
"Looking good, Ramirez," she said → Speaker: emma
Ramirez grinned. "Told you..." → Speaker: ramirez
"Don't let engineering hear..." → Speaker: emma (from context)
```

#### 4. Create Audio Filename Generator (src/audio_filename_generator.py)
New file matching image filename pattern:

```python
def generate_audio_filename(chapter_num: int, scene_num: int,
                           scene_content: str, ext: str = "wav") -> str:
    """
    Generate audio filename matching image naming convention.
    Pattern: chapter_01_scene_02_emma_factory_reading.wav
    Reuses keyword extraction from prompt_generator.py
    """
```

### Phase 3: TTS Engine Integration

#### 5. Create Audio Generator (src/audio_generator.py)
New file following the SDXLGenerator pattern from image_generator.py:

**Class Structure:**
```python
class CoquiTTSGenerator:
    def __init__(self, model_name: str = DEFAULT_TTS_MODEL)
    def load_model()  # Load XTTS v2, apply GPU optimizations
    def generate_speech(text: str, speaker_wav: str, language: str = "en") -> np.ndarray
    def _cleanup_memory()  # Mirror SDXLGenerator pattern
    def unload_model()  # Free VRAM
```

**GPU Optimizations:**
- Load model once, reuse across scenes (like SDXLGenerator)
- Use `torch.cuda.empty_cache()` between generations
- Chunk long text to avoid quality degradation (max 500 chars)
- Concatenate audio segments with small pause (200ms)

**Voice Cloning Strategy:**
- **Initial Implementation**: Use XTTS v2 pretrained speakers
  - Map characters to closest pretrained voices by gender/accent
  - No reference audio needed, works immediately
- **Future Enhancement**: Custom voice cloning
  - Record 10-30 second samples per character
  - Save to `voices/` directory
  - Reference files: `emma_american.wav`, `maxim_russian.wav`, etc.

**Error Handling:**
- Missing voice file → fallback to narrator voice
- CUDA OOM → cleanup memory, retry with smaller chunks
- TTS generation fails → log error, save text to failed_segments.txt, continue

### Phase 4: CLI Implementation

#### 6. Create Audio Generation CLI (src/generate_scene_audio.py)
New file mirroring generate_scene_images.py structure:

**Command-line Arguments:**
```bash
--chapters 1 3          # Specific chapters
--resume 2 5            # Resume from Chapter 2, Scene 5
--dry-run               # Show dialogue parsing without generating
--audio-format {wav,mp3}  # Output format (default: wav)
--single-voice          # Use narrator only (testing mode)
--skip-cache            # Regenerate even if exists
```

**Pipeline Flow:**
1. Parse scenes using existing `scene_parser.parse_all_chapters()`
2. For each scene:
   - Parse dialogue → `dialogue_parser.parse_scene_text()`
   - Generate audio segments with appropriate voices
   - Concatenate segments into single audio file
   - Save to `audio/chapter_XX_scene_YY_[keywords].wav`
   - Cache metadata to `audio_cache/`
3. Logging to `logs/audio_generation_TIMESTAMP.log`

**Logging Format** (matching image generation):
```
[2025-12-24 19:30:00] ================================================================================
[2025-12-24 19:30:00] Novel Scene Audio Generation
[2025-12-24 19:30:00] ================================================================================
[2025-12-24 19:30:01] GPU: NVIDIA GeForce RTX 3080
[2025-12-24 19:30:02] Loading Coqui TTS model: xtts_v2...
[2025-12-24 19:30:15] Model loaded successfully!
[2025-12-24 19:30:15] Found 15 scenes to process
[2025-12-24 19:30:15]
[2025-12-24 19:30:15] ================================================================================
[2025-12-24 19:30:15] Chapter 1, Scene 1 (425 words)
[2025-12-24 19:30:15] Filename: chapter_01_scene_01_emma_factory_reading.wav
[2025-12-24 19:30:15] Parsed: 6 dialogue segments, 4 narration segments
[2025-12-24 19:30:15] Speakers: emma, ramirez, narrator
[2025-12-24 19:32:45] Audio saved: chapter_01_scene_01_emma_factory_reading.wav (duration: 2m 7s)
```

**Scene Processing Function:**
```python
def process_scene(scene: Scene, generator: CoquiTTSGenerator,
                 log_file: str, args) -> bool:
    """
    Process single scene: parse dialogue, generate audio, save.
    Mirrors process_scene() from generate_scene_images.py
    """
    # 1. Parse dialogue segments
    # 2. Generate audio for each segment with appropriate voice
    # 3. Concatenate segments
    # 4. Save audio file + metadata
    # 5. Log results
```

### Phase 5: Dependencies & Setup

#### 7. Update Requirements (requirements.txt)
Add TTS dependencies:

```txt
# Text-to-Speech (add to existing requirements)
TTS>=0.22.0              # Coqui TTS with XTTS v2 (~2GB model download on first run)
pydub>=0.25.1            # Audio manipulation (WAV to MP3 conversion)
soundfile>=0.12.1        # Audio file I/O
scipy>=1.10.0            # Audio processing utilities
```

**Installation:**
```bash
pip install TTS pydub soundfile scipy
```

**First Run:** XTTS v2 model auto-downloads (~2GB) on first TTS generation.

## File Structure After Implementation

```
novel/
├── src/
│   ├── config.py                    # [EDIT] Add audio config
│   ├── scene_parser.py              # [EXISTING] Reuse Scene dataclass
│   ├── voice_config.py              # [NEW] Voice management
│   ├── dialogue_parser.py           # [NEW] Text preprocessing
│   ├── audio_filename_generator.py  # [NEW] Filename generation
│   ├── audio_generator.py           # [NEW] Coqui TTS wrapper
│   ├── generate_scene_audio.py      # [NEW] CLI entry point
│   ├── image_generator.py           # [EXISTING] Reference for patterns
│   └── generate_scene_images.py     # [EXISTING] Reference for CLI
├── audio/                           # [NEW] Generated audio files
│   ├── chapter_01_scene_01_emma_factory_reading.wav
│   ├── chapter_01_scene_02_emma_rowhouse_shocked.wav
│   └── ...
├── audio_cache/                     # [NEW] Metadata and parsed dialogue cache
│   ├── chapter_01_scene_01_metadata.json
│   ├── dialogue_segments_chapter_01_scene_01.json
│   └── ...
├── voices/                          # [NEW] Voice reference audio (optional)
│   ├── narrator_neutral.wav
│   ├── emma_american.wav
│   └── ...
├── logs/                            # [EXISTING] Add audio generation logs
│   ├── audio_generation_20251224_193000.log
│   └── ...
└── requirements.txt                 # [EDIT] Add TTS dependencies
```

## Usage Examples

### Generate Audio for All Chapters
```bash
cd src
python generate_scene_audio.py
```

### Generate Specific Chapters
```bash
python generate_scene_audio.py --chapters 1 3
```

### Preview Dialogue Parsing (No Audio Generation)
```bash
python generate_scene_audio.py --dry-run
```

### Resume from Specific Scene
```bash
python generate_scene_audio.py --resume 2 3
```

### Test with Single Narrator Voice
```bash
python generate_scene_audio.py --chapters 1 --single-voice
```

### Generate Both Images and Audio
```bash
# Sequential execution (recommended to avoid VRAM issues)
python generate_scene_images.py --chapters 1
python generate_scene_audio.py --chapters 1
```

## Performance Estimates (RTX 3080)

- **XTTS v2 VRAM Usage**: ~2-3GB (much lighter than SDXL's 8-9GB)
- **Processing Speed**: ~150-200 words/minute
- **Per Scene**: 500 words = 2.5-3 minutes generation time
- **Full Chapter** (4 scenes): ~10-15 minutes
- **All 4 Chapters** (~15 scenes): ~40-60 minutes

**Memory Strategy:**
- Run image generation first (VRAM-heavy)
- Then run audio generation (lighter)
- Or run separately to avoid GPU contention

## Testing Strategy

### Phase 1: Unit Tests
1. **Dialogue Parser Test**: Run on Chapter One sample
   ```bash
   python dialogue_parser.py
   ```
   Verify: Correctly identifies Emma, Ramirez dialogue with speaker attribution

2. **Voice Configuration Test**: Check voice file loading
   ```bash
   python voice_config.py
   ```
   Verify: Handles missing files, shows fallbacks

3. **TTS Model Loading Test**: Generate 10-second sample
   ```bash
   python audio_generator.py
   ```
   Verify: Model loads, generates test audio successfully

### Phase 2: Single Scene Test
```bash
python generate_scene_audio.py --chapters 1 --dry-run
```
Verify: Dialogue parsing looks correct (speakers identified)

```bash
python generate_scene_audio.py --chapters 1 --resume 1 1 --single-voice
```
Verify: Generates Chapter 1, Scene 1 audio file successfully

### Phase 3: Quality Validation
**Manual Review Checklist:**
- Audio quality acceptable (no glitches, natural prosody)
- Speaker voices distinguishable
- Dialogue attributed to correct character
- Pacing natural (~150 words/min)
- Narration tone appropriate
- No cutoffs or long silences
- Filename matches image naming convention

### Phase 4: Full Chapter Test
```bash
python generate_scene_audio.py --chapters 1
```
Listen to 1-2 complete scenes for quality assurance.

## Critical Files to Modify

1. **src/config.py** - Add audio directories and character voice mappings
2. **requirements.txt** - Add TTS dependencies

## New Files to Create

1. **src/voice_config.py** - Voice profile management and fallback logic
2. **src/dialogue_parser.py** - Dialogue extraction, speaker attribution, text cleaning, chunking
3. **src/audio_filename_generator.py** - Audio filename generation matching image convention
4. **src/audio_generator.py** - Coqui TTS wrapper with GPU optimization
5. **src/generate_scene_audio.py** - Main CLI for audio generation

## Implementation Order

1. Update config.py with audio settings
2. Create voice_config.py for voice management
3. Create dialogue_parser.py and test with Chapter One
4. Create audio_generator.py and test model loading
5. Create audio_filename_generator.py
6. Create generate_scene_audio.py CLI
7. Update requirements.txt
8. Test with single scene (--dry-run, then real generation)
9. Generate full chapter and validate quality
10. Optimize and handle edge cases

## Key Design Decisions

- **Parallel Pipeline**: Audio generation is separate from images (can run independently)
- **Reuse Existing Patterns**: Follows SDXLGenerator class structure, CLI argument patterns, logging format
- **Local-First**: Coqui TTS runs on RTX 3080, no API costs or internet required
- **Graceful Degradation**: Missing voice files fall back to narrator, failed segments logged but don't stop pipeline
- **Caching Strategy**: Cache parsed dialogue to avoid re-parsing on subsequent runs
- **Voice Cloning**: Start with pretrained voices, add custom voice cloning later as enhancement
