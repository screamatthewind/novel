"""
Image mapping metadata system for tracking audio-to-image relationships.

Maintains metadata files that map audio sentences to their corresponding images,
enabling video generation when multiple sentences share the same image.
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path


class ImageMappingMetadata:
    """
    Tracks which audio files map to which image files.

    Generates metadata files in audio_cache/ directory that the video
    generator can use to pair audio and images correctly when images
    are reused across multiple sentences.
    """

    def __init__(self, chapter_num: int):
        """
        Initialize metadata tracker for a chapter.

        Args:
            chapter_num: Chapter number being processed
        """
        self.chapter_num = chapter_num
        self.mappings = []

    def add_mapping(
        self,
        audio_file: str,
        image_file: str,
        sentence_num: int,
        scene_num: int,
        reason: str
    ):
        """
        Add a sentence-to-image mapping.

        Args:
            audio_file: Audio filename (e.g., "chapter_01_scene_01_sent_001_emma.wav")
            image_file: Image filename (e.g., "chapter_01_scene_01_sent_001_emma.png")
            sentence_num: Sentence number within scene
            scene_num: Scene number within chapter
            reason: Reason for decision (e.g., "first_sentence", "changed: character", "no_significant_change")
        """
        self.mappings.append({
            'audio_file': audio_file,
            'image_file': image_file,
            'sentence_num': sentence_num,
            'scene_num': scene_num,
            'reason': reason
        })

    def get_mappings(self) -> List[Dict]:
        """
        Get all mappings recorded so far.

        Returns:
            List of mapping dictionaries
        """
        return self.mappings.copy()

    def save(self, output_dir: str):
        """
        Save metadata to JSON file in audio_cache directory.

        Args:
            output_dir: Directory to save metadata (typically audio_cache/)
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        filename = f"chapter_{self.chapter_num:02d}_image_mapping.json"
        filepath = os.path.join(output_dir, filename)

        # Build metadata structure
        metadata = {
            'chapter': self.chapter_num,
            'generated_at': datetime.now().isoformat(),
            'total_sentences': len(self.mappings),
            'unique_images': len(set(m['image_file'] for m in self.mappings)),
            'mappings': self.mappings
        }

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return filepath

    def load(self, input_dir: str) -> bool:
        """
        Load existing metadata from JSON file.

        Args:
            input_dir: Directory to load metadata from (typically audio_cache/)

        Returns:
            True if metadata loaded successfully, False otherwise
        """
        filename = f"chapter_{self.chapter_num:02d}_image_mapping.json"
        filepath = os.path.join(input_dir, filename)

        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.chapter_num = data['chapter']
            self.mappings = data['mappings']
            return True

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  WARNING: Error loading metadata from {filepath}: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        Get statistics about image reuse.

        Returns:
            Dictionary with statistics:
            - total_sentences: Total number of sentences
            - unique_images: Number of unique images generated
            - reuse_percentage: Percentage of sentences that reused images
            - reason_counts: Breakdown of decision reasons
        """
        total_sentences = len(self.mappings)
        unique_images = len(set(m['image_file'] for m in self.mappings))

        # Calculate reuse percentage
        reused_count = sum(1 for m in self.mappings if 'no_significant_change' in m['reason'])
        reuse_percentage = (reused_count / total_sentences * 100) if total_sentences > 0 else 0

        # Count reasons
        reason_counts = {}
        for mapping in self.mappings:
            reason = mapping['reason']
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        return {
            'total_sentences': total_sentences,
            'unique_images': unique_images,
            'reused_sentences': reused_count,
            'reuse_percentage': reuse_percentage,
            'images_saved': total_sentences - unique_images,
            'reduction_percentage': ((total_sentences - unique_images) / total_sentences * 100) if total_sentences > 0 else 0,
            'reason_counts': reason_counts
        }

    def print_statistics(self):
        """Print human-readable statistics about image reuse."""
        stats = self.get_statistics()

        print(f"\nImage Generation Statistics for Chapter {self.chapter_num}:")
        print("=" * 80)
        print(f"Total sentences:      {stats['total_sentences']}")
        print(f"Unique images:        {stats['unique_images']}")
        print(f"Reused sentences:     {stats['reused_sentences']}")
        print(f"Images saved:         {stats['images_saved']}")
        print(f"Reduction:            {stats['reduction_percentage']:.1f}%")
        print()
        print("Reasons breakdown:")
        for reason, count in sorted(stats['reason_counts'].items(), key=lambda x: -x[1]):
            percentage = (count / stats['total_sentences'] * 100)
            print(f"  {reason:30s}: {count:3d} ({percentage:5.1f}%)")
        print("=" * 80)


def load_image_mapping(chapter_num: int, input_dir: str) -> ImageMappingMetadata:
    """
    Load image mapping metadata for a chapter.

    Args:
        chapter_num: Chapter number to load
        input_dir: Directory containing metadata files (typically audio_cache/)

    Returns:
        ImageMappingMetadata object (empty if file doesn't exist)
    """
    metadata = ImageMappingMetadata(chapter_num)
    metadata.load(input_dir)
    return metadata


def main():
    """Test metadata system."""
    print("Image Mapping Metadata Test")
    print("=" * 80)

    # Create test metadata
    metadata = ImageMappingMetadata(chapter_num=1)

    # Add some test mappings
    metadata.add_mapping(
        audio_file="chapter_01_scene_01_sent_001_emma_factory.wav",
        image_file="chapter_01_scene_01_sent_001_emma_factory.png",
        sentence_num=1,
        scene_num=1,
        reason="first_sentence"
    )

    metadata.add_mapping(
        audio_file="chapter_01_scene_01_sent_002_factory.wav",
        image_file="chapter_01_scene_01_sent_001_emma_factory.png",
        sentence_num=2,
        scene_num=1,
        reason="no_significant_change"
    )

    metadata.add_mapping(
        audio_file="chapter_01_scene_01_sent_003_emma_reading.wav",
        image_file="chapter_01_scene_01_sent_003_emma_reading.png",
        sentence_num=3,
        scene_num=1,
        reason="changed: action"
    )

    metadata.add_mapping(
        audio_file="chapter_01_scene_01_sent_004_factory.wav",
        image_file="chapter_01_scene_01_sent_003_emma_reading.png",
        sentence_num=4,
        scene_num=1,
        reason="no_significant_change"
    )

    # Print statistics
    metadata.print_statistics()

    # Save to temp directory
    import tempfile
    temp_dir = tempfile.mkdtemp()

    print(f"\nSaving metadata to: {temp_dir}")
    filepath = metadata.save(temp_dir)
    print(f"Saved to: {filepath}")

    # Load it back
    print("\nLoading metadata back...")
    loaded = ImageMappingMetadata(chapter_num=1)
    success = loaded.load(temp_dir)

    if success:
        print("✓ Metadata loaded successfully")
        loaded.print_statistics()
    else:
        print("✗ Failed to load metadata")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

    print("\n" + "=" * 80)
    print("Test complete!")


if __name__ == "__main__":
    main()
