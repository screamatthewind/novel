"""
Audio generator using Coqui TTS for multi-voice narration.
Handles TTS model loading, speech generation, and GPU memory management.
"""

import numpy as np
import torch
import soundfile as sf
from typing import Optional, List
import os
import gc
from pathlib import Path
from dotenv import load_dotenv

from config import DEFAULT_TTS_MODEL, DEFAULT_SAMPLE_RATE, DEVICE

# Load environment variables from .env file
# Look for .env in project root (parent of src directory)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


def check_cuda_availability() -> tuple[bool, str]:
    """
    Check CUDA availability with detailed diagnostics.

    Returns:
        Tuple of (is_available, diagnostic_message)
    """
    if not torch.cuda.is_available():
        # Determine why CUDA is not available
        if not hasattr(torch.version, 'cuda') or torch.version.cuda is None:
            return False, (
                "PyTorch installed without CUDA support. "
                "Reinstall with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
            )
        else:
            return False, (
                f"CUDA drivers not detected or incompatible. "
                f"PyTorch CUDA version: {torch.version.cuda}. "
                f"Check NVIDIA drivers are installed and compatible."
            )

    # CUDA is available
    device_name = torch.cuda.get_device_name(0)
    cuda_version = torch.version.cuda if hasattr(torch.version, 'cuda') else "Unknown"
    return True, f"CUDA detected: {device_name} (CUDA {cuda_version})"


