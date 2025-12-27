"""
Prompt generator for converting scene content into SDXL image generation prompts.
Supports both keyword-based (legacy) and LLM-based prompt generation.
"""

import re
import os
import json
from typing import Tuple, Optional
from config import BASE_STYLE, NEGATIVE_PROMPT, OLLAMA_BASE_URL, OLLAMA_MODEL, ANTHROPIC_MODEL, ANTHROPIC_MAX_TOKENS
from character_attributes import (
    CHARACTER_CANONICAL_ATTRIBUTES,
    get_full_description,
    get_compressed_description
)


# Character descriptions for visual consistency
# Optimized for SDXL 77-token limit while maintaining consistency
# Legacy mode (non-storyboard): Use 8-token compressed descriptions
CHARACTER_DESCRIPTIONS = {
    char: get_compressed_description(char, max_tokens=8)
    for char in CHARACTER_CANONICAL_ATTRIBUTES.keys()
}

# Setting keywords to detect
SETTINGS = {
    "factory": ["factory", "assembly line", "production floor", "manufacturing", "industrial"],
    "office": ["office", "cubicle", "desk", "conference room", "workplace"],
    "kitchen": ["kitchen", "table", "counter", "stove", "refrigerator"],
    "train": ["train", "metro", "subway", "rail", "platform"],
    "rowhouse": ["rowhouse", "row house", "apartment", "home", "living room", "bedroom"],
    "cafeteria": ["cafeteria", "cafe", "restaurant", "diner", "food court"],
    "street": ["street", "sidewalk", "road", "avenue", "outdoors"],
    "car": ["car", "vehicle", "driving", "dashboard"],
    "warehouse": ["warehouse", "storage", "distribution center"],
    "school": ["school", "classroom", "hallway", "campus"]
}

# Time of day indicators
TIME_INDICATORS = {
    "morning": ["morning", "dawn", "sunrise", "breakfast", "early"],
    "afternoon": ["afternoon", "lunch", "midday", "noon"],
    "evening": ["evening", "dusk", "sunset", "dinner"],
    "night": ["night", "dark", "midnight", "late"]
}

# Mood/atmosphere keywords
MOOD_KEYWORDS = {
    "shock": ["shocked", "stunned", "disbelief", "frozen", "stared"],
    "warmth": ["warm", "cozy", "comfort", "gentle", "soft"],
    "tension": ["tense", "nervous", "anxious", "worried", "uncertain"],
    "reflection": ["thought", "remembered", "considered", "reflected", "pondered"],
    "urgency": ["hurried", "rushed", "quick", "fast", "urgent"]
}

# Action verbs
ACTION_KEYWORDS = {
    "reading": ["read", "reading", "scanned", "looked at", "viewed"],
    "working": ["working", "operated", "assembled", "built", "typed"],
    "talking": ["talked", "spoke", "said", "conversation", "discussed"],
    "walking": ["walked", "walking", "moved", "stepped", "approached"],
    "watching": ["watched", "watching", "observed", "monitored", "stared"]
}


def normalize_character_name(full_name: str) -> str:
    """
    Normalize a character's full name to their canonical short name.

    Handles variations like "Emma Chen" → "emma", "Elena Volkov" → "elena", etc.

    Args:
        full_name: Full character name (may include spaces, capitals)

    Returns:
        Normalized short name (lowercase, first name only)

    Example:
        >>> normalize_character_name("Emma Chen")
        'emma'
        >>> normalize_character_name("TYLER")
        'tyler'
    """
    # Mapping of full names (and variations) to canonical short names
    name_mapping = {
        'emma': 'emma', 'emma chen': 'emma',
        'tyler': 'tyler', 'tyler chen': 'tyler',
        'elena': 'elena', 'elena volkov': 'elena',
        'maxim': 'maxim', 'maxim orlov': 'maxim',
        'amara': 'amara', 'amara okafor': 'amara',
        'wei': 'wei', 'wei chen': 'wei'
    }

    normalized = full_name.lower().strip()
    return name_mapping.get(normalized, normalized.split()[0])  # Default to first name


