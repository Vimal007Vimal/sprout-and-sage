import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

FRONTEND_URL = "https://sprout-and-sage-frontend-734189490959.us-east1.run.app"
FFMPEG_EXE = "/config/.gemini/antigravity/scratch/sprout-and-sage/.venv/lib/python3.13/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
ARTIFACT_DIR = "/config/.gemini/antigravity/brain/46c7a3a9-36a9-48ae-bd9c-9ccff9f7276a"
OUTPUT_MP4 = os.path.join(ARTIFACT_DIR, "sprout_and_sage_demo.mp4")

async def record_demo():
    raw_dir = os.path.abspath("raw_recordings")
    os.makedirs(raw_dir, exist_ok=True)
    
    async with async_playwright() as p:
        print("Launching Chromium...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=raw_dir,
            record_video_size={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        print(f"Navigating to {FRONTEND_URL}...")
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # 1. Click preset prompt chip: 🌿 Show nursery stock
        print("Clicking preset prompt chip...")
        chip = page.locator(".prompt-chip").first
        if await chip.count() > 0:
            await chip.click()
        else:
            await page.fill("#input", "Show nursery stock")
            await page.click("button[type='submit']")
            
        # Wait for agent response
        print("Waiting for Nursery Inventory response...")
        await page.wait_for_selector(".msg-row.agent", timeout=30000)
        await page.wait_for_timeout(7000)  # Pause to show inventory
        
        # 2. Richer Prompt: Water requirement calculation + Image generation
        print("Sending 2nd rich prompt...")
        prompt_text = "Calculate water requirement for my Monstera in 70F with 40% humidity, and generate a picture of a flourishing Monstera Deliciosa."
        await page.fill("#input", prompt_text)
        await page.wait_for_timeout(1000)
        await page.click("button[type='submit']")
        
        print("Waiting for agent tool call & generated image response...")
        # Wait for second bot message
        await page.wait_for_timeout(28000)  # Allow full tool execution & image render
        await page.wait_for_timeout(7000)  # Pause to showcase generated image & response
        
        print("Closing browser context to finalize video recording...")
        video_path = await page.video.path()
        await context.close()
        await browser.close()
        print(f"Recorded raw WebM video at: {video_path}")
        return video_path

def merge_audio_video(webm_path, audio_wav="lofi_track.wav", output_mp4=OUTPUT_MP4):
    print(f"Combining {webm_path} and {audio_wav} into {output_mp4} using FFmpeg...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", webm_path,
        "-i", audio_wav,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Successfully generated final demo video: {output_mp4}")
    else:
        print(f"FFmpeg error: {res.stderr}")

if __name__ == "__main__":
    webm_file = asyncio.run(record_demo())
    merge_audio_video(webm_file)
