# -*- coding: utf-8 -*-
"""
FULL AI Video Creator
Complete workflow: Analysis -> Script -> Images -> Voice -> Music -> Video
"""

from pathlib import Path
from datetime import datetime
from youtube_analyzer import YouTubeAnalyzer
from script_generator import ScriptGenerator
from dalle_generator import DalleImageGenerator
from openai_tts import OpenAITTS
from thumbnail_generator import ThumbnailGenerator
from config import OUTPUT_DIR, TEMP_DIR
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip
from pydub import AudioSegment
import sys

def create_full_video(
    youtube_url: str,
    background_music_path: str = None,
    music_volume: float = 0.15,
    use_dalle: bool = True
):
    """
    Create complete video with voice and music

    Args:
        youtube_url: YouTube video to analyze
        background_music_path: Path to background music file (optional)
        music_volume: Volume of background music (0.0-1.0)
        use_dalle: True for DALL-E (auto), False for Midjourney (manual)
    """
    print("\n" + "="*60)
    print(" FULL AI VIDEO CREATOR")
    print("="*60)
    print(f"\nSource URL: {youtube_url}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = f"video_{timestamp}"

    try:
        # STEP 1: Analyze YouTube video
        print("\n[STEP 1/7] Analyzing YouTube video...")
        analyzer = YouTubeAnalyzer()
        analysis = analyzer.analyze_full_video(youtube_url)

        if not analysis['success']:
            raise Exception("Failed to analyze video")

        print(f"[OK] Analyzed: {analysis['metadata']['title']}")

        # STEP 2: Generate unique script
        print("\n[STEP 2/7] Generating unique script...")
        script_gen = ScriptGenerator()
        script_data = script_gen.generate_script(
            video_analysis=analysis,
            target_length="short",
            style="engaging"
        )

        if not script_data['success']:
            raise Exception("Failed to generate script")

        print(f"[OK] Script generated: {script_data['title']}")
        print(f"   Script length: {len(script_data['script'])} characters")

        # Clean script text (remove emojis)
        script_text = script_data['script'].encode('ascii', 'ignore').decode('ascii')

        # STEP 3: Generate voiceover
        print("\n[STEP 3/7] Generating voiceover with OpenAI TTS...")
        tts = OpenAITTS()
        voice_path = str(TEMP_DIR / f"{output_name}_voice.mp3")

        if len(script_text) > 4000:
            voice_path = tts.generate_long_speech(
                text=script_text,
                output_path=voice_path,
                voice="onyx"  # Deep male voice
            )
        else:
            voice_path = tts.generate_speech(
                text=script_text,
                output_path=voice_path,
                voice="onyx",
                model="tts-1-hd"
            )

        # Get audio duration (skip if FFmpeg not available)
        try:
            voice_audio = AudioSegment.from_mp3(voice_path)
            voice_duration = len(voice_audio) / 1000.0
            print(f"[OK] Voice duration: {voice_duration:.2f} seconds")
        except:
            print(f"[OK] Voice generated (FFmpeg not available, will use moviepy for duration)")
            voice_duration = None

        # STEP 4: Generate background image
        if use_dalle:
            print("\n[STEP 4/7] Generating image with DALL-E 3...")
            dalle_prompt = script_gen.generate_thumbnail_prompt(script_data)
            print(f"   Prompt: {dalle_prompt[:100]}...")

            dalle_gen = DalleImageGenerator()
            background_image = dalle_gen.generate_image(
                prompt=dalle_prompt,
                output_path=str(TEMP_DIR / f"{output_name}_background.png"),
                size="1792x1024",
                quality="hd"
            )
        else:
            print("\n[STEP 4/7] Midjourney mode (manual)...")
            mj_prompt = script_gen.generate_thumbnail_prompt(script_data)
            print(f"\n   Midjourney Prompt:\n   {mj_prompt}\n")
            print("=" * 60)
            print("MANUAL STEP:")
            print("1. Open Discord -> Midjourney")
            print("2. Type: /imagine")
            print(f"3. Paste prompt above")
            print(f"4. Save image as: temp/{output_name}_background.png")
            print("=" * 60)
            input("\nPress Enter after saving image...")

            background_image = str(TEMP_DIR / f"{output_name}_background.png")
            if not Path(background_image).exists():
                raise Exception("Midjourney image not found!")

        print(f"[OK] Background image ready: {background_image}")

        # STEP 5: Create thumbnail
        print("\n[STEP 5/7] Creating thumbnail...")
        thumb_gen = ThumbnailGenerator(style="clickbait")
        thumbnail_path = thumb_gen.create_thumbnail(
            background_image_path=background_image,
            text=script_data['thumbnail_text'],
            output_path=str(OUTPUT_DIR / f"{output_name}_thumbnail.jpg")
        )

        # STEP 6: Add background music (if provided)
        final_audio_path = voice_path

        if background_music_path and Path(background_music_path).exists():
            print("\n[STEP 6/7] Adding background music...")
            print(f"   Music: {background_music_path}")
            print(f"   Volume: {music_volume * 100}%")

            try:
                # Load voice and music
                voice = AudioSegment.from_mp3(voice_path)
                music = AudioSegment.from_file(background_music_path)

                # Adjust music volume
                music = music - (20 * (1 - music_volume))  # Convert to dB

                # Loop or trim music to match voice duration
                if len(music) < len(voice):
                    # Loop music
                    loops_needed = (len(voice) // len(music)) + 1
                    music = music * loops_needed

                music = music[:len(voice)]

                # Mix voice and music
                mixed = voice.overlay(music)

                # Export mixed audio
                final_audio_path = str(TEMP_DIR / f"{output_name}_final_audio.mp3")
                mixed.export(final_audio_path, format="mp3")

                print(f"[OK] Audio mixed with music")
            except:
                print("[WARNING] Could not mix music (FFmpeg not installed)")
                print("[INFO] Install FFmpeg for music support: https://ffmpeg.org/download.html")
                print("[INFO] Continuing without background music...")
        else:
            print("\n[STEP 6/7] Skipping background music (not provided)")

        # STEP 7: Create final video
        print("\n[STEP 7/7] Creating final video...")

        # Load audio
        audio = AudioFileClip(final_audio_path)
        video_duration = audio.duration

        # Update voice_duration if it wasn't set
        if voice_duration is None:
            voice_duration = video_duration

        # Create video from image
        clip = ImageClip(background_image, duration=video_duration)
        clip = clip.set_fps(30)
        clip = clip.set_audio(audio)

        # Export video
        video_path = str(OUTPUT_DIR / f"{output_name}.mp4")
        clip.write_videofile(
            video_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(TEMP_DIR / 'temp_audio.m4a'),
            remove_temp=True,
            logger=None
        )

        clip.close()
        audio.close()

        # RESULTS
        print("\n" + "="*60)
        print(" VIDEO CREATION COMPLETE!")
        print("="*60)

        print(f"\nFiles created:")
        print(f"  Video:      {video_path}")
        print(f"  Thumbnail:  {thumbnail_path}")
        print(f"  Background: {background_image}")
        print(f"  Voice:      {voice_path}")
        if background_music_path:
            print(f"  Music:      {background_music_path}")

        print(f"\nVideo details:")
        print(f"  Title:      {script_data['title']}")
        print(f"  Duration:   {video_duration:.2f} seconds")
        print(f"  Tags:       {', '.join(script_data['tags'][:5])}")

        print(f"\nDescription preview:")
        print(f"  {script_data['description'][:150]}...")

        print("\n" + "="*60)
        print("COST BREAKDOWN:")
        print("="*60)
        if use_dalle:
            print("  DALL-E 3 HD:    ~$0.08")
        print(f"  OpenAI TTS:     ~${(len(script_text) / 1000) * 0.015:.3f}")
        print(f"  GPT-4o script:  ~$0.01")
        print(f"  TOTAL:          ~${0.08 + (len(script_text) / 1000) * 0.015 + 0.01:.3f}")
        print("="*60)

        print("\n[SUCCESS] Ready to upload to YouTube!")
        print(f"\nCheck 'output' folder:")
        print(f"  - {output_name}.mp4")
        print(f"  - {output_name}_thumbnail.jpg")

        return video_path

    except Exception as e:
        print(f"\n[ERROR] Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Default YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # OPTIONAL: Background music path
    # Download free music from: YouTube Audio Library, Pixabay, Incompetech
    background_music = None  # Set to path if you have music file

    # Ask user for URL
    print("\n" + "="*60)
    print(" FULL AI VIDEO CREATOR")
    print("="*60)
    print("\nPress Enter to use default URL or paste your YouTube URL:")
    print(f"Default: {youtube_url}\n")

    user_input = input("YouTube URL: ").strip()
    if user_input:
        youtube_url = user_input

    # Ask about music
    print("\nDo you have background music file? (optional)")
    print("Press Enter to skip or enter path to music file:")
    music_input = input("Music path: ").strip()
    if music_input and Path(music_input).exists():
        background_music = music_input

    # Create video
    print("\nStarting video creation...\n")

    create_full_video(
        youtube_url=youtube_url,
        background_music_path=background_music,
        music_volume=0.15,  # 15% music volume
        use_dalle=True  # Use DALL-E (set False for Midjourney)
    )

    print("\n")
