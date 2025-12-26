#!/bin/bash
# Full Pipeline Runner for The Obsolescence
# Generates images, audio, and video for all chapters
# Run from project root: ./run_full_pipeline.sh

set -e  # Exit on error

echo "=================================================="
echo "The Obsolescence - Full Generation Pipeline"
echo "=================================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate

# Navigate to src directory
cd src

echo ""
echo "=================================================="
echo "STEP 1: Generating Scene Images (All Chapters)"
echo "=================================================="
echo ""
../venv/Scripts/python generate_scene_images.py \
    --chapters 1 2 3 4 5 6 7 8 9 10 11 12 \
    --enable-smart-detection \
    --enable-ip-adapter \
    --llm haiku

echo ""
echo "=================================================="
echo "STEP 2: Generating Scene Audio (All Chapters)"
echo "=================================================="
echo ""
../venv/Scripts/python generate_scene_audio.py \
    --chapters 1 2 3 4 5 6 7 8 9 10 11 12

echo ""
echo "=================================================="
echo "STEP 3: Generating Combined Video (All Chapters)"
echo "=================================================="
echo ""
../venv/Scripts/python generate_video.py \
    --all \
    --combine

echo ""
echo "=================================================="
echo "Pipeline Complete!"
echo "=================================================="
echo ""
echo "Generated content:"
echo "  - Images: ../images/"
echo "  - Audio: ../audio/"
echo "  - Video: ../videos/"
echo ""
