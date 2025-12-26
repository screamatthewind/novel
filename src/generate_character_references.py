"""
Generate high-quality reference portraits for IP-Adapter FaceID system.
Creates 2-3 portraits per character for consistent character appearance across scenes.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from image_generator import SDXLGenerator
from config import DEFAULT_MODEL


# Character reference portrait prompts
CHARACTER_PROMPTS = {
    "emma": {
        "base_prompt": "graphic novel character reference, Asian American woman mid-40s, dark hair, intelligent analytical expression, practical business attire, sensible appearance, competent professional woman, comic book illustration style, clean character design, digital art, sharp lines, professional character concept art",
        "variations": [
            "front view character portrait, neutral expression, professional setting, graphic novel style",
            "three-quarter view, thoughtful expression, soft cel shading, comic book art",
            "character design with slight smile, confident demeanor, clean illustration style"
        ]
    },
    "tyler": {
        "base_prompt": "graphic novel character reference, Asian American teenage boy age 16, casual clothing, slouched posture, intelligent but initially disengaged expression, modern teenager with earbuds, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            "front view character portrait, earbuds visible, neutral expression, graphic novel style",
            "three-quarter view, phone in hand, thoughtful look, cel shading, comic book art",
            "character design with emerging intelligence in eyes, more engaged expression, clean illustration"
        ]
    },
    "elena": {
        "base_prompt": "graphic novel character reference, Russian American woman approximately 60 years old, short gray hair, sharp penetrating eyes that take in everything, slight frame, intellectually rigorous appearance, analytical demeanor, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            "front view character portrait, sharp gaze, neutral background, graphic novel style",
            "three-quarter view, warm beneath analytical exterior, cel shading, comic book art",
            "character design with gentle expression, teaching demeanor, clean illustration"
        ]
    },
    "maxim": {
        "base_prompt": "graphic novel character reference, Russian working-class man mid-40s, hands that know labor, practical working-class appearance, resilient and weathered features, factory worker, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            "front view character portrait, stoic expression, industrial background, graphic novel style",
            "three-quarter view, hands visible showing labor wear, cel shading, comic book art",
            "character design with quietly bitter expression, resilient demeanor, clean illustration"
        ]
    },
    "amara": {
        "base_prompt": "graphic novel character reference, Kenyan woman late 40s to early 50s, former government minister, fierce and pragmatic appearance, professional attire, carries weight of responsibility, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            "front view character portrait, fierce determined expression, graphic novel style",
            "three-quarter view, pragmatic demeanor, professional setting, cel shading, comic book art",
            "character design with channeled anger and purpose in eyes, clean illustration"
        ]
    },
    "wei": {
        "base_prompt": "graphic novel character reference, Chinese man, intellectual strategist appearance, brilliant analytical demeanor, professional business attire, cold analytical expression, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            "front view character portrait, coldly analytical expression, graphic novel style",
            "three-quarter view, suppressing empathy, calculating look, cel shading, comic book art",
            "character design with haunted troubled expression, conscience emerging, clean illustration"
        ]
    }
}

NEGATIVE_PROMPT = "photograph, photo, photorealistic, realistic photo, 3d render, low quality, blurry, distorted face, multiple faces, deformed, ugly, bad anatomy, extra limbs, cropped face, watermark, text, signature"


def load_character_metadata(character_name: str) -> dict:
    """Load character metadata from JSON file."""
    metadata_path = Path(f"../character_references/{character_name}/metadata.json")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found for character: {character_name}")

    with open(metadata_path, 'r') as f:
        return json.load(f)


def save_character_metadata(character_name: str, metadata: dict):
    """Save updated character metadata to JSON file."""
    metadata_path = Path(f"../character_references/{character_name}/metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def generate_character_references(
    character_name: str,
    generator: SDXLGenerator,
    num_variations: int = 2
):
    """
    Generate reference portrait images for a character.

    Args:
        character_name: Name of character (emma, tyler, elena, maxim, amara, wei)
        generator: Initialized SDXLGenerator instance
        num_variations: Number of portrait variations to generate (default: 2)
    """
    if character_name not in CHARACTER_PROMPTS:
        raise ValueError(f"Unknown character: {character_name}. Available: {list(CHARACTER_PROMPTS.keys())}")

    print(f"\n{'='*80}")
    print(f"Generating reference portraits for: {character_name.upper()}")
    print(f"{'='*80}")

    # Load character metadata
    metadata = load_character_metadata(character_name)
    character_dir = Path(f"../character_references/{character_name}")

    # Get character prompts
    char_data = CHARACTER_PROMPTS[character_name]
    base_prompt = char_data["base_prompt"]
    variations = char_data["variations"][:num_variations]

    reference_images = []

    for i, variation in enumerate(variations, 1):
        print(f"\n{'-'*80}")
        print(f"Generating variation {i}/{num_variations}")
        print(f"{'-'*80}")

        # Combine base prompt with variation
        full_prompt = f"{base_prompt}, {variation}"

        print(f"Prompt: {full_prompt[:100]}...")

        # Generate image
        image = generator.generate_image(
            prompt=full_prompt,
            negative_prompt=NEGATIVE_PROMPT,
            width=1024,  # Square for face detection
            height=1024,
            num_inference_steps=40,  # Higher steps for quality
            guidance_scale=7.5,
            seed=42 + i  # Different seed for each variation
        )

        # Save image
        filename = f"{character_name}_ref_{i:02d}.png"
        output_path = character_dir / filename
        image.save(output_path)
        reference_images.append(filename)

        print(f"✓ Saved: {output_path}")

    # Update metadata with reference image filenames
    metadata["reference_images"] = reference_images
    save_character_metadata(character_name, metadata)

    print(f"\n{'='*80}")
    print(f"✓ Generated {len(reference_images)} reference images for {character_name}")
    print(f"✓ Updated metadata: {character_dir / 'metadata.json'}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate character reference portraits for IP-Adapter FaceID"
    )
    parser.add_argument(
        '--characters',
        nargs='+',
        choices=['emma', 'tyler', 'elena', 'maxim', 'amara', 'wei', 'all'],
        default=['all'],
        help='Characters to generate references for (default: all)'
    )
    parser.add_argument(
        '--num-variations',
        type=int,
        default=2,
        help='Number of portrait variations per character (default: 2)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=DEFAULT_MODEL,
        help=f'SDXL model to use (default: {DEFAULT_MODEL})'
    )

    args = parser.parse_args()

    # Determine which characters to generate
    if 'all' in args.characters:
        characters = ['emma', 'tyler', 'elena', 'maxim', 'amara', 'wei']
    else:
        characters = args.characters

    print("\n" + "="*80)
    print("CHARACTER REFERENCE PORTRAIT GENERATOR")
    print("="*80)
    print(f"Characters: {', '.join(characters)}")
    print(f"Variations per character: {args.num_variations}")
    print(f"Model: {args.model}")
    print("="*80 + "\n")

    # Initialize generator
    print("Initializing SDXL generator...")
    generator = SDXLGenerator(model_id=args.model)
    generator.load_model()

    # Generate references for each character
    for character in characters:
        try:
            generate_character_references(
                character_name=character,
                generator=generator,
                num_variations=args.num_variations
            )
        except Exception as e:
            print(f"\n✗ Error generating references for {character}: {e}")
            continue

    print("\n" + "="*80)
    print("✓ CHARACTER REFERENCE GENERATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review generated portraits for quality and accuracy")
    print("2. Manually select best portraits if needed")
    print("3. Delete unwanted variations and update metadata.json")
    print("4. Run image generation with --enable-ip-adapter flag")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