def extract_characters(text: str) -> list:
    """Extract character names mentioned in the scene."""
    characters = []
    text_lower = text.lower()

    # Check for each known character
    if "emma" in text_lower:
        characters.append("emma")
    if "maxim" in text_lower:
        characters.append("maxim")
    if "elena" in text_lower:
        characters.append("elena")
    if "tyler" in text_lower:
        characters.append("tyler")
    if "amara" in text_lower:
        characters.append("amara")
    if "wei" in text_lower:
        characters.append("wei")

    return characters


def extract_setting(text: str) -> str:
    """Extract primary setting from scene text."""
    text_lower = text.lower()

    # Count keyword matches for each setting
    setting_scores = {}
    for setting, keywords in SETTINGS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            setting_scores[setting] = score

    # Return setting with highest score
    if setting_scores:
        return max(setting_scores, key=setting_scores.get)

    return "interior scene"


def extract_time_of_day(text: str) -> str:
    """Extract time of day from scene text."""
    text_lower = text.lower()

    # Check for time indicators
    for time_period, keywords in TIME_INDICATORS.items():
        if any(keyword in text_lower for keyword in keywords):
            return time_period

    return "daytime"


def extract_mood(text: str, time_of_day: str = "daytime") -> str:
    """Extract dominant mood/atmosphere from scene text and combine with lighting."""
    text_lower = text.lower()

    # Count keyword matches for each mood
    mood_scores = {}
    for mood, keywords in MOOD_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            mood_scores[mood] = score

    # Time-based lighting descriptors
    time_lighting = {
        "morning": "soft morning light",
        "afternoon": "bright daylight",
        "evening": "warm evening tones",
        "night": "dark tones, nighttime"
    }
    lighting = time_lighting.get(time_of_day, "natural lighting")

    # Return mood with highest score, combined with lighting
    if mood_scores:
        mood = max(mood_scores, key=mood_scores.get)
        mood_descriptors = {
            "shock": f"shocked expression, dramatic shadows, {lighting}",
            "warmth": f"warm atmosphere, soft shading, {lighting}",
            "tension": f"tense atmosphere, high contrast, {lighting}",
            "reflection": f"contemplative mood, balanced composition, {lighting}",
            "urgency": f"dynamic composition, intense energy, {lighting}"
        }
        return mood_descriptors.get(mood, f"neutral mood, {lighting}")

    return f"neutral mood, {lighting}"


def extract_action(text: str) -> str:
    """Extract primary action from scene text."""
    text_lower = text.lower()

    # Check for action keywords
    for action, keywords in ACTION_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            action_descriptors = {
                "reading": "reading document or screen",
                "working": "working with equipment or tools",
                "talking": "in conversation",
                "walking": "walking or moving",
                "watching": "observing or watching"
            }
            return action_descriptors.get(action, "")

    return ""


def extract_key_words(text: str, scene_context: str = None, max_words: int = 4) -> str:
    """
    Extract key visual words from scene for filename generation.

    Args:
        text: Sentence or scene content
        scene_context: Optional full scene text for context (used for setting extraction)
        max_words: Maximum number of words to extract

    Returns:
        Underscore-separated key words
    """
    # Get setting from scene context if provided, otherwise from text
    # Use scene_context for setting to ensure consistency across sentences in the scene
    context_text = scene_context if scene_context else text
    setting = extract_setting(context_text)

    # Get characters and action from the specific sentence text
    characters = extract_characters(text)
    action = extract_action(text)

    # Build key words list
    key_words = []

    # Add primary character if present
    if characters:
        key_words.append(characters[0])

    # Add setting
    key_words.append(setting.replace(" ", "_"))

    # Add action keyword if present
    if action:
        action_word = action.split()[0]  # Get first word
        if action_word not in key_words:
            key_words.append(action_word)

    # Limit to max_words
    key_words = key_words[:max_words]

    return "_".join(key_words)


