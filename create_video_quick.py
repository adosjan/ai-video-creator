# -*- coding: utf-8 -*-
"""
Quick video creation - no input prompts
"""

from create_full_video import create_full_video

# Your YouTube URL
youtube_url = "https://www.youtube.com/watch?v=hSNn6iOUxvY"

# Background music (optional)
background_music = None  # Set path if you have music

print("\nCreating video from:", youtube_url)
print("This will take 1-2 minutes...\n")

create_full_video(
    youtube_url=youtube_url,
    background_music_path=background_music,
    music_volume=0.15,
    use_dalle=True  # Automatic with DALL-E
)
