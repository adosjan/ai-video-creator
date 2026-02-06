"""
AI Script Generator
Creates unique video scripts based on analyzed content
Now using Google Gemini - COMPLETELY FREE!
"""

import google.generativeai as genai
from typing import Dict, Optional
from config import settings


class ScriptGenerator:
    """Generates unique video scripts using Google Gemini AI (FREE!)"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize script generator with Gemini

        Args:
            api_key: Google Gemini API key (if not provided, uses config)
            model: Gemini model to use (default: gemini-pro)
        """
        self.api_key = api_key or (settings.gemini_api_key if settings else None)
        if not self.api_key:
            raise ValueError("Gemini API key is required. Get free at: https://makersuite.google.com/app/apikey")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model

    def generate_script(
        self,
        video_analysis: Dict,
        target_length: str = "short",
        style: str = "engaging",
        custom_instructions: Optional[str] = None
    ) -> Dict:
        """
        Generate a unique video script based on analyzed video

        Args:
            video_analysis: Result from YouTubeAnalyzer.analyze_full_video()
            target_length: "short" (60s), "medium" (5min), "long" (15min)
            style: "engaging", "educational", "dramatic", "casual"
            custom_instructions: Additional instructions for AI

        Returns:
            Dict with script, title, description, and metadata
        """
        print(f"[*] Generating {style} script ({target_length}) with Gemini...")

        # Extract key information from analysis
        original_title = video_analysis['metadata']['title']
        transcript = video_analysis.get('transcript', '')
        key_topics = video_analysis['structure'].get('key_topics', [])

        # Calculate target word count based on length
        word_counts = {
            "short": 150,   # ~60 seconds at 150 words/min
            "medium": 750,  # ~5 minutes
            "long": 2250    # ~15 minutes
        }
        target_words = word_counts.get(target_length, 150)

        # Build prompt
        prompt = self._build_prompt(
            original_title=original_title,
            transcript=transcript,
            key_topics=key_topics,
            target_words=target_words,
            style=style,
            custom_instructions=custom_instructions
        )

        # Generate script using Gemini (FREE!)
        try:
            response = self.model.generate_content(prompt)
            content = response.text

            # Parse the response
            result = self._parse_ai_response(content)
            result['success'] = True
            result['target_length'] = target_length
            result['style'] = style

            print("[OK] Script generated successfully with Gemini (FREE)!")
            return result

        except Exception as e:
            print(f"[ERROR] Error generating script: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_prompt(
        self,
        original_title: str,
        transcript: str,
        key_topics: list,
        target_words: int,
        style: str,
        custom_instructions: Optional[str]
    ) -> str:
        """Build the prompt for AI"""

        # Truncate transcript if too long (to fit in context)
        max_transcript_length = 3000
        if transcript and len(transcript) > max_transcript_length:
            transcript = transcript[:max_transcript_length] + "..."
        elif not transcript:
            transcript = "(No transcript available - will create script based on metadata only)"

        prompt = f"""
You are an expert YouTube content creator who specializes in creating engaging, unique video scripts. You understand viral content patterns and create original, transformative content.

I need you to create a UNIQUE and ORIGINAL video script based on a popular video topic.

IMPORTANT RULES:
1. DO NOT copy the original script word-for-word
2. DO NOT use the exact same examples or stories
3. DO create NEW content on the same topic
4. DO add your own perspective and insights
5. DO make it transformative and unique

ORIGINAL VIDEO INFORMATION:
Title: {original_title}
Key Topics: {', '.join(key_topics) if key_topics else 'N/A'}

ORIGINAL TRANSCRIPT (for reference only):
{transcript if transcript else 'Not available'}

YOUR TASK:
Create a {style} video script about this topic that is:
- Approximately {target_words} words (~{target_words/150:.1f} minutes when spoken)
- {style.upper()} in tone and style
- Unique and original (not a copy)
- Engaging and hooks viewers in first 5 seconds
- Has clear structure (intro, main content, call-to-action)

{f'ADDITIONAL INSTRUCTIONS: {custom_instructions}' if custom_instructions else ''}

OUTPUT FORMAT:
Please provide your response in this exact format:

TITLE: [Catchy video title, under 70 characters]

SCRIPT:
[Your complete script here, written for spoken delivery]

DESCRIPTION:
[YouTube video description, 2-3 sentences]

TAGS:
[5-10 relevant tags, comma-separated]

THUMBNAIL_TEXT:
[3-5 words for thumbnail, attention-grabbing]

Now create the script:
"""
        return prompt

    def _parse_ai_response(self, content: str) -> Dict:
        """Parse AI response into structured data"""

        result = {
            'title': '',
            'script': '',
            'description': '',
            'tags': [],
            'thumbnail_text': ''
        }

        # Simple parsing
        lines = content.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith('TITLE:'):
                result['title'] = line.replace('TITLE:', '').strip()
                current_section = None
            elif line.startswith('SCRIPT:'):
                current_section = 'script'
            elif line.startswith('DESCRIPTION:'):
                current_section = 'description'
            elif line.startswith('TAGS:'):
                tags_text = line.replace('TAGS:', '').strip()
                result['tags'] = [tag.strip() for tag in tags_text.split(',')]
                current_section = None
            elif line.startswith('THUMBNAIL_TEXT:'):
                result['thumbnail_text'] = line.replace('THUMBNAIL_TEXT:', '').strip()
                current_section = None
            elif current_section and line:
                if current_section == 'script':
                    result['script'] += line + ' '
                elif current_section == 'description':
                    result['description'] += line + ' '

        # Clean up
        result['script'] = result['script'].strip()
        result['description'] = result['description'].strip()

        return result

    def generate_thumbnail_prompt(self, script_data: Dict) -> str:
        """
        Generate Midjourney prompt for thumbnail based on script

        Args:
            script_data: Output from generate_script()

        Returns:
            Midjourney prompt string
        """
        title = script_data.get('title', '')
        thumbnail_text = script_data.get('thumbnail_text', '')

        # Use Gemini to create optimal Midjourney prompt
        prompt = f"""Create a Midjourney prompt for a YouTube thumbnail based on this video:

Title: {title}
Thumbnail Text: {thumbnail_text}

Generate a Midjourney prompt that will create an eye-catching, professional thumbnail.
Include: dramatic lighting, professional photography style, 8k quality, trending on artstation.
Make it relevant to the topic and visually striking.

OUTPUT ONLY THE MIDJOURNEY PROMPT (no explanation):"""

        try:
            response = self.model.generate_content(prompt)
            midjourney_prompt = response.text.strip()
            return midjourney_prompt

        except Exception as e:
            print(f"[WARNING] Could not generate Midjourney prompt: {e}")
            # Fallback prompt
            return f"professional youtube thumbnail, dramatic lighting, {thumbnail_text}, cinematic, 8k, trending on artstation --ar 16:9"


