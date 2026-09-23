import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

BUCKET_NAME = "sprout-and-sage-assets-qwiklabs-gcp-03-4001ab701a83"
PROJECT_ID = "qwiklabs-gcp-03-4001ab701a83"


def generate_plant_image(
    prompt: str,
    tool_context: ToolContext = None,
) -> str:
    """Generates an image of a plant or botanical scene based on a prompt, saves it as an ADK session artifact,
    and uploads it to public Cloud Storage.

    Args:
        prompt: Detailed description of the plant or botanical scene (e.g., 'A lush Monstera Deliciosa in a sunlit living room').
        tool_context: ADK ToolContext automatically injected during execution.

    Returns:
        The public HTTPS Cloud Storage URL of the generated image (https://storage.googleapis.com/<bucket>/<object>).
    """
    try:
        # 1. Generate image using gemini-3.1-flash-lite-image model in global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break

        if not image_bytes:
            return "Error: No image bytes were returned by the gemini-3.1-flash-lite-image model."

        filename = f"plant_preview_{uuid.uuid4().hex[:8]}.jpg"

        # 2. Save artifact to tool_context if available (for Playground Artifacts panel)
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as artifact_err:
                print(f"Warning: Could not save artifact to ToolContext: {artifact_err}")

        # 3. Upload image bytes directly to GCS bucket (no local file created)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url
    except Exception as e:
        return f"Error generating or uploading plant image: {e}"
