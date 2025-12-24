"""
Prompt generator for converting scene content into SDXL image generation prompts.
Uses rule-based extraction of visual elements from scene text.
"""

import re
from typing import Tuple
from config import BASE_STYLE, NEGATIVE_PROMPT


# Character descriptions for visual consistency
CHARACTER_DESCRIPTIONS = {
    "emma": "professional woman in her 40s, Asian American, professional attire",
    "maxim": "factory worker man, Eastern European, work clothes",
    "elena": "older woman in her 60s, Eastern European",
    "tyler": "teenage boy, casual clothing",
    "amara": "young African woman, professional attire"
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


def extract_mood(text: str) -> str:
    """Extract dominant mood/atmosphere from scene text."""
    text_lower = text.lower()

    # Count keyword matches for each mood
    mood_scores = {}
    for mood, keywords in MOOD_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            mood_scores[mood] = score

    # Return mood with highest score
    if mood_scores:
        mood = max(mood_scores, key=mood_scores.get)
        mood_descriptors = {
            "shock": "shocked expression, tense atmosphere, dramatic shadows",
            "warmth": "warm atmosphere, soft shading, inviting composition",
            "tension": "tense atmosphere, high contrast lighting, dramatic angles",
            "reflection": "contemplative mood, thoughtful expression, balanced composition",
            "urgency": "dynamic composition, motion lines, intense energy"
        }
        return mood_descriptors.get(mood, "balanced lighting, neutral mood")

    return "balanced lighting, neutral mood"


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


def extract_key_words(text: str, max_words: int = 4) -> str:
    """
    Extract key visual words from scene for filename generation.

    Args:
        text: Scene content
        max_words: Maximum number of words to extract

    Returns:
        Underscore-separated key words
    """
    # Get setting, characters, and action
    setting = extract_setting(text)
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


def generate_prompt(scene_content: str) -> str:
    """
    Generate SDXL image prompt from scene content.

    Args:
        scene_content: The text content of the scene

    Returns:
        Complete image generation prompt
    """
    # Extract visual elements
    characters = extract_characters(scene_content)
    setting = extract_setting(scene_content)
    time_of_day = extract_time_of_day(scene_content)
    mood = extract_mood(scene_content)
    action = extract_action(scene_content)

    # Build prompt components
    components = []

    # Characters
    if characters:
        char_descriptions = [CHARACTER_DESCRIPTIONS.get(char, char) for char in characters[:2]]
        components.append(", ".join(char_descriptions))
    else:
        components.append("person")

    # Setting
    components.append(f"in {setting}")

    # Action
    if action:
        components.append(action)

    # Mood
    components.append(mood)

    # Time lighting - adapted for graphic novel style
    time_lighting = {
        "morning": "soft morning lighting, gentle shadows",
        "afternoon": "bright daylight, clear definition",
        "evening": "warm evening tones, long shadows",
        "night": "dark tones, dramatic contrast, nighttime scene"
    }
    components.append(time_lighting.get(time_of_day, "natural lighting, clear linework"))

    # Combine with base style
    prompt = ", ".join(components) + ", " + BASE_STYLE

    return prompt


def generate_filename(chapter_num: int, scene_num: int, scene_content: str) -> str:
    """
    Generate descriptive filename for scene image.

    Args:
        chapter_num: Chapter number
        scene_num: Scene number within chapter
        scene_content: Scene text content

    Returns:
        Filename like 'chapter_01_scene_02_emma_factory_reading.png'
    """
    # Extract key words
    key_words = extract_key_words(scene_content)

    # Format with zero-padded numbers
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

    print("Negative Prompt:")
    print(get_negative_prompt())
    print("\n" + "="*80 + "\n")

    filename = generate_filename(1, 1, sample_scene)
    print("Generated Filename:")
    print(filename)


if __name__ == "__main__":
    main()
