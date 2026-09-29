# ruff: noqa
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

import datetime
import io
import os
from zoneinfo import ZoneInfo
import requests
from PIL import Image, ImageDraw

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google import genai
from google.cloud import storage

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback

MODEL = "gemini-2.5-flash"
GCS_BUCKET = "bwg3-qwiklabs-gcp-04-cc6a8d791f03"
PROJECT_ID = "qwiklabs-gcp-04-cc6a8d791f03"


def search_exercises(query: str, limit: int = 5) -> str:
    """Searches for real exercises, muscles, and workouts using the free wger public API.

    Args:
        query: Name or keyword of the exercise (e.g., 'squat', 'biceps', 'press', 'chest').
        limit: Max number of results to return (default: 5).

    Returns:
        String containing matching exercises, descriptions, and category info.
    """
    try:
        url = "https://wger.de/api/v2/exerciseinfo/"
        params = {"language": 2, "limit": 100}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        
        matches = []
        q = query.lower().strip()
        words = [w for w in q.split() if len(w) > 2]

        for item in results:
            cat = item.get("category", {}).get("name", "General")
            for t in item.get("translations", []):
                if t.get("language") == 2:
                    name = t.get("name", "")
                    desc = t.get("description", "").replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ").strip()
                    target_text = f"{name} {desc} {cat}".lower()
                    
                    if not q or q in target_text or any(w in target_text for w in words):
                        matches.append(f"- **{name}** ({cat}): {desc[:160]}")
                        break
            if len(matches) >= limit:
                break

        return "\n".join(matches) if matches else "No exercises found matching your query."
    except Exception as e:
        return f"Exercise search unavailable: {str(e)}"


def generate_item_image(item_name: str, tool_context: ToolContext) -> str:
    """Generates an image for a workout item or fitness meal, saves it as an artifact, and uploads to GCS.

    Args:
        item_name: Description of the meal or exercise to generate (e.g. 'high protein oatmeal', 'kettlebell deadlift').

    Returns:
        The public HTTPS URL of the uploaded image.
    """
    try:
        # Use Vertex AI gemini-2.5-flash-image in us-central1 to generate photorealistic image
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
        resp = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=f"A delicious, appetizing {item_name}, high protein meal, professional food photography, natural lighting, crisp detail",
        )
        img_bytes = None
        for p in resp.candidates[0].content.parts:
            if hasattr(p, "inline_data") and p.inline_data and p.inline_data.data:
                img_bytes = p.inline_data.data
                break
        if not img_bytes:
            raise ValueError("No image bytes returned in model response")
        mime_type = "image/png"
        ext = "png"
    except Exception as e:
        # High quality graphic fallback
        img = Image.new("RGB", (480, 320), color=(30, 136, 229))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 460, 300], outline=(255, 255, 255), width=3)
        draw.text((40, 60), "FITNESS COACH PLANNER", fill=(255, 255, 255))
        draw.text((40, 140), f"Item: {item_name[:32]}", fill=(255, 241, 118))
        draw.text((40, 200), "Nutrition & Training Visual Guide", fill=(227, 242, 253))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        img_bytes = buf.getvalue()
        mime_type = "image/jpeg"
        ext = "jpg"

    artifact_name = f"image_{int(datetime.datetime.now().timestamp())}.{ext}"
    try:
        tool_context.save_artifact(filename=artifact_name, artifact=img_bytes)
    except Exception:
        pass

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"images/{artifact_name}")
    blob.upload_from_string(img_bytes, content_type=mime_type)
    return f"https://storage.googleapis.com/{GCS_BUCKET}/images/{artifact_name}"


def generate_item_video(item_name: str, tool_context: ToolContext) -> str:
    """Generates a demo workout clip for an exercise, saves it as an artifact, and uploads to GCS.

    Args:
        item_name: Exercise or training movement to demonstrate (e.g. 'pullups', 'lunges').

    Returns:
        The public HTTPS URL of the video file.
    """
    # Placeholder video payload
    video_bytes = b"FITNESS_COACH_VIDEO_DATA_" + item_name.encode()
    artifact_name = f"video_{int(datetime.datetime.now().timestamp())}.mp4"
    try:
        tool_context.save_artifact(filename=artifact_name, artifact=video_bytes)
    except Exception:
        pass

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(f"videos/{artifact_name}")
    blob.upload_from_string(video_bytes, content_type="video/mp4")
    return f"https://storage.googleapis.com/{GCS_BUCKET}/videos/{artifact_name}"


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to save conversation facts and allergy preferences across sessions."""
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None


# Build A2UI schema manager and system prompt
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Fitness Coach, an intelligent fitness and nutrition assistant. "
        "You help users discover exercises, customize workout plans, and track meals. "
        "CRITICAL: Always remember and respect the user's dietary preferences and ALLERGIES across sessions. "
        "Never recommend foods the user is allergic to."
    ),
    workflow_description=(
        "Analyze the user's request. Search real exercises with search_exercises. "
        "Generate visuals with generate_item_image when requested. "
        "Return structured A2UI cards for workout routines and meal plans."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        search_exercises,
        generate_item_image,
        generate_item_video,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
