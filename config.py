# -*- coding: utf-8 -*-
"""
Configuration file with Gemini support
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with Gemini support"""
    
    # Google Gemini API (FREE!) - get at: https://makersuite.google.com/app/apikey
    gemini_api_key: str = ""
    
    # OpenAI API (optional backup, if you have credits)
    openai_api_key: str = ""
    
    # ElevenLabs (for voice)
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "pNInz6obpgDQGcFmaJgB"  # Adam voice
    
    # Discord (for Midjourney - optional)
    discord_bot_token: str = ""
    discord_channel_id: str = ""
    midjourney_bot_id: str = "936929561302675456"
    
    # Video generation settings
    video_length: str = "short"  # short, medium, long
    thumbnail_style: str = "clickbait"  # clickbait, professional, educational
    use_manual_midjourney: bool = True  # True = manual, False = automated
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


# Video length presets
VIDEO_LENGTHS = {
    "short": {
        "duration_seconds": 60,
        "word_count": "100-150",
        "description": "30-90 second videos (perfect for YouTube Shorts)"
    },
    "medium": {
        "duration_seconds": 240,
        "word_count": "300-600",
        "description": "2-5 minute videos (standard YouTube)"
    },
    "long": {
        "duration_seconds": 480,
        "word_count": "800-1200",
        "description": "5-10 minute videos (deep dive content)"
    }
}


# Thumbnail styles
THUMBNAIL_STYLES = {
    "clickbait": {
        "font_size_multiplier": 1.2,
        "use_caps": True,
        "color_scheme": "bright",
        "add_emoji": True
    },
    "professional": {
        "font_size_multiplier": 1.0,
        "use_caps": False,
        "color_scheme": "clean",
        "add_emoji": False
    },
    "educational": {
        "font_size_multiplier": 1.1,
        "use_caps": False,
        "color_scheme": "academic",
        "add_emoji": False
    }
}
