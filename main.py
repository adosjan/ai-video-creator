"""
AI Video Creator - Main Orchestrator
Combines all modules to create complete YouTube videos automatically
"""

from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

# Import all modules
from youtube_analyzer import YouTubeAnalyzer
from script_generator import ScriptGenerator
from elevenlabs_tts import ElevenLabsTTS
from midjourney_bot import SimplifiedMidjourneyClient
from thumbnail_generator import ThumbnailGenerator
from video_editor import VideoEditor
from config import OUTPUT_DIR, TEMP_DIR


class VideoCreator:
    """Main class that orchestrates the entire video creation process"""

    def __init__(
        self,
        video_length: str = "short",
        thumbnail_style: str = "clickbait",
        voice_id: Optional[str] = None,
        use_manual_midjourney: bool = True
    ):
        """
        Initialize Video Creator

        Args:
            video_length: "short", "medium", or "long"
            thumbnail_style: "clickbait", "professional", or "educational"
            voice_id: ElevenLabs voice ID (optional)
            use_manual_midjourney: If True, generates prompts for manual use
        """
        print("[*] Initializing AI Video Creator...")

        self.video_length = video_length
        self.thumbnail_style = thumbnail_style
        self.use_manual_midjourney = use_manual_midjourney

        # Initialize components
        try:
            self.youtube_analyzer = YouTubeAnalyzer()
            print("[OK] YouTube Analyzer ready")

            self.script_generator = ScriptGenerator()
            print("[OK] Script Generator ready")

            self.tts = ElevenLabsTTS(voice_id=voice_id)
            print("[OK] ElevenLabs TTS ready")

            if use_manual_midjourney:
                self.midjourney_client = SimplifiedMidjourneyClient()
                print("[OK] Midjourney (Manual Mode) ready")
            else:
                # from midjourney_bot import MidjourneyClient
                # self.midjourney_client = MidjourneyClient()
                print("[WARNING] Automated Midjourney requires setup")

            self.thumbnail_generator = ThumbnailGenerator(style=thumbnail_style)
            print("[OK] Thumbnail Generator ready")

            self.video_editor = VideoEditor()
            print("[OK] Video Editor ready")

            print("\n[SUCCESS] All systems ready!\n")

        except ValueError as e:
            print(f"\n[ERROR] Initialization Error: {e}")
            print("Please check your .env file and API keys")
            raise

    def create_from_url(
        self,
        url: str,
        custom_prompt: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> Dict:
        """
        Create complete video from YouTube URL

        Args:
            url: YouTube video URL to analyze
            custom_prompt: Custom instructions for script generation
            output_name: Custom name for output files

        Returns:
            Dict with paths to created video and thumbnail
        """
        print("="*60)
        print(" STARTING VIDEO CREATION PROCESS")
        print("="*60)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_name is None:
            output_name = f"video_{timestamp}"

        try:
            # STEP 1: Analyze YouTube video
            print("\n[STEP 1] Analyzing YouTube video...")
            analysis = self.youtube_analyzer.analyze_full_video(url)

            if not analysis['success']:
                raise Exception("Failed to analyze video")

            # STEP 2: Generate unique script
            print("\n[STEP 2] Generating unique script...")
            script_data = self.script_generator.generate_script(
                video_analysis=analysis,
                target_length=self.video_length,
                style="engaging",
                custom_instructions=custom_prompt
            )

            if not script_data['success']:
                raise Exception("Failed to generate script")

            print(f"\n[OK] Script generated: {script_data['title']}")
            print(f"   Script length: {len(script_data['script'])} characters")

            # STEP 3: Generate voiceover
            print("\n[STEP 3] Generating voiceover...")
            audio_path = self.tts.generate_long_audio(
                text=script_data['script'],
                output_path=str(TEMP_DIR / f"{output_name}_audio.mp3")
            )

            # Get audio duration
            audio_duration = self.tts.get_audio_duration(audio_path)
            print(f"   Voiceover duration: {audio_duration:.2f} seconds")

            # STEP 4: Generate images for video
            print("\n[STEP 4] Generating images...")

            # Generate Midjourney prompt
            mj_prompt = self.script_generator.generate_thumbnail_prompt(script_data)
            print(f"\n   Midjourney Prompt:\n   {mj_prompt}\n")

            if self.use_manual_midjourney:
                print("[WARNING] MANUAL STEP REQUIRED:")
                print("="*60)
                print("1. Open Discord and go to your Midjourney server")
                print("2. Type: /imagine")
                print(f"3. Paste this prompt: {mj_prompt}")
                print("4. Wait for generation (~60 seconds)")
                print("5. Save the image to the 'temp' folder")
                print(f"6. Name it: {output_name}_background.png")
                print("="*60)
                input("\nPress Enter when you've saved the image...")

                background_image = str(TEMP_DIR / f"{output_name}_background.png")

                if not Path(background_image).exists():
                    print("[WARNING] Image not found. Creating simple thumbnail instead...")
                    background_image = None
            else:
                # Automated generation (requires setup)
                print("   Generating with Midjourney...")
                # background_image = self.midjourney_client.generate_image_sync(mj_prompt)
                background_image = None

            # STEP 5: Create thumbnail
            print("\n[STEP 5] Creating thumbnail...")

            if background_image and Path(background_image).exists():
                thumbnail_path = self.thumbnail_generator.create_thumbnail(
                    background_image_path=background_image,
                    text=script_data['thumbnail_text'],
                    output_path=str(OUTPUT_DIR / f"{output_name}_thumbnail.jpg")
                )
            else:
                # Fallback: simple thumbnail
                thumbnail_path = self.thumbnail_generator.create_simple_thumbnail(
                    text=script_data['thumbnail_text'],
                    output_path=str(OUTPUT_DIR / f"{output_name}_thumbnail.jpg")
                )

            # STEP 6: Create video
            print("\n[STEP 6] Creating video...")

            # For now, use the background image (or thumbnail) as video background
            if background_image and Path(background_image).exists():
                video_background = background_image
            else:
                video_background = thumbnail_path

            # Create video
            video_path = self.video_editor.create_simple_video(
                images=[video_background],  # Can add more images
                audio_path=audio_path,
                output_path=str(OUTPUT_DIR / f"{output_name}.mp4")
            )

            # STEP 7: Results
            print("\n" + "="*60)
            print(" VIDEO CREATION COMPLETE!")
            print("="*60)

            result = {
                'success': True,
                'title': script_data['title'],
                'description': script_data['description'],
                'tags': script_data['tags'],
                'video_path': video_path,
                'thumbnail_path': thumbnail_path,
                'audio_path': audio_path,
                'script': script_data['script'],
                'midjourney_prompt': mj_prompt
            }

            print(f"\nVideo: {video_path}")
            print(f"Thumbnail: {thumbnail_path}")
            print(f"Title: {result['title']}")
            print(f"Tags: {', '.join(result['tags'][:5])}")

            return result

        except Exception as e:
            print(f"\n[ERROR] Error during video creation: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }

    def create_batch(self, urls: list) -> list:
        """
        Create multiple videos from list of URLs

        Args:
            urls: List of YouTube URLs

        Returns:
            List of results
        """
        results = []

        for i, url in enumerate(urls):
            print(f"\n\n{'='*60}")
            print(f"Processing video {i+1}/{len(urls)}")
            print(f"{'='*60}\n")

            result = self.create_from_url(url)
            results.append(result)

            if result['success']:
                print(f"[OK] Video {i+1} completed successfully")
            else:
                print(f"[ERROR] Video {i+1} failed: {result.get('error')}")

        return results


# Convenience function
def create_video_from_url(url: str, **kwargs) -> Dict:
    """
    Quick function to create video from URL

    Args:
        url: YouTube video URL
        **kwargs: Additional arguments for VideoCreator

    Returns:
        Result dict
    """
    creator = VideoCreator(**kwargs)
    return creator.create_from_url(url)


# Example usage / Testing
if __name__ == "__main__":
    print("""
============================================================
              AI VIDEO CREATOR
         Automated YouTube Video Generation
============================================================
    """)

    # Check if .env is configured
    from config import settings

    if not settings:
        print("\n[ERROR] Configuration Error!")
        print("\nPlease set up your .env file with API keys:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your API keys:")
        print("   - OPENAI_API_KEY")
        print("   - ELEVENLABS_API_KEY")
        print("   - ELEVENLABS_VOICE_ID")
        print("\nOptional (for automated Midjourney):")
        print("   - DISCORD_BOT_TOKEN")
        print("   - MIDJOURNEY_SERVER_ID")
        print("   - MIDJOURNEY_CHANNEL_ID")
        exit(1)

    print("\n[OK] Configuration loaded!\n")

    # Example: Create video
    print("Example usage:\n")
    print("from main import VideoCreator")
    print("\ncreator = VideoCreator(")
    print("    video_length='short',")
    print("    thumbnail_style='clickbait'")
    print(")")
    print("\nresult = creator.create_from_url('https://youtube.com/watch?v=...')")
    print("\nif result['success']:")
    print("    print(f\"Video created: {result['video_path']}\")")

    # Interactive mode
    print("\n" + "="*60)
    user_input = input("\nWant to try creating a video now? (y/n): ").strip().lower()

    if user_input == 'y':
        video_url = input("\nEnter YouTube video URL: ").strip()

        if video_url:
            creator = VideoCreator(
                video_length="short",
                thumbnail_style="clickbait"
            )

            result = creator.create_from_url(video_url)

            if result['success']:
                print("\n[SUCCESS] Check the 'output' folder for your video!")
            else:
                print(f"\n[ERROR] Failed: {result.get('error')}")
        else:
            print("No URL provided.")
    else:
        print("\nOkay! Use the code examples above when you're ready.")

    print("\nThank you for using AI Video Creator!\n")