def generate_prompt(scene_content: str, scene_context: str = None) -> str:
    """
    Generate SDXL image prompt from scene content.

    Uses natural language descriptions optimized for SDXL (not keyword lists).

    Args:
        scene_content: The text content of the sentence
        scene_context: Optional full scene text for context (used for setting extraction)

    Returns:
        Complete image generation prompt in natural language
    """
    # Extract visual elements
    # Use scene_context for setting/environment to ensure consistency across sentences
    # Use scene_content for characters/action to focus on the specific sentence
    characters = extract_characters(scene_content)
    context_text = scene_context if scene_context else scene_content
    setting = extract_setting(context_text)
    time_of_day = extract_time_of_day(context_text)
    mood = extract_mood(context_text, time_of_day)
    action = extract_action(scene_content)

    # Build natural language description
    prompt_parts = []

    # Start with scene description
    if characters:
        # Get character descriptions
        char_descs = [CHARACTER_DESCRIPTIONS.get(char, char) for char in characters[:1]]  # Focus on one character
        char_desc = char_descs[0] if char_descs else "a person"

        # Build natural sentence
        if action:
            prompt_parts.append(f"A {char_desc} {action.replace('in conversation', 'talking').replace('working with equipment or tools', 'working')}")
        else:
            prompt_parts.append(f"A {char_desc}")

        prompt_parts.append(f"in a {setting}")
    else:
        # No specific character
        if action:
            prompt_parts.append(f"A scene showing someone {action.replace('in conversation', 'talking')}")
        else:
            prompt_parts.append(f"A view of a {setting}")

    # Add mood/atmosphere
    if mood:
        # Extract just the key mood descriptor
        mood_clean = mood.split(',')[0]  # Get first part before comma
        prompt_parts.append(f"with {mood_clean}")

    # Combine into natural language prompt
    base_description = " ".join(prompt_parts) + "."

    # Add style specification
    full_prompt = f"{base_description} {BASE_STYLE}"

    return full_prompt


def count_tokens(prompt: str) -> int:
    """
    Count the number of CLIP tokens in a prompt.

    Args:
        prompt: The text prompt to tokenize

    Returns:
        Number of tokens (SDXL has a 77-token limit)
    """
    try:
        from transformers import CLIPTokenizer

        # Load SDXL's CLIP tokenizer
        tokenizer = CLIPTokenizer.from_pretrained(
            "openai/clip-vit-large-patch14"
        )

        # Tokenize the prompt
        tokens = tokenizer(prompt, truncation=False, add_special_tokens=True)
        token_count = len(tokens["input_ids"])

        return token_count

    except ImportError:
        # If transformers not available, estimate based on words
        # Rough estimate: ~1.3 tokens per word on average
        word_count = len(prompt.split())
        estimated_tokens = int(word_count * 1.3)
        print(f"  WARNING: transformers library not available, estimating {estimated_tokens} tokens")
        return estimated_tokens


def validate_prompt_length(prompt: str, max_tokens: int = 77) -> Tuple[bool, int]:
    """
    Validate that a prompt is within SDXL's token limit.

    Args:
        prompt: The prompt to validate
        max_tokens: Maximum allowed tokens (default: 77 for SDXL)

    Returns:
        Tuple of (is_valid, token_count)
    """
    token_count = count_tokens(prompt)
    is_valid = token_count <= max_tokens

    if not is_valid:
        print(f"  WARNING: WARNING: Prompt has {token_count} tokens (limit: {max_tokens})")
        print(f"  Prompt will be truncated by SDXL!")

    return is_valid, token_count


