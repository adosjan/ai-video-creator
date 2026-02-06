"""
Thumbnail Generator
Creates YouTube thumbnails by combining Midjourney images with text overlay
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
from typing import Optional, Tuple
from config import settings, TEMP_DIR, get_thumbnail_style
import requests
from io import BytesIO


class ThumbnailGenerator:
    """Generates YouTube thumbnails with text overlay"""

    def __init__(self, style: str = "clickbait"):
        """
        Initialize thumbnail generator

        Args:
            style: Thumbnail style (clickbait, professional, educational)
        """
        self.style_config = get_thumbnail_style(style)
        self.default_size = (1280, 720)  # YouTube thumbnail size

    def create_thumbnail(
        self,
        background_image_path: str,
        text: str,
        output_path: Optional[str] = None,
        add_elements: bool = True
    ) -> str:
        """
        Create thumbnail with text overlay

        Args:
            background_image_path: Path to background image (from Midjourney)
            text: Text to overlay
            output_path: Output path for thumbnail
            add_elements: Add arrows/circles/elements

        Returns:
            Path to generated thumbnail
        """
        print(f"[*] Creating thumbnail with text: '{text}'")

        if output_path is None:
            output_path = str(TEMP_DIR / "thumbnail.jpg")

        # Load and resize background
        img = Image.open(background_image_path)
        img = img.resize(self.default_size, Image.Resampling.LANCZOS)

        # Enhance image (make it pop)
        img = self._enhance_image(img)

        # Add dark overlay for text readability
        img = self._add_overlay(img)

        # Add text
        img = self._add_text(img, text)

        # Add elements if requested
        if add_elements and self.style_config.get('add_arrows'):
            img = self._add_elements(img)

        # Save
        img.save(output_path, 'JPEG', quality=95)
        print(f"[OK] Thumbnail created: {output_path}")

        return output_path

    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """Enhance image colors and contrast"""
        # Increase saturation
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)

        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)

        return img

    def _add_overlay(self, img: Image.Image, opacity: int = 60) -> Image.Image:
        """Add semi-transparent overlay for text readability"""
        overlay = Image.new('RGBA', img.size, (0, 0, 0, opacity))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        return img.convert('RGB')

    def _add_text(self, img: Image.Image, text: str) -> Image.Image:
        """Add text overlay with outline"""
        draw = ImageDraw.Draw(img)

        # Get font (try to use bold font)
        font_size = self.style_config.get('font_size', 100)
        try:
            # Try to load a bold font (adjust path as needed)
            font = ImageFont.truetype("arial.ttf", font_size)
            outline_font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                # Try Impact font (common on Windows)
                font = ImageFont.truetype("impact.ttf", font_size)
                outline_font = ImageFont.truetype("impact.ttf", font_size)
            except:
                # Fallback to default
                font = ImageFont.load_default()
                outline_font = font

        # Word wrap text if too long
        text = self._wrap_text(text, max_chars_per_line=20)

        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center text
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2

        # Draw text outline (for better visibility)
        outline_width = self.style_config.get('outline_width', 5)
        outline_color = self.style_config.get('outline_color', (0, 0, 0))
        text_color = self.style_config.get('text_color', (255, 255, 0))

        # Draw outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                draw.text((x + adj_x, y + adj_y), text, font=outline_font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

        return img

    def _wrap_text(self, text: str, max_chars_per_line: int = 20) -> str:
        """Wrap text to multiple lines"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_chars_per_line:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def _add_elements(self, img: Image.Image) -> Image.Image:
        """Add arrows, circles, and other elements"""
        draw = ImageDraw.Draw(img, 'RGBA')

        # Add some decorative elements (arrows, circles)
        # This is simplified - you can make it more sophisticated

        # Red arrow in corner
        arrow_color = (255, 0, 0, 200)
        arrow_points = [(1100, 100), (1150, 150), (1100, 200), (1130, 150)]
        draw.polygon(arrow_points, fill=arrow_color)

        # Circle around important area (center)
        if self.style_config.get('add_circles'):
            circle_color = (255, 255, 0, 100)
            circle_bbox = [400, 250, 880, 470]
            draw.ellipse(circle_bbox, outline=circle_color, width=10)

        return img

    def download_image_from_url(self, url: str, output_path: Optional[str] = None) -> str:
        """
        Download image from URL

        Args:
            url: Image URL
            output_path: Where to save

        Returns:
            Path to downloaded image
        """
        if output_path is None:
            output_path = str(TEMP_DIR / "downloaded_image.png")

        print(f"[*] Downloading image from URL...")
        response = requests.get(url)

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(output_path)
            print(f"[OK] Image downloaded: {output_path}")
            return output_path
        else:
            raise Exception(f"Failed to download image: HTTP {response.status_code}")

    def create_simple_thumbnail(
        self,
        text: str,
        background_color: Tuple[int, int, int] = (100, 50, 200),
        output_path: Optional[str] = None
    ) -> str:
        """
        Create simple thumbnail with gradient background (no Midjourney needed)

        Args:
            text: Text for thumbnail
            background_color: Base color for gradient
            output_path: Output path

        Returns:
            Path to generated thumbnail
        """
        if output_path is None:
            output_path = str(TEMP_DIR / "thumbnail_simple.jpg")

        # Create gradient background
        img = self._create_gradient_background(background_color)

        # Add text
        img = self._add_text(img, text)

        # Save
        img.save(output_path, 'JPEG', quality=95)
        print(f"[OK] Simple thumbnail created: {output_path}")

        return output_path

    def _create_gradient_background(self, base_color: Tuple[int, int, int]) -> Image.Image:
        """Create gradient background"""
        img = Image.new('RGB', self.default_size, base_color)
        draw = ImageDraw.Draw(img)

        # Create gradient
        r, g, b = base_color
        for i in range(img.height):
            # Darken as we go down
            factor = 1 - (i / img.height) * 0.5
            color = (int(r * factor), int(g * factor), int(b * factor))
            draw.line([(0, i), (img.width, i)], fill=color)

        return img


# Example usage
if __name__ == "__main__":
    generator = ThumbnailGenerator(style="clickbait")

    # Test 1: Simple thumbnail (no Midjourney needed)
    print("\n=== Test 1: Simple Thumbnail ===")
    simple_thumb = generator.create_simple_thumbnail(
        text="AI WILL CHANGE EVERYTHING",
        background_color=(60, 0, 120)
    )
    print(f"Created: {simple_thumb}")

    # Test 2: With background image (if you have one)
    print("\n=== Test 2: Thumbnail with Background ===")
    # This requires a background image
    # thumb = generator.create_thumbnail(
    #     background_image_path="path/to/midjourney/image.png",
    #     text="SHOCKING AI NEWS"
    #)

    print("\n[OK] Thumbnail generator ready!")
    print("Use create_thumbnail() with a Midjourney background image")
    print("Or use create_simple_thumbnail() for gradient backgrounds")
