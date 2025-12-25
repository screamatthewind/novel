# Video Generation for YouTube

This document explains how to use the video generation system to create YouTube-ready videos from scene images and audio files.

## Overview

The `generate_video.py` script uses MoviePy to combine scene images with their corresponding audio files into MP4 videos suitable for YouTube upload. Each image is displayed for the duration of its associated audio file.

## Installation

First, install the required dependencies:

```bash
# From project root
./venv/Scripts/pip install moviepy imageio imageio-ffmpeg
```

Or install all requirements:

```bash
./venv/Scripts/pip install -r requirements.txt
```

## Video Specifications

The generated videos follow YouTube's recommended specifications:

- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 fps
- **Video Codec**: H.264 (libx264)
- **Audio Codec**: AAC
- **Quality**: CRF 18 (visually lossless)
- **Preset**: medium (balances encoding speed and file size)

Images are automatically:
- Resized to fit within 1920x1080 while maintaining aspect ratio
- Centered on a black background
- Displayed for the exact duration of their audio file

## Usage

All commands should be run from the `src/` directory:

```bash
cd src
```

### Generate Single Chapter Video

```bash
# Chapter 1
../venv/Scripts/python generate_video.py --chapter 1

# Chapter 5
../venv/Scripts/python generate_video.py --chapter 5
```

Output: `videos/The_Obsolescence_Chapter_01.mp4`

### Generate Multiple Chapters (Separate Videos)

```bash
# Generates 3 separate video files
../venv/Scripts/python generate_video.py --chapters 1 2 3
```

Output:
- `videos/The_Obsolescence_Chapter_01.mp4`
- `videos/The_Obsolescence_Chapter_02.mp4`
- `videos/The_Obsolescence_Chapter_03.mp4`

### Generate Combined Multi-Chapter Video

```bash
# Combines chapters 1-3 into a single video
../venv/Scripts/python generate_video.py --chapters 1 2 3 --combine
```

Output: `videos/The_Obsolescence_Chapters_01-03.mp4`

### Generate All Available Chapters

```bash
# Separate video for each chapter
../venv/Scripts/python generate_video.py --all

# Or combine all into one video
../venv/Scripts/python generate_video.py --all --combine
```

### Custom Output Options

```bash
# Custom output directory
../venv/Scripts/python generate_video.py --chapter 1 --output-dir ../my_videos

# Custom filename
../venv/Scripts/python generate_video.py --chapter 1 --output-filename "Chapter_One_Preview.mp4"
```

## File Matching

The script automatically matches image and audio files by name:

```
Audio:  chapter_01_scene_01_emma_factory_working.wav
Image:  chapter_01_scene_01_emma_factory_working.png
```

Both files must exist for a scene to be included in the video. Missing pairs are logged as warnings.

## Output Structure

Generated videos are saved to the `videos/` directory by default:

```
novel/
├── videos/
│   ├── The_Obsolescence_Chapter_01.mp4
│   ├── The_Obsolescence_Chapter_02.mp4
│   └── The_Obsolescence_Chapters_01-12.mp4
├── images/
│   ├── chapter_01_scene_01_emma_factory_working.png
│   └── ...
├── audio/
│   ├── chapter_01_scene_01_emma_factory_working.wav
│   └── ...
└── temp/
    └── video/                   # MoviePy temporary files (auto-cleaned)
```

**Note**: Temporary files during video encoding are stored in `temp/video/` instead of cluttering the `src/` directory.

## Logging

Generation logs are saved to `logs/video_generation.log` and displayed in the console.

The log includes:
- Scene pairs found for each chapter
- Clip creation progress
- Total video duration
- Final file size
- Any errors or warnings

## Performance Considerations

### Encoding Speed

The default preset is `medium`, which balances speed and file size. You can modify this in the script:

- **Faster encoding** (larger files): `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`
- **Slower encoding** (smaller files): `slow`, `slower`, `veryslow`

Edit line 36 in `generate_video.py`:
```python
PRESET = 'fast'  # Change from 'medium' to 'fast'
```

### Quality Settings

The default CRF (Constant Rate Factor) is 18, which is visually lossless:

- **CRF 0**: Lossless (huge files)
- **CRF 18-23**: Visually lossless (recommended)
- **CRF 28**: Good quality
- **CRF 51**: Worst quality

Edit line 37 in `generate_video.py`:
```python
CRF = 23  # Change from 18 to 23 for smaller files
```

### Memory Usage

For long videos with many scenes:
- Each scene clip is loaded into memory
- The script processes all clips before writing
- Expect 1-2 GB RAM usage for a typical chapter

## Troubleshooting

### FFmpeg Not Found

If you get an error about FFmpeg:

```bash
../venv/Scripts/pip install imageio-ffmpeg
```

This package includes FFmpeg binaries automatically.

### Out of Memory

For very long videos, consider:
1. Generating chapters separately instead of combining
2. Closing other applications
3. Reducing image resolution before processing

### Slow Encoding

To speed up encoding:
1. Change preset to `fast` or `veryfast`
2. Reduce CRF to 23 (slightly smaller files, faster encoding)
3. Ensure you're not running other intensive tasks

### Audio/Image Mismatch

If some scenes are missing:
1. Check the logs for warnings about missing files
2. Verify file naming follows the pattern: `chapter_XX_scene_YY_description.{png,wav}`
3. Ensure both image and audio exist for each scene

## YouTube Upload Tips

### Video Metadata

When uploading to YouTube, consider:

- **Title**: "The Obsolescence - Chapter [X]: [Chapter Title]"
- **Description**: Include novel synopsis, chapter summary, credits
- **Tags**: "audiobook", "science fiction", "AI fiction", "speculative fiction"
- **Category**: Entertainment or Education
- **Thumbnail**: Use the first scene image or create a custom thumbnail

### Playlists

Create a playlist to organize all chapter videos:
- Playlist title: "The Obsolescence - Complete Novel"
- Order videos by chapter number
- Add playlist description with full novel synopsis

### Copyright

Since this is original content:
- You own the copyright
- Choose appropriate license (Standard YouTube License or Creative Commons)
- Add credits for any tools used (Stable Diffusion XL, Coqui TTS, etc.)

## Example Workflow

Complete workflow for generating and uploading a chapter:

```bash
# 1. Ensure images and audio are generated
cd src
../venv/Scripts/python generate_scene_images.py --chapter 1
../venv/Scripts/python generate_scene_audio.py --chapter 1

# 2. Generate video
../venv/Scripts/python generate_video.py --chapter 1

# 3. Review the video
# Open videos/The_Obsolescence_Chapter_01.mp4 in a video player

# 4. Upload to YouTube
# Use YouTube Studio to upload the MP4 file
```

## Advanced Usage

### Custom Video Settings

To modify video settings, edit the constants at the top of `generate_video.py`:

```python
YOUTUBE_WIDTH = 1920      # Video width
YOUTUBE_HEIGHT = 1080     # Video height
YOUTUBE_FPS = 30          # Frame rate
VIDEO_CODEC = 'libx264'   # Video codec
AUDIO_CODEC = 'aac'       # Audio codec
PRESET = 'medium'         # Encoding speed
CRF = 18                  # Quality (lower = better)
```

### Batch Processing

To generate all chapters as separate videos:

```bash
# PowerShell
for ($i=1; $i -le 12; $i++) {
    ../venv/Scripts/python generate_video.py --chapter $i
}
```

### Dry Run Testing

To test without generating videos, you can modify the script to skip the `write_videofile` call, or simply check the logs for warnings about missing files before generating.
