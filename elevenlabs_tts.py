"""
ElevenLabs Text-to-Speech Integration
Generates professional voiceovers for videos
"""

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path
from typing import Optional
from config import settings, TEMP_DIR


class ElevenLabsTTS:
    """Handles text-to-speech generation using ElevenLabs"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        """
        Initialize ElevenLabs TTS

        Args:
            api_key: ElevenLabs API key (if not provided, uses config)
            voice_id: Voice ID to use (if not provided, uses config)
        """
        self.api_key = api_key or (settings.elevenlabs_api_key if settings else None)
        self.voice_id = voice_id or (settings.elevenlabs_voice_id if settings else None)

        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")
        if not self.voice_id:
            raise ValueError("ElevenLabs voice ID is required")

        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(
        self,
        text: str,
        output_path: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> str:
        """
        Generate audio from text using ElevenLabs

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (if None, auto-generates)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity (0.0-1.0)
            style: Style exaggeration (0.0-1.0)
            use_speaker_boost: Enable speaker boost

        Returns:
            Path to generated audio file
        """
        print(f"[*] Generating voiceover ({len(text)} characters)...")

        # Generate output path if not provided
        if output_path is None:
            output_path = str(TEMP_DIR / "voiceover.mp3")

        try:
            # Generate audio
            response = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                optimize_streaming_latency="0",
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2",  # Best quality model
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    use_speaker_boost=use_speaker_boost,
                ),
            )

            # Save audio to file
            with open(output_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)

            print(f"[OK] Voiceover generated: {output_path}")
            return output_path

        except Exception as e:
            raise Exception(f"Error generating audio: {str(e)}")

    def get_available_voices(self) -> list:
        """
        Get list of available voices from your ElevenLabs account

        Returns:
            List of voice objects with id, name, category
        """
        try:
            response = self.client.voices.get_all()
            voices = []

            for voice in response.voices:
                voices.append({
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': voice.category,
                })

            return voices

        except Exception as e:
            print(f"[WARNING] Error getting voices: {e}")
            return []

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file in seconds

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            from mutagen.mp3 import MP3
            audio = MP3(audio_path)
            return audio.info.length
        except:
            # Fallback: estimate from file size (rough estimate)
            file_size = Path(audio_path).stat().st_size
            # Rough estimate: 128kbps mp3 = ~16KB per second
            return file_size / 16000

    def split_text_for_generation(self, text: str, max_chars: int = 5000) -> list:
        """
        Split long text into chunks for generation
        (ElevenLabs has a character limit per request)

        Args:
            text: Full text to split
            max_chars: Maximum characters per chunk

        Returns:
            List of text chunks
        """
        if len(text) <= max_chars:
            return [text]

        chunks = []
        sentences = text.split('. ')
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_chars:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def generate_long_audio(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate audio for long text by splitting into chunks
        and concatenating the results

        Args:
            text: Long text to convert
            output_path: Output path for final audio

        Returns:
            Path to generated audio file
        """
        print(f"[*] Generating long voiceover ({len(text)} characters)...")

        if output_path is None:
            output_path = str(TEMP_DIR / "voiceover_long.mp3")

        # Split text into chunks
        chunks = self.split_text_for_generation(text)

        if len(chunks) == 1:
            return self.generate_audio(text, output_path)

        print(f"[*] Split into {len(chunks)} chunks")

        # Generate audio for each chunk
        chunk_files = []
        for i, chunk in enumerate(chunks):
            chunk_path = str(TEMP_DIR / f"chunk_{i}.mp3")
            self.generate_audio(chunk, chunk_path)
            chunk_files.append(chunk_path)

        # Concatenate all chunks
        print("🔗 Concatenating audio chunks...")
        self._concatenate_audio_files(chunk_files, output_path)

        # Clean up chunk files
        for chunk_file in chunk_files:
            Path(chunk_file).unlink(missing_ok=True)

        print(f"[OK] Long voiceover generated: {output_path}")
        return output_path

    def _concatenate_audio_files(self, file_paths: list, output_path: str):
        """Concatenate multiple audio files into one"""
        try:
            from pydub import AudioSegment

            combined = AudioSegment.empty()
            for file_path in file_paths:
                audio = AudioSegment.from_mp3(file_path)
                combined += audio

            combined.export(output_path, format="mp3")

        except ImportError:
            # Fallback: use ffmpeg directly
            import subprocess

            # Create file list for ffmpeg
            list_file = TEMP_DIR / "concat_list.txt"
            with open(list_file, 'w') as f:
                for file_path in file_paths:
                    f.write(f"file '{file_path}'\n")

            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy', output_path, '-y'
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            list_file.unlink()


# Example usage
if __name__ == "__main__":
    try:
        tts = ElevenLabsTTS()

        # List available voices
        print("\n=== Available Voices ===")
        voices = tts.get_available_voices()
        for voice in voices[:5]:  # Show first 5
            print(f"- {voice['name']} ({voice['voice_id']})")

        # Generate sample audio
        sample_text = """
        Welcome to this AI-generated video.
        Today, we're going to explore how artificial intelligence
        is transforming content creation.
        Let's dive right in!
        """

        output_file = tts.generate_audio(sample_text)
        print(f"\n[OK] Sample audio generated: {output_file}")

        # Get duration
        duration = tts.get_audio_duration(output_file)
        print(f"Duration: {duration:.2f} seconds")

    except ValueError as e:
        print(f"[ERROR] {e}")
        print("Please set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in your .env file")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
