"""
Storyboard analysis engine for visual scene planning.

Uses Claude Haiku API to analyze sentences for detailed visual composition,
camera angles, character expressions, and mood. Implements aggressive caching
to minimize API costs.
"""

import hashlib
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from anthropic import Anthropic
from scene_parser import Sentence
from config import ANTHROPIC_MODEL, ANTHROPIC_MAX_TOKENS, HAIKU_INPUT_COST_PER_MILLION, HAIKU_OUTPUT_COST_PER_MILLION


@dataclass
class AttributeChange:
    """Specific attribute change detected in a sentence."""
    character_name: str
    attribute_type: str  # "hair", "clothing", "accessories"
    old_state: str
    new_state: str
    explicit_mention: str  # Text that triggered the change
    confidence: float  # 0.0-1.0


@dataclass
class StoryboardAnalysis:
    """Stores detailed visual analysis for a single sentence."""
    # Source info
    chapter_num: int
    scene_num: int
    sentence_num: int
    sentence_content: str

    # Character presence
    characters_present: List[str]  # ["Emma", "Tyler"]
    character_roles: Dict[str, str]  # {"Emma": "acting", "Tyler": "referenced"}

    # Camera and framing
    camera_framing: str  # "close-up", "medium shot", "wide shot"
    camera_angle: str    # "high angle", "level", "low angle"
    camera_movement: Optional[str] = None  # "pan", "zoom", "steady"

    # Composition
    composition: str = ""  # Visual arrangement description
    visual_focus: str = ""  # What draws the eye first
    depth_cues: str = ""   # Foreground/midground/background

    # Character details
    expressions: Dict[str, str] = None      # Character -> expression
    body_language: Dict[str, str] = None    # Character -> posture/gesture
    movement: Optional[str] = None          # Physical movement

    # Visual continuity
    props: List[str] = None           # Objects present
    clothing_state: Optional[str] = None  # Clothing details
    spatial_context: str = ""       # Where this is happening

    # Special techniques
    special_techniques: List[str] = None  # "flashback", "montage"

    # Mood and tone
    mood: str = ""  # Emotional atmosphere
    tone: str = ""  # Narrative tone
    lighting_suggestion: str = ""  # "harsh shadows", "soft light"

    # Continuity tracking
    continuity_from_previous: Optional[str] = None
    continuity_to_next: Optional[str] = None

    # Metadata
    confidence: float = 1.0  # 0.0-1.0
    analysis_timestamp: datetime = None
    api_tokens: Dict[str, int] = None  # {"input": 387, "output": 102}

    # Attribute change tracking
    attribute_changes: List[AttributeChange] = None  # Detected attribute changes

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.expressions is None:
            self.expressions = {}
        if self.body_language is None:
            self.body_language = {}
        if self.props is None:
            self.props = []
        if self.special_techniques is None:
            self.special_techniques = []
        if self.attribute_changes is None:
            self.attribute_changes = []
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()
        if self.api_tokens is None:
            self.api_tokens = {"input": 0, "output": 0}


