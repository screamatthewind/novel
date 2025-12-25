"""
Scene parser for extracting scenes from chapter markdown files.
Splits chapters on '* * *' separators and excludes CRAFT NOTES sections.
"""

import re
import glob
from dataclasses import dataclass
from typing import List
from config import CHAPTER_DIR, CHAPTER_NAMES


@dataclass
class Scene:
    """Represents a single scene extracted from a chapter."""
    chapter_num: int
    chapter_title: str
    scene_num: int
    content: str
    word_count: int


@dataclass
class Sentence:
    """Represents a single sentence from a scene."""
    chapter_num: int
    scene_num: int
    sentence_num: int
    content: str
    word_count: int


def extract_chapter_number(filename: str) -> int:
    """
    Extract chapter number from filename like 'The_Obsolescence_Chapter_01.md'.

    Args:
        filename: Full path or filename of the chapter

    Returns:
        Chapter number as integer
    """
    # Extract just the filename from the path
    basename = filename.split('\\')[-1].split('/')[-1]

    # Match pattern: The_Obsolescence_Chapter_[Number].md
    match = re.search(r'Chapter_(\d+)\.md', basename)
    if match:
        chapter_num_str = match.group(1)
        if chapter_num_str in CHAPTER_NAMES:
            return CHAPTER_NAMES[chapter_num_str]

    raise ValueError(f"Could not extract chapter number from filename: {filename}")


def remove_craft_notes(content: str) -> str:
    """
    Remove CRAFT NOTES section from chapter content.
    Finds '^CRAFT NOTES' and truncates everything after.

    Args:
        content: Full chapter markdown content

    Returns:
        Content with CRAFT NOTES removed
    """
    # Find CRAFT NOTES section (case insensitive, at start of line)
    match = re.search(r'^CRAFT NOTES', content, re.MULTILINE | re.IGNORECASE)
    if match:
        return content[:match.start()].strip()
    return content


def split_scenes(content: str) -> List[str]:
    """
    Split chapter content into scenes using '* * *' separator.

    Args:
        content: Chapter content (with CRAFT NOTES already removed)

    Returns:
        List of scene content strings
    """
    # Pattern matches: '* * *' with optional spaces around asterisks
    # Must be on its own line
    separator_pattern = r'^\*\s+\*\s+\*\s*$'

    # Split on the separator
    scenes = re.split(separator_pattern, content, flags=re.MULTILINE)

    # Clean up: strip whitespace and filter out empty scenes
    scenes = [scene.strip() for scene in scenes if scene.strip()]

    return scenes


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences at sentence boundaries.

    Handles standard punctuation (.!?) and preserves dialogue formatting.

    Args:
        text: Text to split into sentences

    Returns:
        List of sentences
    """
    # Replace common abbreviations to avoid false splits
    text = text.replace('Mr.', 'Mr~')
    text = text.replace('Mrs.', 'Mrs~')
    text = text.replace('Ms.', 'Ms~')
    text = text.replace('Dr.', 'Dr~')
    text = text.replace('vs.', 'vs~')
    text = text.replace('etc.', 'etc~')
    text = text.replace('i.e.', 'i~e~')
    text = text.replace('e.g.', 'e~g~')

    # Split on sentence boundaries (. ! ?) followed by space and capital letter
    # This regex captures the punctuation with the sentence
    sentence_pattern = r'([.!?]+\s+)'
    parts = re.split(sentence_pattern, text)

    # Reconstruct sentences by pairing text with punctuation
    sentences = []
    current_sentence = ""

    for part in parts:
        current_sentence += part
        # If this part ends with sentence-ending punctuation followed by whitespace
        if re.search(r'[.!?]+\s+$', part):
            # Restore abbreviations
            sentence = current_sentence.strip()
            sentence = sentence.replace('~', '.')
            if sentence:
                sentences.append(sentence)
            current_sentence = ""

    # Add any remaining text as the last sentence
    if current_sentence.strip():
        sentence = current_sentence.strip()
        sentence = sentence.replace('~', '.')
        sentences.append(sentence)

    return [s for s in sentences if s.strip()]


def parse_scene_sentences(scene: Scene) -> List[Sentence]:
    """
    Parse a scene into individual sentences.

    Args:
        scene: Scene object to parse

    Returns:
        List of Sentence objects
    """
    sentence_texts = split_into_sentences(scene.content)

    sentences = []
    for i, sentence_text in enumerate(sentence_texts, start=1):
        word_count = len(sentence_text.split())
        sentence = Sentence(
            chapter_num=scene.chapter_num,
            scene_num=scene.scene_num,
            sentence_num=i,
            content=sentence_text,
            word_count=word_count
        )
        sentences.append(sentence)

    return sentences


def parse_chapter(filepath: str) -> List[Scene]:
    """
    Parse a single chapter file and extract all scenes.

    Args:
        filepath: Path to the chapter markdown file

    Returns:
        List of Scene objects
    """
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract chapter number and title
    chapter_num = extract_chapter_number(filepath)
    chapter_title = f"Chapter {chapter_num}"

    # Remove CRAFT NOTES section
    content = remove_craft_notes(content)

    # Split into scenes
    scene_texts = split_scenes(content)

    # Create Scene objects
    scenes = []
    for i, scene_text in enumerate(scene_texts, start=1):
        word_count = len(scene_text.split())
        scene = Scene(
            chapter_num=chapter_num,
            chapter_title=chapter_title,
            scene_num=i,
            content=scene_text,
            word_count=word_count
        )
        scenes.append(scene)

    return scenes


def parse_all_chapters(chapter_numbers: List[int] = None) -> List[Scene]:
    """
    Parse all chapter files and return all scenes.

    Args:
        chapter_numbers: Optional list of specific chapter numbers to parse.
                        If None, parses all chapters.

    Returns:
        List of all Scene objects from all chapters
    """
    # Find all chapter files
    pattern = f"{CHAPTER_DIR}/The_Obsolescence_Chapter_*.md"
    chapter_files = glob.glob(pattern)

    # Filter by requested chapters if specified
    if chapter_numbers:
        filtered_files = []
        for filepath in chapter_files:
            try:
                chapter_num = extract_chapter_number(filepath)
                if chapter_num in chapter_numbers:
                    filtered_files.append(filepath)
            except ValueError:
                continue
        chapter_files = filtered_files

    # Sort by chapter number
    chapter_files.sort(key=lambda f: extract_chapter_number(f))

    # Parse all chapters
    all_scenes = []
    for filepath in chapter_files:
        scenes = parse_chapter(filepath)
        all_scenes.extend(scenes)

    return all_scenes


def main():
    """Test the scene parser on all chapters."""
    scenes = parse_all_chapters()

    print(f"Total scenes extracted: {len(scenes)}\n")

    # Group by chapter
    by_chapter = {}
    for scene in scenes:
        if scene.chapter_num not in by_chapter:
            by_chapter[scene.chapter_num] = []
        by_chapter[scene.chapter_num].append(scene)

    # Print summary
    for chapter_num in sorted(by_chapter.keys()):
        chapter_scenes = by_chapter[chapter_num]
        total_words = sum(s.word_count for s in chapter_scenes)
        print(f"Chapter {chapter_num}: {len(chapter_scenes)} scenes ({total_words:,} words)")
        for scene in chapter_scenes:
            preview = scene.content[:80].replace('\n', ' ')
            print(f"  Scene {scene.scene_num}: {scene.word_count} words - {preview}...")
        print()


if __name__ == "__main__":
    main()
