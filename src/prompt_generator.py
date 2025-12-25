"""
Prompt generator for converting scene content into SDXL image generation prompts.
Uses rule-based extraction of visual elements from scene text.
"""

import re
from typing import Tuple
from config import BASE_STYLE, NEGATIVE_PROMPT


# Character descriptions for visual consistency
# Optimized for SDXL 77-token limit while maintaining consistency
CHARACTER_DESCRIPTIONS = {
    "emma": "Asian American woman 40s, dark hair, business attire, analytical",
    "maxim": "Eastern European man 40s, factory work clothes, tired resilient",
    "elena": "woman 60s, gray hair, sharp eyes, Eastern European, analytical",
    "tyler": "Asian American teen 16, casual clothes, earbuds, phone",
    "amara": "African woman 50s, Kenyan, professional attire, fierce"
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
        print(f"  ⚠ transformers library not available, estimating {estimated_tokens} tokens")
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
        print(f"  ⚠ WARNING: Prompt has {token_count} tokens (limit: {max_tokens})")
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