class SceneVisualHistory:
    """Tracks visual state across sentences for continuity."""

    def __init__(self):
        self.current_characters: List[str] = []
        self.current_framing: str = ""
        self.current_location: str = ""
        self.current_props: List[str] = []
        self.current_mood: str = ""
        self.current_character_attributes: Dict[str, str] = {}  # character -> current description
        self.history: List[StoryboardAnalysis] = []

    def get_continuity_context(self, manager=None) -> str:
        """
        Generate context string for API calls.

        Args:
            manager: Optional AttributeStateManager to include current character attributes

        Returns:
            Context string describing current visual state
        """
        if not self.history:
            return "This is the first sentence in the scene."

        last = self.history[-1]
        context_parts = []

        if self.current_characters:
            context_parts.append(f"Current characters: {', '.join(self.current_characters)}")
        if self.current_framing:
            context_parts.append(f"Current framing: {self.current_framing}")
        if self.current_location:
            context_parts.append(f"Location: {self.current_location}")
        if self.current_props:
            context_parts.append(f"Visible props: {', '.join(self.current_props)}")

        # Include current character attributes if manager provided
        if manager and self.current_character_attributes:
            attr_strs = [f"{char}: {desc}" for char, desc in self.current_character_attributes.items()]
            context_parts.append(f"Character attributes: {'; '.join(attr_strs)}")

        return " | ".join(context_parts) if context_parts else "No previous context."

    def update_from_storyboard(self, analysis: StoryboardAnalysis, manager=None):
        """
        Update visual history from new analysis.

        Args:
            analysis: StoryboardAnalysis to update from
            manager: Optional AttributeStateManager to cache current attributes
        """
        self.current_characters = analysis.characters_present
        self.current_framing = analysis.camera_framing
        self.current_location = analysis.spatial_context
        self.current_props = analysis.props
        self.current_mood = analysis.mood

        # Cache current character attributes from manager
        if manager:
            self.current_character_attributes = {}
            for char in analysis.characters_present:
                state = manager.get_current_attributes(char.lower())
                if state:
                    self.current_character_attributes[char] = state.to_compressed_string(max_tokens=15)

        self.history.append(analysis)

    def reset(self):
        """Reset visual history (call at scene boundaries)."""
        self.current_characters = []
        self.current_framing = ""
        self.current_location = ""
        self.current_props = []
        self.current_mood = ""
        self.history = []


