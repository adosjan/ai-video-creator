"""
Midjourney Integration via Discord
Generates images using Midjourney bot through Discord API
"""

import discord
import asyncio
import aiohttp
from typing import Optional
from pathlib import Path
from config import settings, TEMP_DIR
import time


class MidjourneyClient:
    """Handles Midjourney image generation through Discord"""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        server_id: Optional[str] = None,
        channel_id: Optional[str] = None
    ):
        """
        Initialize Midjourney client

        Args:
            bot_token: Discord bot token
            server_id: Discord server ID where Midjourney bot is present
            channel_id: Channel ID to send commands to
        """
        self.bot_token = bot_token or (settings.discord_bot_token if settings else None)
        self.server_id = server_id or (settings.midjourney_server_id if settings else None)
        self.channel_id = channel_id or (settings.midjourney_channel_id if settings else None)

        if not all([self.bot_token, self.server_id, self.channel_id]):
            raise ValueError("Discord bot token, server ID, and channel ID are required")

        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)

        self.generated_image_url = None
        self.is_ready = False

        # Setup event handlers
        @self.client.event
        async def on_ready():
            print(f"[OK] Discord bot logged in as {self.client.user}")
            self.is_ready = True

        @self.client.event
        async def on_message(message):
            await self._handle_message(message)

    async def _handle_message(self, message):
        """Handle incoming Discord messages (looking for Midjourney results)"""
        # Check if message is from Midjourney bot
        if message.author.name == "Midjourney Bot" or message.author.id == 936929561302675456:
            # Check if message has attachments (generated images)
            if message.attachments:
                # Get the first attachment (usually the generated image)
                self.generated_image_url = message.attachments[0].url
                print(f"[*] Image generated: {self.generated_image_url}")

    async def start_bot(self):
        """Start the Discord bot"""
        await self.client.start(self.bot_token)

    async def send_imagine_command(self, prompt: str) -> str:
        """
        Send /imagine command to Midjourney

        Args:
            prompt: Midjourney prompt

        Returns:
            URL of generated image
        """
        # Wait for bot to be ready
        timeout = 30
        start_time = time.time()
        while not self.is_ready:
            if time.time() - start_time > timeout:
                raise TimeoutError("Bot failed to connect within timeout")
            await asyncio.sleep(0.5)

        # Get channel
        channel = self.client.get_channel(int(self.channel_id))
        if not channel:
            raise ValueError(f"Could not find channel with ID: {self.channel_id}")

        # Send command
        print(f"[*] Sending Midjourney prompt: {prompt[:100]}...")

        # Note: This sends a text message. For actual /imagine command,
        # you need to interact with Midjourney bot's slash command
        # This is a simplified version - actual implementation would use interactions
        await channel.send(f"/imagine prompt: {prompt}")

        # Wait for image to be generated (with timeout)
        self.generated_image_url = None
        timeout = 120  # 2 minutes max wait
        start_time = time.time()

        while not self.generated_image_url:
            if time.time() - start_time > timeout:
                raise TimeoutError("Image generation timed out")
            await asyncio.sleep(2)

        return self.generated_image_url

    async def download_image(self, image_url: str, output_path: Optional[str] = None) -> str:
        """
        Download generated image from URL

        Args:
            image_url: URL of the image to download
            output_path: Where to save the image

        Returns:
            Path to downloaded image
        """
        if output_path is None:
            output_path = str(TEMP_DIR / "midjourney_image.png")

        print(f"[*] Downloading image...")

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    print(f"[OK] Image saved: {output_path}")
                    return output_path
                else:
                    raise Exception(f"Failed to download image: HTTP {response.status}")

    def generate_image_sync(self, prompt: str, output_path: Optional[str] = None) -> str:
        """
        Synchronous wrapper for image generation

        Args:
            prompt: Midjourney prompt
            output_path: Where to save the image

        Returns:
            Path to generated image
        """
        async def _generate():
            # Start bot in background
            bot_task = asyncio.create_task(self.start_bot())

            try:
                # Send command and wait for result
                image_url = await self.send_imagine_command(prompt)

                # Download image
                image_path = await self.download_image(image_url, output_path)

                return image_path
            finally:
                # Close bot connection
                await self.client.close()
                try:
                    await bot_task
                except:
                    pass

        return asyncio.run(_generate())


class SimplifiedMidjourneyClient:
    """
    Simplified Midjourney client for users who prefer manual generation
    Provides prompts and instructions instead of full automation
    """

    def __init__(self):
        self.prompts_generated = []

    def generate_prompt(self, description: str, style: str = "professional") -> str:
        """
        Generate optimized Midjourney prompt

        Args:
            description: What you want to generate
            style: Style preset (professional, dramatic, artistic, etc.)

        Returns:
            Optimized Midjourney prompt
        """
        style_presets = {
            "professional": "professional photography, studio lighting, high detail, 8k, sharp focus",
            "dramatic": "dramatic lighting, cinematic, epic composition, moody atmosphere, ultra detailed",
            "artistic": "digital art, trending on artstation, highly detailed, vibrant colors, concept art",
            "youtube": "youtube thumbnail style, attention-grabbing, vibrant colors, dramatic, professional",
        }

        base_style = style_presets.get(style, style_presets["professional"])

        prompt = f"{description}, {base_style} --ar 16:9 --v 6"

        self.prompts_generated.append(prompt)
        return prompt

    def get_instructions(self) -> str:
        """Get manual instructions for using Midjourney"""
        return """
Manual Midjourney Instructions:

1. Open Discord and go to your Midjourney server
2. Go to a generation channel
3. Type: /imagine
4. Paste the prompt generated by this tool
5. Wait for Midjourney to generate the image (~60 seconds)
6. Right-click on the generated image and save it
7. Place the saved image in the 'temp' folder

Automated generation requires proper Discord bot setup.
        """


# Example usage
if __name__ == "__main__":
    print("\n=== Midjourney Integration Test ===\n")

    # Option 1: Simplified client (generates prompts only)
    print("Option 1: Simplified Client (Manual Generation)")
    simple_client = SimplifiedMidjourneyClient()

    prompt = simple_client.generate_prompt(
        description="AI robot with glowing blue eyes, futuristic technology",
        style="youtube"
    )

    print(f"\nGenerated Prompt:\n{prompt}\n")
    print(simple_client.get_instructions())

    # Option 2: Full automated client (requires setup)
    print("\n" + "="*50)
    print("Option 2: Automated Client (Requires Discord Bot Setup)")
    print("="*50)

    try:
        # This requires proper Discord bot setup
        # client = MidjourneyClient()
        # image_path = client.generate_image_sync(prompt)
        # print(f"[OK] Image generated: {image_path}")

        print("\n[WARNING] Automated generation requires:")
        print("1. Discord bot token")
        print("2. Server ID where Midjourney is present")
        print("3. Channel ID for generation")
        print("\nSet these in your .env file:")
        print("- DISCORD_BOT_TOKEN")
        print("- MIDJOURNEY_SERVER_ID")
        print("- MIDJOURNEY_CHANNEL_ID")

    except ValueError as e:
        print(f"\n[ERROR] {e}")
