#!/usr/bin/env bash
# Full pipeline script for The Obsolescence novel generation
# Runs cleanup, image generation, audio generation, and video generation sequentially

set -e  # Exit on error

echo "================================================================================"
echo "The Obsolescence - Full Generation Pipeline"
echo "================================================================================"
echo ""
# Get chapter selection ONCE at the beginning
read -p "Enter chapter numbers to process (e.g., 1 2 3) or press Enter for all: " CHAPTERS

echo ""
if [ -z "$CHAPTERS" ]; then
    echo "Selected: ALL chapters"
else
    echo "Selected: Chapters $CHAPTERS"
fi

echo ""
read -p "Cleanup existing generated files before starting? (y/N): " CLEANUP_CONFIRM

echo ""
if [[ "$CLEANUP_CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Pipeline will: CLEANUP, then generate images, audio, and video"
else
    echo "Pipeline will: Generate images, audio, and video (keeping existing files)"
fi

echo ""
read -p "Continue? (y/N): " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Pipeline cancelled."
    exit 0
fi

echo ""

if [[ "$CLEANUP_CONFIRM" =~ ^[Yy]$ ]]; then
    echo "================================================================================"
    echo "Step 1: Cleanup"
    echo "================================================================================"
    echo ""

    # Run cleanup script with --yes flag to skip confirmation
    ../venv/Scripts/python cleanup.py --yes

    echo ""
else
    echo "Skipping cleanup - will use/overwrite existing files as needed"
    echo ""
fi

echo "Starting pipeline..."
echo ""

echo ""
echo "================================================================================"
echo "Step 2: Generate Scene Images"
echo "================================================================================"
echo ""

if [ -z "$CHAPTERS" ]; then
    echo "Generating images for all chapters..."
    ../venv/Scripts/python generate_scene_images.py
else
    echo "Generating images for chapters: $CHAPTERS"
    ../venv/Scripts/python generate_scene_images.py --chapters $CHAPTERS
fi

echo ""
echo "================================================================================"
echo "Step 3: Generate Scene Audio"
echo "================================================================================"
echo ""

if [ -z "$CHAPTERS" ]; then
    echo "Generating audio for all chapters..."
    ../venv/Scripts/python generate_scene_audio.py
else
    echo "Generating audio for chapters: $CHAPTERS"
    ../venv/Scripts/python generate_scene_audio.py --chapters $CHAPTERS
fi

echo ""
echo "================================================================================"
echo "Step 4: Generate Video"
echo "================================================================================"
echo ""

if [ -z "$CHAPTERS" ]; then
    echo "Generating video for all chapters..."
    ../venv/Scripts/python generate_video.py --all
else
    echo "Generating video for chapters: $CHAPTERS"
    ../venv/Scripts/python generate_video.py --chapters $CHAPTERS
fi

echo ""
echo "================================================================================"
echo "Pipeline Complete!"
echo "================================================================================"
echo ""
echo "All steps completed successfully."
echo "Generated files can be found in:"
echo "  - Images: ../images/"
echo "  - Audio:  ../audio/"
echo "  - Videos: ../videos/"
echo ""

exit 0
