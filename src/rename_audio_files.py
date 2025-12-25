#!/usr/bin/env python3
"""
Rename audio files to match image filenames for consistency.

This script fixes the filename inconsistency issue where audio files
were generated with sentence-level location extraction (wrong) instead
of scene-level location extraction (correct, matching images).

Usage:
    # Dry run - show what would be renamed without making changes
    python rename_audio_files.py --chapter 1 --dry-run

    # Actually rename files for Chapter 1
    python rename_audio_files.py --chapter 1

    # Rename files for multiple chapters
    python rename_audio_files.py --chapters 1 2 3

    # Rename all chapters (use with caution!)
    python rename_audio_files.py --all
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from config import AUDIO_DIR, AUDIO_CACHE_DIR, OUTPUT_DIR


class AudioRenamer:
    """Rename audio files to match image filenames."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.audio_dir = Path(AUDIO_DIR)
        self.cache_dir = Path(AUDIO_CACHE_DIR)
        self.images_dir = Path(OUTPUT_DIR)

        self.stats = {
            'total_images': 0,
            'matched_audio': 0,
            'renamed': 0,
            'missing_audio': 0,
            'missing_images': 0,
            'errors': 0
        }

    def find_image_audio_pairs(self, chapter_num: int) -> List[Tuple[Path, Path, Path]]:
        """
        Find all image files and their corresponding (mismatched) audio files.

        Args:
            chapter_num: Chapter number

        Returns:
            List of (image_path, old_audio_path, new_audio_path) tuples
            where new_audio_path is what the audio file SHOULD be named
        """
        chapter_str = f"chapter_{chapter_num:02d}"
        pairs = []

        # Find all image files for this chapter
        image_files = sorted(self.images_dir.glob(f"{chapter_str}_scene_*_sent_*.png"))
        self.stats['total_images'] += len(image_files)

        for image_file in image_files:
            # Expected audio filename (matching image)
            expected_audio_name = image_file.name.replace('.png', '.wav')
            expected_audio_path = self.audio_dir / expected_audio_name

            # Check if audio already has correct name
            if expected_audio_path.exists():
                self.stats['matched_audio'] += 1
                print(f"[OK] Already matched: {expected_audio_name}")
                continue

            # Need to find the actual audio file
            # Extract chapter_XX_scene_YY_sent_ZZZ prefix
            # Example: chapter_01_scene_01_sent_001_emma_factory.png
            #          -> chapter_01_scene_01_sent_001
            parts = image_file.stem.split('_')
            if len(parts) >= 6:  # chapter_XX_scene_YY_sent_ZZZ_...
                prefix = '_'.join(parts[:6])  # chapter_01_scene_01_sent_001

                # Find audio files with this prefix
                audio_candidates = list(self.audio_dir.glob(f"{prefix}_*.wav"))

                if len(audio_candidates) == 1:
                    old_audio_path = audio_candidates[0]
                    pairs.append((image_file, old_audio_path, expected_audio_path))
                elif len(audio_candidates) == 0:
                    self.stats['missing_audio'] += 1
                    print(f"[WARN] Missing audio for: {image_file.name}")
                else:
                    # Multiple matches - shouldn't happen but handle it
                    self.stats['errors'] += 1
                    print(f"[ERROR] Multiple audio files match: {image_file.name}")
                    for candidate in audio_candidates:
                        print(f"  - {candidate.name}")
            else:
                self.stats['errors'] += 1
                print(f"[ERROR] Unexpected filename format: {image_file.name}")

        return pairs

    def find_orphan_audio_files(self, chapter_num: int) -> List[Path]:
        """
        Find audio files that don't have corresponding images.

        These are files beyond where image generation stopped.
        We should NOT rename these - they'll be corrected when images are generated.

        Args:
            chapter_num: Chapter number

        Returns:
            List of orphan audio file paths
        """
        chapter_str = f"chapter_{chapter_num:02d}"
        orphans = []

        audio_files = sorted(self.audio_dir.glob(f"{chapter_str}_scene_*_sent_*.wav"))

        for audio_file in audio_files:
            # Check if corresponding image exists
            # Try both old and new naming patterns
            parts = audio_file.stem.split('_')
            if len(parts) >= 6:
                prefix = '_'.join(parts[:6])

                # Check if ANY image exists with this prefix
                image_candidates = list(self.images_dir.glob(f"{prefix}_*.png"))

                if not image_candidates:
                    orphans.append(audio_file)

        return orphans

    def rename_cache_files(self, old_audio_path: Path, new_audio_path: Path) -> bool:
        """
        Rename cache files associated with an audio file.

        Args:
            old_audio_path: Current audio file path
            new_audio_path: New audio file path

        Returns:
            True if successful, False otherwise
        """
        # Cache filename pattern: {audio_filename}_metadata.json
        old_cache_name = old_audio_path.stem + "_metadata.json"
        new_cache_name = new_audio_path.stem + "_metadata.json"

        old_cache_path = self.cache_dir / old_cache_name
        new_cache_path = self.cache_dir / new_cache_name

        if old_cache_path.exists():
            if self.dry_run:
                print(f"  [DRY RUN] Would rename cache: {old_cache_name} -> {new_cache_name}")
                return True
            else:
                try:
                    old_cache_path.rename(new_cache_path)
                    print(f"  [OK] Renamed cache: {new_cache_name}")
                    return True
                except Exception as e:
                    print(f"  [ERROR] Error renaming cache: {e}")
                    return False
        else:
            print(f"  [WARN] No cache file found: {old_cache_name}")
            return True  # Not an error if cache doesn't exist

    def rename_pair(self, image_file: Path, old_audio_path: Path, new_audio_path: Path) -> bool:
        """
        Rename a single audio file and its cache to match image filename.

        Args:
            image_file: Image file path (reference)
            old_audio_path: Current audio file path
            new_audio_path: Target audio file path

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*80}")
        print(f"Image:     {image_file.name}")
        print(f"Old audio: {old_audio_path.name}")
        print(f"New audio: {new_audio_path.name}")

        if self.dry_run:
            print("[DRY RUN] Would rename audio file")
            self.rename_cache_files(old_audio_path, new_audio_path)
            return True

        # Check if target already exists (shouldn't happen)
        if new_audio_path.exists():
            print(f"[ERROR] Target already exists: {new_audio_path.name}")
            self.stats['errors'] += 1
            return False

        # Rename audio file
        try:
            old_audio_path.rename(new_audio_path)
            print(f"[OK] Renamed audio file")

            # Rename cache files
            self.rename_cache_files(old_audio_path, new_audio_path)

            self.stats['renamed'] += 1
            return True

        except Exception as e:
            print(f"[ERROR] Error renaming audio file: {e}")
            self.stats['errors'] += 1
            return False

    def process_chapter(self, chapter_num: int):
        """
        Process all files for a chapter.

        Args:
            chapter_num: Chapter number
        """
        print(f"\n{'='*80}")
        print(f"Processing Chapter {chapter_num}")
        print(f"{'='*80}")

        # Find pairs to rename
        pairs = self.find_image_audio_pairs(chapter_num)

        if not pairs:
            print("\n[OK] No files need renaming")
            return

        print(f"\nFound {len(pairs)} files to rename")

        if self.dry_run:
            print("\n[DRY RUN MODE - No files will be changed]")

        # Process each pair
        for image_file, old_audio_path, new_audio_path in pairs:
            self.rename_pair(image_file, old_audio_path, new_audio_path)

        # Report orphan audio files (for information only)
        orphans = self.find_orphan_audio_files(chapter_num)
        if orphans:
            print(f"\n{'='*80}")
            print(f"Orphan Audio Files (no corresponding images)")
            print(f"{'='*80}")
            print(f"Found {len(orphans)} audio files without images.")
            print("These will be corrected when images are generated with the fixed code.")
            print("\nFirst 5 orphans:")
            for orphan in orphans[:5]:
                print(f"  - {orphan.name}")
            if len(orphans) > 5:
                print(f"  ... and {len(orphans) - 5} more")

    def print_summary(self):
        """Print final statistics."""
        print(f"\n{'='*80}")
        print("Rename Summary")
        print(f"{'='*80}")
        print(f"Total images found:           {self.stats['total_images']}")
        print(f"Already matched:              {self.stats['matched_audio']}")
        print(f"Files renamed:                {self.stats['renamed']}")
        print(f"Missing audio:                {self.stats['missing_audio']}")
        print(f"Errors:                       {self.stats['errors']}")
        print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(
        description="Rename audio files to match image filenames"
    )

    parser.add_argument(
        '--chapter',
        type=int,
        help='Process specific chapter number'
    )

    parser.add_argument(
        '--chapters',
        type=int,
        nargs='+',
        help='Process specific chapter numbers (e.g., --chapters 1 2 3)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all chapters (use with caution!)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be renamed without making changes'
    )

    args = parser.parse_args()

    # Determine which chapters to process
    chapters = []
    if args.chapter:
        chapters = [args.chapter]
    elif args.chapters:
        chapters = args.chapters
    elif args.all:
        chapters = list(range(1, 13))  # All 12 chapters
    else:
        print("Error: Must specify --chapter, --chapters, or --all")
        sys.exit(1)

    # Create renamer
    renamer = AudioRenamer(dry_run=args.dry_run)

    # Process chapters
    for chapter in chapters:
        renamer.process_chapter(chapter)

    # Print summary
    renamer.print_summary()

    if args.dry_run:
        print("\n[DRY RUN COMPLETE - No files were changed]")
        print("Run without --dry-run to actually rename files")


if __name__ == "__main__":
    main()
