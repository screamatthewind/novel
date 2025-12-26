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
from config import DEFAULT_MODEL, CHARACTER_REFERENCES_DIR


# Character reference portrait prompts
CHARACTER_PROMPTS = {
    "emma": {
        "base_prompt": "graphic novel character reference, Asian American woman mid-40s, dark hair, intelligent analytical expression, practical business attire, sensible appearance, competent professional woman, comic book illustration style, clean character design, digital art, sharp lines, professional character concept art",
        "variations": [
            # Core angles (geometric coverage)
            "front view character portrait, neutral expression, eye level angle, even lighting, graphic novel style",
            "three-quarter view from left, thoughtful expression, 45 degree angle, soft cel shading, comic book art",
            "profile view from left side, neutral expression, 90 degree angle, clean silhouette, graphic novel style",
            "three-quarter view from right, slight smile, 45 degree angle, professional setting, cel shading",
            # Expression/lighting variations
            "front view, analytical concentrated expression, problem-solving demeanor, clean illustration style",
            "three-quarter view, warm professional smile, approachable demeanor, soft lighting, comic book art",
            "front view close-up, dramatic side lighting, highlights intelligence, detailed facial features, graphic novel style",
            "medium close-up, confident competent expression, leadership quality, clean character design"
        ]
    },
    "tyler": {
        "base_prompt": "graphic novel character reference, Asian American teenage boy age 16, casual clothing, slouched posture, intelligent but initially disengaged expression, modern teenager with earbuds, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            # Core angles (geometric coverage)
            "front view character portrait, earbuds visible, neutral expression, eye level angle, graphic novel style",
            "three-quarter view from left, phone in hand, thoughtful look, 45 degree angle, cel shading, comic book art",
            "profile view from left side, earbuds visible, 90 degree angle, clean silhouette, graphic novel style",
            "three-quarter view from right, slight slouch, 45 degree angle, casual setting, cel shading",
            # Expression/lighting variations
            "front view, slightly disengaged expression, typical teenager demeanor, clean illustration style",
            "three-quarter view, emerging intelligence in eyes, more engaged expression, soft lighting, comic book art",
            "front view close-up, dramatic lighting, showing intelligence beneath teenage exterior, graphic novel style",
            "medium close-up, serious thoughtful expression, questioning demeanor, clean character design"
        ]
    },
    "elena": {
        "base_prompt": "graphic novel character reference, Russian American woman approximately 60 years old, short gray hair, sharp penetrating eyes that take in everything, slight frame, intellectually rigorous appearance, analytical demeanor, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            # Core angles (geometric coverage)
            "front view character portrait, sharp penetrating gaze, eye level angle, even lighting, graphic novel style",
            "three-quarter view from left, analytical expression, 45 degree angle, soft cel shading, comic book art",
            "profile view from left side, intellectual demeanor, 90 degree angle, clean silhouette, graphic novel style",
            "three-quarter view from right, thoughtful expression, 45 degree angle, study setting, cel shading",
            # Expression/lighting variations
            "front view, sharp eyes that take in everything at once, intellectually rigorous, clean illustration style",
            "three-quarter view, warm beneath analytical exterior, gentle teaching expression, soft lighting, comic book art",
            "front view close-up, dramatic side lighting, highlights sharp intelligence, detailed facial features, graphic novel style",
            "medium close-up, honest unsentimental expression, mentor demeanor, clean character design"
        ]
    },
    "maxim": {
        "base_prompt": "graphic novel character reference, Russian working-class man mid-40s, hands that know labor, practical working-class appearance, resilient and weathered features, factory worker, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            # Core angles (geometric coverage)
            "front view character portrait, stoic expression, eye level angle, industrial lighting, graphic novel style",
            "three-quarter view from left, hands visible showing labor wear, 45 degree angle, cel shading, comic book art",
            "profile view from left side, weathered resilient features, 90 degree angle, clean silhouette, graphic novel style",
            "three-quarter view from right, practical demeanor, 45 degree angle, working-class setting, cel shading",
            # Expression/lighting variations
            "front view, quietly bitter expression, stoic working-class demeanor, clean illustration style",
            "three-quarter view, resilient determined expression, hands prominent, soft lighting, comic book art",
            "front view close-up, dramatic side lighting, highlights weathered features, detailed facial features, graphic novel style",
            "medium close-up, observant practical expression, bearing witness demeanor, clean character design"
        ]
    },
    "amara": {
        "base_prompt": "graphic novel character reference, Kenyan woman late 40s to early 50s, former government minister, fierce and pragmatic appearance, professional attire, carries weight of responsibility, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            # Core angles (geometric coverage)
            "front view character portrait, fierce determined expression, eye level angle, even lighting, graphic novel style",
            "three-quarter view from left, pragmatic demeanor, 45 degree angle, soft cel shading, comic book art",
            "profile view from left side, carries weight of responsibility, 90 degree angle, clean silhouette, graphic novel style",
            "three-quarter view from right, professional expression, 45 degree angle, ministerial setting, cel shading",
            # Expression/lighting variations
            "front view, fierce determination in eyes, weight of responsibility visible, clean illustration style",
            "three-quarter view, channeled anger into action, purposeful expression, soft lighting, comic book art",
            "front view close-up, dramatic side lighting, highlights fierce pragmatism, detailed facial features, graphic novel style",
            "medium close-up, guilt and determination combined, resistance builder demeanor, clean character design"
        ]
    },
    "wei": {
        "base_prompt": "graphic novel character reference, Chinese man, intellectual strategist appearance, brilliant analytical demeanor, professional business attire, cold analytical expression, comic book illustration style, clean character design, digital art, concept art",
        "variations": [
            # Core angles (geometric coverage)
            "front view character portrait, coldly analytical expression, eye level angle, even lighting, graphic novel style",
            "three-quarter view from left, calculating look, 45 degree angle, soft cel shading, comic book art",
            "profile view from left side, intellectual strategist demeanor, 90 degree angle, clean silhouette, graphic novel style",
            "three-quarter view from right, suppressing empathy, 45 degree angle, professional setting, cel shading",
            # Expression/lighting variations
            "front view, coldly analytical expression, brilliant but emotionless, clean illustration style",
            "three-quarter view, suppressing empathy visible in eyes, calculating demeanor, soft lighting, comic book art",
            "front view close-up, dramatic side lighting, hints of conscience emerging, detailed facial features, graphic novel style",
            "medium close-up, haunted troubled expression, questioning own work, clean character design"
        ]
    }
}

