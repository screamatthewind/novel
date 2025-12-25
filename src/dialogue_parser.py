"""
Dialogue parser for extracting speech segments from novel text.
Identifies speakers, separates dialogue from narration, and preprocesses text for TTS.
"""

from dataclasses import dataclass
from typing import List
import re


@dataclass
class DialogueSegment:
    """A segment of text with speaker attribution."""
    text: str
    speaker: str  # Character name or "narrator"
    segment_type: str  # "dialogue" or "narration"


def clean_markdown(text: str) -> str:
    """
    Clean markdown formatting and prepare text for TTS.

    Args:
        text: Raw text with markdown formatting

    Returns:
        Cleaned text suitable for TTS
    """
    # Remove scene separators
    text = re.sub(r'\n\s*\* \* \*\s*\n', '\n\n', text)

    # Remove italic markers (preserve content)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # Replace em-dashes with comma-space for natural pauses
    text = text.replace('—', ', ')

    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
    text = re.sub(r' +', ' ', text)  # Single spaces only

    return text.strip()


def extract_dialogue_with_speaker(text: str) -> List[DialogueSegment]:
    """
    Parse text into dialogue and narration segments with speaker attribution.

    Handles patterns like:
    - "Text," Emma said.
    - Emma said: "Text"
    - "Text" (attributed to previous speaker or context)

    Args:
        text: Novel scene text

    Returns:
        List of DialogueSegment objects
    """
    segments = []

    # Clean the text first
    cleaned_text = clean_markdown(text)

    # Split into paragraphs
    paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]

    # Known character names from the novel
    character_names = [
        'emma', 'maxim', 'amara', 'tyler', 'mark', 'elena',
        'diane', 'ramirez', 'wei'
    ]

    # Track the last speaker for context
    last_speaker = 'narrator'

    for para in paragraphs:
        # Pattern 1: "Dialogue" Speaker said/asked/etc.
        # e.g., "Looking good, Ramirez," she said
        # Also handles: "Dialogue," speaker said, doing something
        pattern1 = r'"([^"]+)"[,.]?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|asked|replied|shouted|whispered|muttered|continued|added|laughed|grinned)'
        match1 = re.search(pattern1, para)

        # Pattern 2: Speaker said: "Dialogue"
        # e.g., Emma said: "Don't let them hear you"
        pattern2 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|asked|replied|shouted|whispered|muttered):\s+"([^"]+)"'
        match2 = re.search(pattern2, para)

        # Pattern 3: "Dialogue" with pronoun attribution
        # e.g., "Text," she said (where "she" refers to last female speaker)
        pattern3 = r'"([^"]+)"[,.]?\s+(?:he|she)\s+(?:said|asked|replied|shouted|whispered|muttered|continued|added|laughed|grinned)'
        match3 = re.search(pattern3, para)

        # Try to find character name in paragraph (for pronoun context)
        para_lower = para.lower()
        char_in_para = None
        for char_name in character_names:
            if char_name in para_lower:
                char_in_para = char_name
                break

        if match1:
            # Extract dialogue and speaker
            dialogue = match1.group(1)
            speaker = match1.group(2).lower()

            # Validate speaker
            if speaker not in character_names:
                speaker = last_speaker

            segments.append(DialogueSegment(
                text=dialogue,
                speaker=speaker,
                segment_type="dialogue"
            ))
            last_speaker = speaker

            # Check if there's narration before the dialogue
            before_dialogue = para[:match1.start()].strip()
            if before_dialogue:
                segments.insert(-1, DialogueSegment(
                    text=before_dialogue,
                    speaker="narrator",
                    segment_type="narration"
                ))

            # Check if there's narration after the dialogue tag
            after_dialogue = para[match1.end():].strip()
            if after_dialogue:
                segments.append(DialogueSegment(
                    text=after_dialogue,
                    speaker="narrator",
                    segment_type="narration"
                ))

        elif match2:
            dialogue = match2.group(2)
            speaker = match2.group(1).lower()

            if speaker not in character_names:
                speaker = last_speaker

            # Narration before
            before_dialogue = para[:match2.start()].strip()
            if before_dialogue:
                segments.append(DialogueSegment(
                    text=before_dialogue,
                    speaker="narrator",
                    segment_type="narration"
                ))

            segments.append(DialogueSegment(
                text=dialogue,
                speaker=speaker,
                segment_type="dialogue"
            ))
            last_speaker = speaker

            # Narration after
            after_dialogue = para[match2.end():].strip()
            if after_dialogue:
                segments.append(DialogueSegment(
                    text=after_dialogue,
                    speaker="narrator",
                    segment_type="narration"
                ))

        elif match3:
            # Pronoun reference - use character in paragraph or last speaker
            dialogue = match3.group(1)

            # Use character from paragraph context if available, otherwise last_speaker
            speaker = char_in_para if char_in_para else last_speaker

            segments.append(DialogueSegment(
                text=dialogue,
                speaker=speaker,
                segment_type="dialogue"
            ))
            last_speaker = speaker

            # Narration before
            before_dialogue = para[:match3.start()].strip()
            if before_dialogue:
                segments.insert(-1, DialogueSegment(
                    text=before_dialogue,
                    speaker="narrator",
                    segment_type="narration"
                ))

            # Narration after
            after_dialogue = para[match3.end():].strip()
            if after_dialogue:
                segments.append(DialogueSegment(
                    text=after_dialogue,
                    speaker="narrator",
                    segment_type="narration"
                ))
        else:
            # Check if paragraph contains any quoted text (unattributed dialogue)
            quoted_text = re.findall(r'"([^"]+)"', para)

            if quoted_text:
                # Split paragraph by quotes
                parts = re.split(r'"[^"]+"', para)

                for i, quote in enumerate(quoted_text):
                    # Add narration before quote
                    if i < len(parts) and parts[i].strip():
                        segments.append(DialogueSegment(
                            text=parts[i].strip(),
                            speaker="narrator",
                            segment_type="narration"
                        ))

                    # Add dialogue (use last speaker or check context)
                    segments.append(DialogueSegment(
                        text=quote,
                        speaker=last_speaker,
                        segment_type="dialogue"
                    ))

                # Add final narration part
                if len(parts) > len(quoted_text) and parts[-1].strip():
                    segments.append(DialogueSegment(
                        text=parts[-1].strip(),
                        speaker="narrator",
                        segment_type="narration"
                    ))
            else:
                # Pure narration paragraph
                segments.append(DialogueSegment(
                    text=para,
                    speaker="narrator",
                    segment_type="narration"
                ))

    return segments


