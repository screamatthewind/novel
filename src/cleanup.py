"""
Cleanup utility for "The Obsolescence" novel project.

Safely deletes all generated files (audio, images, videos, logs, caches) to enable
a clean regeneration from scratch. Preserves source files, configuration, and .gitkeep markers.

Usage:
    # Preview what will be deleted
    python cleanup.py --dry-run

    # Execute cleanup with confirmation
    python cleanup.py

    # Execute without confirmation (careful!)
    python cleanup.py --yes

    # Verbose mode showing each file
    python cleanup.py --verbose
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# File patterns to delete in each directory (preserving .gitkeep)
# These match the directories defined in config.py and .gitignore
CLEANUP_TARGETS = {
    'audio': ['*.wav', '*.mp3'],
    'audio_cache': ['*.json'],
    'images': ['*.png', '*.jpg', '*.jpeg'],
    'videos': ['*.mp4', '*.avi', '*.mov'],
    'logs': ['*.log'],
    'prompt_cache': ['*.txt'],
}

# Directories to completely remove (will be recreated by scripts as needed)
DIRECTORY_TARGETS = [
    'temp',           # Temporary files (MoviePy, video generation, voice downloads)
    '.cache',         # General cache
    'huggingface',    # HuggingFace model cache
]


def get_project_root() -> Path:
    """Get the project root directory (parent of src/)."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def find_pycache_dirs(root: Path) -> List[Path]:
    """Recursively find all __pycache__ directories, excluding venv."""
    pycache_dirs = []
    for dirpath, dirnames, _ in os.walk(root):
        # Skip venv directory
        if 'venv' in dirnames:
            dirnames.remove('venv')

        if '__pycache__' in dirnames:
            pycache_dirs.append(Path(dirpath) / '__pycache__')
    return pycache_dirs


