"""
Main CLI script for generating scene audio from novel chapters.

Parses markdown chapters, extracts scenes, converts dialogue to speech,
and creates multi-voice audio files using Coqui TTS XTTS v2.
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path

from scene_parser import parse_all_chapters, Scene
from dialogue_parser import parse_scene_text, DialogueSegment
from audio_filename_generator import generate_audio_filename
from audio_generator import CoquiTTSGenerator
from voice_config import get_voice_for_speaker
from config import (
    AUDIO_DIR,
    AUDIO_CACHE_DIR,
    LOG_DIR,
    DEFAULT_AUDIO_FORMAT,
    MAX_TTS_CHUNK_SIZE
)


def setup_logging() -> str:
    """
    Setup logging file for this generation run.

    Returns:
        Path to log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"audio_generation_{timestamp}.log")
    return log_file


def log_message(log_file: str, message: str, print_to_console: bool = True):
    """
    Write message to log file and optionally print to console.

    Args:
        log_file: Path to log file
        message: Message to log
        print_to_console: Whether to also print to console
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    if print_to_console:
        # Replace Unicode symbols that may not render in Windows console
        console_message = message.replace('⟳', '>').replace('✓', '[OK]').replace('✗', '[ERROR]').replace('⊙', '[SKIP]').replace('⚠', '[WARN]')
        print(console_message)


def save_dialogue_to_cache(filename: str, segments: list[DialogueSegment]):
    """
    Save parsed dialogue segments to cache for future reference.

    Args:
        filename: Audio filename (e.g., 'chapter_01_scene_02_emma_factory.wav')
        segments: List of DialogueSegment objects
    """
    # Create cache filename
    cache_filename = filename.replace('.wav', '_dialogue.json')
    cache_path = os.path.join(AUDIO_CACHE_DIR, cache_filename)

    # Convert segments to dict for JSON serialization
    segments_data = [
        {
            'text': seg.text,
            'speaker': seg.speaker,
            'type': seg.segment_type
        }
        for seg in segments
    ]

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(segments_data, f, indent=2, ensure_ascii=False)


def save_metadata_to_cache(filename: str, metadata: dict):
    """
    Save generation metadata to cache.

    Args:
        filename: Audio filename
        metadata: Metadata dictionary
    """
    cache_filename = filename.replace('.wav', '_metadata.json')
    cache_path = os.path.join(AUDIO_CACHE_DIR, cache_filename)

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def process_scene(
    scene: Scene,
    generator: CoquiTTSGenerator,
    log_file: str,
    args: argparse.Namespace,
    dry_run: bool = False
) -> bool:
    """
    Process a single scene: parse dialogue, generate audio, save files.

    Args:
        scene: Scene object to process
        generator: Initialized Coqui TTS generator
        log_file: Path to log file
        args: Command-line arguments
        dry_run: If True, only parse and display dialogue without generating audio

    Returns:
        True if successful, False if error occurred
    """
    # Generate filename
    filename = generate_audio_filename(
        scene.chapter_num,
        scene.scene_num,
        scene.content,
        ext=args.audio_format
    )
    output_path = os.path.join(AUDIO_DIR, filename)

    # Log scene info
    log_message(
        log_file,
        f"\n{'='*80}\nChapter {scene.chapter_num}, Scene {scene.scene_num} ({scene.word_count} words)"
    )
    log_message(log_file, f"Filename: {filename}")

    # Parse dialogue
    log_message(log_file, "Parsing dialogue segments...")
    segments = parse_scene_text(scene.content)

    dialogue_count = sum(1 for s in segments if s.segment_type == 'dialogue')
    narration_count = sum(1 for s in segments if s.segment_type == 'narration')

    log_message(log_file, f"Parsed: {dialogue_count} dialogue, {narration_count} narration segments")

    # Get unique speakers
    speakers = set(seg.speaker for seg in segments)
    log_message(log_file, f"Speakers: {', '.join(sorted(speakers))}")

    if dry_run:
        print(f"\n[DRY RUN] Would generate: {filename}")
        print(f"Segments breakdown:")
        for i, seg in enumerate(segments[:5], 1):  # Show first 5 segments
            print(f"  {i}. [{seg.segment_type}] {seg.speaker}: {seg.text[:50]}...")
        if len(segments) > 5:
            print(f"  ... and {len(segments) - 5} more segments")
        return True

    # Check if audio already exists
    if os.path.exists(output_path) and not args.skip_cache:
        log_message(log_file, f"⊙ Audio already exists, skipping: {filename}")
        return True

    try:
        # Generate audio for each segment
        start_time = datetime.now()
        log_message(log_file, f"⟳ Generating audio segments...")

        audio_segments = []

        for i, segment in enumerate(segments, 1):
            # Get voice for speaker
            if args.single_voice:
                speaker_wav = get_voice_for_speaker("narrator")
            else:
                speaker_wav = get_voice_for_speaker(segment.speaker)

            log_message(
                log_file,
                f"  [{i}/{len(segments)}] {segment.segment_type} ({segment.speaker}): {len(segment.text)} chars",
                print_to_console=False
            )

            # Generate audio for this segment (with chunking if needed)
            audio = generator.generate_speech_chunked(
                text=segment.text,
                speaker_wav=speaker_wav if os.path.exists(speaker_wav) else None,
                language="en",
                max_chunk_size=MAX_TTS_CHUNK_SIZE
            )

            if audio is not None:
                audio_segments.append(audio)
            else:
                log_message(log_file, f"  ⚠ Warning: Failed to generate segment {i}")

        if not audio_segments:
            log_message(log_file, f"✗ ERROR: No audio segments generated")
            return False

        # Concatenate all segments
        log_message(log_file, f"Concatenating {len(audio_segments)} audio segments...")
        final_audio = generator.concatenate_audio_segments(
            audio_segments,
            pause_duration=0.3  # 300ms pause between segments
        )

        # Save audio file
        success = generator.save_audio(final_audio, output_path)

        if not success:
            log_message(log_file, f"✗ ERROR: Failed to save audio file")
            return False

        # Get duration
        duration = generator.get_audio_duration(final_audio)
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        # Save dialogue and metadata to cache
        save_dialogue_to_cache(filename, segments)

        metadata = {
            'chapter': scene.chapter_num,
            'scene': scene.scene_num,
            'word_count': scene.word_count,
            'segment_count': len(segments),
            'dialogue_count': dialogue_count,
            'narration_count': narration_count,
            'speakers': sorted(list(speakers)),
            'duration_seconds': duration,
            'generated_at': datetime.now().isoformat()
        }
        save_metadata_to_cache(filename, metadata)

        # Log success
        elapsed = (datetime.now() - start_time).total_seconds()
        log_message(
            log_file,
            f"✓ Audio saved: {filename} (duration: {minutes}m {seconds}s, took {elapsed/60:.1f} minutes)"
        )

        return True

    except Exception as e:
        log_message(log_file, f"✗ ERROR generating audio: {str(e)}")
        import traceback
        log_message(log_file, traceback.format_exc(), print_to_console=False)
        # Save dialogue anyway for manual retry
        save_dialogue_to_cache(filename, segments)
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate scene audio from novel chapters using Coqui TTS"
    )

    parser.add_argument(
        '--chapters',
        type=int,
        nargs='+',
        help='Specific chapter numbers to process (e.g., --chapters 1 3)'
    )

    parser.add_argument(
        '--resume',
        type=int,
        nargs=2,
        metavar=('CHAPTER', 'SCENE'),
        help='Resume from specific chapter and scene (e.g., --resume 2 5)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show dialogue parsing without generating audio'
    )

    parser.add_argument(
        '--audio-format',
        type=str,
        default=DEFAULT_AUDIO_FORMAT,
        choices=['wav', 'mp3'],
        help=f'Output audio format (default: {DEFAULT_AUDIO_FORMAT})'
    )

    parser.add_argument(
        '--single-voice',
        action='store_true',
        help='Use narrator voice only (testing mode)'
    )

    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Regenerate even if audio file exists'
    )

    args = parser.parse_args()

    # Setup logging
    log_file = setup_logging()
    log_message(log_file, "="*80)
    log_message(log_file, "Novel Scene Audio Generation")
    log_message(log_file, "="*80)

    # Check CUDA availability
    if not args.dry_run:
        try:
            import torch
        except ImportError:
            log_message(log_file, "ERROR: PyTorch not installed. Please run: pip install -r requirements.txt")
            sys.exit(1)

        if torch.cuda.is_available():
            log_message(log_file, f"GPU: {torch.cuda.get_device_name(0)}")
            log_message(log_file, f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            log_message(log_file, "⚠ WARNING: CUDA not available. Using CPU (will be slower)")

    # Parse chapters
    log_message(log_file, "\nParsing chapters...")
    scenes = parse_all_chapters(chapter_numbers=args.chapters)

    if not scenes:
        log_message(log_file, "ERROR: No scenes found to process")
        sys.exit(1)

    log_message(log_file, f"Found {len(scenes)} scenes to process")

    # Filter scenes if resuming
    if args.resume:
        resume_chapter, resume_scene = args.resume
        scenes = [
            s for s in scenes
            if (s.chapter_num > resume_chapter) or
               (s.chapter_num == resume_chapter and s.scene_num >= resume_scene)
        ]
        log_message(
            log_file,
            f"Resuming from Chapter {resume_chapter}, Scene {resume_scene} ({len(scenes)} scenes)"
        )

    # Dry run mode - just show dialogue parsing
    if args.dry_run:
        log_message(log_file, "\n=== DRY RUN MODE ===\n")
        for scene in scenes:
            process_scene(scene, None, log_file, args, dry_run=True)
        log_message(log_file, f"\nDry run complete. Would generate {len(scenes)} audio files.")
        return

    # Load TTS model
    log_message(log_file, "\nLoading Coqui TTS model...")
    generator = CoquiTTSGenerator()

    if not generator.load_model():
        log_message(log_file, "ERROR: Failed to load TTS model")
        log_message(log_file, "Please install TTS: pip install TTS soundfile scipy pydub")
        log_message(log_file, "Note: Ensure PyTorch with CUDA is installed first!")
        sys.exit(1)

    # Process scenes
    log_message(log_file, f"\nProcessing {len(scenes)} scenes...")
    log_message(log_file, f"Estimated time: {len(scenes) * 3 / 60:.1f} hours\n")

    success_count = 0
    error_count = 0

    try:
        for i, scene in enumerate(scenes, start=1):
            log_message(log_file, f"\n--- Scene {i}/{len(scenes)} ---")

            success = process_scene(scene, generator, log_file, args)

            if success:
                success_count += 1
            else:
                error_count += 1

    except KeyboardInterrupt:
        log_message(log_file, "\n\n⚠ Generation interrupted by user")

    finally:
        # Cleanup
        log_message(log_file, "\nCleaning up...")
        generator.unload_model()

        # Final summary
        log_message(log_file, "\n" + "="*80)
        log_message(log_file, "Generation Summary")
        log_message(log_file, "="*80)
        log_message(log_file, f"Total scenes: {len(scenes)}")
        log_message(log_file, f"Successful: {success_count}")
        log_message(log_file, f"Errors: {error_count}")
        log_message(log_file, f"Audio files saved to: {AUDIO_DIR}")
        log_message(log_file, f"Metadata cached to: {AUDIO_CACHE_DIR}")
        log_message(log_file, f"Log saved to: {log_file}")
        log_message(log_file, "="*80)


if __name__ == "__main__":
    main()
