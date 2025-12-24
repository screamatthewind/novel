"""
SDXL image generator optimized for RTX 3080 10GB GPU.
Handles model loading, memory optimization, and image generation.
"""

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import gc
from config import (
    DEFAULT_MODEL,
    DEVICE,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_STEPS,
    DEFAULT_GUIDANCE
)


class SDXLGenerator:
    """SDXL image generator with RTX 3080 optimizations."""

    def __init__(self, model_id: str = DEFAULT_MODEL):
        """
        Initialize the SDXL generator.

        Args:
            model_id: HuggingFace model ID (default: stabilityai/stable-diffusion-xl-base-1.0)
        """
        self.model_id = model_id
        self.pipe = None
        self.device = DEVICE

    def load_model(self):
        """
        Load SDXL model with memory optimizations for RTX 3080.
        Downloads ~13GB model on first run.
        """
        print(f"Loading SDXL model: {self.model_id}")
        print("Note: First run will download ~13GB model from HuggingFace")

        # Load with fp16 precision for memory efficiency
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        )

        # Move to GPU
        self.pipe = self.pipe.to(self.device)

        # Critical memory optimizations for 10GB VRAM
        print("Applying memory optimizations...")

        # 1. Enable xFormers for flash attention (reduces VRAM significantly)
        try:
            self.pipe.enable_xformers_memory_efficient_attention()
            print("  ✓ xFormers memory efficient attention enabled")
        except Exception as e:
            print(f"  ⚠ Could not enable xFormers: {e}")

        # 2. Enable model CPU offload (moves UNet to CPU when idle)
        self.pipe.enable_model_cpu_offload()
        print("  ✓ Model CPU offload enabled")

        # 3. Enable VAE slicing (process images in slices)
        self.pipe.enable_vae_slicing()
        print("  ✓ VAE slicing enabled")

        # 4. Enable VAE tiling (allows higher resolutions)
        self.pipe.enable_vae_tiling()
        print("  ✓ VAE tiling enabled")

        # 5. Use fast DPM++ scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        print("  ✓ DPM++ scheduler configured")

        print("Model loaded successfully!")
        print(f"Expected VRAM usage: 8-9GB during generation")

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        num_inference_steps: int = DEFAULT_STEPS,
        guidance_scale: float = DEFAULT_GUIDANCE,
        seed: int = 42
    ) -> Image.Image:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of desired image
            negative_prompt: Elements to avoid in the image
            width: Image width in pixels (default: 1344)
            height: Image height in pixels (default: 768)
            num_inference_steps: Number of denoising steps (default: 30)
            guidance_scale: How closely to follow prompt (default: 7.5)
            seed: Random seed for reproducibility (default: 42)

        Returns:
            Generated PIL Image

        Raises:
            RuntimeError: If CUDA OOM occurs
        """
        if self.pipe is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Set random seed for reproducibility
        generator = torch.Generator(device=self.device).manual_seed(seed)

        try:
            # Generate image
            print(f"Generating image ({width}x{height}, {num_inference_steps} steps)...")

            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )

            image = result.images[0]

            # Clean up CUDA memory after generation
            self._cleanup_memory()

            return image

        except RuntimeError as e:
            if "out of memory" in str(e):
                print("\n⚠ CUDA Out of Memory Error!")
                print("Trying with reduced resolution...")

                # Clear memory
                self._cleanup_memory()

                # Retry with 75% resolution
                reduced_width = int(width * 0.75)
                reduced_height = int(height * 0.75)

                # Make dimensions divisible by 8 (required by SDXL)
                reduced_width = (reduced_width // 8) * 8
                reduced_height = (reduced_height // 8) * 8

                print(f"Retrying with {reduced_width}x{reduced_height}...")

                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=reduced_width,
                    height=reduced_height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                )

                image = result.images[0]
                self._cleanup_memory()

                return image
            else:
                raise

    def _cleanup_memory(self):
        """Clean up CUDA memory after generation."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

    def unload_model(self):
        """Unload model and free VRAM."""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            self._cleanup_memory()
            print("Model unloaded, VRAM freed")


def main():
    """Test the SDXL generator."""
    # Test prompt - graphic novel style
    test_prompt = (
        "professional woman in her 40s in factory setting, reading tablet screen, "
        "shocked expression, afternoon sunlight, graphic novel illustration, "
        "comic book art style, detailed line work, dramatic shading, high contrast"
    )

    test_negative = (
        "photorealistic, photo, photograph, 3d render, blurry, low quality, "
        "distorted anatomy, extra limbs, deformed, amateur"
    )

    print("SDXL Generator Test")
    print("=" * 80)
    print(f"\nPrompt: {test_prompt}")
    print(f"\nNegative: {test_negative}")
    print("\n" + "=" * 80 + "\n")

    # Check CUDA availability
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available. This script requires a CUDA-capable GPU.")
        return

    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print()

    # Initialize generator
    generator = SDXLGenerator()

    # Load model
    generator.load_model()

    # Generate test image
    print("\nGenerating test image...")
    print("This will take 5-7 minutes on RTX 3080...")

    image = generator.generate_image(
        prompt=test_prompt,
        negative_prompt=test_negative,
        seed=42
    )

    # Save test image
    output_path = "test_generation.png"
    image.save(output_path)
    print(f"\n✓ Test image saved to: {output_path}")

    # Unload model
    generator.unload_model()

    print("\n" + "=" * 80)
    print("Test complete!")


if __name__ == "__main__":
    main()
