"""
Main CLI script for generating scene images from novel chapters.

Parses markdown chapters, extracts scenes, generates SDXL prompts,
and creates photorealistic images optimized for RTX 3080.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from scene_parser import parse_all_chapters, Scene, parse_scene_sentences, Sentence
from prompt_generator import (
    generate_prompt,
    generate_filename,
    get_negative_prompt,
    generate_prompt_with_llm,
    generate_prompts_comparison
)
from config import (
    OUTPUT_DIR,
    LOG_DIR,
    PROMPT_CACHE_DIR,
    DEFAULT_STEPS,
    DEFAULT_GUIDANCE,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT
)
from cost_tracker import CostTracker


def setup_logging() -> str:
    """
    Setup logging file for this generation run.

    Returns:
        Path to log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"generation_{timestamp}.log")
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
        print(message)


def save_prompt_to_cache(filename: str, prompt: str, negative_prompt: str, method_suffix: str = ""):
    """
    Save prompt to cache file for future reference.

    Args:
        filename: Image filename (e.g., 'chapter_01_scene_02_emma_factory.png')
        prompt: Positive prompt
        negative_prompt: Negative prompt
        method_suffix: Optional suffix to add before .txt (e.g., "_OLLAMA", "_HAIKU", "_KEYWORD")
    """
    # Create cache filename (replace .png with method suffix + .txt)
    cache_filename = filename.replace('.png', f'{method_suffix}.txt')
    cache_path = os.path.join(PROMPT_CACHE_DIR, cache_filename)

    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write("PROMPT:\n")
        f.write(prompt)
        f.write("\n\n")
        f.write("NEGATIVE PROMPT:\n")
        f.write(negative_prompt)


