# -*- coding: utf-8 -*-
"""
Create AI Video with DALL-E (instead of Midjourney)
Fully automated - uses OpenAI DALL-E 3 for images
"""

from pathlib import Path
from datetime import datetime
from youtube_analyzer import YouTubeAnalyzer
from script_generator import ScriptGenerator
from dalle_generator import DalleImageGenerator
from thumbnail_generator import ThumbnailGenerator
from video_editor import VideoEditor
from config import OUTPUT_DIR, TEMP_DIR

# YouTube URL to analyze
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print("\n" + "="*60)
print(" CREATING VIDEO WITH DALL-E (FULLY AUTOMATED)")
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

    # STEP 3: Generate image with DALL-E
    print("\n[STEP 3] Generating image with DALL-E 3...")
    dalle_prompt = script_gen.generate_thumbnail_prompt(script_data)
    print(f"\n   DALL-E Prompt:\n   {dalle_prompt}\n")

    dalle_gen = DalleImageGenerator()
    background_image = dalle_gen.generate_image(
        prompt=dalle_prompt,
        output_path=str(TEMP_DIR / f"{output_name}_background.png"),
        size="1792x1024",  # landscape for video
        quality="hd"  # high quality
    )

    print(f"[OK] DALL-E image generated: {background_image}")

    # STEP 4: Create thumbnail
    print("\n[STEP 4] Creating thumbnail...")
    thumb_gen = ThumbnailGenerator(style="clickbait")
    thumbnail_path = thumb_gen.create_thumbnail(
        background_image_path=background_image,
        text=script_data['thumbnail_text'],
        output_path=str(OUTPUT_DIR / f"{output_name}_thumbnail.jpg")
    )

    # STEP 5: Create video (60 seconds, no audio for now)
    print("\n[STEP 5] Creating video...")
    editor = VideoEditor()

    # For now, create video without audio (until ElevenLabs works)
    from moviepy.editor import ImageClip

    video_path = str(OUTPUT_DIR / f"{output_name}.mp4")
    clip = ImageClip(background_image, duration=60)
    clip = clip.set_fps(30)

    clip.write_videofile(
        video_path,
        fps=30,
        codec='libx264',
        audio=False,
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
    print(f"Background: {background_image}")
    print(f"Title: {script_data['title']}")
    print(f"Description: {script_data['description'][:100]}...")
    print(f"Tags: {', '.join(script_data['tags'][:5])}")

    print("\n" + "="*60)
    print("[NOTE] This video has NO AUDIO (60s silent)")
    print("When ElevenLabs works, voice will be added")
    print("="*60)

    print("\nGenerated Script:")
    print("-" * 60)
    # Remove emojis for Windows console compatibility
    script_text = script_data['script'].encode('ascii', 'ignore').decode('ascii')
    print(script_text)
    print("-" * 60)

    print("\nCost breakdown:")
    print("- DALL-E 3 HD image: ~$0.08")
    print("- OpenAI GPT-4o script: ~$0.01")
    print("Total cost: ~$0.09 per video")

    print("\n" + "="*60)
    print("ADVANTAGES OF DALL-E:")
    print("="*60)
    print("+ Fully automated - no manual steps")
    print("+ Official OpenAI API - no risk of ban")
    print("+ Fast generation (30-60 seconds)")
    print("+ Consistent quality")
    print("+ Already have API key")
    print("\nDISADVANTAGES:")
    print("- Costs $0.08 per image (vs Midjourney subscription)")
    print("- Less artistic control than Midjourney")
    print("="*60)

    print("\nCheck 'output' folder for your files!")
    print(f"- Video: {output_name}.mp4")
    print(f"- Thumbnail: {output_name}_thumbnail.jpg")

except Exception as e:
    print(f"\n[ERROR] Video creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n")
