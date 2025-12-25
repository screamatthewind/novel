"""
Main CLI script for generating scene audio from novel chapters.

Parses markdown chapters, extracts scenes, converts dialogue to speech,
and creates multi-voice audio files using Coqui TTS.
"""

import argparse
import os
import sys
import json
from datetime import datetime
from pathlib import Path

from scene_parser import parse_all_chapters, Scene, parse_scene_sentences, Sentence
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


def process_sentence(
    sentence: Sentence,
    generator: CoquiTTSGenerator,
    log_file: str,
    args: argparse.Namespace,
    dry_run: bool = False
) -> bool:
    """
    Process a single sentence: generate audio, save file.

    Args:
        sentence: Sentence object to process
        generator: Initialized Coqui TTS generator
        log_file: Path to log file
        args: Command-line arguments
        dry_run: If True, only show what would be generated without creating audio

    Returns:
        True if successful, False if error occurred
    """
    # Generate filename
    filename = generate_audio_filename(
        sentence.chapter_num,
        sentence.scene_num,
        sentence.content,
        ext=args.audio_format,
        sentence_num=sentence.sentence_num
    )
    output_path = os.path.join(AUDIO_DIR, filename)

    # Log sentence info
    log_message(
        log_file,
        f"\n{'='*80}\nChapter {sentence.chapter_num}, Scene {sentence.scene_num}, Sentence {sentence.sentence_num} ({sentence.word_count} words)"
    )
    log_message(log_file, f"Filename: {filename}")
    log_message(log_file, f"Text: {sentence.content[:100]}{'...' if len(sentence.content) > 100 else ''}")

    if dry_run:
        print(f"\n[DRY RUN] Would generate: {filename}")
        print(f"Text: {sentence.content[:100]}...")
        return True

    # Check if audio already exists
    if os.path.exists(output_path) and not args.skip_cache:
        log_message(log_file, f"⊙ Audio already exists, skipping: {filename}")
        return True

    try:
        # Generate audio for the sentence
        start_time = datetime.now()
        log_message(log_file, f"⟳ Generating audio...")

        # Determine speaker and get voice configuration
        if args.single_voice:
            voice_info = get_voice_for_speaker("narrator")
        else:
            # Parse sentence to detect if it's dialogue and extract speaker
            segments = parse_scene_text(sentence.content)
            if segments and segments[0].segment_type == 'dialogue':
                voice_info = get_voice_for_speaker(segments[0].speaker)
            else:
                voice_info = get_voice_for_speaker("narrator")

        # Generate audio with appropriate voice (file or speaker name)
        if voice_info['type'] == 'file':
            audio = generator.generate_speech_chunked(
                text=sentence.content,
                speaker_wav=voice_info['value'],
                language="en",
                max_chunk_size=MAX_TTS_CHUNK_SIZE
            )
        else:  # type == 'speaker'
            audio = generator.generate_speech_chunked(
                text=sentence.content,
                speaker_name=voice_info['value'],
                language="en",
                max_chunk_size=MAX_TTS_CHUNK_SIZE
            )

        if audio is None:
            log_message(log_file, f"✗ ERROR: Failed to generate audio")
            return False

        # Save audio file
        success = generator.save_audio(audio, output_path)

        if not success:
            log_message(log_file, f"✗ ERROR: Failed to save audio file")
            return False

        # Get duration
        duration = generator.get_audio_duration(audio)

        # Save metadata to cache
        metadata = {
            'chapter': sentence.chapter_num,
            'scene': sentence.scene_num,
            'sentence': sentence.sentence_num,
            'word_count': sentence.word_count,
            'duration_seconds': duration,
            'generated_at': datetime.now().isoformat()
        }
        save_metadata_to_cache(filename, metadata)

        # Log success
        elapsed = (datetime.now() - start_time).total_seconds()
        log_message(
            log_file,
            f"✓ Audio saved: {filename} (duration: {duration:.2f}s, took {elapsed:.1f} seconds)"
        )

        return True

    except Exception as e:
        log_message(log_file, f"✗ ERROR generating audio: {str(e)}")
        import traceback
        log_message(log_file, traceback.format_exc(), print_to_console=False)
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

    log_message(log_file, f"Found {len(scenes)} scenes")

    # Parse scenes into sentences
    log_message(log_file, "Parsing sentences from scenes...")
    all_sentences = []
    for scene in scenes:
        sentences = parse_scene_sentences(scene)
        all_sentences.extend(sentences)

    log_message(log_file, f"Found {len(all_sentences)} sentences to process")

    # Filter sentences if resuming
    if args.resume:
        resume_chapter, resume_scene = args.resume
        all_sentences = [
            s for s in all_sentences
            if (s.chapter_num > resume_chapter) or
               (s.chapter_num == resume_chapter and s.scene_num >= resume_scene)
        ]
        log_message(
            log_file,
            f"Resuming from Chapter {resume_chapter}, Scene {resume_scene} ({len(all_sentences)} sentences)"
        )

    # Dry run mode - just show what would be generated
    if args.dry_run:
        log_message(log_file, "\n=== DRY RUN MODE ===\n")
        for sentence in all_sentences[:10]:  # Show first 10 sentences
            process_sentence(sentence, None, log_file, args, dry_run=True)
        log_message(log_file, f"\nDry run complete. Would generate {len(all_sentences)} audio files.")
        return

    # Load TTS model
    log_message(log_file, "\nLoading Coqui TTS model...")
    generator = CoquiTTSGenerator()

    if not generator.load_model():
        log_message(log_file, "ERROR: Failed to load TTS model")
        log_message(log_file, "Please install Coqui TTS: pip install TTS")
        log_message(log_file, "Note: Ensure PyTorch with CUDA is installed first!")
        sys.exit(1)

    # Process sentences
    log_message(log_file, f"\nProcessing {len(all_sentences)} sentences...")
    log_message(log_file, f"Estimated time: {len(all_sentences) * 0.5 / 60:.1f} hours\n")

    success_count = 0
    error_count = 0

    try:
        for i, sentence in enumerate(all_sentences, start=1):
            log_message(log_file, f"\n--- Sentence {i}/{len(all_sentences)} ---")

            success = process_sentence(sentence, generator, log_file, args)

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
        log_message(log_file, f"Total sentences: {len(all_sentences)}")
        log_message(log_file, f"Successful: {success_count}")
        log_message(log_file, f"Errors: {error_count}")
        log_message(log_file, f"Audio files saved to: {AUDIO_DIR}")
        log_message(log_file, f"Metadata cached to: {AUDIO_CACHE_DIR}")
        log_message(log_file, f"Log saved to: {log_file}")
        log_message(log_file, "="*80)


if __name__ == "__main__":
    main()
