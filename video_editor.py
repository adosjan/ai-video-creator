"""
Video Editor Module
Creates videos from images, audio, and text
"""

from moviepy.editor import (
    ImageClip, AudioFileClip, VideoFileClip,
    CompositeVideoClip, TextClip, concatenate_videoclips
)
from moviepy.video.fx import resize, fadein, fadeout
from pathlib import Path
from typing import List, Optional, Dict
from config import OUTPUT_DIR, TEMP_DIR
import subprocess


class VideoEditor:
    """Handles video creation and editing"""

    def __init__(self, fps: int = 30):
        """
        Initialize video editor

        Args:
            fps: Frames per second for output video
        """
        self.fps = fps

    def create_simple_video(
        self,
        images: List[str],
        audio_path: str,
        output_path: Optional[str] = None,
        duration_per_image: Optional[float] = None
    ) -> str:
        """
        Create video from images and audio

        Args:
            images: List of image paths
            audio_path: Path to audio file
            output_path: Output path for video
            duration_per_image: Duration to show each image (if None, auto-calculates)

        Returns:
            Path to created video
        """
        print(f"[*] Creating video from {len(images)} images and audio...")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "output_video.mp4")

        # Load audio
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration

        # Calculate duration per image if not specified
        if duration_per_image is None:
            duration_per_image = audio_duration / len(images)

        print(f"[*] Audio duration: {audio_duration:.2f}s")
        print(f"[*] Duration per image: {duration_per_image:.2f}s")

        # Create clips from images
        clips = []
        for i, image_path in enumerate(images):
            print(f"  Processing image {i+1}/{len(images)}...")
            clip = ImageClip(image_path, duration=duration_per_image)
            clip = clip.set_fps(self.fps)

            # Add fade in/out for smooth transitions
            if len(images) > 1:
                clip = clip.fadein(0.5).fadeout(0.5)

            clips.append(clip)

        # Concatenate all clips
        video = concatenate_videoclips(clips, method="compose")

        # Trim or loop video to match audio duration
        if video.duration < audio_duration:
            # Loop video if shorter than audio
            times_to_loop = int(audio_duration / video.duration) + 1
            video = concatenate_videoclips([video] * times_to_loop)

        video = video.set_duration(audio_duration)

        # Add audio
        video = video.set_audio(audio)

        # Write output
        print("💾 Writing video file...")
        video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(TEMP_DIR / 'temp_audio.m4a'),
            remove_temp=True,
            logger=None  # Suppress moviepy logs
        )

        print(f"[OK] Video created: {output_path}")

        # Clean up
        audio.close()
        video.close()

        return output_path

    def create_slideshow_video(
        self,
        images_with_durations: List[Dict[str, any]],
        audio_path: str,
        output_path: Optional[str] = None,
        add_zoom_effect: bool = True
    ) -> str:
        """
        Create slideshow video with custom durations and effects

        Args:
            images_with_durations: List of dicts with 'path' and 'duration'
            audio_path: Path to audio file
            output_path: Output path
            add_zoom_effect: Add Ken Burns zoom effect

        Returns:
            Path to created video
        """
        print(f"[*] Creating slideshow video...")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "slideshow_video.mp4")

        # Load audio
        audio = AudioFileClip(audio_path)

        # Create clips
        clips = []
        for i, item in enumerate(images_with_durations):
            image_path = item['path']
            duration = item['duration']

            print(f"  Processing image {i+1}/{len(images_with_durations)}...")

            clip = ImageClip(image_path, duration=duration)
            clip = clip.set_fps(self.fps)

            # Add zoom effect
            if add_zoom_effect:
                clip = self._add_ken_burns_effect(clip)

            # Add transitions
            clip = clip.fadein(0.5).fadeout(0.5)

            clips.append(clip)

        # Concatenate
        video = concatenate_videoclips(clips, method="compose")

        # Adjust duration to match audio
        video = video.set_duration(min(video.duration, audio.duration))
        audio = audio.set_duration(video.duration)

        # Add audio
        video = video.set_audio(audio)

        # Write output
        print("💾 Writing video file...")
        video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(TEMP_DIR / 'temp_audio.m4a'),
            remove_temp=True,
            logger=None
        )

        print(f"[OK] Slideshow video created: {output_path}")

        # Clean up
        audio.close()
        video.close()

        return output_path

    def _add_ken_burns_effect(self, clip):
        """Add Ken Burns (zoom) effect to clip"""
        def zoom(get_frame, t):
            frame = get_frame(t)
            zoom_factor = 1 + 0.1 * (t / clip.duration)  # Zoom from 1.0 to 1.1
            return resize.resize(frame, zoom_factor)

        return clip.fl(zoom)

    def create_text_overlay_video(
        self,
        background_video_or_image: str,
        text_segments: List[Dict],
        audio_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create video with text overlays (like subtitles)

        Args:
            background_video_or_image: Background video or image
            text_segments: List of {'text': str, 'start': float, 'end': float}
            audio_path: Audio path
            output_path: Output path

        Returns:
            Path to created video
        """
        print(f"[*] Creating video with text overlays...")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "text_overlay_video.mp4")

        # Load background
        if background_video_or_image.endswith(('.mp4', '.avi', '.mov')):
            background = VideoFileClip(background_video_or_image)
        else:
            audio = AudioFileClip(audio_path)
            background = ImageClip(background_video_or_image, duration=audio.duration)
            background = background.set_fps(self.fps)
            audio.close()

        # Load audio
        audio = AudioFileClip(audio_path)
        background = background.set_audio(audio)

        # Create text clips
        text_clips = []
        for segment in text_segments:
            txt_clip = TextClip(
                segment['text'],
                fontsize=50,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(background.w * 0.8, None)
            )
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(segment['start']).set_end(segment['end'])
            text_clips.append(txt_clip)

        # Composite
        video = CompositeVideoClip([background] + text_clips)

        # Write output
        print("💾 Writing video file...")
        video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(TEMP_DIR / 'temp_audio.m4a'),
            remove_temp=True,
            logger=None
        )

        print(f"[OK] Video with text overlays created: {output_path}")

        # Clean up
        audio.close()
        background.close()
        video.close()

        return output_path

    def add_background_music(
        self,
        video_path: str,
        music_path: str,
        output_path: Optional[str] = None,
        music_volume: float = 0.3
    ) -> str:
        """
        Add background music to existing video

        Args:
            video_path: Path to video
            music_path: Path to music file
            output_path: Output path
            music_volume: Volume of background music (0.0-1.0)

        Returns:
            Path to video with music
        """
        if output_path is None:
            output_path = str(OUTPUT_DIR / "video_with_music.mp4")

        # Use ffmpeg directly for better performance
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', music_path,
            '-filter_complex',
            f'[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=shortest',
            '-c:v', 'copy',
            '-c:a', 'aac',
            output_path,
            '-y'
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[OK] Background music added: {output_path}")

        return output_path

    def create_youtube_short(
        self,
        image_or_video: str,
        audio_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create YouTube Short (9:16 aspect ratio, max 60 seconds)

        Args:
            image_or_video: Background image or video
            audio_path: Audio path
            output_path: Output path

        Returns:
            Path to YouTube Short
        """
        print(f"[*] Creating YouTube Short (9:16 aspect ratio)...")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "youtube_short.mp4")

        # Load audio
        audio = AudioFileClip(audio_path)

        # Limit to 60 seconds
        max_duration = 60
        if audio.duration > max_duration:
            audio = audio.subclip(0, max_duration)

        # Load background
        if image_or_video.endswith(('.mp4', '.avi', '.mov')):
            background = VideoFileClip(image_or_video)
        else:
            background = ImageClip(image_or_video, duration=audio.duration)
            background = background.set_fps(self.fps)

        # Resize to 9:16 (1080x1920)
        target_width = 1080
        target_height = 1920

        # Crop to 9:16 aspect ratio
        background = self._crop_to_aspect_ratio(background, target_width, target_height)

        # Set audio
        background = background.set_audio(audio)

        # Write output
        print("💾 Writing YouTube Short...")
        background.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(TEMP_DIR / 'temp_audio.m4a'),
            remove_temp=True,
            logger=None
        )

        print(f"[OK] YouTube Short created: {output_path}")

        # Clean up
        audio.close()
        background.close()

        return output_path

    def _crop_to_aspect_ratio(self, clip, target_width: int, target_height: int):
        """Crop clip to target aspect ratio"""
        # Calculate target aspect ratio
        target_aspect = target_width / target_height

        # Get current dimensions
        current_width, current_height = clip.size
        current_aspect = current_width / current_height

        if current_aspect > target_aspect:
            # Too wide - crop width
            new_width = int(current_height * target_aspect)
            x1 = (current_width - new_width) // 2
            clip = clip.crop(x1=x1, width=new_width)
        else:
            # Too tall - crop height
            new_height = int(current_width / target_aspect)
            y1 = (current_height - new_height) // 2
            clip = clip.crop(y1=y1, height=new_height)

        # Resize to target dimensions
        clip = clip.resize((target_width, target_height))

        return clip


# Example usage
if __name__ == "__main__":
    print("\n=== Video Editor Test ===\n")

    editor = VideoEditor()

    print("Video editor initialized!")
    print("\nAvailable methods:")
    print("- create_simple_video(images, audio)")
    print("- create_slideshow_video(images_with_durations, audio)")
    print("- create_youtube_short(image_or_video, audio)")
    print("- create_text_overlay_video(background, text_segments, audio)")

    print("\n[WARNING] To test, provide image and audio files")
