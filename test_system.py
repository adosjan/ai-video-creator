"""
Simple test script for AI Video Creator (no emojis for Windows compatibility)
"""

print("\n" + "="*60)
print(" AI VIDEO CREATOR - SYSTEM TEST")
print("="*60 + "\n")

# Test imports
print("Testing imports...")
try:
    from youtube_analyzer import YouTubeAnalyzer
    print("[OK] YouTube Analyzer")
except Exception as e:
    print(f"[ERROR] YouTube Analyzer: {e}")

try:
    from script_generator import ScriptGenerator
    print("[OK] Script Generator")
except Exception as e:
    print(f"[ERROR] Script Generator: {e}")

try:
    from elevenlabs_tts import ElevenLabsTTS
    print("[OK] ElevenLabs TTS")
except Exception as e:
    print(f"[ERROR] ElevenLabs TTS: {e}")

try:
    from midjourney_bot import SimplifiedMidjourneyClient
    print("[OK] Midjourney Client")
except Exception as e:
    print(f"[ERROR] Midjourney Client: {e}")

try:
    from thumbnail_generator import ThumbnailGenerator
    print("[OK] Thumbnail Generator")
except Exception as e:
    print(f"[ERROR] Thumbnail Generator: {e}")

try:
    from video_editor import VideoEditor
    print("[OK] Video Editor")
except Exception as e:
    print(f"[ERROR] Video Editor: {e}")

# Test configuration
print("\nTesting configuration...")
try:
    from config import settings

    if settings:
        print("[OK] Configuration loaded")
        print(f"    OpenAI API Key: {'SET' if settings.openai_api_key else 'MISSING'}")
        print(f"    ElevenLabs API Key: {'SET' if settings.elevenlabs_api_key else 'MISSING'}")
        print(f"    ElevenLabs Voice ID: {'SET' if settings.elevenlabs_voice_id else 'MISSING'}")
    else:
        print("[ERROR] Configuration not loaded - check .env file")
except Exception as e:
    print(f"[ERROR] Configuration: {e}")

print("\n" + "="*60)
print(" SYSTEM STATUS")
print("="*60)

# Check if all required components are ready
try:
    from config import settings
    if settings and settings.openai_api_key and settings.elevenlabs_api_key:
        print("\n[SUCCESS] All systems ready!")
        print("\nYou can now create videos using:")
        print("  python -c \"from main import VideoCreator; creator = VideoCreator()\"")
        print("\nOr import in your code:")
        print("  from main import VideoCreator")
        print("  creator = VideoCreator()")
        print("  result = creator.create_from_url('https://youtube.com/...')")
    else:
        print("\n[WARNING] Missing API keys in .env file")
        print("Please check your .env file and add:")
        print("  - OPENAI_API_KEY")
        print("  - ELEVENLABS_API_KEY")
        print("  - ELEVENLABS_VOICE_ID")
except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n")