def generate_filename(chapter_num: int, scene_num: int, scene_content: str, sentence_num: int = None, scene_context: str = None) -> str:
    """
    Generate descriptive filename for scene image.

    Args:
        chapter_num: Chapter number
        scene_num: Scene number within chapter
        scene_content: Sentence or scene text content
        sentence_num: Optional sentence number within scene
        scene_context: Optional full scene text for context (used for setting extraction)

    Returns:
        Filename like 'chapter_01_scene_02_sent_03_emma_factory_reading.png'
        or 'chapter_01_scene_02_emma_factory_reading.png' if sentence_num not provided
    """
    # Extract key words, using scene context for setting if provided
    key_words = extract_key_words(scene_content, scene_context=scene_context)

    # Format with zero-padded numbers
    if sentence_num is not None:
        filename = f"chapter_{chapter_num:02d}_scene_{scene_num:02d}_sent_{sentence_num:03d}_{key_words}.png"
    else:
        filename = f"chapter_{chapter_num:02d}_scene_{scene_num:02d}_{key_words}.png"

    return filename


def get_negative_prompt() -> str:
    """Return the standard negative prompt for all images."""
    return NEGATIVE_PROMPT


# ============================================================================
# LLM-BASED PROMPT GENERATION
# ============================================================================

def generate_prompt_with_ollama(sentence: str, scene_context: str = None) -> Optional[str]:
    """
    Generate SDXL prompt using Ollama (local LLM).

    Args:
        sentence: The specific sentence to generate prompt for
        scene_context: Full scene text for continuity

    Returns:
        Generated prompt string, or None if failed
    """
    try:
        import requests
    except ImportError:
        print("  WARNING: requests library not available. Install with: pip install requests")
        return None

    # Build LLM prompt
    llm_prompt = _build_llm_prompt(sentence, scene_context)

    # Call Ollama API
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": llm_prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        generated_prompt = result.get("response", "").strip()

        if not generated_prompt:
            print("  WARNING: Ollama returned empty response")
            return None

        return generated_prompt

    except requests.exceptions.ConnectionError:
        print(f"  WARNING: Could not connect to Ollama at {OLLAMA_BASE_URL}")
        print(f"  Make sure Ollama is running and model is downloaded: ollama pull {OLLAMA_MODEL}")
        return None
    except Exception as e:
        print(f"  WARNING: Ollama error: {str(e)[:100]}")
        return None


def generate_prompt_with_haiku(sentence: str, scene_context: str = None, cost_tracker=None) -> tuple:
    """
    Generate SDXL prompt using Claude Haiku (Anthropic API).

    Args:
        sentence: The specific sentence to generate prompt for
        scene_context: Full scene text for continuity
        cost_tracker: Optional CostTracker instance to record usage

    Returns:
        Tuple of (generated_prompt, input_tokens, output_tokens)
        Returns (None, 0, 0) if failed
    """
    try:
        import anthropic
    except ImportError:
        print("  WARNING: anthropic library not available. Install with: pip install anthropic")
        return None, 0, 0

    # Check for API key (loaded from .env file via config.py)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  WARNING: ANTHROPIC_API_KEY not found")
        print("  Add it to .env file in project root: ANTHROPIC_API_KEY=your_key_here")
        return None, 0, 0

    # Build LLM prompt
    llm_prompt = _build_llm_prompt(sentence, scene_context)

    # Call Claude API
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=ANTHROPIC_MAX_TOKENS,
            messages=[
                {"role": "user", "content": llm_prompt}
            ]
        )

        generated_prompt = message.content[0].text.strip()

        # Extract token usage from response
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

        # Track costs if tracker provided
        if cost_tracker:
            cost_tracker.add_api_call(input_tokens, output_tokens)

        if not generated_prompt:
            print("  WARNING: Claude returned empty response")
            return None, input_tokens, output_tokens

        return generated_prompt, input_tokens, output_tokens

    except Exception as e:
        print(f"  WARNING: Claude API error: {e}")
        return None, 0, 0


