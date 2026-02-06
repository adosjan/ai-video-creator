# -*- coding: utf-8 -*-
"""
Create AI Video - Simple Script
Just edit the URL and run!
"""

from main import VideoCreator

# YouTube URL to analyze (change this to any video you want)
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print("\n" + "="*60)
print(" CREATING VIDEO FROM YOUTUBE URL")
print("="*60)
print(f"\nSource URL: {youtube_url}\n")

# Initialize creator
creator = VideoCreator(
    video_length="short",       # "short" (60s), "medium" (5min), "long" (15min)
    thumbnail_style="clickbait",  # "clickbait", "professional", "educational"
    use_manual_midjourney=True  # True = you create images manually
)

# Create video
result = creator.create_from_url(youtube_url)

# Show results
if result['success']:
    print("\n" + "="*60)
    print(" VIDEO CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"\nTitle: {result['title']}")
    print(f"Video: {result['video_path']}")
    print(f"Thumbnail: {result['thumbnail_path']}")
    print(f"\nTags: {', '.join(result['tags'][:5])}")
    print("\nCheck the 'output' folder for your video!")
else:
    print("\n[ERROR] Video creation failed:")
    print(result.get('error', 'Unknown error'))

print("\n")
