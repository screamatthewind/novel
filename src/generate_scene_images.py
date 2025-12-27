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
    generate_prompts_comparison,
    extract_characters,
    generate_storyboard_informed_prompt
)
from config import (
    OUTPUT_DIR,
    LOG_DIR,
    PROMPT_CACHE_DIR,
    DEFAULT_STEPS,
    DEFAULT_GUIDANCE,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    ENABLE_SMART_DETECTION,
    IMAGE_MAPPING_DIR,
    ENABLE_IP_ADAPTER,
    ENABLE_STORYBOARD,
    STORYBOARD_CACHE_DIR,
    STORYBOARD_REPORT_DIR
)
from cost_tracker import CostTracker
from visual_change_detector import VisualChangeDetector
from image_mapping_metadata import ImageMappingMetadata


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
    cost_tracker: CostTracker = None,
    detector: VisualChangeDetector = None,
    current_image_filename: str = None,
    metadata: ImageMappingMetadata = None,
    storyboard_analyzer=None,
    novel_context=None,
    scene_history=None,
    attribute_manager=None
) -> tuple:
    """
    Process a single sentence: generate prompt, create image, save files.

    Args:
        sentence: Sentence object to process
        generator: Initialized SDXL generator
        log_file: Path to log file
        args: Command-line arguments
        dry_run: If True, only generate and display prompts without creating images
        cost_tracker: Cost tracker for API usage
        detector: Visual change detector (for smart detection mode)
        current_image_filename: Current image filename (for reuse)
        metadata: Image mapping metadata tracker
        storyboard_analyzer: StoryboardAnalyzer for storyboard mode (optional)
        novel_context: NovelContext for character descriptions (optional)
        scene_history: SceneVisualHistory for continuity tracking (optional)

    Returns:
        Tuple of (success: bool, image_filename: str)
    """
    # Log sentence info
    log_message(
        log_file,
        f"\n{'='*80}\nChapter {sentence.chapter_num}, Scene {sentence.scene_num}, Sentence {sentence.sentence_num} ({sentence.word_count} words)"
    )
    log_message(log_file, f"Sentence: {sentence.content}")

    # Storyboard analysis (if enabled)
    storyboard_analysis = None
    if storyboard_analyzer:
        # Get character context
        char_context = ""
        if novel_context:
            characters = extract_characters(sentence.content)
            char_context = novel_context.get_all_character_contexts(characters)

        # Get scene continuity context
        scene_continuity = ""
        if scene_history:
            scene_continuity = scene_history.get_continuity_context(manager=attribute_manager)

        # Analyze sentence with storyboard
        storyboard_analysis = storyboard_analyzer.analyze_sentence(
            sentence,
            character_context=char_context,
            scene_continuity=scene_continuity
        )

        # Apply attribute changes to manager (if detected)
        if attribute_manager and storyboard_analysis.attribute_changes:
            storyboard_analyzer.apply_attribute_changes_to_manager(
                storyboard_analysis,
                attribute_manager,
                sentence.sentence_num
            )

        # Update scene history with manager
        if scene_history:
            scene_history.update_from_storyboard(storyboard_analysis, manager=attribute_manager)

    # Smart detection: Check if new image is needed
    needs_new_image = True
    detection_reason = "generation_mode"
    image_filename = None

    if storyboard_analysis and detector and current_image_filename and not dry_run:
        # Use storyboard-enhanced detection
        needs_new_image, detection_reason = detector.analyze_with_storyboard(sentence, storyboard_analysis)

        if not needs_new_image:
            # Reuse current image
            image_filename = current_image_filename
            log_message(log_file, f"✓ Reusing image: {image_filename} ({detection_reason})")
        else:
            log_message(log_file, f"-> New image needed: {detection_reason}")
            detector.update_storyboard_state(storyboard_analysis)

    elif detector and current_image_filename and not dry_run:
        # Analyze visual state (non-storyboard mode)
        visual_state = detector.analyze_sentence(sentence)
        needs_new_image, detection_reason = detector.needs_new_image(visual_state)

        if not needs_new_image:
            # Reuse current image
            image_filename = current_image_filename
            log_message(log_file, f"✓ Reusing image: {image_filename} ({detection_reason})")
        else:
            log_message(log_file, f"-> New image needed: {detection_reason}")
            detector.update_state(visual_state)

    # Generate filename (same for all methods)
    # This is the audio filename - always generated per sentence
    audio_filename = generate_filename(
        sentence.chapter_num,
        sentence.scene_num,
        sentence.content,
        sentence.sentence_num,
        scene_context=sentence.scene_context
    )

    # Image filename - only generate if needed
    if needs_new_image:
        image_filename = audio_filename  # Same name when generating new image

    # Record mapping in metadata if tracker provided
    if metadata and image_filename:
        # Convert to .wav for audio filename in metadata
        audio_file_for_metadata = audio_filename.replace('.png', '.wav')
        metadata.add_mapping(
            audio_file=audio_file_for_metadata,
            image_file=image_filename,
            sentence_num=sentence.sentence_num,
            scene_num=sentence.scene_num,
            reason=detection_reason
        )

    # For backward compatibility, use image_filename as "filename" variable
    filename = image_filename

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
        return (True, filename)

    # Single method: generate prompt with specified method
    if storyboard_analysis:
        # Use storyboard-informed prompt generation
        log_message(log_file, "Mode: STORYBOARD")
        prompt = generate_storyboard_informed_prompt(
            sentence.content,
            storyboard_analysis,
            scene_context=sentence.scene_context,
            attribute_manager=attribute_manager
        )
    elif args.llm in ["ollama", "haiku"]:
        log_message(log_file, f"Mode: LLM ({args.llm})")
        prompt, input_tokens, output_tokens = generate_prompt_with_llm(
            sentence.content,
            scene_context=sentence.scene_context,
            method=args.llm,
            cost_tracker=cost_tracker
        )
        if not prompt:
            log_message(log_file, f"Failed to generate prompt with {args.llm}, falling back to keyword method")
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

    # Detect character and use IP-Adapter if enabled (before dry-run check so we can verify)
    character_name = None
    if generator and generator.enable_ip_adapter and generator.ip_adapter_loaded:
            # Map character full names to short names for metadata lookup
            char_mapping = {
                'emma': 'emma', 'emma chen': 'emma',
                'tyler': 'tyler', 'tyler chen': 'tyler',
                'elena': 'elena', 'elena volkov': 'elena',
                'maxim': 'maxim', 'maxim orlov': 'maxim',
                'amara': 'amara', 'amara okafor': 'amara',
                'wei': 'wei', 'wei chen': 'wei'
            }

            # Try storyboard analysis first (more reliable than keyword extraction)
            characters = []
            if storyboard_analysis and storyboard_analysis.characters_present:
                # Extract characters from storyboard analysis
                storyboard_chars = storyboard_analysis.characters_present
                log_message(log_file, f"-> Storyboard characters: {storyboard_chars}")

                # Map full names to short names
                for char in storyboard_chars:
                    char_lower = char.lower()
                    if char_lower in char_mapping:
                        characters.append(char_mapping[char_lower])

                # Prioritize "acting" characters over "referenced" ones
                if characters and storyboard_analysis.character_roles:
                    acting_chars = [
                        char for char in characters
                        if any(
                            role in ['acting', 'acting/speaking', 'acting/listening']
                            for name, role in storyboard_analysis.character_roles.items()
                            if name.lower() in char_mapping and char_mapping[name.lower()] == char
                        )
                    ]
                    if acting_chars:
                        character_name = acting_chars[0]  # Use first acting character
                    else:
                        character_name = characters[0]  # Fall back to first character
                elif characters:
                    character_name = characters[0]

            # Fallback: Extract characters from sentence text (original method)
            if not character_name:
                characters = extract_characters(sentence.content)
                for char in characters:
                    if char in char_mapping:
                        character_name = char_mapping[char]
                        break

    # Log character detection result
    if character_name:
        log_message(log_file, f"-> Using character reference: {character_name}")

    # Check for dry-run mode
    if dry_run:
        print(f"\n[DRY RUN] Would generate: {filename}")
        print(f"Prompt: {prompt[:100]}...")
        return (True, filename)

    # If reusing image, skip generation
    if not needs_new_image:
        return (True, image_filename)

    # Check if image already exists
    output_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(output_path):
        log_message(log_file, f"⊙ Image already exists, skipping: {filename}")
        return (True, filename)

    try:
        # Generate image
        start_time = datetime.now()
        log_message(log_file, f">> Generating image...")

        # Calculate seed based on chapter, scene, and sentence for variety
        seed = 42 + (sentence.chapter_num * 1000) + (sentence.scene_num * 100) + sentence.sentence_num

        # Generate image with or without character reference
        if character_name:
            image = generator.generate_with_character_ref(
                prompt=prompt,
                negative_prompt=negative_prompt,
                character_name=character_name,
                width=args.width,
                height=args.height,
                num_inference_steps=args.steps,
                guidance_scale=args.guidance,
                seed=seed
            )
        else:
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

        return (True, filename)

    except Exception as e:
        log_message(log_file, f"ERROR generating image: {str(e)}")
        # Save prompt anyway for manual retry
        method_suffix = f"_{args.llm.upper()}" if args.llm != "keyword" else ""
        save_prompt_to_cache(filename, prompt, negative_prompt, method_suffix=method_suffix)
        return (False, filename)


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

    parser.add_argument(
        '--enable-smart-detection',
        action='store_true',
        default=ENABLE_SMART_DETECTION,
        help='Enable smart visual change detection to reduce image generation'
    )

    parser.add_argument(
        '--enable-ip-adapter',
        action='store_true',
        default=ENABLE_IP_ADAPTER,
        help='Enable IP-Adapter FaceID for character consistency'
    )

    parser.add_argument(
        '--enable-storyboard',
        action='store_true',
        default=ENABLE_STORYBOARD,
        help='Enable storyboard analysis for enhanced visual planning'
    )

    parser.add_argument(
        '--storyboard-cache-dir',
        type=str,
        help='Directory for storyboard analysis cache (default: from config)'
    )

    parser.add_argument(
        '--rebuild-storyboard',
        action='store_true',
        help='Force rebuild of storyboard cache and delete existing images for specified chapters'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear storyboard cache and images for specified chapters, then exit (no generation)'
    )

    args = parser.parse_args()

    # Handle --clear-cache mode (early exit, no image generation)
    if args.clear_cache:
        from storyboard_analyzer import StoryboardAnalyzer

        print("="*80)
        print("Cache Clearing Mode")
        print("="*80)

        if not args.chapters:
            print("ERROR: --clear-cache requires --chapters to specify which chapters to clear")
            sys.exit(1)

        cache_dir = args.storyboard_cache_dir if args.storyboard_cache_dir else STORYBOARD_CACHE_DIR
        analyzer = StoryboardAnalyzer(
            cache_dir=cache_dir,
            rebuild_cache=False,  # Not rebuilding, just clearing
            images_dir=OUTPUT_DIR
        )

        print(f"\nClearing cache and images for chapters: {args.chapters}")
        total_cache = 0
        total_images = 0

        for chapter_num in args.chapters:
            cache_deleted, images_deleted = analyzer.delete_chapter_cache_and_images(chapter_num)
            total_cache += cache_deleted
            total_images += images_deleted
            print(f"  Chapter {chapter_num}: Deleted {cache_deleted} cache files, {images_deleted} image files")

        print(f"\nTotal: {total_cache} cache files, {total_images} image files deleted")
        print("="*80)
        sys.exit(0)

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
    # If only one chapter specified, process only first scene
    first_scene_only = args.chapters is not None and len(args.chapters) == 1
    scenes = parse_all_chapters(chapter_numbers=args.chapters, first_scene_only=first_scene_only)

    if first_scene_only and scenes:
        log_message(log_file, f"Single chapter mode: Processing first scene only")

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
            # Initialize detector and metadata for dry run
            detector = VisualChangeDetector() if args.enable_smart_detection else None
            metadata = ImageMappingMetadata(chapter_num=1)
            current_image = None

            # Initialize storyboard analyzer if enabled
            storyboard_analyzer = None
            novel_context = None
            scene_history = None
            if args.enable_storyboard:
                from storyboard_analyzer import StoryboardAnalyzer, SceneVisualHistory
                from novel_context import NovelContext

                log_message(log_file, "Initializing storyboard analysis...")
                cache_dir = args.storyboard_cache_dir if args.storyboard_cache_dir else STORYBOARD_CACHE_DIR
                storyboard_analyzer = StoryboardAnalyzer(
                    cache_dir=cache_dir,
                    rebuild_cache=args.rebuild_storyboard,
                    images_dir=OUTPUT_DIR
                )
                novel_context = NovelContext()
                scene_history = SceneVisualHistory()
                log_message(log_file, "-> Storyboard analysis enabled")

                # If rebuilding cache, delete cache and images for specified chapters
                if args.rebuild_storyboard and args.chapters:
                    log_message(log_file, "Rebuild mode: Deleting storyboard cache and images for specified chapters...")
                    for chapter_num in args.chapters:
                        cache_deleted, images_deleted = storyboard_analyzer.delete_chapter_cache_and_images(chapter_num)
                        log_message(log_file, f"  Chapter {chapter_num}: Deleted {cache_deleted} cache files, {images_deleted} image files")
                    log_message(log_file, "-> Cache and images cleared")

            for sentence in all_sentences[:10]:  # Show first 10 sentences
                success, image_file = process_sentence(
                    sentence, None, log_file, args, dry_run=True,
                    cost_tracker=cost_tracker, detector=detector,
                    current_image_filename=current_image, metadata=metadata,
                    storyboard_analyzer=storyboard_analyzer,
                    novel_context=novel_context,
                    scene_history=scene_history
                )
                if success and image_file:
                    current_image = image_file

            log_message(log_file, f"\nDry run complete. Would generate {len(all_sentences)} images.")

            # Print smart detection stats if enabled
            if args.enable_smart_detection and metadata:
                metadata.print_statistics()

            # Print cost summary if haiku was used
            if args.llm in ["haiku", "compare"] and cost_tracker.session_api_calls > 0:
                cost_tracker.print_summary()

            # Print storyboard analysis cost summary if enabled
            if args.enable_storyboard and storyboard_analyzer:
                total_cost, cost_report = storyboard_analyzer.get_cost_estimate()
                log_message(log_file, "\n" + "="*80)
                log_message(log_file, cost_report)
                log_message(log_file, "="*80)

        return

    # Load SDXL model
    log_message(log_file, "\nLoading SDXL model...")
    from image_generator import SDXLGenerator
    generator = SDXLGenerator(enable_ip_adapter=args.enable_ip_adapter)
    generator.load_model()

    # Log IP-Adapter status
    if args.enable_ip_adapter:
        if generator.ip_adapter_loaded:
            log_message(log_file, "IP-Adapter: ENABLED (character consistency active)")
        else:
            log_message(log_file, "IP-Adapter: FAILED TO LOAD (falling back to standard generation)")

    # Create cost tracker for this session
    session_name = f"generate_images_chapters_{'_'.join(map(str, args.chapters)) if args.chapters else 'all'}"
    with CostTracker(session_name) as cost_tracker:
        # Process sentences
        log_message(log_file, f"\nProcessing {len(all_sentences)} sentences...")
        if args.enable_smart_detection:
            log_message(log_file, "Smart detection: ENABLED")
        if args.enable_storyboard:
            log_message(log_file, "Storyboard analysis: ENABLED")
        if not args.enable_smart_detection and not args.enable_storyboard:
            log_message(log_file, f"Estimated time: {len(all_sentences) * 6 / 60:.1f} hours\n")

        success_count = 0
        error_count = 0

        # Initialize detector and metadata trackers per chapter
        detector_by_chapter = {}
        metadata_by_chapter = {}
        current_image_by_chapter = {}

        # Initialize storyboard components if enabled
        storyboard_analyzer = None
        novel_context = None
        scene_history_by_chapter = {}
        attribute_manager_by_chapter = {}  # Track attribute state per chapter

        if args.enable_storyboard:
            from storyboard_analyzer import StoryboardAnalyzer, SceneVisualHistory
            from novel_context import NovelContext
            from attribute_state_manager import AttributeStateManager

            log_message(log_file, "Initializing storyboard analysis...")
            cache_dir = args.storyboard_cache_dir if args.storyboard_cache_dir else STORYBOARD_CACHE_DIR

            # If rebuilding cache, delete cache and images FIRST before creating analyzer
            if args.rebuild_storyboard and args.chapters:
                log_message(log_file, "Rebuild mode: Deleting storyboard cache and images for specified chapters...")
                temp_analyzer = StoryboardAnalyzer(
                    cache_dir=cache_dir,
                    rebuild_cache=False,
                    images_dir=OUTPUT_DIR
                )
                for chapter_num in args.chapters:
                    cache_deleted, images_deleted = temp_analyzer.delete_chapter_cache_and_images(chapter_num)
                    log_message(log_file, f"  Chapter {chapter_num}: Deleted {cache_deleted} cache files, {images_deleted} image files")
                log_message(log_file, "-> Cache and images cleared")

            storyboard_analyzer = StoryboardAnalyzer(
                cache_dir=cache_dir,
                rebuild_cache=args.rebuild_storyboard,
                images_dir=OUTPUT_DIR
            )
            novel_context = NovelContext()
            log_message(log_file, "-> Storyboard analyzer ready")

        # Group sentences by chapter for metadata tracking
        chapters_processed = set()

        try:
            for i, sentence in enumerate(all_sentences, start=1):
                log_message(log_file, f"\n--- Sentence {i}/{len(all_sentences)} ---")

                chapter_num = sentence.chapter_num
                scene_num = sentence.scene_num

                # Initialize detector/metadata for this chapter if needed
                if chapter_num not in detector_by_chapter:
                    if args.enable_smart_detection or args.enable_storyboard:
                        detector_by_chapter[chapter_num] = VisualChangeDetector()
                        metadata_by_chapter[chapter_num] = ImageMappingMetadata(chapter_num)
                        current_image_by_chapter[chapter_num] = None
                        log_message(log_file, f"-> Initialized detection for Chapter {chapter_num}")

                    if args.enable_storyboard:
                        from storyboard_analyzer import SceneVisualHistory
                        from attribute_state_manager import AttributeStateManager
                        scene_history_by_chapter[chapter_num] = SceneVisualHistory()
                        attribute_manager_by_chapter[chapter_num] = AttributeStateManager(chapter_num)
                        log_message(log_file, f"-> Initialized attribute manager for Chapter {chapter_num}")

                # Get detector/metadata for this chapter
                detector = detector_by_chapter.get(chapter_num) if (args.enable_smart_detection or args.enable_storyboard) else None
                metadata = metadata_by_chapter.get(chapter_num) if (args.enable_smart_detection or args.enable_storyboard) else None
                current_image = current_image_by_chapter.get(chapter_num)
                scene_history = scene_history_by_chapter.get(chapter_num) if args.enable_storyboard else None
                attribute_manager = attribute_manager_by_chapter.get(chapter_num) if args.enable_storyboard else None

                # Process sentence
                success, image_file = process_sentence(
                    sentence, generator, log_file, args,
                    cost_tracker=cost_tracker, detector=detector,
                    current_image_filename=current_image, metadata=metadata,
                    storyboard_analyzer=storyboard_analyzer,
                    novel_context=novel_context,
                    scene_history=scene_history,
                    attribute_manager=attribute_manager
                )

                if success:
                    success_count += 1
                    # Update current image for this chapter
                    if image_file:
                        current_image_by_chapter[chapter_num] = image_file
                else:
                    error_count += 1

                chapters_processed.add(chapter_num)

        except KeyboardInterrupt:
            log_message(log_file, "\n\n⚠ Generation interrupted by user")

        finally:
            # Save metadata files for each chapter processed
            if args.enable_smart_detection and metadata_by_chapter:
                log_message(log_file, "\nSaving image mapping metadata...")
                for chapter_num, metadata in metadata_by_chapter.items():
                    if metadata:
                        filepath = metadata.save(IMAGE_MAPPING_DIR)
                        log_message(log_file, f"  ✓ Saved metadata for Chapter {chapter_num}: {filepath}")
                        # Print statistics for this chapter
                        metadata.print_statistics()

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

            if args.enable_smart_detection:
                log_message(log_file, f"Metadata saved to: {IMAGE_MAPPING_DIR}")

            log_message(log_file, f"Log saved to: {log_file}")
            log_message(log_file, "="*80)

            # Print cost summary if haiku was used
            if args.llm in ["haiku", "compare"] and cost_tracker.session_api_calls > 0:
                cost_tracker.print_summary()

            # Print storyboard analysis cost summary if enabled
            if args.enable_storyboard and storyboard_analyzer:
                total_cost, cost_report = storyboard_analyzer.get_cost_estimate()
                log_message(log_file, "\n" + "="*80)
                log_message(log_file, cost_report)
                log_message(log_file, "="*80)

            # Print attribute change statistics if storyboard enabled
            if args.enable_storyboard and attribute_manager_by_chapter:
                log_message(log_file, "\n" + "="*80)
                log_message(log_file, "Attribute Change Statistics")
                log_message(log_file, "="*80)
                for chapter_num in sorted(attribute_manager_by_chapter.keys()):
                    manager = attribute_manager_by_chapter[chapter_num]
                    stats = manager.get_statistics()
                    log_message(log_file, f"\nChapter {chapter_num}:")
                    log_message(log_file, f"  Total changes: {stats['total_changes']}")
                    log_message(log_file, f"  Characters tracked: {stats['characters_tracked']}")
                    if stats['total_changes'] > 0:
                        log_message(log_file, f"  Changes by character: {stats['changes_by_character']}")
                        log_message(log_file, f"  Changes by type: {stats['changes_by_type']}")
                log_message(log_file, "="*80)


if __name__ == "__main__":
    main()
