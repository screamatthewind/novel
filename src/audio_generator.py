"""
Audio generator using Resemble AI Chatterbox TTS for multi-voice narration.
Handles TTS model loading, speech generation, and GPU memory management.
"""

import numpy as np
import torch
import soundfile as sf
from typing import Optional, List
import os
import gc

from config import DEFAULT_TTS_MODEL, DEFAULT_SAMPLE_RATE, DEVICE


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


class ChatterboxTTSGenerator:
    """
    Wrapper for Resemble AI Chatterbox TTS models.
    Manages model loading, speech generation, and memory cleanup.
    """

    def __init__(self, model_name: str = DEFAULT_TTS_MODEL, device: str = DEVICE):
        """
        Initialize TTS generator.

        Args:
            model_name: TTS model identifier (chatterbox, multilingual, or turbo)
            device: Device to use ('cuda' or 'cpu')
        """
        self.model_name = model_name
        self.model = None
        self.sample_rate = DEFAULT_SAMPLE_RATE

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
            print(f"\nLoading Chatterbox TTS model: {self.model_name}")
            print(f"Target device: {self.device}")

            # Import the appropriate Chatterbox model
            if self.model_name == "turbo":
                from chatterbox.tts_turbo import ChatterboxTurboTTS

                # Get Hugging Face token from environment if available
                hf_token = os.environ.get("HF_TOKEN")

                if hf_token:
                    print("Using Hugging Face token from environment")
                    self.model = ChatterboxTurboTTS.from_pretrained(
                        device=self.device,
                        token=hf_token
                    )
                else:
                    # Try without token (model might be public)
                    try:
                        self.model = ChatterboxTurboTTS.from_pretrained(device=self.device)
                    except Exception as token_error:
                        if "token" in str(token_error).lower():
                            print("\n[INFO] Chatterbox Turbo requires authentication.")
                            print("Please set HF_TOKEN environment variable or use standard model.")
                            print("Falling back to standard Chatterbox model...")
                            from chatterbox.tts import ChatterboxTTS
                            self.model = ChatterboxTTS.from_pretrained(device=self.device)
                        else:
                            raise

            elif self.model_name == "multilingual":
                from chatterbox.tts import ChatterboxTTS
                self.model = ChatterboxTTS.from_pretrained(
                    model_id="ResembleAI/chatterbox-multilingual",
                    device=self.device
                )
            else:  # Default to standard chatterbox
                from chatterbox.tts import ChatterboxTTS
                self.model = ChatterboxTTS.from_pretrained(device=self.device)

            # Get sample rate from model (Chatterbox uses 24kHz)
            self.sample_rate = 24000

            print(f"[OK] Model loaded successfully! Sample rate: {self.sample_rate} Hz\n")
            return True

        except Exception as e:
            print(f"\n[ERROR] Error loading Chatterbox TTS model: {e}")
            import traceback
            print(traceback.format_exc())
            return False

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
            speaker_name: Built-in speaker name (not used in Chatterbox)
            language: Language code

        Returns:
            Audio array or None if generation fails
        """
        if self.model is None:
            print("Error: Model not loaded. Call load_model() first.")
            return None

        if not text.strip():
            return None

        try:
            # Chatterbox requires a reference audio for voice cloning
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode with provided speaker wav
                audio = self.model.generate(
                    text=text,
                    audio_prompt_path=speaker_wav
                )
            else:
                # No reference audio - use default generation
                # Note: Chatterbox performs best with reference audio
                print(f"Warning: No reference audio provided for '{text[:50]}...'. Using default voice.")
                audio = self.model.generate(text=text)

            # Chatterbox returns a torch tensor, convert to numpy
            if torch.is_tensor(audio):
                audio = audio.cpu().numpy().astype(np.float32)
            elif isinstance(audio, list):
                audio = np.array(audio, dtype=np.float32)

            # Ensure audio is 1D array
            if len(audio.shape) > 1:
                audio = audio.squeeze()

            return audio

        except Exception as e:
            print(f"Error generating speech: {e}")
            print(f"Text preview: {text[:100]}...")
            import traceback
            print(traceback.format_exc())
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
            speaker_name: Built-in speaker name (not used)
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
    # Test Chatterbox TTS model loading and generation
    print("Chatterbox TTS Generator Test")
    print("=" * 70)

    generator = ChatterboxTTSGenerator(model_name="turbo")

    print("\n1. Loading model...")
    if generator.load_model():
        print("\n2. Generating test audio with voice cloning...")

        # Use male_calm_mature voice for testing
        voice_file = "../voices/male_calm_mature.wav"

        if os.path.exists(voice_file):
            print(f"   Using voice: {voice_file}")
        else:
            print(f"   WARNING: Voice file not found: {voice_file}")
            print("   Using default voice instead")
            voice_file = None

        test_text = "Looking good, Ramirez. That modification you suggested for the bracket feed is working."

        audio = generator.generate_speech(test_text, speaker_wav=voice_file)

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
            speaker_wav=voice_file
        )

        if chunked_audio is not None:
            duration = generator.get_audio_duration(chunked_audio)
            print(f"   Generated {duration:.2f} seconds of chunked audio")

        print("\n4. Unloading model...")
        generator.unload_model()

    else:
        print("Failed to load model. Make sure chatterbox-tts is installed:")
        print("  pip install chatterbox-tts")
        print("Note: Ensure PyTorch with CUDA is installed first!")

    print("\n" + "=" * 70)
    print("Test complete!")
