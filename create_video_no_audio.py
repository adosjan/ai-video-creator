# -*- coding: utf-8 -*-
"""
Create AI Video WITHOUT Audio
Test version - just thumbnail/image for 60 seconds
"""

from pathlib import Path
from datetime import datetime
from youtube_analyzer import YouTubeAnalyzer
from script_generator import ScriptGenerator
from thumbnail_generator import ThumbnailGenerator
from config import OUTPUT_DIR, TEMP_DIR
from moviepy.editor import ImageClip

# YouTube URL to analyze
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print("\n" + "="*60)
print(" CREATING VIDEO WITHOUT AUDIO (TEST MODE)")
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
    print(f"\n   Script Preview:")
    print(f"   {script_data['script'][:200]}...")

    # STEP 3: Generate Midjourney prompt
    print("\n[STEP 3] Generating Midjourney prompt...")
    mj_prompt = script_gen.generate_thumbnail_prompt(script_data)
    print(f"\n   Midjourney Prompt:\n   {mj_prompt}\n")

    # For testing, skip Midjourney and use simple thumbnail
    print("[INFO] Skipping Midjourney step (using simple thumbnail)")
    print("To use Midjourney manually later:")
    print(f"1. Paste in Discord: {mj_prompt}")
    print(f"2. Save as: temp/{output_name}_background.png")

    background_image = None  # Always use simple thumbnail for testing

    # STEP 4: Create thumbnail
    print("\n[STEP 4] Creating thumbnail...")
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

    # STEP 5: Create video (60 seconds, no audio)
    print("\n[STEP 5] Creating 60-second video without audio...")
    video_path = str(OUTPUT_DIR / f"{output_name}.mp4")

    # Use thumbnail or background image
    image_to_use = background_image if background_image else thumbnail_path

    # Create 60-second video clip from image
    clip = ImageClip(image_to_use, duration=60)
    clip = clip.set_fps(30)

    # Write video file
    clip.write_videofile(
        video_path,
        fps=30,
        codec='libx264',
        audio=False,  # No audio
        temp_audiofile=str(TEMP_DIR / 'temp_audio.m4a'),
        remove_temp=True,
        logger=None
    )

    clip.close()

    # STEP 6: Results
    print("\n" + "="*60)
    print(" VIDEO CREATION COMPLETE!")
    print("="*60)

    print(f"\nVideo: {video_path}")
    print(f"Thumbnail: {thumbnail_path}")
    print(f"Title: {script_data['title']}")
    print(f"Description: {script_data['description'][:100]}...")
    print(f"Tags: {', '.join(script_data['tags'][:5])}")

    print("\n" + "="*60)
    print("[NOTE] This video has NO AUDIO (60s silent)")
    print("When ElevenLabs works, use create_video.py for voice")
    print("="*60)

    print("\nGenerated Script:")
    print("-" * 60)
    print(script_data['script'])
    print("-" * 60)

    print("\nCheck 'output' folder for your files!")
    print(f"- Video: {output_name}.mp4")
    print(f"- Thumbnail: {output_name}_thumbnail.jpg")

except Exception as e:
    print(f"\n[ERROR] Video creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n")