def _build_llm_prompt(sentence: str, scene_context: str = None) -> str:
    """
    Build the prompt to send to the LLM for generating SDXL prompts.

    Args:
        sentence: The specific sentence to generate prompt for
        scene_context: Full scene text for continuity

    Returns:
        Formatted LLM prompt string
    """
    # Get scene context snippet (first 300 chars for context without overwhelming)
    context_snippet = ""
    if scene_context:
        context_snippet = scene_context[:300].strip()
        if len(scene_context) > 300:
            context_snippet += "..."

    # Get character descriptions for characters in scene
    characters_in_scene = extract_characters(sentence)
    if scene_context:
        characters_in_scene.extend(extract_characters(scene_context))
    characters_in_scene = list(set(characters_in_scene))  # Remove duplicates

    char_desc_text = ""
    if characters_in_scene:
        char_desc_lines = [f"- {char.title()}: {CHARACTER_DESCRIPTIONS.get(char, 'unknown')}"
                          for char in characters_in_scene]
        char_desc_text = "\n".join(char_desc_lines)

    # Build the LLM prompt
    llm_prompt = f"""You are generating image prompts for Stable Diffusion XL to illustrate a novel.

Given this sentence from the novel:
"{sentence}"
"""

    if context_snippet:
        llm_prompt += f"""
Scene context (for continuity):
"{context_snippet}"
"""

    if char_desc_text:
        llm_prompt += f"""
Character visual descriptions:
{char_desc_text}
"""

    llm_prompt += f"""
Generate a natural language SDXL prompt (under 77 tokens) that:
1. Focuses on what's happening in THIS specific sentence
2. Includes key objects/details mentioned in the sentence
3. Describes character expression/posture specific to this moment
4. Only mentions setting if it's central to the sentence
5. Uses this artistic style: {BASE_STYLE}

Return ONLY the prompt text, nothing else. Do not include explanations or meta-commentary."""

    return llm_prompt


def generate_prompt_with_llm(sentence: str, scene_context: str = None, method: str = "ollama", cost_tracker=None) -> tuple:
    """
    Generate SDXL prompt using specified LLM method.

    Args:
        sentence: The specific sentence to generate prompt for
        scene_context: Full scene text for continuity
        method: Which LLM to use ("ollama" or "haiku")
        cost_tracker: Optional CostTracker instance (for haiku only)

    Returns:
        For haiku: Tuple of (generated_prompt, input_tokens, output_tokens)
        For ollama: Tuple of (generated_prompt, 0, 0)
        Returns (None, 0, 0) if failed
    """
    if method == "ollama":
        prompt = generate_prompt_with_ollama(sentence, scene_context)
        return prompt, 0, 0
    elif method == "haiku":
        return generate_prompt_with_haiku(sentence, scene_context, cost_tracker)
    else:
        print(f"  WARNING: Unknown LLM method: {method}")
        return None, 0, 0


def generate_prompts_comparison(sentence: str, scene_context: str = None, cost_tracker=None) -> dict:
    """
    Generate prompts using all methods (keyword, ollama, haiku) for comparison.

    Args:
        sentence: The specific sentence to generate prompt for
        scene_context: Full scene text for continuity
        cost_tracker: Optional CostTracker instance for haiku

    Returns:
        Dictionary with keys: "keyword", "ollama", "haiku", "tokens"
        Each prompt value is the generated prompt (or None if failed)
        "tokens" contains dict with "input" and "output" for haiku usage
    """
    results = {}
    tokens = {"input": 0, "output": 0}

    # Keyword-based (original method)
    print("  Generating keyword-based prompt...")
    results["keyword"] = generate_prompt(sentence, scene_context)

    # Ollama
    print("  Generating Ollama prompt...")
    results["ollama"] = generate_prompt_with_ollama(sentence, scene_context)

    # Claude Haiku
    print("  Generating Haiku prompt...")
    haiku_prompt, input_tokens, output_tokens = generate_prompt_with_haiku(sentence, scene_context, cost_tracker)
    results["haiku"] = haiku_prompt
    tokens["input"] = input_tokens
    tokens["output"] = output_tokens

    results["tokens"] = tokens
    return results


# ============================================================================
# STORYBOARD-INFORMED PROMPT GENERATION
# ============================================================================

