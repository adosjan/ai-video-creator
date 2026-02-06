# -*- coding: utf-8 -*-
"""
DALL-E Image Generator
Alternative to Midjourney with official OpenAI API
"""

from openai import OpenAI
from pathlib import Path
from config import settings, TEMP_DIR
import requests
import os

class DalleImageGenerator:
    """Generate images using DALL-E 3 (official OpenAI API)"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_image(
        self,
        prompt: str,
        output_path: str = None,
        size: str = "1792x1024",  # landscape for video
        quality: str = "standard"  # or "hd" for better quality
    ) -> str:
        """
        Generate image using DALL-E 3

        Args:
            prompt: Description of image to generate
            output_path: Where to save the image
            size: Image size - "1024x1024", "1792x1024", "1024x1792"
            quality: "standard" or "hd"

        Returns:
            Path to generated image
        """
        print(f"[*] Generating image with DALL-E 3...")
        print(f"    Size: {size}, Quality: {quality}")

        try:
            # Generate image
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )

            # Get image URL
            image_url = response.data[0].url
            print(f"[OK] Image generated!")

            # Download image
            if output_path is None:
                output_path = str(TEMP_DIR / "dalle_generated.png")

            print(f"[*] Downloading image...")
            image_data = requests.get(image_url).content

            with open(output_path, 'wb') as f:
                f.write(image_data)

            print(f"[OK] Image saved: {output_path}")
            return output_path

        except Exception as e:
            print(f"[ERROR] DALL-E generation failed: {e}")
            raise


# Test usage
if __name__ == "__main__":
    print("\n=== DALL-E Image Generator Test ===\n")

    generator = DalleImageGenerator()

    test_prompt = "A dramatic cinematic scene showing a vintage cassette tape floating in space, surrounded by colorful musical notes and retro 80s style neon lights, photorealistic, epic lighting"

    print(f"Test prompt: {test_prompt}\n")

    image_path = generator.generate_image(
        prompt=test_prompt,
        size="1792x1024",  # landscape for video
        quality="hd"  # high quality
    )

    print(f"\n[OK] Test complete!")
    print(f"Image saved to: {image_path}")
    print("\nNote: DALL-E 3 costs:")
    print("- Standard quality: $0.040 per image")
    print("- HD quality: $0.080 per image")
