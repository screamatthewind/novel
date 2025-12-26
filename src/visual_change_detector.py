"""
Visual change detection system for smart image generation.

Detects when visual context changes significantly enough to warrant generating
a new image, versus reusing the current image.
"""

from typing import Tuple
from scene_parser import Sentence
from prompt_generator import (
    extract_characters,
    extract_setting,
    extract_action,
    extract_time_of_day,
    ACTION_KEYWORDS
)


class VisualChangeDetector:
    """
    Detects when new image is needed versus reusing previous image.

    Tracks visual state (character, setting, action, time) across sentences
    and determines when changes are significant enough to generate new image.
    """

    def __init__(self):
        """Initialize detector with empty state."""
        self.current_state = {
            'character': None,
            'setting': None,
            'action': None,
            'time_of_day': None
        }
        self.sentence_count = 0

    def analyze_sentence(self, sentence: Sentence) -> dict:
        """
        Extract visual elements from sentence.

        Args:
            sentence: Sentence object containing content and scene context

        Returns:
            Dictionary with visual state: character, setting, action, time_of_day
        """
        # Extract visual elements
        characters = extract_characters(sentence.content)

        # Use scene_context for setting and time to ensure consistency within scene
        setting = extract_setting(sentence.scene_context)
        time_of_day = extract_time_of_day(sentence.scene_context)

        # Use sentence content for action (specific to this moment)
        action = extract_action(sentence.content)

        return {
            'character': characters[0] if characters else None,
            'setting': setting,
            'action': action,
            'time_of_day': time_of_day
        }

    def needs_new_image(self, new_state: dict) -> Tuple[bool, str]:
        """
        Determine if new image needed based on state change.

        Args:
            new_state: Visual state dictionary from analyze_sentence()

        Returns:
            Tuple of (needs_new_image: bool, reason: str)
        """
        # First sentence always needs image
        if self.current_state['character'] is None and self.sentence_count == 0:
            return (True, "first_sentence")

        # Track changes
        changes = []

        # Character change (high priority)
        if new_state['character'] != self.current_state['character']:
            # Allow None -> character or character -> None transitions
            if new_state['character'] or self.current_state['character']:
                changes.append("character")

        # Setting change (high priority)
        if new_state['setting'] != self.current_state['setting']:
            changes.append("setting")

        # Action change (medium priority - only if significant)
        if new_state['action'] and self.current_state['action']:
            if self._is_significant_action_change(
                self.current_state['action'],
                new_state['action']
            ):
                changes.append("action")
        elif new_state['action'] and not self.current_state['action']:
            # New action when there was none
            changes.append("action")

        # Time change (lower priority, but still important for lighting)
        if new_state['time_of_day'] != self.current_state['time_of_day']:
            changes.append("time")

        # Decision logic:
        # - Character change OR setting change: always generate new image
        # - 2+ changes of any type: generate new image
        # - Time change alone: generate new image (lighting is important)
        # - Action-only change: Don't generate (too minor)
        if 'character' in changes or 'setting' in changes:
            return (True, f"changed: {', '.join(changes)}")
        elif len(changes) >= 2:
            return (True, f"changed: {', '.join(changes)}")
        elif 'time' in changes and len(changes) == 1:
            return (True, "changed: time")

        return (False, "no_significant_change")

    def _is_significant_action_change(self, old_action: str, new_action: str) -> bool:
        """
        Determine if action change is significant enough for new image.

        Args:
            old_action: Previous action description
            new_action: New action description

        Returns:
            True if action change is significant
        """
        # Extract action categories from descriptive strings
        # (e.g., "reading document or screen" -> "reading")
        old_category = self._get_action_category(old_action)
        new_category = self._get_action_category(new_action)

        # Same category = not significant
        if old_category == new_category:
            return False

        # Define action change significance matrix
        # Some transitions are more visually significant than others

        # Static to dynamic (or vice versa) is significant
        static_actions = {'reading', 'watching', 'working'}
        dynamic_actions = {'walking', 'talking'}

        old_is_static = old_category in static_actions
        new_is_static = new_category in static_actions

        # Static <-> Dynamic transition is significant
        if old_is_static != new_is_static:
            return True

        # Within same type (static or dynamic), not significant
        return False

    def _get_action_category(self, action_description: str) -> str:
        """
        Extract action category from action description.

        Args:
            action_description: Full action description (e.g., "reading document or screen")

        Returns:
            Action category (e.g., "reading")
        """
        # Check which category this description belongs to
        for category in ACTION_KEYWORDS.keys():
            if category in action_description.lower():
                return category

        return "unknown"

    def update_state(self, new_state: dict):
        """
        Update current state after generating new image.

        Args:
            new_state: New visual state to store
        """
        self.current_state = new_state.copy()
        self.sentence_count += 1

    def reset(self):
        """
        Reset detector state (call at start of new scene).
        """
        self.current_state = {
            'character': None,
            'setting': None,
            'action': None,
            'time_of_day': None
        }
        self.sentence_count = 0


def main():
    """Test visual change detection logic."""
    from scene_parser import Sentence

    print("Visual Change Detector Test")
    print("=" * 80)

    # Create test sentences
    test_sentences = [
        Sentence(
            chapter_num=1,
            scene_num=1,
            sentence_num=1,
            content="Emma stared at her tablet in the factory.",
            word_count=8,
            scene_context="Emma stared at her tablet in the factory. The machines hummed around her. The afternoon sun streamed through windows."
        ),
        Sentence(
            chapter_num=1,
            scene_num=1,
            sentence_num=2,
            content="The machines hummed around her.",
            word_count=5,
            scene_context="Emma stared at her tablet in the factory. The machines hummed around her. The afternoon sun streamed through windows."
        ),
        Sentence(
            chapter_num=1,
            scene_num=1,
            sentence_num=3,
            content="She walked to the window.",
            word_count=5,
            scene_context="Emma stared at her tablet in the factory. The machines hummed around her. The afternoon sun streamed through windows."
        ),
        Sentence(
            chapter_num=1,
            scene_num=1,
            sentence_num=4,
            content="Tyler entered the factory floor.",
            word_count=5,
            scene_context="Tyler entered the factory floor. He looked around nervously."
        ),
    ]

    detector = VisualChangeDetector()

    for i, sentence in enumerate(test_sentences):
        print(f"\nSentence {i+1}: \"{sentence.content}\"")

        # Analyze
        state = detector.analyze_sentence(sentence)
        print(f"  State: character={state['character']}, setting={state['setting']}, "
              f"action={state['action']}, time={state['time_of_day']}")

        # Check if new image needed
        needs_new, reason = detector.needs_new_image(state)
        print(f"  New image needed: {needs_new} ({reason})")

        # Update state if new image generated
        if needs_new:
            detector.update_state(state)
            print("  → Image generated, state updated")
        else:
            print("  → Reusing previous image")

    print("\n" + "=" * 80)
    print("Test complete!")


if __name__ == "__main__":
    main()
