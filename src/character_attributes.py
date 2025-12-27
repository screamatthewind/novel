"""
Canonical Character Attribute Definitions

This module defines detailed visual attributes for all main characters in The Obsolescence.
These attributes ensure visual consistency across generated images by providing detailed,
specific descriptions (25-30 tokens each) that minimize SDXL's interpretation variance.

Attributes are organized by category:
- hair: Hairstyle, length, color, accessories
- face: Age, ethnicity, eyes, expression
- clothing: Specific garments, colors, fit
- accessories: Glasses, jewelry, watches, etc.
- skin: Skin tone, complexion
- build: Body type, posture

Usage:
    from character_attributes import get_full_description, get_compressed_description

    # Get full 25-30 token description
    emma_desc = get_full_description("emma")

    # Get compressed version for tight token budgets
    emma_short = get_compressed_description("emma", max_tokens=15)
"""

# Canonical character attribute definitions
# Each character: ~25-30 tokens total across all attributes
CHARACTER_CANONICAL_ATTRIBUTES = {
    "emma": {
        "hair": "shoulder-length straight dark brown hair, NO hat, NO hair accessories",
        "face": "mid-40s Asian American woman, intelligent brown eyes, analytical expression",
        "clothing": "navy blue fitted blazer, crisp white button-up shirt, black slacks, black leather flats",
        "accessories": "NO glasses, NO jewelry, practical silver wristwatch",
        "skin": "light brown skin tone, professional appearance",
        "build": "average build, professional posture, sensible stance"
    },

    "tyler": {
        "hair": "short dark brown hair, messy teenager style, NO hat",
        "face": "16-year-old Asian American teen boy, brown eyes, slightly slouched posture",
        "clothing": "gray hoodie, dark jeans, white sneakers, casual teenage style",
        "accessories": "white earbuds, smartphone in hand, NO glasses",
        "skin": "light brown skin tone, youthful appearance",
        "build": "slim teenage build, casual slouch, relaxed stance"
    },

    "elena": {
        "hair": "short gray hair, practical cut, NO hat, NO hair accessories",
        "face": "60-year-old Russian woman, sharp observant gray eyes, slight frame",
        "clothing": "simple cardigan sweater, dark pants, comfortable shoes, practical style",
        "accessories": "reading glasses on chain around neck, NO jewelry",
        "skin": "pale white skin tone, aged appearance",
        "build": "slight frame, upright posture, alert stance"
    },

    "maxim": {
        "hair": "short dark brown hair with gray streaks, practical working-class cut",
        "face": "mid-40s Russian man, weathered features, observant blue eyes",
        "clothing": "worn work jacket, flannel shirt, dark work pants, sturdy boots",
        "accessories": "NO glasses, NO jewelry, practical digital watch",
        "skin": "pale white skin tone, weathered from labor",
        "build": "strong working-class build, hands that know labor, solid stance"
    },

    "amara": {
        "hair": "natural black hair in short professional style, NO hat",
        "face": "late 40s Black Kenyan woman, fierce dark eyes, determined expression",
        "clothing": "professional African-print blouse, dark skirt, practical shoes",
        "accessories": "small gold earrings, NO glasses, simple necklace",
        "skin": "dark brown skin tone, professional appearance",
        "build": "average build, confident posture, authoritative stance"
    }
}


def get_full_description(character_name: str) -> str:
    """
    Get the full canonical description for a character.

    Combines all attributes into a single comma-separated string
    suitable for SDXL image generation (~25-30 tokens).

    Args:
        character_name: Character name (lowercase, e.g., "emma", "tyler")

    Returns:
        Full character description string, or None if character not found

    Example:
        >>> desc = get_full_description("emma")
        >>> print(desc)
        'mid-40s Asian American woman, intelligent brown eyes, analytical expression, ...'
    """
    if character_name not in CHARACTER_CANONICAL_ATTRIBUTES:
        return None

    attrs = CHARACTER_CANONICAL_ATTRIBUTES[character_name]

    # Combine in order: face, hair, clothing, accessories
    # (Skin and build are typically incorporated into face/clothing naturally)
    parts = [
        attrs["face"],
        attrs["hair"],
        attrs["clothing"],
        attrs["accessories"]
    ]

    return ", ".join(parts)


def get_compressed_description(character_name: str, max_tokens: int = 15) -> str:
    """
    Get a compressed character description for tight token budgets.

    Progressively removes less critical attributes to fit within token limit:
    1. Full description (~30 tokens)
    2. Face + hair + clothing (~20 tokens)
    3. Face + clothing (~15 tokens)
    4. Face only (~8 tokens)

    Args:
        character_name: Character name (lowercase, e.g., "emma", "tyler")
        max_tokens: Maximum token count (approximate, based on word count)

    Returns:
        Compressed character description, or None if character not found

    Example:
        >>> desc = get_compressed_description("emma", max_tokens=8)
        >>> print(desc)
        'mid-40s Asian American woman, intelligent brown eyes, analytical expression'
    """
    if character_name not in CHARACTER_CANONICAL_ATTRIBUTES:
        return None

    attrs = CHARACTER_CANONICAL_ATTRIBUTES[character_name]

    # Estimate: ~1.3 words per token (rough SDXL approximation)
    max_words = int(max_tokens * 1.3)

    # Progressive compression levels
    if max_tokens >= 25:
        # Full description
        return get_full_description(character_name)
    elif max_tokens >= 18:
        # Face + hair + clothing
        parts = [attrs["face"], attrs["hair"], attrs["clothing"]]
        return ", ".join(parts)
    elif max_tokens >= 12:
        # Face + clothing only
        parts = [attrs["face"], attrs["clothing"]]
        return ", ".join(parts)
    else:
        # Face only (minimum viable description)
        return attrs["face"]


def get_attribute(character_name: str, attribute_type: str) -> str:
    """
    Get a specific attribute for a character.

    Args:
        character_name: Character name (lowercase, e.g., "emma", "tyler")
        attribute_type: Attribute category ("hair", "face", "clothing", "accessories", "skin", "build")

    Returns:
        Attribute string, or None if character/attribute not found

    Example:
        >>> hair = get_attribute("emma", "hair")
        >>> print(hair)
        'shoulder-length straight dark brown hair, NO hat, NO hair accessories'
    """
    if character_name not in CHARACTER_CANONICAL_ATTRIBUTES:
        return None

    attrs = CHARACTER_CANONICAL_ATTRIBUTES[character_name]
    return attrs.get(attribute_type)


def get_all_characters() -> list:
    """
    Get list of all characters with canonical attributes defined.

    Returns:
        List of character names (lowercase strings)

    Example:
        >>> characters = get_all_characters()
        >>> print(characters)
        ['emma', 'tyler', 'elena', 'maxim', 'amara']
    """
    return list(CHARACTER_CANONICAL_ATTRIBUTES.keys())


def get_attribute_categories() -> list:
    """
    Get list of all attribute categories.

    Returns:
        List of attribute category names

    Example:
        >>> categories = get_attribute_categories()
        >>> print(categories)
        ['hair', 'face', 'clothing', 'accessories', 'skin', 'build']
    """
    if not CHARACTER_CANONICAL_ATTRIBUTES:
        return []

    # Get categories from first character (all characters have same structure)
    first_char = list(CHARACTER_CANONICAL_ATTRIBUTES.values())[0]
    return list(first_char.keys())


# Backward compatibility: Generate 8-token descriptions for legacy mode
CHARACTER_DESCRIPTIONS_LEGACY = {
    char: get_compressed_description(char, max_tokens=8)
    for char in CHARACTER_CANONICAL_ATTRIBUTES.keys()
}