class CoquiTTSGenerator:
    """
    Wrapper for Coqui TTS models.
    Manages model loading, speech generation, and memory cleanup.
    """

    def __init__(self, model_name: str = DEFAULT_TTS_MODEL, device: str = DEVICE):
        """
        Initialize TTS generator.

        Args:
            model_name: TTS model identifier (e.g., 'tts_models/en/vctk/vits' or 'tts_models/multilingual/multi-dataset/xtts_v2')
            device: Device to use ('cuda' or 'cpu')
        """
        self.model_name = model_name
        self.model = None
        self.sample_rate = DEFAULT_SAMPLE_RATE
        self.latent_cache = {}  # Cache for speaker latents (voice cloning)

        # Detect CUDA with diagnostics
        cuda_available, diagnostic_msg = check_cuda_availability()

        if device == "cuda" and not cuda_available:
            print("\n" + "="*70)
            print("WARNING: CUDA requested but not available")
            print("="*70)
            print(f"Reason: {diagnostic_msg}")
            print("Falling back to CPU (generation will be MUCH slower)")
            print("="*70 + "\n")
            self.device = "cpu"
        elif device == "cuda" and cuda_available:
            print(f"\n{diagnostic_msg}")
            self.device = "cuda"
        else:
            # User explicitly requested CPU or other device
            self.device = device
            if device == "cpu":
                print("Using CPU (generation will be slower)")

    def load_model(self) -> bool:
        """
        Load the TTS model into memory.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Patch TTS library to use weights_only=False for PyTorch 2.6+
            import TTS.utils.io
            original_load = TTS.utils.io.torch.load
            def patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return original_load(*args, **kwargs)
            TTS.utils.io.torch.load = patched_load

            from TTS.api import TTS
            import warnings

            # Suppress MeCab warnings for English-only usage
            warnings.filterwarnings('ignore', message='.*MeCab.*')
            warnings.filterwarnings('ignore', message='.*mecab.*')

            print(f"\nLoading TTS model: {self.model_name}")
            print(f"Target device: {self.device}")

            # Initialize TTS model
            self.model = TTS(self.model_name).to(self.device)

            # Verify model is on expected device
            if hasattr(self.model, 'synthesizer') and hasattr(self.model.synthesizer, 'tts_model'):
                model_device = next(self.model.synthesizer.tts_model.parameters()).device
                print(f"Model device: {model_device}")
                if str(model_device) != self.device and not (self.device == "cuda" and "cuda" in str(model_device)):
                    print(f"WARNING: Model on {model_device} but expected {self.device}")

            # Get actual sample rate from model config
            if hasattr(self.model, 'synthesizer') and hasattr(self.model.synthesizer, 'output_sample_rate'):
                self.sample_rate = self.model.synthesizer.output_sample_rate
            else:
                # Default for XTTS v2
                self.sample_rate = 24000

            print(f"[OK] Model loaded successfully! Sample rate: {self.sample_rate} Hz\n")
            return True

        except Exception as e:
            print(f"\n[ERROR] Error loading TTS model: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def get_speaker_latents(self, speaker_wav: str):
        """
        Compute or retrieve cached speaker latents for voice cloning.

        Args:
            speaker_wav: Path to reference audio file

        Returns:
            Tuple of (gpt_cond_latent, speaker_embedding)
        """
        print(f"[AUDIO_GEN] get_speaker_latents() called for: {speaker_wav}")

        # Check cache first
        if speaker_wav in self.latent_cache:
            print(f"[AUDIO_GEN] [OK] Latents found in cache")
            return self.latent_cache[speaker_wav]

        # Compute latents from reference audio
        print(f"[AUDIO_GEN] Computing speaker latents (not cached)...")
        abs_path = os.path.abspath(speaker_wav)
        print(f"[AUDIO_GEN] Absolute path: {abs_path}")
        print(f"[AUDIO_GEN] File exists: {os.path.exists(speaker_wav)}")

        if os.path.exists(speaker_wav):
            file_size = os.path.getsize(speaker_wav)
            print(f"[AUDIO_GEN] File size: {file_size} bytes")

        # Access the underlying TTS model for XTTS-specific methods
        print(f"[AUDIO_GEN] Calling synthesizer.tts_model.get_conditioning_latents()...")
        gpt_cond_latent, speaker_embedding = self.model.synthesizer.tts_model.get_conditioning_latents(
            audio_path=[speaker_wav]
        )

        print(f"[AUDIO_GEN] [OK] Latents computed successfully")
        print(f"[AUDIO_GEN]   - GPT cond latent shape: {gpt_cond_latent.shape if hasattr(gpt_cond_latent, 'shape') else type(gpt_cond_latent)}")
        print(f"[AUDIO_GEN]   - Speaker embedding shape: {speaker_embedding.shape if hasattr(speaker_embedding, 'shape') else type(speaker_embedding)}")

        # Cache for future use
        self.latent_cache[speaker_wav] = (gpt_cond_latent, speaker_embedding)
        return gpt_cond_latent, speaker_embedding

    def generate_speech(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        speaker_name: Optional[str] = None,
        language: str = "en"
    ) -> Optional[np.ndarray]:
        """
        Generate speech audio from text.

        Args:
            text: Text to synthesize
            speaker_wav: Path to speaker reference audio (for voice cloning)
            speaker_name: Built-in XTTS speaker name (alternative to speaker_wav)
            language: Language code

        Returns:
            Audio array or None if generation fails
        """
        print(f"\n[AUDIO_GEN] ========== generate_speech() called ==========")
        print(f"[AUDIO_GEN] Text preview: {text[:100]}...")
        print(f"[AUDIO_GEN] Speaker WAV param: {speaker_wav}")
        print(f"[AUDIO_GEN] Speaker name param: {speaker_name}")
        print(f"[AUDIO_GEN] Language: {language}")

        if self.model is None:
            print("[AUDIO_GEN] ✗ Error: Model not loaded. Call load_model() first.")
            return None

        if not text.strip():
            print("[AUDIO_GEN] ✗ Error: Empty text provided")
            return None

        try:
            # Prioritize voice cloning if file path provided and exists
            if speaker_wav:
                file_exists = os.path.exists(speaker_wav)
                print(f"[AUDIO_GEN] Speaker WAV provided: {speaker_wav}")
                print(f"[AUDIO_GEN] File exists: {file_exists}")

                if file_exists:
                    print(f"[AUDIO_GEN] >>> MODE: VOICE CLONING <<<")
                    # Voice cloning mode - use latents for proper voice encoding
                    gpt_cond_latent, speaker_embedding = self.get_speaker_latents(speaker_wav)

                    print(f"[AUDIO_GEN] Calling TTS model inference API...")
                    # Use the lower-level inference API with computed latents
                    out = self.model.synthesizer.tts_model.inference(
                        text=text,
                        language=language,
                        gpt_cond_latent=gpt_cond_latent,
                        speaker_embedding=speaker_embedding
                    )

                    # XTTS returns waveform in 'wav' key
                    audio = out["wav"]
                    print(f"[AUDIO_GEN] [OK] Voice cloning synthesis complete")
                else:
                    print(f"[AUDIO_GEN] [ERROR] File doesn't exist, falling through to speaker mode")
                    if speaker_name:
                        print(f"[AUDIO_GEN] >>> MODE: BUILT-IN SPEAKER (fallback) <<<")
                        audio = self.model.tts(
                            text=text,
                            speaker=speaker_name,
                            language=language
                        )
                    else:
                        print(f"[AUDIO_GEN] >>> MODE: DEFAULT SPEAKER (fallback) <<<")
                        audio = self.model.tts(
                            text=text,
                            speaker="Claribel Dervla",
                            language=language
                        )
            elif speaker_name:
                # Built-in speaker mode - use high-level API
                print(f"[AUDIO_GEN] >>> MODE: BUILT-IN SPEAKER <<<")
                print(f"[AUDIO_GEN] Using speaker: {speaker_name}")
                audio = self.model.tts(
                    text=text,
                    speaker=speaker_name,
                    language=language
                )
                print(f"[AUDIO_GEN] [OK] Built-in speaker synthesis complete")
            else:
                # Fallback to default young, upbeat speaker
                print(f"[AUDIO_GEN] >>> MODE: DEFAULT SPEAKER <<<")
                print(f"[AUDIO_GEN] Using default speaker: Claribel Dervla")
                audio = self.model.tts(
                    text=text,
                    speaker="Claribel Dervla",  # Young, upbeat default
                    language=language
                )
                print(f"[AUDIO_GEN] [OK] Default speaker synthesis complete")

            # Convert to numpy array if needed
            if isinstance(audio, list):
                audio = np.array(audio, dtype=np.float32)
                print(f"[AUDIO_GEN] Converted list to numpy array")
            elif torch.is_tensor(audio):
                audio = audio.cpu().numpy().astype(np.float32)
                print(f"[AUDIO_GEN] Converted tensor to numpy array")

            print(f"[AUDIO_GEN] [OK] Audio generation SUCCESS")
            print(f"[AUDIO_GEN] Audio shape: {audio.shape}")
            print(f"[AUDIO_GEN] Audio duration: {len(audio) / self.sample_rate:.2f}s")
            print(f"[AUDIO_GEN] ========================================\n")

            return audio

        except Exception as e:
            print(f"[AUDIO_GEN] *** ERROR generating speech ***")
            print(f"[AUDIO_GEN] Error: {e}")
            print(f"[AUDIO_GEN] Text preview: {text[:100]}...")
            import traceback
            print(traceback.format_exc())
            print(f"[AUDIO_GEN] ========================================\n")
            return None

    def generate_speech_chunked(
        self,
        text: str,
        speaker_wav: Optional[str] = None,
        speaker_name: Optional[str] = None,
        language: str = "en",
        max_chunk_size: int = 500
    ) -> Optional[np.ndarray]:
        """
        Generate speech for long text by chunking at sentence boundaries.

        Args:
            text: Text to synthesize
            speaker_wav: Path to speaker reference audio
            speaker_name: Built-in speaker name
            language: Language code
            max_chunk_size: Maximum characters per chunk

        Returns:
            Concatenated audio array or None if generation fails
        """
        from dialogue_parser import chunk_text

        if len(text) <= max_chunk_size:
            return self.generate_speech(text, speaker_wav, speaker_name, language)

        # Split into chunks
        chunks = chunk_text(text, max_chunk_size)
        audio_segments = []

        for i, chunk in enumerate(chunks):
            print(f"  Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
            audio = self.generate_speech(chunk, speaker_wav, speaker_name, language)

            if audio is not None:
                audio_segments.append(audio)

                # Add small pause between chunks (200ms)
                pause_samples = int(0.2 * self.sample_rate)
                pause = np.zeros(pause_samples, dtype=np.float32)
                audio_segments.append(pause)

        if not audio_segments:
            return None

        # Concatenate all segments
        return np.concatenate(audio_segments)

    def concatenate_audio_segments(
        self,
        audio_segments: List[np.ndarray],
        pause_duration: float = 0.3
    ) -> np.ndarray:
        """
        Concatenate multiple audio segments with pauses.

        Args:
            audio_segments: List of audio arrays
            pause_duration: Pause duration in seconds between segments

        Returns:
            Concatenated audio array
        """
        if not audio_segments:
            return np.array([], dtype=np.float32)

        result = []
        pause_samples = int(pause_duration * self.sample_rate)
        pause = np.zeros(pause_samples, dtype=np.float32)

        for i, segment in enumerate(audio_segments):
            result.append(segment)

            # Add pause between segments (but not after the last one)
            if i < len(audio_segments) - 1:
                result.append(pause)

        return np.concatenate(result)

    def save_audio(self, audio: np.ndarray, output_path: str) -> bool:
        """
        Save audio array to file.

        Args:
            audio: Audio array
            output_path: Path to save audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save as WAV file
            sf.write(output_path, audio, self.sample_rate)
            return True

        except Exception as e:
            print(f"Error saving audio: {e}")
            return False

    def _cleanup_memory(self):
        """Clean up GPU memory after generation."""
        if self.device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()

    def unload_model(self):
        """Unload the model and free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            self.latent_cache.clear()  # Clear cached speaker latents
            self._cleanup_memory()
            print("Model unloaded successfully")

    def get_audio_duration(self, audio: np.ndarray) -> float:
        """
        Get duration of audio in seconds.

        Args:
            audio: Audio array

        Returns:
            Duration in seconds
        """
        return len(audio) / self.sample_rate


if __name__ == "__main__":
    # Test Coqui TTS XTTS v2 model loading and generation
    print("Coqui TTS Generator Test")
    print("=" * 70)

    generator = CoquiTTSGenerator()

    print("\n1. Loading model...")
    if generator.load_model():
        print("\n2. Generating test audio with voice cloning...")

        # Use narrator voice for testing
        voice_file = "../voices/male_calm_mature.wav"

        if os.path.exists(voice_file):
            print(f"   Using voice: {voice_file}")
        else:
            print(f"   WARNING: Voice file not found: {voice_file}")
            print("   Using built-in speaker instead")
            voice_file = None

        test_text = "Looking good, Ramirez. That modification you suggested for the bracket feed is working."

        if voice_file:
            audio = generator.generate_speech(test_text, speaker_wav=voice_file)
        else:
            audio = generator.generate_speech(test_text, speaker_name="Claribel Dervla")

        if audio is not None:
            duration = generator.get_audio_duration(audio)
            print(f"   Generated {duration:.2f} seconds of audio")
            print(f"   Audio shape: {audio.shape}")
            print(f"   Sample rate: {generator.sample_rate} Hz")

            # Save test audio
            test_output = "../audio/test_generation.wav"
            if generator.save_audio(audio, test_output):
                print(f"   Saved to: {test_output}")

        print("\n3. Testing chunked generation with voice cloning...")
        long_text = (
            "This is a longer piece of text that will be split into multiple chunks. "
            "Each chunk will be generated separately and then concatenated together. "
            "This helps maintain quality for long passages. The system adds small pauses "
            "between chunks to make the audio sound more natural."
        )

        chunked_audio = generator.generate_speech_chunked(
            long_text,
            max_chunk_size=100,
            speaker_wav=voice_file if voice_file else None,
            speaker_name=None if voice_file else "Claribel Dervla"
        )

        if chunked_audio is not None:
            duration = generator.get_audio_duration(chunked_audio)
            print(f"   Generated {duration:.2f} seconds of chunked audio")

        print("\n4. Unloading model...")
        generator.unload_model()

    else:
        print("Failed to load model. Make sure Coqui TTS is installed:")
        print("  pip install TTS")
        print("Note: Ensure PyTorch with CUDA is installed first!")

    print("\n" + "=" * 70)
    print("Test complete!")