def process_sentence(
    sentence: Sentence,
    generator,  # SDXLGenerator or None for dry-run
    log_file: str,
    args: argparse.Namespace,
    dry_run: bool = False,
    cost_tracker: CostTracker = None
) -> bool:
    """
    Process a single sentence: generate prompt, create image, save files.

    Args:
        sentence: Sentence object to process
        generator: Initialized SDXL generator
        log_file: Path to log file
        args: Command-line arguments
        dry_run: If True, only generate and display prompts without creating images

    Returns:
        True if successful, False if error occurred
    """
    # Log sentence info
    log_message(
        log_file,
        f"\n{'='*80}\nChapter {sentence.chapter_num}, Scene {sentence.scene_num}, Sentence {sentence.sentence_num} ({sentence.word_count} words)"
    )
    log_message(log_file, f"Sentence: {sentence.content}")

    # Generate filename (same for all methods)
    filename = generate_filename(
        sentence.chapter_num,
        sentence.scene_num,
        sentence.content,
        sentence.sentence_num,
        scene_context=sentence.scene_context
    )

    # Handle comparison mode - generate prompts with all methods
    if args.llm == "compare":
        log_message(log_file, "Mode: COMPARISON (keyword, ollama, haiku)")
        prompts = generate_prompts_comparison(sentence.content, scene_context=sentence.scene_context, cost_tracker=cost_tracker)
        negative_prompt = get_negative_prompt()

        # Save all prompts to cache
        for method, prompt in prompts.items():
            if method == "tokens":
                continue  # Skip tokens dict
            if prompt:
                suffix = f"_{method.upper()}"
                save_prompt_to_cache(filename, prompt, negative_prompt, method_suffix=suffix)
                log_message(log_file, f"[{method.upper()}] Prompt: {prompt}")
            else:
                log_message(log_file, f"[{method.upper()}] Failed to generate prompt")

        # Log token usage if haiku was used
        if "tokens" in prompts and prompts["tokens"]["input"] > 0:
            log_message(log_file, f"[HAIKU] Tokens: {prompts['tokens']['input']} in / {prompts['tokens']['output']} out")

        log_message(log_file, f"✓ Comparison prompts saved for: {filename}")
        return True

    # Single method: generate prompt with specified method
    if args.llm in ["ollama", "haiku"]:
        log_message(log_file, f"Mode: LLM ({args.llm})")
        prompt, input_tokens, output_tokens = generate_prompt_with_llm(
            sentence.content,
            scene_context=sentence.scene_context,
            method=args.llm,
            cost_tracker=cost_tracker
        )
        if not prompt:
            log_message(log_file, f"✗ Failed to generate prompt with {args.llm}, falling back to keyword method")
            prompt = generate_prompt(sentence.content, scene_context=sentence.scene_context)
        elif args.llm == "haiku" and input_tokens > 0:
            log_message(log_file, f"Tokens: {input_tokens} in / {output_tokens} out")
    else:
        # Default: keyword-based
        log_message(log_file, "Mode: KEYWORD")
        prompt = generate_prompt(sentence.content, scene_context=sentence.scene_context)

    negative_prompt = get_negative_prompt()
    log_message(log_file, f"Filename: {filename}")
    log_message(log_file, f"Prompt: {prompt}")

    if dry_run:
        print(f"\n[DRY RUN] Would generate: {filename}")
        print(f"Prompt: {prompt[:100]}...")
        return True

    # Check if image already exists
    output_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(output_path):
        log_message(log_file, f"⊙ Image already exists, skipping: {filename}")
        return True

    try:
        # Generate image
        start_time = datetime.now()
        log_message(log_file, f"⟳ Generating image...")

        # Calculate seed based on chapter, scene, and sentence for variety
        seed = 42 + (sentence.chapter_num * 1000) + (sentence.scene_num * 100) + sentence.sentence_num

        image = generator.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=args.width,
            height=args.height,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance,
            seed=seed
        )

        # Save image
        image.save(output_path)

        # Save prompt to cache
        method_suffix = f"_{args.llm.upper()}" if args.llm != "keyword" else ""
        save_prompt_to_cache(filename, prompt, negative_prompt, method_suffix=method_suffix)

        # Log success
        elapsed = (datetime.now() - start_time).total_seconds()
        log_message(
            log_file,
            f"✓ Image saved: {filename} (took {elapsed/60:.1f} minutes)"
        )

        return True

    except Exception as e:
        log_message(log_file, f"✗ ERROR generating image: {str(e)}")
        # Save prompt anyway for manual retry
        method_suffix = f"_{args.llm.upper()}" if args.llm != "keyword" else ""
        save_prompt_to_cache(filename, prompt, negative_prompt, method_suffix=method_suffix)
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate scene images from novel chapters using SDXL"
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
        help='Show prompts without generating images'
    )

    parser.add_argument(
        '--llm',
        type=str,
        choices=['keyword', 'ollama', 'haiku', 'compare'],
        default='keyword',
        help='Prompt generation method: keyword (default), ollama (local LLM), haiku (Claude API), compare (all three)'
    )

    parser.add_argument(
        '--steps',
        type=int,
        default=DEFAULT_STEPS,
        help=f'Number of inference steps (default: {DEFAULT_STEPS})'
    )

    parser.add_argument(
        '--guidance',
        type=float,
        default=DEFAULT_GUIDANCE,
        help=f'Guidance scale (default: {DEFAULT_GUIDANCE})'
    )

    parser.add_argument(
        '--width',
        type=int,
        default=DEFAULT_WIDTH,
        help=f'Image width (default: {DEFAULT_WIDTH})'
    )

    parser.add_argument(
        '--height',
        type=int,
        default=DEFAULT_HEIGHT,
        help=f'Image height (default: {DEFAULT_HEIGHT})'
    )

    args = parser.parse_args()

    # Setup logging
    log_file = setup_logging()
    log_message(log_file, "="*80)
    log_message(log_file, "Novel Scene Image Generation")
    log_message(log_file, "="*80)

    # Check CUDA availability
    if not args.dry_run:
        try:
            import torch
        except ImportError:
            log_message(log_file, "ERROR: PyTorch not installed. Please run: pip install -r requirements.txt")
            sys.exit(1)

        if not torch.cuda.is_available():
            log_message(log_file, "ERROR: CUDA not available. This script requires a CUDA-capable GPU.")
            sys.exit(1)

        log_message(log_file, f"GPU: {torch.cuda.get_device_name(0)}")
        log_message(log_file, f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

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

    # Dry run mode - just show prompts
    if args.dry_run:
        log_message(log_file, "\n=== DRY RUN MODE ===\n")

        # Create cost tracker for dry run (if using haiku)
        session_name = f"dry_run_chapters_{'_'.join(map(str, args.chapters)) if args.chapters else 'all'}"
        with CostTracker(session_name) as cost_tracker:
            for sentence in all_sentences[:10]:  # Show first 10 sentences
                process_sentence(sentence, None, log_file, args, dry_run=True, cost_tracker=cost_tracker)

            log_message(log_file, f"\nDry run complete. Would generate {len(all_sentences)} images.")

            # Print cost summary if haiku was used
            if args.llm in ["haiku", "compare"] and cost_tracker.session_api_calls > 0:
                cost_tracker.print_summary()

        return

    # Load SDXL model
    log_message(log_file, "\nLoading SDXL model...")
    from image_generator import SDXLGenerator
    generator = SDXLGenerator()
    generator.load_model()

    # Create cost tracker for this session
    session_name = f"generate_images_chapters_{'_'.join(map(str, args.chapters)) if args.chapters else 'all'}"
    with CostTracker(session_name) as cost_tracker:
        # Process sentences
        log_message(log_file, f"\nProcessing {len(all_sentences)} sentences...")
        log_message(log_file, f"Estimated time: {len(all_sentences) * 6 / 60:.1f} hours\n")

        success_count = 0
        error_count = 0

        try:
            for i, sentence in enumerate(all_sentences, start=1):
                log_message(log_file, f"\n--- Sentence {i}/{len(all_sentences)} ---")

                success = process_sentence(sentence, generator, log_file, args, cost_tracker=cost_tracker)

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
            log_message(log_file, f"Images saved to: {OUTPUT_DIR}")
            log_message(log_file, f"Prompts cached to: {PROMPT_CACHE_DIR}")
            log_message(log_file, f"Log saved to: {log_file}")
            log_message(log_file, "="*80)

            # Print cost summary if haiku was used
            if args.llm in ["haiku", "compare"] and cost_tracker.session_api_calls > 0:
                cost_tracker.print_summary()


if __name__ == "__main__":
    main()
