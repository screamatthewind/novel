"""
Character Attribute State Manager

Tracks and persists character visual attributes across sentences within a chapter.
Ensures character appearance consistency by maintaining state and only updating
attributes when explicitly mentioned in the story.

Key features:
- Lazy initialization from canonical attributes
- Persistence across sentences and scenes within a chapter
- Change tracking with history and reasoning
- Progressive compression for tight token budgets
- Statistics for debugging and validation

Lifecycle:
- Attributes persist across sentences within a chapter
- Attributes persist across scene breaks ('* * *') within a chapter
- Attributes reset to canonical at chapter boundaries
- Updates only occur on explicit story mentions (via storyboard analyzer)

Usage:
    manager = AttributeStateManager(chapter_num=1)
    state = manager.get_current_attributes("emma")
    prompt_desc = state.to_prompt_string()

    # When story mentions "removed her blazer"
    manager.update_attribute("emma", "clothing", "white button-up shirt, black slacks",
                            sentence_num=42, reason="removed blazer")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class AttributeChange:
    """Record of a single attribute change."""
    sentence_num: int
    attribute_type: str  # "hair", "clothing", "accessories", etc.
    old_value: str
    new_value: str
    reason: str  # Why the change occurred (from story text)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "sentence_num": self.sentence_num,
            "attribute_type": self.attribute_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "timestamp": self.timestamp
        }


@dataclass
class CharacterAttributeState:
    """
    Current visual state for a single character.

    Tracks all mutable attributes with change history.
    Face, skin, and build are read-only (controlled by IP-Adapter).
    """
    character_name: str
    hair: str
    face: str  # Read-only (IP-Adapter controls facial features)
    clothing: str
    accessories: str
    skin: str  # Read-only
    build: str  # Read-only
    last_updated_sentence: int = 0
    change_history: List[AttributeChange] = field(default_factory=list)

    # Mutable attribute categories (can be changed by story events)
    MUTABLE_ATTRIBUTES = {"hair", "clothing", "accessories"}

    # Read-only attribute categories (controlled by IP-Adapter/canonical)
    READONLY_ATTRIBUTES = {"face", "skin", "build"}

    def to_prompt_string(self) -> str:
        """
        Generate SDXL-ready description for image prompts.

        Combines all current attributes in priority order:
        face, hair, clothing, accessories.

        Returns:
            Comma-separated description string (~25-30 tokens)

        Example:
            'mid-40s Asian American woman, intelligent brown eyes, shoulder-length dark brown hair, ...'
        """
        # Order: face, hair, clothing, accessories
        # (Skin and build are typically incorporated naturally)
        parts = [
            self.face,
            self.hair,
            self.clothing,
            self.accessories
        ]

        return ", ".join(parts)

    def to_compressed_string(self, max_tokens: int = 15) -> str:
        """
        Generate compressed description for tight token budgets.

        Progressive compression:
        - 25+ tokens: Full description
        - 18+ tokens: Face + hair + clothing
        - 12+ tokens: Face + clothing
        - <12 tokens: Face only

        Args:
            max_tokens: Target token count (approximate)

        Returns:
            Compressed description string

        Example:
            >>> state.to_compressed_string(max_tokens=12)
            'mid-40s Asian American woman, navy blue fitted blazer, white shirt'
        """
        if max_tokens >= 25:
            # Full description
            return self.to_prompt_string()
        elif max_tokens >= 18:
            # Face + hair + clothing
            parts = [self.face, self.hair, self.clothing]
            return ", ".join(parts)
        elif max_tokens >= 12:
            # Face + clothing only
            parts = [self.face, self.clothing]
            return ", ".join(parts)
        else:
            # Face only (minimum viable)
            return self.face

    def update_attribute(self, attribute_type: str, new_value: str,
                        sentence_num: int, reason: str) -> bool:
        """
        Update a mutable attribute with change tracking.

        Args:
            attribute_type: Attribute category to update ("hair", "clothing", "accessories")
            new_value: New attribute value
            sentence_num: Sentence number where change occurred
            reason: Explanation from story text (e.g., "removed blazer")

        Returns:
            True if update succeeded, False if attribute is read-only

        Example:
            >>> state.update_attribute("clothing", "white shirt, black slacks",
            ...                       sentence_num=42, reason="removed blazer")
            True
        """
        # Validate attribute is mutable
        if attribute_type not in self.MUTABLE_ATTRIBUTES:
            print(f"Warning: Cannot update read-only attribute '{attribute_type}' for {self.character_name}")
            return False

        # Get current value
        old_value = getattr(self, attribute_type)

        # Record change
        change = AttributeChange(
            sentence_num=sentence_num,
            attribute_type=attribute_type,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )
        self.change_history.append(change)

        # Update attribute
        setattr(self, attribute_type, new_value)
        self.last_updated_sentence = sentence_num

        return True

    def get_change_count(self) -> int:
        """Get total number of attribute changes."""
        return len(self.change_history)

    def get_changes_by_type(self, attribute_type: str) -> List[AttributeChange]:
        """Get all changes for a specific attribute type."""
        return [c for c in self.change_history if c.attribute_type == attribute_type]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization/logging."""
        return {
            "character_name": self.character_name,
            "hair": self.hair,
            "face": self.face,
            "clothing": self.clothing,
            "accessories": self.accessories,
            "skin": self.skin,
            "build": self.build,
            "last_updated_sentence": self.last_updated_sentence,
            "change_count": self.get_change_count(),
            "change_history": [c.to_dict() for c in self.change_history]
        }


