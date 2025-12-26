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
import time
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


def check_nvenc_availability() -> tuple[bool, str]:
    """
    Check if NVENC GPU encoding is available.

    Returns:
        Tuple of (is_available, diagnostic_message)
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return False, "CUDA not available"
        gpu_name = torch.cuda.get_device_name(0)
        return True, f"NVENC available on {gpu_name}"
    except ImportError:
        return False, "PyTorch not installed"


# Import video configuration from config.py
try:
    from config import (
        VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
        VIDEO_CODEC_CPU, VIDEO_CODEC_GPU,
        VIDEO_PRESET_CPU, VIDEO_PRESET_GPU,
        VIDEO_CRF, VIDEO_AUDIO_CODEC, ENABLE_GPU_ENCODING
    )
    YOUTUBE_WIDTH = VIDEO_WIDTH
    YOUTUBE_HEIGHT = VIDEO_HEIGHT
    YOUTUBE_FPS = VIDEO_FPS
    AUDIO_CODEC = VIDEO_AUDIO_CODEC
except ImportError:
    # Fallback to hardcoded values if config.py not available
    logger.warning("Could not import from config.py, using hardcoded defaults")
    YOUTUBE_WIDTH = 1080
    YOUTUBE_HEIGHT = 1920
    YOUTUBE_FPS = 30
    VIDEO_CODEC_CPU = 'libx264'
    VIDEO_CODEC_GPU = 'h264_nvenc'
    VIDEO_PRESET_CPU = 'medium'
    VIDEO_PRESET_GPU = 'p5'
    VIDEO_CRF = 18
    AUDIO_CODEC = 'aac'
    ENABLE_GPU_ENCODING = True


class VideoGenerator:
    """Generate video from scene images and audio files."""

    def __init__(self, project_root: Path, output_dir: Path, enable_gpu: bool = True):
        """
        Initialize the video generator.

        Args:
            project_root: Root directory of the project
            output_dir: Directory to save generated videos
            enable_gpu: Enable GPU-accelerated encoding (auto-falls back to CPU if unavailable)
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

        # Detect GPU encoding capability
        self.gpu_encoding_enabled = False
        if enable_gpu:
            nvenc_available, nvenc_message = check_nvenc_availability()
            if nvenc_available:
                self.gpu_encoding_enabled = True
                logger.info(f"GPU encoding enabled: {nvenc_message}")
                logger.info(f"Using codec: {VIDEO_CODEC_GPU}, preset: {VIDEO_PRESET_GPU}")
            else:
                logger.warning(f"GPU encoding disabled: {nvenc_message}")
                logger.info(f"Falling back to CPU encoding: codec={VIDEO_CODEC_CPU}, preset={VIDEO_PRESET_CPU}")
        else:
            logger.info("GPU encoding disabled by configuration")
            logger.info(f"Using CPU encoding: codec={VIDEO_CODEC_CPU}, preset={VIDEO_PRESET_CPU}")

        logger.info(f"Images directory: {self.images_dir}")
        logger.info(f"Audio directory: {self.audio_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Temp directory: {self.temp_dir}")

    def find_sentence_pairs(self, chapter_num: int, first_scene_only: bool = False) -> List[Tuple[Path, Path]]:
        """
        Find matching image and audio file pairs for a chapter (sentence-level).

        Args:
            chapter_num: Chapter number (1-12)
            first_scene_only: If True, only return pairs from scene 1

        Returns:
            List of (image_path, audio_path) tuples, sorted by scene and sentence number
        """
        chapter_str = f"chapter_{chapter_num:02d}"
        pairs = []

        # Find all audio files for this chapter (sentence-level files have "sent_" in the name)
        if first_scene_only:
            audio_files = sorted(self.audio_dir.glob(f"{chapter_str}_scene_01_sent_*.wav"))
        else:
            audio_files = sorted(self.audio_dir.glob(f"{chapter_str}_scene_*_sent_*.wav"))

        for audio_file in audio_files:
            # Construct corresponding image filename
            # chapter_01_scene_01_sent_001_description.wav -> chapter_01_scene_01_sent_001_description.png
            image_file = self.images_dir / audio_file.name.replace('.wav', '.png')

            if image_file.exists():
                pairs.append((image_file, audio_file))
                logger.debug(f"Found pair: {image_file.name} + {audio_file.name}")
            else:
                logger.warning(f"Missing image for audio: {audio_file.name}")

        scene_info = "scene 1 only" if first_scene_only else "all scenes"
        logger.info(f"Found {len(pairs)} sentence pairs for chapter {chapter_num} ({scene_info})")
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

    def _get_encoding_params(self) -> dict:
        """
        Get FFmpeg encoding parameters based on GPU availability.

        Returns:
            Dictionary with codec, preset, ffmpeg_params, and threads
        """
        if self.gpu_encoding_enabled:
            # NVENC GPU encoding
            return {
                'codec': VIDEO_CODEC_GPU,
                'preset': VIDEO_PRESET_GPU,
                'ffmpeg_params': [
                    '-cq', str(VIDEO_CRF),  # Constant quality mode (like CRF for x264)
                    '-rc', 'vbr_hq',  # Variable bitrate high quality mode
                    '-rc-lookahead', '32',  # Look ahead 32 frames for better quality
                    '-spatial-aq', '1',  # Enable spatial adaptive quantization
                    '-temporal-aq', '1',  # Enable temporal adaptive quantization
                    '-gpu', '0',  # Use first GPU
                ],
                'threads': None  # GPU encoding doesn't use CPU threads parameter
            }
        else:
            # CPU encoding (libx264)
            return {
                'codec': VIDEO_CODEC_CPU,
                'preset': VIDEO_PRESET_CPU,
                'ffmpeg_params': ['-crf', str(VIDEO_CRF)],
                'threads': 4
            }

    def generate_chapter_video(self, chapter_num: int, output_filename: str = None, first_scene_only: bool = False) -> Path:
        """
        Generate video for a complete chapter.

        Args:
            chapter_num: Chapter number (1-12)
            output_filename: Optional custom output filename
            first_scene_only: If True, only process the first scene

        Returns:
            Path to the generated video file
        """
        # Determine output filename first to check if it exists
        if output_filename is None:
            output_filename = f"The_Obsolescence_Chapter_{chapter_num:02d}.mp4"

        output_path = self.output_dir / output_filename

        # Check if file already exists
        if output_path.exists():
            logger.info(f"Video already exists, skipping: {output_path}")
            return output_path

        logger.info(f"Generating video for Chapter {chapter_num}")

        # Find all sentence pairs for this chapter
        sentence_pairs = self.find_sentence_pairs(chapter_num, first_scene_only=first_scene_only)

        if not sentence_pairs:
            logger.error(f"No sentence pairs found for chapter {chapter_num}")
            raise ValueError(f"No sentences found for chapter {chapter_num}")

        # Create clips for each sentence
        clips = []
        logger.info(f"Creating {len(sentence_pairs)} sentence clips...")

        for image_path, audio_path in tqdm(sentence_pairs, desc="Creating clips"):
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

        # Write video file
        logger.info(f"Writing video to {output_path}")
        logger.info(f"Total duration: {final_video.duration:.2f}s ({final_video.duration/60:.2f} minutes)")

        # Get encoding parameters
        encoding_params = self._get_encoding_params()
        logger.info(f"Encoding with: codec={encoding_params['codec']}, preset={encoding_params['preset']}")

        encode_start = time.time()
        final_video.write_videofile(
            str(output_path),
            fps=YOUTUBE_FPS,
            codec=encoding_params['codec'],
            audio_codec=AUDIO_CODEC,
            preset=encoding_params['preset'],
            ffmpeg_params=encoding_params['ffmpeg_params'],
            threads=encoding_params['threads'],
            logger='bar',  # Show progress bar
            temp_audiofile=str(self.temp_dir / 'audio.mp4')
        )

        encode_time = time.time() - encode_start
        encode_fps = final_video.duration * YOUTUBE_FPS / encode_time if encode_time > 0 else 0
        logger.info(f"Encoding completed in {encode_time:.2f}s ({encode_fps:.2f} fps)")

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
        # Determine output filename first to check if it exists
        if output_filename is None:
            chapter_range = f"{min(chapter_nums):02d}-{max(chapter_nums):02d}"
            output_filename = f"The_Obsolescence_Chapters_{chapter_range}.mp4"

        output_path = self.output_dir / output_filename

        # Check if file already exists
        if output_path.exists():
            logger.info(f"Video already exists, skipping: {output_path}")
            return output_path

        logger.info(f"Generating multi-chapter video for chapters: {chapter_nums}")

        all_clips = []

        for chapter_num in chapter_nums:
            # Multiple chapters mode: process all scenes
            sentence_pairs = self.find_sentence_pairs(chapter_num, first_scene_only=False)

            if not sentence_pairs:
                logger.warning(f"No sentence pairs found for chapter {chapter_num}, skipping")
                continue

            logger.info(f"Adding {len(sentence_pairs)} sentences from Chapter {chapter_num}")

            for image_path, audio_path in tqdm(sentence_pairs, desc=f"Chapter {chapter_num}"):
                try:
                    clip = self.create_scene_clip(image_path, audio_path)
                    all_clips.append(clip)
                except Exception as e:
                    logger.error(f"Error creating clip for {image_path.name}: {e}")
                    raise

        if not all_clips:
            logger.error("No clips created for any chapter")
            raise ValueError("No sentences found for specified chapters")

        # Concatenate all clips
        logger.info(f"Concatenating {len(all_clips)} total clips...")
        final_video = concatenate_videoclips(all_clips, method="compose")

        # Write video file
        logger.info(f"Writing video to {output_path}")
        logger.info(f"Total duration: {final_video.duration:.2f}s ({final_video.duration/60:.2f} minutes)")

        # Get encoding parameters
        encoding_params = self._get_encoding_params()
        logger.info(f"Encoding with: codec={encoding_params['codec']}, preset={encoding_params['preset']}")

        encode_start = time.time()
        final_video.write_videofile(
            str(output_path),
            fps=YOUTUBE_FPS,
            codec=encoding_params['codec'],
            audio_codec=AUDIO_CODEC,
            preset=encoding_params['preset'],
            ffmpeg_params=encoding_params['ffmpeg_params'],
            threads=encoding_params['threads'],
            logger='bar',
            temp_audiofile=str(self.temp_dir / 'audio.mp4')
        )

        encode_time = time.time() - encode_start
        encode_fps = final_video.duration * YOUTUBE_FPS / encode_time if encode_time > 0 else 0
        logger.info(f"Encoding completed in {encode_time:.2f}s ({encode_fps:.2f} fps)")

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
        default='videos',
        help='Output directory for generated videos (default: videos)'
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
    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='Disable GPU encoding and use CPU (libx264) instead'
    )

    args = parser.parse_args()

    # Determine project root (parent of src/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / args.output_dir

    # Create video generator
    generator = VideoGenerator(project_root, output_dir, enable_gpu=not args.no_gpu)

    try:
        if args.chapter:
            # Single chapter - process first scene only
            generator.generate_chapter_video(args.chapter, args.output_filename, first_scene_only=True)

        elif args.chapters:
            if args.combine:
                # Multiple chapters in one video
                generator.generate_multi_chapter_video(args.chapters, args.output_filename)
            else:
                # Multiple chapters as separate videos - process all scenes
                for chapter_num in args.chapters:
                    generator.generate_chapter_video(chapter_num, first_scene_only=False)

        elif args.all:
            # Find all available chapters (looking for sentence-level files)
            audio_files = sorted(generator.audio_dir.glob("chapter_*_scene_*_sent_*.wav"))
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
                # Each chapter as separate video - process all scenes
                for chapter_num in available_chapters:
                    generator.generate_chapter_video(chapter_num, first_scene_only=False)

        logger.info("All videos generated successfully!")

    except Exception as e:
        logger.error(f"Video generation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
