#!/usr/bin/env python3
"""
Full Pipeline Runner for The Obsolescence
Generates images, audio, and video for all chapters
"""

import subprocess
import sys
from pathlib import Path


def run_command(description: str, command: list[str]) -> None:
    """Run a command and handle errors."""
    print("\n" + "=" * 50)
    print(description)
    print("=" * 50)
    print()

    result = subprocess.run(command, cwd=Path(__file__).parent)
    if result.returncode != 0:
        print(f"\n❌ Error: {description} failed with code {result.returncode}")
        sys.exit(result.returncode)


def main():
    """Run the full generation pipeline."""
    print("=" * 50)
    print("The Obsolescence - Full Generation Pipeline")
    print("=" * 50)
    print()

    # Get Python executable from venv
    venv_python = Path(__file__).parent.parent / "venv" / "Scripts" / "python.exe"
    python_exe = str(venv_python)

    # Step 1: Generate scene images
    run_command(
        "STEP 1: Generating Scene Images (All Chapters)",
        [
            python_exe,
            "generate_scene_images.py",
            "--chapters", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
            "--enable-smart-detection",
            "--enable-ip-adapter",
            "--llm", "haiku"
        ]
    )

    # Step 2: Generate scene audio
    run_command(
        "STEP 2: Generating Scene Audio (All Chapters)",
        [
            python_exe,
            "generate_scene_audio.py",
            "--chapters", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"
        ]
    )

    # Step 3: Generate combined video
    run_command(
        "STEP 3: Generating Combined Video (All Chapters)",
        [
            python_exe,
            "generate_video.py",
            "--all",
            "--combine"
        ]
    )

    print("\n" + "=" * 50)
    print("Pipeline Complete!")
    print("=" * 50)
    print("\nGenerated content:")
    print("  - Images: ../images/")
    print("  - Audio: ../audio/")
    print("  - Video: ../videos/")
    print()


if __name__ == "__main__":
    main()
