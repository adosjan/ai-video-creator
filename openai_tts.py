# -*- coding: utf-8 -*-
"""
OpenAI Text-to-Speech Module
Alternative to ElevenLabs with high quality voices
"""

from openai import OpenAI
from pathlib import Path
from config import settings, TEMP_DIR
from pydub import AudioSegment
import os

class OpenAITTS:
    """Generate speech using OpenAI TTS API"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        # Available voices: alloy, echo, fable, onyx, nova, shimmer
        self.default_voice = "onyx"  # Male, deep voice (similar to Adam)

    def generate_speech(
        self,
        text: str,
        output_path: str = None,
        voice: str = None,
        model: str = "tts-1-hd"  # or "tts-1" for faster/cheaper
    ) -> str:
        """
        Generate speech from text

        Args:
            text: Text to convert to speech
            output_path: Where to save audio file
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: "tts-1-hd" (high quality) or "tts-1" (faster)

        Returns:
            Path to generated audio file
        """
        if voice is None:
            voice = self.default_voice

        if output_path is None:
            output_path = str(TEMP_DIR / "openai_tts_output.mp3")

        print(f"[*] Generating speech with OpenAI TTS...")
        print(f"    Voice: {voice}, Model: {model}")
        print(f"    Text length: {len(text)} characters")

        try:
            # Generate speech
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="mp3"
            )

            # Save to file
            response.stream_to_file(output_path)

            print(f"[OK] Speech generated: {output_path}")

            # Get duration (skip if FFmpeg not available)
            try:
                audio = AudioSegment.from_mp3(output_path)
                duration = len(audio) / 1000.0  # Convert to seconds
                print(f"[OK] Audio duration: {duration:.2f} seconds")
            except:
                print(f"[OK] Audio file created (FFmpeg not available for duration check)")

            return output_path

        except Exception as e:
            print(f"[ERROR] TTS generation failed: {e}")
            raise

    def generate_long_speech(
        self,
        text: str,
        output_path: str = None,
        voice: str = None,
        max_chunk_size: int = 4000
    ) -> str:
        """
        Generate speech for long text by chunking

        Args:
            text: Long text to convert
            output_path: Output path
            voice: Voice to use
            max_chunk_size: Max characters per chunk

        Returns:
            Path to combined audio
        """
        if output_path is None:
            output_path = str(TEMP_DIR / "openai_tts_long.mp3")

        if voice is None:
            voice = self.default_voice

        print(f"[*] Generating speech for long text ({len(text)} chars)...")

        # Split text into chunks
        chunks = self._split_text(text, max_chunk_size)
        print(f"[*] Split into {len(chunks)} chunks")

        # Generate audio for each chunk
        audio_segments = []
        temp_files = []

        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}...")

            temp_path = str(TEMP_DIR / f"chunk_{i}.mp3")
            temp_files.append(temp_path)

            self.generate_speech(
                text=chunk,
                output_path=temp_path,
                voice=voice
            )

            audio_segments.append(AudioSegment.from_mp3(temp_path))

        # Combine all segments
        print(f"[*] Combining {len(audio_segments)} audio segments...")
        combined = sum(audio_segments)
        combined.export(output_path, format="mp3")

        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass

        duration = len(combined) / 1000.0
        print(f"[OK] Long speech generated: {output_path}")
        print(f"[OK] Total duration: {duration:.2f} seconds")

        return output_path

    def _split_text(self, text: str, max_size: int) -> list:
        """Split text into chunks at sentence boundaries"""
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) + 2 <= max_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# Test usage
if __name__ == "__main__":
    print("\n=== OpenAI TTS Test ===\n")

    tts = OpenAITTS()

    print("Available voices:")
    print("- alloy (neutral)")
    print("- echo (male)")
    print("- fable (British male)")
    print("- onyx (deep male) <- DEFAULT")
    print("- nova (female)")
    print("- shimmer (soft female)")

    test_text = """
    Have you ever wondered why some videos go viral while others don't?
    Today we're going to explore the secrets behind the internet's most
    popular content and how you can use these strategies for your own videos.
    """

    print(f"\nTest text: {test_text.strip()}\n")

    # Test with default voice (onyx)
    audio_path = tts.generate_speech(
        text=test_text.strip(),
        voice="onyx",
        model="tts-1-hd"
    )

    print(f"\n[OK] Test complete!")
    print(f"Audio saved to: {audio_path}")
    print("\nCost: ~$0.015 per 1000 characters")
    print("Quality: HD quality, very natural sounding")
