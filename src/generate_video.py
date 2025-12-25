#!/usr/bin/env python3
"""
Generate video from scene images and audio files for YouTube upload.

This script combines generated scene images with their corresponding audio files
to create a video. Each image is displayed for the duration of its audio file.

Usage:
    # Generate video for specific chapter
    python generate_video.py --chapter 1

    # Generate video for multiple chapters
    python generate_video.py --chapters 1 2 3

    # Generate video for all available chapters
    python generate_video.py --all

    # Custom output directory
    python generate_video.py --chapter 1 --output-dir ../videos
"""

import argparse
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/video_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# YouTube recommended specs
YOUTUBE_WIDTH = 1920
YOUTUBE_HEIGHT = 1080
YOUTUBE_FPS = 30
VIDEO_CODEC = 'libx264'
AUDIO_CODEC = 'aac'
PRESET = 'medium'  # Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
CRF = 18  # Constant Rate Factor: 0 (lossless) to 51 (worst), 18-23 is visually lossless


class VideoGenerator:
    """Generate video from scene images and audio files."""

    def __init__(self, project_root: Path, output_dir: Path):
        """
        Initialize the video generator.

        Args:
            project_root: Root directory of the project
            output_dir: Directory to save generated videos
        """
        self.project_root = project_root
        self.images_dir = project_root / 'images'
        self.audio_dir = project_root / 'audio'
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create temp directory for MoviePy temporary files
        self.temp_dir = project_root / 'temp' / 'video'
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Set MoviePy's temp directory via environment variable
        os.environ['TMPDIR'] = str(self.temp_dir)
        os.environ['TEMP'] = str(self.temp_dir)
        os.environ['TMP'] = str(self.temp_dir)

        logger.info(f"Images directory: {self.images_dir}")
        logger.info(f"Audio directory: {self.audio_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Temp directory: {self.temp_dir}")

    def find_scene_pairs(self, chapter_num: int) -> List[Tuple[Path, Path]]:
        """
        Find matching image and audio file pairs for a chapter.

        Args:
            chapter_num: Chapter number (1-12)

        Returns:
            List of (image_path, audio_path) tuples, sorted by scene number
        """
        chapter_str = f"chapter_{chapter_num:02d}"
        pairs = []

        # Find all audio files for this chapter
        audio_files = sorted(self.audio_dir.glob(f"{chapter_str}_scene_*.wav"))

        for audio_file in audio_files:
            # Construct corresponding image filename
            # chapter_01_scene_01_description.wav -> chapter_01_scene_01_description.png
            image_file = self.images_dir / audio_file.name.replace('.wav', '.png')

            if image_file.exists():
                pairs.append((image_file, audio_file))
                logger.debug(f"Found pair: {image_file.name} + {audio_file.name}")
            else:
                logger.warning(f"Missing image for audio: {audio_file.name}")

        logger.info(f"Found {len(pairs)} scene pairs for chapter {chapter_num}")
        return pairs

    def resize_image_to_fit(self, image_path: Path) -> ImageClip:
        """
        Load and resize image to fit YouTube dimensions while maintaining aspect ratio.

        Args:
            image_path: Path to the image file

        Returns:
            ImageClip resized to fit YouTube dimensions
        """
        # Create image clip
        clip = ImageClip(str(image_path))

        # Calculate scaling to fit within YouTube dimensions while maintaining aspect ratio
        img_width, img_height = clip.size
        width_ratio = YOUTUBE_WIDTH / img_width
        height_ratio = YOUTUBE_HEIGHT / img_height
        scale_ratio = min(width_ratio, height_ratio)

        new_width = int(img_width * scale_ratio)
        new_height = int(img_height * scale_ratio)

        # Resize image
        clip = clip.resized((new_width, new_height))

        # Center on black background
        clip = clip.with_position('center')

        return clip

    def create_scene_clip(self, image_path: Path, audio_path: Path) -> CompositeVideoClip:
        """
        Create a video clip for a single scene.

        Args:
            image_path: Path to the scene image
            audio_path: Path to the scene audio

        Returns:
            VideoClip with image and audio combined
        """
        # Load audio to get duration
        audio_clip = AudioFileClip(str(audio_path))
        duration = audio_clip.duration

        # Load and resize image
        image_clip = self.resize_image_to_fit(image_path)
        image_clip = image_clip.with_duration(duration)

        # Create black background
        background = ColorClip(
            size=(YOUTUBE_WIDTH, YOUTUBE_HEIGHT),
            color=(0, 0, 0),
            duration=duration
        )

        # Composite image on background
        video_clip = CompositeVideoClip([background, image_clip])

        # Add audio
        video_clip = video_clip.with_audio(audio_clip)

        return video_clip

    def generate_chapter_video(self, chapter_num: int, output_filename: str = None) -> Path:
        """
        Generate video for a complete chapter.

        Args:
            chapter_num: Chapter number (1-12)
            output_filename: Optional custom output filename

        Returns:
            Path to the generated video file
        """
        logger.info(f"Generating video for Chapter {chapter_num}")

        # Find all scene pairs for this chapter
        scene_pairs = self.find_scene_pairs(chapter_num)

        if not scene_pairs:
            logger.error(f"No scene pairs found for chapter {chapter_num}")
            raise ValueError(f"No scenes found for chapter {chapter_num}")

        # Create clips for each scene
        clips = []
        logger.info(f"Creating {len(scene_pairs)} scene clips...")

        for image_path, audio_path in tqdm(scene_pairs, desc="Creating clips"):
            try:
                clip = self.create_scene_clip(image_path, audio_path)
                clips.append(clip)
                logger.debug(f"Created clip for {image_path.name} (duration: {clip.duration:.2f}s)")
            except Exception as e:
                logger.error(f"Error creating clip for {image_path.name}: {e}")
                raise

        # Concatenate all clips
        logger.info("Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")

        # Determine output filename
        if output_filename is None:
            output_filename = f"The_Obsolescence_Chapter_{chapter_num:02d}.mp4"

        output_path = self.output_dir / output_filename

        # Write video file
        logger.info(f"Writing video to {output_path}")
        logger.info(f"Total duration: {final_video.duration:.2f}s ({final_video.duration/60:.2f} minutes)")

        final_video.write_videofile(
            str(output_path),
            fps=YOUTUBE_FPS,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            preset=PRESET,
            ffmpeg_params=['-crf', str(CRF)],
            threads=4,
            logger='bar'  # Show progress bar
        )

        # Clean up
        final_video.close()
        for clip in clips:
            clip.close()

        logger.info(f"Video generation complete: {output_path}")
        logger.info(f"File size: {output_path.stat().st_size / (1024*1024):.2f} MB")

        return output_path

    def generate_multi_chapter_video(self, chapter_nums: List[int], output_filename: str = None) -> Path:
        """
        Generate a single video containing multiple chapters.

        Args:
            chapter_nums: List of chapter numbers to include
            output_filename: Optional custom output filename

        Returns:
            Path to the generated video file
        """
        logger.info(f"Generating multi-chapter video for chapters: {chapter_nums}")

        all_clips = []

        for chapter_num in chapter_nums:
            scene_pairs = self.find_scene_pairs(chapter_num)

            if not scene_pairs:
                logger.warning(f"No scene pairs found for chapter {chapter_num}, skipping")
                continue

            logger.info(f"Adding {len(scene_pairs)} scenes from Chapter {chapter_num}")

            for image_path, audio_path in tqdm(scene_pairs, desc=f"Chapter {chapter_num}"):
                try:
                    clip = self.create_scene_clip(image_path, audio_path)
                    all_clips.append(clip)
                except Exception as e:
                    logger.error(f"Error creating clip for {image_path.name}: {e}")
                    raise

        if not all_clips:
            logger.error("No clips created for any chapter")
            raise ValueError("No scenes found for specified chapters")

        # Concatenate all clips
        logger.info(f"Concatenating {len(all_clips)} total clips...")
        final_video = concatenate_videoclips(all_clips, method="compose")

        # Determine output filename
        if output_filename is None:
            chapter_range = f"{min(chapter_nums):02d}-{max(chapter_nums):02d}"
            output_filename = f"The_Obsolescence_Chapters_{chapter_range}.mp4"

        output_path = self.output_dir / output_filename

        # Write video file
        logger.info(f"Writing video to {output_path}")
        logger.info(f"Total duration: {final_video.duration:.2f}s ({final_video.duration/60:.2f} minutes)")

        final_video.write_videofile(
            str(output_path),
            fps=YOUTUBE_FPS,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            preset=PRESET,
            ffmpeg_params=['-crf', str(CRF)],
            threads=4,
            logger='bar'
        )

        # Clean up
        final_video.close()
        for clip in all_clips:
            clip.close()

        logger.info(f"Video generation complete: {output_path}")
        logger.info(f"File size: {output_path.stat().st_size / (1024*1024):.2f} MB")

        return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate video from scene images and audio files for YouTube upload.'
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--chapter',
        type=int,
        help='Generate video for a single chapter (1-12)'
    )
    group.add_argument(
        '--chapters',
        type=int,
        nargs='+',
        help='Generate video for multiple chapters (e.g., --chapters 1 2 3)'
    )
    group.add_argument(
        '--all',
        action='store_true',
        help='Generate videos for all available chapters'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='../videos',
        help='Output directory for generated videos (default: ../videos)'
    )
    parser.add_argument(
        '--output-filename',
        type=str,
        help='Custom output filename (without path)'
    )
    parser.add_argument(
        '--combine',
        action='store_true',
        help='Combine multiple chapters into a single video file'
    )

    args = parser.parse_args()

    # Determine project root (parent of src/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / args.output_dir

    # Create video generator
    generator = VideoGenerator(project_root, output_dir)

    try:
        if args.chapter:
            # Single chapter
            generator.generate_chapter_video(args.chapter, args.output_filename)

        elif args.chapters:
            if args.combine:
                # Multiple chapters in one video
                generator.generate_multi_chapter_video(args.chapters, args.output_filename)
            else:
                # Multiple chapters as separate videos
                for chapter_num in args.chapters:
                    generator.generate_chapter_video(chapter_num)

        elif args.all:
            # Find all available chapters
            audio_files = sorted(generator.audio_dir.glob("chapter_*_scene_*.wav"))
            available_chapters = sorted(set(
                int(f.name.split('_')[1]) for f in audio_files
            ))

            if not available_chapters:
                logger.error("No chapter audio files found")
                sys.exit(1)

            logger.info(f"Found chapters: {available_chapters}")

            if args.combine:
                # All chapters in one video
                generator.generate_multi_chapter_video(available_chapters, args.output_filename)
            else:
                # Each chapter as separate video
                for chapter_num in available_chapters:
                    generator.generate_chapter_video(chapter_num)

        logger.info("All videos generated successfully!")

    except Exception as e:
        logger.error(f"Video generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