class StoryboardAnalyzer:
    """Main storyboard analysis engine with cache-first API calls."""

    SYSTEM_PROMPT = """You are a visual storyboard consultant analyzing fiction for graphic novel adaptation.

For each sentence, extract:
1. PEOPLE: All mentioned (names/pronouns), their roles (acting/speaking/spoken-to/referenced)
2. CAMERA: Framing (close-up, medium, wide, two-shot, POV, over-shoulder) and angle (high, level, low)
3. COMPOSITION: Visual arrangement, focal points, depth
4. CHARACTER DETAILS: Expression, posture, gesture specific to this moment
5. VISUAL CONTINUITY: Props, clothing, positions from context
6. MOOD/TONE: Emotional atmosphere
7. VISUAL FOCUS: What the viewer's eye should be drawn to

**CRITICAL - Attribute Change Detection:**
ONLY report attribute changes when EXPLICITLY mentioned in the text:
- "removed her blazer" → clothing change (old: "blazer + shirt", new: "shirt only")
- "tied her hair back" → hair change (old: "loose hair", new: "tied back")
- "put on glasses" → accessory change (old: "no glasses", new: "glasses")
- "took off his jacket" → clothing change
- "pulled down her sleeves" → clothing change

DO NOT infer changes from context - only explicit textual mentions count!
If no explicit mention, leave attribute_changes as empty array.

Output brief, actionable descriptions optimized for SDXL prompts. No explanations.
Respond ONLY with valid JSON matching this structure:
{
    "characters_present": ["character1", "character2"],
    "character_roles": {"character1": "acting", "character2": "referenced"},
    "camera_framing": "medium shot",
    "camera_angle": "level",
    "camera_movement": null,
    "composition": "brief description",
    "visual_focus": "what draws the eye",
    "depth_cues": "foreground/midground/background",
    "expressions": {"character1": "expression"},
    "body_language": {"character1": "posture/gesture"},
    "movement": "physical movement if any",
    "props": ["prop1", "prop2"],
    "clothing_state": "clothing details if relevant",
    "spatial_context": "where this is happening",
    "special_techniques": [],
    "mood": "emotional atmosphere",
    "tone": "narrative tone",
    "lighting_suggestion": "lighting description",
    "continuity_from_previous": "what continues from previous sentence",
    "continuity_to_next": "what might continue to next sentence",
    "confidence": 0.9,
    "attribute_changes": [
        {
            "character_name": "emma",
            "attribute_type": "clothing",
            "old_state": "blazer + shirt",
            "new_state": "shirt only",
            "explicit_mention": "removed her blazer",
            "confidence": 0.95
        }
    ]
}"""

    def __init__(self, cache_dir: str = "../storyboard_cache", rebuild_cache: bool = False,
                 images_dir: str = "../images"):
        """
        Initialize storyboard analyzer.

        Args:
            cache_dir: Directory for caching analysis results
            rebuild_cache: If True, ignore existing cache and force re-analysis
            images_dir: Directory where generated images are stored
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.rebuild_cache = rebuild_cache
        self.images_dir = Path(images_dir)

        # Initialize Anthropic client
        self.client = Anthropic()  # Uses ANTHROPIC_API_KEY from environment

        # Cache index for quick lookups
        self.index_file = self.cache_dir / "index.json"
        self.cache_index = self._load_cache_index()

        # Statistics tracking
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "api_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        }

    def _load_cache_index(self) -> Dict:
        """Load cache index from disk."""
        if self.index_file.exists() and not self.rebuild_cache:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache_index(self):
        """Save cache index to disk."""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_index, f, indent=2)

    def _generate_cache_key(self, sentence: Sentence) -> str:
        """
        Generate cache key from sentence content hash.

        Args:
            sentence: Sentence to generate key for

        Returns:
            Cache key string
        """
        content_hash = hashlib.md5(sentence.content.encode()).hexdigest()[:8]
        return f"ch{sentence.chapter_num:02d}_sc{sentence.scene_num:02d}_s{sentence.sentence_num:03d}_{content_hash}"

    def _get_cache_filepath(self, chapter_num: int, cache_key: str) -> Path:
        """Get filepath for cached analysis."""
        chapter_dir = self.cache_dir / f"{chapter_num:02d}"
        chapter_dir.mkdir(exist_ok=True)
        return chapter_dir / f"{cache_key}.json"

    def get_cached_analysis(self, cache_key: str, chapter_num: int) -> Optional[StoryboardAnalysis]:
        """
        Retrieve cached analysis if available.

        Args:
            cache_key: Cache key to look up
            chapter_num: Chapter number for file organization

        Returns:
            StoryboardAnalysis if cached, None otherwise
        """
        if self.rebuild_cache:
            return None

        cache_file = self._get_cache_filepath(chapter_num, cache_key)

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Convert timestamp string back to datetime
                if 'analysis_timestamp' in data and isinstance(data['analysis_timestamp'], str):
                    data['analysis_timestamp'] = datetime.fromisoformat(data['analysis_timestamp'])

                self.stats["cache_hits"] += 1
                return StoryboardAnalysis(**data)
            except Exception as e:
                print(f"Warning: Failed to load cache {cache_file}: {e}")
                return None

        self.stats["cache_misses"] += 1
        return None

    def save_analysis(self, cache_key: str, analysis: StoryboardAnalysis):
        """
        Save analysis to cache.

        Args:
            cache_key: Cache key for storage
            analysis: StoryboardAnalysis to cache
        """
        cache_file = self._get_cache_filepath(analysis.chapter_num, cache_key)

        # Convert to dict and handle datetime serialization
        data = asdict(analysis)
        if isinstance(data.get('analysis_timestamp'), datetime):
            data['analysis_timestamp'] = data['analysis_timestamp'].isoformat()

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        # Update index
        self.cache_index[cache_key] = str(cache_file)
        self._save_cache_index()

    def _call_haiku_api(
        self,
        sentence: Sentence,
        character_context: str = "",
        scene_continuity: str = ""
    ) -> StoryboardAnalysis:
        """
        Call Claude Haiku API for storyboard analysis.

        Args:
            sentence: Sentence to analyze
            character_context: Character descriptions from Novel Bible
            scene_continuity: Visual continuity from previous sentences

        Returns:
            StoryboardAnalysis object
        """
        # Build user prompt
        user_prompt = f"""Analyze this sentence for visual storyboard:

SENTENCE: "{sentence.content}"

SCENE CONTEXT (for reference):
{sentence.scene_context[:500]}...

CHARACTER CONTEXT:
{character_context}

CONTINUITY FROM PREVIOUS:
{scene_continuity}