def generate_storyboard_informed_prompt(sentence_content: str, storyboard_analysis, scene_context: str = None, attribute_manager=None) -> str:
    """
    Generate SDXL prompt from storyboard analysis.

    Token Budget Strategy (77 tokens total):
    - 25-30 tokens: Character description (from attribute manager if available)
    - 8 tokens: Camera angle/framing
    - 8 tokens: Primary action/pose
    - 5 tokens: Mood/expression
    - 15 tokens: Style (BASE_STYLE)
    - 6-11 tokens: Buffer

    Progressive compression if over 77 tokens:
    1. Remove mood
    2. Remove action
    3. Compress character to face + clothing (20 tokens)
    4. Compress character to face only (8 tokens)

    Prompt Template:
    {camera_framing} {camera_angle}. {character_desc} {expression} {action}.
    {composition}. {mood}. {BASE_STYLE}

    Args:
        sentence_content: The sentence text
        storyboard_analysis: StoryboardAnalysis object with detailed visual info
        scene_context: Optional scene context (not heavily used, storyboard has better info)
        attribute_manager: Optional AttributeStateManager for current character attributes

    Returns:
        Complete SDXL prompt optimized for 77-token limit
    """
    prompt_parts = []

    # Camera framing and angle (8 tokens budget)
    camera_part = f"{storyboard_analysis.camera_framing}, {storyboard_analysis.camera_angle}"
    prompt_parts.append(camera_part)

    # Character description with expression (25-30 tokens budget if using attribute manager)
    if storyboard_analysis.characters_present:
        primary_char = normalize_character_name(storyboard_analysis.characters_present[0])

        # Use attribute manager if available for detailed, consistent descriptions
        if attribute_manager:
            char_state = attribute_manager.get_current_attributes(primary_char)
            if char_state:
                char_desc = char_state.to_prompt_string()  # ~25-30 tokens
            else:
                # Fallback to canonical if character not in manager
                char_desc = get_compressed_description(primary_char, max_tokens=28)
                if not char_desc:
                    char_desc = CHARACTER_DESCRIPTIONS.get(primary_char, primary_char)
        else:
            # Legacy mode: use short 8-token descriptions
            char_desc = CHARACTER_DESCRIPTIONS.get(primary_char, primary_char)

        # Add expression if available
        # Check for both normalized and original name in expressions dict
        expression = None
        if storyboard_analysis.expressions:
            expression = storyboard_analysis.expressions.get(
                primary_char,
                storyboard_analysis.expressions.get(storyboard_analysis.characters_present[0])
            )

        if expression:
            char_part = f"{char_desc}, {expression}"
        else:
            char_part = char_desc

        prompt_parts.append(char_part)

    # Action/body language (8 tokens budget)
    if storyboard_analysis.movement:
        prompt_parts.append(storyboard_analysis.movement)
    elif storyboard_analysis.body_language and storyboard_analysis.characters_present:
        primary_char_bodylang = normalize_character_name(storyboard_analysis.characters_present[0])
        # Check for both normalized and original name in body_language dict
        body_lang = storyboard_analysis.body_language.get(
            primary_char_bodylang,
            storyboard_analysis.body_language.get(storyboard_analysis.characters_present[0])
        )
        if body_lang:
            prompt_parts.append(body_lang)

    # Composition and visual focus (10 tokens budget)
    if storyboard_analysis.visual_focus:
        prompt_parts.append(f"focus on {storyboard_analysis.visual_focus}")
    elif storyboard_analysis.composition:
        # Take first part of composition (truncate if too long)
        comp = storyboard_analysis.composition.split('.')[0][:50]
        prompt_parts.append(comp)

    # Setting/spatial context (8 tokens budget)
    if storyboard_analysis.spatial_context:
        # Extract key location words (remove verbose descriptions)
        location = storyboard_analysis.spatial_context.split(',')[0][:40]
        prompt_parts.append(f"in {location}")

    # Mood and lighting (8 tokens budget)
    mood_parts = []
    if storyboard_analysis.mood:
        mood_parts.append(storyboard_analysis.mood)
    if storyboard_analysis.lighting_suggestion:
        mood_parts.append(storyboard_analysis.lighting_suggestion)

    if mood_parts:
        mood_text = ", ".join(mood_parts)[:50]  # Truncate if too long
        prompt_parts.append(mood_text)

    # Combine all parts
    base_description = ". ".join(prompt_parts) + "."

    # Add style specification (15 tokens budget)
    full_prompt = f"{base_description} {BASE_STYLE}"

    # Validate token count and trim if necessary
    is_valid, token_count = validate_prompt_length(full_prompt, max_tokens=77)

    if not is_valid:
        # Progressive compression strategy
        # 1. Remove mood
        # 2. Remove action
        # 3. Compress character to face + clothing (20 tokens)
        # 4. Compress character to face only (8 tokens)

        prompt_parts_trimmed = []

        # Always keep camera
        prompt_parts_trimmed.append(camera_part)

        # Always keep character (start with compressed version)
        if storyboard_analysis.characters_present:
            primary_char = normalize_character_name(storyboard_analysis.characters_present[0])

            # Try progressively compressed character descriptions
            # Start with 8-token budget to ensure clothing is included
            if attribute_manager:
                char_state = attribute_manager.get_current_attributes(primary_char)
                if char_state:
                    # Try 8-token version (face + compressed clothing)
                    char_desc = char_state.to_compressed_string(max_tokens=8)
                else:
                    char_desc = get_compressed_description(primary_char, max_tokens=8)
                    if not char_desc:
                        char_desc = CHARACTER_DESCRIPTIONS.get(primary_char, primary_char)
            else:
                char_desc = CHARACTER_DESCRIPTIONS.get(primary_char, primary_char)

            prompt_parts_trimmed.append(char_desc)

        # Add back elements one by one until we approach limit
        remaining_parts = []
        if storyboard_analysis.expressions and storyboard_analysis.characters_present:
            primary_char_expr = normalize_character_name(storyboard_analysis.characters_present[0])
            # Check for both normalized and original name in expressions dict
            expression = storyboard_analysis.expressions.get(
                primary_char_expr,
                storyboard_analysis.expressions.get(storyboard_analysis.characters_present[0])
            )
            if expression:
                remaining_parts.append(expression)

        if storyboard_analysis.visual_focus:
            remaining_parts.append(f"focus on {storyboard_analysis.visual_focus}")

        if storyboard_analysis.mood:
            remaining_parts.append(storyboard_analysis.mood.split(',')[0])

        # Add remaining parts until we hit token limit
        for part in remaining_parts:
            test_prompt = ". ".join(prompt_parts_trimmed + [part]) + f". {BASE_STYLE}"
            test_valid, test_count = validate_prompt_length(test_prompt, max_tokens=77)
            if test_valid:
                prompt_parts_trimmed.append(part)
            else:
                break  # Stop adding, we've hit the limit

        full_prompt = ". ".join(prompt_parts_trimmed) + f". {BASE_STYLE}"

    return full_prompt


def main():
    """Test prompt generation with sample scene text."""
    # Sample scene text
    sample_scene = """
    Emma stared at the email on her tablet. The factory floor hummed with the sound
    of machines. She felt a shock run through her body as she read the layoff notice.
    The afternoon sun streamed through the industrial windows.
    """

    print("Sample Scene:")
    print(sample_scene)
    print("\n" + "="*80 + "\n")

    prompt = generate_prompt(sample_scene)
    print("Generated Prompt (Graphic Novel Style):")
    print(prompt)
    print("\n" + "="*80 + "\n")

    # Validate token count
    is_valid, token_count = validate_prompt_length(prompt)
    print(f"Token Count: {token_count}/77")
    if is_valid:
        print("OK - Prompt is within SDXL token limit")
    else:
        print("ERROR - Prompt EXCEEDS token limit and will be truncated!")
    print("\n" + "="*80 + "\n")

    print("Negative Prompt:")
    print(get_negative_prompt())
    print("\n" + "="*80 + "\n")

    filename = generate_filename(1, 1, sample_scene)
    print("Generated Filename:")
    print(filename)


if __name__ == "__main__":
    main()