# Example usage
if __name__ == "__main__":
    # Mock video analysis for testing
    mock_analysis = {
        'metadata': {
            'title': '10 AI Tools That Will Change Everything',
            'channel': 'Tech Channel'
        },
        'transcript': 'Artificial intelligence is transforming how we work. In this video, I will show you the top 10 AI tools that everyone should know about...',
        'structure': {
            'key_topics': ['ai', 'tools', 'automation', 'productivity']
        }
    }

    # Initialize generator (make sure you have .env with GEMINI_API_KEY)
    try:
        generator = ScriptGenerator()

        result = generator.generate_script(
            video_analysis=mock_analysis,
            target_length="short",
            style="engaging"
        )

        if result['success']:
            print("\n=== Generated Script ===")
            print(f"Title: {result['title']}")
            print(f"\nScript Preview: {result['script'][:200]}...")
            print(f"\nThumbnail Text: {result['thumbnail_text']}")

            # Generate Midjourney prompt
            mj_prompt = generator.generate_thumbnail_prompt(result)
            print(f"\nMidjourney Prompt: {mj_prompt}")
        else:
            print(f"Error: {result['error']}")

    except ValueError as e:
        print(f"[ERROR] {e}")
        print("Please set GEMINI_API_KEY in your .env file")
        print("Get free key at: https://makersuite.google.com/app/apikey")
