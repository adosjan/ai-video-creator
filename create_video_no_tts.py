# -*- coding: utf-8 -*-
"""
Create AI Video WITHOUT TTS (No Voice)
Test version to check system without ElevenLabs
"""

from pathlib import Path
from datetime import datetime
from youtube_analyzer import YouTubeAnalyzer
from script_generator import ScriptGenerator
from midjourney_bot import SimplifiedMidjourneyClient
from thumbnail_generator import ThumbnailGenerator
from video_editor import VideoEditor
from config import OUTPUT_DIR, TEMP_DIR
import subprocess

def create_silent_audio(duration_seconds, output_path):
    """Create silent audio file using ffmpeg"""
    print(f"[*] Creating silent audio ({duration_seconds}s)...")

    # Create silent audio directly with ffmpeg
    subprocess.run([
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'anullsrc=r=44100:cl=stereo',
        '-t', str(duration_seconds),
        '-q:a', '2',
        '-acodec', 'libmp3lame',
        output_path,
        '-y'
    ], capture_output=True, check=True)

    print(f"[OK] Silent audio created: {output_path}")
    return output_path


# YouTube URL to analyze
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print("\n" + "="*60)
print(" CREATING VIDEO WITHOUT TTS (TEST MODE)")
print("="*60)
print(f"\nSource URL: {youtube_url}\n")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_name = f"video_{timestamp}"

try:
    # STEP 1: Analyze YouTube video
    print("\n[STEP 1] Analyzing YouTube video...")
    analyzer = YouTubeAnalyzer()
    analysis = analyzer.analyze_full_video(youtube_url)

    if not analysis['success']:
        raise Exception("Failed to analyze video")

    print(f"[OK] Analyzed: {analysis['metadata']['title']}")

    # STEP 2: Generate unique script
    print("\n[STEP 2] Generating unique script...")
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

    # STEP 3: Create silent audio (60 seconds for YouTube Shorts)
    print("\n[STEP 3] Creating silent audio instead of TTS...")
    audio_path = str(TEMP_DIR / f"{output_name}_audio.mp3")
    create_silent_audio(60, audio_path)

    # STEP 4: Generate Midjourney prompt
    print("\n[STEP 4] Generating Midjourney prompt...")
    mj_prompt = script_gen.generate_thumbnail_prompt(script_data)
    print(f"\n   Midjourney Prompt:\n   {mj_prompt}\n")

    # Manual Midjourney step (optional - skip for testing)
    print("[WARNING] MANUAL STEP (OPTIONAL FOR TESTING):")
    print("="*60)
    print("You can skip this and just press Enter to use simple thumbnail")
    print("OR create image in Midjourney:")
    print("1. Open Discord -> Midjourney server")
    print("2. Type: /imagine")
    print(f"3. Paste: {mj_prompt}")
    print("4. Save image to 'temp' folder")
    print(f"5. Name it: {output_name}_background.png")
    print("="*60)
    input("\nPress Enter to continue (skip image or after saving)...")

    background_image = str(TEMP_DIR / f"{output_name}_background.png")
    if not Path(background_image).exists():
        print("[WARNING] Image not found. Using simple thumbnail.")
        background_image = None

    # STEP 5: Create thumbnail
    print("\n[STEP 5] Creating thumbnail...")
    thumb_gen = ThumbnailGenerator(style="clickbait")

    if background_image:
        thumbnail_path = thumb_gen.create_thumbnail(
            background_image_path=background_image,
            text=script_data['thumbnail_text'],
            output_path=str(OUTPUT_DIR / f"{output_name}_thumbnail.jpg")
        )
    else:
        thumbnail_path = thumb_gen.create_simple_thumbnail(
            text=script_data['thumbnail_text'],
            output_path=str(OUTPUT_DIR / f"{output_name}_thumbnail.jpg")
        )

    # STEP 6: Create video
    print("\n[STEP 6] Creating video...")
    editor = VideoEditor()

    video_background = background_image if background_image else thumbnail_path

    video_path = editor.create_simple_video(
        images=[video_background],
        audio_path=audio_path,
        output_path=str(OUTPUT_DIR / f"{output_name}.mp4")
    )

    # STEP 7: Results
    print("\n" + "="*60)
    print(" VIDEO CREATION COMPLETE!")
    print("="*60)

    print(f"\nVideo: {video_path}")
    print(f"Thumbnail: {thumbnail_path}")
    print(f"Title: {script_data['title']}")
    print(f"Description: {script_data['description']}")
    print(f"Tags: {', '.join(script_data['tags'][:5])}")

    print("\n[NOTE] This video has SILENT audio (60s)")
    print("When ElevenLabs works, use create_video.py for voice")

    print("\nCheck 'output' folder for your files!")

except Exception as e:
    print(f"\n[ERROR] Video creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n")
