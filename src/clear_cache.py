"""
Simple script to clear storyboard cache and images for specified chapters.

Usage:
    python clear_cache.py --chapters 1
    python clear_cache.py --chapters 1 2 3
"""

import argparse
import sys
from pathlib import Path

# Import config for directory paths
from config import STORYBOARD_CACHE_DIR, OUTPUT_DIR


def clear_chapter_cache_and_images(chapter_num: int, cache_dir: Path, images_dir: Path):
    """
    Delete all cached storyboard files and generated images for a specific chapter.

    Args:
        chapter_num: Chapter number to delete cache and images for
        cache_dir: Path to storyboard cache directory
        images_dir: Path to images directory

    Returns:
        Tuple of (cache_files_deleted, image_files_deleted)
    """
    cache_files_deleted = 0
    image_files_deleted = 0

    # Delete storyboard cache files for this chapter
    chapter_cache_dir = cache_dir / f"{chapter_num:02d}"
    if chapter_cache_dir.exists():
        cache_files = list(chapter_cache_dir.glob("*.json"))
        for cache_file in cache_files:
            try:
                cache_file.unlink()
                cache_files_deleted += 1
            except Exception as e:
                print(f"Warning: Failed to delete cache file {cache_file}: {e}")

        # Remove directory if empty
        try:
            if not any(chapter_cache_dir.iterdir()):
                chapter_cache_dir.rmdir()
        except Exception:
            pass

    # Delete generated images for this chapter
    if images_dir.exists():
        # Pattern: chapter_XX_*.png
        image_pattern = f"chapter_{chapter_num:02d}_*.png"
        image_files = list(images_dir.glob(image_pattern))
        for image_file in image_files:
            try:
                image_file.unlink()
                image_files_deleted += 1
            except Exception as e:
                print(f"Warning: Failed to delete image file {image_file}: {e}")

    return cache_files_deleted, image_files_deleted


def main():
    parser = argparse.ArgumentParser(description="Clear storyboard cache and images for chapters")
    parser.add_argument(
        '--chapters',
        type=int,
        nargs='+',
        required=True,
        help='Chapter numbers to clear (e.g., --chapters 1 2 3)'
    )

    args = parser.parse_args()

    cache_dir = Path(STORYBOARD_CACHE_DIR)
    images_dir = Path(OUTPUT_DIR)

    print("="*80)
    print("Cache Clearing Tool")
    print("="*80)
    print(f"\nClearing cache and images for chapters: {args.chapters}")
    print(f"Cache directory: {cache_dir}")
    print(f"Images directory: {images_dir}")
    print()

    total_cache = 0
    total_images = 0

    for chapter_num in args.chapters:
        cache_deleted, images_deleted = clear_chapter_cache_and_images(
            chapter_num, cache_dir, images_dir
        )
        total_cache += cache_deleted
        total_images += images_deleted
        print(f"  Chapter {chapter_num}: Deleted {cache_deleted} cache files, {images_deleted} image files")

    print(f"\nTotal: {total_cache} cache files, {total_images} image files deleted")
    print("="*80)


if __name__ == "__main__":
    main()
