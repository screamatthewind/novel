"""
SDXL image generator optimized for RTX 3080 10GB GPU.
Handles model loading, memory optimization, and image generation.
Supports IP-Adapter FaceID for character consistency.
"""

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import gc
import json
from pathlib import Path
import numpy as np
from config import (
    DEFAULT_MODEL,
    DEVICE,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_STEPS,
    DEFAULT_GUIDANCE,
    CHARACTER_REFERENCES_DIR,
    IP_ADAPTER_MODEL,
    IP_ADAPTER_SUBFOLDER,
    IP_ADAPTER_WEIGHT_NAME,
    IP_ADAPTER_SCALE_DEFAULT,
    FACEID_SCALE_DEFAULT,
    ENABLE_IP_ADAPTER
)


class SDXLGenerator:
    """SDXL image generator with RTX 3080 optimizations and IP-Adapter FaceID support."""

    def __init__(self, model_id: str = DEFAULT_MODEL, enable_ip_adapter: bool = ENABLE_IP_ADAPTER):
        """
        Initialize the SDXL generator.

        Args:
            model_id: HuggingFace model ID (default: stabilityai/stable-diffusion-xl-base-1.0)
            enable_ip_adapter: Enable IP-Adapter FaceID for character consistency (default: False)
        """
        self.model_id = model_id
        self.pipe = None
        self.device = DEVICE
        self.enable_ip_adapter = enable_ip_adapter
        self.ip_adapter_loaded = False
        self.face_encoder = None
        self.character_embeddings_cache = {}  # Cache face embeddings to avoid recomputation

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
        self.pipe.vae.enable_slicing()
        print("  ✓ VAE slicing enabled")

        # 4. Enable VAE tiling (allows higher resolutions)
        self.pipe.vae.enable_tiling()
        print("  ✓ VAE tiling enabled")

        # 5. Use fast DPM++ scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        print("  ✓ DPM++ scheduler configured")

        # 6. Load IP-Adapter if enabled
        if self.enable_ip_adapter:
            self._load_ip_adapter()

        print("Model loaded successfully!")
        if self.enable_ip_adapter:
            print(f"Expected VRAM usage: ~10GB during generation (with IP-Adapter)")
        else:
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

    def _load_ip_adapter(self):
        """
        Load IP-Adapter FaceID models for character consistency.
        Keeps face encoder on CPU to save VRAM, moves to GPU only during encoding.
        """
        try:
            print("\nLoading IP-Adapter FaceID...")

            # Load IP-Adapter for SDXL
            from diffusers import StableDiffusionXLPipeline
            from ip_adapter import IPAdapterFaceIDPlus

            # Create IP-Adapter instance
            self.ip_adapter = IPAdapterFaceIDPlus(
                self.pipe,
                IP_ADAPTER_MODEL,
                IP_ADAPTER_SUBFOLDER,
                IP_ADAPTER_WEIGHT_NAME,
                device=self.device
            )

            print("  ✓ IP-Adapter FaceID loaded")

            # Load InsightFace for face embeddings (keep on CPU to save VRAM)
            from insightface.app import FaceAnalysis

            self.face_encoder = FaceAnalysis(
                name="buffalo_l",
                providers=['CPUExecutionProvider']  # Keep on CPU to save VRAM
            )
            self.face_encoder.prepare(ctx_id=-1)  # -1 = CPU

            print("  ✓ InsightFace face encoder loaded (CPU)")
            print("  ℹ Face encoder kept on CPU to save VRAM")

            self.ip_adapter_loaded = True

        except Exception as e:
            print(f"  ⚠ Failed to load IP-Adapter: {e}")
            print("  ℹ Falling back to standard SDXL generation")
            self.enable_ip_adapter = False
            self.ip_adapter_loaded = False

    def get_character_reference(self, character_name: str) -> dict:
        """
        Load character reference metadata and image path.

        Args:
            character_name: Name of character (emma, tyler, etc.)

        Returns:
            Dictionary with 'image_path', 'ip_adapter_scale', 'faceid_scale'
            Returns None if character reference not found
        """
        try:
            # Load metadata
            metadata_path = Path(CHARACTER_REFERENCES_DIR) / character_name / "metadata.json"
            if not metadata_path.exists():
                print(f"  ⚠ No metadata found for character: {character_name}")
                return None

            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Get first reference image
            if not metadata.get('reference_images'):
                print(f"  ⚠ No reference images for character: {character_name}")
                return None

            image_filename = metadata['reference_images'][0]
            image_path = Path(CHARACTER_REFERENCES_DIR) / character_name / image_filename

            if not image_path.exists():
                print(f"  ⚠ Reference image not found: {image_path}")
                return None

            return {
                'image_path': str(image_path),
                'ip_adapter_scale': metadata.get('ip_adapter_scale', IP_ADAPTER_SCALE_DEFAULT),
                'faceid_scale': metadata.get('faceid_scale', FACEID_SCALE_DEFAULT)
            }

        except Exception as e:
            print(f"  ⚠ Error loading character reference for {character_name}: {e}")
            return None

    def generate_face_embedding(self, reference_image_path: str) -> np.ndarray:
        """
        Generate FaceID embedding from reference image.
        Uses cache to avoid recomputation.

        Args:
            reference_image_path: Path to character reference portrait

        Returns:
            Face embedding as numpy array
        """
        # Check cache first
        if reference_image_path in self.character_embeddings_cache:
            return self.character_embeddings_cache[reference_image_path]

        try:
            # Load image
            image = Image.open(reference_image_path).convert('RGB')
            image_np = np.array(image)

            # Extract face embedding (on CPU)
            faces = self.face_encoder.get(image_np)

            if len(faces) == 0:
                raise ValueError(f"No face detected in reference image: {reference_image_path}")

            # Get embedding from first/largest face
            face_embedding = faces[0].embedding

            # Cache for future use
            self.character_embeddings_cache[reference_image_path] = face_embedding

            return face_embedding

        except Exception as e:
            raise RuntimeError(f"Failed to generate face embedding: {e}")

    def generate_with_character_ref(
        self,
        prompt: str,
        negative_prompt: str,
        character_name: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        num_inference_steps: int = DEFAULT_STEPS,
        guidance_scale: float = DEFAULT_GUIDANCE,
        seed: int = 42,
        ip_adapter_scale: float = None,
        faceid_scale: float = None
    ) -> Image.Image:
        """
        Generate image with character reference for consistency.
        Falls back to standard generation if reference missing or IP-Adapter not loaded.

        Args:
            prompt: Text description of desired image
            negative_prompt: Elements to avoid in the image
            character_name: Name of character to apply consistency to
            width: Image width in pixels
            height: Image height in pixels
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow prompt
            seed: Random seed for reproducibility
            ip_adapter_scale: IP-Adapter influence strength (None = use metadata default)
            faceid_scale: FaceID influence strength (None = use metadata default)

        Returns:
            Generated PIL Image
        """
        # Fallback to standard generation if IP-Adapter not enabled/loaded
        if not self.enable_ip_adapter or not self.ip_adapter_loaded:
            return self.generate_image(
                prompt, negative_prompt, width, height,
                num_inference_steps, guidance_scale, seed
            )

        # Get character reference
        char_ref = self.get_character_reference(character_name)
        if char_ref is None:
            print(f"  ℹ Falling back to standard generation for {character_name}")
            return self.generate_image(
                prompt, negative_prompt, width, height,
                num_inference_steps, guidance_scale, seed
            )

        try:
            print(f"Generating with character reference: {character_name}")

            # Use provided scales or defaults from metadata
            ip_scale = ip_adapter_scale if ip_adapter_scale is not None else char_ref['ip_adapter_scale']
            face_scale = faceid_scale if faceid_scale is not None else char_ref['faceid_scale']

            # Generate face embedding
            face_embedding = self.generate_face_embedding(char_ref['image_path'])

            # Set random seed
            generator = torch.Generator(device=self.device).manual_seed(seed)

            # Generate with IP-Adapter FaceID
            print(f"  ℹ IP-Adapter scale: {ip_scale}, FaceID scale: {face_scale}")

            image = self.ip_adapter.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                faceid_embeds=face_embedding,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                s_scale=ip_scale,
                shortcut=faceid_scale > 0,
                generator=generator
            )[0]

            # Clean up memory
            self._cleanup_memory()

            return image

        except Exception as e:
            print(f"  ⚠ Error generating with character reference: {e}")
            print(f"  ℹ Falling back to standard generation")
            return self.generate_image(
                prompt, negative_prompt, width, height,
                num_inference_steps, guidance_scale, seed
            )

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