def chunk_text(text: str, max_chars: int = 500) -> List[str]:
    """
    Split text into chunks at sentence boundaries.

    Args:
        text: Text to chunk
        max_chars: Maximum characters per chunk

    Returns:
        List of text chunks
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current_chunk = ""

    # Split on sentence boundaries
    sentences = re.split(r'([.!?]+\s+)', text)

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""

        full_sentence = sentence + punctuation

        if len(current_chunk) + len(full_sentence) <= max_chars:
            current_chunk += full_sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = full_sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def parse_scene_text(scene_content: str) -> List[DialogueSegment]:
    """
    Main entry point: parse scene text into dialogue segments.

    Args:
        scene_content: Full scene text

    Returns:
        List of DialogueSegment objects with speaker attribution
    """
    return extract_dialogue_with_speaker(scene_content)


if __name__ == "__main__":
    # Test with sample text from Chapter One
    test_text = '''
"Looking good, Ramirez," she said, handing the tablet back. "That modification you suggested for the bracket feed—it's working."

Ramirez grinned. "Told you the machine was smarter than the manual. Just needed someone to listen."

Emma laughed. "Don't let engineering hear you say that. They hate when the floor proves them wrong."

She moved through the Hartwell Manufacturing facility with the easy confidence of someone who'd earned her place.

* * *

The email came at 4:47 PM.

Emma was at her desk, finishing production reports, thinking about whether she had time to grab dinner before Tyler's game.
'''

    print("Dialogue Parser Test")
    print("=" * 70)
    print("\nInput text:")
    print(test_text)
    print("\n" + "=" * 70)
    print("\nParsed segments:")
    print("=" * 70)

    segments = parse_scene_text(test_text)

    for i, seg in enumerate(segments, 1):
        type_label = seg.segment_type.upper()
        print(f"\n[{i}] {type_label} - Speaker: {seg.speaker}")
        print(f"    Text: {seg.text[:100]}{'...' if len(seg.text) > 100 else ''}")

    print(f"\n" + "=" * 70)
    print(f"Total segments: {len(segments)}")
    print(f"Dialogue segments: {sum(1 for s in segments if s.segment_type == 'dialogue')}")
    print(f"Narration segments: {sum(1 for s in segments if s.segment_type == 'narration')}")

    # Test chunking
    print("\n" + "=" * 70)
    print("Text Chunking Test")
    print("=" * 70)

    long_text = "This is a sentence. This is another sentence. And here's a third one! What about a question? More text here. Even more text to make it longer. We need to test chunking. This should split properly. At sentence boundaries only. Never in the middle of a sentence."
    chunks = chunk_text(long_text, max_chars=100)

    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i} ({len(chunk)} chars): {chunk}")
