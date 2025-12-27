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

    def analyze_with_storyboard(
        self,
        sentence: Sentence,
        storyboard
    ) -> Tuple[bool, str]:
        """
        Enhanced image reuse decision based on storyboard analysis.

        Decision rules (in priority order):
        1. First sentence in scene → New image
        2. Special techniques (flashback, montage) → New image
        3. Character entry/exit → New image
        4. Camera angle change → New image
        5. Camera framing change → New image
        6. Expression/mood dramatically different → New image
        7. Spatial position change → New image
        8. Same framing, characters, mood → Reuse

        Args:
            sentence: Sentence object
            storyboard: StoryboardAnalysis object with detailed visual info

        Returns:
            Tuple of (needs_new_image: bool, reason: str)
        """
        # First sentence always needs image
        if self.sentence_count == 0:
            self.sentence_count += 1
            return (True, "first_sentence")

        # Track what changed
        changes = []

        # 1. Special techniques (highest priority)
        if storyboard.special_techniques:
            return (True, f"special_technique: {', '.join(storyboard.special_techniques)}")

        # 2. Character presence change
        prev_chars = set(self.current_state.get('characters', []))
        new_chars = set(storyboard.characters_present)

        if prev_chars != new_chars:
            # Character entered or exited
            if new_chars - prev_chars:
                changes.append(f"character_entry: {', '.join(new_chars - prev_chars)}")
            if prev_chars - new_chars:
                changes.append(f"character_exit: {', '.join(prev_chars - new_chars)}")

        # 3. Camera angle change (significant visual shift)
        if self.current_state.get('camera_angle') != storyboard.camera_angle:
            if self.current_state.get('camera_angle'):  # Not first image
                changes.append(f"camera_angle: {self.current_state.get('camera_angle')} → {storyboard.camera_angle}")

        # 4. Camera framing change (significant visual shift)
        if self.current_state.get('camera_framing') != storyboard.camera_framing:
            if self.current_state.get('camera_framing'):  # Not first image
                changes.append(f"camera_framing: {self.current_state.get('camera_framing')} → {storyboard.camera_framing}")

        # 5. Spatial context change (location change)
        if self.current_state.get('spatial_context') != storyboard.spatial_context:
            if self.current_state.get('spatial_context'):  # Not first image
                changes.append(f"location: {storyboard.spatial_context}")

        # 6. Expression/mood change (check if dramatic)
        if storyboard.characters_present:
            primary_char = storyboard.characters_present[0]
            old_expression = self.current_state.get('expressions', {}).get(primary_char)
            new_expression = storyboard.expressions.get(primary_char)

            if old_expression and new_expression:
                # Check if expressions are dramatically different
                if self._is_dramatic_expression_change(old_expression, new_expression):
                    changes.append(f"expression: {old_expression} → {new_expression}")

        # 7. Mood change (atmospheric)
        if self.current_state.get('mood') != storyboard.mood:
            if self.current_state.get('mood'):  # Not first image
                # Only count dramatic mood shifts
                if self._is_dramatic_mood_change(self.current_state.get('mood'), storyboard.mood):
                    changes.append(f"mood: {storyboard.mood}")

        # Decision logic
        if changes:
            # Any significant change warrants new image
            self.sentence_count += 1
            return (True, ", ".join(changes))

        # No significant changes - reuse image
        return (False, "no_significant_change")

    def update_storyboard_state(self, storyboard):
        """
        Update state from storyboard analysis.

        Args:
            storyboard: StoryboardAnalysis object
        """
        self.current_state = {
            'characters': storyboard.characters_present.copy(),
            'camera_angle': storyboard.camera_angle,
            'camera_framing': storyboard.camera_framing,
            'spatial_context': storyboard.spatial_context,
            'expressions': storyboard.expressions.copy() if storyboard.expressions else {},
            'mood': storyboard.mood,
        }

    def _is_dramatic_expression_change(self, old_expr: str, new_expr: str) -> bool:
        """
        Check if expression change is dramatic enough for new image.

        Args:
            old_expr: Previous expression
            new_expr: New expression

        Returns:
            True if change is dramatic
        """
        # Define expression categories
        positive_expressions = ['happy', 'smiling', 'pleased', 'satisfied', 'content', 'relieved']
        negative_expressions = ['sad', 'angry', 'frustrated', 'worried', 'anxious', 'shocked', 'horrified', 'disgusted']
        neutral_expressions = ['neutral', 'calm', 'thoughtful', 'focused', 'concentrated']

        def get_expression_category(expr):
            expr_lower = expr.lower()
            if any(word in expr_lower for word in positive_expressions):
                return 'positive'
            elif any(word in expr_lower for word in negative_expressions):
                return 'negative'
            else:
                return 'neutral'

        old_category = get_expression_category(old_expr)
        new_category = get_expression_category(new_expr)

        # Category change is dramatic
        return old_category != new_category

    def _is_dramatic_mood_change(self, old_mood: str, new_mood: str) -> bool:
        """
        Check if mood change is dramatic enough for new image.

        Args:
            old_mood: Previous mood
            new_mood: New mood

        Returns:
            True if change is dramatic
        """
        # Define mood categories
        tense_moods = ['tense', 'anxious', 'urgent', 'dramatic', 'suspenseful', 'threatening']
        calm_moods = ['calm', 'peaceful', 'serene', 'gentle', 'soft', 'quiet']
        dark_moods = ['dark', 'ominous', 'foreboding', 'grim', 'bleak']
        hopeful_moods = ['hopeful', 'optimistic', 'bright', 'warm', 'uplifting']

        def get_mood_category(mood):
            mood_lower = mood.lower()
            if any(word in mood_lower for word in tense_moods):
                return 'tense'
            elif any(word in mood_lower for word in calm_moods):
                return 'calm'
            elif any(word in mood_lower for word in dark_moods):
                return 'dark'
            elif any(word in mood_lower for word in hopeful_moods):
                return 'hopeful'
            else:
                return 'neutral'

        old_category = get_mood_category(old_mood)
        new_category = get_mood_category(new_mood)

        # Category change is dramatic
        return old_category != new_category


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
