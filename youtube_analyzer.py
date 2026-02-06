"""
YouTube Video Analyzer
Extracts transcripts, metadata, and analyzes video structure
"""

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Dict, List, Optional
import re
from datetime import timedelta


class YouTubeAnalyzer:
    """Analyzes YouTube videos to extract content and metadata"""

    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)',
            r'youtube\.com/embed/([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValueError(f"Could not extract video ID from URL: {url}")

    def get_video_metadata(self, url: str) -> Dict:
        """
        Get video metadata using yt-dlp
        Returns title, description, duration, views, etc.
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                metadata = {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),  # seconds
                    'duration_formatted': str(timedelta(seconds=info.get('duration', 0))),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'channel': info.get('channel'),
                    'channel_id': info.get('channel_id'),
                    'upload_date': info.get('upload_date'),
                    'thumbnail_url': info.get('thumbnail'),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                }

                return metadata
        except Exception as e:
            raise Exception(f"Error getting video metadata: {str(e)}")

    def get_transcript(self, video_id: str, languages: List[str] = ['en']) -> Optional[str]:
        """
        Get video transcript/subtitles
        Returns full transcript as text
        """
        try:
            # Try to get transcript using list_transcripts first
            transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try to find a transcript in desired languages
            transcript = None
            for lang in languages:
                try:
                    transcript = transcript_list_obj.find_transcript([lang])
                    break
                except:
                    continue

            # If no transcript in desired language, try to get any available transcript
            if not transcript:
                try:
                    transcript = transcript_list_obj.find_generated_transcript(['en'])
                except:
                    # Try any available transcript
                    available = list(transcript_list_obj)
                    if available:
                        transcript = available[0]

            if transcript:
                transcript_data = transcript.fetch()
                full_transcript = ' '.join([entry['text'] for entry in transcript_data])
                return full_transcript

            return None

        except Exception as e:
            print(f"[WARNING] Could not get transcript: {str(e)}")
            return None

    def analyze_video_structure(self, transcript: str) -> Dict:
        """
        Analyze video structure from transcript
        Identifies intro, main content, outro
        """
        if not transcript:
            return {}

        words = transcript.split()
        total_words = len(words)

        # Simple structure analysis
        structure = {
            'total_words': total_words,
            'estimated_speaking_time': total_words / 150,  # ~150 words per minute
            'has_intro': self._detect_intro(transcript),
            'has_outro': self._detect_outro(transcript),
            'key_topics': self._extract_key_topics(transcript),
        }

        return structure

    def _detect_intro(self, transcript: str) -> bool:
        """Detect if video has intro (greetings, channel intro)"""
        intro_keywords = ['hey', 'hi', 'hello', 'welcome', 'what\'s up', 'today']
        first_100_words = ' '.join(transcript.split()[:100]).lower()
        return any(keyword in first_100_words for keyword in intro_keywords)

    def _detect_outro(self, transcript: str) -> bool:
        """Detect if video has outro (call to action, goodbye)"""
        outro_keywords = ['subscribe', 'like', 'comment', 'thanks for watching', 'see you']
        last_100_words = ' '.join(transcript.split()[-100:]).lower()
        return any(keyword in last_100_words for keyword in outro_keywords)

    def _extract_key_topics(self, transcript: str, top_n: int = 5) -> List[str]:
        """Extract key topics from transcript (simple word frequency)"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'is', 'was', 'are', 'were', 'this', 'that', 'it', 'be'}

        words = re.findall(r'\w+', transcript.lower())
        words = [w for w in words if w not in stop_words and len(w) > 3]

        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top N words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [word for word, count in top_words]

    def analyze_full_video(self, url: str) -> Dict:
        """
        Complete video analysis
        Returns metadata, transcript, and structure analysis
        """
        print(f"[*] Analyzing video: {url}")

        # Extract video ID
        video_id = self.extract_video_id(url)
        print(f"[*] Video ID: {video_id}")

        # Get metadata
        print("[*] Fetching metadata...")
        metadata = self.get_video_metadata(url)

        # Get transcript
        print("[*] Fetching transcript...")
        transcript = self.get_transcript(video_id)

        # Analyze structure
        structure = {}
        if transcript:
            print("[*] Analyzing structure...")
            structure = self.analyze_video_structure(transcript)

        result = {
            'video_id': video_id,
            'url': url,
            'metadata': metadata,
            'transcript': transcript,
            'structure': structure,
            'success': True
        }

        print("[OK] Analysis complete!")
        return result


# Example usage
if __name__ == "__main__":
    analyzer = YouTubeAnalyzer()

    # Test with a video URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        result = analyzer.analyze_full_video(test_url)

        print("\n=== Video Analysis Results ===")
        print(f"Title: {result['metadata']['title']}")
        print(f"Channel: {result['metadata']['channel']}")
        print(f"Duration: {result['metadata']['duration_formatted']}")
        print(f"Views: {result['metadata']['view_count']:,}")

        if result['transcript']:
            print(f"\nTranscript length: {len(result['transcript'])} characters")
            print(f"Key topics: {result['structure']['key_topics']}")
        else:
            print("\n[WARNING] No transcript available")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