def get_file_size(path: Path) -> int:
    """Get file size in bytes, handling errors."""
    try:
        return path.stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def format_size(bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def scan_files(root: Path, verbose: bool = False) -> Tuple[Dict[str, List[Path]], List[Path], List[Path]]:
    """
    Scan for files to delete.

    Returns:
        Tuple of (file_targets, directory_targets, pycache_dirs)
    """
    files_to_delete = {key: [] for key in CLEANUP_TARGETS.keys()}
    dirs_to_delete = []

    # Scan file targets
    for dir_name, patterns in CLEANUP_TARGETS.items():
        dir_path = root / dir_name
        if not dir_path.exists():
            continue

        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                # Preserve .gitkeep files
                if file_path.name != '.gitkeep':
                    files_to_delete[dir_name].append(file_path)

    # Scan directory targets
    for dir_name in DIRECTORY_TARGETS:
        dir_path = root / dir_name
        if dir_path.exists():
            dirs_to_delete.append(dir_path)

    # Find __pycache__ directories
    pycache_dirs = find_pycache_dirs(root)

    return files_to_delete, dirs_to_delete, pycache_dirs


def calculate_statistics(files_to_delete: Dict[str, List[Path]],
                         dirs_to_delete: List[Path],
                         pycache_dirs: List[Path]) -> Dict[str, Tuple[int, int]]:
    """
    Calculate deletion statistics.

    Returns:
        Dict mapping category to (file_count, total_size)
    """
    stats = {}

    # File statistics
    for category, files in files_to_delete.items():
        count = len(files)
        size = sum(get_file_size(f) for f in files)
        stats[category] = (count, size)

    # Directory statistics
    dir_count = len(dirs_to_delete)
    dir_size = 0
    for dir_path in dirs_to_delete:
        for dirpath, _, filenames in os.walk(dir_path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                dir_size += get_file_size(filepath)
    stats['directories'] = (dir_count, dir_size)

    # __pycache__ statistics
    pycache_count = 0
    pycache_size = 0
    for pycache_dir in pycache_dirs:
        for dirpath, _, filenames in os.walk(pycache_dir):
            pycache_count += len(filenames)
            for filename in filenames:
                filepath = Path(dirpath) / filename
                pycache_size += get_file_size(filepath)
    stats['pycache'] = (pycache_count, pycache_size)

    return stats


def print_summary(stats: Dict[str, Tuple[int, int]]):
    """Print deletion summary."""
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)

    category_names = {
        'audio': 'Audio files',
        'audio_cache': 'Audio cache',
        'images': 'Images',
        'videos': 'Videos',
        'logs': 'Logs',
        'prompt_cache': 'Prompt cache',
        'pycache': 'Python cache',
        'directories': 'Temp directories',
    }

    total_files = 0
    total_size = 0

    for category, (count, size) in stats.items():
        name = category_names.get(category, category)

        if category == 'directories':
            if count > 0:
                print(f"{name:20} {count} directories ({format_size(size)})")
        else:
            if count > 0:
                print(f"{name:20} {count} files ({format_size(size)})")

        total_files += count
        total_size += size

    print("-" * 60)
    print(f"{'TOTAL':20} {total_files} items ({format_size(total_size)})")
    print("=" * 60 + "\n")


def delete_files(files_to_delete: Dict[str, List[Path]],
                dirs_to_delete: List[Path],
                pycache_dirs: List[Path],
                verbose: bool = False,
                dry_run: bool = False):
    """Delete files and directories."""
    deleted_count = 0
    error_count = 0

    # Delete files
    for category, files in files_to_delete.items():
        for file_path in files:
            try:
                if verbose:
                    action = "Would delete" if dry_run else "Deleting"
                    print(f"{action}: {file_path}")

                if not dry_run:
                    file_path.unlink()
                deleted_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error deleting {file_path}: {e}", file=sys.stderr)

    # Delete directories
    for dir_path in dirs_to_delete:
        try:
            if verbose:
                action = "Would remove" if dry_run else "Removing"
                print(f"{action} directory: {dir_path}")

            if not dry_run:
                shutil.rmtree(dir_path)
            deleted_count += 1

        except Exception as e:
            error_count += 1
            print(f"Error removing {dir_path}: {e}", file=sys.stderr)

    # Delete __pycache__ directories
    for pycache_dir in pycache_dirs:
        try:
            if verbose:
                action = "Would remove" if dry_run else "Removing"
                print(f"{action} __pycache__: {pycache_dir}")

            if not dry_run:
                shutil.rmtree(pycache_dir)
            deleted_count += 1

        except Exception as e:
            error_count += 1
            print(f"Error removing {pycache_dir}: {e}", file=sys.stderr)

    return deleted_count, error_count


def main():
    parser = argparse.ArgumentParser(
        description='Clean all generated files from The Obsolescence project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview files to delete without actually deleting')
    parser.add_argument('--yes', '-y', action='store_true',
                       help='Skip confirmation prompt')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show each file being deleted')

    args = parser.parse_args()

    # Get project root
    root = get_project_root()

    print(f"Project root: {root}\n")

    # Scan for files to delete
    print("Scanning for generated files...")
    files_to_delete, dirs_to_delete, pycache_dirs = scan_files(root, args.verbose)

    # Calculate statistics
    stats = calculate_statistics(files_to_delete, dirs_to_delete, pycache_dirs)

    # Print summary
    print_summary(stats)

    # Check if there's anything to delete
    total_items = sum(count for count, _ in stats.values())
    if total_items == 0:
        print("No files to delete. Project is already clean!")
        return 0

    # Confirmation
    if args.dry_run:
        print("DRY RUN MODE - No files will be deleted\n")
    elif not args.yes:
        response = input("Proceed with deletion? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("Cleanup cancelled.")
            return 0

    # Delete files
    print()
    deleted_count, error_count = delete_files(
        files_to_delete,
        dirs_to_delete,
        pycache_dirs,
        args.verbose,
        args.dry_run
    )

    # Final report
    print()
    if args.dry_run:
        print(f"Dry run complete. {total_items} items would be deleted.")
    else:
        print(f"Cleanup complete!")
        print(f"Successfully deleted: {deleted_count} items")
        if error_count > 0:
            print(f"Errors encountered: {error_count} items", file=sys.stderr)
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
