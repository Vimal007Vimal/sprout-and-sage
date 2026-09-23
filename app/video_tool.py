# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import uuid
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

BUCKET_NAME = "sprout-and-sage-assets-qwiklabs-gcp-03-4001ab701a83"
PROJECT_ID = "qwiklabs-gcp-03-4001ab701a83"
LOCATION = "global"
MODEL_NAME = "gemini-omni-flash-preview"


def generate_plant_video(prompt: str, tool_context: ToolContext = None) -> str:
    """Generates a short video for a botanical or plant item using Google's Omni model.

    Saves the video artifact with tool_context if available, and uploads the video
    bytes to public Cloud Storage, returning its public https URL.

    Args:
        prompt: Description of the plant or botanical scene to render in video format.
        tool_context: ADK ToolContext used to save artifacts to the Playground panel.

    Returns:
        The public HTTPS URL of the uploaded video in Cloud Storage.
    """
    try:
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location=LOCATION,
        )

        video_prompt = f"A short video of {prompt}, vivid botanical lighting, smooth motion"
        response = client.interactions.create(
            model=MODEL_NAME,
            input=video_prompt,
        )

        out_video = getattr(response, "output_video", None)
        if not out_video or not hasattr(out_video, "data") or not out_video.data:
            return "Error: No video data returned from gemini-omni-flash-preview."

        raw_data = out_video.data
        if isinstance(raw_data, bytes):
            video_bytes = raw_data
        elif isinstance(raw_data, str):
            video_bytes = base64.b64decode(raw_data)
        else:
            video_bytes = bytes(raw_data)

        mime_type = getattr(out_video, "mime_type", "video/mp4") or "video/mp4"
        ext = "mp4" if "mp4" in mime_type else "webm"
        filename = f"plant_video_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save artifact if tool_context is provided
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                tool_context.save_artifact(
                    filename=filename,
                    artifact=types.Part.from_bytes(
                        data=video_bytes,
                        mime_type=mime_type,
                    ),
                )
            except Exception as e:
                print(f"Warning: Could not save artifact in tool_context: {e}")

        # 2. Upload video bytes to Cloud Storage bucket without local file writes
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url

    except Exception as e:
        return f"Error generating video: {e}"