NEGATIVE_PROMPT = "photograph, photo, photorealistic, realistic photo, 3d render, low quality, blurry, distorted face, multiple faces, deformed, ugly, bad anatomy, extra limbs, cropped face, watermark, text, signature"


def load_character_metadata(character_name: str) -> dict:
    """Load character metadata from JSON file."""
    metadata_path = Path(f"{CHARACTER_REFERENCES_DIR}/{character_name}/metadata.json")
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found for character: {character_name}")

    with open(metadata_path, 'r') as f:
        return json.load(f)


def save_character_metadata(character_name: str, metadata: dict):
    """Save updated character metadata to JSON file."""
    metadata_path = Path(f"{CHARACTER_REFERENCES_DIR}/{character_name}/metadata.json")
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
    character_dir = Path(f"{CHARACTER_REFERENCES_DIR}/{character_name}")

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

        print(f"[OK] Saved: {output_path}")

    # Update metadata with reference image filenames
    metadata["reference_images"] = reference_images
    save_character_metadata(character_name, metadata)

    print(f"\n{'='*80}")
    print(f"[OK] Generated {len(reference_images)} reference images for {character_name}")
    print(f"[OK] Updated metadata: {character_dir / 'metadata.json'}")
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
        default=8,
        help='Number of portrait variations per character (default: 8)'
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
            print(f"\n[ERROR] Error generating references for {character}: {e}")
            continue

    print("\n" + "="*80)
    print("[OK] CHARACTER REFERENCE GENERATION COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Review generated portraits for quality and accuracy")
    print("2. Manually select best portraits if needed")
    print("3. Delete unwanted variations and update metadata.json")
    print("4. Run image generation with --enable-ip-adapter flag")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
