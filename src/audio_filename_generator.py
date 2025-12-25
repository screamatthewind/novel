"""
Audio filename generator for scene audio files.
Matches the image naming convention using keyword extraction.
"""

from prompt_generator import extract_key_words


def generate_audio_filename(
    chapter_num: int,
    scene_num: int,
    scene_content: str,
    ext: str = "wav",
    sentence_num: int = None
) -> str:
    """
    Generate descriptive filename for scene audio.

    Matches image filename pattern for consistency.

    Args:
        chapter_num: Chapter number
        scene_num: Scene number within chapter
        scene_content: Scene text content
        ext: File extension (default: wav)
        sentence_num: Optional sentence number within scene

    Returns:
        Filename like 'chapter_01_scene_02_sent_03_emma_factory_reading.wav'
        or 'chapter_01_scene_02_emma_factory_reading.wav' if sentence_num not provided
    """
    # Extract key words using same function as image generator
    key_words = extract_key_words(scene_content)

    # Format with zero-padded numbers
    if sentence_num is not None:
        filename = f"chapter_{chapter_num:02d}_scene_{scene_num:02d}_sent_{sentence_num:03d}_{key_words}.{ext}"
    else:
        filename = f"chapter_{chapter_num:02d}_scene_{scene_num:02d}_{key_words}.{ext}"

    return filename


if __name__ == "__main__":
    # Test filename generation
    print("Audio Filename Generator Test")
    print("=" * 70)

    test_cases = [
        {
            "chapter": 1,
            "scene": 1,
            "content": """
                Emma checked the line supervisor's tablet. Production was ahead of schedule.
                "Looking good, Ramirez," she said. The factory floor hummed with machines.
            """
        },
        {
            "chapter": 1,
            "scene": 2,
            "content": """
                Emma sat at the kitchen table, staring at her phone. The email from HR
                had been clear. She felt shocked, frozen. The house was quiet.
            """
        },
        {
            "chapter": 2,
            "scene": 1,
            "content": """
                Maxim Orlov walked through the Moscow factory. Elena stood by the assembly
                line, watching the robots work. The evening light cast long shadows.
            """
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  Chapter {test['chapter']}, Scene {test['scene']}")
        print(f"  Content preview: {test['content'].strip()[:60]}...")

        filename = generate_audio_filename(
            test['chapter'],
            test['scene'],
            test['content']
        )

        print(f"  Generated filename: {filename}")

    print("\n" + "=" * 70)
    print("Test complete!")