class AttributeStateManager:
    """
    Manages character attribute state across a chapter.

    Provides lazy initialization, state tracking, and persistence for character
    visual attributes throughout a chapter's generation process.

    Lifecycle:
    - One manager per chapter
    - Attributes persist across sentences and scenes within chapter
    - Reset to canonical at chapter boundaries

    Usage:
        manager = AttributeStateManager(chapter_num=1)

        # Get current state (lazy init)
        emma_state = manager.get_current_attributes("emma")

        # Update when story mentions change
        manager.update_attribute("emma", "clothing", "white shirt",
                                sentence_num=42, reason="removed blazer")

        # Get statistics
        stats = manager.get_statistics()
    """

    def __init__(self, chapter_num: int):
        """
        Initialize attribute manager for a chapter.

        Args:
            chapter_num: Chapter number being processed
        """
        self.chapter_num = chapter_num
        self.character_states: Dict[str, CharacterAttributeState] = {}
        self.current_scene_num: int = 1

    def initialize_character(self, character_name: str) -> Optional[CharacterAttributeState]:
        """
        Initialize character state from canonical attributes.

        Args:
            character_name: Character name (lowercase, e.g., "emma")

        Returns:
            CharacterAttributeState instance, or None if character not found

        Example:
            >>> state = manager.initialize_character("emma")
            >>> print(state.clothing)
            'navy blue fitted blazer, crisp white button-up shirt, black slacks'
        """
        from character_attributes import CHARACTER_CANONICAL_ATTRIBUTES

        if character_name not in CHARACTER_CANONICAL_ATTRIBUTES:
            return None

        attrs = CHARACTER_CANONICAL_ATTRIBUTES[character_name]

        state = CharacterAttributeState(
            character_name=character_name,
            hair=attrs["hair"],
            face=attrs["face"],
            clothing=attrs["clothing"],
            accessories=attrs["accessories"],
            skin=attrs["skin"],
            build=attrs["build"],
            last_updated_sentence=0,
            change_history=[]
        )

        self.character_states[character_name] = state
        return state

    def get_current_attributes(self, character_name: str) -> Optional[CharacterAttributeState]:
        """
        Get current attribute state for a character (lazy initialization).

        If character hasn't been seen yet in this chapter, initializes from
        canonical attributes. Otherwise returns existing state.

        Args:
            character_name: Character name (lowercase, e.g., "emma")

        Returns:
            CharacterAttributeState instance, or None if character not defined

        Example:
            >>> state = manager.get_current_attributes("emma")
            >>> prompt = state.to_prompt_string()
        """
        # Return existing state if already initialized
        if character_name in self.character_states:
            return self.character_states[character_name]

        # Lazy initialization
        return self.initialize_character(character_name)

    def update_attribute(self, character_name: str, attribute_type: str,
                        new_value: str, sentence_num: int, reason: str) -> bool:
        """
        Update a character's attribute when story explicitly mentions change.

        Args:
            character_name: Character name (lowercase, e.g., "emma")
            attribute_type: Attribute to update ("hair", "clothing", "accessories")
            new_value: New attribute value
            sentence_num: Sentence number where change occurred
            reason: Story text that triggered change (e.g., "removed her blazer")

        Returns:
            True if update succeeded, False otherwise

        Example:
            >>> manager.update_attribute("emma", "clothing",
            ...                         "white button-up shirt, black slacks",
            ...                         sentence_num=42, reason="removed blazer")
            True
        """
        # Get or initialize character state
        state = self.get_current_attributes(character_name)
        if not state:
            print(f"Warning: Unknown character '{character_name}'")
            return False

        # Delegate to state object
        return state.update_attribute(attribute_type, new_value, sentence_num, reason)

    def reset_for_new_scene(self, scene_num: int):
        """
        Called at scene boundaries ('* * *') within a chapter.

        NOTE: Attributes do NOT reset at scene boundaries. They persist
        across scenes within the same chapter. This method is provided
        for tracking purposes only.

        Args:
            scene_num: New scene number
        """
        self.current_scene_num = scene_num
        # Attributes persist - no state changes

    def reset_for_new_chapter(self, chapter_num: int):
        """
        Reset all character states to canonical attributes for a new chapter.

        Args:
            chapter_num: New chapter number

        Example:
            >>> manager.reset_for_new_chapter(chapter_num=2)
            # All character attributes reset to canonical
        """
        self.chapter_num = chapter_num
        self.current_scene_num = 1
        self.character_states.clear()
        # States will be lazily re-initialized on first access

    def get_statistics(self) -> dict:
        """
        Get attribute change statistics for logging and debugging.

        Returns:
            Dictionary with statistics including:
            - total_changes: Total attribute changes across all characters
            - characters_tracked: Number of characters with state
            - changes_by_character: Per-character change counts
            - changes_by_type: Per-attribute-type change counts

        Example:
            >>> stats = manager.get_statistics()
            >>> print(f"Total changes: {stats['total_changes']}")
            Total changes: 3
        """
        total_changes = sum(state.get_change_count() for state in self.character_states.values())

        changes_by_character = {
            char: state.get_change_count()
            for char, state in self.character_states.items()
        }

        # Count changes by attribute type
        changes_by_type = {"hair": 0, "clothing": 0, "accessories": 0}
        for state in self.character_states.values():
            for change in state.change_history:
                if change.attribute_type in changes_by_type:
                    changes_by_type[change.attribute_type] += 1

        return {
            "chapter_num": self.chapter_num,
            "total_changes": total_changes,
            "characters_tracked": len(self.character_states),
            "changes_by_character": changes_by_character,
            "changes_by_type": changes_by_type,
            "character_details": {
                char: state.to_dict()
                for char, state in self.character_states.items()
            }
        }

    def get_all_characters(self) -> List[str]:
        """
        Get list of all characters currently tracked by this manager.

        Returns:
            List of character names (lowercase)
        """
        return list(self.character_states.keys())

    def export_state(self) -> str:
        """
        Export full manager state as JSON for debugging/logging.

        Returns:
            JSON string containing all character states and statistics
        """
        stats = self.get_statistics()
        return json.dumps(stats, indent=2)
