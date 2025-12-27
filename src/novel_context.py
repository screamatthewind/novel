"""
Novel context parser for extracting canonical character descriptions
from The Obsolescence Novel Bible.
"""

import re
from pathlib import Path
from typing import Dict, Optional


class NovelContext:
    """Parses Novel Bible for canonical character descriptions."""

    def __init__(self, bible_path: str = "../docs/reference/The_Obsolescence_Novel_Bible.md"):
        """
        Initialize novel context parser.

        Args:
            bible_path: Path to Novel Bible markdown file
        """
        self.bible_path = Path(bible_path)
        self.character_descriptions = self._extract_characters()

    def _extract_characters(self) -> Dict[str, str]:
        """
        Extract character descriptions from Novel Bible.

        Returns:
            Dictionary mapping character names to descriptions
        """
        if not self.bible_path.exists():
            print(f"Warning: Novel Bible not found at {self.bible_path}")
            return self._get_default_descriptions()

        try:
            with open(self.bible_path, 'r', encoding='utf-8') as f:
                content = f.read()

            characters = {}

            # Extract Emma Chen
            emma_match = re.search(
                r'EMMA CHEN.*?Age: (.*?).*?Appearance: (.*?)(?=\n\nPersonality:)',
                content,
                re.DOTALL
            )
            if emma_match:
                age = emma_match.group(1).strip()
                appearance = emma_match.group(2).strip()
                characters['emma'] = f"{age} Asian American woman, {appearance.lower()}"

            # Extract Tyler Chen
            tyler_match = re.search(
                r'TYLER CHEN.*?Age: (.*?).*?Appearance: (.*?)(?=\n\nPersonality:)',
                content,
                re.DOTALL
            )
            if tyler_match:
                age = tyler_match.group(1).strip()
                appearance = tyler_match.group(2).strip()
                characters['tyler'] = f"{age}, {appearance.lower()}"

            # Extract Elena Volkov
            elena_match = re.search(
                r'ELENA VOLKOV.*?Age: (.*?).*?Appearance: (.*?)(?=\n\nBackground:)',
                content,
                re.DOTALL
            )
            if elena_match:
                age = elena_match.group(1).strip()
                appearance = elena_match.group(2).strip()
                characters['elena'] = f"{age}, {appearance.lower()}"

            # Extract Maxim Orlov
            maxim_match = re.search(
                r'MAXIM ORLOV.*?Age: (.*?).*?Appearance: (.*?)(?=\n\nBackground:)',
                content,
                re.DOTALL
            )
            if maxim_match:
                age = maxim_match.group(1).strip()
                appearance = maxim_match.group(2).strip()
                characters['maxim'] = f"{age} Russian, {appearance.lower()}"

            # Extract Amara Okafor
            amara_match = re.search(
                r'AMARA OKAFOR.*?Age: (.*?)(?=\n\nBackground:)',
                content,
                re.DOTALL
            )
            if amara_match:
                age = amara_match.group(1).strip()
                # Amara has minimal appearance description in bible
                characters['amara'] = f"{age} Kenyan woman, fierce, pragmatic"

            # If extraction failed, use defaults
            if not characters:
                return self._get_default_descriptions()

            return characters

        except Exception as e:
            print(f"Warning: Failed to parse Novel Bible: {e}")
            return self._get_default_descriptions()

    def _get_default_descriptions(self) -> Dict[str, str]:
        """
        Get default character descriptions as fallback.

        Returns:
            Dictionary of default character descriptions
        """
        return {
            "emma": "Mid-40s Asian American woman, practical professional, sensible shoes",
            "tyler": "16-year-old, typical teenager, slouch, earbuds, phone",
            "elena": "Approximately 60, short gray hair, sharp eyes, slight frame, analytical",
            "maxim": "Mid-40s Russian, working-class, hands that know labor",
            "amara": "Late 40s-50s Kenyan woman, fierce, pragmatic",
            "wei": "Chinese strategist, brilliant, analytical",
            # Secondary characters
            "mark": "Emma's husband, supportive",
            "katya": "Former Russian economist",
            "diane": "Professional woman",
            "ramirez": "Professional",
        }

    def get_character_context(self, character_name: str) -> str:
        """
        Get canonical description for a character.

        Args:
            character_name: Character name (case-insensitive)

        Returns:
            Character description string, or empty string if not found
        """
        char_key = character_name.lower().strip()
        return self.character_descriptions.get(char_key, "")

    def get_all_character_contexts(self, character_names: list[str]) -> str:
        """
        Get combined context for multiple characters.

        Args:
            character_names: List of character names

        Returns:
            Formatted string with all character descriptions
        """
        if not character_names:
            return ""

        contexts = []
        for name in character_names:
            desc = self.get_character_context(name)
            if desc:
                contexts.append(f"{name.title()}: {desc}")

        return "\n".join(contexts) if contexts else ""

    def extract_character_from_sentence(self, sentence: str) -> list[str]:
        """
        Extract character names mentioned in a sentence.

        Args:
            sentence: Sentence text to analyze

        Returns:
            List of character names found
        """
        # Simple name matching - could be enhanced with NER
        found_characters = []

        for char_name in self.character_descriptions.keys():
            # Match full name (case-insensitive)
            if char_name.lower() in sentence.lower():
                found_characters.append(char_name)

        # Check for pronouns and common patterns
        # This is basic - storyboard analyzer will do deeper analysis
        if any(word in sentence.lower() for word in ['emma', 'she', 'her']) and 'emma' in self.character_descriptions:
            if 'emma' not in found_characters:
                # Only add if context suggests Emma (this is heuristic)
                pass

        return found_characters


def main():
    """Test the novel context parser."""
    context = NovelContext()

    print("Character Descriptions from Novel Bible:\n")

    for char_name in ['Emma', 'Tyler', 'Elena', 'Maxim', 'Amara']:
        desc = context.get_character_context(char_name)
        print(f"{char_name}: {desc}")
        print()

    # Test multi-character context
    print("\nMulti-character context for Emma and Tyler:")
    multi = context.get_all_character_contexts(['Emma', 'Tyler'])
    print(multi)


if __name__ == "__main__":
    main()