Provide detailed visual analysis as JSON."""

        try:
            # Call Haiku API
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=ANTHROPIC_MAX_TOKENS * 2,  # Allow more tokens for storyboard analysis
                system=self.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            # Track token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            self.stats["api_calls"] += 1
            self.stats["total_input_tokens"] += input_tokens
            self.stats["total_output_tokens"] += output_tokens

            # Parse JSON response
            response_text = response.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            analysis_data = json.loads(response_text)

            # Parse attribute changes
            attribute_changes = []
            raw_changes = analysis_data.get("attribute_changes", [])
            for change_data in raw_changes:
                try:
                    change = AttributeChange(
                        character_name=change_data.get("character_name", "").lower(),
                        attribute_type=change_data.get("attribute_type", ""),
                        old_state=change_data.get("old_state", ""),
                        new_state=change_data.get("new_state", ""),
                        explicit_mention=change_data.get("explicit_mention", ""),
                        confidence=change_data.get("confidence", 0.0)
                    )
                    attribute_changes.append(change)
                except Exception as e:
                    print(f"  Warning: Failed to parse attribute change: {e}")

            # Create StoryboardAnalysis object
            analysis = StoryboardAnalysis(
                chapter_num=sentence.chapter_num,
                scene_num=sentence.scene_num,
                sentence_num=sentence.sentence_num,
                sentence_content=sentence.content,
                characters_present=analysis_data.get("characters_present", []),
                character_roles=analysis_data.get("character_roles", {}),
                camera_framing=analysis_data.get("camera_framing", "medium shot"),
                camera_angle=analysis_data.get("camera_angle", "level"),
                camera_movement=analysis_data.get("camera_movement"),
                composition=analysis_data.get("composition", ""),
                visual_focus=analysis_data.get("visual_focus", ""),
                depth_cues=analysis_data.get("depth_cues", ""),
                expressions=analysis_data.get("expressions", {}),
                body_language=analysis_data.get("body_language", {}),
                movement=analysis_data.get("movement"),
                props=analysis_data.get("props", []),
                clothing_state=analysis_data.get("clothing_state"),
                spatial_context=analysis_data.get("spatial_context", ""),
                special_techniques=analysis_data.get("special_techniques", []),
                mood=analysis_data.get("mood", ""),
                tone=analysis_data.get("tone", ""),
                lighting_suggestion=analysis_data.get("lighting_suggestion", ""),
                continuity_from_previous=analysis_data.get("continuity_from_previous"),
                continuity_to_next=analysis_data.get("continuity_to_next"),
                confidence=analysis_data.get("confidence", 1.0),
                attribute_changes=attribute_changes,
                analysis_timestamp=datetime.now(),
                api_tokens={"input": input_tokens, "output": output_tokens}
            )

            return analysis

        except Exception as e:
            print(f"Error calling Haiku API: {e}")
            # Return minimal analysis on error
            return StoryboardAnalysis(
                chapter_num=sentence.chapter_num,
                scene_num=sentence.scene_num,
                sentence_num=sentence.sentence_num,
                sentence_content=sentence.content,
                characters_present=[],
                character_roles={},
                camera_framing="medium shot",
                camera_angle="level",
                confidence=0.0,
                analysis_timestamp=datetime.now(),
                api_tokens={"input": 0, "output": 0}
            )

    def analyze_sentence(
        self,
        sentence: Sentence,
        character_context: str = "",
        scene_continuity: str = ""
    ) -> StoryboardAnalysis:
        """
        Analyze a sentence with cache-first strategy.

        Args:
            sentence: Sentence to analyze
            character_context: Character descriptions from Novel Bible
            scene_continuity: Visual continuity from previous sentences

        Returns:
            StoryboardAnalysis object
        """
        # Generate cache key
        cache_key = self._generate_cache_key(sentence)

        # Check cache FIRST
        cached = self.get_cached_analysis(cache_key, sentence.chapter_num)
        if cached:
            print(f"  [CACHE HIT] Ch{sentence.chapter_num} Sc{sentence.scene_num} S{sentence.sentence_num}")
            return cached

        # Cache miss - call API
        print(f"  [API CALL] Ch{sentence.chapter_num} Sc{sentence.scene_num} S{sentence.sentence_num}")
        analysis = self._call_haiku_api(sentence, character_context, scene_continuity)

        # Save to cache
        self.save_analysis(cache_key, analysis)

        return analysis

    def apply_attribute_changes_to_manager(
        self,
        analysis: StoryboardAnalysis,
        manager,  # AttributeStateManager
        sentence_num: int
    ):
        """
        Apply detected attribute changes to the attribute state manager.

        Only applies changes with confidence >= 0.8 to avoid false positives.

        Args:
            analysis: StoryboardAnalysis containing detected changes
            manager: AttributeStateManager instance to update
            sentence_num: Current sentence number

        Example:
            >>> analyzer.apply_attribute_changes_to_manager(analysis, manager, 42)
            # Updates manager if analysis contains high-confidence attribute changes
        """
        if not analysis.attribute_changes:
            return

        for change in analysis.attribute_changes:
            # Only apply high-confidence changes
            if change.confidence < 0.8:
                print(f"  [SKIP] Low confidence attribute change ({change.confidence:.2f}): "
                      f"{change.character_name} {change.attribute_type}")
                continue

            # Apply change to manager
            success = manager.update_attribute(
                character_name=change.character_name,
                attribute_type=change.attribute_type,
                new_value=change.new_state,
                sentence_num=sentence_num,
                reason=change.explicit_mention
            )

            if success:
                print(f"  [ATTR CHANGE] {change.character_name}.{change.attribute_type}: "
                      f"'{change.explicit_mention}'")
            else:
                print(f"  [ATTR FAIL] Could not update {change.character_name}.{change.attribute_type}")

    def delete_chapter_cache_and_images(self, chapter_num: int) -> Tuple[int, int]:
        """
        Delete all cached storyboard files and generated images for a specific chapter.

        Args:
            chapter_num: Chapter number to delete cache and images for

        Returns:
            Tuple of (cache_files_deleted, image_files_deleted)
        """
        cache_files_deleted = 0
        image_files_deleted = 0

        # Delete storyboard cache files for this chapter
        chapter_cache_dir = self.cache_dir / f"{chapter_num:02d}"
        if chapter_cache_dir.exists():
            cache_files = list(chapter_cache_dir.glob("*.json"))
            for cache_file in cache_files:
                try:
                    cache_file.unlink()
                    cache_files_deleted += 1
                except Exception as e:
                    print(f"Warning: Failed to delete cache file {cache_file}: {e}")

            # Remove directory if empty
            try:
                if not any(chapter_cache_dir.iterdir()):
                    chapter_cache_dir.rmdir()
            except Exception:
                pass

        # Delete generated images for this chapter
        if self.images_dir.exists():
            # Pattern: chapter_XX_*.png
            image_pattern = f"chapter_{chapter_num:02d}_*.png"
            image_files = list(self.images_dir.glob(image_pattern))
            for image_file in image_files:
                try:
                    image_file.unlink()
                    image_files_deleted += 1
                except Exception as e:
                    print(f"Warning: Failed to delete image file {image_file}: {e}")

        # Update cache index to remove deleted entries
        keys_to_remove = []
        for key, path in self.cache_index.items():
            if chapter_cache_dir in Path(path).parents:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.cache_index[key]

        if keys_to_remove:
            self._save_cache_index()

        return cache_files_deleted, image_files_deleted

    def get_cost_estimate(self) -> Tuple[float, str]:
        """
        Calculate cost estimate based on token usage.

        Returns:
            Tuple of (cost_in_dollars, formatted_report)
        """
        input_cost = (self.stats["total_input_tokens"] / 1_000_000) * HAIKU_INPUT_COST_PER_MILLION
        output_cost = (self.stats["total_output_tokens"] / 1_000_000) * HAIKU_OUTPUT_COST_PER_MILLION
        total_cost = input_cost + output_cost

        report = f"""Storyboard Analysis Cost:
- Cache hits: {self.stats['cache_hits']}
- Cache misses: {self.stats['cache_misses']}
- API calls: {self.stats['api_calls']}
- Input tokens: {self.stats['total_input_tokens']:,}
- Output tokens: {self.stats['total_output_tokens']:,}
- Input cost: ${input_cost:.4f}
- Output cost: ${output_cost:.4f}
- Total cost: ${total_cost:.4f}"""

        return total_cost, report
